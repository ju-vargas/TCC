#!/usr/bin/env python3
"""
Pior aumento de SNR do BCD-MMSE (iter 1) no formato sobre o float, em SER = 10^-2, por perfil de
mobilidade: lento (TDLA30-5/-10 e TDLA30-75, até ~3 km/h) e rápido (TDLA30-300, TDLC300-100 e
TDLB100-400, de ~12 a ~123 km/h). Pontos pareados: uma linha por configuração, um ponto por
perfil, um painel por formato (<18,8>, <20,8>, <22,12>, <24,12> e <28,12>, todos no modo fixo
RND_ZERO/WRAP), com o fundo no degradê do mapa de perda. Dados da [4] v4, os mesmos do mapa.
Mostra que a escolha do formato não muda entre os perfis.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_perfis.py [--linear]

Com --linear, eixo x linear, com um alcance por painel (..._linear).
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import figuras_analise_grupos as fag
from figuras_analise_grupos import LARGURA, eixos, salvar
from figuras_formatos import ler, perdas
from mapa_cenarios_v4 import DEGRADE, LETRAS, NORMA, paineis
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
ORDEM = sorted(LETRAS, key=lambda k: LETRAS[k])   # 1A ... 3F


def pior(p, k, cens, I, F):
    vs = [p[(k, c, I, F, *MODO)] for c in cens]
    return None if None in vs else max(vs)


def main(linear=False):
    fag.SAIDA = V4 / "figuras" / "perfis"
    p = perdas(ler(V4), "BCD-MMSE (iter 1)")
    pn = paineis()
    # 2 linhas x 3 colunas, cada painel com a largura da versão de 2 colunas (figura de
    # 1,5 LARGURA); o sexto espaço fica com a legenda
    fig, grade = plt.subplots(2, 3, figsize=(1.5 * LARGURA, 6.6), sharey=True,
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
    main(linear="--linear" in sys.argv)
