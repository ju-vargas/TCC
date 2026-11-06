#!/usr/bin/env python3
"""
Figuras da [5] com os cenários lado a lado: para cada configuração, uma figura com um
gráfico por formato candidato (formato fixo) e, em cada gráfico, uma linha por par
(N, portadora). Linha contínua com marcador = BCD-MMSE com a inversa no hardware HLS;
tracejada fina da mesma cor = a referência ideal (float64) do mesmo par.

Junta todas as pastas de resultados/5_candidatos/. Um modo (quantização) por vez,
sempre com AP_SAT.

Também grava perdas.png: a perda de SNR em SER = 1e-2 de cada formato em relação à
referência do mesmo par, um gráfico por configuração e um ponto por par.

Grava em resultados/5_candidatos/figuras_por_formato/<quant>/iter<T>/configuracao_<k>.png,
perdas.png e os .pdf.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_cenarios.py [--quant AP_TRN] [--iteracao 1]
"""

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib.pyplot as plt                       # noqa: E402
import numpy as np                                    # noqa: E402

from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (INK_PRIMARY, INK_SECONDARY, SURFACE,  # noqa: E402
                              _style_axes, configuration_title)
from figuras_candidatos import pasta_ref  # noqa: E402
from figuras_formatos import LIMIAR_DB, condicoes, ler, snr_no_alvo  # noqa: E402

CANDIDATOS = AQUI / "resultados" / "5_candidatos"
#: Uma cor por par, na ordem fixa da paleta (node scripts/validate_palette.js
#: "#2a78d6,#eb6834,#1baf7a,#eda100,#e87ba4" -> ALL CHECKS PASS nos pares vizinhos).
#: Como as linhas se cruzam, o marcador também muda de par para par.
CORES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
MARCADORES = ("o", "s", "^", "D", "v")
SNR_REF = np.arange(-10, 11, 2, dtype=float)
SER_MIN = 1e-4
#: Eixo de perda: linear até o limiar de 0,1 dB e logarítmico acima; perda maior que o
#: teto, ou SER que não chega a 1e-2, vira uma barra até o teto, hachurada com x.
TETO_DB = 10.0


def figura_perdas(rodadas, ref, conds, formatos, estilo, info, curva, titulo, saida):
    paineis = {p.label: p for p in ALL_PANELS}
    rotulos = sorted({d["rotulo"] for d in rodadas}, key=lambda r: TCC_CONFIGURATION[r])
    ncol = 4
    nlin = int(np.ceil(len(rotulos) / ncol))
    fig, axes = plt.subplots(nlin, ncol, figsize=(4.2 * ncol, 2.9 * nlin + 0.8), squeeze=False,
                             sharey=True)
    fig.patch.set_facecolor(SURFACE)
    # Barras agrupadas por formato, os pares sempre na mesma ordem dentro do grupo
    larg = 0.84 / len(conds)
    desloc = (np.arange(len(conds)) - (len(conds) - 1) / 2) * larg
    for j, rotulo in enumerate(rotulos):
        ax = axes[j // ncol][j % ncol]
        ax.set_facecolor(SURFACE)
        for k, c in enumerate(conds):
            r = snr_no_alvo(SNR_REF, ref[c][rotulo][curva])
            # Referência já abaixo de 1e-2 na menor SNR da grade: o cruzamento real fica
            # antes de -10 dB, e a perda medida é só um limite inferior (barra hachurada)
            fora = ref[c][rotulo][curva][0] < 1e-2
            xs, ys, xt = [], [], []
            for n_fmt, fmt in enumerate(formatos):
                d = next((d for d in rodadas if d["rotulo"] == rotulo and d["condicao"] == c
                          and (d["int_bits"], d["frac_bits"]) == fmt), None)
                if d is None:
                    continue
                x = snr_no_alvo(d["snr_db"], d["ser"][curva])
                if x is None or r is None or x - r > TETO_DB:
                    xt.append(n_fmt + desloc[k])
                else:
                    xs.append(n_fmt + desloc[k])
                    ys.append(max(0.0, x - r))
            cor = estilo[c][0]
            if fora:
                ax.bar(xs, ys, width=larg, facecolor=SURFACE, edgecolor=cor, hatch="////",
                       linewidth=0.8, zorder=3)
                # Perda zero aqui quer dizer que as duas curvas já começam abaixo de 1e-2:
                # a perda não foi medida, e a barra sumiria
                for x0, y0 in zip(xs, ys):
                    if y0 == 0:
                        ax.text(x0, 0.004, "?", ha="center", va="bottom", fontsize=6.5,
                                color=cor, fontweight="bold", zorder=4)
            else:
                ax.bar(xs, ys, width=larg, color=cor, edgecolor=SURFACE, linewidth=0.5, zorder=3)
            ax.bar(xt, [TETO_DB] * len(xt), width=larg, facecolor=SURFACE, edgecolor=cor,
                   hatch="xx", linewidth=0.8, zorder=3)
        ax.axhline(LIMIAR_DB, color=INK_SECONDARY, linestyle="--", linewidth=0.9, zorder=2)
        ax.set_yscale("symlog", linthresh=LIMIAR_DB, linscale=1.0)
        ax.set_ylim(0, TETO_DB * 1.4)
        ax.set_yticks([0, 0.05, 0.1, 1, 10])
        ax.set_yticklabels(["0", "0,05", "0,1", "1", "10"])
        ax.set_xticks(range(len(formatos)))
        ax.set_xticklabels([f"<{i + f},{i}>" for i, f in formatos], rotation=45, ha="right",
                           fontsize=7.5)
        ax.grid(True, axis="y", color="#e4e3df", linewidth=0.7, zorder=0)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        ax.tick_params(colors=INK_SECONDARY, labelsize=8, length=3, width=0.8)
        ax.set_title(configuration_title(paineis[rotulo]), fontsize=8, color=INK_PRIMARY, pad=4)
        if j % ncol == 0:
            ax.set_ylabel("Perda em SER = 1e-2 (dB)", fontsize=8.5, color=INK_SECONDARY)
    for j in range(len(rotulos), nlin * ncol):
        axes[j // ncol][j % ncol].axis("off")
    from matplotlib.patches import Patch
    h = [Patch(facecolor=estilo[c][0], edgecolor=SURFACE) for c in conds]
    lab = [f"{c}: $N$ = {info[c][0]}, $f_c$ = {info[c][1]:g} GHz".replace(".", ",") for c in conds]
    h += [plt.Line2D([], [], color=INK_SECONDARY, linestyle="--", linewidth=0.9),
          Patch(facecolor=SURFACE, edgecolor=INK_SECONDARY, hatch="xx"),
          Patch(facecolor=SURFACE, edgecolor=INK_SECONDARY, hatch="////"),
          plt.Line2D([], [], color=INK_SECONDARY, marker="$?$", linestyle="none", markersize=6)]
    lab += [f"limiar de {LIMIAR_DB:g} dB".replace(".", ","),
            f"mais de {TETO_DB:g} dB ou não chega a 1e-2",
            "hachurada: referência já abaixo de 1e-2 em -10 dB\n(perda é um limite inferior)",
            "?: as duas curvas já abaixo de 1e-2 em -10 dB\n(perda não medida)"]
    fig.legend(h, lab, loc="lower center", ncol=4, frameon=False, fontsize=8.5,
               labelcolor=INK_SECONDARY)
    fig.suptitle(f"Perda de SNR de cada formato em relação à referência ideal do mesmo par\n"
                 f"{titulo}", fontsize=10.5, color=INK_PRIMARY)
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    png = saida / "perdas.png"
    fig.savefig(png, dpi=180, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quant", default="AP_TRN", help="AP_TRN ou AP_RND")
    ap.add_argument("--iteracao", type=int, default=1)
    a = ap.parse_args()
    curva = f"BCD-MMSE (iter {a.iteracao})"
    rodadas = [d for p in sorted(CANDIDATOS.iterdir()) if (p / "dados").is_dir()
               for d in ler(p) if d["quant"] == a.quant and d["overflow"] == "AP_SAT"]
    conds = condicoes(rodadas)
    ref = {c: json.loads((pasta_ref(c) / "bcd_iterations_results.json").read_text()) for c in conds}
    formatos = sorted({(d["int_bits"], d["frac_bits"]) for d in rodadas},
                      key=lambda f: (f[0], f[1]))
    estilo = {c: (CORES[i], MARCADORES[i]) for i, c in enumerate(conds)}
    info = {d["condicao"]: (d["n_amostras"], d["portadora_ghz"]) for d in rodadas}

    saida = CANDIDATOS / "figuras_por_formato" / a.quant / f"iter{a.iteracao}"
    saida.mkdir(parents=True, exist_ok=True)
    paineis = {p.label: p for p in ALL_PANELS}
    for rotulo in sorted({d["rotulo"] for d in rodadas}, key=lambda r: TCC_CONFIGURATION[r]):
        doc = [d for d in rodadas if d["rotulo"] == rotulo]
        # Corta o eixo de SNR onde todas as curvas já estão abaixo de SER_MIN
        ultimo = -10.0
        for d in doc:
            y = np.asarray(d["ser"][curva], float)
            ultimo = max([ultimo] + [s for s, v in zip(d["snr_db"], y) if v >= SER_MIN])
        for c in conds:
            y = np.asarray(ref[c][rotulo][curva], float)
            ultimo = max([ultimo] + [s for s, v in zip(SNR_REF, y) if v >= SER_MIN])
        xmax = min(10.0, ultimo + 2)

        ncol = 4
        nlin = int(np.ceil((len(formatos) + 1) / ncol))
        fig, axes = plt.subplots(nlin, ncol, figsize=(3.3 * ncol, 3.2 * nlin), squeeze=False,
                                 sharex=True, sharey=True)
        fig.patch.set_facecolor(SURFACE)
        for j, (i_bits, f_bits) in enumerate(formatos):
            ax = axes[j // ncol][j % ncol]
            _style_axes(ax)
            for c in conds:
                cor, marc = estilo[c]
                yr = np.asarray(ref[c][rotulo][curva], float)
                ax.plot(SNR_REF, np.where(yr <= 0, np.nan, yr), color=cor, linestyle="--",
                        linewidth=1.0, alpha=0.9, zorder=2)
                d = next((d for d in doc if d["condicao"] == c
                          and (d["int_bits"], d["frac_bits"]) == (i_bits, f_bits)), None)
                if d is None:
                    continue
                y = np.asarray(d["ser"][curva], float)
                n, fc = info[c]
                ax.plot(d["snr_db"], np.where(y <= 0, np.nan, y), color=cor, linestyle="-",
                        marker=marc, markersize=4.5, linewidth=1.6, markeredgecolor=SURFACE,
                        markeredgewidth=0.6, zorder=3,
                        label=f"{c}: $N$ = {n}, $f_c$ = {fc:g} GHz".replace(".", ","))
            ax.set_xlim(-10.3, xmax + 0.3)
            ax.set_ylim(SER_MIN, 1)
            ax.set_title(f"ap_fixed<{i_bits + f_bits},{i_bits}>", fontsize=9.5,
                         color=INK_PRIMARY, pad=5)
            if j % ncol == 0:
                ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
            ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)
            ax.xaxis.set_tick_params(labelbottom=True)
        for j in range(len(formatos), nlin * ncol):
            axes[j // ncol][j % ncol].axis("off")
        leg = axes[-1][-1]
        h, lab = axes[0][0].get_legend_handles_labels()
        h += [plt.Line2D([], [], color=INK_SECONDARY, linestyle="--", linewidth=1.0)]
        lab += ["referência ideal (float64),\nna cor do par"]
        leg.legend(h, lab, loc="center", frameon=False, fontsize=8.5, labelcolor=INK_SECONDARY)
        fig.suptitle(f"{configuration_title(paineis[rotulo]).replace(chr(10), ': ')}\n"
                     f"{curva}, inversa no hardware HLS, {a.quant}/AP_SAT", fontsize=10.5,
                     color=INK_PRIMARY)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        png = saida / f"configuracao_{TCC_CONFIGURATION[rotulo]}.png"
        fig.savefig(png, dpi=180, facecolor=SURFACE, bbox_inches="tight")
        fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
        plt.close(fig)
    figura_perdas(rodadas, ref, conds, formatos, estilo, info, curva,
                  f"{curva}, inversa no hardware HLS, {a.quant}/AP_SAT", saida)
    print(f"{len({d['rotulo'] for d in rodadas})} figuras e perdas.png em {saida}/")


if __name__ == "__main__":
    main()
