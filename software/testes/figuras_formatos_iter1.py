#!/usr/bin/env python3
"""
SER x SNR com os formatos sobrepostos: uma figura por cenário, um painel por configuração.
Em cada painel, LMMSE, ZF e BCD-MMSE com 1 iteração da referência float64, e o BCD-MMSE com
1 iteração com a inversa do hardware HLS em <22,12>, <24,12> e <28,14> (AP_RND_ZERO,
AP_WRAP), da rodada de figuras_modo_fixo.py. Cores das figuras bcd_iterations: LMMSE
vermelho, ZF rosa, BCD-MMSE (iter 1) laranja; os formatos ficam no laranja e se separam
pelo traço e pelo marcador.

Saída: <pasta>/figuras/formatos_iter1/<cenário>_N<N>_<GHz>GHz/ser_formatos_iter1.{png,pdf}
(e o _data.csv da figura).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_formatos_iter1.py [resultados/5_candidatos/modo_fixo_3dB]
"""

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

from dbp_sim.params import ALL_PANELS, M1_Driver, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (BCD_ITERATION_MARKERS, BCD_ITERATION_RAMP,  # noqa: E402
                              INK_PRIMARY, INK_SECONDARY, ITERATION_ZF_COLOR,
                              SERIES_STYLE, SURFACE, _style_axes, configuration_title)
from figuras_modo_fixo import PASTA, pasta_referencia   # noqa: E402

STEM = "ser_formatos_iter1"
BCD1 = "BCD-MMSE (iter 1)"
LARANJA = BCD_ITERATION_RAMP[0]
# curva -> (cor, marcador, traço); formatos (I, F) com AP_RND_ZERO/AP_WRAP
CURVAS = {
    "LMMSE": (SERIES_STYLE["LMMSE"][0], SERIES_STYLE["LMMSE"][1], "-"),
    "ZF": (ITERATION_ZF_COLOR, SERIES_STYLE["ZF"][1], "-"),
    f"{BCD1}, float": (LARANJA, BCD_ITERATION_MARKERS[0], "-"),
}
FORMATOS = {(12, 10): ("o", "--"), (12, 12): ("s", "-."), (14, 14): ("D", ":")}
for (I, F), (m, t) in FORMATOS.items():
    CURVAS[f"{BCD1}, <{I + F},{I}>"] = (LARANJA, m, t)


def main() -> None:
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else PASTA
    condicoes = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}
    for cond in sorted(p.name for p in (pasta / "dados").iterdir()):
        ref_pasta = pasta_referencia(cond)
        ref = json.loads((ref_pasta / "bcd_iterations_results.json").read_text())
        resultados, grade = {}, None
        for rotulo in ref:
            k = TCC_CONFIGURATION[rotulo]
            r = {"LMMSE": ref[rotulo]["LMMSE"], "ZF": ref[rotulo]["ZF"],
                 f"{BCD1}, float": ref[rotulo][BCD1]}
            for I, F in FORMATOS:
                arq = pasta / "dados" / cond / f"configuracao_{k}" / f"{I}_{F}_AP_RND_ZERO_AP_WRAP.json"
                d = json.loads(arq.read_text())
                if grade is None:
                    grade = d["snr_db"]
                # Mesma grade e mesmos sorteios da referência: a comparação ponto a ponto vale
                assert d["snr_db"] == grade and len(ref[rotulo]["LMMSE"]) == len(grade), arq
                r[f"{BCD1}, <{I + F},{I}>"] = d["ser"][BCD1]
            resultados[rotulo] = r
        paineis = [p for p in ALL_PANELS if p.label in resultados]
        saida = pasta / "figuras" / "formatos_iter1" / ref_pasta.name
        desenhar(resultados, paineis, grade, saida, cond, *condicoes[cond])


def desenhar(resultados, paineis, grade, saida: Path, cond: str, n: int, fc: float) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    snr = np.asarray(grade, dtype=float)
    ncols = 3
    nrows = int(np.ceil(len(paineis) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.1 * ncols, 3.5 * nrows), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for i, painel in enumerate(paineis):
        ax = axes[i // ncols][i % ncols]
        _style_axes(ax)
        for curva, (cor, marcador, traco) in CURVAS.items():
            y = np.asarray(resultados[painel.label][curva], dtype=float)
            y = np.where(y <= 0, np.nan, y)          # eixo log: tira os pontos sem erro
            ax.plot(snr, y, color=cor, marker=marcador, linestyle=traco, markersize=4.5,
                    linewidth=1.6, markeredgecolor=SURFACE, markeredgewidth=0.6,
                    label=curva, zorder=3)
        ax.set_title(configuration_title(painel), fontsize=9, color=INK_PRIMARY, pad=8)
        if i % ncols == 0:
            ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
        if i // ncols == nrows - 1 or i + ncols >= len(paineis):
            ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)
    for j in range(len(paineis), nrows * ncols):
        axes[j // ncols][j % ncols].set_visible(False)

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=9.5,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, -0.005), handlelength=3.0,
               columnspacing=1.6)
    titulo = (f"Condição de teste: {cond.replace('+', ', ')}   |   $N$ = {n}   |   "
              + f"$f_c$ = {fc / 1e9:g} GHz".replace(".", ",")
              + "   |   inversa do BCD-MMSE: float64 e hls ap_fixed<W,I,AP_RND_ZERO,AP_WRAP>")
    fig.text(0.5, 0.985, titulo, ha="center", va="top", fontsize=9.5, color=INK_SECONDARY)
    fig.tight_layout(rect=(0, 0.06, 1, 0.965))
    png = saida / f"{STEM}.png"
    fig.savefig(png, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(saida / f"{STEM}.pdf", facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    with open(saida / f"{STEM}_data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["configuracao", "curva", *[f"{s:g}" for s in grade]])
        for painel in paineis:
            for curva in CURVAS:
                w.writerow([TCC_CONFIGURATION[painel.label], curva,
                            *resultados[painel.label][curva]])
    print(png)


if __name__ == "__main__":
    main()
