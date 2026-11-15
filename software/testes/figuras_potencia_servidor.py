#!/usr/bin/env python3
"""
Figuras de potência e energia das arquiteturas de inversão (Vivado 2023.2, servidor).

Dados: hardware/resultados_servidor/resultados_vivado_servidor.csv (Alveo U50,
xcu50-fsvh2104-2-e, 100 MHz; potência com SAIF do testbench). Só as arquiteturas otimizadas,
16 x 16; a versão sem otimização não atende o limite de nenhuma condição de teste.

Figuras (pasta hardware/resultados_servidor/figuras):
  potencia_dinamica_formatos   potência dinâmica x formato, uma linha por arquitetura
  potencia_media_condicao      potência média no ritmo exigido (275 inversões a cada T_c),
                               estática + dinâmica, por condição de teste, formato <24,12>
  energia_inversao_formatos    energia por inversão x formato (candidata)
  potencia_recursos_lado       ocupação do FPGA e potência dinâmica, lado a lado (a versão que vai
                               para a tese, junto com energia_inversao_formatos)
  recursos_faixa_arquitetura   uso de cada recurso por arquitetura, do menor ao maior formato
  energia_potencia_recursos    três painéis com o mesmo eixo de formatos: energia por inversão,
                               potência dinâmica (com a faixa dinâmica/estática de cada
                               condição à direita) e ocupação do FPGA (recurso mais usado)

Potência média no ritmo exigido = estática + energia por inversão x 275 / T_c. Supõe que a
dinâmica cai a zero quando o módulo espera o próximo bloco (só a estática fica).

Uso: nice -n 19 ../simulador/.venv/bin/python figuras_potencia_servidor.py
"""

import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib                                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
import numpy as np                                      # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402
from matplotlib.patches import Patch                    # noqa: E402

import figuras_analise_grupos as fag                    # noqa: E402
from figuras_analise_grupos import eixos, legenda_quadro  # noqa: E402
from dbp_sim.plotting import GRID, INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE  # noqa: E402

TABELA = AQUI.parent.parent / "hardware" / "resultados_servidor" / "resultados_vivado_servidor.csv"
fag.SAIDA = TABELA.parent / "figuras"
fag.DPI = 600
LARGURA = 6.3
plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["pdf.fonttype"] = 42

# arquitetura -> (condição de teste, T_c em ms, limite em ciclos)
ARQ = {"9090": ("TDLA30-5", 25.0, 9090), "4545": ("TDLA30-10", 12.5, 4545),
       "606": ("TDLA30-75", 1.6667, 606), "455": ("TDLC300-100", 1.25, 454),
       "152_sistolico": ("TDLA30-300", 0.4167, 151), "114_sistolico": ("TDLB100-400", 0.3125, 113)}
# MANUAL_GRAFICOS.md, seção 5 (cenário): TDLA30-10 marrom #8c5a2e (aprovado em 2026-11-09),
# cheia, com marcador próprio "<" para não depender só da cor (proposta, falta aprovar)
COR = {"TDLA30-5": "#52514e", "TDLA30-10": "#8c5a2e", "TDLA30-75": "#35bcd9",
       "TDLA30-300": "#eb6834", "TDLC300-100": "#4a3aa7", "TDLB100-400": "#d64ad6"}
MARCA = {"TDLA30-5": "o", "TDLA30-10": "<", "TDLA30-75": "s", "TDLA30-300": "D",
         "TDLC300-100": "^", "TDLB100-400": "v"}
VAZADO = set()   # todos cheios (pedido da autora, 2026-11-09)
# versão sem otimização na figura de energia (pedido da autora, 2026-11-15): preto, tracejada
SEM_OPT = {"16 x 16": "Without opt., 16 × 16", "32 x 32": "Without opt., 32 × 32"}
COR.update({SEM_OPT["16 x 16"]: INK_PRIMARY, SEM_OPT["32 x 32"]: INK_PRIMARY})
MARCA.update({SEM_OPT["16 x 16"]: "X", SEM_OPT["32 x 32"]: "P"})
TRACO = {SEM_OPT["16 x 16"]: (0, (3, 2)), SEM_OPT["32 x 32"]: (0, (1, 1.5))}
ORDEM = ["TDLA30-5", "TDLA30-10", "TDLA30-75", "TDLC300-100", "TDLA30-300", "TDLB100-400"]
FORMATOS = [("<18,8>", "AP_RND_ZERO/AP_WRAP"), ("<18,8>", "AP_TRN/AP_SAT"),
            ("<20,8>", "AP_RND_ZERO/AP_WRAP"), ("<22,12>", "AP_RND_ZERO/AP_WRAP"),
            ("<24,12>", "AP_RND_ZERO/AP_WRAP"), ("<26,12>", "AP_RND_ZERO/AP_WRAP"),
            ("<28,14>", "AP_RND_ZERO/AP_WRAP"), ("<30,14>", "AP_TRN/AP_SAT")]
ABREV = {"AP_RND_ZERO/AP_WRAP": "RND_ZERO/WRAP", "AP_TRN/AP_SAT": "TRN/SAT"}
N_PRB = 275
MS = 6   # tamanho dos marcadores (era 4,5; maiores a pedido, 2026-11-09)
DISPOSITIVO = {"lut": 871680, "ff": 1743360, "dsp": 5952, "bram_18k": 2688}  # XCU50 (utilizacao.rpt)


def ler():
    """{(condição, formato, modo): linha} das arquiteturas otimizadas em 16 x 16."""
    dados = {}
    with open(TABELA, newline="") as f:
        for r in csv.DictReader(f):
            if r["tamanho"] != "16 x 16" or r["arquitetura"] not in ARQ:
                continue
            cond, tc, lim = ARQ[r["arquitetura"]]
            v = {k: (float(r[k]) if r[k] else None) for k in
                 ("potencia_dinamica_w", "potencia_total_w", "energia_por_inversao_uj",
                  "intervalo_ciclos", "dsp", "lut", "ff", "bram_18k")}
            if v["lut"] is not None:
                v["ocupacao_pct"] = max(100 * (v[k] or 0) / DISPOSITIVO[k] for k in DISPOSITIVO)
            if v["potencia_dinamica_w"] is not None:
                v["estatica_w"] = v["potencia_total_w"] - v["potencia_dinamica_w"]
                v["dinamica_media_w"] = v["energia_por_inversao_uj"] * 1e-6 * N_PRB / (tc * 1e-3)
                v["ocupacao_tempo"] = v["intervalo_ciclos"] / lim
            dados[(cond, r["formato"], r["quantizacao/overflow"])] = v
    return dados


def ler_sem_otimizacao():
    """{(rótulo, formato, modo): linha} da versão sem otimização, em 16 x 16 e 32 x 32."""
    dados = {}
    with open(TABELA, newline="") as f:
        for r in csv.DictReader(f):
            if r["arquitetura"] == "sem_otimizacao" and r["energia_por_inversao_uj"]:
                v = {k: float(r[k]) for k in ("energia_por_inversao_uj", "potencia_dinamica_w",
                                              "potencia_total_w")}
                v["estatica_w"] = v["potencia_total_w"] - v["potencia_dinamica_w"]
                v["ocupacao_pct"] = max(100 * float(r[k]) / DISPOSITIVO[k] for k in DISPOSITIVO)
                dados[(SEM_OPT[r["tamanho"]], r["formato"], r["quantizacao/overflow"])] = v
    return dados


PERFIL_LEG = (("Low mobility", ("TDLA30-5", "TDLA30-10", "TDLA30-75")),
              ("High mobility", ("TDLC300-100", "TDLA30-300", "TDLB100-400")),
              ("Without optimization", tuple(SEM_OPT.values())))


def legenda_perfis(fig, ax_direita, y=0.0, fontsize=7, discreto=False):
    """Legenda em 3 colunas, cada uma com o título no topo: baixa mobilidade, alta mobilidade e
    versão sem otimização (pedido da autora, 2026-11-15)."""
    linhas = max(len(c) for _, c in PERFIL_LEG) + 1
    h, titulos = [], []
    for titulo, conds in PERFIL_LEG:
        titulos.append(len(h))
        h.append(Patch(visible=False, label=titulo))
        for c in conds:
            rot = c.replace("Without opt., ", "")
            d = discreto and c in SEM_OPT.values()
            h.append(Line2D([], [], color=COR[c], marker=MARCA[c], ms=DISCRETO["ms"] if d else MS,
                            lw=DISCRETO["lw"] if d else 1.4, mew=DISCRETO["mew"] if d else 1.0,
                            mfc=SURFACE if c in VAZADO else COR[c], mec=COR[c],
                            ls=TRACO.get(c, "-"), label=rot))
        h += [Patch(visible=False, label="")] * (len(titulos) * linhas - len(h))
    leg = legenda_quadro(fig, ax_direita, h, y=y, ncol=len(PERFIL_LEG), fontsize=fontsize)
    for i, t in enumerate(leg.get_texts()):
        if i in titulos:
            t.set_color(INK_PRIMARY)
    return leg


def rotulos_formatos(ax):
    # o modo só aparece quando não é o RND_ZERO/WRAP (o padrão, dito na legenda da figura)
    ax.set_xticks(range(len(FORMATOS)),
                  [f + ("\nTRN/SAT" if m == "AP_TRN/AP_SAT" else "") for f, m in FORMATOS],
                  fontsize=7)
    ax.set_xlim(-0.4, len(FORMATOS) - 0.6)


def marcas_log(ax, valores):
    ax.set_yticks(valores, [f"{v:g}" for v in valores])
    ax.minorticks_off()


def figura_por_formato(dados, chave, nome, ylabel, casas, marcas, rotulo_direto=True, escala="log",
                       series=ORDEM, ncol=3):
    fig, ax = plt.subplots(figsize=(LARGURA, 3.6), facecolor=SURFACE)
    eixos(ax, grade_x=False, grade_y=True)
    linhas = []
    for cond in series:
        xs, ys = [], []
        for i, (f, m) in enumerate(FORMATOS):
            v = dados.get((cond, f, m))
            if v and v.get(chave) is not None:
                xs.append(i)
                ys.append(v[chave])
                linhas.append([cond, f, m, f"{v[chave]:.{casas}f}"])
        ax.plot(xs, ys, color=COR[cond], marker=MARCA[cond], ms=MS, lw=1.4,
                mfc=SURFACE if cond in VAZADO else COR[cond], mec=COR[cond], mew=1.2,
                ls=TRACO.get(cond, "-"), zorder=3)
        if rotulo_direto:
            # <30,14> TRN/SAT não cabe no FPGA na arquitetura da TDLB100-400
            extra = "\n(<30,14> does not fit\nthe FPGA: 7,512 DSP)" if xs[-1] < len(FORMATOS) - 1 else ""
            ax.annotate(cond + extra, (xs[-1], ys[-1]), xytext=(6, 0),
                        textcoords="offset points", va="center", fontsize=7,
                        color=COR[cond], linespacing=1.1)
    if escala == "log":
        ax.set_yscale("log")
        marcas_log(ax, marcas)
    else:  # linear desde 0 (energia, pedido da autora em 2026-11-15)
        ax.set_ylim(0, None)
    rotulos_formatos(ax)
    ax.set_xlim(-0.4, len(FORMATOS) + (0.9 if rotulo_direto else -0.6))
    ax.set_ylabel(ylabel, fontsize=8, color=INK_SECONDARY)
    ax.set_xlabel("Format", fontsize=8, color=INK_SECONDARY)
    ax.tick_params(axis="y", labelsize=7)
    if rotulo_direto:
        fig.tight_layout()
    else:
        h = [Line2D([], [], color=COR[c], marker=MARCA[c], ms=MS, lw=1.4,
                    mfc=SURFACE if c in VAZADO else COR[c], mec=COR[c],
                    ls=TRACO.get(c, "-"), label=c) for c in series]
        if len(series) > len(ORDEM):
            fig.tight_layout(rect=(0, 0.21, 1, 1))
            legenda_perfis(fig, ax)
        else:
            fig.tight_layout(rect=(0, 0.13, 1, 1))
            legenda_quadro(fig, ax, h, ncol=ncol, fontsize=7)
    fag.salvar(fig, nome, linhas, ["condicao", "formato", "modo", chave])


def figura_media(dados, fmt=("<24,12>", "AP_RND_ZERO/AP_WRAP")):
    fig, ax = plt.subplots(figsize=(LARGURA, 2.8), facecolor=SURFACE)
    eixos(ax, grade_x=True, grade_y=False)
    linhas = []
    for y, cond in enumerate(ORDEM):
        v = dados[(cond, *fmt)]
        e, d = v["estatica_w"], v["dinamica_media_w"]
        ax.barh(y, e, height=0.55, color="#e4e3df", edgecolor=SURFACE, lw=1, zorder=2)
        # TDLA30-10 (provisório): barra vazada, só o contorno na cor da TDLA30-5
        ax.barh(y, d, left=e, height=0.55, zorder=2,
                color=SURFACE if cond in VAZADO else COR[cond],
                edgecolor=COR[cond] if cond in VAZADO else SURFACE, lw=1)
        ax.text(e + d + 0.05, y, f"{e + d:.2f} W  (static {100 * e / (e + d):.0f} %)",
                va="center", fontsize=7, color=INK_SECONDARY)
        linhas.append([cond, *fmt, f"{e:.3f}", f"{d:.3f}", f"{e + d:.3f}",
                       f"{v['ocupacao_tempo']:.3f}"])
    ax.set_yticks(range(len(ORDEM)), ORDEM, fontsize=7.5)
    ax.set_xlim(0, 6.2)
    ax.set_xlabel("Average power at the required rate [W]", fontsize=8, color=INK_SECONDARY)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_title(f"{fmt[0]} {ABREV[fmt[1]]}", fontsize=8, color=INK_PRIMARY, loc="left")
    # rótulos diretos na primeira barra, no lugar de uma legenda com uma cor que não existe
    v0 = dados[(ORDEM[0], *fmt)]
    ax.text(v0["estatica_w"] / 2, 0, "static", ha="center", va="center", fontsize=7,
            color=INK_SECONDARY)
    ax.annotate("dynamic", (v0["estatica_w"] + v0["dinamica_media_w"] / 2, -0.28),
                xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                fontsize=7, color=INK_SECONDARY)
    ax.set_ylim(len(ORDEM) - 0.5, -0.85)
    fig.tight_layout()
    fag.salvar(fig, "potencia_media_condicao", linhas,
               ["condicao", "formato", "modo", "estatica_w", "dinamica_media_w", "media_w",
                "ocupacao_tempo"])


# versão sem otimização discreta na figura de ocupação e potência (fica perto de zero;
# pedido da autora, 2026-11-15)
DISCRETO = dict(ms=2.5, lw=0.7, mew=0.6, zorder=2.5)


def linha_cond(ax, dados, cond, chave, discreto=False):
    xs, ys = [], []
    for i, (f, m) in enumerate(FORMATOS):
        v = dados.get((cond, f, m))
        if v and v.get(chave) is not None:
            xs.append(i)
            ys.append(v[chave])
    estilo = dict(ms=MS, lw=1.4, mew=1.2, zorder=3)
    if discreto and cond in SEM_OPT.values():
        estilo = DISCRETO
    ax.plot(xs, ys, color=COR[cond], marker=MARCA[cond],
            mfc=SURFACE if cond in VAZADO else COR[cond], mec=COR[cond],
            ls=TRACO.get(cond, "-"), **estilo)
    return xs, ys


def espalhar(ys_px, minimo):
    """Posições (em pixels) o mais perto possível das originais, na mesma ordem, com pelo
    menos `minimo` entre vizinhas."""
    ordem = sorted(range(len(ys_px)), key=lambda i: ys_px[i])
    pos = [ys_px[i] for i in ordem]
    for _ in range(200):
        for j in range(1, len(pos)):
            if pos[j] - pos[j - 1] < minimo:
                meio = (pos[j] + pos[j - 1]) / 2
                pos[j - 1], pos[j] = meio - minimo / 2, meio + minimo / 2
    out = [0] * len(ys_px)
    for i, p_ in zip(ordem, pos):
        out[i] = p_
    return out


def figura_tres_paineis(dados):
    """Energia por inversão, potência dinâmica e ocupação do FPGA, com o mesmo eixo de formatos."""
    fig, axs = plt.subplots(3, 1, figsize=(LARGURA, 8.4), sharex=True, facecolor=SURFACE,
                            gridspec_kw=dict(height_ratios=(1, 1.15, 0.9)))
    fig.subplots_adjust(left=0.1, right=0.82, top=0.985, bottom=0.135, hspace=0.14)
    linhas = []
    for cond in ORDEM:
        for f, m in FORMATOS:
            v = dados.get((cond, f, m)) or {}
            e = v.get("estatica_w")
            linhas.append([cond, f, m] + [
                "" if v.get(k) is None else f"{v[k]:.3f}"
                for k in ("energia_por_inversao_uj", "potencia_dinamica_w", "estatica_w",
                          "ocupacao_pct")] +
                ["" if e is None else f"{100 * v['potencia_dinamica_w'] / e:.1f}"])
    # (a) energia por inversão, log como em energia_inversao_formatos
    ax = axs[0]
    eixos(ax, grade_x=False, grade_y=True)
    for cond in ORDEM:
        linha_cond(ax, dados, cond, "energia_por_inversao_uj")
    ax.set_yscale("log")
    marcas_log(ax, [2, 3, 5, 10, 20, 30])
    ax.set_ylabel("Energy per inversion [µJ]", fontsize=8, color=INK_SECONDARY)
    # (b) potência dinâmica, linear; à direita, a faixa dinâmica/estática de cada condição
    ax = axs[1]
    eixos(ax, grade_x=False, grade_y=True)
    fins = []
    for cond in ORDEM:
        xs, ys = linha_cond(ax, dados, cond, "potencia_dinamica_w")
        pct = [100 * dados[(cond, *FORMATOS[i])]["potencia_dinamica_w"] /
               dados[(cond, *FORMATOS[i])]["estatica_w"] for i in xs]
        fins.append((cond, ys[-1], f"{min(pct):.0f} to {max(pct):.0f} %"))
    ax.set_ylim(0, 5.0)
    ax.set_yticks([i / 2 for i in range(11)], [f"{i / 2:g}" for i in range(11)])
    ax.set_ylabel("Dynamic power [W]", fontsize=8, color=INK_SECONDARY)
    fig.canvas.draw()
    tr = ax.transData
    px = [tr.transform((0, y))[1] for _, y, _ in fins]
    novo_px = espalhar(px, 9 * fig.dpi / 72)
    for (cond, _, txt), yp in zip(fins, novo_px):
        yd = tr.inverted().transform((0, yp))[1]
        ax.annotate(txt, (1.02, yd), xycoords=("axes fraction", "data"), va="center",
                    ha="left", fontsize=7, color=COR[cond], annotation_clip=False)
    ax.annotate("dynamic / static", (1.02, 5.0), xycoords=("axes fraction", "data"),
                xytext=(0, 9), textcoords="offset points", va="bottom", ha="left", fontsize=7, color=INK_SECONDARY, annotation_clip=False)
    # (c) ocupação do FPGA: o recurso mais usado (LUT, FF, DSP ou BRAM), em % da XCU50
    ax = axs[2]
    eixos(ax, grade_x=False, grade_y=True)
    for cond in ORDEM:
        linha_cond(ax, dados, cond, "ocupacao_pct")
    # <30,14> na TDLB100-400: não sintetizado; 7512 DSP na estimativa do HLS (observação da tabela)
    x30 = len(FORMATOS) - 1
    y30 = 100 * 7512 / DISPOSITIVO["dsp"]
    # liga ao <28,14> da mesma linha, pontilhado: é estimativa, não síntese
    y28 = dados[("TDLB100-400", *FORMATOS[x30 - 1])]["ocupacao_pct"]
    ax.plot([x30 - 1, x30], [y28, y30], color=COR["TDLB100-400"], lw=1.4, ls=(0, (1, 1.5)),
            zorder=2.9)
    ax.plot([x30], [y30], ls="", marker=MARCA["TDLB100-400"], ms=MS, mfc=SURFACE,
            mec=COR["TDLB100-400"], mew=1.2, zorder=3)
    ax.annotate("HLS estimate,\nnot synthesizable", (x30, y30), xytext=(-8, 0),
                textcoords="offset points", ha="right", va="center", fontsize=6.5,
                color=COR["TDLB100-400"], linespacing=1.1)
    ax.axhline(100, color=INK_PRIMARY, lw=0.8, zorder=2)
    ax.annotate("XCU50 capacity", (1.0, 100), xycoords=("axes fraction", "data"),
                xytext=(4, 0), textcoords="offset points", va="center", ha="left",
                fontsize=7, color=INK_SECONDARY, annotation_clip=False)
    ax.set_ylim(0, 135)
    ax.set_yticks(range(0, 140, 20), [str(v) for v in range(0, 140, 20)])
    ax.set_ylabel("FPGA utilization [%]\n(most used resource)", fontsize=8,
                  color=INK_SECONDARY)
    rotulos_formatos(ax)
    ax.set_xlabel("Format", fontsize=8, color=INK_SECONDARY)
    for a in axs:
        a.tick_params(axis="y", labelsize=7)
    h = [Line2D([], [], color=COR[c], marker=MARCA[c], ms=MS, lw=1.4,
                mfc=SURFACE if c in VAZADO else COR[c], mec=COR[c], label=c) for c in ORDEM]
    legenda_quadro(fig, axs[2], h, y=0.01, ncol=3, fontsize=7)
    fag.salvar(fig, "energia_potencia_recursos", linhas,
               ["condicao", "formato", "modo", "energia_por_inversao_uj", "potencia_dinamica_w",
                "estatica_w", "ocupacao_pct", "dinamica_sobre_estatica_pct"])


def figura_lado_a_lado(dados, series=ORDEM):
    """Ocupação do FPGA e potência dinâmica, lado a lado (a energia por inversão fica na
    figura própria, energia_inversao_formatos, a pedido da autora em 2026-11-13)."""
    # legenda de 4 linhas (3 colunas por perfil) pede 0,5 pol a mais embaixo
    extra = 0.5 if len(series) > len(ORDEM) else 0.0
    W, H = LARGURA, 4.45 + extra
    fig = plt.figure(figsize=(W, H), facecolor=SURFACE)
    # polegadas: margem esquerda, largura do painel, vão 1 (eixo y do 2), vão 2 (faixas % e eixo
    # y do 3), margem direita; embaixo: rótulos girados dos formatos, "Format" e a legenda
    # ordem: ocupação, potência (a das faixas %, na extrema direita)
    esq, vao, dir_ = 0.55, 0.75, 0.85
    pw = (W - esq - vao - dir_) / 2
    base, alt = 1.62 + extra, 2.65
    xs0 = [esq, esq + pw + vao]
    axs = [fig.add_axes((x / W, base / H, pw / W, alt / H)) for x in xs0]
    linhas = []
    for cond in series:
        for f, m in FORMATOS:
            v = dados.get((cond, f, m)) or {}
            e = v.get("estatica_w")
            linhas.append([cond, f, m] + [
                "" if v.get(k) is None else f"{v[k]:.3f}"
                for k in ("energia_por_inversao_uj", "potencia_dinamica_w", "estatica_w",
                          "ocupacao_pct")] +
                ["" if e is None else f"{100 * v['potencia_dinamica_w'] / e:.1f}"])
    rotulo = dict(fontsize=7.5, color=INK_SECONDARY)
    for ax in axs:
        eixos(ax, grade_x=False, grade_y=True)
        # o formato termina sempre junto da marca; o TRN/SAT vem antes, para alinhar os números
        ax.set_xticks(range(len(FORMATOS)),
                      [("TRN/SAT " if m == "AP_TRN/AP_SAT" else "") + f for f, m in FORMATOS],
                      fontsize=6.5, rotation=90, rotation_mode="anchor", ha="right",
                      va="center")
        ax.set_xlim(-0.5, len(FORMATOS) - 0.5)
        ax.tick_params(axis="y", labelsize=6.5)
    # (b) potência dinâmica, linear; à direita, a faixa dinâmica/estática de cada condição
    ax = axs[1]
    fins = []
    for cond in series:
        xs, ys = linha_cond(ax, dados, cond, "potencia_dinamica_w", discreto=True)
        pct = [100 * dados[(cond, *FORMATOS[i])]["potencia_dinamica_w"] /
               dados[(cond, *FORMATOS[i])]["estatica_w"] for i in xs]
        fins.append((cond, ys[-1], f"{min(pct):.0f} to {max(pct):.0f} %"))
    # versões sem otimização: as duas linhas se sobrepõem, então um rótulo só para as duas
    sem = [x for x in fins if x[0] in SEM_OPT.values()]
    if sem:
        pct = [float(t) for _, _, txt in sem for t in txt.replace(" %", "").split(" to ")]
        fins = [x for x in fins if x not in sem] + [
            (sem[0][0], max(y for _, y, _ in sem), f"{min(pct):.0f} to {max(pct):.0f} %")]
    ax.set_ylim(0, 5.0)
    ax.set_yticks([i / 2 for i in range(11)], [f"{i / 2:g}" for i in range(11)])
    ax.set_ylabel("Dynamic power [W]", **rotulo)
    fig.canvas.draw()
    tr = ax.transData
    px = [tr.transform((0, y))[1] for _, y, _ in fins]
    for (cond, _, txt), yp in zip(fins, espalhar(px, 8.5 * fig.dpi / 72)):
        yd = tr.inverted().transform((0, yp))[1]
        ax.annotate(txt, (1.03, yd), xycoords=("axes fraction", "data"), va="center",
                    ha="left", fontsize=6.5, color=COR[cond], annotation_clip=False)
    ax.annotate("dynamic /\nstatic", (1.03, 5.0), xycoords=("axes fraction", "data"),
                xytext=(0, 9), textcoords="offset points", va="bottom", ha="left",
                fontsize=6.5, color=INK_SECONDARY, annotation_clip=False, linespacing=1.1)
    # (a) ocupação do FPGA: o recurso mais usado (LUT, FF, DSP ou BRAM), em % da XCU50
    ax = axs[0]
    for cond in series:
        linha_cond(ax, dados, cond, "ocupacao_pct", discreto=True)
    # <30,14> na TDLB100-400: não sintetizado; 7512 DSP na estimativa do HLS (observação da tabela)
    x30, y30 = len(FORMATOS) - 1, 100 * 7512 / DISPOSITIVO["dsp"]
    # liga ao <28,14> da mesma linha, pontilhado: é estimativa, não síntese
    y28 = dados[("TDLB100-400", *FORMATOS[x30 - 1])]["ocupacao_pct"]
    ax.plot([x30 - 1, x30], [y28, y30], color=COR["TDLB100-400"], lw=1.4, ls=(0, (1, 1.5)),
            zorder=2.9)
    ax.plot([x30], [y30], ls="", marker=MARCA["TDLB100-400"], ms=MS, mfc=SURFACE,
            mec=COR["TDLB100-400"], mew=1.2, zorder=3)
    ax.annotate("HLS estimate,\nnot synthesizable", (x30, y30), xytext=(-7, 0),
                textcoords="offset points", ha="right", va="center", fontsize=6.3,
                color=COR["TDLB100-400"], linespacing=1.1)
    ax.axhline(100, color=INK_PRIMARY, lw=0.8, zorder=2)
    ax.annotate("XCU50 capacity", (-0.3, 100), xytext=(0, 2), textcoords="offset points",
                va="bottom", ha="left", fontsize=6.3, color=INK_SECONDARY)
    ax.set_ylim(0, 135)
    ax.set_yticks(range(0, 140, 20), [str(v) for v in range(0, 140, 20)])
    ax.set_ylabel("FPGA utilization, most used resource [%]", **rotulo)
    fig.text((xs0[0] + xs0[1] + pw) / 2 / W, (0.69 + extra) / H, "Format", ha="center", va="top", **rotulo)
    h = [Line2D([], [], color=COR[c], marker=MARCA[c], ms=MS, lw=1.4,
                mfc=SURFACE if c in VAZADO else COR[c], mec=COR[c], ls=TRACO.get(c, "-"),
                label=c) for c in series]
    if len(series) > len(ORDEM):
        legenda_perfis(fig, axs[1], y=0.01, discreto=True)
    else:
        legenda_quadro(fig, axs[1], h, y=0.01, ncol=3, fontsize=7)
    fag.salvar(fig, "potencia_recursos_lado", linhas,
               ["condicao", "formato", "modo", "energia_por_inversao_uj", "potencia_dinamica_w",
                "estatica_w", "ocupacao_pct", "dinamica_sobre_estatica_pct"])


# MANUAL_GRAFICOS.md, seção 5 (recurso do FPGA), validada em 2026-11-13
COR_RECURSO = {"lut": "#2a78d6", "ff": "#eda100", "dsp": "#e87ba4", "bram_18k": "#7a7974"}
NOME_RECURSO = {"lut": "LUT", "ff": "FF", "dsp": "DSP", "bram_18k": "BRAM"}
LETRA_RECURSO = {"lut": "L", "ff": "F", "dsp": "D", "bram_18k": "B"}
TOPO_RECURSO = 80   # topo do eixo y da figura de recursos, em % do XCU50


def figura_recursos_faixa(estilo="traco", ligar_maximo=False):
    """Uso de cada recurso do XCU50 por arquitetura (16 x 16), eixo linear até 80 %.
    estilo="traco": traço do menor ao maior uso entre os formatos, com tracinho nas pontas;
    estilo="pontos": um ponto por formato, sem traço. ligar_maximo: tracejado ligando o maior
    uso de cada recurso entre as arquiteturas (testado e recusado em 2026-11-13)."""
    arqs = [("sem_otimizacao", "Without\nopt."), ("9090", "TDLA30-5"), ("4545", "TDLA30-10"),
            ("606", "TDLA30-75"), ("455", "TDLC300-100"), ("152_sistolico", "TDLA30-300"),
            ("114_sistolico", "TDLB100-400")]
    tecnicas = [("Loop\npipelining", 1, 1), ("Dataflow", 2, 2), ("Batches", 3, 4),
                ("Systolic\narrays", 5, 6)]
    vals = {}
    with open(TABELA, newline="") as f:
        for r in csv.DictReader(f):
            if r["tamanho"] != "16 x 16" or not r["lut"]:
                continue
            for k in DISPOSITIVO:
                vals.setdefault((r["arquitetura"], k), []).append(
                    (100 * float(r[k]) / DISPOSITIVO[k], r["formato"], r["quantizacao/overflow"]))
    fig, ax = plt.subplots(figsize=(LARGURA, 3.5), facecolor=SURFACE)
    eixos(ax, grade_x=False, grade_y=True)
    larg = 0.19
    linhas = []
    for i, (arq, _) in enumerate(arqs):
        for j, k in enumerate(DISPOSITIVO):
            v = vals[(arq, k)]
            lo, hi = min(x[0] for x in v), max(x[0] for x in v)
            x = i + (j - 1.5) * larg
            cor = COR_RECURSO[k]
            estoura = arq == "114_sistolico" and k == "dsp"
            if estilo == "traco":
                # traço do menor ao maior formato, com tracinho nas pontas (bigode sem a caixa);
                # no DSP da TDLB100-400 a ponta de cima é a seta do <30,14> (abaixo)
                ax.plot([x, x], [lo, hi], color=cor, lw=1.4, solid_capstyle="butt", zorder=3)
                for y in ((lo,) if estoura else (lo, hi)):
                    ax.plot([x - larg * 0.32, x + larg * 0.32], [y, y], color=cor, lw=1.4,
                            solid_capstyle="butt", zorder=3)
            else:
                # um ponto por formato, sem traço
                ax.plot([x] * len(v), [p_[0] for p_ in v], ls="", marker="o", ms=5, mfc=cor,
                        mec=cor, mew=0, alpha=0.85, zorder=4)
            linhas.append([arq, NOME_RECURSO[k], f"{lo:.2f}", f"{hi:.2f}", len(v)])
            if estoura:
                # <30,14> não sintetizado: 7.512 DSPs na estimativa do HLS (observação do CSV),
                # passa de 100 %. O eixo vai só até 100 %: tracejado do maior formato sintetizado
                # até o topo e uma seta indicando que estoura
                est = 100 * 7512 / DISPOSITIVO["dsp"]
                ax.plot([x, x], [hi, TOPO_RECURSO], color=cor, lw=1.4, ls=(0, (2, 1.6)),
                        zorder=3, clip_on=False)
                ax.annotate("", xy=(x, TOPO_RECURSO + 5.5), xytext=(x, TOPO_RECURSO - 0.8),
                            annotation_clip=False,
                            arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.4,
                                            mutation_scale=7, shrinkA=0, shrinkB=0))
                ax.annotate(f"<30,14>: {est:.0f} % (HLS estimate, above XCU50 capacity)",
                            (x, TOPO_RECURSO + 2.5), xytext=(-8, 0),
                            textcoords="offset points", ha="right", va="center", fontsize=6,
                            color=INK_SECONDARY, annotation_clip=False)
                ax.annotate(LETRA_RECURSO[k], (x, TOPO_RECURSO + 2.5), xytext=(6, 0),
                            textcoords="offset points", ha="left", va="center", fontsize=5.5,
                            color=INK_SECONDARY, annotation_clip=False)
                linhas.append([arq, "DSP (<30,14>, HLS estimate)", "", f"{est:.2f}", 1])
                continue
            ax.annotate(LETRA_RECURSO[k], (x, hi), xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=5.5, color=INK_SECONDARY)
    if ligar_maximo:
        # tracejado na cor do recurso ligando o maior uso (o formato que mais usa) entre as
        # arquiteturas, sem marcador
        for j, k in enumerate(DISPOSITIVO):
            xs = [i + (j - 1.5) * larg for i in range(len(arqs))]
            ys = [max(x[0] for x in vals[(arq, k)]) for arq, _ in arqs]
            ax.plot(xs, ys, color=COR_RECURSO[k], lw=0.8, ls=(0, (3, 2)), alpha=0.8, zorder=2)
    # eixo linear até 80 % (pedido da autora, 2026-11-13), grade a cada 10 %; a linha de 100 %
    # sai do gráfico, e a seta do <30,14> diz que ele passa da capacidade
    ax.set_ylim(0, TOPO_RECURSO)
    ax.set_yticks(range(0, TOPO_RECURSO + 1, 10),
                  [str(v) for v in range(0, TOPO_RECURSO + 1, 10)])
    ax.set_ylabel("XCU50 utilization [%]", fontsize=8, color=INK_SECONDARY)
    ax.set_xticks(range(len(arqs)), [n for _, n in arqs], fontsize=7)
    ax.set_xlim(-0.55, len(arqs) - 0.45)
    ax.tick_params(axis="y", labelsize=7)
    # técnica da Metodologia embaixo dos nomes, com um traço sobre as arquiteturas de cada uma
    for nome, a, b in tecnicas:
        ax.annotate("", xy=(a - 0.42, -0.17), xytext=(b + 0.42, -0.17),
                    xycoords=("data", "axes fraction"), textcoords=("data", "axes fraction"),
                    arrowprops=dict(arrowstyle="-", color=INK_MUTED, lw=0.8))
        ax.text((a + b) / 2, -0.19, nome, transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=6.5, color=INK_SECONDARY, linespacing=1.1)
    for i in range(len(arqs) - 1):
        ax.axvline(i + 0.5, color=GRID, lw=0.6, zorder=1)
    if estilo == "traco":
        h = [Line2D([], [], color=COR_RECURSO[k], lw=1.4,
                    label=f"{NOME_RECURSO[k]} ({LETRA_RECURSO[k]})") for k in DISPOSITIVO]
    else:
        h = [Line2D([], [], ls="", marker="o", ms=5, color=COR_RECURSO[k],
                    label=f"{NOME_RECURSO[k]} ({LETRA_RECURSO[k]})") for k in DISPOSITIVO]
    fig.subplots_adjust(left=0.09, right=0.99, top=0.92, bottom=0.33)
    legenda_quadro(fig, ax, h, y=0.0, ncol=4, fontsize=7)
    fag.salvar(fig, "recursos_faixa_arquitetura" + ("" if estilo == "traco" else "_pontos")
               + ("_max" if ligar_maximo else ""), linhas,
               ["arquitetura", "recurso", "min_pct", "max_pct", "n_formatos"])


def main():
    dados = ler()
    figura_por_formato(dados, "potencia_dinamica_w", "potencia_dinamica_formatos",
                       "Dynamic power [W]", 3, [0.2, 0.3, 0.5, 1, 2, 3, 5])
    figura_por_formato({**dados, **ler_sem_otimizacao()}, "energia_por_inversao_uj",
                       "energia_inversao_formatos", "Energy per inversion [µJ]", 3,
                       [2, 5, 10, 20, 50, 100], rotulo_direto=False, escala="log",
                       series=ORDEM + list(SEM_OPT.values()), ncol=4)
    figura_media(dados)
    figura_tres_paineis(dados)
    figura_lado_a_lado({**dados, **ler_sem_otimizacao()}, ORDEM + list(SEM_OPT.values()))
    figura_recursos_faixa("traco")
    figura_recursos_faixa("pontos")
    figura_recursos_faixa("traco", ligar_maximo=True)


if __name__ == "__main__":
    main()
