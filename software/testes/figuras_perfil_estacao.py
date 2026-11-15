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
    ../simulador/.venv/bin/python figuras_perfil_estacao.py --comparar-formatos --tcc
"""

import argparse
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from figuras_analise_grupos import legenda_quadro
from figuras_analise_grupos import (ABREV_CENARIO, ALL_PANELS, CENARIOS, ESTACOES, FAIXAS, FORMATOS, GRADE,
                                    INK_MUTED, INK_PRIMARY, INK_SECONDARY,
                                    LARGURA, LETRAS, MODULATION_LABEL, PASTA,
                                    SURFACE, TCC_CONFIGURATION, carregar,
                                    eixos, estado_snr, num, perda, salvar)
import figuras_analise_grupos as fag
from mapa_grupos_v4 import LETRAS_NOVAS

LETRAS_TODAS = {**LETRAS, **LETRAS_NOVAS}

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


def painel(ax, fontes, fmt, rot, rotulo, grade=GRADE, xlim=(-10, 10), cores=None,
           zf_fraco=None):
    """Faixa (mínimo a máximo entre as fontes) e mediana de cada curva. fontes: lista de
    {curva: SER}, uma por par (painel de configuração) ou por configuração (painel de
    cenário); rotulo: as primeiras colunas do CSV. cores: (LMMSE, BCD-MMSE), padrão os
    de sempre. zf_fraco: cor do ZF desenhado como fundo, atrás das outras curvas."""
    cor_l, cor_b = cores or (COR_LMMSE, COR_BCD)
    eixos(ax, grade_x=True, grade_y=True)
    ax.set_yscale("log")
    ax.set_ylim(PISO, 1)
    ax.set_xlim(*xlim)
    linhas = []
    curvas = [("LMMSE", "LMMSE", cor_l)]
    if zf_fraco:
        m = np.array([np.maximum(f["ZF"], PISO) for f in fontes])
        ax.fill_between(grade, m.min(0), m.max(0), color=zf_fraco, alpha=0.35, lw=0,
                        zorder=0.5)
        ax.plot(grade, np.median(m, 0), color=zf_fraco, lw=1.2, zorder=0.6)
    else:
        curvas.append(("ZF", "ZF", COR_ZF))
    for chave, nome, cor in (*curvas, (fmt, f"BCD-MMSE (iter 1), {rot}", cor_b)):
        m = np.array([np.maximum(f[chave], PISO) for f in fontes])
        lo, mid, hi = m.min(0), np.median(m, 0), m.max(0)
        if cor == cor_b:
            ax.fill_between(grade, lo, hi, facecolor="none", edgecolor=cor, hatch="////",
                            lw=0, zorder=2.5)
        else:
            ax.fill_between(grade, lo, hi, color=cor, alpha=0.18, lw=0, zorder=2)
        for borda in (lo, hi):
            ax.plot(grade, borda, color=cor, lw=0.6, alpha=0.8, zorder=2.6)
        ax.plot(grade, mid, color=cor, lw=1.6, zorder=3)
        linhas += [[*rotulo, nome, est, *v] for est, v in
                   (("minimo", lo), ("mediana", mid), ("maximo", hi))]
    ref = np.median([np.maximum(f["BCD"], PISO) for f in fontes], 0)
    ax.plot(grade, ref, color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)), zorder=4)
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


def eixo_snr(ax, xlim=(-10, 10), passo=None, sem_ultimo=False):
    """Eixo de SNR com marcas e números a cada 2,5 dB em todos os painéis."""
    # a cada 5 dB no eixo do QPSK com M = 256 (de -20 a 0): números longos não cabem a cada 2,5
    passo = passo or (5 if xlim[0] < -10 else 2.5)
    marcas = np.arange(xlim[0], xlim[1] + 0.1, passo)
    rotulos = [f"{v:g}".replace("-", "−") for v in marcas]
    if sem_ultimo:   # painéis próximos: o último número encostaria no primeiro do vizinho
        rotulos[-1] = ""
    ax.set_xticks(marcas, rotulos)
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


# Curvas do TCC (--comparar-formatos): em cada grupo e modulação, os formatos escolhidos do
# grupo (Tabela tab:formatos-escolhidos) nas colunas e duas condições nas linhas (critérios
# da autora em "Análise bits.md", Highlights): a de maior aumento de SNR no primeiro formato
# escolhido (o pior caso, como no mapa) e a TDLB100-400 (N = 24), a de maior diferença entre
# as curvas das configurações. Se o pior caso já é a TDLB100-400, a primeira linha é o
# segundo pior. O QPSK dos grupos 2 e 3 (17 a 24) vem da rodada modo_fixo_3dB_qpsk_256, na
# grade de -20 a 10 dB da referência curvas_qpsk_256 (mesma semente).
# 2026-11-09: sem o critério "atinge SER = 10^-2"; grupo 1 com 0,1 dB no <26,12> (grade inteira)
FMTS_GRUPO = {"G1": ((12, 12), (12, 14)),
              "G2": ((14, 14), (14, 16)),
              "G3": ((12, 12), (14, 16))}
QPSK_256 = {"G2": (17, 18, 19, 20), "G3": (21, 22, 23, 24)}
# Formato escolhido só com IoTh de 10 dB (configurações A a D): coluna a mais, à esquerda,
# com a faixa só dessas configurações. <18,8> fora da [5]: grade inteira da rodada
# modo_fixo_3dB_iot10 quando existir; senão a grade curta da [4] v4 (NaN fora dela)
FMT_IOT10 = {"G1": (8, 10), "G2": (12, 10), "G3": (12, 10)}
FORMATOS = {**FORMATOS, (8, 10): ("<18,8>", "AP_RND_ZERO_AP_WRAP", "18-8")}
IOT10 = PASTA.parent / "modo_fixo_3dB_iot10" / "dados"
V4_DADOS = PASTA.parents[1] / "4_varredura_formatos" / "v4_formatos_juntos_16_configs" / "dados"


def iot_db(k):
    from dbp_sim.params import QPSK_256_PANELS
    return {TCC_CONFIGURATION[p.label]: p for p in ALL_PANELS + QPSK_256_PANELS}[k].iot_db


def completar_18_8(ser):
    """Põe o <18,8> em ser (configurações 1 a 8), da grade inteira ou da v4."""
    import json
    nome = "8_10_AP_RND_ZERO_AP_WRAP.json"
    for c in CENARIOS:
        for k in range(1, 9):
            arq = IOT10 / c / f"configuracao_{k}" / nome
            if arq.exists():
                ser[(c, k)][(8, 10)] = json.loads(arq.read_text())["ser"][BCD1]
                continue
            j = json.loads((V4_DADOS / c / f"configuracao_{k}" / nome).read_text())
            pos = {x: i for i, x in enumerate(GRADE)}
            v = np.full(len(GRADE), np.nan)
            for x, y in zip(j["snr_db"], j["ser"][BCD1]):
                v[pos[x]] = y
            ser[(c, k)][(8, 10)] = v
GRADE_QPSK_256 = tuple(range(-20, 11, 2))
DADOS_QPSK_256 = PASTA.parent / "modo_fixo_3dB_qpsk_256" / "dados"
REF_QPSK_256 = PASTA.parents[1] / "1_referencia_float" / "curvas_qpsk_256"
EXTREMO = "TDLB100-400"
BCD1 = "BCD-MMSE (iter 1)"


V5_QPSK = (PASTA.parents[1] / "4_varredura_formatos" / "v5_qpsk_grupos_2_3" / "dados")


REF_QPSK_128 = PASTA.parents[1] / "1_referencia_float" / "curvas_qpsk_128"
DADOS_QPSK_128 = PASTA.parent / "modo_fixo_3dB_qpsk_128" / "dados"
QPSK_128 = (5, 6, 7, 8)
MAPA = PASTA.parent / "modo_fixo_mapa" / "dados"


def carregar_qpsk_256(fonte="inteira", ks=None, ref_dir=None, dados=None):
    """{(cenário, config): {curva: SER}} das configurações 17 a 24, como carregar(). Com
    fonte="v5", o ponto fixo vem da [4] v5 (grade curta em volta de 10^-2, a mesma do mapa),
    posto na grade inteira com NaN fora das SNRs simuladas (a curva só aparece nelas)."""
    import json
    ser = {}
    for c in CENARIOS:
        pasta = next(p for p in (ref_dir or REF_QPSK_256).iterdir()
                     if c in p.name.split("_")[0].split("+"))
        ref = json.loads((pasta / "bcd_iterations_results.json").read_text())
        assert tuple(ref["snr_db"]) == GRADE_QPSK_256
        rotulo = {TCC_CONFIGURATION[p.label]: p.label for p in ALL_PANELS}
        for k in ks or (*QPSK_256["G2"], *QPSK_256["G3"]):
            r = ref[rotulo.get(k, str(k))]
            d = {"LMMSE": r["LMMSE"], "ZF": r["ZF"], "BCD": r[BCD1]}
            for (I, F), (_, modo, _) in FORMATOS.items():
                pasta_f = V5_QPSK if fonte == "v5" else (dados or DADOS_QPSK_256)
                arq = pasta_f / c / f"configuracao_{k}" / f"{I}_{F}_{modo}.json"
                if not arq.exists() and fonte != "v5":
                    # formatos que só a rodada 6 (modo_fixo_mapa) tem na grade inteira, como
                    # o <26,12> do grupo 1 com QPSK (formato escolhido desde 2026-11-09)
                    arq = MAPA / c / f"configuracao_{k}" / f"{I}_{F}_{modo}.json"
                if not arq.exists():
                    continue
                j = json.loads(arq.read_text())
                if fonte == "v5":
                    pos = {x: i for i, x in enumerate(GRADE_QPSK_256)}
                    v = np.full(len(GRADE_QPSK_256), np.nan)
                    for x, y in zip(j["snr_db"], j["ser"][BCD1]):
                        v[pos[x]] = y
                    d[(I, F)] = v
                else:
                    assert tuple(j["snr_db"]) == GRADE_QPSK_256, arq
                    d[(I, F)] = j["ser"][BCD1]
            ser[(c, k)] = d
    return ser


def condicoes_curvas(ser, ks, fmt, grade):
    """(pior caso do formato entre as configurações ks, TDLB100-400)."""
    from figuras_formatos import snr_no_alvo

    def pior(c):
        vs = []
        for k in ks:
            xb = snr_no_alvo(grade, ser[(c, k)]["BCD"])
            xf = snr_no_alvo(grade, ser[(c, k)][fmt])
            vs.append(np.inf if xf is None or xb is None else max(0.0, xf - xb))
        return max(vs)
    ordem = sorted(CENARIOS, key=pior, reverse=True)
    primeira = next(c for c in ordem if c != EXTREMO)
    return primeira, EXTREMO


TCC = Path(__file__).resolve().parents[2] / "TG2_-__ECP_UFRGS" / "Images" / "RESULTADOS"


def figura_formatos(ser, estacao, mod, ks, fmts, grade=GRADE, xlim=(-10, 10), tcc=False,
                    fmt_iot10=None):
    """Uma linha por condição (condicoes_curvas) e uma coluna por formato; faixas entre as
    configurações ks, como em --por cenario. Com tcc, sem o título (ele vai na legenda
    da figura no TCC) e só o PDF em TCC/Images/RESULTADOS/curvas_ser_<grupo>_<mod>.pdf."""
    g, M, C, _ = next(e for e in ESTACOES if e[0] == estacao)
    cenarios = condicoes_curvas(ser, ks, fmts[0], grade)
    k10 = tuple(k for k in ks if iot_db(k) == 10)
    if fmt_iot10:
        fmts = (fmt_iot10, *fmts)
    nlin, ncol = len(cenarios), len(fmts)
    altura = 1.25 + 1.85 * nlin
    fig, axs = plt.subplots(nlin, ncol, figsize=(LARGURA, altura), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    linhas = []
    for i, c in enumerate(cenarios):
        for j, fmt in enumerate(fmts):
            ax = axs[i][j]
            rot = FORMATOS[fmt][0]
            kk = k10 if (fmt_iot10 and j == 0) else ks
            linhas += painel(ax, [ser[(c, k)] for k in kk], fmt, rot, [c, rot], grade, xlim)
            eixo_snr(ax, xlim, 5 if ncol >= 4 else None,   # 4 colunas: a cada 5 dB
                     sem_ultimo=j < ncol - 1)
            if i == 0:
                cabecalho(ax, rot, fag.MODO[FORMATOS[fmt][1]])
                if fmt_iot10 and j == 0:
                    ax.annotate(f"IoTh 10 dB only ({', '.join(LETRAS_TODAS[k] for k in k10)})",
                                (0.5, 1), xycoords="axes fraction", xytext=(0, 26),
                                textcoords="offset points", ha="center", va="bottom",
                                fontsize=6.5, color=INK_SECONDARY)
            if j > 0:
                ax.tick_params(labelleft=False)
            if j == 0:
                # condição numa linha só (sobra largura para os painéis)
                nome, det = CENARIOS_EN[c].split(": ")
                nome = nome.replace(" and TDLA30-10", "/-10")
                ax.set_ylabel(f"{nome}, {det}\nSER", color=INK_SECONDARY, fontsize=7)
            if i == nlin - 1:
                ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    nome_mod = MODULATION_LABEL.get(mod, mod)
    if not tcc:
        fig.suptitle(f"{nome_mod}: $M$ = {M}, $C$ = {C}, $M_c$ = {M // C}   |   "
                     f"configurations {', '.join(sorted(LETRAS_TODAS[k] for k in ks))}",
                     fontsize=9, color=INK_PRIMARY, y=0.995)
    # ncol=2: as três faixas (LMMSE, ZF, BCD-MMSE) ficam uma abaixo da outra na 1a coluna
    handles = [faixa_legenda(COR_LMMSE, "LMMSE in float"), faixa_legenda(COR_ZF, "ZF in float"),
               faixa_legenda(COR_BCD, "BCD-MMSE (iter 1) in fixed point"),
               Line2D([], [], color=INK_SECONDARY, lw=1.6,
                      label="median over the configurations"),
               Line2D([], [], color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)),
                      label="BCD-MMSE (iter 1) in float (median)")]
    titulo_leg = "Range: lowest to highest SER over the configurations of each panel"
    if not tcc:
        fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=7,
                   labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, 0.0), title=titulo_leg,
                   title_fontsize=7)
    # colunas próximas: deixa os painéis largos o bastante para os números do eixo x
    fig.subplots_adjust(left=0.085, right=0.99, top=1 - (0.35 if tcc else 0.6) / altura,
                        bottom=(1.2 if tcc else 0.95) / altura, hspace=0.25, wspace=0.08)
    if tcc:   # no TCC, a legenda num quadro alinhado à direita, como nas outras figuras
        legenda_quadro(fig, axs[-1][-1], handles, ncol=2, fontsize=7, title=titulo_leg,
                       title_fontsize=7)
    sufixo = f"_{mod.lower()}"
    print(g, mod, "condições:", cenarios)
    if tcc:
        TCC.mkdir(parents=True, exist_ok=True)
        fig.savefig(TCC / f"curvas_ser_{g}{sufixo}.pdf", facecolor=SURFACE, bbox_inches="tight")
        fig.savefig(PASTA / "figuras" / "perfil_estacao" / f"tcc_curvas_ser_{g}{sufixo}.png",
                    facecolor=SURFACE, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(TCC / f"curvas_ser_{g}{sufixo}.pdf")
        return
    fag.SAIDA = PASTA / "figuras" / "perfil_estacao"
    salvar(fig, f"comparacao_formatos_{g}{sufixo}", linhas,
           ["par", "formato", "curva", "estatistica", *[f"{x:g}" for x in grade]])


# Figuras de curvas de SER por grupo (2026-11-10, pedido da autora), um par por grupo. As
# figuras de figura_formatos, com todos os formatos, ficam no apêndice.
# - curvas_ser_<g>_ioth10: o formato escolhido só com IoTh de 10 dB (FMT_IOT10), com essas
#   configurações; 16-QAM e QPSK lado a lado, cada coluna com as condições da sua modulação.
# - curvas_ser_<g>_ioth20: o formato do limite de 3 dB com todas as configurações, só com as
#   de IoTh de 20 dB (as que definem esse formato); uma condição por linha, 16-QAM e QPSK no
#   mesmo painel (as curvas ficam afastadas). O QPSK em tons mais escuros, e o ZF como fundo.
# Cada figura tem uma IoTh só: misturar as duas alarga as faixas (até 4 dB no grupo 1).
EIXO = (-20, 10)   # mesmo eixo de SNR nas duas modulações e nos três grupos
CORES_MOD = {"16QAM": (COR_LMMSE, COR_BCD, "#d9d8d4"),   # (LMMSE, BCD-MMSE, ZF de fundo)
             "QPSK": ("#8f1414", "#a86a00", "#a3a29c")}
# linha do ZF quando a figura só tem uma IoTh, por cor de fundo do ZF
ZF_LINHA = {"#d9d8d4": "#b3b2ac", "#a3a29c": "#7d7c76"}
QUEBRA_LEG = {"BCD-MMSE (iter 1) in fixed point": "BCD-MMSE (iter 1)\nin fixed point",
              "median over the configurations": "median over the\nconfigurations",
              "BCD-MMSE (iter 1) in float (median)": "BCD-MMSE (iter 1)\nin float (median)"}


def legenda_lado(fig, axs, handles, titulo_extra=""):
    """Quadro estreito ao lado dos painéis, itens empilhados, base na base dos painéis."""
    titulo = "Range: lowest to\nhighest SER over\nthe configurations\nof each panel" + titulo_extra
    fig.legend(handles=handles, labels=[QUEBRA_LEG.get(h.get_label(), h.get_label())
                                        for h in handles],
               loc="lower left", ncol=1, fontsize=7, title=titulo, title_fontsize=7,
               bbox_to_anchor=(axs[0][-1].get_position().x1 + 0.025,
                               axs[-1][-1].get_position().y0),
               frameon=True, facecolor=SURFACE, edgecolor=INK_MUTED, framealpha=1,
               fancybox=False, labelcolor=INK_SECONDARY, alignment="left", borderpad=0.6)


def rotulo_condicao(ax, c):
    nome, det = CENARIOS_EN[c].split(": ")
    ax.set_ylabel(f"{nome.replace(' and TDLA30-10', '/-10')}, {det}\nSER",
                  color=INK_SECONDARY, fontsize=7)


def handles_curvas(zf_fraco=False):
    zf = (Patch(facecolor=CORES_MOD["16QAM"][2], alpha=0.6, edgecolor=CORES_MOD["16QAM"][2],
                label="ZF in float") if zf_fraco else faixa_legenda(COR_ZF, "ZF in float"))
    return [faixa_legenda(COR_LMMSE, "LMMSE in float"), zf,
            faixa_legenda(COR_BCD, "BCD-MMSE (iter 1) in fixed point"),
            Line2D([], [], color=INK_SECONDARY, lw=1.6, label="median over the configurations"),
            Line2D([], [], color=INK_PRIMARY, lw=0.8, ls=(0, (3, 2)),
                   label="BCD-MMSE (iter 1) in float (median)")]


def salvar_tcc(fig, nome):
    pasta = TCC / "curvas_ser"   # figuras novas de 2026-11-10 numa pasta própria
    pasta.mkdir(parents=True, exist_ok=True)
    fig.savefig(pasta / f"{nome}.pdf", facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(PASTA / "figuras" / "perfil_estacao" / f"tcc_{nome}.png", facecolor=SURFACE,
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(pasta / f"{nome}.pdf")


def figuras_grupo_tese(g, fontes):
    """Par de figuras do grupo g. fontes: {modulação: (ser, grade, configurações)}."""
    fmt10, fmt20 = FMT_IOT10[g], FMTS_GRUPO[g][0]
    # condições escolhidas com todas as configurações e o formato de 3 dB, como no apêndice
    cond = {m: condicoes_curvas(d, ks, fmt20, gr) for m, (d, gr, ks) in fontes.items()}
    figura_ioth10(g, fontes, cond, fmt10)
    figura_ioth20(g, fontes, cond, fmt20)


def figura_ioth10(g, fontes, cond, fmt):
    """IoTh de 10 dB: 16-QAM e QPSK lado a lado, duas condições por coluna."""
    altura = 0.6 + 1.85 * 2
    fig, axs = plt.subplots(2, 2, figsize=(LARGURA, altura), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for j, (mod, (d, gr, ks)) in enumerate(fontes.items()):
        k10 = tuple(k for k in ks if iot_db(k) == 10)
        for i, c in enumerate(cond[mod]):
            ax = axs[i][j]
            painel(ax, [d[(c, k)] for k in k10], fmt, FORMATOS[fmt][0], [c], gr, EIXO)
            eixo_snr(ax, EIXO, sem_ultimo=j == 0)
            # a condição em cima de cada painel (as colunas têm condições diferentes)
            ax.set_title(CENARIOS_EN[c].replace(": ", ", ").replace(" and TDLA30-10", "/-10"),
                         fontsize=7, color=INK_SECONDARY, pad=4)
            if j == 0:
                ax.set_ylabel("SER", color=INK_SECONDARY, fontsize=7)
            else:
                ax.tick_params(labelleft=False)
            if i == 0:
                ax.annotate(f"{MODULATION_LABEL.get(mod, mod)} "
                            f"({', '.join(LETRAS_TODAS[k] for k in k10)})",
                            (0.5, 1), xycoords="axes fraction", xytext=(0, 16),
                            textcoords="offset points", ha="center", va="bottom",
                            fontsize=8.5, color=INK_PRIMARY)
            if i == 1:
                ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    fig.subplots_adjust(left=0.085, right=0.76, top=1 - 0.45 / altura, bottom=0.45 / altura,
                        hspace=0.38, wspace=0.08)
    legenda_lado(fig, axs, handles_curvas())
    salvar_tcc(fig, f"curvas_ser_{g}_ioth10")


def figura_ioth20(g, fontes, cond, fmt):
    """IoTh de 20 dB: 16-QAM e QPSK no mesmo painel, uma condição por linha."""
    # primeiras linhas das duas modulações e, por último, a TDLB100-400 (a mais exigente)
    conds = [*dict.fromkeys(cond[m][0] for m in fontes), EXTREMO]
    altura = 0.5 + 1.75 * len(conds)
    fig, axs_ = plt.subplots(len(conds), 1, figsize=(LARGURA, altura), squeeze=False)
    axs = [[a] for a in axs_[:, 0]]
    fig.patch.set_facecolor(SURFACE)
    k20 = {m: tuple(k for k in ks if iot_db(k) == 20) for m, (_, _, ks) in fontes.items()}
    for i, c in enumerate(conds):
        ax = axs[i][0]
        for mod, (d, gr, _) in fontes.items():
            cl, cb, cz = CORES_MOD[mod]
            painel(ax, [d[(c, k)] for k in k20[mod]], fmt, FORMATOS[fmt][0], [c], gr, EIXO,
                   cores=(cl, cb), zf_fraco=cz)
        for x, t in ((-17.5, "QPSK"), (8, "16-QAM")):
            ax.annotate(t, (x, 2e-4), fontsize=7, color=INK_PRIMARY, ha="center")
        eixo_snr(ax, EIXO, passo=2.5)
        rotulo_condicao(ax, c)
        if i == len(conds) - 1:
            ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    fig.subplots_adjust(left=0.085, right=0.76, top=1 - 0.35 / altura, bottom=0.45 / altura,
                        hspace=0.3)
    todas = [LETRAS_TODAS[k] for m in fontes for k in k20[m]]
    axs[0][0].set_title(f"IoTh 20 dB only ({', '.join(todas)})", fontsize=7,
                        color=INK_SECONDARY, pad=4)
    legenda_lado(fig, axs, handles_curvas(zf_fraco=True), "\n\nDarker colors: QPSK")
    salvar_tcc(fig, f"curvas_ser_{g}_ioth20")


def figuras_todos_grupos(fontes, c=EXTREMO):
    """Duas figuras com os três grupos na mesma condição c, um grupo por linha (2026-11-10):
    curvas_ser_grupos_ioth10 (formato FMT_IOT10 de cada grupo, 16-QAM e QPSK lado a lado) e
    curvas_ser_grupos_ioth20 (formato de 3 dB de cada grupo, 16-QAM e QPSK no mesmo painel)."""
    grupos = list(fontes)
    nome_c = CENARIOS_EN[c].replace(": ", ", ").replace(" and TDLA30-10", "/-10")

    # IoTh de 10 dB: uma linha por grupo, 16-QAM e QPSK lado a lado
    altura = 0.75 + 1.85 * len(grupos)
    fig, axs = plt.subplots(len(grupos), 2, figsize=(LARGURA, altura), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for i, g in enumerate(grupos):
        fmt = FMT_IOT10[g]
        for j, (mod, (d, gr, ks)) in enumerate(fontes[g].items()):
            ax = axs[i][j]
            k10 = tuple(k for k in ks if iot_db(k) == 10)
            painel(ax, [d[(c, k)] for k in k10], fmt, FORMATOS[fmt][0], [c], gr, EIXO)
            eixo_snr(ax, EIXO, sem_ultimo=j == 0)
            # título curto: os dois painéis da linha dividem a largura
            ax.set_title(f"Group {g[1:]}, {FORMATOS[fmt][0]}: "
                         f"{', '.join(LETRAS_TODAS[k] for k in k10)}",
                         fontsize=7, color=INK_SECONDARY, pad=4, loc="left")
            if j == 0:
                ax.set_ylabel("SER", color=INK_SECONDARY, fontsize=7)
            else:
                ax.tick_params(labelleft=False)
            if i == 0:
                ax.annotate(MODULATION_LABEL.get(mod, mod), (0.5, 1), xycoords="axes fraction",
                            xytext=(0, 16), textcoords="offset points", ha="center",
                            va="bottom", fontsize=8.5, color=INK_PRIMARY)
            if i == len(grupos) - 1:
                ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    fig.subplots_adjust(left=0.085, right=0.76, top=1 - 0.6 / altura, bottom=0.45 / altura,
                        hspace=0.38, wspace=0.08)
    fig.suptitle(f"IoTh 10 dB only, {nome_c}", fontsize=7, color=INK_SECONDARY,
                 x=(axs[0][0].get_position().x0 + axs[0][-1].get_position().x1) / 2,
                 y=1 - 0.08 / altura)
    legenda_lado(fig, axs, handles_curvas())
    salvar_tcc(fig, "curvas_ser_grupos_ioth10")

    # IoTh de 20 dB e, como variante, de 10 dB: um painel por grupo, 16-QAM e QPSK juntos
    figura_grupos_mesclada(fontes, c, 20, {g: FMTS_GRUPO[g][0] for g in grupos},
                           "curvas_ser_grupos_ioth20")
    figura_grupos_mesclada(fontes, c, 10, FMT_IOT10, "curvas_ser_grupos_ioth10_mesclada")
    # limite de 0,1 dB (2026-11-10): <24,12> nos três grupos só com IoTh de 10 dB, e o formato
    # de 0,1 dB com todas as configurações (FMTS_GRUPO[g][1]) com as de IoTh de 20 dB
    figura_grupos_mesclada(fontes, c, 10, {g: (12, 12) for g in grupos},
                           "curvas_ser_grupos_ioth10_01db")
    figura_grupos_mesclada(fontes, c, 20, {g: FMTS_GRUPO[g][1] for g in grupos},
                           "curvas_ser_grupos_ioth20_01db")
    # as duas IoTh lado a lado, uma figura por limite (3 dB e 0,1 dB)
    figura_grupos_2col(fontes, c, FMT_IOT10, {g: FMTS_GRUPO[g][0] for g in grupos},
                       "curvas_ser_grupos_3db")
    figura_grupos_2col(fontes, c, {g: (12, 12) for g in grupos},
                       {g: FMTS_GRUPO[g][1] for g in grupos}, "curvas_ser_grupos_01db")
    figura_grupos_range(fontes, c)
    # formatos escolhidos só com as configurações de IoTh de 10 dB (Tabela tab:formatos-escolhidos)
    figura_grupos_range(fontes, c, "curvas_ser_grupos_range_ioth10", [
        ("Up to 3 dB, IoTh 10 dB only", FMT_IOT10, (10,), True),
        ("Up to 0.1 dB, IoTh 10 dB only", {g: (12, 12) for g in grupos}, (10,), True)])


def figura_grupos_mesclada(fontes, c, iot, fmts, nome):
    """Um painel por grupo na condição c, só com as configurações de IoTh iot, cada grupo no
    seu formato fmts[g]; 16-QAM e QPSK no mesmo painel, QPSK mais escuro, ZF como fundo."""
    grupos = list(fontes)
    nome_c = CENARIOS_EN[c].replace(": ", ", ").replace(" and TDLA30-10", "/-10")
    altura = 0.5 + 1.75 * len(grupos)
    fig, axs_ = plt.subplots(len(grupos), 1, figsize=(LARGURA, altura), squeeze=False)
    axs = [[a] for a in axs_[:, 0]]
    fig.patch.set_facecolor(SURFACE)
    for i, g in enumerate(grupos):
        ax = axs[i][0]
        fmt = fmts[g]
        kk = {m: tuple(k for k in ks if iot_db(k) == iot) for m, (_, _, ks) in fontes[g].items()}
        for mod, (d, gr, _) in fontes[g].items():
            cl, cb, cz = CORES_MOD[mod]
            painel(ax, [d[(c, k)] for k in kk[mod]], fmt, FORMATOS[fmt][0], [c], gr, EIXO,
                   cores=(cl, cb), zf_fraco=cz)
        for x, t in ((-17.5, "QPSK"), (8, "16-QAM")):
            ax.annotate(t, (x, 2e-4), fontsize=7, color=INK_PRIMARY, ha="center")
        eixo_snr(ax, EIXO, passo=2.5)
        ax.set_ylabel("SER", color=INK_SECONDARY, fontsize=7)
        M, C = next((e[1], e[2]) for e in ESTACOES if e[0] == g)
        ax.set_title(f"Group {g[1:]} ($M$ = {M}, $C$ = {C}), {FORMATOS[fmt][0]}: "
                     f"{', '.join(LETRAS_TODAS[k] for m in kk for k in kk[m])}", fontsize=7,
                     color=INK_SECONDARY, pad=4, loc="left")
        if i == len(grupos) - 1:
            ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    fig.subplots_adjust(left=0.085, right=0.76, top=1 - 0.4 / altura, bottom=0.45 / altura,
                        hspace=0.4)
    fig.suptitle(f"IoTh {iot:g} dB only, {nome_c}", fontsize=7, color=INK_SECONDARY,
                 x=(axs[0][0].get_position().x0 + axs[0][0].get_position().x1) / 2,
                 y=1 - 0.08 / altura)
    legenda_lado(fig, axs, handles_curvas(zf_fraco=True), "\n\nDarker colors: QPSK")
    salvar_tcc(fig, nome)


def figura_grupos_2col(fontes, c, fmts10, fmts20, nome):
    """Três grupos na condição c (2026-11-10): uma linha por grupo, IoTh de 10 dB na 1a
    coluna (formato fmts10[g]) e de 20 dB na 2a (fmts20[g]); 16-QAM e QPSK no mesmo painel,
    QPSK mais escuro, ZF como fundo. Junta as figuras de figura_grupos_mesclada."""
    grupos = list(fontes)
    nome_c = CENARIOS_EN[c].replace(": ", ", ").replace(" and TDLA30-10", "/-10")
    # linhas mais baixas: os painéis ficam mais largos em proporção (a largura é a do texto)
    altura = 1.35 + 1.55 * len(grupos)   # sobra embaixo para a legenda
    fig, axs = plt.subplots(len(grupos), 2, figsize=(LARGURA, altura), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for i, g in enumerate(grupos):
        for j, (iot, fmts) in enumerate(((10, fmts10), (20, fmts20))):
            ax = axs[i][j]
            fmt = fmts[g]
            for mod, (d, gr, ks) in fontes[g].items():
                cl, cb, cz = CORES_MOD[mod]
                kk = tuple(k for k in ks if iot_db(k) == iot)
                painel(ax, [d[(c, k)] for k in kk], fmt, FORMATOS[fmt][0], [c], gr, EIXO,
                       cores=(cl, cb), zf_fraco=cz)
            for x, t in ((-17, "QPSK"), (8, "16-QAM")):
                ax.annotate(t, (x, 2e-4), fontsize=6.5, color=INK_PRIMARY, ha="center")
            eixo_snr(ax, EIXO, passo=5)   # o 10 aparece nas duas colunas
            ax.set_title(f"Group {g[1:]}, {FORMATOS[fmt][0]}", fontsize=7,
                         color=INK_SECONDARY, pad=4, loc="left")
            if j == 0:
                ax.set_ylabel("SER", color=INK_SECONDARY, fontsize=7)
            else:
                ax.tick_params(labelleft=False)
            if i == 0:
                letras = "A to D" if iot == 10 else "E to H"
                ax.annotate(f"IoTh {iot} dB ({letras})", (0.5, 1), xycoords="axes fraction",
                            xytext=(0, 16), textcoords="offset points", ha="center",
                            va="bottom", fontsize=8.5, color=INK_PRIMARY)
            if i == len(grupos) - 1:
                ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    # painéis na largura toda; a legenda vai embaixo, num quadro alinhado à direita
    fig.subplots_adjust(left=0.07, right=0.99, top=1 - 0.6 / altura, bottom=1.05 / altura,
                        hspace=0.5, wspace=0.1)
    fig.suptitle(nome_c, fontsize=7, color=INK_SECONDARY,
                 x=(axs[0][0].get_position().x0 + axs[0][-1].get_position().x1) / 2,
                 y=1 - 0.08 / altura)
    legenda_quadro(fig, axs[-1][-1], handles_curvas(zf_fraco=True), ncol=3, fontsize=7,
                   title="Range: lowest to highest SER over the configurations of each panel."
                         "  Darker colors: QPSK", title_fontsize=7)
    salvar_tcc(fig, nome)


ESTILO_IOTH = {10: {}, 20: {"marker": "^", "ms": 3.2}}
PONTILHADO = (0, (1, 1.3))
# faixa do ZF nas figuras de range, sem transparência: (fundo, borda) pela cor do ZF da modulação
ZF_QAM, ZF_QPSK = "#d9d8d4", "#a3a29c"
# o do QPSK é o mais claro: a faixa dele passa por trás das curvas do 16-QAM
ZF_FAIXA = {ZF_QAM: ("#d3d2cc", "#7d7c76"), ZF_QPSK: ("#e7e6e1", "#9a9993")}   # ponto flutuante: pontos mais grossos e juntos, para aparecer   # 20 dB: linha com triângulos


def painel_range(ax, fontes_mod, fmt, c, cores, iots=(10, 20), zf=True):
    """Faixa do menor ao maior SER entre todas as configurações da modulação (as duas IoTh) e,
    no lugar da mediana, uma linha por IoTh: a média do SER entre as configurações dessa IoTh
    (que só diferem em K). IoTh 10 dB em linha cheia e 20 dB em linha cheia com triângulos
    (o tracejado ficava difícil de ler); o BCD-MMSE em ponto flutuante em pontilhado fino.
    As faixas do LMMSE e do BCD-MMSE em ponto fixo são preenchidas de leve (a hachura
    atrapalhava). fontes_mod: (ser, grade, configurações). iots: as IoTh
    desenhadas (as configurações das outras ficam fora da faixa também). zf=False: sem o ZF."""
    d, gr, ks = fontes_mod
    ks = [k for k in ks if iot_db(k) in iots]
    cl, cb, cz = cores
    estilo = {i: e for i, e in ESTILO_IOTH.items() if i in iots}
    for chave, cor in ((("ZF", cz),) if zf else ()) + (("LMMSE", cl), (fmt, cb)):
        m = np.array([np.maximum(d[(c, k)][chave], PISO) for k in ks])
        lo, hi = m.min(0), m.max(0)
        if chave == "ZF":   # fundo, atrás das outras curvas
            # opaco (com transparência, a sobreposição virava outro cinza), um cinza por
            # modulação e com borda, para as duas faixas ficarem separadas
            fundo, borda = ZF_FAIXA[cz]
            ax.fill_between(gr, lo, hi, color=fundo, lw=0, zorder=0.4 if cz == ZF_QPSK else 0.5)
            for v in (lo, hi):
                ax.plot(gr, v, color=borda, lw=0.6, zorder=0.7)
            if len(iots) == 1:
                # com uma IoTh só, a faixa do ZF é estreita e some: linha num cinza um pouco
                # mais escuro que a faixa (com as duas IoTh, a faixa larga já aparece)
                ax.plot(gr, m.mean(0), color=ZF_LINHA[cz], lw=1.1, zorder=0.6)
            continue
        # faixas preenchidas de leve: vermelho no LMMSE (a autora quer a faixa dele pintada,
        # 2026-11-11) e amarelo no BCD-MMSE em ponto fixo
        ax.fill_between(gr, lo, hi, color=cor, alpha=0.15 if chave == "LMMSE" else 0.22, lw=0,
                        zorder=2)
        for iot, kw in estilo.items():
            ki = [k for k in ks if iot_db(k) == iot]
            ax.plot(gr, np.mean([np.maximum(d[(c, k)][chave], PISO) for k in ki], 0),
                    color=cor, lw=1.3, zorder=3, **kw)
    for iot in estilo:
        ki = [k for k in ks if iot_db(k) == iot]
        ax.plot(gr, np.mean([np.maximum(d[(c, k)]["BCD"], PISO) for k in ki], 0),
                color=INK_PRIMARY, lw=1.1, ls=PONTILHADO, zorder=4)


def _mistura(c1, c2, t):
    """Cor entre c1 (t = 0) e c2 (t = 1)."""
    r1, r2 = matplotlib.colors.to_rgb(c1), matplotlib.colors.to_rgb(c2)
    return matplotlib.colors.to_hex([x + t * (y - x) for x, y in zip(r1, r2)])


# Figuras de faixas: QPSK mais escuro que o 16-QAM (2026-11-12, pedido da autora: 60% do
# caminho até as cores escuras de CORES_MOD; com as escuras inteiras o pontilhado preto sumia)
CORES_RANGE = {"16QAM": CORES_MOD["16QAM"][:2],
               "QPSK": tuple(_mistura(a, b, 0.6) for a, b in
                             zip(CORES_MOD["16QAM"][:2], CORES_MOD["QPSK"][:2]))}


def figura_grupos_range(fontes, c=EXTREMO, nome="curvas_ser_grupos_range", colunas=None,
                        compacta=False, legenda=True):
    """Três grupos na condição c (2026-11-11): uma linha por grupo e uma coluna por item de
    colunas: (cabeçalho, {grupo: formato}, IoTh desenhadas, com ZF). Padrão: formato de 3 dB
    e de 0,1 dB com todas as configurações (as duas IoTh) e, na 3a coluna, o de 3 dB só com
    IoTh de 10 dB, sem o ZF (as linhas dele deixavam o painel confuso). Em cada painel,
    16-QAM e QPSK (painel_range). compacta: mais baixa e sem o título da condição (que vai
    na caption), para duas figuras por página no apêndice; legenda=False tira o quadro."""
    grupos = list(fontes)
    colunas = colunas or [
        ("Up to 3 dB, all configurations", {g: FMTS_GRUPO[g][0] for g in grupos}, (10, 20), True),
        ("Up to 0.1 dB, all configurations", {g: FMTS_GRUPO[g][1] for g in grupos}, (10, 20),
         True),
        ("Up to 3 dB, IoTh 10 dB only", FMT_IOT10, (10,), False)]
    ncol = len(colunas)
    nome_c = CENARIOS_EN[c].replace(": ", ", ").replace(" and TDLA30-10", "/-10")
    if compacta:
        topo, base = 0.4, (1.15 if legenda else 0.4)
        altura = topo + base + 1.0 * len(grupos)
    else:
        topo, base = (0.6 if ncol <= 2 else 0.8), 1.15
        altura = 1.45 + 1.55 * len(grupos)
    fig, axs = plt.subplots(len(grupos), ncol, figsize=(LARGURA, altura), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for i, g in enumerate(grupos):
        for j, (cab, fmts, iots, com_zf) in enumerate(colunas):
            ax = axs[i][j]
            fmt = fmts[g]
            eixos(ax, grade_x=True, grade_y=True)
            ax.set_yscale("log")
            ax.set_ylim(PISO, 1)
            ax.set_xlim(*EIXO)
            ax.axhline(1e-2, color=INK_MUTED, lw=0.6, ls=":", zorder=1)
            for mod, f in fontes[g].items():
                # QPSK em tons mais escuros (CORES_RANGE) e ZF com um cinza por modulação
                painel_range(ax, f, fmt, c, (*CORES_RANGE[mod], CORES_MOD[mod][2]), iots,
                             com_zf)
            for x, t in ((-17, "QPSK"), (7.5, "16-QAM")):
                ax.annotate(t, (x, 2e-4), fontsize=6.5, color=INK_PRIMARY, ha="center")
            eixo_snr(ax, EIXO, passo=5 if ncol <= 2 else 10)
            ax.set_title(f"Group {g[1:]}, {FORMATOS[fmt][0]}", fontsize=7,
                         color=INK_SECONDARY, pad=4, loc="left")
            if j == 0:
                ax.set_ylabel("SER", color=INK_SECONDARY, fontsize=7)
            else:
                ax.tick_params(labelleft=False)
            if i == 0:
                ax.annotate(cab.replace(", ", ",\n") if ncol > 2 else cab, (0.5, 1),
                            xycoords="axes fraction", xytext=(0, 16),
                            textcoords="offset points", ha="center", va="bottom",
                            fontsize=8.5 if ncol <= 2 else 7.5, color=INK_PRIMARY)
            if i == len(grupos) - 1:
                ax.set_xlabel("SNR [dB]", color=INK_SECONDARY)
    fig.subplots_adjust(left=0.07, right=0.99, top=1 - topo / altura, bottom=base / altura,
                        hspace=0.5, wspace=0.1)
    if not compacta:
        fig.suptitle(nome_c, fontsize=7, color=INK_SECONDARY,
                     x=(axs[0][0].get_position().x0 + axs[0][-1].get_position().x1) / 2,
                     y=1 - 0.08 / altura)
    todas = sorted({i for _, _, iots, _ in colunas for i in iots})
    com_zf = any(z for *_, z in colunas)
    handles = [Patch(facecolor=(*matplotlib.colors.to_rgb(COR_LMMSE), 0.15), edgecolor=COR_LMMSE,
                     lw=1.3, label="LMMSE"),
               *([Patch(facecolor=ZF_FAIXA[z][0], edgecolor=ZF_FAIXA[z][1], lw=0.6,
                        label=f"ZF, {m}") for m, z in (("16-QAM", ZF_QAM), ("QPSK", ZF_QPSK))]
                 if com_zf else []),
               Patch(facecolor=(*matplotlib.colors.to_rgb(COR_BCD), 0.22), edgecolor=COR_BCD,
                     lw=1.3, label="BCD-MMSE, fixed point")]
    linhas = [*[Line2D([], [], color=INK_SECONDARY, lw=1.3, label=f"IoTh {i} dB (mean over K)",
                       **ESTILO_IOTH[i]) for i in todas],
              Line2D([], [], color=INK_PRIMARY, lw=1.1, ls=PONTILHADO, label="BCD-MMSE, float")]
    # faixas (retângulos) na 1a linha e linhas na 2a: o matplotlib preenche a legenda por
    # coluna, então intercala faixa e linha de cada coluna
    n = max(len(handles), len(linhas))
    handles = [h for k in range(n) for h in (*handles[k:k + 1], *linhas[k:k + 1])]
    if legenda:
        legenda_quadro(fig, axs[-1][-1], handles, ncol=n, fontsize=7,
                       title="Shaded: lowest to highest SER over the configurations of each "
                             "modulation in the panel.\nLMMSE and ZF in float; "
                             "BCD-MMSE with 1 iteration; QPSK in darker shades",
                       title_fontsize=7)
    salvar_tcc(fig, nome)


def comparar_formatos(ser, tcc):
    paineis = {TCC_CONFIGURATION[p.label]: p for p in ALL_PANELS}
    completar_18_8(ser)
    ser_q = carregar_qpsk_256()
    ser_v5 = carregar_qpsk_256("v5")
    fontes = {}   # {grupo: {modulação: (ser, grade, configurações)}}, para figuras_grupo_tese
    for g, _, _, ks in ESTACOES:
        fmts = FMTS_GRUPO[g]
        fontes[g] = {}
        for mod in ("16QAM", "QPSK"):
            kk = tuple(k for k in ks if paineis[k].modulation == mod)
            if kk and g == "G1" and mod == "QPSK" and (DADOS_QPSK_128.parent / "FIM").exists():
                # QPSK do grupo 1 a partir de -20 dB (rodada5_qpsk_128.sh), como nos grupos 2 e 3
                ser_g1 = carregar_qpsk_256(ks=QPSK_128, ref_dir=REF_QPSK_128,
                                           dados=DADOS_QPSK_128)
                figura_formatos(ser_g1, g, mod, kk, fmts, GRADE_QPSK_256, (-20, 0), tcc=tcc,
                                fmt_iot10=FMT_IOT10[g])
                fontes[g][mod] = (ser_g1, GRADE_QPSK_256, QPSK_128)
            elif kk:
                figura_formatos(ser, g, mod, kk, fmts, tcc=tcc, fmt_iot10=FMT_IOT10[g])
                fontes[g][mod] = (ser, GRADE, kk)
            elif g in QPSK_256:
                kq = QPSK_256[g]
                falta = [(c, k, f) for c in CENARIOS for k in kq
                         for f in (FMT_IOT10[g], *fmts) if f not in ser_q[(c, k)]]
                fonte = ser_q
                if falta:
                    # enquanto a grade inteira não termina, a grade curta da v5
                    print(g, "QPSK: faltam", len(falta), "rodadas da modo_fixo_3dB_qpsk_256;"
                          " usando a v5 (grade curta)")
                    fonte = ser_v5
                # o QPSK com M = 256 cruza 10^-2 perto de -13 dB: eixo próprio
                figura_formatos(fonte, g, mod, kq, fmts, GRADE_QPSK_256, (-20, 0), tcc=tcc,
                                fmt_iot10=FMT_IOT10[g])
                fontes[g][mod] = (fonte, GRADE_QPSK_256, kq)
    if tcc:
        for g, f in fontes.items():
            figuras_grupo_tese(g, f)
        figuras_todos_grupos(fontes)
        # 2026-11-11: a figura de faixas por condição de teste. A TDLC300-100 vai para os
        # Resultados; as outras ficam no apêndice
        # 2026-11-12 (pedido da autora): grupo 3 na 2a linha e grupo 2 na 3a
        ordem = {g: fontes[g] for g in ("G1", "G3", "G2")}
        for c in ("TDLC300-100", "TDLB100-400", "TDLA30-5", "TDLA30-75", "TDLA30-300"):
            # apêndice: duas por página, só a última (TDLB100-400) com legenda
            figura_grupos_range(ordem, c, f"curvas_ser_grupos_range_{ABREV_CENARIO[c]}",
                                compacta=c != "TDLC300-100", legenda=c in ("TDLC300-100", "TDLB100-400"))


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
                    help="uma figura por grupo e modulação, com as condições de "
                         "condicoes_curvas nas linhas e os formatos escolhidos nas colunas")
    ap.add_argument("--tcc", action="store_true",
                    help="com --comparar-formatos: versão do TCC (sem título, fonte Type 42) "
                         "em TCC/Images/RESULTADOS")
    args = ap.parse_args()
    if args.tcc:
        plt.rcParams["pdf.fonttype"] = 42
    ser = carregar()
    if args.comparar_formatos:
        comparar_formatos(ser, args.tcc)
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
