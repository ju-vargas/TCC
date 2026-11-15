"""Parte de cada etapa da inversão em LUT, DSP e potência dinâmica (Vivado do servidor, projeto roteado).

Dados: hardware/etapas/etapas_dominantes.csv (gerado por hardware/etapas/etapas_dominantes.py).
Cada barra é a média entre os formatos da arquitetura; o _data.csv guarda também o mínimo e o
máximo, e a figura informa a maior diferença entre formatos.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib                                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
from matplotlib.patches import Patch                    # noqa: E402

import figuras_analise_grupos as fag                    # noqa: E402
from dbp_sim.plotting import GRID, INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE  # noqa: E402

DADOS = AQUI.parent.parent / "hardware" / "etapas" / "etapas_dominantes.csv"
fag.SAIDA = AQUI.parent.parent / "hardware" / "resultados_servidor" / "figuras"
fag.DPI = 600
LARGURA = 6.3
plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["pdf.fonttype"] = 42

ARQS = [("sem_otimizacao", "Without opt., 16×16"), ("sem_otimizacao_32x32", "Without opt., 32×32"), ("9090", "TDLA30-5"), ("4545", "TDLA30-10"),
        ("606", "TDLA30-75"), ("455", "TDLC300-100"), ("152_sistolico", "TDLA30-300"),
        ("114_sistolico", "TDLB100-400")]
# Etapas na ordem do pipeline: rampa ordinal violeta (validada com --ordinal em 2026-11-13)
# e cinza para o restante.
ETAPAS = [("lu", "LU", "#2b1f6b", "white"), ("df", "D and F", "#4d3db5", "white"),
          ("fs", "Forward subst.", "#7b6cdc", "white"), ("inv", "Inversion", "#a79cec", INK_PRIMARY),
          ("restante", "Other (memories, control)", "#d3d1ca", INK_PRIMARY)]
PAINEIS = [("lut", "LUT"), ("dsp", "DSP"), ("pdin_w", "Dynamic power")]


def ler():
    partes = defaultdict(list)
    for r in csv.DictReader(open(DADOS)):
        t = float(r["total"])
        if t == 0:
            continue
        partes[(r["arquitetura"], r["grandeza"])].append(
            [100 * float(r[e]) / t for e, *_ in ETAPAS])
    return partes


def main():
    partes = ler()
    fig, axs = plt.subplots(1, 3, figsize=(LARGURA, 2.9), sharey=True)
    fig.patch.set_facecolor(SURFACE)
    linhas, maior_dif = [], 0.0
    for ax, (g, titulo) in zip(axs, PAINEIS):
        ax.set_facecolor(SURFACE)
        for i, (arq, nome) in enumerate(ARQS):
            v = partes[(arq, g)]
            if not v:  # 32x32: sem potência
                continue
            media = [sum(x[k] for x in v) / len(v) for k in range(len(ETAPAS))]
            esq = 0.0
            for k, (e, _, cor, tinta) in enumerate(ETAPAS):
                mn, mx = min(x[k] for x in v), max(x[k] for x in v)
                maior_dif = max(maior_dif, mx - mn)
                linhas.append([g, nome, e, round(media[k], 1), round(mn, 1), round(mx, 1), len(v)])
                ax.barh(i, media[k], left=esq, color=cor, edgecolor=SURFACE, linewidth=1, height=0.68)
                if media[k] >= 9:
                    ax.text(esq + media[k] / 2, i, f"{media[k]:.0f}", ha="center", va="center",
                            fontsize=6.5, color=tinta)
                esq += media[k]
        ax.set_xlim(0, 100)
        ax.set_xticks(range(0, 101, 25))
        ax.set_xlabel("Percentage of total (%)", fontsize=7.5, color=INK_SECONDARY)
        ax.set_title(titulo, fontsize=8, color=INK_PRIMARY)
        ax.tick_params(labelsize=7, colors=INK_SECONDARY, length=0)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        for s in ax.spines.values():
            s.set_visible(False)
    axs[0].set_yticks(range(len(ARQS)))
    axs[0].set_yticklabels([n for _, n in ARQS])
    axs[0].invert_yaxis()
    fig.legend(handles=[Patch(facecolor=c, edgecolor=SURFACE, label=n) for _, n, c, _ in ETAPAS],
               loc="lower center", ncol=5, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.02),
               handlelength=1.2, columnspacing=1.2, labelcolor=INK_SECONDARY)
    fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=1.0)
    print(f"maior diferença entre formatos: {maior_dif:.1f} pontos")
    fag.salvar(fig, "etapas_dominantes", linhas,
               ["grandeza", "arquitetura", "etapa", "media_pct", "min_pct", "max_pct", "n_formatos"])


if __name__ == "__main__":
    main()
