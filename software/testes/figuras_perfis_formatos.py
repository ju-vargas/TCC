#!/usr/bin/env python3
"""
Maior aumento de SNR em SER = 10^-2 por formato e por perfil de mobilidade (2026-11-13).

Um painel por grupo (linhas) e por conjunto de configurações (colunas: A a H e só IoTh de
10 dB, A a D). Em cada painel, as linhas são os 10 formatos do mapa, na ordem do mapa, cada
um no modo fixo do mapa do grupo. Cada ponto é o maior aumento entre as configurações do
painel e as condições de um perfil: vazado = baixa mobilidade, cheio = alta mobilidade.
O formato escolhido por um perfil é o primeiro, de cima para baixo, com o ponto até o limite
(0,1 dB ou 3 dB, arredondado em 2 casas, como na Tabela tab:formatos-escolhidos). À direita,
o rótulo diz qual critério o formato atende primeiro em cada perfil.

Saída: TCC/Images/RESULTADOS/perfis_mobilidade_formatos.pdf e, em <V4>/figuras/perfis/,
tcc_perfis_mobilidade_formatos.png e _data.csv.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_perfis_formatos.py
"""

import csv

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import grade_inteira as gi
import mapa_cenarios_v4 as mc
import mapa_grupos_v4 as mg
from figuras_analise_grupos import LARGURA, eixos, legenda_quadro
from figuras_formatos import ler, perdas
from figuras_perfis import COR, NOMES, PERFIS, TCC, VERMELHO
from dbp_sim.plotting import INK_PRIMARY, INK_SECONDARY, SURFACE

plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["pdf.fonttype"] = 42

PISO, TETO = 0.01, 30.0
LIMITES = (3, 0.1)
MODO_PADRAO = ("AP_RND_ZERO", "AP_WRAP")
SAIDA = mg.V4 / "figuras" / "perfis"


def dados():
    """{grupo: (linhas de formato [(I, F, modo)], {subconjunto: [configurações]})} e as
    células da grade inteira. Modo de cada formato: o do mapa do grupo (mapa_grupos_v4)."""
    mc.NOMES.update(mc.LETRAS)
    mc.NOMES.update(mg.LETRAS_NOVAS)
    circuitos = {n: (*ks, *(k for k, m in mg.NOVAS.items() if m == n))
                 for n, ks in mg.CIRCUITOS.items()}
    mc.CIRCUITOS = circuitos
    v5 = [d for d in ler(mg.V5) if d["configuracao"] in mg.NOVAS] if mg.NOVAS else []
    p = perdas(ler(mg.V4) + v5, f"BCD-MMSE (iter {mg.T})")
    occ_n = {n: mg.ocupacao(n) for n in circuitos}
    occ_k = {k: occ_n[n] for n, ks in circuitos.items() for k in ks}
    linhas = mc.ORDENS[mg.POR]
    pn = mc.paineis()
    ordem = sorted([*mg.CONFIGS, *mg.NOVAS],
                   key=lambda k: (pn[k].iot_db, pn[k].modulation != "16QAM", pn[k].K))
    pc = gi.Perdas()
    out = {}
    for g, (M, C) in mg.GRUPOS.items():
        ks = [k for k in ordem if (pn[k].M, pn[k].C) == (M, C)]
        _, modos = mc.modo_fixo(p, occ_k, ks, linhas, mg.LIMITE, p_celulas=pc)
        n = next(n for n, cs in circuitos.items() if ks[0] in cs)
        fmts = [(I, F, e[n]) for (I, F), e in zip(linhas, modos)]
        out[g] = (fmts, {"A-H": ks, "A-D": [k for k in ks if pn[k].iot_db == 10]})
    return out, pc


def pior(pc, ks, cens, I, F, modo):
    vs = [pc[(k, c, I, F, *modo)] for k in ks for c in cens]
    return None if None in vs else max(vs)


def escolhido(vals, lim):
    """Índice do primeiro formato (menor W) com o pior aumento até o limite."""
    return next((i for i, v in enumerate(vals) if v is not None and round(v, 2) <= lim), None)


def rotulo(I, F, modo):
    r = f"<{I + F},{I}>"
    return r if tuple(modo) == MODO_PADRAO else f"{r} {modo[0][3:]}/{modo[1][3:]}"


def painel(ax, pc, fmts, ks):
    eixos(ax, grade_x=False)
    bx = np.logspace(np.log10(PISO), np.log10(TETO), 300)
    meio = np.maximum((bx[:-1] + bx[1:]) / 2, PISO)
    ax.pcolormesh(bx, [-1, 100], meio[None, :], cmap=mc.DEGRADE, norm=mc.NORMA, zorder=0,
                  rasterized=True)
    for v in LIMITES:
        ax.axvline(v, color=INK_PRIMARY if v < 1 else SURFACE, lw=0.9, ls=(0, (3, 2)), zorder=1)
    vals = [[pior(pc, ks, cens, I, F, m) for I, F, m in fmts] for _, cens, *_ in PERFIS]
    falhou = False
    for y, (I, F, m) in enumerate(fmts):
        vs = [vals[0][y], vals[1][y]]
        xs = [TETO if v is None else max(v, PISO) for v in vs]
        if None not in vs:
            ax.annotate("", xy=(xs[1], y), xytext=(xs[0], y), zorder=2,
                        arrowprops=dict(arrowstyle="-", color=COR, lw=1.0, shrinkA=3,
                                        shrinkB=3))
        for (_, _, mk, face), x, v in zip(PERFIS, xs, vs):
            if v is None:
                falhou = True
                ax.plot(x, y, marker="x", color=VERMELHO, ms=4, mew=1.1, zorder=3,
                        clip_on=False)
            else:
                ax.plot(x, y, marker=mk, ms=4, mfc=face, mec=COR, mew=1.1, ls="none",
                        zorder=3)
    # à direita: o critério que o formato atende primeiro em cada perfil
    marcas = {}
    for lim in LIMITES:
        lento, rapido = (escolhido(v, lim) for v in vals)
        if lento == rapido:
            marcas.setdefault(rapido, []).append(f"{lim:g} dB")
        else:
            marcas.setdefault(rapido, []).append(f"{lim:g} dB high")
            marcas.setdefault(lento, []).append(f"{lim:g} dB low")
    for y, txt in marcas.items():
        if y is not None:
            ax.annotate("◂ " + ", ".join(txt), (1, y), xycoords=("axes fraction", "data"),
                        xytext=(3, 0), textcoords="offset points", va="center", ha="left",
                        fontsize=5.8, color=INK_PRIMARY, annotation_clip=False)
    # só o formato no eixo; os modos ficam na legenda da figura no texto do TCC
    ax.set_yticks(range(len(fmts)), [f"<{I + F},{I}>" for I, F, _ in fmts])
    ax.set_ylim(len(fmts) - 0.5, -0.5)
    ax.set_xscale("log")
    ax.set_xlim(PISO / 1.35, TETO)
    ax.set_xticks([0.01, 0.1, 1, 3, 10], ["≤ 0.01", "0.1", "1", "3", "10"])
    ax.minorticks_off()
    ax.tick_params(axis="both", labelsize=6, pad=2)
    linhas = [[rotulo(*f), "" if a is None else f"{a:.3f}", "" if b is None else f"{b:.3f}"]
              for f, a, b in zip(fmts, *vals)]
    return falhou, linhas


def figura():
    grupos, pc = dados()
    colunas = (("A-H", "All configurations"), ("A-D", "IoTh 10 dB only"))
    altura = 7.2
    fig, grade = plt.subplots(3, 2, figsize=(LARGURA, altura), facecolor=SURFACE)
    falhou, linhas = False, []
    for (g, (fmts, subs)), linha in zip(grupos.items(), grade):
        for j, (ax, (sub, cab)) in enumerate(zip(linha, colunas)):
            f_, ls = painel(ax, pc, fmts, subs[sub])
            falhou |= f_
            linhas += [[g, cab, *l] for l in ls]
            if j == 0:
                ax.set_ylabel(f"Group {g}", fontsize=7, color=INK_SECONDARY)
            if g == 1:
                ax.set_title(cab, fontsize=7, color=INK_PRIMARY, pad=6)
            if g == 3:
                ax.set_xlabel("Worst SNR increase [dB]", fontsize=6.5, color=INK_SECONDARY)
    h = [Line2D([], [], marker=m, mfc=face, mec=COR, ls="none", ms=4, mew=1.1,
                label=f"{nome}: {', '.join(NOMES.get(c, c) for c in cens)}")
         for nome, cens, m, face in PERFIS]
    h.append(Line2D([], [], color=INK_PRIMARY, lw=0.9, ls=(0, (3, 2)),
                    label="0.1 dB and 3 dB limits"))
    if falhou:
        h.append(Line2D([], [], marker="x", color=VERMELHO, ls="none", ms=4, mew=1.1,
                        label="does not reach SER = $10^{-2}$"))
    fig.subplots_adjust(left=0.1, right=0.9, top=1 - 0.35 / altura, bottom=0.85 / altura,
                        hspace=0.28, wspace=0.62)
    legenda_quadro(fig, grade[-1][-1], h, ncol=2, fontsize=6.5, columnspacing=1.5)
    return fig, linhas


def main():
    fig, linhas = figura()
    SAIDA.mkdir(parents=True, exist_ok=True)
    TCC.mkdir(parents=True, exist_ok=True)
    fig.savefig(TCC / "perfis_mobilidade_formatos.pdf", facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(SAIDA / "tcc_perfis_mobilidade_formatos.png", facecolor=SURFACE, dpi=250,
                bbox_inches="tight")
    plt.close(fig)
    with open(SAIDA / "tcc_perfis_mobilidade_formatos_data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["grupo", "configuracoes", "formato", "pior_aumento_baixa_db",
                    "pior_aumento_alta_db"])
        w.writerows(linhas)
    print(TCC / "perfis_mobilidade_formatos.pdf")


if __name__ == "__main__":
    main()
