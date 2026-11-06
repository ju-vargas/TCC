#!/usr/bin/env python3
"""
Fronteira de Pareto ocupação x perda da [4] v4 (formatos juntos, 16 configurações, 35 modos),
separada por tamanho do circuito: 16 x 16 (configurações 1 a 8 e 13 a 16) e 32 x 32
(configurações 9 a 12, M = 256 com C = 8).

Para cada cenário, número de iterações e circuito, cada ponto é um formato num modo: a perda
de SNR em SER = 10^-2 na configuração em que ele vai pior (entre as do circuito) contra a
maior ocupação da XCU50 entre LUT, DSP, FF e BRAM da síntese HLS do mesmo formato, modo e
tamanho (sinteses/modos_16x16 ou modos_32x32). Os pontos que dão × em alguma configuração
ficam numa faixa no alto e não entram na fronteira.

Uma figura por circuito e número de iterações, com uma linha por cenário, em
resultados/pareto/v4/, e uma tabela por circuito com os pontos da fronteira e a perda em
cada configuração (fronteira_<n>x<n>.csv). Enquanto a simulação não termina, só entram as
configurações que já têm todas as rodadas; o título diz quais.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python pareto_v4.py [--dados PASTA]
"""

import argparse
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator

from figuras_formatos import GARGALO, LIMIAR_DB, ler, perdas
from pareto_modos import ABREV, CODIGO, CONDS, CORES, EMPATE, TETO, fronteira
from dbp_sim.plotting import GRID, INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE

AQUI = Path(__file__).resolve().parent
V4 = AQUI / "resultados" / "4_varredura_formatos" / "v4_formatos_juntos_16_configs"
SINTESES = AQUI.parent.parent / "hardware" / "cholesky_hardware" / "sinteses"
SAIDA = AQUI / "resultados" / "pareto" / "v4"
CIRCUITOS = {16: (1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16), 32: (9, 10, 11, 12)}
FORMATOS = ((6, 8), (6, 10), (8, 10), (8, 12), (12, 10), (12, 12), (12, 14), (12, 16),
            (14, 14), (14, 16))
#: Cor pelos bits inteiros (a paleta validada de pareto_modos), marcador pelos fracionários
COR_I = dict(zip((6, 8, 12, 14), CORES))
MARCADOR_F = {8: "o", 10: "s", 12: "D", 14: "^", 16: "v"}
N_MODOS = 35


def ocupacao(n: int) -> dict:
    """{(I, F, q, o): (maior % da XCU50 entre GARGALO, recurso)} das sínteses n x n."""
    pasta = SINTESES / f"modos_{n}x{n}"
    xml = next(pasta.glob("*/csynth.xml"))
    disp = {e.tag: float(e.text) for e in ET.parse(xml).getroot().find("AreaEstimates/AvailableResources")}
    with open(pasta / "recursos.csv") as fh:
        return {(int(r["int_bits"]), int(r["frac_bits"]), r["quant"], r["overflow"]):
                max((100 * float(r[c]) / disp[c], c) for c in GARGALO) for r in csv.DictReader(fh)}


def nivel(v):
    if v is None:
        return "×"
    return "<=0,1" if round(v, 2) <= LIMIAR_DB else ("<=3" if round(v, 2) <= 3 else ">3")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dados", default=str(V4), help="Pasta da varredura (padrão: a v4)")
    args = parser.parse_args()
    rodadas = ler(Path(args.dados))
    # Configurações completas: todas as rodadas de todos os formatos, modos e cenários
    contagem = {}
    for d in rodadas:
        contagem[d["configuracao"]] = contagem.get(d["configuracao"], 0) + 1
    completas = {k for k, c in contagem.items() if c == len(FORMATOS) * N_MODOS * len(CONDS)}
    SAIDA.mkdir(parents=True, exist_ok=True)
    for n, configs_circ in CIRCUITOS.items():
        configs = [k for k in configs_circ if k in completas]
        if not configs:
            print(f"  {n}x{n}: nenhuma configuração completa ainda")
            continue
        occ = ocupacao(n)
        linhas_csv = []
        for t in (1, 4):
            p = perdas(rodadas, f"BCD-MMSE (iter {t})")
            fig, eixos = plt.subplots(len(CONDS), 1, figsize=(11, 6.0 * len(CONDS)), squeeze=False)
            fig.patch.set_facecolor(SURFACE)
            for li, (cond, titulo) in enumerate(CONDS):
                ax = eixos[li][0]
                ax.set_facecolor(SURFACE)
                casos = []   # (I, F, q, o, ocupação, recurso, pior perda, config do pior, perdas)
                for I, F in FORMATOS:
                    for (I2, F2, q, o), (oc, rec) in occ.items():
                        if (I2, F2) != (I, F):
                            continue
                        vs = {k: p.get((k, cond, I, F, q, o)) for k in configs}
                        if any(v is None for v in vs.values()):
                            pior, k_pior = TETO, next(k for k, v in vs.items() if v is None)
                        else:
                            k_pior = max(vs, key=vs.get)
                            pior = vs[k_pior]
                        casos.append((I, F, q, o, oc, rec, pior, k_pior, vs))
                for I, F in FORMATOS:
                    xs = [c[4] for c in casos if c[:2] == (I, F)]
                    ys = [c[6] for c in casos if c[:2] == (I, F)]
                    ax.scatter(xs, ys, s=40, color=COR_I[I], marker=MARCADOR_F[F], alpha=0.6,
                               edgecolor=SURFACE, linewidth=0.8, zorder=3)
                validos = [i for i, c in enumerate(casos) if c[6] < TETO]
                front = [validos[j] for j in fronteira([(casos[i][4], casos[i][6]) for i in validos])]
                fx = [casos[i][4] for i in front]
                fy = [casos[i][6] for i in front]
                ax.step(fx, fy, where="post", color=INK_PRIMARY, linewidth=1.4, zorder=4)
                ax.scatter(fx, fy, s=70, facecolor="none", edgecolor=INK_PRIMARY, linewidth=1.2, zorder=5)
                lista = []
                for m, i in enumerate(front):
                    I, F, q, o, oc, rec, pior, k_pior, vs = casos[i]
                    iguais = [c for c in casos if c[:2] == (I, F) and c[4] == oc and abs(c[6] - pior) <= EMPATE]
                    codigos = ",".join(CODIGO[(c[2], c[3])] for c in iguais)
                    ax.annotate(codigos, (oc, pior), xytext=(5, 4 + 9 * (m % 2)), textcoords="offset points",
                                fontsize=7.5, color=INK_PRIMARY, fontweight="bold", zorder=6)
                    nomes = ", ".join(f"{ABREV[c[2]]}/{ABREV[c[3]]}" for c in iguais)
                    lista.append(f"{codigos}  <{I + F},{I}> {nomes}: {oc:.2f}% ({rec.replace('_18K', '')}), "
                                 f"{pior:.2f} dB (pior: config. {k_pior})".replace(".", ","))
                    for c in iguais:
                        linhas_csv.append({
                            "iteracoes": t, "cenario": cond, "formato": f"<{I + F},{I}>",
                            "codigo": CODIGO[(c[2], c[3])], "quant": c[2], "estouro": c[3],
                            "ocupacao_pct": round(c[4], 3), "recurso": c[5],
                            "pior_perda_db": round(c[6], 3), "config_pior": c[7],
                            **{f"config_{k}": ("x" if c[8][k] is None else round(c[8][k], 3)) for k in configs},
                            **{f"nivel_{k}": nivel(c[8][k]) for k in configs}})
                ax.text(0.0, -0.2, "Fronteira:\n" + "\n".join(lista), transform=ax.transAxes, ha="left",
                        va="top", fontsize=7.5, color=INK_PRIMARY, linespacing=1.4)
                ax.axhline(LIMIAR_DB, color=INK_SECONDARY, linestyle="--", linewidth=1, zorder=2)
                ax.text(1.0, LIMIAR_DB, " 0,1 dB", transform=ax.get_yaxis_transform(), ha="left",
                        va="center", fontsize=7.5, color=INK_SECONDARY)
                ax.axhline(3, color=INK_SECONDARY, linestyle=":", linewidth=1, zorder=2)
                ax.text(1.0, 3, " 3 dB", transform=ax.get_yaxis_transform(), ha="left", va="center",
                        fontsize=7.5, color=INK_SECONDARY)
                ax.set_yscale("symlog", linthresh=0.1, linscale=0.6)
                ax.yaxis.set_major_locator(FixedLocator([0, 0.05, 0.1, 0.5, 1, 2, 3, 5, TETO]))
                ax.set_yticklabels(["0", "0,05", "0,1", "0,5", "1", "2", "3", "5", "×"])
                ax.set_ylim(-0.01, TETO * 1.4)
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}%".replace(".", ",")))
                ax.set_xlabel(f"Maior ocupação entre LUT, DSP, FF e BRAM (% da XCU50, síntese HLS {n} x {n})",
                              fontsize=9, color=INK_SECONDARY)
                ax.set_ylabel("Pior perda de SNR em SER = $10^{-2}$ [dB]", fontsize=9, color=INK_SECONDARY)
                ax.set_title(titulo, fontsize=10, color=INK_PRIMARY, loc="left")
                ax.grid(True, color=GRID, linewidth=0.7, zorder=0)
                for lado in ("top", "right"):
                    ax.spines[lado].set_visible(False)
                for lado in ("left", "bottom"):
                    ax.spines[lado].set_color(INK_MUTED)
                ax.tick_params(colors=INK_SECONDARY, labelsize=8)
            faltam = [k for k in configs_circ if k not in configs]
            fig.suptitle(
                f"Circuito {n} x {n}, {t} {'iterações' if t > 1 else 'iteração'}: pior perda entre as configurações "
                f"{', '.join(map(str, configs))} ([4] v4)\ncontra a ocupação da síntese HLS (C synthesis, XCU50, "
                "100 MHz, sem diretivas)\n"
                + (f"Ainda sem as configurações {', '.join(map(str, faltam))} (simulação em andamento)\n" if faltam else "")
                + "Faixa × no alto: o formato e modo não chega a SER = $10^{-2}$ em alguma configuração;\nfica fora "
                "da fronteira. Linha preta: fronteira de Pareto (nenhum outro ponto tem menos perda e menos "
                "ocupação;\ndiferenças de perda até 0,02 dB contam como empate)\n"
                "Código do modo: letra = quantização (A TRN, B TRN_ZERO, C RND, D RND_ZERO, E RND_MIN_INF, "
                "F RND_INF, G RND_CONV),\nnúmero = estouro (1 SAT, 2 SAT_ZERO, 3 SAT_SYM, 4 WRAP, 5 WRAP_SM)",
                fontsize=10, color=INK_PRIMARY, y=0.995)
            legenda = [Line2D([], [], linestyle="", marker=MARCADOR_F[F], color=COR_I[I], markersize=7,
                              label=f"<{I + F},{I}>") for I, F in FORMATOS]
            fig.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, 0.951), fontsize=8,
                       frameon=False, ncol=10, labelcolor=INK_SECONDARY, title="formato (cor = I, marcador = F)",
                       title_fontsize=8)
            fig.tight_layout(rect=(0, 0, 0.96, 0.935), h_pad=3)
            fig.subplots_adjust(top=0.925)
            png = SAIDA / f"pareto_{n}x{n}_iter{t}.png"
            fig.savefig(png, dpi=160, facecolor=SURFACE)
            fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE)
            plt.close(fig)
            print(f"  {png}")
        tabela = SAIDA / f"fronteira_{n}x{n}.csv"
        with open(tabela, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(linhas_csv[0]))
            w.writeheader()
            w.writerows(linhas_csv)
        print(f"  {tabela}: {len(linhas_csv)} linhas")


if __name__ == "__main__":
    main()
