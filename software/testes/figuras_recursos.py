#!/usr/bin/env python3
"""
Mapas de custo das sínteses HLS dos 8 formatos da [4] v3 nos 35 modos (sinteses/modos_16x16/).

Mesmo desenho dos mapas de perda da [4] v3 (figuras_juntos.py): uma linha por modo
(7 quantizações x 5 estouros) e uma coluna por formato, com um mapa para os formatos dos
pares com N = 192, 168 e 132 e outro para os do (24; 3,5 GHz). O custo não depende do
par, da configuração nem do número de iterações, só do formato e do modo. O rótulo do
modo mais barato tem fundo laranja.

Figuras: LUT, DSP, ciclos, e uma com FF, BRAM e URAM. Os valores são estimativas da
C synthesis do Vitis HLS (XCU50, 100 MHz, sem diretivas).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_recursos.py
"""

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Rectangle

from figuras_juntos import (BASE, DESTAQUE, ENTRE, INK_MUTED, INK_PRIMARY, INK_SECONDARY,
                            L_ESTOURO, L_QUANT, LADO, MARGEM, MODOS, SURFACE, painel)

AQUI = Path(__file__).resolve().parent
SINTESES = AQUI.parent.parent / "hardware" / "cholesky_hardware" / "sinteses" / "modos_16x16"
GRUPOS = (("TDLA30-5, TDLA30-75, TDLA30-300 e TDLC300-100", [(12, 12), (12, 16), (14, 16), (14, 20)]),
          ("TDLB100-400", [(10, 12), (10, 16), (12, 20), (12, 24)]))
RECURSOS = {"LUT": "LUT", "DSP": "DSP", "ciclos": "Ciclos (latência)", "FF": "FF",
            "BRAM_18K": "BRAM (18K)", "URAM": "URAM"}
TOPO = 3.1
#: Rampa sequencial de rosa, do claro ao escuro (o tom do meio é o rosa da paleta
#: categórica, #e87ba4), para não confundir custo com a perda, que é azul
SEQ = ("#fdeef4", "#f9d3e2", "#f3b0cb", "#e87ba4", "#d65a8a", "#b83f6f", "#8f2b55", "#661c3c")


def milhar(v):
    return f"{v:,.0f}".replace(",", ".")


def faixas(valores):
    """Limites das faixas de cor: passo "redondo" (1, 2, 2,5 ou 5 x 10^k), no máximo uma
    faixa por cor da rampa."""
    lo, hi = min(valores), max(valores)
    if lo == hi:
        return [lo, lo + 1]
    passo_min = (hi - lo) / len(SEQ)
    k = 10 ** math.floor(math.log10(passo_min))
    passo = next(m * k for m in (1, 2, 2.5, 5, 10) if m * k >= passo_min)
    inicio = math.floor(lo / passo) * passo
    limites = [inicio]
    while limites[-1] <= hi:
        limites.append(limites[-1] + passo)
    return limites


def ler():
    with open(SINTESES / "recursos.csv") as fh:
        return {(int(r["int_bits"]), int(r["frac_bits"]), r["quant"], r["overflow"]): r
                for r in csv.DictReader(fh)}


def figura(dados, campos, saida: Path):
    """Uma figura com um bloco por campo; cada bloco tem os dois grupos de formatos e a
    sua própria legenda de cores."""
    largura_painel = [L_QUANT + L_ESTOURO + len(f) * LADO for _, f in GRUPOS]
    # Cada bloco avança a largura dos mapas mais uma folga depois de cada um, e há mais
    # duas folgas entre blocos
    largura_bloco = sum(largura_painel) + ENTRE * len(largura_painel)
    W = 2 * MARGEM + len(campos) * largura_bloco + 2 * ENTRE * (len(campos) - 1) - ENTRE
    H = TOPO + len(MODOS) * LADO + BASE
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(SURFACE)
    x = MARGEM
    for campo in campos:
        valores = [float(dados[(I, F, q, o)][campo]) for _, fmts in GRUPOS
                   for I, F in fmts for q, o in MODOS]
        limites = faixas(valores)
        n_cores = len(limites) - 1
        cores = [SEQ[i] for i in np.linspace(0, len(SEQ) - 1, n_cores).round().astype(int)]
        cmap, norm = ListedColormap(cores), BoundaryNorm(limites, n_cores)
        escuro = lambda v, limites=limites, n=n_cores: np.searchsorted(limites, v, "right") - 1 >= n / 2
        x0 = x
        for (titulo, fmts), larg in zip(GRUPOS, largura_painel):
            M = np.array([[float(dados[(I, F, q, o)][campo]) for I, F in fmts] for q, o in MODOS])
            # Mais barato: comparando do formato com menos bits para o de mais
            chave = [tuple(M[a]) for a in range(len(MODOS))]
            melhor = min(chave)
            destaque = (set() if all(c == melhor for c in chave)
                        else {a for a, c in enumerate(chave) if c == melhor})
            painel(fig, x, TOPO, M, fmts, f"{RECURSOS[campo]}: {titulo}", texto_f=milhar,
                   cor_f=lambda v, cmap=cmap, norm=norm: cmap(norm(v)), claro=escuro,
                   destaque=destaque)
            x += larg + ENTRE
        # Legenda do bloco, centrada sobre os seus dois mapas
        rotulos = [f"{milhar(a)} a {milhar(b)}" if b - a > 1 else milhar(a)
                   for a, b in zip(limites[:-1], limites[1:])]
        alcas = [Rectangle((0, 0), 1, 1, facecolor=c, edgecolor=INK_MUTED, linewidth=0.5)
                 for c in (*cores, DESTAQUE)]
        meio = (x0 + x - ENTRE) / 2
        fig.legend(alcas, rotulos + ["mais barato"], loc="upper center",
                   bbox_to_anchor=(meio / W, 1 - 1.15 / H), ncol=min(5, len(alcas)),
                   frameon=False, fontsize=8, labelcolor=INK_SECONDARY, handlelength=1.4,
                   title=RECURSOS[campo], title_fontsize=8.5)
        x += 2 * ENTRE
    nomes = ", ".join(RECURSOS[c] for c in campos)
    fig.text(0.5, 1 - 0.15 / H,
             f"{nomes} da inversa de G_c (16 x 16), por formato e modo\n"
             "Estimativa da C synthesis do Vitis HLS, XCU50-FSVH2104-2-E, 100 MHz, sem diretivas\n"
             "Não depende do par (N, portadora), da configuração nem do número de iterações\n"
             "Fundo laranja no rótulo: o modo mais barato, comparando do formato com menos bits "
             "para o de mais",
             ha="center", va="top", fontsize=10, color=INK_PRIMARY)
    fig.savefig(saida, dpi=180, facecolor=SURFACE)
    fig.savefig(saida.with_suffix(".pdf"), facecolor=SURFACE)
    plt.close(fig)
    return saida


def main():
    dados = ler()
    destino = SINTESES / "figuras"
    destino.mkdir(exist_ok=True)
    for nome, campos in (("lut", ["LUT"]), ("dsp", ["DSP"]), ("ciclos", ["ciclos"]),
                         ("ff_bram_uram", ["FF", "BRAM_18K", "URAM"])):
        print(f"  {figura(dados, campos, destino / f'mapa_{nome}.png')}")


if __name__ == "__main__":
    main()
