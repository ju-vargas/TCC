#!/usr/bin/env python3
"""
Figuras e tabela da rodada dos formatos candidatos (varredura_formatos.py com poucos
formatos, todas as configurações e os 5 pares (N, portadora)).

Para cada configuração, uma figura com um gráfico por par (N, portadora): a SER do
BCD-MMSE (1 iteração, ou --iteracao) com a inversa no hardware HLS em cada
formato candidato e modo, e a referência ideal (float64, preta e tracejada).
Cor = formato; linha contínua = arredondamento (AP_RND), pontilhada = truncamento
(AP_TRN).

Também grava perdas_candidatos.csv: a perda de SNR em SER = 10^-2 em relação à
referência, por candidato, configuração, par e iteração, e imprime o pior caso.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_candidatos.py resultados/5_candidatos/<pasta>
"""

import argparse
import csv
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib.pyplot as plt                       # noqa: E402
import numpy as np                                    # noqa: E402

from dbp_sim.params import ALL_PANELS, M1_Driver, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (INK_PRIMARY, INK_SECONDARY, SURFACE,  # noqa: E402
                              _style_axes, configuration_title)
from figuras_formatos import snr_no_alvo  # noqa: E402

REFERENCIA = AQUI / "resultados" / "1_referencia_float" / "curvas"
#: Cores validadas (node scripts/validate_palette.js "#2a78d6,#eb6834" --pairs all
#: -> ALL CHECKS PASS); o modo vai no tipo de linha, e a referência é preta tracejada
CORES = ("#2a78d6", "#eb6834")
LINHA = {"AP_RND": "-", "AP_TRN": ":"}
MARCADOR = {"AP_RND": "o", "AP_TRN": "s"}
REF_COR = "#0b0b0b"


def pasta_ref(cond: str) -> Path:
    n, fc = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}[cond]
    return next(p for p in REFERENCIA.iterdir()
                if p.name.endswith(f"_N{n}_{fc / 1e9:g}GHz") and cond in p.name.split("_")[0].split("+"))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("pasta")
    parser.add_argument("--iteracao", type=int, default=1)
    args = parser.parse_args()
    pasta = Path(args.pasta)
    rodadas = [json.loads(f.read_text()) for f in sorted(pasta.glob("dados/*/*/*.json"))]
    curva = f"BCD-MMSE (iter {args.iteracao})"
    conds = sorted({d["condicao"] for d in rodadas},
                   key=lambda c: (-next(d["n_amostras"] for d in rodadas if d["condicao"] == c),
                                  next(d["portadora_ghz"] for d in rodadas if d["condicao"] == c)))
    ref = {c: json.loads((pasta_ref(c) / "bcd_iterations_results.json").read_text()) for c in conds}
    formatos = sorted({(d["int_bits"], d["frac_bits"]) for d in rodadas})
    cor = {f: CORES[i % len(CORES)] for i, f in enumerate(formatos)}

    # Tabela de perdas (todas as iterações)
    linhas = []
    for d in rodadas:
        for c, serie in d["ser"].items():
            r = snr_no_alvo(range(-10, 11, 2), ref[d["condicao"]][d["rotulo"]][c])
            x = snr_no_alvo(d["snr_db"], serie)
            linhas.append({"formato": f"ap_fixed<{d['int_bits'] + d['frac_bits']},{d['int_bits']}>",
                           "quant": d["quant"], "overflow": d["overflow"],
                           "configuracao": d["configuracao"], "condicao": d["condicao"],
                           "n_amostras": d["n_amostras"], "portadora_ghz": f"{d['portadora_ghz']:g}",
                           "curva": c, "falhas": d["falhas"],
                           "perda_db": "" if (x is None or r is None) else f"{max(0.0, x - r):.3f}",
                           "atinge_1e-2": "sim" if x is not None else "não"})
    with open(pasta / "perdas_candidatos.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print(f"{pasta / 'perdas_candidatos.csv'}: {len(linhas)} linhas")
    for (fmt, q, o) in sorted({(l["formato"], l["quant"], l["overflow"]) for l in linhas}):
        for c in sorted({l["curva"] for l in linhas}):
            sel = [l for l in linhas if (l["formato"], l["quant"], l["overflow"], l["curva"]) == (fmt, q, o, c)]
            p = [float(l["perda_db"]) for l in sel if l["perda_db"]]
            nao = sum(1 for l in sel if l["atinge_1e-2"] == "não")
            falhas = sum(int(l["falhas"]) for l in sel)
            pior = max(sel, key=lambda l: float(l["perda_db"] or 99))
            print(f"  {fmt:16s} {q}/{o}  {c}: perda máx. {max(p):.2f} dB "
                  f"(configuração {pior['configuracao']}, {pior['condicao']}), média {np.mean(p):.3f} dB, "
                  f"{nao} sem chegar a 1e-2, {falhas} falhas")

    # Figuras
    saida = pasta / "figuras" / f"iter{args.iteracao}"
    saida.mkdir(parents=True, exist_ok=True)
    paineis = {p.label: p for p in ALL_PANELS}
    for rotulo in sorted({d["rotulo"] for d in rodadas}, key=lambda r: TCC_CONFIGURATION[r]):
        painel = paineis[rotulo]
        fig, axes = plt.subplots(2, 3, figsize=(12.3, 7.2), squeeze=False)
        fig.patch.set_facecolor(SURFACE)
        for i, cond in enumerate(conds):
            ax = axes[i // 3][i % 3]
            _style_axes(ax)
            snr = np.arange(-10, 11, 2, dtype=float)
            for d in rodadas:
                if d["rotulo"] != rotulo or d["condicao"] != cond:
                    continue
                f = (d["int_bits"], d["frac_bits"])
                y = np.asarray(d["ser"][curva], float)
                ax.plot(d["snr_db"], np.where(y <= 0, np.nan, y), color=cor[f],
                        linestyle=LINHA.get(d["quant"][:6], "-"),
                        marker=MARCADOR.get(d["quant"][:6], "o"), markersize=4.5,
                        linewidth=1.8, markeredgecolor=SURFACE, markeredgewidth=0.6,
                        label=f"ap_fixed<{f[0] + f[1]},{f[0]}> {d['quant']}", zorder=3)
            yr = np.asarray(ref[cond][rotulo][curva], float)
            ax.plot(snr, np.where(yr <= 0, np.nan, yr), color=REF_COR, linestyle="--",
                    linewidth=1.4, label="referência ideal (float64)", zorder=4)
            ax.set_xlim(-10.5, 10.5)
            d0 = next(d for d in rodadas if d["condicao"] == cond)
            ax.set_title(f"{cond}: $N$ = {d0['n_amostras']}, $f_c$ = "
                         f"{d0['portadora_ghz']:g} GHz".replace(".", ","), fontsize=9,
                         color=INK_PRIMARY, pad=6)
            if i % 3 == 0:
                ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
            ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)
        leg = axes[1][2]
        leg.axis("off")
        h, lab = axes[0][0].get_legend_handles_labels()
        leg.legend(h, lab, loc="center", frameon=False, fontsize=9, labelcolor=INK_SECONDARY)
        fig.suptitle(f"{configuration_title(painel).replace(chr(10), ': ')}\n"
                     f"{curva}, inversa no hardware HLS, formatos candidatos", fontsize=10.5,
                     color=INK_PRIMARY)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        png = saida / f"configuracao_{TCC_CONFIGURATION[rotulo]}.png"
        fig.savefig(png, dpi=180, facecolor=SURFACE, bbox_inches="tight")
        fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
        plt.close(fig)
    print(f"  figuras em {saida}/")


if __name__ == "__main__":
    main()
