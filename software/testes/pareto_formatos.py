#!/usr/bin/env python3
"""
Fronteira de Pareto dos formatos ap_fixed<W,I> da inversa de G_c: perda de SNR contra o
float64 (em SER = 1e-2) x custo (bits W, DSP e LUT), com AP_TRN/AP_SAT.

A perda de cada formato é a pior entre as configurações e condições da varredura [4]
(configurações 1, 6, 8, 10 e 12; TDLA30-5 e TDLA30-300). Os formatos das rodadas de
candidatos ([5]) entram com a pior perda nessas mesmas configurações e condições, e com
marcador vazado, porque usam a grade inteira de SNR (outros sorteios).

O custo em DSP e LUT vem da síntese HLS sem diretivas, 16 x 16
(hardware/cholesky_hardware/sintetizar_formatos.py -> sinteses/formatos_16x16/recursos.csv).
Formato sem síntese fica fora das figuras de DSP e LUT.

Um formato está na fronteira quando nenhum outro custa o mesmo ou menos e perde menos.
Perda acima do teto do gráfico, ou SER que não chega a 1e-2, é desenhada no teto.

Grava em resultados/pareto/: pareto_iter<T>.png (três painéis: W, DSP, LUT) e
pareto.csv.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python pareto_formatos.py
        [--varredura resultados/4_varredura_formatos/v2_casos_extremos] [--teto 1.0]
"""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figuras_formatos import AQUI, LIMIAR_DB, REF_COR, SURFACE, INK_SECONDARY, ler, perdas

#: Uma cor por número de iterações, da mesma rampa ordinal das outras figuras.
CORES = {1: "#86b6ef", 2: "#3987e5", 3: "#184f95", 4: "#0d366b"}
MODO = ("AP_TRN", "AP_SAT")
RECURSOS = AQUI.parent.parent / "hardware" / "cholesky_hardware" / "sinteses" / "formatos_16x16" / "recursos.csv"
CANDIDATOS = sorted(p for p in (AQUI / "resultados" / "5_candidatos").iterdir() if p.is_dir())


def piores(rodadas, curva, casos):
    """{(I, F): pior perda (None = não cruza) entre os casos (config, cond)}, só TRN/SAT."""
    p = perdas([d for d in rodadas if (d["quant"], d["overflow"]) == MODO], curva)
    por_formato = {}
    for (k, cond, i, f, _, _), v in p.items():
        if (str(k), cond) in casos:
            por_formato.setdefault((int(i), int(f)), []).append(v)
    saida = {}
    for fmt, vs in por_formato.items():
        if len(vs) < len(casos):
            continue                          # formato com casos faltando: fora
        saida[fmt] = None if any(v is None for v in vs) else max(vs)
    return saida


def fronteira(pontos, eps=1e-3):
    """pontos: [(custo, perda ou inf, fmt)]. Devolve os fmt na fronteira. Ganho menor que
    eps dB não conta (perdas de 0,0001 dB são ruído de Monte Carlo)."""
    na = set()
    melhor = np.inf
    for custo, perda, fmt in sorted(pontos, key=lambda x: (x[0], x[1])):
        if perda < melhor - eps:
            na.add(fmt)
            melhor = perda
    return na


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--varredura", default=str(AQUI / "resultados" / "4_varredura_formatos" / "v2_casos_extremos"))
    ap.add_argument("--teto", type=float, default=1.0, help="teto do eixo de perda (dB)")
    a = ap.parse_args()
    varredura = Path(a.varredura)
    r4 = ler(varredura)
    casos = {(str(d["configuracao"]), d["condicao"]) for d in r4}
    r5 = [d for pasta in CANDIDATOS for d in ler(pasta)
          if (str(d["configuracao"]), d["condicao"]) in casos]

    recursos = {}
    if RECURSOS.exists():
        with open(RECURSOS) as fh:
            for linha in csv.DictReader(fh):
                if int(linha["n"]) == 16:
                    recursos[(int(linha["int_bits"]), int(linha["frac_bits"]))] = linha

    destino = AQUI / "resultados" / "pareto"
    destino.mkdir(exist_ok=True)
    linhas_csv = []
    eixos = (("W", "Bits por parte (W = I + F)"), ("DSP", "DSP (síntese sem diretivas, 16 x 16)"),
             ("LUT", "LUT (síntese sem diretivas, 16 x 16)"))
    for it in (1, 2, 3, 4):
        curva = f"BCD-MMSE (iter {it})"
        p4, p5 = piores(r4, curva, casos), piores(r5, curva, casos)
        formatos ={f: ("[5]", v) for f, v in p5.items() if f not in p4}
        formatos.update({f: ("[4]", v) for f, v in p4.items()})

        fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
        fig.patch.set_facecolor(SURFACE)
        for ax, (chave, rotulo) in zip(axs, eixos):
            pontos = []
            for (i, f), (origem, v) in formatos.items():
                if chave == "W":
                    custo = i + f
                elif (i, f) in recursos:
                    custo = int(recursos[(i, f)][chave])
                else:
                    continue
                pontos.append((custo, np.inf if v is None else v, (i, f)))
            na = fronteira(pontos)
            for custo, perda, fmt in pontos:
                origem = formatos[fmt][0]
                y = min(perda, a.teto)
                ax.scatter(custo, y, s=36 if fmt in na else 18,
                           facecolors=(CORES[it] if origem == "[4]" else "none"),
                           edgecolors=CORES[it], alpha=1.0 if fmt in na else 0.35, zorder=3)
                if fmt in na:
                    ax.annotate(f"<{sum(fmt)},{fmt[0]}>", (custo, y), fontsize=7,
                                xytext=(3, 4), textcoords="offset points", color=INK_SECONDARY,
                                rotation=35)
                if chave == "W":
                    linha = next((l for l in linhas_csv if l["formato"] == f"<{sum(fmt)},{fmt[0]}>"), None)
                    if linha is None:
                        linha = {"formato": f"<{sum(fmt)},{fmt[0]}>", "int_bits": fmt[0],
                                 "frac_bits": fmt[1], "W": sum(fmt), "origem": origem,
                                 "DSP": recursos.get(fmt, {}).get("DSP", ""),
                                 "LUT": recursos.get(fmt, {}).get("LUT", "")}
                        linhas_csv.append(linha)
                    linha[f"pior_perda_db_iter{it}"] = "nao_cruza" if perda == np.inf else round(perda, 3)
                fr_col = f"fronteira_{chave}_iter{it}"
                linha = next(l for l in linhas_csv if l["formato"] == f"<{sum(fmt)},{fmt[0]}>")
                linha[fr_col] = int(fmt in na)
            xs = sorted((c, min(p, a.teto)) for c, p, f in pontos if f in na)
            if xs:
                ax.step(*zip(*xs), where="post", color=CORES[it], lw=1.2, zorder=2)
            ax.axhline(LIMIAR_DB, color=REF_COR, ls="--", lw=0.8)
            ax.axhspan(a.teto * 0.97, a.teto * 1.03, color="#e4e3df", zorder=0)
            ax.set_facecolor(SURFACE)
            ax.set_xlabel(rotulo)
            ax.grid(alpha=0.3)
        axs[0].set_ylabel("Pior perda de SNR em SER = 1e-2 (dB)")
        axs[0].set_ylim(-0.03, a.teto * 1.05)
        axs[0].text(0.01, a.teto * 0.93, f"teto: > {a.teto:g} dB ou não chega a 1e-2",
                    transform=axs[0].get_yaxis_transform(), fontsize=7, color=INK_SECONDARY)
        axs[0].text(0.01, LIMIAR_DB + 0.015, f"{LIMIAR_DB:g} dB",
                    transform=axs[0].get_yaxis_transform(), fontsize=7, color=INK_SECONDARY)
        fig.suptitle(f"BCD-MMSE, {it} iteração(ões): pior caso nas configurações 1, 6, 8, 10 e 12 "
                     "(TDLA30-5 e TDLA30-300), TRN/SAT. Cheio: varredura [4]; vazado: [5]",
                     fontsize=9)
        fig.tight_layout()
        arq = destino / f"pareto_iter{it}.png"
        fig.savefig(arq, dpi=150, facecolor=SURFACE)
        plt.close(fig)
        print(arq)

    campos = ["formato", "int_bits", "frac_bits", "W", "origem", "DSP", "LUT"]
    campos += [f"pior_perda_db_iter{t}" for t in (1, 2, 3, 4)]
    campos += [f"fronteira_{c}_iter{t}" for t in (1, 2, 3, 4) for c in ("W", "DSP", "LUT")]
    linhas_csv.sort(key=lambda l: (l["W"], l["int_bits"]))
    with open(destino / "pareto.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, restval="")
        w.writeheader()
        w.writerows(linhas_csv)
    print(destino / "pareto.csv")


if __name__ == "__main__":
    main()
