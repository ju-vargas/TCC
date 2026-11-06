#!/usr/bin/env python3
"""
Perfil de SER de uma estação num formato, no estilo de um relatório de perfil (faixas de
percentis ao longo do eixo x, com um resumo em barra empilhada e um bloco de métricas).

Uma figura por formato e estação (G1, G2, G3). Em cima:
- barra empilhada: fração dos casos (configuração x par) com perda até 0,1 dB, de 0,1 a 3 dB
  e acima de 3 dB (perda do BCD-MMSE com 1 iteração no formato contra o mesmo em float, em
  SER = 1e-2, como nos mapas);
- métricas: pior perda e onde ocorre, perda mediana e quanto de SNR o BCD-MMSE precisa a
  mais que o LMMSE (os dois em float).
Embaixo, um painel por configuração da estação. Em cada painel, LMMSE, ZF e BCD-MMSE com
1 iteração no formato: a faixa vai do menor ao maior SER entre os 5 pares (N, portadora) em
cada SNR, e a linha é a mediana dos 5. Com só 5 pares, percentis não teriam significado. O
tracejado fino é a mediana do BCD-MMSE em float, a referência da perda.

Saída: resultados/5_candidatos/modo_fixo_3dB/figuras/perfil_estacao/
       perfil_<estação>_<W>-<I>.{png,pdf} e _data.csv

Com --por cenario: um painel por par (N, portadora) e a faixa entre as configurações da
estação, em perfil_por_cenario_<estação>[_<modulação>]_<W>-<I>. No G1, 16-QAM e QPSK ficam
em figuras separadas (--mod), porque a modulação desloca as curvas em vários dB.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_perfil_estacao.py [--estacao G1] [--formato 24-12]
        [--por configuracao|cenario] [--mod 16QAM|QPSK] [--todas]
"""

import argparse
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from figuras_analise_grupos import (ALL_PANELS, CENARIOS, ESTACOES, FAIXAS, FORMATOS, GRADE,
                                    INK_MUTED, INK_PRIMARY, INK_SECONDARY,
                                    LARGURA, LETRAS, MODULATION_LABEL, PASTA,
                                    SURFACE, TCC_CONFIGURATION, carregar,
                                    eixos, estado_snr, num, perda, salvar)
import figuras_analise_grupos as fag

PISO = 1e-4   # piso do eixo de SER: pontos sem erro ficam nele
# Cores: LMMSE vermelho e BCD-MMSE amarelo forte (os da bcd_iterations), ZF cinza; sem
# verde, a pedido da autora. validate_palette.js --pairs all: CVD pior 11,1 (deutan), visão
# normal pior 20,4; o cinza é neutro de propósito (falha só no piso de croma) e o amarelo
# fica abaixo de 3:1 no fundo, por isso cada faixa tem borda e a linha da mediana.
# As faixas do LMMSE e do ZF são preenchidas; a do BCD-MMSE é só hachurada (linhas finas),
# para que a sobreposição mostre as duas em vez de uma cor de mistura (vermelho com
# amarelo virava laranja). O BCD-MMSE no formato é azul, o mesmo do mapa de perda e da
# parte do formato nas barras (MANUAL_GRAFICOS.md); validate_palette.js --pairs all com
# o vermelho e o cinza: CVD pior 11,1, visão normal 21,2.
COR_LMMSE, COR_ZF, COR_BCD = "#d62828", "#8a8983", "#eda100"   # BCD-MMSE em amarelo forte, como a parte float das barras
plt.rcParams["hatch.linewidth"] = 0.45   # padrão 1,0
CURVAS = (("LMMSE", "LMMSE", COR_LMMSE),
          ("ZF", "ZF", COR_ZF))


def painel(ax, fontes, fmt, rot, rotulo):
    """Faixa (mínimo a máximo entre as fontes) e mediana de cada curva. fontes: lista de
    {curva: SER}, uma por par (painel de configuração) ou por configuração (painel de
    cenário); rotulo: as primeiras colunas do CSV."""
    eixos(ax, grade_x=True, grade_y=True)
    ax.set_yscale("log")
    ax.set_ylim(PISO, 1)
    ax.set_xlim(-10, 10)
    linhas = []
    for chave, nome, cor in (*CURVAS, (fmt, f"BCD-MMSE (iter 1), {rot}", COR_BCD)):
        m = np.array([np.maximum(f[chave], PISO) for f in fontes])
        lo, mid, hi = m.min(0), np.median(m, 0), m.max(0)
        if cor == COR_BCD:
            ax.fill_between(GRADE, lo, hi, facecolor="none", edgecolor=cor, hatch="////",
                            lw=0, zorder=2.5)
        else:
            ax.fill_between(GRADE, lo, hi, color=cor, alpha=0.18, lw=0, zorder=2)
        for borda in (lo, hi):
            ax.plot(GRADE, borda, color=cor, lw=0.6, alpha=0.8, zorder=2.6)
        ax.plot(GRADE, mid, color=cor, lw=1.6, zorder=3)
        linhas += [[*rotulo, nome, est, *v] for est, v in
                   (("minimo", lo), ("mediana", mid), ("maximo", hi))]
    ref = np.median([np.maximum(f["BCD"], PISO) for f in fontes], 0)
    ax.plot(GRADE, ref, color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)), zorder=4)
    ax.axhline(1e-2, color=INK_MUTED, lw=0.6, ls=":", zorder=1)
    linhas.append([*rotulo, "BCD-MMSE (iter 1), float", "mediana", *ref])
    return linhas


# Textos da figura em inglês, ponto decimal (MANUAL_GRAFICOS.md)
plt.rcParams["mathtext.default"] = "regular"
CENARIOS_EN = {c: t.replace(" e ", " and ").replace("3,5", "3.5") for c, t in CENARIOS.items()}


def cabecalho(ax, rot, modo):
    """Formato em cima e o modo embaixo, menor e mais fino (como nas barras)."""
    ax.set_title(rot, fontsize=8.5, color=INK_PRIMARY, pad=12)
    ax.annotate(modo, (0.5, 1), xycoords="axes fraction", xytext=(0, 3),
                textcoords="offset points", ha="center", va="bottom", fontsize=6.5,
                fontweight="light", color=INK_SECONDARY)


def eixo_snr(ax):
    """Eixo de SNR com marcas e números a cada 2,5 dB em todos os painéis."""
    marcas = np.arange(-10, 10.1, 2.5)
    ax.set_xticks(marcas, [f"{v:g}".replace("-", "−") for v in marcas])
    ax.tick_params(axis="x", labelsize=6, labelbottom=True)


def faixa_legenda(cor, rotulo):
    """Amostra da faixa na legenda: preenchida (LMMSE, ZF) ou hachurada (BCD-MMSE)."""
    if cor == COR_BCD:
        return Patch(facecolor="none", edgecolor=cor, hatch="////", lw=0.6, label=rotulo)
    return Patch(facecolor=(*matplotlib.colors.to_rgb(cor), 0.25), edgecolor=cor, lw=0.6,
                 label=rotulo)


def metricas(ser, ks, fmt):
    """Perdas dos casos (config, par) e as métricas do bloco da direita."""
    casos = {(k, c): perda(ser[(c, k)], fmt) for k in ks for c in CENARIOS}
    validos = {kc: v for kc, (v, _) in casos.items() if v is not None}
    pior = max(validos, key=validos.get)
    gap = []
    for k in ks:
        for c in CENARIOS:
            xl, _ = estado_snr(ser[(c, k)]["LMMSE"])
            xb, _ = estado_snr(ser[(c, k)]["BCD"])
            if xl is not None and xb is not None:
                gap.append(xb - xl)
    return casos, validos, pior, gap


def figura(ser, estacao, fmt, por="configuracao", mod=None):
    """por = "configuracao": um painel por configuração, faixa entre os 5 pares.
    por = "cenario": um painel por par, faixa entre as configurações da estação (com a
    modulação mod, para não misturar 16-QAM e QPSK no G1)."""
    g, M, C, ks = next(e for e in ESTACOES if e[0] == estacao)
    rot = FORMATOS[fmt][0]
    modo = fag.MODO[FORMATOS[fmt][1]]
    paineis = {TCC_CONFIGURATION[p.label]: p for p in ALL_PANELS}
    if mod:
        ks = tuple(k for k in ks if paineis[k].modulation == mod)
    ncol = 2
    if por == "cenario":
        itens_p = list(CENARIOS)
        pos = {c: (i // 2, i % 2) for i, c in enumerate(itens_p)}
    else:
        itens_p = list(ks)
        # Grade: linhas por (K, IoT); colunas por modulação (G1) ou 2 x 2 (G2, G3)
        mods = sorted({paineis[k].modulation for k in ks}, key=lambda m: m != "16QAM")
        if len(mods) > 1:
            pos = {k: ((ks.index(k) % 4), mods.index(paineis[k].modulation)) for k in ks}
        else:
            pos = {k: (i // 2, i % 2) for i, k in enumerate(ks)}
    nlin = max(r for r, _ in pos.values()) + 1

    altura = 0.75 + 1.75 * nlin
    fig = plt.figure(figsize=(LARGURA, altura))
    fig.patch.set_facecolor(SURFACE)
    gs = GridSpec(nlin, ncol, figure=fig, hspace=0.5, wspace=0.12)

    # ---- painéis
    linhas = []
    ultima = {}   # última linha ocupada em cada coluna (onde vai o rótulo do eixo x)
    for item in itens_p:
        ultima[pos[item][1]] = max(ultima.get(pos[item][1], 0), pos[item][0])
    for item in itens_p:
        r, c = pos[item]
        ax = fig.add_subplot(gs[r, c])
        if por == "cenario":
            linhas += painel(ax, [ser[(item, k)] for k in ks], fmt, rot, [item])
            titulo = CENARIOS_EN[item].replace(": ", "   ")
        else:
            linhas += painel(ax, [ser[(cc, item)] for cc in CENARIOS], fmt, rot,
                             [LETRAS[item], item])
            p = paineis[item]
            titulo = (f"{LETRAS[item]} ({item})   $K$ = {p.K}, IoTh = {p.iot_db:g} dB, "
                      f"{MODULATION_LABEL.get(p.modulation, p.modulation)}")
        ax.set_title(titulo, fontsize=7.5, color=INK_PRIMARY, pad=3, loc="left")
        if c == 0:
            ax.set_ylabel("SER", color=INK_SECONDARY)
        else:
            ax.tick_params(labelleft=False)
        if r == ultima[c]:
            ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
        eixo_snr(ax)

    nome_mod = f", {MODULATION_LABEL.get(mod, mod)}" if mod else ""
    fig.suptitle(f"{nome_mod.lstrip(', ') + ': ' if nome_mod else ''}$M$ = {M}, $C$ = {C}, "
                 f"$M_c$ = {M // C}   |   {rot} {modo}", fontsize=9.5, color=INK_PRIMARY, y=0.995)
    if por == "cenario":
        de = f"over the {len(ks)} configurations ({', '.join(sorted(LETRAS[k] for k in ks))})"
    else:
        de = "over the 5 test conditions"
    handles = [faixa_legenda(cor, f"{nome}, range {de}")
               for _, nome, cor in (*CURVAS, (None, f"BCD-MMSE (iter 1), {rot}", COR_BCD))]
    handles += [Line2D([], [], color=INK_SECONDARY, lw=1.6,
                       label=f"solid line: median {de.split(' (')[0]}"),
                Line2D([], [], color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)),
                       label="BCD-MMSE (iter 1) in float, reference (median)")]
    if por == "cenario" and len(itens_p) % 2:
        # a legenda ocupa o lugar vazio da grade (ao lado do último painel)
        axl = fig.add_subplot(gs[nlin - 1, 1])
        axl.axis("off")
        curtos = [faixa_legenda(cor, nome)
                  for _, nome, cor in (*CURVAS, (None, f"BCD-MMSE (iter 1), {rot}", COR_BCD))]
        curtos += [Line2D([], [], color=INK_SECONDARY, lw=1.6,
                          label=f"median over the {len(ks)} configurations"),
                   Line2D([], [], color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)),
                          label="BCD-MMSE (iter 1) in float,\nreference (median)")]
        leg = axl.legend(handles=curtos, loc="center", frameon=False, fontsize=7,
                         labelcolor=INK_SECONDARY, alignment="left",
                         title=f"Range: lowest to highest SER over\nconfigurations "
                               f"{', '.join(sorted(LETRAS[k] for k in ks))}")
        leg.get_title().set_fontsize(7)
        leg.get_title().set_color(INK_PRIMARY)
        fig.subplots_adjust(left=0.1, right=0.98, top=1 - 0.45 / altura, bottom=0.45 / altura)
    else:
        fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=7,
                   labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, -0.005))
        fig.subplots_adjust(left=0.1, right=0.98, top=1 - 0.45 / altura,
                            bottom=0.6 / altura + 0.06)

    fag.SAIDA = PASTA / "figuras" / "perfil_estacao"
    sufixo = f"_{mod.replace('16QAM', '16qam').lower()}" if mod else ""
    prefixo = "perfil_por_cenario" if por == "cenario" else "perfil"
    nome = f"{prefixo}_{g}{sufixo}_{rot.strip('<>').replace(',', '-')}"
    cab = ["par"] if por == "cenario" else ["letra", "configuracao"]
    salvar(fig, nome, linhas, [*cab, "curva", "estatistica", *[f"{s:g}" for s in GRADE]])
    grupo = f"{g}{nome_mod.replace(', ', ' ')}" if mod else g
    return linha_tabela(ser, ks, fmt, grupo)


def linha_tabela(ser, ks, fmt, grupo):
    """Métricas de um grupo (estação ou estação e modulação) num formato, para a tabela."""
    casos, validos, pior, gap = metricas(ser, ks, fmt)
    n = len(casos)
    cont = [sum(1 for v, _ in casos.values() if v is not None and round(v, 2) <= FAIXAS[0][0]),
            sum(1 for v, _ in casos.values()
                if v is not None and FAIXAS[0][0] < round(v, 2) <= FAIXAS[1][0]),
            sum(1 for v, _ in casos.values() if v is None or round(v, 2) > FAIXAS[1][0])]
    (kp, cp), vp = pior, validos[pior]
    return dict(grupo=grupo, formato=FORMATOS[fmt][0], configs=", ".join(LETRAS[k] for k in ks),
                n=n, ate01=cont[0], ate3=cont[1], acima3=cont[2], pior=vp,
                pior_onde=f"{LETRAS[kp]}, {cp}",
                mediana=float(np.median(list(validos.values()))),
                gap_med=float(np.median(gap)), gap_min=min(gap), gap_max=max(gap))


def tabela(linhas):
    """CSV e LaTeX (estilo das tabelas do TCC) com as métricas que saíram das figuras."""
    import csv
    pasta = PASTA / "figuras" / "perfil_estacao"
    with open(pasta / "tabela_perfil.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)

    def pct(c, n):
        return f"{round(100 * c / n)}\\% ({c})"

    tex = [r"\begin{table}[htbp]",
           r"\caption{Perda de SNR do BCD-MMSE com 1 iteração em ponto fixo contra o mesmo em "
           r"float, em SER = $10^{-2}$, por estação e formato. Cada caso é uma configuração em "
           r"um par ($N$, portadora); as colunas das faixas dão a fração e o número de casos. "
           r"Perdas em dB.}",
           r"\label{tab:perfil-perdas}", r"\centering", r"\footnotesize",
           r"\renewcommand{\arraystretch}{1.2}",
           r"\begin{tabular}{|c|c|c|c|c|c|c|}", r"\hline",
           r"Grupo & Formato & Até 0,1 & De 0,1 a 3 & Acima de 3 & Pior perda (onde) "
           r"& Mediana \\", r"\hline"]
    for i, l in enumerate(linhas):
        # Grupo na primeira linha e as configurações na segunda (sem \multirow, que o TCC
        # não carrega)
        j = sum(1 for m in range(i) if linhas[m]["grupo"] == l["grupo"])   # posição no grupo
        grupo = {0: l["grupo"], 1: f"({l['configs']})"}.get(j, "")
        pior = f"{num(l['pior'])} ({l['pior_onde']})"
        tex.append(f"{grupo} & {l['formato'].replace('<', '$<$').replace('>', '$>$')} & "
                   f"{pct(l['ate01'], l['n'])} & {pct(l['ate3'], l['n'])} & "
                   f"{pct(l['acima3'], l['n'])} & {pior} & {num(l['mediana'])} \\\\")
        ultima_do_grupo = i == len(linhas) - 1 or linhas[i + 1]["grupo"] != l["grupo"]
        tex.append(r"\hline" if ultima_do_grupo else r"\cline{2-7}")
    tex += [r"\end{tabular}", r"\end{table}", "",
            r"\begin{table}[htbp]",
            r"\caption{Quanto o BCD-MMSE com 1 iteração perde para o LMMSE (SNR a mais em "
            r"SER = $10^{-2}$, os dois em float), por estação.}",
            r"\label{tab:perfil-bcd-lmmse}", r"\centering", r"\footnotesize",
            r"\renewcommand{\arraystretch}{1.2}",
            r"\begin{tabular}{|c|c|c|c|}", r"\hline",
            r"Grupo & Mediana (dB) & Menor (dB) & Maior (dB) \\", r"\hline"]
    vistos = []
    for l in linhas:
        if l["grupo"] in vistos:
            continue
        vistos.append(l["grupo"])
        tex.append(f"{l['grupo']} ({l['configs']}) & {num(l['gap_med'], 1)} & "
                   f"{num(l['gap_min'], 1)} & {num(l['gap_max'], 1)} \\\\")
        tex.append(r"\hline")
    tex += [r"\end{tabular}", r"\end{table}"]
    (pasta / "tabela_perfil.tex").write_text("\n".join(tex) + "\n")
    print(pasta / "tabela_perfil.tex")


# Painéis escolhidos para comparar os formatos dentro de cada grupo: o cenário de pior perda
# do <22,12> e o TDLB100-400 (N = 24), o único que muda bastante o resultado (faixa do LMMSE
# mais larga, BCD-MMSE mais perto do LMMSE e, no G2 e no G1 QPSK, a perda do formato).
SELECAO = (("G1", "16QAM", ("TDLC300-100", "TDLB100-400")),
           ("G1", "QPSK", ("TDLC300-100", "TDLB100-400")),
           ("G2", None, ("TDLA30-75", "TDLB100-400")),
           ("G3", None, ("TDLA30-5", "TDLB100-400")))
FMTS_COMPARACAO = ((12, 10), (12, 12), (14, 14))


def figura_formatos(ser, estacao, mod, cenarios):
    """Uma linha por cenário escolhido e uma coluna por formato; faixas entre as
    configurações do grupo, como em --por cenario."""
    g, M, C, ks = next(e for e in ESTACOES if e[0] == estacao)
    paineis = {TCC_CONFIGURATION[p.label]: p for p in ALL_PANELS}
    if mod:
        ks = tuple(k for k in ks if paineis[k].modulation == mod)
    nlin, ncol = len(cenarios), len(FMTS_COMPARACAO)
    altura = 1.25 + 1.85 * nlin
    fig, axs = plt.subplots(nlin, ncol, figsize=(LARGURA, altura), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    linhas = []
    for i, c in enumerate(cenarios):
        for j, fmt in enumerate(FMTS_COMPARACAO):
            ax = axs[i][j]
            rot = FORMATOS[fmt][0]
            linhas += painel(ax, [ser[(c, k)] for k in ks], fmt, rot, [c, rot])
            eixo_snr(ax)
            if i == 0:
                cabecalho(ax, rot, fag.MODO[FORMATOS[fmt][1]])
            if j > 0:
                ax.tick_params(labelleft=False)
            if j == 0:
                ax.set_ylabel(f"{CENARIOS_EN[c].split(':')[0]}\n{CENARIOS_EN[c].split(': ')[1]}"
                              "\n\nSER", color=INK_SECONDARY, fontsize=7.5)
            if i == nlin - 1:
                ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    nome_mod = f", {MODULATION_LABEL.get(mod, mod)}" if mod else ""
    fig.suptitle(f"{nome_mod.lstrip(', ') + ': ' if nome_mod else ''}$M$ = {M}, $C$ = {C}, "
                 f"$M_c$ = {M // C}   |   configurations {', '.join(sorted(LETRAS[k] for k in ks))}", fontsize=9,
                 color=INK_PRIMARY, y=0.995)
    handles = [faixa_legenda(COR_LMMSE, "LMMSE"), faixa_legenda(COR_ZF, "ZF"),
               faixa_legenda(COR_BCD, "BCD-MMSE (iter 1) in fixed point"),
               Line2D([], [], color=INK_SECONDARY, lw=1.6,
                      label=f"median over the {len(ks)} configurations"),
               Line2D([], [], color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)),
                      label="BCD-MMSE (iter 1) in float (median)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=7,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, 0.0),
               title=f"Range: lowest to highest SER over the {len(ks)} configurations",
               title_fontsize=7)
    # colunas próximas: deixa os painéis largos o bastante para os 9 números do eixo x
    fig.subplots_adjust(left=0.13, right=0.98, top=1 - 0.6 / altura,
                        bottom=0.95 / altura, hspace=0.28, wspace=0.12)
    fag.SAIDA = PASTA / "figuras" / "perfil_estacao"
    sufixo = f"_{mod.lower()}" if mod else ""
    salvar(fig, f"comparacao_formatos_{g}{sufixo}", linhas,
           ["par", "formato", "curva", "estatistica", *[f"{x:g}" for x in GRADE]])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--estacao", default="G1", choices=[e[0] for e in ESTACOES])
    ap.add_argument("--formato", default="24-12", help="22-12, 24-12, 26-12, 28-14 ou 30-14")
    ap.add_argument("--por", default="configuracao", choices=["configuracao", "cenario"],
                    help="um painel por configuração (faixa = pares) ou por par (faixa = "
                         "configurações)")
    ap.add_argument("--mod", choices=["16QAM", "QPSK"],
                    help="só as configurações com essa modulação (no G1 com --por cenario)")
    ap.add_argument("--todas", action="store_true",
                    help="<22,12>, <24,12> e <28,14> nas 3 estações (G1 separado por "
                         "modulação quando --por cenario)")
    ap.add_argument("--comparar-formatos", action="store_true",
                    help="uma figura por grupo com os cenários de SELECAO nas linhas e os "
                         "3 formatos nas colunas")
    args = ap.parse_args()
    ser = carregar()
    if args.comparar_formatos:
        for g, m, cens in SELECAO:
            figura_formatos(ser, g, m, cens)
        return
    if args.todas:
        linhas = []
        for g, *_ in ESTACOES:
            mods = ("16QAM", "QPSK") if (g == "G1" and args.por == "cenario") else (None,)
            for m in mods:
                for f in ("22-12", "24-12", "28-14"):
                    fmt = next(x for x, v in FORMATOS.items() if v[2] == f)
                    linhas.append(figura(ser, g, fmt, args.por, m))
        if args.por == "cenario":
            tabela(linhas)
        return
    fmt = next(f for f, v in FORMATOS.items() if v[2] == args.formato)
    figura(ser, args.estacao, fmt, args.por, args.mod)


if __name__ == "__main__":
    sys.exit(main())
