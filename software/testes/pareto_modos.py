#!/usr/bin/env python3
"""
Fronteira de Pareto perda x custo dos 35 modos, nos formatos da [4] v3.

Para cada par (N, portadora) e número de iterações, cada ponto é um formato num modo
(quantização, estouro): perda de SNR em SER = 10^-2 na configuração mais exigente (o pior
caso das configurações 6 e 8, [4] v3) contra o custo da síntese HLS (LUT ou DSP,
sinteses/modos_16x16). A fronteira liga os pontos que nenhum outro supera nos dois ao
mesmo tempo (menos perda e menos custo); os pontos dela levam o nome do modo.

Uma figura por número de iterações, com uma linha por par e uma coluna por recurso, em
resultados/pareto/modos/, e uma tabela com os pontos da fronteira (fronteira.csv).

Com --interpolada, a fronteira liga os pontos por retas (interpolação linear entre os
pontos vizinhos) em vez de degraus, em pareto_modos_interpolado_iter<T>.png; as figuras
em degrau e a tabela não são tocadas.

Com --porcentagem, o custo é a ocupação da FPGA (% do que a XCU50 tem, pelo campo
AvailableResources do relatório do HLS), com uma terceira coluna para o recurso que mais
ocupa entre LUT, DSP, FF e BRAM (o gargalo), em pareto_modos_porcentagem*_iter<T>.png e
fronteira_porcentagem.csv. Pode ser usado junto com --interpolada.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python pareto_modos.py [--interpolada] [--porcentagem]
"""

import argparse
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator

from figuras_formatos import LIMIAR_DB, OVERFLOWS, QUANTS, ler, perdas
from figuras_recursos import SINTESES, ler as ler_sinteses
from dbp_sim.plotting import GRID, INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE

AQUI = Path(__file__).resolve().parent
V3 = AQUI / "resultados" / "4_varredura_formatos" / "v3_formatos_juntos"
SAIDA = AQUI / "resultados" / "pareto" / "modos"
CONFIGS = (6, 8)      # as mais exigentes da [4] v2 em todos os pares
CONDS = (("TDLA30-5", "TDLA30-5 e TDLA30-10: $N$ = 192, 3,5 GHz"),
         ("TDLA30-75", "TDLA30-75: $N$ = 192, 28 GHz"),
         ("TDLA30-300", "TDLA30-300: $N$ = 168, 28 GHz"),
         ("TDLC300-100", "TDLC300-100: $N$ = 132, 3,5 GHz"),
         ("TDLB100-400", "TDLB100-400: $N$ = 24, 3,5 GHz"))
RECURSOS = (("LUT", "LUT"), ("DSP", "DSP"))
RECURSOS_PCT = (("LUT", "LUT"), ("DSP", "DSP"), ("gargalo", "Maior ocupação"))
GARGALO = ("LUT", "DSP", "FF", "BRAM_18K")   # recursos comparados no gargalo (URAM é zero)
#: Cor e marcador por posição do formato no par (do menor para o maior W). Paleta
#: validada: node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a,#eda100"
#: --mode light -> ALL CHECKS PASS (contraste baixo do verde e do amarelo: os marcadores
#: e a legenda carregam a identidade junto da cor)
CORES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
MARCADORES = ("o", "s", "D", "^")
TETO = 8.0            # onde o × (não chega a 10^-2) é desenhado
EMPATE = 0.02         # diferenças de perda até isso contam como empate na fronteira
ABREV = {"AP_TRN": "TRN", "AP_TRN_ZERO": "TRN_Z", "AP_RND": "RND", "AP_RND_ZERO": "RND_Z",
         "AP_RND_MIN_INF": "RND_MI", "AP_RND_INF": "RND_I", "AP_RND_CONV": "RND_C",
         "AP_SAT": "SAT", "AP_SAT_ZERO": "SAT_Z", "AP_SAT_SYM": "SAT_S", "AP_WRAP": "WRAP",
         "AP_WRAP_SM": "WRAP_SM"}
#: Código fixo de cada modo, o mesmo em todos os gráficos: letra = quantização, número =
#: estouro, na ordem das linhas dos mapas de perda (TRN/SAT = A1, RND_MIN_INF/WRAP = E4)
CODIGO = {(q, o): f"{chr(ord('A') + i)}{j + 1}" for i, q in enumerate(QUANTS)
          for j, o in enumerate(OVERFLOWS)}


def fronteira(pontos):
    """Índices dos pontos não dominados: nenhum outro tem custo menor ou igual e perda
    menor (com empate até EMPATE dB), com pelo menos um dos dois estritamente melhor."""
    ordem = sorted(range(len(pontos)), key=lambda i: (pontos[i][0], pontos[i][1]))
    escolhidos, melhor = [], np.inf
    for i in ordem:
        custo, perda = pontos[i]
        if perda < melhor - EMPATE:
            escolhidos.append(i)
            melhor = perda
    return escolhidos


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--interpolada", action="store_true",
                        help="Fronteira por retas entre os pontos, em arquivos à parte")
    parser.add_argument("--porcentagem", action="store_true",
                        help="Custo em %% da FPGA, com a coluna do recurso gargalo, em arquivos à parte")
    args = parser.parse_args()
    interpolada, pct = args.interpolada, args.porcentagem
    rodadas = ler(V3)
    sint = ler_sinteses()
    recursos = RECURSOS_PCT if pct else RECURSOS
    # Total de cada recurso na XCU50, do próprio relatório do HLS
    xml = next(SINTESES.glob("*/csynth.xml"))
    disp = {e.tag: float(e.text) for e in ET.parse(xml).getroot().find("AreaEstimates/AvailableResources")}

    def custo_de(chave, campo):
        """(custo, recurso): o valor absoluto, ou a % da FPGA com --porcentagem; no gargalo,
        a maior % entre GARGALO e o recurso dela."""
        r = sint[chave]
        if not pct:
            return float(r[campo]), campo
        if campo == "gargalo":
            return max((100 * float(r[c]) / disp[c], c) for c in GARGALO)
        return 100 * float(r[campo]) / disp[campo], campo
    SAIDA.mkdir(parents=True, exist_ok=True)
    linhas_csv = []
    for t in (1, 4):
        p = perdas(rodadas, f"BCD-MMSE (iter {t})")
        fig, eixos = plt.subplots(len(CONDS), len(recursos), figsize=(6.5 * len(recursos), 4.2 * len(CONDS)),
                                  squeeze=False)
        fig.patch.set_facecolor(SURFACE)
        for li, (cond, titulo) in enumerate(CONDS):
            formatos = sorted({(d["int_bits"], d["frac_bits"]) for d in rodadas
                               if d["condicao"] == cond}, key=lambda f: (f[0] + f[1], f[0]))
            casos = []
            for b, (I, F) in enumerate(formatos):
                for q, o in [(k[2], k[3]) for k in sint if k[:2] == (I, F)]:
                    vs = [p.get((k, cond, I, F, q, o)) for k in CONFIGS]
                    perda = TETO if any(v is None for v in vs) else max(vs)
                    casos.append((b, I, F, q, o, perda))
            for ci, (campo, nome) in enumerate(recursos):
                ax = eixos[li][ci]
                ax.set_facecolor(SURFACE)
                custos = [custo_de((I, F, q, o), campo) for _, I, F, q, o, _ in casos]
                pontos = [(c, caso[5]) for (c, _), caso in zip(custos, casos)]
                front = fronteira(pontos)
                for b, (I, F) in enumerate(formatos):
                    idx = [i for i, c in enumerate(casos) if c[0] == b]
                    ax.scatter([pontos[i][0] for i in idx], [pontos[i][1] for i in idx], s=34,
                               color=CORES[b], marker=MARCADORES[b], alpha=0.55,
                               edgecolor=SURFACE, linewidth=0.8, zorder=3,
                               label=f"<{I + F},{I}>")
                # Fronteira em degrau e os nomes dos modos dela
                fx = [pontos[i][0] for i in front]
                fy = [pontos[i][1] for i in front]
                if interpolada:
                    ax.plot(fx, fy, color=INK_PRIMARY, linewidth=1.4, zorder=4)
                else:
                    ax.step(fx, fy, where="post", color=INK_PRIMARY, linewidth=1.4, zorder=4)
                ax.scatter(fx, fy, s=60, facecolor="none", edgecolor=INK_PRIMARY, linewidth=1.2,
                           zorder=5)
                # Os pontos da fronteira levam o código do modo (o mesmo em todos os gráficos,
                # não é ordem de classificação); a lista no canto traz os nomes, do mais
                # barato para o mais caro
                lista = []
                for n, i in enumerate(front):
                    b, I, F, q, o, perda = casos[i]
                    # Modos do mesmo formato com o mesmo custo e a mesma perda: todos os códigos
                    iguais = [c for j, c in enumerate(casos) if pontos[j] == pontos[i] and c[0] == b]
                    codigos = ",".join(CODIGO[(c[3], c[4])] for c in iguais)
                    ax.annotate(codigos, (pontos[i][0], pontos[i][1]), xytext=(5, 4 + 9 * (n % 2)),
                                textcoords="offset points", fontsize=7.5, color=INK_PRIMARY,
                                fontweight="bold", zorder=6)
                    valor = "×" if perda >= TETO else f"{perda:.2f}".replace(".", ",")
                    if pct:
                        gargalo = f" ({custos[i][1].replace('_18K', '')})" if campo == "gargalo" else ""
                        custo = f"{pontos[i][0]:.2f}%".replace(".", ",") + gargalo
                    else:
                        custo = f"{int(pontos[i][0]):,}".replace(",", ".") + f" {nome}"
                    nomes = ", ".join(f"{ABREV[c[3]]}/{ABREV[c[4]]}" for c in iguais)
                    lista.append(f"{codigos}  <{I + F},{I}> {nomes}: {custo}, {valor} dB")
                    linhas_csv.append({"iteracoes": t, "condicao": cond, "recurso": campo,
                                       "formato": f"<{I + F},{I}>", "codigos": codigos,
                                       "modos": " ".join(f"{c[3]}/{c[4]}" for c in iguais),
                                       "custo": round(pontos[i][0], 3) if pct else int(pontos[i][0]),
                                       "recurso_do_custo": custos[i][1],
                                       "perda_db": "x" if perda >= TETO else round(perda, 3)})
                ax.text(0.98, 0.42, "Fronteira:\n" + "\n".join(lista), transform=ax.transAxes,
                        ha="right", va="center", fontsize=7, color=INK_PRIMARY, zorder=7,
                        bbox=dict(facecolor=SURFACE, alpha=0.9, edgecolor=INK_MUTED, linewidth=0.6,
                                  boxstyle="round,pad=0.4"))
                ax.axhline(LIMIAR_DB, color=INK_SECONDARY, linestyle="--", linewidth=1, zorder=2)
                ax.text(1.0, LIMIAR_DB, " 0,1 dB", transform=ax.get_yaxis_transform(),
                        ha="left", va="center", fontsize=7.5, color=INK_SECONDARY)
                ax.set_yscale("symlog", linthresh=0.1, linscale=0.6)
                ticks = [0, 0.05, 0.1, 0.5, 1, 2, 5, TETO]
                ax.yaxis.set_major_locator(FixedLocator(ticks))
                ax.set_yticklabels(["0", "0,05", "0,1", "0,5", "1", "2", "5", "×"])
                ax.set_ylim(-0.01, TETO * 1.4)
                if pct:
                    rot = ("Maior ocupação entre LUT, DSP, FF e BRAM" if campo == "gargalo"
                           else f"{nome}")
                    ax.set_xlabel(f"{rot} (% da XCU50, síntese HLS)", fontsize=9,
                                  color=INK_SECONDARY)
                    ax.xaxis.set_major_formatter(
                        plt.FuncFormatter(lambda v, _: f"{v:g}%".replace(".", ",")))
                else:
                    ax.set_xlabel(f"{nome} (síntese HLS)", fontsize=9, color=INK_SECONDARY)
                ax.set_ylabel("Perda de SNR em SER = $10^{-2}$ [dB]", fontsize=9,
                              color=INK_SECONDARY)
                ax.set_title(titulo, fontsize=10, color=INK_PRIMARY, loc="left")
                ax.grid(True, color=GRID, linewidth=0.7, zorder=0)
                for lado in ("top", "right"):
                    ax.spines[lado].set_visible(False)
                for lado in ("left", "bottom"):
                    ax.spines[lado].set_color(INK_MUTED)
                ax.tick_params(colors=INK_SECONDARY, labelsize=8)
                ax.legend(loc="upper right", fontsize=7.5, frameon=False, labelcolor=INK_SECONDARY,
                          title="formato", title_fontsize=7.5)
        fig.suptitle(f"Perda x custo dos 35 modos, {t} {'iterações' if t > 1 else 'iteração'}: "
                     "pior caso das configurações 6 e 8 ([4] v3) contra a síntese HLS "
                     "(C synthesis, XCU50, 100 MHz, sem diretivas)\n"
                     + ("Custo em % do que a XCU50 tem (DSP 5.952, LUT 871.680, FF 1.743.360, "
                        "BRAM 2.688); maior ocupação = o recurso que mais ocupa (gargalo)\n"
                        if pct else "") +
                     "Linha preta: fronteira de Pareto (nenhum outro ponto tem menos perda e "
                     "menos custo; diferenças de perda até 0,02 dB contam como empate)"
                     + ("\nAs retas só ligam os pontos da fronteira: entre eles não existe formato "
                        "nem modo" if interpolada else "") + "\n"
                     "Código do modo (o mesmo em todos os gráficos, não é classificação): "
                     "letra = quantização, número = estouro\n"
                     "A TRN, B TRN_ZERO, C RND, D RND_ZERO, E RND_MIN_INF, F RND_INF, G RND_CONV; "
                     "1 SAT, 2 SAT_ZERO, 3 SAT_SYM, 4 WRAP, 5 WRAP_SM\n"
                     "Vários códigos num ponto: modos do mesmo formato com o mesmo custo e a mesma "
                     "perda\nNomes na lista sem o prefixo AP_ (_Z = _ZERO, RND_MI = RND_MIN_INF, "
                     "RND_I = RND_INF, RND_C = RND_CONV, SAT_S = SAT_SYM)",
                     fontsize=10, color=INK_PRIMARY)
        fig.tight_layout(rect=(0, 0, 0.97, 0.955))
        nome_arq = ("pareto_modos" + ("_porcentagem" if pct else "")
                    + ("_interpolado" if interpolada else "") + f"_iter{t}.png")
        png = SAIDA / nome_arq
        fig.savefig(png, dpi=160, facecolor=SURFACE)
        fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE)
        plt.close(fig)
        print(f"  {png}")
    if interpolada:
        return
    tabela = SAIDA / ("fronteira_porcentagem.csv" if pct else "fronteira.csv")
    with open(tabela, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas_csv[0]))
        w.writeheader()
        w.writerows(linhas_csv)
    print(f"  {tabela}: {len(linhas_csv)} pontos")


if __name__ == "__main__":
    main()
