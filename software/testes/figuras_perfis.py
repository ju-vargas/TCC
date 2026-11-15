#!/usr/bin/env python3
"""
Pior aumento de SNR do BCD-MMSE (iter 1) no formato sobre o float, em SER = 10^-2, por perfil de
mobilidade: lento (TDLA30-5/-10 e TDLA30-75, até ~3 km/h) e rápido (TDLA30-300, TDLC300-100 e
TDLB100-400, de ~12 a ~123 km/h). Pontos pareados: uma linha por configuração, um ponto por
perfil, um painel por formato (<18,8>, <20,8>, <22,12>, <24,12> e <28,12>, todos no modo fixo
RND_ZERO/WRAP), com o fundo no degradê do mapa de perda. Dados da [4] v4 e, para as QPSK
dos grupos 2 e 3 (2C, 2D, 2G, 2H, 3C, 3D, 3G, 3H), da v5, os mesmos dos mapas por grupo
(mapa_grupos_v4.py). Mostra que a escolha do formato não muda entre os perfis.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_perfis.py [--linear] [--tcc]

Com --linear, eixo x linear, com um alcance por painel (..._linear).
Com --tcc, a versão do TCC (figura_grupo): uma figura por grupo, só com os formatos
escolhidos do grupo, sem título, fonte Type 42, em
TCC/Images/RESULTADOS/perfis_mobilidade_grupo<g>.pdf. (figura_tcc, com os 3 grupos numa
figura 3 x 3, ficou como alternativa.)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import figuras_analise_grupos as fag
from figuras_analise_grupos import LARGURA, eixos, legenda_quadro, salvar
from figuras_formatos import ler, perdas
import grade_inteira as gi
from mapa_cenarios_v4 import DEGRADE, LETRAS, NORMA, paineis
from mapa_grupos_v4 import LETRAS_NOVAS, NOVAS, V5
from pareto_v4 import V4
from dbp_sim.plotting import INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE

plt.rcParams["mathtext.default"] = "regular"

# Pontos em preto (escolha da autora; amarelo e rosa testados), sem borda;
# (nome, condições, marcador, preenchimento): vazado (lento) e cheio (rápido)
COR = INK_PRIMARY
PERFIS = (("Low mobility", ("TDLA30-5", "TDLA30-75"), "o", "none"),
          ("High mobility", ("TDLA30-300", "TDLC300-100", "TDLB100-400"), "o", COR))
# (I, F), do menor para o maior W; o modo fixo de todos é RND_ZERO/WRAP (até 3 dB, 1 iteração)
FORMATOS = ((8, 10), (8, 12), (12, 10), (12, 12), (12, 16))
VERMELHO = "#d03b3b"   # × : não chega a 10^-2
MODO = ("AP_RND_ZERO", "AP_WRAP")
PISO, TETO = 0.01, 5.0            # eixo log; perda 0 vai para o piso
NOMES = {"TDLA30-5": "TDLA30-5 and -10"}
LETRAS.update({k: v for k, v in LETRAS_NOVAS.items() if k in NOVAS})   # QPSK da v5
ORDEM = sorted(LETRAS, key=lambda k: LETRAS[k])   # 1A ... 3H
TCC = Path(__file__).resolve().parents[2] / "TG2_-__ECP_UFRGS" / "Images" / "RESULTADOS"


def pior(p, k, cens, I, F, modo=MODO):
    vs = [p[(k, c, I, F, *modo)] for c in cens]
    return None if None in vs else max(vs)


# Versão do TCC (--tcc): uma linha de painéis por grupo, com os formatos escolhidos do grupo
# (Tabela tab:formatos-escolhidos do TCC), um por critério: atinge SER = 10^-2, aumento até
# 3 dB e até 0,1 dB. (I, F, modo); no grupo 3 o <24,12> vale para os dois primeiros.
TRN_SAT = ("AP_TRN", "AP_SAT")
# 2026-11-09: sem o critério "atinge SER = 10^-2"; grupo 1 com 0,1 dB no <26,12>
CRITERIOS = ("Up to 3 dB", "Up to 0.1 dB")
ESCOLHIDOS = {"1": ((12, 12, MODO), (12, 14, MODO)),
              "2": ((14, 14, MODO), (14, 16, TRN_SAT)),
              "3": ((12, 12, MODO), (14, 16, TRN_SAT))}
# Formatos escolhidos só com as configurações de IoTh de 10 dB (A a D), na mesma ordem de
# critérios (Tabela tab:formatos-escolhidos, parte de baixo)
ESCOLHIDOS_IOT10 = {"1": ((8, 10, MODO), (12, 12, MODO)),
                    "2": ((12, 10, MODO), (12, 12, MODO)),
                    "3": ((12, 10, MODO), (12, 12, MODO))}
ABREV = {"AP_RND_ZERO": "RND_ZERO", "AP_WRAP": "WRAP", "AP_TRN": "TRN", "AP_SAT": "SAT"}


def figura_grupo(p, g):
    """Uma figura por grupo, no estilo da figura original de 5 formatos (aumento de SNR no
    eixo x, configurações no y, linhas próximas): um painel por formato escolhido do grupo;
    critérios com o mesmo formato (grupo 3) dividem o painel."""
    paineis_g = []
    for crit, fmt in zip(CRITERIOS, ESCOLHIDOS[g]):
        if paineis_g and paineis_g[-1][1] == fmt:
            paineis_g[-1][0].append(crit)
        else:
            paineis_g.append(([crit], fmt))
    ks = [k for k in ORDEM if LETRAS[k][0] == g]
    ys = {k: i for i, k in enumerate(ks)}
    altura = 1.15 + 0.17 * len(ks)
    fig, axs = plt.subplots(1, len(paineis_g), figsize=(LARGURA, altura),
                            sharey=True, facecolor=SURFACE, squeeze=False)
    axs = axs[0]
    linhas = []
    for j, (ax, (crits, (I, F, modo))) in enumerate(zip(axs, paineis_g)):
        eixos(ax, grade_x=False)
        bx = np.logspace(np.log10(PISO / 1.35), np.log10(TETO), 300)
        meio = np.maximum((bx[:-1] + bx[1:]) / 2, PISO)
        ax.pcolormesh(bx, [-1, 100], meio[None, :], cmap=DEGRADE, norm=NORMA, zorder=0,
                      rasterized=True)
        for v in (0.1, 3):
            ax.axvline(v, color=INK_PRIMARY if v < 1 else SURFACE, lw=0.9, ls=(0, (3, 2)),
                       zorder=1)
        for k in ks:
            vs = [pior(p, k, cens, I, F, modo) for _, cens, *_ in PERFIS]
            xs = [TETO if v is None else max(v, PISO) for v in vs]
            if None not in vs:
                ax.annotate("", xy=(xs[1], ys[k]), xytext=(xs[0], ys[k]), zorder=2,
                            arrowprops=dict(arrowstyle="-", color=COR, lw=1.2,
                                            shrinkA=3.0, shrinkB=3.0))
            for (_, _, m, face), x, v in zip(PERFIS, xs, vs):
                if v is None:
                    ax.plot(x, ys[k], marker="x", color=VERMELHO, ms=5, mew=1.3, zorder=3,
                            clip_on=False)
                else:
                    ax.plot(x, ys[k], marker=m, ms=5, mfc=face, mec=COR, mew=1.4,
                            ls="none", zorder=3)
            linhas.append([g, " / ".join(crits), f"<{I + F},{I}>", "/".join(modo), LETRAS[k],
                           *("" if v is None else f"{v:.3f}" for v in vs)])
        ax.set_ylim(len(ks) - 0.5, -0.5)
        ax.set_xscale("log")
        ax.set_xlim(PISO / 1.35, TETO)
        ax.set_xticks([0.01, 0.1, 1, 3], ["≤ 0.01", "0.1", "1", "3"])
        ax.minorticks_off()
        ax.tick_params(axis="both", labelsize=7)
        ax.set_title(f"<{I + F},{I}> {ABREV[modo[0]]}/{ABREV[modo[1]]}\n"
                     + " and ".join(c[0].lower() + c[1:] if i else c
                                    for i, c in enumerate(crits)),
                     fontsize=7.5, color=INK_PRIMARY, loc="left")
        ax.set_xlabel("Worst SNR increase [dB]", fontsize=7.5, color=INK_SECONDARY)
    axs[0].set_yticks(range(len(ks)), [LETRAS[k] for k in ks])
    axs[0].set_ylabel("Configuration", fontsize=7.5, color=INK_SECONDARY)
    h = [Line2D([], [], marker=m, mfc=face, mec=COR, ls="none", ms=5, mew=1.4,
                label=f"{nome}: {', '.join(NOMES.get(c, c) for c in cens)}")
         for nome, cens, m, face in PERFIS]
    h.append(Line2D([], [], color=INK_PRIMARY, lw=0.9, ls=(0, (3, 2)),
                    label="0.1 dB and 3 dB limits"))
    fig.tight_layout(rect=(0, 0.44 / altura, 1, 1), w_pad=1.0)
    legenda_quadro(fig, axs[-1], h, ncol=2, fontsize=6.5, columnspacing=1.5)
    return fig, linhas


def figura_tcc(p, vertical=False, iot10=False):
    """3 x 3 painéis: grupos nas linhas, critérios nas colunas; aumento de SNR em escala log
    no eixo x (ou no y, com vertical=True, e as configurações no x). Com iot10=True, só as
    configurações A a D (IoTh de 10 dB) e os formatos escolhidos com elas."""
    escolhidos = ESCOLHIDOS_IOT10 if iot10 else ESCOLHIDOS
    fig, grade = plt.subplots(3, 3, figsize=(LARGURA, 4.0 if iot10 else 6.4),
                              facecolor=SURFACE)
    falhou, linhas = False, []
    for g, linha in zip("123", grade):
        ks = [k for k in ORDEM if LETRAS[k][0] == g and (not iot10 or LETRAS[k][1] in "ABCD")]
        ys = {k: i for i, k in enumerate(ks)}
        for j, (ax, (I, F, modo)) in enumerate(zip(linha, escolhidos[g])):
            eixos(ax, grade_x=False)
            bx = np.logspace(np.log10(PISO), np.log10(TETO), 300)
            meio = np.maximum((bx[:-1] + bx[1:]) / 2, PISO)
            # pt(v, y): ponto (aumento v, linha y) nas coordenadas do eixo
            pt = (lambda v, y: (y, v)) if vertical else (lambda v, y: (v, y))
            if vertical:
                ax.pcolormesh([-1, 100], bx, meio[:, None], cmap=DEGRADE, norm=NORMA,
                              zorder=0, rasterized=True)
            else:
                ax.pcolormesh(bx, [-1, 100], meio[None, :], cmap=DEGRADE, norm=NORMA,
                              zorder=0, rasterized=True)
            for v in (0.1, 3):
                (ax.axhline if vertical else ax.axvline)(
                    v, color=INK_PRIMARY if v < 1 else SURFACE, lw=0.9, ls=(0, (3, 2)),
                    zorder=1)
            for k in ks:
                vs = [pior(p, k, cens, I, F, modo) for _, cens, *_ in PERFIS]
                xs = [TETO if v is None else max(v, PISO) for v in vs]
                if None not in vs:
                    ax.annotate("", xy=pt(xs[1], ys[k]), xytext=pt(xs[0], ys[k]), zorder=2,
                                arrowprops=dict(arrowstyle="-", color=COR, lw=1.1,
                                                shrinkA=3.2, shrinkB=3.2))
                for (_, _, m, face), x, v in zip(PERFIS, xs, vs):
                    if v is None:
                        falhou = True
                        ax.plot(*pt(x, ys[k]), marker="x", color=VERMELHO, ms=5, mew=1.3,
                                zorder=3, clip_on=False)
                    else:
                        ax.plot(*pt(x, ys[k]), marker=m, ms=5, mfc=face, mec=COR, mew=1.4,
                                ls="none", zorder=3)
                linhas.append([g, CRITERIOS[j], f"<{I + F},{I}>", "/".join(modo), LETRAS[k],
                               *("" if v is None else f"{v:.3f}" for v in vs)])
            marcas = ([0.01, 0.1, 1, 3], ["≤ 0.01", "0.1", "1", "3"])
            if vertical:
                ax.set_xlim(-0.6, len(ks) - 0.4)
                ax.set_yscale("log")
                ax.set_ylim(PISO / 1.35, TETO)   # folga: o ponto no piso não é cortado
                ax.set_yticks(*(marcas if j == 0 else (marcas[0], [])))
                ax.set_xticks(range(len(ks)), [LETRAS[k] for k in ks])
            else:
                ax.set_ylim(len(ks) - 0.5, -0.5)
                ax.set_xscale("log")
                ax.set_xlim(PISO / 1.35, TETO)
                ax.set_xticks(*marcas)
                ax.set_yticks(range(len(ks)), [LETRAS[k] for k in ks] if j == 0 else [])
            ax.minorticks_off()
            ax.tick_params(axis="both", labelsize=7.5)
            ax.set_title(f"<{I + F},{I}> {ABREV[modo[0]]}/{ABREV[modo[1]]}", fontsize=8,
                         color=INK_PRIMARY, loc="left")
            if g == "1":
                ax.annotate(CRITERIOS[j], (0.5, 1), xycoords="axes fraction",
                            xytext=(0, 17), textcoords="offset points", ha="center",
                            va="bottom", fontsize=8.5, color=INK_PRIMARY)
            if g == "3":
                ax.set_xlabel("Configuration" if vertical else "Worst SNR increase [dB]",
                              fontsize=8, color=INK_SECONDARY)
        linha[0].set_ylabel(f"Group {g}\nWorst SNR increase [dB]" if vertical else f"Group {g}",
                            fontsize=8, color=INK_SECONDARY)
    h = [Line2D([], [], marker=m, mfc=face, mec=COR, ls="none", ms=5, mew=1.4,
                label=f"{nome}: {', '.join(NOMES.get(c, c) for c in cens)}")
         for nome, cens, m, face in PERFIS]
    h.append(Line2D([], [], color=INK_PRIMARY, lw=0.9, ls=(0, (3, 2)),
                    label="0.1 dB and 3 dB limits"))
    if falhou:
        h.append(Line2D([], [], marker="x", color=VERMELHO, ls="none", ms=5, mew=1.3,
                        label="does not reach SER = $10^{-2}$"))
    fig.tight_layout(rect=(0, 0.11 if iot10 else 0.08, 1, 1), h_pad=1.2)
    legenda_quadro(fig, grade[-1][-1], h, ncol=2, fontsize=7, columnspacing=1.5)
    return fig, linhas


def painel_perfis(ax, p, ks, I, F, modo):
    """Um painel de figura_tcc (horizontal): pontos pareados por configuração sobre o degradê.
    Devolve (falhou, linhas do CSV sem grupo e critério)."""
    eixos(ax, grade_x=False)
    bx = np.logspace(np.log10(PISO), np.log10(TETO), 300)
    meio = np.maximum((bx[:-1] + bx[1:]) / 2, PISO)
    ax.pcolormesh(bx, [-1, 100], meio[None, :], cmap=DEGRADE, norm=NORMA, zorder=0,
                  rasterized=True)
    for v in (0.1, 3):
        ax.axvline(v, color=INK_PRIMARY if v < 1 else SURFACE, lw=0.9, ls=(0, (3, 2)), zorder=1)
    ys = {k: i for i, k in enumerate(ks)}
    falhou, linhas = False, []
    for k in ks:
        vs = [pior(p, k, cens, I, F, modo) for _, cens, *_ in PERFIS]
        xs = [TETO if v is None else max(v, PISO) for v in vs]
        if None not in vs:
            ax.annotate("", xy=(xs[1], ys[k]), xytext=(xs[0], ys[k]), zorder=2,
                        arrowprops=dict(arrowstyle="-", color=COR, lw=1.1, shrinkA=3.2,
                                        shrinkB=3.2))
        for (_, _, m, face), x, v in zip(PERFIS, xs, vs):
            if v is None:
                falhou = True
                ax.plot(x, ys[k], marker="x", color=VERMELHO, ms=5, mew=1.3, zorder=3,
                        clip_on=False)
            else:
                ax.plot(x, ys[k], marker=m, ms=5, mfc=face, mec=COR, mew=1.4, ls="none",
                        zorder=3)
        linhas.append([f"<{I + F},{I}>", "/".join(modo), LETRAS[k],
                       *("" if v is None else f"{v:.3f}" for v in vs)])
    ax.set_yticks(range(len(ks)), [LETRAS[k] for k in ks])
    ax.set_ylim(len(ks) - 0.5, -0.5)
    ax.set_xscale("log")
    ax.set_xlim(PISO / 1.35, TETO)
    ax.set_xticks([0.01, 0.1, 1, 3], ["≤ 0.01", "0.1", "1", "3"])
    ax.minorticks_off()
    ax.tick_params(axis="both", labelsize=7.5)
    ax.set_title(f"<{I + F},{I}> {ABREV[modo[0]]}/{ABREV[modo[1]]}", fontsize=8,
                 color=INK_PRIMARY, loc="left")
    return falhou, linhas


def figura_tcc_ioth(p):
    """Junta as duas versões de figura_tcc: em cada grupo, as configurações A a D (IoTh de
    10 dB) com os formatos escolhidos só com elas (ESCOLHIDOS_IOT10) e, embaixo, as E a H
    (IoTh de 20 dB) com os formatos escolhidos com todas (ESCOLHIDOS). Critérios nas colunas."""
    # linhas da grade: por grupo, A-D e E-H, e um espaço entre os grupos
    razoes = [4, 4, 0.01, 4, 4, 0.01, 4, 4]
    fig = plt.figure(figsize=(LARGURA, 7.2), facecolor=SURFACE)
    gs = fig.add_gridspec(len(razoes), 3, height_ratios=razoes, hspace=0.62, wspace=0.12,
                          left=0.13, right=0.985, top=0.955, bottom=0.115)
    falhou, linhas = False, []
    linhas_gs = {"1": (0, 1), "2": (3, 4), "3": (6, 7)}
    for g in "123":
        for sub, (lin, letras, escolhidos, rot) in enumerate(
                ((linhas_gs[g][0], "ABCD", ESCOLHIDOS_IOT10, "IoTh 10 dB"),
                 (linhas_gs[g][1], "EFGH", ESCOLHIDOS, "IoTh 20 dB"))):
            ks = [k for k in ORDEM if LETRAS[k][0] == g and LETRAS[k][1] in letras]
            for j, (I, F, modo) in enumerate(escolhidos[g]):
                ax = fig.add_subplot(gs[lin, j])
                f_, ls = painel_perfis(ax, p, ks, I, F, modo)
                falhou |= f_
                linhas += [[g, rot, CRITERIOS[j], *l] for l in ls]
                if j:
                    ax.set_yticklabels([])
                else:
                    ax.set_ylabel(rot, fontsize=7.5, color=INK_SECONDARY)
                if sub == 0:
                    ax.set_xticklabels([])
                elif g == "3":
                    ax.set_xlabel("Worst SNR increase [dB]", fontsize=8, color=INK_SECONDARY)
                if g == "1" and sub == 0:
                    ax.annotate(CRITERIOS[j], (0.5, 1), xycoords="axes fraction",
                                xytext=(0, 17), textcoords="offset points", ha="center",
                                va="bottom", fontsize=8.5, color=INK_PRIMARY)
        # nome do grupo à esquerda, centrado nos dois painéis do grupo
        a0 = gs[linhas_gs[g][0], 0].get_position(fig)
        a1 = gs[linhas_gs[g][1], 0].get_position(fig)
        fig.text(0.015, (a0.y1 + a1.y0) / 2, f"Group {g}", rotation=90, ha="left",
                 va="center", fontsize=8.5, color=INK_PRIMARY)
    h = [Line2D([], [], marker=m, mfc=face, mec=COR, ls="none", ms=5, mew=1.4,
                label=f"{nome}: {', '.join(NOMES.get(c, c) for c in cens)}")
         for nome, cens, m, face in PERFIS]
    h.append(Line2D([], [], color=INK_PRIMARY, lw=0.9, ls=(0, (3, 2)),
                    label="0.1 dB and 3 dB limits"))
    if falhou:
        h.append(Line2D([], [], marker="x", color=VERMELHO, ls="none", ms=5, mew=1.3,
                        label="does not reach SER = $10^{-2}$"))
    legenda_quadro(fig, fig.axes[-1], h, ncol=2, fontsize=7, columnspacing=1.5)
    return fig, linhas


def figura_tcc_3col(p):
    """Três colunas, como a figura de faixas das curvas de SER (2026-11-11): até 3 dB e até
    0,1 dB com todas as configurações (ESCOLHIDOS) e até 3 dB só com IoTh de 10 dB
    (ESCOLHIDOS_IOT10, configurações A a D). Um grupo por linha, fontes menores."""
    colunas = (("Up to 3 dB,\nall configurations", lambda g: ESCOLHIDOS[g][0], "ABCDEFGH"),
               ("Up to 0.1 dB,\nall configurations", lambda g: ESCOLHIDOS[g][1], "ABCDEFGH"),
               ("Up to 3 dB,\nIoTh 10 dB only", lambda g: ESCOLHIDOS_IOT10[g][0], "ABCD"))
    altura = 5.3
    fig, grade = plt.subplots(3, 3, figsize=(LARGURA, altura), facecolor=SURFACE)
    falhou, linhas = False, []
    for g, linha in zip("123", grade):
        for j, (ax, (cab, fmt, letras)) in enumerate(zip(linha, colunas)):
            I, F, modo = fmt(g)
            ks = [k for k in ORDEM if LETRAS[k][0] == g and LETRAS[k][1] in letras]
            f_, ls = painel_perfis(ax, p, ks, I, F, modo)
            falhou |= f_
            linhas += [[g, cab.replace("\n", " "), *l] for l in ls]
            for ln in ax.lines:
                if ln.get_marker() in ("o", "x"):
                    ln.set_markersize(4)
                    ln.set_markeredgewidth(1.1)
            ax.tick_params(axis="both", labelsize=6, pad=2)
            ax.set_title(ax.get_title(loc="left"), fontsize=6.5, color=INK_PRIMARY, loc="left",
                         pad=3)
            if j == 0:
                ax.set_ylabel(f"Group {g}", fontsize=7, color=INK_SECONDARY)
            if g == "1":
                ax.annotate(cab, (0.5, 1), xycoords="axes fraction", xytext=(0, 13),
                            textcoords="offset points", ha="center", va="bottom", fontsize=7,
                            color=INK_PRIMARY)
            if g == "3":
                ax.set_xlabel("Worst SNR increase [dB]", fontsize=6.5, color=INK_SECONDARY)
    h = [Line2D([], [], marker=m, mfc=face, mec=COR, ls="none", ms=4, mew=1.1,
                label=f"{nome}: {', '.join(NOMES.get(c, c) for c in cens)}")
         for nome, cens, m, face in PERFIS]
    h.append(Line2D([], [], color=INK_PRIMARY, lw=0.9, ls=(0, (3, 2)),
                    label="0.1 dB and 3 dB limits"))
    if falhou:
        h.append(Line2D([], [], marker="x", color=VERMELHO, ls="none", ms=4, mew=1.1,
                        label="does not reach SER = $10^{-2}$"))
    fig.subplots_adjust(left=0.1, right=0.985, top=1 - 0.55 / altura, bottom=0.95 / altura,
                        hspace=0.42, wspace=0.28)
    legenda_quadro(fig, grade[-1][-1], h, ncol=2, fontsize=6.5, columnspacing=1.5)
    return fig, linhas


def main(linear=False, tcc=False):
    fag.SAIDA = V4 / "figuras" / "perfis"
    if tcc:
        plt.rcParams["pdf.fonttype"] = 42
    v5 = [d for d in ler(V5) if d["configuracao"] in NOVAS] if NOVAS else []
    p = perdas(ler(V4) + v5, "BCD-MMSE (iter 1)")
    if tcc:
        # mesmos dados das barras e das curvas: grade inteira (grade_inteira.py)
        p = gi.Perdas()
        TCC.mkdir(parents=True, exist_ok=True)
        # uma figura só com os três grupos (subseção própria no TCC, depois da tabela dos
        # formatos escolhidos); figura_grupo fica para as versões por grupo
        linhas = []
        for sufixo, iot10 in (("", False), ("_iot10", True)):
            fig, ls = figura_tcc(p, iot10=iot10)
            linhas += [[l[0], ("IoTh 10 dB: " if iot10 else "") + l[1], *l[2:]] for l in ls]
            fig.savefig(TCC / f"perfis_mobilidade{sufixo}.pdf", facecolor=SURFACE,
                        bbox_inches="tight")
            fig.savefig(fag.SAIDA / f"tcc_perfis_mobilidade{sufixo}.png", facecolor=SURFACE,
                        dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(TCC / f"perfis_mobilidade{sufixo}.pdf")
        # versão junta (2026-11-09): A-D com os formatos de IoTh 10 dB e E-H com os de todas
        fig, ls = figura_tcc_ioth(p)
        fig.savefig(TCC / "perfis_mobilidade_ioth.pdf", facecolor=SURFACE, bbox_inches="tight")
        fig.savefig(fag.SAIDA / "tcc_perfis_mobilidade_ioth.png", facecolor=SURFACE, dpi=600,
                    bbox_inches="tight")
        plt.close(fig)
        print(TCC / "perfis_mobilidade_ioth.pdf")
        # versão em 3 colunas (2026-11-11), a usada no TCC
        fig, ls3 = figura_tcc_3col(p)
        fig.savefig(TCC / "perfis_mobilidade_3col.pdf", facecolor=SURFACE, bbox_inches="tight")
        fig.savefig(fag.SAIDA / "tcc_perfis_mobilidade_3col.png", facecolor=SURFACE, dpi=200,
                    bbox_inches="tight")
        plt.close(fig)
        print(TCC / "perfis_mobilidade_3col.pdf")
        import csv
        with open(fag.SAIDA / "tcc_perfis_mobilidade_3col_data.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["grupo", "coluna", "formato", "modo", "nome",
                        "pior_perda_lento_db", "pior_perda_rapido_db"])
            w.writerows(ls3)
        with open(fag.SAIDA / "tcc_perfis_mobilidade_ioth_data.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["grupo", "ioth", "criterio", "formato", "modo", "nome",
                        "pior_perda_lento_db", "pior_perda_rapido_db"])
            w.writerows(ls)
        with open(fag.SAIDA / "tcc_perfis_mobilidade_data.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["grupo", "criterio", "formato", "modo", "nome",
                        "pior_perda_lento_db", "pior_perda_rapido_db"])
            w.writerows(linhas)
        return
    pn = paineis()
    # 2 linhas x 3 colunas, cada painel com a largura da versão de 2 colunas (figura de
    # 1,5 LARGURA); o sexto espaço fica com a legenda
    # altura: 6,6 polegadas eram para 16 configurações; cresce com o número de linhas
    altura = 6.6 * (len(ORDEM) + 1.4) / (16 + 1.4)
    tamanho = (1.5 * LARGURA, altura)
    fig, grade = plt.subplots(2, 3, figsize=tamanho, sharey=True,
                              facecolor=SURFACE)
    axs, livre = grade.flat[:len(FORMATOS)], grade.flat[len(FORMATOS)]
    livre.axis("off")
    falhou = False
    # y: uma linha por configuração, com um espaço entre os grupos (1, 2, 3)
    ys, y = {}, 0
    for k in ORDEM:
        if ys and LETRAS[k][0] != LETRAS[prev][0]:
            y += 0.7
        ys[k], prev, y = y, k, y + 1
    linhas = []
    for ax, (I, F) in zip(axs, FORMATOS):
        eixos(ax, grade_x=False)
        # Fundo no degradê do mapa de perda: a mesma cor quer dizer o mesmo aumento de SNR
        finitos = [v for k in ORDEM for _, cens, *_ in PERFIS
                   if (v := pior(p, k, cens, I, F)) is not None]
        topo = TETO if not linear else max(0.1, 1.15 * max(finitos))
        bx = (np.linspace(0, topo, 300) if linear
              else np.logspace(np.log10(PISO), np.log10(TETO), 300))
        meio = np.maximum((bx[:-1] + bx[1:]) / 2, PISO)
        ax.pcolormesh(bx, [-1, 100], meio[None, :], cmap=DEGRADE, norm=NORMA, zorder=0,
                      rasterized=True)
        for v in (0.1, 3):
            ax.axvline(v, color=INK_PRIMARY if v < 1 else SURFACE, lw=0.9, ls=(0, (3, 2)),
                       zorder=1)
        for k in ORDEM:
            vs = [pior(p, k, cens, I, F) for _, cens, *_ in PERFIS]
            xs = [TETO if v is None else (v if linear else max(v, PISO)) for v in vs]
            if linear:
                xs = [topo if v is None else v for v in vs]
            # traço só entre as bordas dos pontos, para não atravessar o vazado
            if None not in vs:
                ax.annotate("", xy=(xs[1], ys[k]), xytext=(xs[0], ys[k]), zorder=2,
                            arrowprops=dict(arrowstyle="-", color=COR, lw=1.2,
                                            shrinkA=3.4, shrinkB=3.4))
            for (nome, _, m, face), x, v in zip(PERFIS, xs, vs):
                if v is None:
                    falhou = True
                    ax.plot(x, ys[k], marker="x", color=VERMELHO, ms=5, mew=1.3, zorder=3,
                            clip_on=False)
                else:
                    ax.plot(x, ys[k], marker=m, ms=5.5, mfc=face, mec=COR, mew=1.5,
                            ls="none", zorder=3)
            q = pn[k]
            linhas.append([f"<{I + F},{I}>", LETRAS[k], k, q.M, q.C, q.K, f"{q.iot_db:g}",
                           q.modulation, *("" if v is None else f"{v:.3f}" for v in vs),
                           "" if None in vs else f"{abs(vs[0] - vs[1]):.3f}"])
        ax.set_ylim(y - 0.5, -0.5)
        if linear:
            # cada painel com o seu alcance, para as diferenças pequenas aparecerem
            ax.set_xlim(0, topo)
        else:
            ax.set_xscale("log")
            ax.set_xlim(PISO, TETO)
            ax.set_xticks([0.01, 0.03, 0.1, 0.3, 1, 3],
                          ["≤ 0.01", "0.03", "0.1", "0.3", "1", "3"])
        ax.tick_params(axis="both", labelsize=7)
        ax.set_title(f"<{I + F},{I}>", fontsize=8, color=INK_PRIMARY, loc="left")
        ax.set_xlabel("Worst SNR increase [dB]", fontsize=7.5, color=INK_SECONDARY)
    for linha in grade:
        linha[0].set_yticks([ys[k] for k in ORDEM], [LETRAS[k] for k in ORDEM])
        linha[0].set_ylabel("Configuration", fontsize=7.5, color=INK_SECONDARY)
    fig.suptitle("Worst SNR increase over float at SER = $10^{-2}$ per mobility profile\n"
                 "(BCD-MMSE, 1 iteration, RND_ZERO/WRAP)", fontsize=9, color=INK_PRIMARY)
    h = [Line2D([], [], marker=m, mfc=face, mec=COR, ls="none", ms=5.5, mew=1.5,
                label=f"{nome}:\n{', '.join(NOMES.get(c, c) for c in cens)}")
         for nome, cens, m, face in PERFIS]
    h.append(Line2D([], [], color=INK_PRIMARY, lw=0.9, ls=(0, (3, 2)),
                    label="0.1 dB and 3 dB limits"))
    if falhou:
        h.append(Line2D([], [], marker="x", color=VERMELHO, ls="none", ms=5, mew=1.3,
                        label="does not reach SER = $10^{-2}$"))
    livre.legend(handles=h, loc="center left", frameon=False, fontsize=6.5,
                 labelcolor=INK_SECONDARY, labelspacing=1.2)
    fig.tight_layout()
    salvar(fig, "perfis_mobilidade" + ("_linear" if linear else ""), linhas,
           ["formato", "nome", "configuracao", "M", "C", "K", "iot_db", "modulacao",
            "pior_perda_lento_db", "pior_perda_rapido_db", "diferenca_db"])


if __name__ == "__main__":
    import sys
    main(linear="--linear" in sys.argv, tcc="--tcc" in sys.argv)
