#!/usr/bin/env python3
"""
Três figuras da análise por grupos (estação e circuito), todas com o BCD-MMSE de 1 iteração
e os formatos no modo fixo do mapa até 3 dB (rodada [5] modo_fixo_3dB, grade inteira de SNR,
mesma semente da referência float [1]).

1. snr_necessaria_<cenário>: SNR para SER = 1e-2 de LMMSE, ZF e BCD-MMSE (float) da
   referência e do BCD-MMSE com a inversa em <22,12>, <24,12> e <28,14>. Uma figura por par
   (N, portadora); linhas = configurações agrupadas por estação (G1, G2, G3). Pontos em vez
   de barras: a SNR é negativa em boa parte dos casos e 0 dB não é uma base, então o
   comprimento de uma barra não teria significado.
2. compromisso_<ocupacao|potencia>: perda de SNR x custo da arquitetura, só 16 x 16 (a
   32 x 32 só existe sem otimização). Um painel por cenário; em cada um, a arquitetura feita
   para aquele cenário (9090, 4545, 606, 455, 152, 114) nos 5 formatos sintetizados. A perda
   é a pior entre as configurações do circuito 16 x 16 (1 a 8 e 13 a 16) naquele cenário.
   Custo: maior ocupação da XCU50 (LUT, FF, DSP ou BRAM) ou potência dinâmica, do Vivado
   2023.2 no servidor (hardware/resultados_servidor/).
3. mapa_perda_estacoes: perda por configuração (linhas, agrupadas por estação) e formato
   (colunas). Cada célula é a pior perda entre os 5 pares, com o par embaixo.

Perda = SNR do BCD-MMSE com a inversa em ponto fixo - SNR do BCD-MMSE em float, em SER = 1e-2
(snr_no_alvo de figuras_formatos.py, a mesma dos mapas). Quando a referência já está abaixo
de 1e-2 em -10 dB, a SNR é presa em -10 dB e a perda vira limite inferior (marcado no CSV).

Saída: resultados/5_candidatos/modo_fixo_3dB/figuras/analise_grupos/ (png, pdf, _data.csv).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_analise_grupos.py [--configs A,D,M,N]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib                                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
import numpy as np                                      # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402
from matplotlib.patches import Patch, Rectangle         # noqa: E402

from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (BCD_ITERATION_RAMP, GRID, INK_MUTED, INK_PRIMARY,  # noqa: E402
                              INK_SECONDARY, ITERATION_ZF_COLOR, MODULATION_LABEL,
                              SERIES_STYLE, SURFACE)
from figuras_formatos import ALVO, snr_no_alvo           # noqa: E402
from figuras_modo_fixo import PASTA, pasta_referencia    # noqa: E402
from mapa_cenarios_v4 import LETRAS                      # noqa: E402

SAIDA = PASTA / "figuras" / "analise_grupos"
SUFIXO = []   # com --configs: as letras no fim do nome, para não gravar em cima das 16
SERVIDOR = AQUI.parent.parent / "hardware" / "resultados_servidor"
BCD1 = "BCD-MMSE (iter 1)"
GRADE = list(range(-10, 11, 2))

# Pares (N, portadora) simulados; TDLA30-10 usa as matrizes do TDLA30-5
CENARIOS = {"TDLA30-5": "TDLA30-5 e TDLA30-10: $N$ = 192, 3,5 GHz",
            "TDLA30-75": "TDLA30-75: $N$ = 192, 28 GHz",
            "TDLA30-300": "TDLA30-300: $N$ = 168, 28 GHz",
            "TDLC300-100": "TDLC300-100: $N$ = 132, 3,5 GHz",
            "TDLB100-400": "TDLB100-400: $N$ = 24, 3,5 GHz"}
ABREV_CENARIO = {"TDLA30-5": "A30-5", "TDLA30-75": "A30-75", "TDLA30-300": "A30-300",
                 "TDLC300-100": "C300", "TDLB100-400": "B100"}

# Estações (M e C fixos na instalação) e o circuito que cada uma usa (M_c = M / C)
ESTACOES = (("G1", 128, 8, (1, 2, 3, 4, 5, 6, 7, 8)),
            ("G2", 256, 8, (9, 10, 11, 12)),
            ("G3", 256, 16, (13, 14, 15, 16)))
CIRCUITO_16 = (1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16)

# Formatos sintetizados: (I, F) do simulador -> (rótulo, arquivo, pasta do servidor)
FORMATOS = {(12, 10): ("<22,12>", "AP_RND_ZERO_AP_WRAP", "22-12"),
            (12, 12): ("<24,12>", "AP_RND_ZERO_AP_WRAP", "24-12"),
            (12, 14): ("<26,12>", "AP_RND_ZERO_AP_WRAP", "26-12"),
            (14, 14): ("<28,14>", "AP_RND_ZERO_AP_WRAP", "28-14"),
            (14, 16): ("<30,14>", "AP_TRN_AP_SAT", "30-14")}
MODO = {"AP_RND_ZERO_AP_WRAP": "RND_ZERO/WRAP", "AP_TRN_AP_SAT": "TRN/SAT"}
FORMATOS_FIG1 = ((12, 10), (12, 12), (14, 14))   # os 3 formatos pedidos

# Arquitetura feita para cada cenário (alvo de ciclos) e o cenário do seu testbench
ARQUITETURAS = (("TDLA30-5", "9090", "TDLA30-5"), ("TDLA30-10", "4545", "TDLA30-5"),
                ("TDLA30-75", "606", "TDLA30-75"), ("TDLA30-300", "152_sistolico", "TDLA30-300"),
                ("TDLC300-100", "455", "TDLC300-100"),
                ("TDLB100-400", "114_sistolico", "TDLB100-400"))

# Cores: as mesmas da bcd_iterations e da ser_formatos_iter1 (LMMSE vermelho, ZF rosa,
# BCD-MMSE iter 1 laranja). Os formatos ficam no laranja e se separam pelo marcador vazado.
LARANJA = BCD_ITERATION_RAMP[0]
SERIES_FIG1 = (("LMMSE", "LMMSE, float", SERIES_STYLE["LMMSE"][0], "o", True),
               ("ZF", "ZF, float", ITERATION_ZF_COLOR, "s", True),
               ("BCD", "BCD-MMSE (iter 1), float", LARANJA, "v", True),
               ((12, 10), "BCD-MMSE (iter 1), <22,12>", LARANJA, "o", False),
               ((12, 12), "BCD-MMSE (iter 1), <24,12>", LARANJA, "s", False),
               ((14, 14), "BCD-MMSE (iter 1), <28,14>", LARANJA, "D", False))
# Formatos na figura 2: rampa de um tom (azul), do menor para o maior W
AZUIS = ("#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b")
MARC_FORMATO = ("v", "^", "s", "D", "o")
# Faixas do mapa em tons claros para o número ficar legível; sem verde (pedido da autora):
# até 0,1 dB em cinza neutro, depois amarelo e vermelho
FAIXAS = ((0.1, "#e6e5e0", "até 0,1 dB"), (3.0, "#fde3a7", "de 0,1 a 3 dB"),
          (np.inf, "#f4c6c6", "acima de 3 dB"))
VERMELHO = "#d03b3b"   # × de "não chega a 1e-2", como nos mapas de modo fixo

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "axes.titlesize": 8.5, "axes.labelsize": 8.5,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5})
LARGURA = 6.3   # polegadas: largura de texto de uma página A4 com margens de 3 e 2 cm


def num(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def eixos(ax, grade_x=True, grade_y=False):
    ax.set_facecolor(SURFACE)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(INK_MUTED)
        ax.spines[lado].set_linewidth(0.8)
    ax.tick_params(colors=INK_SECONDARY, length=3, width=0.8)
    if grade_x:
        ax.grid(True, axis="x", color=GRID, linewidth=0.6, zorder=0)
    if grade_y:
        ax.grid(True, axis="y", color=GRID, linewidth=0.6, zorder=0)


def salvar(fig, nome: str, linhas: list[list], cabecalho: list[str]) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA / f"{nome}.png", dpi=250, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(SAIDA / f"{nome}.pdf", facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    with open(SAIDA / f"{nome}_data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)
    print(SAIDA / f"{nome}.png")


# ---------------------------------------------------------------- dados de SER

def estado_snr(ser):
    """(SNR em SER = 1e-2, estado): 'ok', 'abaixo' (já abaixo em -10 dB, SNR presa em -10)
    ou 'nao_atinge' (não chega a 1e-2 até 10 dB; SNR None)."""
    x = snr_no_alvo(GRADE, ser)
    if x is None:
        return None, "nao_atinge"
    return x, ("abaixo" if ser[0] < ALVO else "ok")


def carregar():
    """{(cenário, config): {curva: SER}} com LMMSE, ZF, BCD (float) e (I, F) do hardware."""
    rotulo = {TCC_CONFIGURATION[p.label]: p.label for p in ALL_PANELS}
    ser = {}
    for cond in CENARIOS:
        ref = json.loads((pasta_referencia(cond) / "bcd_iterations_results.json").read_text())
        for k, lab in rotulo.items():
            r = {"LMMSE": ref[lab]["LMMSE"], "ZF": ref[lab]["ZF"], "BCD": ref[lab][BCD1]}
            assert all(len(v) == len(GRADE) for v in r.values()), (cond, k)
            for (I, F), (_, modo, _) in FORMATOS.items():
                arq = PASTA / "dados" / cond / f"configuracao_{k}" / f"{I}_{F}_{modo}.json"
                d = json.loads(arq.read_text())
                assert d["snr_db"] == GRADE, arq   # mesma grade e sorteios da referência
                r[(I, F)] = d["ser"][BCD1]
            ser[(cond, k)] = r
    return ser


def perda(r, fmt):
    """(perda em dB ou None se o hardware não chega a 1e-2, limite_inferior)"""
    xr, er = estado_snr(r["BCD"])
    xh, eh = estado_snr(r[fmt])
    if xh is None or xr is None:
        return None, False
    return max(0.0, xh - xr), (er == "abaixo" and eh == "ok")


def descricao(k: int) -> str:
    p = next(p for p in ALL_PANELS if TCC_CONFIGURATION[p.label] == k)
    return (f"$K$ = {p.K}, IoT = {p.iot_db:g} dB, "
            f"{MODULATION_LABEL.get(p.modulation, p.modulation)}")


def titulo_estacao(g, M, C):
    return f"{g}: $M$ = {M}, $C$ = {C} (circuito {M // C} × {M // C})"


# ---------------------------------------------------------------- figura 1

def figura_snr(ser, configs) -> None:
    """Pontos: SNR necessária para SER = 1e-2, uma figura por par."""
    grupos = [(g, M, C, [k for k in ks if k in configs]) for g, M, C, ks in ESTACOES]
    grupos = [x for x in grupos if x[3]]
    n_lin = sum(len(x[3]) for x in grupos)
    sub = np.linspace(-0.3, 0.3, len(SERIES_FIG1))   # posição de cada série dentro da linha
    X_FORA = 12.2                                    # coluna "não atinge"
    for cond, titulo in CENARIOS.items():
        altura = 1.3 + 0.42 * n_lin + 0.3 * len(grupos)
        fig, ax = plt.subplots(figsize=(LARGURA, altura))
        eixos(ax)
        y, yticks, ylabels, linhas = 0.0, [], [], []
        for g, M, C, ks in grupos:
            ax.text(-10.9, y - 0.75, titulo_estacao(g, M, C), ha="left", va="center",
                    fontsize=8, color=INK_PRIMARY, fontweight="bold")
            for k in ks:
                r = ser[(cond, k)]
                for j, (chave, nome, cor, marc, cheio) in enumerate(SERIES_FIG1):
                    x, est = estado_snr(r[chave])
                    yy = y + sub[j]
                    linhas.append([LETRAS[k], k, g, nome, "" if x is None else f"{x:.3f}", est])
                    if est == "nao_atinge":
                        ax.text(X_FORA, yy, "×", color=VERMELHO, ha="center", va="center",
                                fontsize=8, fontweight="bold", zorder=4)
                        continue
                    ax.plot(x, yy, marker=marc, linestyle="none", markersize=5,
                            color=cor, markerfacecolor=cor if cheio else SURFACE,
                            markeredgecolor=cor if not cheio else SURFACE,
                            markeredgewidth=1.1 if not cheio else 0.5, zorder=3)
                    if est == "abaixo":   # SNR presa no início da grade: seta para a esquerda
                        ax.annotate("", xy=(x - 0.9, yy), xytext=(x - 0.15, yy),
                                    arrowprops=dict(arrowstyle="-|>", color=cor, lw=0.8))
                yticks.append(y)
                ylabels.append(f"{LETRAS[k]} ({k})   {descricao(k)}")
                y += 1
            y += 0.6
        ax.set_yticks(yticks, ylabels)
        ax.set_ylim(y - 0.6 - 0.5, -1.25)
        ax.set_xlim(-11, 13)
        ax.set_xticks([-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, X_FORA],
                      [*[str(v).replace("-", "−") for v in GRADE], "não\natinge"])
        ax.axvline(11.1, color=INK_MUTED, linewidth=0.6, linestyle=":")
        for t in ax.get_yticklabels():
            t.set_color(INK_SECONDARY)
        ax.set_xlabel("SNR para SER = $10^{-2}$ [dB]", color=INK_SECONDARY)
        ax.set_title(titulo, color=INK_PRIMARY, pad=6)
        handles = [Line2D([], [], marker=m, linestyle="none", markersize=5, color=c,
                          markerfacecolor=c if ch else SURFACE,
                          markeredgecolor=c if not ch else SURFACE,
                          markeredgewidth=1.1 if not ch else 0.5, label=n)
                   for _, n, c, m, ch in SERIES_FIG1]
        handles.append(Line2D([], [], marker="$\\leftarrow$", linestyle="none",
                              markersize=7, color=INK_SECONDARY,
                              label="já abaixo de $10^{-2}$ em −10 dB"))
        fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
                   fontsize=7.5, labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, -0.01),
                   columnspacing=1.2, handletextpad=0.4)
        fig.tight_layout(rect=(0, 0.55 / altura, 1, 1))
        salvar(fig, f"snr_necessaria_{cond}{''.join(SUFIXO)}", linhas,
               ["letra", "configuracao", "estacao", "curva", "snr_db", "estado"])


# ---------------------------------------------------------------- figura 2

def utilizacao(rpt: Path) -> dict:
    """{recurso: (usado, disponível)} da primeira tabela do utilizacao.rpt do Vivado."""
    nomes = {"CLB LUTs": "LUT", "CLB Registers": "FF", "Block RAM Tile": "BRAM", "DSPs": "DSP"}
    saida = {}
    for linha in rpt.read_text().splitlines():
        partes = [p.strip() for p in linha.strip().strip("|").split("|")]
        if len(partes) >= 5 and partes[0] in nomes and nomes[partes[0]] not in saida:
            saida[nomes[partes[0]]] = (float(partes[1]), float(partes[4]))
    return saida


def pasta_versao(pasta_fmt: str, arq: str) -> Path:
    p = SERVIDOR / "formatos" / "versoes" / f"{pasta_fmt}_{arq}"
    if not p.exists() and pasta_fmt == "24-12":   # 152 e 114 em <24,12>: pacote_servidor_2023
        p = SERVIDOR / "versoes" / arq
    return p


def custo(pasta_fmt: str, arq: str, cen_tb: str, cen: str):
    """(maior ocupação %, recurso, potência dinâmica W) ou None se a versão não existe."""
    p = pasta_versao(pasta_fmt, arq)
    rpt = p / "trabalho" / "vivado" / "utilizacao.rpt"
    if not rpt.exists():
        return None
    u = utilizacao(rpt)
    rec, (usado, disp) = max(u.items(), key=lambda kv: kv[1][0] / kv[1][1])
    with open(p / "trabalho" / "potencia" / "potencia.csv") as f:
        pot = {r["cenario"]: float(r["dinamica_w"]) for r in csv.DictReader(f)}
    # 4545: o testbench roda as matrizes do TDLA30-10 (as mesmas do TDLA30-5)
    w = pot.get(cen, pot.get(cen_tb))
    return 100 * usado / disp, rec, w


def figura_compromisso(ser) -> None:
    pontos = []
    for cen, arq, cen_sim in ARQUITETURAS:
        for i, ((I, F), (rot, modo, pasta_fmt)) in enumerate(FORMATOS.items()):
            ps = [perda(ser[(cen_sim, k)], (I, F)) for k in CIRCUITO_16]
            nao = any(v is None for v, _ in ps)
            pior = None if nao else max(v for v, _ in ps)
            lim = any(li for _, li in ps)
            c = custo(pasta_fmt, arq, cen_sim, cen)
            pontos.append(dict(cen=cen, arq=arq, i=i, rot=rot, modo=MODO[modo], perda=pior,
                               limite=lim, custo=c))
    X_FORA = 8.0   # posição do "não atinge" no eixo symlog
    for tipo, rotulo_y in (("ocupacao", "Maior ocupação da XCU50 [%]"),
                           ("potencia", "Potência dinâmica [W]")):
        fig, axs = plt.subplots(3, 2, figsize=(LARGURA, 7.6))
        for ax, (cen, arq, _) in zip(axs.flat, ARQUITETURAS):
            eixos(ax, grade_x=True, grade_y=True)
            ax.set_xscale("symlog", linthresh=0.1, linscale=1.0)
            ax.axvspan(0, 0.1, color=FAIXAS[0][1], alpha=0.55, zorder=0, lw=0)
            ax.axvspan(0.1, 3, color=FAIXAS[1][1], alpha=0.45, zorder=0, lw=0)
            for lim in (0.1, 3):
                ax.axvline(lim, color=INK_MUTED, linestyle="--", linewidth=0.8, zorder=1)
            ys, nota, gargalo = [], [], {}
            for p in (q for q in pontos if q["cen"] == cen):
                if p["custo"] is None:
                    nota.append(f"{p['rot']}: não cabe na XCU50")
                    continue
                occ, rec, w = p["custo"]
                y = occ if tipo == "ocupacao" else w
                x = X_FORA if p["perda"] is None else p["perda"]
                ys.append(y)
                ax.plot(x, y, marker=MARC_FORMATO[p["i"]], color=AZUIS[p["i"]],
                        markersize=6, linestyle="none", markeredgecolor=SURFACE,
                        markeredgewidth=0.6, zorder=3)
                gargalo.setdefault(rec, []).append(p["rot"])
            lo, hi = min(ys), max(ys)
            folga = (hi - lo) * 0.15 or hi * 0.1
            ax.set_ylim(lo - folga, hi + folga)
            ax.set_xlim(0, 12)
            ax.set_xticks([0, 0.05, 0.1, 0.3, 1, 3, X_FORA],
                          ["0", "0,05", "0,1", "0,3", "1", "3", "não\natinge"])
            ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                lambda v, _: num(v, 1 if tipo == "ocupacao" else 2)))
            nome_arq = arq.replace("_sistolico", " sistólica")
            ax.set_title(f"{cen}: arquitetura {nome_arq}", color=INK_PRIMARY, pad=4)
            if tipo == "ocupacao":
                # recurso mais usado; quando difere entre formatos, os formatos entre parênteses
                partes = sorted(gargalo.items(), key=lambda kv: -len(kv[1]))
                txt = "gargalo: " + partes[0][0] + "".join(
                    f" ({r} em {', '.join(fs)})" for r, fs in partes[1:])
                nota.insert(0, txt)
            if nota:
                ax.text(0.98, 0.97, "\n".join(nota), transform=ax.transAxes, fontsize=6.3,
                        color=INK_SECONDARY, va="top", ha="right")
        for ax in axs[-1]:
            ax.set_xlabel("Pior perda de SNR, circuito 16 × 16 [dB]", color=INK_SECONDARY)
        for ax in axs[:, 0]:
            ax.set_ylabel(rotulo_y, color=INK_SECONDARY)
        handles = [Line2D([], [], marker=MARC_FORMATO[i], color=AZUIS[i], linestyle="none",
                          markersize=6, markeredgecolor=SURFACE, label=f"{r} {MODO[m]}")
                   for i, (r, m, _) in enumerate(FORMATOS.values())]
        fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=7.5,
                   labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, -0.005))
        fig.text(0.5, 0.995, "BCD-MMSE com 1 iteração; perda = pior entre as configurações "
                 "1 a 8 e 13 a 16 no cenário; Vivado 2023.2 (servidor), 100 MHz",
                 ha="center", va="top", fontsize=7.5, color=INK_SECONDARY)
        fig.tight_layout(rect=(0, 0.06, 1, 0.98), h_pad=1.2)
        linhas = []
        for p in pontos:
            occ, rec, w = p["custo"] if p["custo"] else ("", "", "")
            linhas.append([p["cen"], p["arq"], p["rot"], p["modo"],
                           "nao_atinge" if p["perda"] is None else f"{p['perda']:.3f}",
                           int(p["limite"]), occ if occ == "" else f"{occ:.2f}", rec, w])
        salvar(fig, f"compromisso_{tipo}", linhas,
               ["cenario", "arquitetura", "formato", "modo", "pior_perda_db",
                "perda_limite_inferior", "maior_ocupacao_pct", "recurso", "dinamica_w"])


# ---------------------------------------------------------------- figura 3

def figura_mapa(ser, configs) -> None:
    fmts = list(FORMATOS)
    grupos = [(g, M, C, [k for k in ks if k in configs]) for g, M, C, ks in ESTACOES]
    grupos = [x for x in grupos if x[3]]
    n_lin = sum(len(x[3]) for x in grupos)
    altura = 1.4 + 0.36 * n_lin + 0.3 * len(grupos)
    fig, ax = plt.subplots(figsize=(LARGURA, altura))
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    x0 = 0.0          # início das colunas (os rótulos ficam à esquerda, em x negativo)
    y, linhas = 0.0, []
    for g, M, C, ks in grupos:
        ax.text(-3.9, y + 0.45, titulo_estacao(g, M, C), ha="left", va="center",
                fontsize=8, color=INK_PRIMARY, fontweight="bold")
        y += 0.75
        for k in ks:
            ax.text(-3.9, y + 0.5, f"{LETRAS[k]} ({k})", ha="left", va="center",
                    fontsize=7.5, color=INK_PRIMARY)
            ax.text(-3.15, y + 0.5, descricao(k), ha="left", va="center", fontsize=7,
                    color=INK_SECONDARY)
            for j, fmt in enumerate(fmts):
                vals = {c: perda(ser[(c, k)], fmt) for c in CENARIOS}
                if any(v is None for v, _ in vals.values()):
                    pior_c = next(c for c, (v, _) in vals.items() if v is None)
                    v, cor, txt = None, FAIXAS[2][1], "×"
                else:
                    pior_c = max(vals, key=lambda c: vals[c][0])
                    v = vals[pior_c][0]
                    cor = next(c for lim, c, _ in FAIXAS if round(v, 2) <= lim)
                    txt = ("≥ " if vals[pior_c][1] else "") + num(v)
                ax.add_patch(Rectangle((x0 + j, y), 1, 1, facecolor=cor, edgecolor=SURFACE,
                                       linewidth=1.5))
                ax.text(x0 + j + 0.5, y + 0.36, txt, ha="center", va="center",
                        fontsize=8 if v is not None else 10,
                        color=VERMELHO if v is None else INK_PRIMARY,
                        fontweight="bold" if v is None or v > 3 else "normal")
                ax.text(x0 + j + 0.5, y + 0.78, ABREV_CENARIO[pior_c], ha="center",
                        va="center", fontsize=6.5, color=INK_SECONDARY)
                linhas.append([LETRAS[k], k, g, FORMATOS[fmt][0], MODO[FORMATOS[fmt][1]],
                               *[("nao_atinge" if vals[c][0] is None else f"{vals[c][0]:.3f}")
                                 for c in CENARIOS], pior_c])
            y += 1
        y += 0.3
    for j, fmt in enumerate(fmts):
        rot, modo, _ = FORMATOS[fmt]
        ax.text(x0 + j + 0.5, -0.75, rot, ha="center", va="bottom", fontsize=8,
                color=INK_PRIMARY, fontweight="bold")
        ax.text(x0 + j + 0.5, -0.05, MODO[modo].replace("/", "\n"), ha="center", va="bottom",
                fontsize=6.3, linespacing=1.0,
                color=INK_SECONDARY)
    ax.set_xlim(-4.0, x0 + len(fmts) + 0.05)
    ax.set_ylim(y, -1.25)
    handles = [Patch(facecolor=c, edgecolor=INK_MUTED, linewidth=0.4, label=t)
               for _, c, t in FAIXAS]
    handles.append(Line2D([], [], marker="$\\times$", color=VERMELHO, linestyle="none",
                          markersize=7, label="não chega a $10^{-2}$"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=7.5,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.5, 0.0, "Célula: pior perda de SNR em SER = $10^{-2}$ entre os 5 pares "
             "(par embaixo do número), BCD-MMSE com 1 iteração; ≥: referência já abaixo de "
             "$10^{-2}$ em −10 dB", ha="center", va="top", fontsize=6.5, color=INK_SECONDARY)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    salvar(fig, f"mapa_perda_estacoes{''.join(SUFIXO)}", linhas,
           ["letra", "configuracao", "estacao", "formato", "modo",
            *[f"perda_{c}" for c in CENARIOS], "pior_par"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--configs", help="nomes das configurações (ex.: 1A,1D,2E,3B); padrão: as 16")
    args = ap.parse_args()
    if args.configs:
        por_letra = {v: k for k, v in LETRAS.items()}
        letras = [c.strip().upper() for c in args.configs.split(",")]
        configs = {por_letra[c] for c in letras}
        SUFIXO.append("_" + "".join(sorted(letras)))
    else:
        configs = set(LETRAS)
    ser = carregar()
    figura_snr(ser, configs)
    if not SUFIXO:   # a figura 2 não depende de --configs
        figura_compromisso(ser)
    figura_mapa(ser, configs)


if __name__ == "__main__":
    main()
