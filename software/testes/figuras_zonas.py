#!/usr/bin/env python3
"""
Gráficos de zonas: a perda de SNR do formato (BCD-MMSE com 1 iteração, ponto fixo contra
float, em SER = 1e-2) com o fundo pintado nas faixas de perda que o trabalho já usa: até
0,1 dB, de 0,1 a 3 dB e acima de 3 dB. As zonas são retas porque só esses dois limites têm
critério; um painel por formato (<22,12>, <24,12>, <28,14>).

Versões (todas em resultados/5_candidatos/modo_fixo_3dB/figuras/zonas/):
- v1_dificuldade: um ponto por caso (configuração x par). x = SNR que o LMMSE (float)
  precisa para SER = 1e-2, uma medida de quão difícil é o caso. Cor = par, marcador =
  estação.
- v2_algoritmo_x_formato: um ponto por caso. x = quanto o BCD-MMSE em float perde para o
  LMMSE (SNR a mais em SER = 1e-2), y = quanto o formato perde para o BCD-MMSE em float.
  Separa a perda do algoritmo da perda do hardware. Casos em que o LMMSE já está abaixo de
  1e-2 em -10 dB ficam de fora (a diferença não é conhecida).
- v3_rotulos: um ponto por configuração, com a letra num rótulo (como no exemplo). x =
  mediana dos 5 pares da SNR do LMMSE, y = pior perda entre os 5 pares. Fundo escuro com o
  nome da zona.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_zonas.py
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import figuras_analise_grupos as fag
from figuras_analise_grupos import (CENARIOS, ESTACOES, FORMATOS, INK_MUTED, INK_PRIMARY,
                                    INK_SECONDARY, LARGURA, LETRAS, PASTA, SURFACE,
                                    carregar, eixos, estado_snr, num, perda, salvar)

FMTS = ((12, 10), (12, 12), (14, 14))
# Cores dos pares, sem verde (pedido da autora): validate_palette.js --pairs all passa em
# CVD (pior 8,7) e visão normal (pior 17,2); o cinza é neutro de propósito (falha só no
# piso de croma). O marcador também
# muda por par na v2, para não depender só da cor.
COR_PAR = dict(zip(CENARIOS, ("#52514e", "#35bcd9", "#eb6834", "#4a3aa7", "#d64ad6")))
NOME_PAR = {"TDLA30-5": "TDLA30-5/10 ($N$ = 192, 3,5 GHz)",
            "TDLA30-75": "TDLA30-75 ($N$ = 192, 28 GHz)",
            "TDLA30-300": "TDLA30-300 ($N$ = 168, 28 GHz)",
            "TDLC300-100": "TDLC300-100 ($N$ = 132, 3,5 GHz)",
            "TDLB100-400": "TDLB100-400 ($N$ = 24, 3,5 GHz)"}
MARC_ESTACAO = {"G1": "o", "G2": "s", "G3": "D"}
MARC_PAR = dict(zip(CENARIOS, ("o", "s", "D", "^", "v")))
COR_ESTACAO = {"G1": "#2a78d6", "G2": "#eb6834", "G3": "#4a3aa7"}
ESTACAO = {k: g for g, _, _, ks in ESTACOES for k in ks}
NOME_ESTACAO = {g: f"{g}: $M$ = {M}, $C$ = {C}" for g, M, C, _ in ESTACOES}

# Zonas: (de, até, cor clara, cor escura, nome)
ZONAS = ((0, 0.1, "#ecebe6", "#6f7d8c", "ATÉ 0,1 dB"),
         (0.1, 3, "#fdf0cf", "#c9a54e", "DE 0,1 A 3 dB"),
         (3, 50, "#f7d9d9", "#a8443f", "ACIMA DE 3 dB"))
Y_MAX = 5.0
Y_TICKS = ([0, 0.05, 0.1, 0.3, 1, 3], ["0", "0,05", "0,1", "0,3", "1", "3"])
X_ABAIXO = -11.4   # coluna dos casos em que o LMMSE já está abaixo de 1e-2 em -10 dB


def zonas(ax, escuro=False, nomes=True):
    ax.set_yscale("symlog", linthresh=0.1, linscale=1.0)
    ax.set_ylim(0, Y_MAX)
    ax.set_yticks(*Y_TICKS)
    ax.yaxis.set_minor_locator(plt.NullLocator())
    for de, ate, clara, escura, nome in ZONAS:
        ax.axhspan(de, min(ate, Y_MAX), color=escura if escuro else clara, lw=0, zorder=0)
        if nomes:
            meio = np.sqrt(max(de, 0.02) * min(ate, Y_MAX)) if de > 0 else 0.05
            ax.text(0.985, meio, nome, transform=ax.get_yaxis_transform(), ha="right",
                    va="center", fontsize=11 if escuro else 9, fontweight="bold",
                    color="#ffffff" if escuro else INK_MUTED,
                    alpha=0.85 if escuro else 0.9, zorder=1)
    for lim in (0.1, 3):
        ax.axhline(lim, color="#ffffff" if escuro else INK_MUTED, lw=0.8,
                   ls="-" if escuro else "--", zorder=1)


def casos(ser, fmt):
    """Um registro por (configuração, par), com as SNRs e as perdas."""
    linhas = []
    for k in range(1, 17):
        for c in CENARIOS:
            r = ser[(c, k)]
            xl, el = estado_snr(r["LMMSE"])
            xb, eb = estado_snr(r["BCD"])
            v, lim = perda(r, fmt)
            linhas.append(dict(k=k, c=c, g=ESTACAO[k], snr_lmmse=xl, est_lmmse=el,
                               gap=(None if el == "abaixo" or xl is None or xb is None
                                    else xb - xl),
                               perda=v, limite=lim))
    return linhas


def fora(v):
    """y de uma perda: acima do topo do eixo (ou None) vai para perto do topo."""
    return Y_MAX * 0.85 if v is None or v > Y_MAX * 0.85 else v


def v1(ser):
    fig, axs = plt.subplots(3, 1, figsize=(LARGURA, 8.4), sharex=True)
    dados = []
    for ax, fmt in zip(axs, FMTS):
        eixos(ax, grade_x=True, grade_y=False)
        zonas(ax)
        for d in casos(ser, fmt):
            x = X_ABAIXO if d["est_lmmse"] == "abaixo" else d["snr_lmmse"]
            ax.plot(x, fora(d["perda"]), marker=MARC_ESTACAO[d["g"]], color=COR_PAR[d["c"]],
                    markersize=5, linestyle="none", markeredgecolor=SURFACE,
                    markeredgewidth=0.6, alpha=0.9, zorder=3)
            dados.append([FORMATOS[fmt][0], LETRAS[d["k"]], d["k"], d["g"], d["c"],
                          "" if x is None else f"{x:.3f}", d["est_lmmse"],
                          "nao_atinge" if d["perda"] is None else f"{d['perda']:.3f}"])
        ax.axvline(-10.7, color=INK_MUTED, lw=0.6, ls=":")
        ax.set_title(f"{FORMATOS[fmt][0]} RND_ZERO/WRAP", loc="left", color=INK_PRIMARY,
                     pad=3)
        ax.set_ylabel("Perda do formato [dB]", color=INK_SECONDARY)
    axs[-1].set_xlim(-12.0, 2)
    axs[-1].set_xticks([X_ABAIXO, -10, -8, -6, -4, -2, 0, 2],
                       ["≤ −10", "−10", "−8", "−6", "−4", "−2", "0", "2"])
    axs[-1].set_xlabel("SNR que o LMMSE (float) precisa para SER = $10^{-2}$ [dB]"
                       "   (mais à direita = caso mais difícil)", color=INK_SECONDARY)
    h = [Line2D([], [], marker="o", color=COR_PAR[c], linestyle="none", markersize=5,
                label=NOME_PAR[c]) for c in CENARIOS]
    h += [Line2D([], [], marker=MARC_ESTACAO[g], color=INK_SECONDARY, linestyle="none",
                 markersize=5, markerfacecolor="none", label=NOME_ESTACAO[g])
          for g in MARC_ESTACAO]
    fig.legend(handles=h, loc="lower center", ncol=2, frameon=False, fontsize=7,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    salvar(fig, "v1_dificuldade", dados, ["formato", "letra", "configuracao", "estacao",
                                          "par", "snr_lmmse_db", "estado_lmmse", "perda_db"])


def v2(ser):
    fig, axs = plt.subplots(3, 1, figsize=(LARGURA, 8.4), sharex=True)
    dados = []
    for ax, fmt in zip(axs, FMTS):
        eixos(ax, grade_x=True, grade_y=False)
        zonas(ax)
        omitidos = 0
        for d in casos(ser, fmt):
            if d["gap"] is None:
                omitidos += 1
                continue
            ax.plot(d["gap"], fora(d["perda"]), marker=MARC_PAR[d["c"]], color=COR_PAR[d["c"]],
                    markersize=5, linestyle="none", markeredgecolor=SURFACE,
                    markeredgewidth=0.6, alpha=0.9, zorder=3)
            dados.append([FORMATOS[fmt][0], LETRAS[d["k"]], d["k"], d["g"], d["c"],
                          f"{d['gap']:.3f}",
                          "nao_atinge" if d["perda"] is None else f"{d['perda']:.3f}"])
        ax.set_title(f"{FORMATOS[fmt][0]} RND_ZERO/WRAP", loc="left", color=INK_PRIMARY,
                     pad=3)
        ax.set_ylabel("Perda do formato [dB]", color=INK_SECONDARY)
    axs[-1].set_xlim(-0.1, 3.6)
    axs[-1].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: num(v, 1)))
    axs[-1].set_xlabel("Quanto o BCD-MMSE (float) perde para o LMMSE em SER = $10^{-2}$ [dB]",
                       color=INK_SECONDARY)
    h = [Line2D([], [], marker=MARC_PAR[c], color=COR_PAR[c], linestyle="none", markersize=5,
                label=NOME_PAR[c]) for c in CENARIOS]
    fig.legend(handles=h, loc="lower center", ncol=2, frameon=False, fontsize=7,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, 0.015))
    fig.text(0.5, 0.005, f"{omitidos} dos 80 casos de cada formato ficam de fora: o LMMSE já "
             "está abaixo de $10^{-2}$ em −10 dB, então a diferença não é conhecida",
             ha="center", va="bottom", fontsize=6.5, color=INK_SECONDARY)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    salvar(fig, "v2_algoritmo_x_formato", dados, ["formato", "letra", "configuracao",
                                                  "estacao", "par", "perda_bcd_lmmse_db",
                                                  "perda_formato_db"])


def rotulos_juntos(ax, pontos, raio=24):
    """Um rótulo por grupo de pontos a menos de raio pixels um do outro (letras juntas)."""
    ax.set_xlim(-12.0, 2)
    tela = ax.transData.transform([(x, y) for x, y, _ in pontos])
    grupos = []
    for i in np.argsort(tela[:, 0]):
        for gr in grupos:
            if np.hypot(*(tela[i] - tela[gr[0]])) < raio:
                gr.append(i)
                break
        else:
            grupos.append([i])
    for gr in grupos:
        x, y = max((pontos[i][:2] for i in gr), key=lambda p: p[1])
        letras = ", ".join(sorted(pontos[i][2] for i in gr))
        ax.annotate(letras, (x, y), xytext=(8, 4), textcoords="offset points", fontsize=7,
                    color="#ffffff", va="center", fontweight="bold", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.2", fc="#3a3a38", ec="none", alpha=0.9))


def v3(ser):
    fig, axs = plt.subplots(3, 1, figsize=(LARGURA, 8.4), sharex=True)
    dados = []
    for ax, fmt in zip(axs, FMTS):
        eixos(ax, grade_x=False, grade_y=False)
        zonas(ax, escuro=True)
        ax.grid(True, axis="x", color="#ffffff", alpha=0.35, lw=0.6, zorder=1)
        por_k, pontos = {}, []
        for d in casos(ser, fmt):
            por_k.setdefault(d["k"], []).append(d)
        for k, ds in por_k.items():
            xs = [X_ABAIXO if d["est_lmmse"] == "abaixo" else d["snr_lmmse"] for d in ds]
            x = float(np.median(xs))
            ps = [d["perda"] for d in ds]
            pior = None if any(p is None for p in ps) else max(ps)
            y = fora(pior)
            g = ESTACAO[k]
            ax.plot(x, y, marker="o", markersize=9, color=COR_ESTACAO[g],
                    markeredgecolor="#ffffff", markeredgewidth=1.0, zorder=4)
            pontos.append((x, y, LETRAS[k]))
            dados.append([FORMATOS[fmt][0], LETRAS[k], k, g, f"{x:.3f}",
                          "nao_atinge" if pior is None else f"{pior:.3f}"])
        rotulos_juntos(ax, pontos)
        ax.set_title(f"{FORMATOS[fmt][0]} RND_ZERO/WRAP", loc="left", color=INK_PRIMARY,
                     pad=3)
        ax.set_ylabel("Pior perda nos 5 pares [dB]", color=INK_SECONDARY)
    axs[-1].set_xlim(-12.0, 2)
    axs[-1].set_xticks([X_ABAIXO, -10, -8, -6, -4, -2, 0, 2],
                       ["≤ −10", "−10", "−8", "−6", "−4", "−2", "0", "2"])
    axs[-1].set_xlabel("SNR que o LMMSE (float) precisa para SER = $10^{-2}$, mediana dos 5 "
                       "pares [dB]", color=INK_SECONDARY)
    h = [Line2D([], [], marker="o", color=COR_ESTACAO[g], linestyle="none", markersize=7,
                markeredgecolor="#ffffff", label=NOME_ESTACAO[g]) for g in COR_ESTACAO]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=7.5,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    salvar(fig, "v3_rotulos", dados, ["formato", "letra", "configuracao", "estacao",
                                      "snr_lmmse_mediana_db", "pior_perda_db"])


def main():
    fag.SAIDA = PASTA / "figuras" / "zonas"
    ser = carregar()
    v1(ser)
    v2(ser)
    v3(ser)


if __name__ == "__main__":
    main()
