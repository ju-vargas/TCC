#!/usr/bin/env python3
"""
Compromisso entre qualidade (aumento de SNR do formato) e custo do hardware (potência,
energia e recursos) nas arquiteturas de inversão.

Qualidade: pior aumento de SNR em SER = 10^-2 do BCD-MMSE (iter 1) no formato sobre o float,
entre as configurações do grupo, na grade inteira (grade_inteira.py: os mesmos dados das
barras, das curvas, do mapa e dos perfis). TDLA30-10 usa a simulação da TDLA30-5 (mesmas
matrizes, Seção de condições de teste). Duas escolhas de configurações: todas (A a H) e só
IoTh de 10 dB (A a D).

Custo: hardware/resultados_servidor/resultados_vivado_servidor.csv (Vivado 2023.2, Alveo U50,
100 MHz, potência com SAIF). As arquiteturas otimizadas só existem em 16 x 16 (grupos 1 e 3,
M_c = 16); o grupo 2 (32 x 32) só tem a versão sem otimização. A potência foi medida com
matrizes do grupo 1 (1A a 1H); o grupo 3 usa o mesmo circuito 16 x 16.

Saídas (hardware/resultados_servidor/figuras e .../tabelas):
  potencia_dinamica_formatos                 potência dinâmica x formato, uma linha por condição
  aumento_snr_perfis                         pior aumento de SNR x formato, painel por grupo,
                                             perfil de mobilidade (vazado/cheio), A-H e A-D
  plano_snr_potencia                         plano aumento de SNR x potência dinâmica relativa ao
                                             <24,12>; linha = grupo (G1, G3), coluna = A-H ou A-D;
                                             vazado = perfil lento, cheio = rápido; linha = Pareto
  quadrantes_cond_g1, _g3                    aumento de SNR (pior configuração do IoTh na
                                             condição) x potência dinâmica em W na arquitetura da
                                             própria condição; painéis IoTh 10 e 20 dB; cor =
                                             condição, marcador = formato, linha = Pareto
  (quadrantes_snr_potencia e plano_snr_potencia: versões anteriores, fora do main)
  (figura_compromisso, por arquitetura, ficou no código mas fora do main: a autora recusou)
  (cada uma em .png, .pdf e _data.csv; sem faixas de cor, grade de papel log)
  tabela_*.tex                               tabelas do TCC (cópia em chapters/RESULTADOS/hardware.tex)
  resumo.txt                                 números do texto

Uso: nice -n 19 ../simulador/.venv/bin/python analise_potencia_qualidade.py
"""

import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib                                       # noqa: E402
import matplotlib.ticker                                # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402

import figuras_analise_grupos as fag                    # noqa: E402
import grade_inteira as gi                              # noqa: E402
from figuras_analise_grupos import eixos, legenda_quadro  # noqa: E402
from dbp_sim.plotting import GRID as GRID_COR  # noqa: E402
from dbp_sim.plotting import INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE  # noqa: E402
from mapa_cenarios_v4 import LETRAS, paineis           # noqa: E402

TABELA = AQUI.parent.parent / "hardware" / "resultados_servidor" / "resultados_vivado_servidor.csv"
FIGURAS = TABELA.parent / "figuras"
TABELAS = TABELA.parent / "tabelas"
fag.SAIDA = FIGURAS
fag.DPI = 600
plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["pdf.fonttype"] = 42
LARGURA = 6.3

# arquitetura -> (condição de teste, T_c em ms, limite em ciclos)
ARQ = {"9090": ("TDLA30-5", 25.0, 9090), "4545": ("TDLA30-10", 12.5, 4545),
       "606": ("TDLA30-75", 1.6667, 606), "455": ("TDLC300-100", 1.25, 454),
       "152_sistolico": ("TDLA30-300", 0.4167, 151), "114_sistolico": ("TDLB100-400", 0.3125, 113)}
ORDEM = ["TDLA30-5", "TDLA30-10", "TDLA30-75", "TDLC300-100", "TDLA30-300", "TDLB100-400"]
SIMULADA = {c: ("TDLA30-5" if c == "TDLA30-10" else c) for c in ORDEM}
LIMITE = {c: lim for c, _, lim in ARQ.values()}
TC = {c: tc for c, tc, _ in ARQ.values()}
N_PRB = 275
DISPOSITIVO = {"lut": 871680, "ff": 1743360, "dsp": 5952, "bram_18k": 2688}  # XCU50 (utilizacao.rpt)
NOME_REC = {"lut": "LUT", "ff": "FF", "dsp": "DSP", "bram_18k": "BRAM"}

RZW, TS = "AP_RND_ZERO/AP_WRAP", "AP_TRN/AP_SAT"
# formatos com hardware: (rótulo, I, F, modo no hardware)
FORMATOS = [("<18,8>", 8, 10, RZW), ("<20,8>", 8, 12, RZW), ("<22,12>", 12, 10, RZW),
            ("<24,12>", 12, 12, RZW), ("<26,12>", 12, 14, RZW), ("<28,14>", 14, 14, RZW),
            ("<30,14>", 14, 16, TS)]
# modo fixo de cada formato no grupo (mapa_cenarios_v4.modo_fixo com a [4] v4/v5): só o
# <18,8> do grupo 3 sai em TRN/SAT
MODO_GRUPO = {g: {f: m for f, _, _, m in FORMATOS} for g in (1, 2, 3)}
MODO_GRUPO[3]["<18,8>"] = TS
# formatos escolhidos (Tabela tab:formatos-escolhidos): critério -> grupo -> formato
CRITERIOS = ["Reaches", "3 dB", "0.1 dB"]
ESCOLHIDOS = {"A-H": {1: ("<22,12>", "<24,12>", "<26,12>"), 2: ("<24,12>", "<28,14>", "<30,14>"),
                      3: ("<24,12>", "<24,12>", "<30,14>")},
              "A-D": {1: ("<18,8>", "<18,8>", "<24,12>"), 2: ("<22,12>", "<22,12>", "<24,12>"),
                      3: ("<22,12>", "<22,12>", "<24,12>")}}
GRUPOS = {1: (128, 8), 2: (256, 8), 3: (256, 16)}
COR_GRUPO = {1: "#2a78d6", 2: "#eb6834", 3: "#4a3aa7"}       # manual, seção 5
MARCA_GRUPO = {1: "o", 2: "s", 3: "D"}
COR_COND = {"TDLA30-5": "#52514e", "TDLA30-10": "#8c5a2e", "TDLA30-75": "#35bcd9",
            "TDLA30-300": "#eb6834", "TDLC300-100": "#4a3aa7", "TDLB100-400": "#d64ad6"}
MARCA_COND = {"TDLA30-5": "o", "TDLA30-10": "o", "TDLA30-75": "s", "TDLA30-300": "D",
              "TDLC300-100": "^", "TDLB100-400": "v"}


def ler_hw():
    """{(arquitetura, formato, modo, tamanho): linha numérica}"""
    hw = {}
    with open(TABELA, newline="") as f:
        for r in csv.DictReader(f):
            v = {k: (float(r[k]) if r[k] else None) for k in
                 ("lut", "ff", "dsp", "bram_18k", "caminho_critico_ns", "potencia_dinamica_w",
                  "potencia_total_w", "energia_por_inversao_uj", "intervalo_ciclos")}
            hw[(r["arquitetura"], r["formato"], r["quantizacao/overflow"], r["tamanho"])] = v
    return hw


def arq_da(cond):
    return next(a for a, (c, *_) in ARQ.items() if c == cond)


def custo(hw, cond, fmt, modo=None):
    """Linha do hardware da condição (arquitetura dela, 16 x 16), ou None se não cabe."""
    modo = modo or next(m for f, _, _, m in FORMATOS if f == fmt)
    v = hw.get((arq_da(cond), fmt, modo, "16 x 16"))
    if not v or v["potencia_dinamica_w"] is None:
        return None
    v = dict(v)
    v["estatica_w"] = v["potencia_total_w"] - v["potencia_dinamica_w"]
    v["media_w"] = v["estatica_w"] + v["energia_por_inversao_uj"] * 1e-6 * N_PRB / (TC[cond] * 1e-3)
    v["mais_usado"] = max(DISPOSITIVO, key=lambda k: v[k] / DISPOSITIVO[k])
    v["mais_usado_pct"] = 100 * v[v["mais_usado"]] / DISPOSITIVO[v["mais_usado"]]
    return v


def configs(g, so_iot10=False, iot=None):
    p = paineis()
    M, C = GRUPOS[g]
    ks = [k for k in range(1, 25) if (p[k].M, p[k].C) == (M, C)]
    iot = 10 if so_iot10 else iot
    return [k for k in ks if iot is None or p[k].iot_db == iot]


PERDAS = gi.Perdas()


def pior(g, cond, fmt, so_iot10=False, iot=None):
    """(pior aumento entre as configurações, configuração) na condição; None se alguma não
    atinge 10^-2; 'pendente' se falta rodada."""
    I, F = next((I, F) for f, I, F, _ in FORMATOS if f == fmt)
    q, o = MODO_GRUPO[g][fmt].split("/")
    vs = []
    for k in configs(g, so_iot10, iot):
        try:
            vs.append((PERDAS[(k, SIMULADA[cond], I, F, q, o)], k))
        except KeyError:
            return "pendente"
    if any(v is None for v, _ in vs):
        return None
    return max(vs)


def pior_todas(g, fmt, so_iot10=False):
    r = [pior(g, c, fmt, so_iot10) for c in ORDEM]
    if "pendente" in r:
        return "pendente"
    if None in r:
        return None
    return max(r)


def fmt_num(v, casas):
    return "--" if v is None else f"{v:.{casas}f}"


# ----------------------------------------------------------------------------- figuras
# perfis de mobilidade (figuras_perfis.PERFIS); TDLA30-10 usa a simulação da TDLA30-5
PERFIS = {"Low mobility": ("TDLA30-5", "TDLA30-10", "TDLA30-75"),
          "High mobility": ("TDLC300-100", "TDLA30-300", "TDLB100-400")}
PISO_X = 0.001                    # eixo log; aumento abaixo de 0,001 dB (inclusive 0) vai para o piso
LIMIARES = (0.1, 3.0)


def grade_log(ax, eixo="y"):
    """Grade de papel log: linhas das décadas e das subdivisões, sem faixas de cor."""
    from dbp_sim.plotting import GRID
    eixo_obj = ax.xaxis if eixo == "x" else ax.yaxis
    eixo_obj.set_minor_locator(matplotlib.ticker.LogLocator(base=10, subs=range(2, 10), numticks=20))
    eixo_obj.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.grid(True, axis=eixo, which="major", color=GRID, linewidth=0.7, zorder=0)
    ax.grid(True, axis=eixo, which="minor", color=GRID, linewidth=0.35, zorder=0)


def limiares(ax, eixo="y"):
    for v in LIMIARES:
        (ax.axhline if eixo == "y" else ax.axvline)(v, color=INK_SECONDARY, lw=0.8, ls=(0, (1, 1.5)),
                                                    zorder=1)


def eixo_aumento(ax, eixo="y"):
    getattr(ax, f"set_{eixo}scale")("log")
    getattr(ax, f"set_{eixo}lim")(PISO_X * 0.8, 25)
    marcas = [0.001, 0.01, 0.1, 1, 3, 10]
    getattr(ax, f"set_{eixo}ticks")(marcas, ["\u2264 0.001", "0.01", "0.1", "1", "3", "10"])
    grade_log(ax, eixo)
    limiares(ax, eixo)


def pior_perfil(g, perfil, fmt, so10):
    r = [pior(g, c, fmt, so10) for c in PERFIS[perfil]]
    if "pendente" in r:
        return "pendente"
    return None if None in r else max(r)


def titulo_grupo(g):
    M, C = GRUPOS[g]
    return f"$M$ = {M}, $C$ = {C}, $M_c$ = {M // C}"


def figura_aumento_perfis():
    """Pior aumento de SNR x formato, um painel por grupo, uma série por perfil e conjunto."""
    fig, axs = plt.subplots(1, 3, figsize=(LARGURA, 2.9), sharey=True, facecolor=SURFACE)
    linhas = []
    for ax, g in zip(axs, (1, 2, 3)):
        eixos(ax, grade_x=False, grade_y=False)
        eixo_aumento(ax)
        for so10, ls in ((False, "-"), (True, (0, (3, 2)))):
            for perfil, cheio in (("Low mobility", False), ("High mobility", True)):
                pts = []
                for i, (f, *_) in enumerate(FORMATOS):
                    r = pior_perfil(g, perfil, f, so10)
                    linhas.append([f"G{g}", "A-D" if so10 else "A-H", perfil, f,
                                   "pendente" if r == "pendente" else
                                   ("nao atinge" if r is None else f"{r[0]:.3f}"),
                                   "" if not isinstance(r, tuple) else str(r[1])])
                    # sem valor (pendente) fica nan: a linha não pula o formato que falta
                    pts.append((i, max(r[0], PISO_X) if isinstance(r, tuple) else float("nan")))
                if pts:
                    ax.plot(*zip(*pts), color=INK_PRIMARY, lw=1.0, ls=ls, marker="o", ms=3.8,
                            mfc=INK_PRIMARY if cheio else SURFACE, mec=INK_PRIMARY, mew=0.9,
                            zorder=3)
        ax.set_title(titulo_grupo(g), loc="left", fontsize=8, color=INK_PRIMARY)
        ax.set_xticks(range(len(FORMATOS)), [f for f, *_ in FORMATOS], rotation=90, fontsize=7)
        ax.set_xlim(-0.5, len(FORMATOS) - 0.5)
        ax.tick_params(labelsize=7)
        ax.minorticks_on()
        ax.tick_params(axis="x", which="minor", bottom=False)
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    for v, t in zip(LIMIARES, ("0.1 dB", "3 dB")):
        axs[-1].annotate(t, (1, v), xycoords=("axes fraction", "data"), xytext=(3, 0),
                         textcoords="offset points", va="center", fontsize=6.5, color=INK_MUTED)
    axs[0].set_ylabel("Worst SNR increase over\nBCD-MMSE float [dB]", fontsize=8, color=INK_SECONDARY)
    fig.supxlabel("Format", fontsize=8, color=INK_SECONDARY, y=0.0)
    h = [Line2D([], [], color=INK_PRIMARY, marker="o", ms=3.8, lw=0, mfc=SURFACE, label="Low mobility"),
         Line2D([], [], color=INK_PRIMARY, marker="o", ms=3.8, lw=0, mfc=INK_PRIMARY, label="High mobility"),
         Line2D([], [], color=INK_PRIMARY, lw=1.0, label="All configurations (A to H)"),
         Line2D([], [], color=INK_PRIMARY, lw=1.0, ls=(0, (3, 2)), label="IoTh 10 dB (A to D)")]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 0.995), ncol=4, fontsize=7,
               frameon=False, labelcolor=INK_SECONDARY, handlelength=2.4, columnspacing=1.4)
    fig.subplots_adjust(left=0.12, right=0.94, top=0.88, bottom=0.25, wspace=0.08)
    fag.salvar(fig, "aumento_snr_perfis", linhas,
               ["grupo", "configuracoes", "perfil", "formato", "pior_aumento_db", "configuracao_do_pior"])


def pareto(pts):
    """Pontos (x, y) não dominados: nenhum outro tem x e y menores ou iguais."""
    return sorted(p for p in pts if not any(q != p and q[0] <= p[0] and q[1] <= p[1] for q in pts))


def figura_compromisso(hw, grandeza="potencia_dinamica_w", nome="compromisso_snr_potencia",
                       rotulo="Dynamic power [W]"):
    """Plano aumento de SNR x potência, um painel por arquitetura (linha = perfil)."""
    fig, axs = plt.subplots(2, 3, figsize=(LARGURA, 5.0), sharex=True, facecolor=SURFACE)
    fig.subplots_adjust(left=0.1, right=0.92, top=0.93, bottom=0.09, hspace=0.32, wspace=0.62)
    series = [(g, so10) for g in (1, 3) for so10 in (False, True)]
    linhas = []
    for ax, cond in zip(axs.flat, [c for p in PERFIS.values() for c in p]):
        eixos(ax, grade_x=False, grade_y=True)
        eixo_aumento(ax, "x")
        ys = {}
        for g, so10 in series:
            pts = []
            for f, *_ in FORMATOS:
                v = custo(hw, cond, f, MODO_GRUPO[g][f])
                r = pior(g, cond, f, so10)
                linhas.append([cond, f"G{g}", "A-D" if so10 else "A-H", f,
                               "" if v is None else f"{v[grandeza]:.3f}",
                               "pendente" if r == "pendente" else
                               ("nao atinge" if r is None else f"{r[0]:.3f}")])
                if v is None or not isinstance(r, tuple):
                    continue
                pts.append((max(r[0], PISO_X), v[grandeza], f))
                ys.setdefault(f, []).append((max(r[0], PISO_X), v[grandeza]))
            cor = COR_GRUPO[g]
            ax.scatter([x for x, _, _ in pts], [y for _, y, _ in pts], s=16, marker=MARCA_GRUPO[g],
                       facecolors=SURFACE if so10 else cor, edgecolors=cor, linewidths=0.9, zorder=4)
            fr = pareto([(x, y) for x, y, _ in pts])
            if len(fr) > 1:
                ax.plot(*zip(*fr), color=cor, lw=0.9, ls=(0, (3, 2)) if so10 else "-", zorder=3)
        # formato: o mesmo circuito nos dois grupos, então cada formato é uma linha horizontal;
        # o rótulo fica à direita, afastado dos vizinhos
        rot = sorted((y[0][1], f) for f, y in ys.items())
        ax.margins(y=0.08)
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, ymax)
        altura = ax.get_window_extent().height * 72 / fig.dpi      # em pontos
        gap = 7.0 * (ymax - ymin) / altura                           # 7 pt em unidades do eixo
        pos = []
        for y, f in rot:
            pos.append(max(y, pos[-1] + gap) if pos else y)
        excesso = pos[-1] - (ymax - 0.3 * gap) if pos else 0
        for i in range(len(pos) - 1, -1, -1):                       # empurra para baixo o que passou do topo
            if excesso <= 0:
                break
            pos[i] -= excesso
            excesso = (pos[i - 1] + gap) - pos[i] if i else 0
        for (y, f), yp in zip(rot, pos):
            ax.annotate(f, (1, yp), xycoords=("axes fraction", "data"), xytext=(2, 0),
                        textcoords="offset points", va="center", fontsize=6, color=INK_SECONDARY,
                        annotation_clip=False)
        ax.set_title(f"{cond} ({ARQ[arq_da(cond)][2]} cycles)", loc="left", fontsize=7.5,
                     color=INK_PRIMARY)
        ax.tick_params(labelsize=7)
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    for ax in axs.flat:      # a grade depois da escala: set_xscale nos eixos compartilhados a apaga
        grade_log(ax, "x")
    for ax, p in zip(axs[:, 0], PERFIS):
        ax.set_ylabel(f"{p}\n{rotulo}", fontsize=8, color=INK_SECONDARY)
    for ax in axs[1]:     # o rótulo do piso vai para a esquerda da marca, longe do 0.01
        ax.get_xticklabels()[0].set_horizontalalignment("right")
    fig.supxlabel("Worst SNR increase over BCD-MMSE float [dB]", fontsize=8, color=INK_SECONDARY,
                  y=0.01)
    h = [Line2D([], [], color=COR_GRUPO[g], marker=MARCA_GRUPO[g], ms=4.2, mew=0.9,
                mfc=SURFACE if so10 else COR_GRUPO[g], ls=(0, (3, 2)) if so10 else "-", lw=0.9,
                label=f"G{g}, " + ("IoTh 10 dB (A to D)" if so10 else "A to H"))
         for g, so10 in series]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 0.995), ncol=4, fontsize=7,
               frameon=False, labelcolor=INK_SECONDARY, handlelength=2.4, columnspacing=1.2)
    fig.subplots_adjust(left=0.1, right=0.92, top=0.93, bottom=0.09, hspace=0.32, wspace=0.62)
    fag.salvar(fig, nome, linhas, ["condicao", "grupo", "configuracoes", "formato", grandeza,
                                   "pior_aumento_db"])


def figura_potencia_formatos(hw):
    """Potência dinâmica x formato, uma linha por condição (antes o painel de baixo de
    compromisso_formatos), eixo log com grade de papel log, rótulo direto em cada linha."""
    fig, ax = plt.subplots(figsize=(LARGURA, 3.0), facecolor=SURFACE)
    eixos(ax, grade_x=False, grade_y=False)
    linhas = []
    for cond in ORDEM:
        pts = [(i, custo(hw, cond, f)["potencia_dinamica_w"])
               for i, (f, *_) in enumerate(FORMATOS) if custo(hw, cond, f)]
        vaz = cond == "TDLA30-10"
        ax.plot(*zip(*pts), color=COR_COND[cond], marker=MARCA_COND[cond], ms=4.5, lw=1.3,
                mfc=SURFACE if vaz else COR_COND[cond], mec=COR_COND[cond], mew=1.2,
                ls=(0, (3, 2)) if vaz else "-", zorder=3)
        ax.annotate(cond, pts[-1], xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=6.5, color=COR_COND[cond])
        linhas += [[cond, FORMATOS[i][0], f"{y:.3f}"] for i, y in pts]
    ax.set_yscale("log")
    ax.set_ylim(0.12, 6)
    ax.set_yticks([0.2, 0.5, 1, 2, 5], ["0.2", "0.5", "1", "2", "5"])
    grade_log(ax, "y")
    ax.set_ylabel("Dynamic power [W]", fontsize=8, color=INK_SECONDARY)
    ax.tick_params(labelsize=7)
    ax.set_xticks(range(len(FORMATOS)), [f + ("\nTRN/SAT" if m == TS else "") for f, _, _, m in FORMATOS],
                  fontsize=7)
    ax.tick_params(axis="x", which="minor", bottom=False)
    ax.set_xlim(-0.4, len(FORMATOS) + 0.8)
    ax.set_xlabel("Format", fontsize=8, color=INK_SECONDARY)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.97, bottom=0.2)
    fag.salvar(fig, "potencia_dinamica_formatos", linhas, ["condicao", "formato", "potencia_dinamica_w"])


BASE = "<24,12>"


def potencia_relativa(hw, g, fmt):
    """Potência dinâmica do formato sobre a do <24,12>, na mesma arquitetura: (média, mín, máx)
    entre as arquiteturas otimizadas em que o formato cabe."""
    q = []
    for c in ORDEM:
        v, b = custo(hw, c, fmt, MODO_GRUPO[g][fmt]), custo(hw, c, BASE)
        if v and b:
            q.append(v["potencia_dinamica_w"] / b["potencia_dinamica_w"])
    return sum(q) / len(q), min(q), max(q)


def figura_plano(hw):
    """Plano aumento de SNR x potência relativa: linha = grupo, coluna = conjunto de
    configurações; cada formato é uma linha horizontal; vazado = perfil lento, cheio = rápido."""
    fig, axs = plt.subplots(2, 2, figsize=(LARGURA, 5.4), sharex=True, sharey=True, facecolor=SURFACE)
    fig.subplots_adjust(left=0.1, right=0.9, top=0.86, bottom=0.1, hspace=0.22, wspace=0.3)
    linhas = []
    for i, g in enumerate((1, 3)):
        rel = {f: potencia_relativa(hw, g, f) for f, *_ in FORMATOS}
        for j, so10 in enumerate((False, True)):
            ax = axs[i][j]
            eixos(ax, grade_x=False, grade_y=False)
            for perfil, cheio in (("Low mobility", False), ("High mobility", True)):
                pts = []
                for f, *_ in FORMATOS:
                    r = pior_perfil(g, perfil, f, so10)
                    linhas.append([f"G{g}", "A-D" if so10 else "A-H", perfil, f,
                                   f"{rel[f][0]:.3f}", f"{rel[f][1]:.3f}", f"{rel[f][2]:.3f}",
                                   "pendente" if r == "pendente" else
                                   ("nao atinge" if r is None else f"{r[0]:.3f}")])
                    if isinstance(r, tuple):
                        pts.append((max(r[0], PISO_X), 100 * rel[f][0]))
                # vazado maior por cima do cheio menor: valores iguais aparecem como anel com ponto
                ax.scatter(*zip(*pts), s=42 if not cheio else 14, marker="o", linewidths=1.0,
                           facecolors=INK_PRIMARY if cheio else "none", edgecolors=INK_PRIMARY,
                           zorder=5 if not cheio else 4)
                fr = pareto(pts)
                ax.plot(*zip(*fr), color=INK_PRIMARY, lw=0.9, ls="-" if cheio else (0, (3, 2)),
                        zorder=3)
            eixo_aumento(ax, "x")
            ax.set_ylim(60, 168)
            ax.set_yticks([60, 80, 100, 120, 140, 160])
            # grade y nas alturas dos formatos: cada linha horizontal é um formato
            for f_, *_ in FORMATOS:
                ax.axhline(100 * rel[f_][0], color=GRID_COR, lw=0.8, zorder=0)
            ax.tick_params(labelsize=7)
            # nome de cada formato à direita, na altura dele (afastado dos vizinhos)
            rot = sorted((100 * rel[f][0], f) for f, *_ in FORMATOS)
            pos = []
            for y, f in rot:
                pos.append(max(y, pos[-1] + 5.5) if pos else y)
            for (y, f), yp in zip(rot, pos):
                # rótulo afastado do vizinho: um traço curto liga o nome à linha do formato
                ax.annotate(f, (1, y), xycoords=("axes fraction", "data"),
                            xytext=(1.06, yp), textcoords=("axes fraction", "data"), va="center",
                            fontsize=6.5, color=INK_SECONDARY, annotation_clip=False,
                            arrowprops=dict(arrowstyle="-", color=GRID_COR, lw=0.8,
                                            shrinkA=0, shrinkB=0))
            ax.set_title(titulo_grupo(g), loc="left", fontsize=7.5, color=INK_PRIMARY)
            if i == 0:
                ax.annotate("All configurations (A to H)" if not so10 else "IoTh 10 dB (A to D)",
                            (0.5, 1.14), xycoords="axes fraction", ha="center", fontsize=8,
                            color=INK_PRIMARY)
    for ax in axs.flat:
        grade_log(ax, "x")
    for ax in axs[1]:
        ax.get_xticklabels()[0].set_horizontalalignment("right")
    for ax in axs[:, 0]:
        ax.set_ylabel(f"Dynamic power relative\nto {BASE} [%]", fontsize=8, color=INK_SECONDARY)
    fig.supxlabel("Worst SNR increase over BCD-MMSE float [dB]", fontsize=8, color=INK_SECONDARY,
                  y=0.02)
    h = [Line2D([], [], color=INK_PRIMARY, marker="o", ms=6.5, mfc="none", ls=(0, (3, 2)), lw=0.9,
                label="Low mobility"),
         Line2D([], [], color=INK_PRIMARY, marker="o", ms=3.8, mfc=INK_PRIMARY, lw=0.9,
                label="High mobility")]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 0.94), ncol=2, fontsize=7,
               frameon=False, labelcolor=INK_SECONDARY, handlelength=2.6, columnspacing=1.6)
    fag.salvar(fig, "plano_snr_potencia", linhas,
               ["grupo", "configuracoes", "perfil", "formato", "potencia_relativa_media",
                "potencia_relativa_min", "potencia_relativa_max", "pior_aumento_db"])


def figura_bussola(hw):
    """Plano em quadrantes (como o political compass): centro em 0,1 dB e na potência do
    <24,12>; um painel por grupo; cheio = todas as configurações, vazado = só IoTh 10 dB;
    aumento = pior entre todas as condições de teste."""
    import math
    X0, Y0 = 0.1, 100.0
    fig, axs = plt.subplots(1, 2, figsize=(LARGURA, 3.55), facecolor=SURFACE)
    fig.subplots_adjust(left=0.09, right=0.9, top=0.84, bottom=0.15, wspace=0.42)
    linhas = []
    for ax, g in zip(axs, (1, 3)):
        ax.set_facecolor(SURFACE)
        for lado in ax.spines.values():
            lado.set_color(INK_MUTED)
            lado.set_linewidth(0.6)
        ax.set_xscale("log")
        ax.set_xlim(10 ** -3.2, 10 ** 1.2)   # simétrico em décadas em torno de 0,1 dB
        ax.set_ylim(20, 180)                 # simétrico em torno de 100 %
        grade_log(ax, "x")
        ax.set_xticks([0.001, 0.01, 0.1, 1, 10], ["≤ 0.001", "0.01", "0.1", "1", "10"])
        ax.set_yticks([20, 60, 100, 140, 180])
        ax.grid(True, axis="y", color=GRID_COR, lw=0.6, zorder=0)
        ax.tick_params(labelsize=7, colors=INK_SECONDARY, length=2.5, width=0.6)
        # eixos do plano, cruzando no centro
        ax.axvline(X0, color=INK_PRIMARY, lw=1.0, zorder=2)
        ax.axhline(Y0, color=INK_PRIMARY, lw=1.0, zorder=2)
        ax.axvline(3.0, color=INK_SECONDARY, lw=0.8, ls=(0, (1, 1.5)), zorder=2)
        ax.text(3.0, 140, "3 dB", rotation=90, ha="right", va="center", fontsize=6,
                color=INK_SECONDARY, zorder=2)
        # nomes dos quadrantes nos cantos, numa faixa sem dados (y abaixo de 30 e acima de 170)
        caixa = dict(boxstyle="square,pad=0.15", fc=SURFACE, ec="none")
        for (x, y, ha, va), t in zip(((0.0105, 0.02, "left", "bottom"), (0.99, 0.02, "right", "bottom"),
                                      (0.0105, 0.98, "left", "top"), (0.99, 0.98, "right", "top")),
                                     ("less power, \u2264 0.1 dB", "less power, > 0.1 dB",
                                      "more power, \u2264 0.1 dB", "more power, > 0.1 dB")):
            ax.text(x, y, t, transform=ax.transAxes, ha=ha, va=va, fontsize=6.3,
                    color=INK_SECONDARY, bbox=caixa, zorder=3)
        rel = {f: potencia_relativa(hw, g, f) for f, *_ in FORMATOS}
        cor = COR_GRUPO[g]
        for so10 in (False, True):
            pts = []
            for f, *_ in FORMATOS:
                r = pior_todas(g, f, so10)
                linhas.append([f"G{g}", "A-D" if so10 else "A-H", f, f"{rel[f][0]:.3f}",
                               f"{rel[f][1]:.3f}", f"{rel[f][2]:.3f}",
                               "pendente" if r == "pendente" else
                               ("nao atinge" if r is None else f"{r[0]:.3f}")])
                if isinstance(r, tuple):
                    pts.append((max(r[0], PISO_X), 100 * rel[f][0]))
            ax.scatter(*zip(*pts), s=26, marker=MARCA_GRUPO[g], linewidths=1.0,
                       facecolors=SURFACE if so10 else cor, edgecolors=cor, zorder=5)
            fr = pareto(pts)
            ax.plot(*zip(*fr), color=cor, lw=0.9, ls=(0, (3, 2)) if so10 else "-", zorder=4)
        # nome do formato à direita da sua linha (afastado dos vizinhos)
        rot = sorted((100 * rel[f][0], f) for f, *_ in FORMATOS)
        pos = []
        for y, f in rot:
            pos.append(max(y, pos[-1] + 6.5) if pos else y)
        for (y, f), yp in zip(rot, pos):
            ax.axhline(y, color=GRID_COR, lw=0.8, zorder=0)
            ax.annotate(f, (1, y), xycoords=("axes fraction", "data"), xytext=(1.04, yp),
                        textcoords=("axes fraction", "data"), va="center", fontsize=6.5,
                        color=INK_SECONDARY, annotation_clip=False,
                        arrowprops=dict(arrowstyle="-", color=GRID_COR, lw=0.8, shrinkA=0, shrinkB=0))
        ax.set_title(titulo_grupo(g), loc="left", fontsize=8, color=INK_PRIMARY)
        ax.set_xlabel("Worst SNR increase over\nBCD-MMSE float [dB]", fontsize=7.5,
                      color=INK_SECONDARY)
    axs[0].set_ylabel(f"Dynamic power relative to {BASE} [%]", fontsize=7.5, color=INK_SECONDARY)
    for ax in axs:
        ax.get_xticklabels()[0].set_horizontalalignment("right")
    h = [Line2D([], [], color=COR_GRUPO[g], marker=MARCA_GRUPO[g], ms=4.5, mew=1.0,
                mfc=SURFACE if so10 else COR_GRUPO[g], ls=(0, (3, 2)) if so10 else "-", lw=0.9,
                label=f"G{g}, " + ("IoTh 10 dB (A to D)" if so10 else "A to H"))
         for g in (1, 3) for so10 in (False, True)]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 0.93), ncol=4, fontsize=6.8,
               frameon=False, labelcolor=INK_SECONDARY, handlelength=2.4, columnspacing=1.0)
    fag.salvar(fig, "quadrantes_snr_potencia", linhas,
               ["grupo", "configuracoes", "formato", "potencia_relativa_media",
                "potencia_relativa_min", "potencia_relativa_max", "pior_aumento_db"])


def potencia_relativa_perfil(hw, g, fmt, perfil):
    """Potência dinâmica do formato sobre a do <24,12> na mesma arquitetura, média das
    arquiteturas do perfil. G2 (32 x 32) só tem a versão sem otimização, a mesma nos dois perfis.
    None se não há medida."""
    if g == 2:
        v = hw.get(("sem_otimizacao", fmt, MODO_GRUPO[g][fmt], "32 x 32"))
        b = hw.get(("sem_otimizacao", BASE, RZW, "32 x 32"))
        if not v or v["potencia_dinamica_w"] is None:
            return None
        return v["potencia_dinamica_w"] / b["potencia_dinamica_w"]
    q = []
    for c in PERFIS[perfil]:
        v, b = custo(hw, c, fmt, MODO_GRUPO[g][fmt]), custo(hw, c, BASE)
        if v is None:
            return None          # não cabe numa arquitetura do perfil (o <30,14> na TDLB100-400)
        q.append(v["potencia_dinamica_w"] / b["potencia_dinamica_w"])
    return sum(q) / len(q)


def rotular_formatos(ax, linhas_fmt):
    """Um nome por formato, junto do par de pontos dele (cheio e vazado na mesma altura).
    Tenta à esquerda, à direita, acima e abaixo; evita outros rótulos, pontos e traços."""
    import numpy as np
    rend = ax.figure.canvas.get_renderer()
    caixa_ax = ax.get_window_extent(rend)
    tr = ax.transData
    obst = []            # (x, y, folga em pontos): marcadores pedem mais folga que os traços
    for _, xs, y in linhas_fmt:
        for x in xs:
            obst.append((*tr.transform((x, y)), 3.0))
        if len(xs) > 1:
            for x in np.geomspace(min(xs), max(xs), 40):
                obst.append((*tr.transform((x, y)), 0.5))
    ocupado = []
    fundo = dict(boxstyle="square,pad=0.1", fc=SURFACE, ec="none")
    for f, xs, y in sorted(linhas_fmt, key=lambda t: t[2]):
        xe, xd = min(xs), max(xs)
        meio = (xe * xd) ** 0.5
        # primeiro na mesma altura do par; senão, afastado, com um traço até o ponto
        cand = [((xe, y), (-6, 0), "right", "center", False), ((xd, y), (6, 0), "left", "center", False)]
        for dy in (11, -11, 18, -18):
            va = "bottom" if dy > 0 else "top"
            # o ponto cheio (à direita) primeiro: costuma ficar mais isolado
            cand += [((xd, y), (8, dy), "left", va, True), ((xd, y), (-8, dy), "right", va, True),
                     ((xe, y), (-8, dy), "right", va, True), ((xe, y), (8, dy), "left", va, True)]
        feito = False
        for ponto, off, ha, va, traco in cand:
            t = ax.annotate(f, ponto, xytext=off, textcoords="offset points", ha=ha, va=va,
                            fontsize=6.3, color=INK_PRIMARY, zorder=6, bbox=fundo,
                            arrowprops=dict(arrowstyle="-", color=INK_SECONDARY, lw=0.5,
                                            shrinkA=0, shrinkB=3.5) if traco else None)
            t.update_positions(rend)
            bb = matplotlib.text.Text.get_window_extent(t, rend)   # só o texto, sem o traço
            dentro = caixa_ax.x0 + 2 < bb.x0 and bb.x1 < caixa_ax.x1 - 2 and \
                caixa_ax.y0 + 14 < bb.y0 and bb.y1 < caixa_ax.y1 - 14
            bate = any(bb.overlaps(o) for o in ocupado) or \
                any(bb.x0 - d < px < bb.x1 + d and bb.y0 - d < py < bb.y1 + d for px, py, d in obst)
            if traco and not bate:
                px0, py0 = tr.transform((x, y))
                cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 if off[1] > 0 else bb.y1)
                for t_ in np.linspace(0.15, 0.95, 12):
                    qx, qy = px0 + t_ * (cx - px0), py0 + t_ * (cy - py0)
                    if any(o_.x0 < qx < o_.x1 and o_.y0 < qy < o_.y1 for o_ in ocupado) or \
                            any(abs(qx - px) < 3 and abs(qy - py) < 3 for px, py, d in obst if d > 1):
                        bate = True
                        break
            if dentro and not bate:
                ocupado.append(bb.expanded(1.08, 1.15))
                feito = True
                break
            t.remove()
        if not feito:
            print("rótulo sem lugar livre:", f)
            t = ax.annotate(f, (xe, y), xytext=(-6, 0), textcoords="offset points", ha="right",
                            va="center", fontsize=6.3, color=INK_PRIMARY, zorder=6, bbox=fundo)
            ocupado.append(t.get_window_extent(rend))


def rotular_acima(ax, pts, linha):
    """Nome do formato à direita do ponto, um pouco acima; evita outros rótulos, pontos, os nomes
    das regiões e (se der) a curva de Pareto."""
    import numpy as np
    rend = ax.figure.canvas.get_renderer()
    caixa_ax = ax.get_window_extent(rend)
    tr = ax.transData
    obst = [(*tr.transform((x, y)), 3.0) for x, y, _ in pts]
    for (x1, y1), (x2, y2) in zip(linha, linha[1:]):           # a curva de Pareto
        for t_ in np.linspace(0, 1, 30):
            xa = 10 ** (np.log10(x1) + t_ * (np.log10(x2) - np.log10(x1)))
            obst.append((*tr.transform((xa, y1 + t_ * (y2 - y1))), 0.5))
    # nomes dos quadrantes e o "3 dB" também são obstáculos
    ocupado = [c.get_window_extent(rend).expanded(1.05, 1.2) for c in getattr(ax, "_cantos", [])]
    fundo = None          # sem caixa: o fundo do painel é colorido
    for x, y, f in sorted(pts, key=lambda t: -t[1]):
        # sempre à direita do ponto, um pouco acima (a curva de Pareto desce para a direita);
        # se não couber, à direita e um pouco abaixo; por último, mais longe, com um traço
        cand = [((5, 1), "left", False), ((5, -1), "left", False)]
        cand += [((8, dy), "left", True) for dy in (9, -9, 15, -15)]
        cand += [((-8, dy), "right", True) for dy in (9, -9, 15, -15)]   # perto da borda direita
        # pontos apertados: sobe para a faixa vazia acima deles, com o traço até o ponto
        cand += [((dx, dy), ha, True) for dy in (24, 34, 44, 54) for dx, ha in
                 ((8, "left"), (-8, "right"), (0, "center"), (-25, "right"), (25, "left"),
                  (-40, "right"))]
        # primeira rodada evita também a curva; se não couber, aceita cobrir um trecho dela
        cand = [(o, h, t_, True) for o, h, t_ in cand] + [(o, h, t_, False) for o, h, t_ in cand
                                                          if not t_]
        feito = False
        for off, ha, traco, evita_curva in cand:
            t = ax.annotate(f, (x, y), xytext=off, textcoords="offset points", ha=ha,
                            va="bottom" if off[1] > 0 else "top",
                            fontsize=6.3, color=INK_PRIMARY, zorder=6, bbox=fundo,
                            arrowprops=dict(arrowstyle="-", color=INK_SECONDARY, lw=0.5,
                                            shrinkA=0, shrinkB=3.5) if traco else None)
            t.update_positions(rend)
            bb = matplotlib.text.Text.get_window_extent(t, rend)   # só o texto, sem o traço
            dentro = caixa_ax.x0 + 2 < bb.x0 and bb.x1 < caixa_ax.x1 - 2 and \
                caixa_ax.y0 + 2 < bb.y0 and bb.y1 < caixa_ax.y1 - 2
            bate = any(bb.overlaps(o) for o in ocupado) or \
                any(bb.x0 - d < px < bb.x1 + d and bb.y0 - d < py < bb.y1 + d
                    for px, py, d in obst if evita_curva or d > 1)
            # sem traço, o nome tem de ficar mais perto do próprio ponto que de qualquer outro
            if not traco and not bate:
                cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
                px0, py0 = tr.transform((x, y))
                d0 = (cx - px0) ** 2 + (cy - py0) ** 2
                bate = any((cx - px) ** 2 + (cy - py) ** 2 < d0 for px, py, d in obst
                           if d > 1 and (px, py) != (px0, py0))
            if traco and not bate:
                px0, py0 = tr.transform((x, y))
                cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 if off[1] > 0 else bb.y1)
                for t_ in np.linspace(0.15, 0.95, 12):
                    qx, qy = px0 + t_ * (cx - px0), py0 + t_ * (cy - py0)
                    if any(o_.x0 < qx < o_.x1 and o_.y0 < qy < o_.y1 for o_ in ocupado) or \
                            any(abs(qx - px) < 3 and abs(qy - py) < 3 for px, py, d in obst if d > 1):
                        bate = True
                        break
            if dentro and not bate:
                ocupado.append(bb.expanded(1.08, 1.15))
                feito = True
                break
            t.remove()
        if not feito:
            print("rótulo sem lugar livre:", f)
            t = ax.annotate(f, (x, y), xytext=(5, 1), textcoords="offset points", ha="left",
                            va="bottom", fontsize=6.3, color=INK_PRIMARY, zorder=6, bbox=fundo)
            ocupado.append(t.get_window_extent(rend))


XMIN_Q, XMAX_Q = 0.004, 45.0   # eixo x dos quadrantes: menor aumento A-H é ~0,007 dB, maior 11,5 dB
YMIN_E, YMAX_E = 1.4, 60.0      # energia por inversão das arquiteturas otimizadas: 1,75 a 32,5 uJ
YMIN_LOG, YMAX_LOG = 0.12, 7.0  # eixo y em log das figuras por condição (0,15 a 4,7 W)
YMIN_Q, YMAX_Q = 0.0, 5.25     # eixo y comum, linear: potência dinâmica de 0,37 a 4,7 W nos grupos 1 e 3
# arquitetura de cada perfil: a da condição mais exigente dele, que atende também as outras
ARQ_PERFIL = {"Low mobility": "TDLA30-75", "High mobility": "TDLB100-400"}
FAIXA_COR = ("#e6e5e0", "#fde3a7", "#f4c6c6")   # até 0,1 dB, 0,1 a 3 dB, acima de 3 dB (manual, seção 6)


def fundo_quadrantes(ax, hw, conds=None, esquerda=True, direita=True, xmin=None, ylog=False,
                     energia=False, rotulo_x=True):
    """Eixos, fundo em quatro regiões (até/acima de 0,1 dB x dinâmica abaixo/acima da estática),
    limiares de 0,1 e 3 dB e rótulos dos eixos, comuns aos planos de quadrantes."""
    ax.set_facecolor(SURFACE)
    for lado in ax.spines.values():
        lado.set_color(INK_MUTED)
        lado.set_linewidth(0.6)
    XMIN_Q = xmin or globals()["XMIN_Q"]
    ax.set_xscale("log")
    ax.set_xlim(XMIN_Q, XMAX_Q)
    # ylog: potência dinâmica em log (2026-11-15, a autora: pontos perto de 0,2-1 W difíceis de ver)
    ymin, ymax = (YMIN_LOG, YMAX_LOG) if ylog else (YMIN_Q, YMAX_Q)
    if energia:   # energia por inversão em log, sem linha da potência estática (2026-11-15)
        ymin, ymax = YMIN_E, YMAX_E
    if ylog:
        ax.set_yscale("log")
    ax.set_ylim(ymin, ymax)
    # divisão horizontal: potência estática do FPGA nas duas arquiteturas (total - dinâmica)
    conds = conds or list(ARQ_PERFIL.values())
    est = [custo(hw, c, f_)["estatica_w"] for c in conds for f_, *_ in FORMATOS if custo(hw, c, f_)]
    Y0 = sum(est) / len(est)
    # fundo nas faixas de perda do manual (seção 6), as mesmas de compromisso_formatos
    for (x0, x1), cor_f in zip(((XMIN_Q, 0.1), (0.1, 3.0), (3.0, XMAX_Q)), FAIXA_COR):
        ax.fill_between([x0, x1], ymin, ymax, color=cor_f, lw=0, zorder=0)
    ax.set_xticks([0.01, 0.1, 1, 3, 10], ["0.01", "0.1", "1", "3", "10"])
    ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(base=10, subs=(2, 5), numticks=20))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    marcas_y = [0.2, 0.5, 1, 2, 5] if ylog else [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    if energia:
        marcas_y = [2, 5, 10, 20, 50]   # 5 marcas, como na potência (a autora)
    ax.set_yticks(marcas_y, [f"{v:g}" for v in marcas_y])
    if ylog:
        ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.grid(True, axis="x", which="major", color=GRID_COR, lw=0.7, zorder=0.5)
    ax.grid(True, axis="x", which="minor", color=GRID_COR, lw=0.4, zorder=0.5)
    ax.grid(True, axis="y", which="major", color=GRID_COR, lw=0.6, zorder=0.5)
    ax.tick_params(labelsize=7, colors=INK_SECONDARY, length=2.5, width=0.6)
    ax.axvline(0.1, color=INK_PRIMARY, lw=0.9, zorder=2)
    if energia:
        direita = esquerda_estatica = False
    else:
        esquerda_estatica = esquerda
        ax.axhline(Y0, color=INK_PRIMARY, lw=0.9, zorder=2)
    meio = (lambda a, b: (a * b) ** 0.5) if ylog else (lambda a, b: (a + b) / 2)
    for y, t in ((meio(Y0, ymax), "dynamic > static"), (meio(Y0, ymin), "dynamic < static")):
        if not direita:
            break
        ax.text(1.02, y, t, rotation=90, ha="left", va="center", fontsize=6.5,
                color=INK_SECONDARY, transform=ax.get_yaxis_transform())
    if esquerda_estatica:
        # na faixa > 3 dB, à direita: à esquerda cruzava a linha de 0,1 dB e a da TDLA30-300 (2026-11-15)
        ax.annotate(f"static power,\n{min(est):.2f} to {max(est):.2f} W", (XMAX_Q / 1.15, Y0),
                    xytext=(0, 2), textcoords="offset points", ha="right", va="bottom", fontsize=6,
                    color=INK_SECONDARY, zorder=3)
    caixa = dict(boxstyle="square,pad=0.15", fc="none", ec="none")
    ax._cantos = [ax.text((XMIN_Q * 0.1) ** 0.5, ymax * 0.97 if ylog else ymax - 0.08, "≤ 0.1 dB", ha="center",
                          va="top", fontsize=7, color=INK_SECONDARY, bbox=caixa, zorder=3),
                  ax.text((0.1 * 3.0) ** 0.5, ymax * 0.97 if ylog else ymax - 0.08, "0.1 to 3 dB", ha="center",
                          va="top", fontsize=7, color=INK_SECONDARY, bbox=caixa, zorder=3),
                  ax.text((3.0 * XMAX_Q) ** 0.5, ymax * 0.97 if ylog else ymax - 0.08, "> 3 dB", ha="center", va="top",
                          fontsize=7, color=INK_SECONDARY, bbox=caixa, zorder=3)]
    if rotulo_x:
        ax.set_xlabel("SNR increase over BCD-MMSE float [dB]", fontsize=7.5, color=INK_SECONDARY)
    if esquerda:
        ax.set_ylabel("Energy per inversion [µJ]" if energia else "Dynamic power [W]",
                      fontsize=7.5, color=INK_SECONDARY)


# formatos no plano (manual, seção 5): formas bem diferentes; estrela e cruzes com área maior
MARCA_FMT = {"<18,8>": "*", "<20,8>": "^", "<22,12>": "s", "<24,12>": "d", "<26,12>": "o",
             "<28,14>": "P", "<30,14>": "X"}
AREA_FMT = {"*": 80, "^": 44, "s": 34, "d": 46, "o": 38, "P": 50, "X": 50}  # maiores a pedido (2026-11-09)
LIMITES_COND = (("3 dB", 3.0), ("0.1 dB", 0.1))


def escolha_cond(hw, g, cond, iot, limite):
    """Menor formato (ordem de FORMATOS, da menor palavra para a maior) que cabe na arquitetura da
    condição e cujo pior aumento entre as configurações daquele IoTh, naquela condição, fica até o
    limite. Mesmos dados da figura (grade inteira). (formato, aumento, potência dinâmica W),
    None se nenhum atende, 'pendente' se falta rodada antes de achar um."""
    for f, *_ in FORMATOS:
        v = custo(hw, cond, f, MODO_GRUPO[g][f])
        if v is None:
            continue
        r = pior(g, cond, f, iot=iot)
        if r == "pendente":
            return "pendente"
        # arredondado em duas casas, como na escolha dos formatos (decisão de 2026-11-09)
        if r is not None and round(r[0], 2) <= limite:
            return f, r[0], v["potencia_dinamica_w"]
    return None


XMIN_C, PISO_C = 0.0006, 0.001   # eixo x da figura por condição e piso dos aumentos


def figura_quadrantes_cond(hw, g):
    """Plano aumento de SNR x potência dinâmica com as seis condições de teste, um painel por IoTh
    (10 dB à esquerda, 20 dB à direita). Cada ponto é um formato numa condição: x = pior
    configuração do grupo com aquele IoTh, naquela condição; y = potência dinâmica do formato na
    arquitetura daquela condição (a modulação da pior fica só no CSV). Linha = todos os formatos
    da condição em ordem de bits (tracejada no low mobility, cheia no high mobility); círculo =
    formato escolhido para 3 dB e para 0,1 dB (escolha_cond)."""
    # 2026-11-15: linha de cima potência dinâmica, linha de baixo energia por inversão (a autora)
    # 2026-11-15: legenda numa coluna à direita, um item por linha (a autora)
    fig, axs2 = plt.subplots(2, 2, figsize=(LARGURA, 7.8), sharey="row", sharex=True,
                             facecolor=SURFACE)
    fig.subplots_adjust(left=0.08, right=0.775, top=0.945, bottom=0.065, wspace=0.07, hspace=0.12)
    axs = axs2[1]
    pn = paineis()
    linhas = []
    for linha_ax, chave in zip(axs2, ("potencia_dinamica_w", "energia_por_inversao_uj")):
      energia = chave == "energia_por_inversao_uj"
      for ax, iot in zip(linha_ax, (10, 20)):
        fundo_quadrantes(ax, hw, ORDEM, esquerda=iot == 10, direita=False, xmin=XMIN_C,
                         ylog=True, energia=energia, rotulo_x=energia)
        # piso de 0,001 dB: no IoTh 10 dB muitos aumentos ficam entre 0 e 0,004 dB (ruído)
        ax.set_xticks([PISO_C, 0.01, 0.1, 1, 3, 10], ["≤ 0.001", "0.01", "0.1", "1", "3", "10"])
        ax.tick_params(axis="x", labelbottom=True)   # números do eixo x também na linha de cima
        if not energia:
            ax.set_title(f"IoTh = {iot} dB", fontsize=8, color=INK_PRIMARY, pad=4)
        else:
            for t in ax._cantos:
                t.set_visible(False)
        for c in ORDEM:
            pts = []
            for f, *_ in FORMATOS:
                v = custo(hw, c, f, MODO_GRUPO[g][f])
                r = pior(g, c, f, iot=iot)
                mod = pn[r[1]].modulation if isinstance(r, tuple) else ""
                linhas.append([f"G{g}", iot, c, arq_da(c), f, chave,
                               "" if v is None else f"{v[chave]:.3f}",
                               "pendente" if r == "pendente" else
                               ("nao atinge" if r is None else f"{r[0]:.3f}"),
                               "" if not isinstance(r, tuple) else str(r[1]), mod])
                if isinstance(r, tuple) and v is not None:
                    pts.append((max(r[0], PISO_C), v[chave], f, mod))
            # 2026-11-15: sem Pareto (a autora); a linha liga todos os formatos em ordem de bits
            if len(pts) > 1:
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color=COR_COND[c], lw=1.4,
                        zorder=4, ls=(0, (3, 2)) if c in PERFIS["Low mobility"] else "-")
            # formatos escolhidos (menor formato até 3 dB e até 0,1 dB, Tabela escolha_condicao)
            escolhidos = set()
            for _, lim in LIMITES_COND:
                e = escolha_cond(hw, g, c, iot, lim)
                if isinstance(e, tuple):
                    escolhidos.add(e[0])
            for x, y, f, _ in pts:
                if f in escolhidos:
                    ax.scatter(x, y, s=120, marker="o",
                               facecolors="none", edgecolors=INK_PRIMARY, linewidths=1.0, zorder=6)
                ax.scatter(x, y, s=AREA_FMT[MARCA_FMT[f]], marker=MARCA_FMT[f],
                           facecolors=COR_COND[c], edgecolors=SURFACE, linewidths=0.5, zorder=5)
    fig.text(0.085, 0.995, titulo_grupo(g), ha="left", va="top", fontsize=8.5, color=INK_PRIMARY)
    # uma coluna por perfil, com o nome do perfil no topo (alça vazia) e o traço do perfil
    hc = []
    for perfil, ls in (("Low mobility", (0, (3, 2))), ("High mobility", "-")):
        hc.append(Line2D([], [], ls="", label=perfil))
        hc += [Line2D([], [], color=COR_COND[c], lw=1.4, ls=ls, label=c) for c in PERFIS[perfil]]
    hf = [Line2D([], [], ls="", marker=MARCA_FMT[f], ms=(AREA_FMT[MARCA_FMT[f]] ** 0.5) * 1.05,
                 mfc=INK_SECONDARY, mec=SURFACE, mew=0.5, label=f) for f, *_ in FORMATOS]
    hf.append(Line2D([], [], ls="", marker="o", ms=9, mfc="none", mec=INK_PRIMARY, mew=1.0,
                     label="best trade-off"))
    # rótulo da potência estática vai para a legenda (no gráfico, cobria pontos)
    rot_est = ""
    for t in list(axs2[0][0].texts):
        if t.get_text().startswith("static power"):
            rot_est = t.get_text().replace(",\n", ", ")
            t.remove()
    if rot_est:   # no gráfico de IoTh 20 dB, à esquerda e abaixo da linha: região sem pontos
        ax_e = axs2[0][1]
        y_est = None
        for l in ax_e.lines:   # a axhline da potência estática
            yd = l.get_ydata()
            if len(yd) == 2 and yd[0] == yd[1] and tuple(l.get_xdata()) == (0, 1):
                y_est = yd[0]
        ax_e.annotate(rot_est.replace(", ", ",\n"), (XMIN_C * 1.15, y_est), xytext=(0, -2),
                      textcoords="offset points", ha="left", va="top", fontsize=6,
                      color=INK_SECONDARY, zorder=3)
    quadro = dict(frameon=True, facecolor=SURFACE, edgecolor=INK_MUTED, framealpha=1,
                  fancybox=False, fontsize=7, labelcolor=INK_SECONDARY, alignment="left",
                  borderpad=0.6, borderaxespad=0, title_fontsize=7, handletextpad=0.4,
                  columnspacing=1.0)
    # os dois quadros numa coluna à direita dos gráficos, um item por linha
    x0, y = 0.79, axs2[0][1].get_position().y1
    l1 = fig.legend(handles=hc, loc="upper left", bbox_to_anchor=(x0, y),
                    ncol=1, handlelength=2.2, title="Test condition", **quadro)
    fig.canvas.draw()
    alt = l1.get_window_extent().transformed(fig.transFigure.inverted()).height
    l2 = fig.legend(handles=hf, loc="upper left", bbox_to_anchor=(x0, y - alt - 0.02), ncol=1,
                    handlelength=1.0, title="Format", **quadro)
    for t in l1.get_texts():
        if t.get_text() in PERFIS:
            t.set_color(INK_PRIMARY)
    fig.add_artist(l2)
    fag.salvar(fig, f"quadrantes_cond_g{g}", linhas,
               ["grupo", "ioth_db", "condicao", "arquitetura", "formato", "grandeza", "valor",
                "aumento_db_pior_configuracao", "configuracao_do_pior", "modulacao_do_pior"])


# ----------------------------------------------------------------------------- tabelas
def cab(*linhas):
    return r"\begin{tabular}[c]{@{}c@{}}" + r"\\".join(linhas) + r"\end{tabular}"


def ltx_fmt(f, m=None):
    s = f.replace("<", r"$\langle ").replace(">", r"\rangle$")
    return s + (r"$^{*}$" if m == TS else "")


# todas as combinações de formato e modo sintetizadas (o <18,8> nos dois modos)
FORMATOS_HW = [("<18,8>", RZW), ("<18,8>", TS), ("<20,8>", RZW), ("<22,12>", RZW),
               ("<24,12>", RZW), ("<26,12>", RZW), ("<28,14>", RZW), ("<30,14>", TS)]
ABREV = {RZW: "RND\\_ZERO/WRAP", TS: "TRN/SAT"}


def tabela_por_formato(hw, chave, casas, nome, legenda, caption, label):
    linhas = [r"\begin{tabular}{l" + "c" * len(FORMATOS_HW) + "}", r"\toprule",
              r"\textbf{Test condition} & " + " & ".join(
                  r"\textbf{" + ltx_fmt(f, m) + "}" for f, m in FORMATOS_HW) + r" \\",
              r"\midrule"]
    for cond in ORDEM:
        cel = [fmt_num(custo(hw, cond, f, m)[chave] if custo(hw, cond, f, m) else None, casas)
               for f, m in FORMATOS_HW]
        linhas.append(f"{cond} & " + " & ".join(cel) + r" \\")
    linhas.append(r"\midrule")
    for tam in ("16 x 16", "32 x 32"):
        cel = []
        for f, m in FORMATOS_HW:
            v = hw.get(("sem_otimizacao", f, m, tam))
            cel.append(fmt_num(v[chave] if v else None, casas))
        rot = tam.replace(" x ", r" $\times$ ")
        linhas.append(f"Without opt., {rot} & " + " & ".join(cel) + r" \\")
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever(nome, caption, label, linhas, legenda, sep="3pt")


def linha_recursos(rot, v, extra=""):
    cols = ["lut", "ff", "dsp", "bram_18k"]
    if not v or v["lut"] is None:
        return f"{rot} & " + " & ".join(["--"] * 6) + r" \\"
    cel = [f"{v[c]:,.0f} ({100 * v[c] / DISPOSITIVO[c]:.1f})" for c in cols]
    iv = v["intervalo_ciclos"]
    iv = "--" if iv is None else (f"{iv:,.0f}" if iv == int(iv) else f"{iv:,.1f}")
    cc = "--" if v["caminho_critico_ns"] is None else f"{v['caminho_critico_ns']:.2f}"
    return f"{rot} & " + " & ".join(cel) + f" & {cc} & {iv}" + r" \\"


def cabecalho_recursos(primeira):
    return [r"\begin{tabular}{lcccccc}", r"\toprule",
            r"\textbf{" + primeira + "} & " + " & ".join(r"\textbf{" + NOME_REC[c] + "}"
                                                     for c in ("lut", "ff", "dsp", "bram_18k"))
            + r" & " + cab(r"\textbf{Critical}", r"\textbf{path (ns)}") + " & "
            + cab(r"\textbf{Interval}", r"\textbf{(cycles)}") + r" \\", r"\midrule"]


def rot_fmt(f, m):
    return ltx_fmt(f) + " " + ABREV[m]


def tabela_recursos(hw):
    """Recursos de todas as arquiteturas otimizadas (16 x 16), em todos os formatos."""
    linhas = cabecalho_recursos("Format")
    for n, cond in enumerate(ORDEM):
        linhas.append(r"\multicolumn{7}{l}{\textbf{" + cond + f" (limit: {LIMITE[cond]:,} cycles)" + r"}} \\")
        for f, m in FORMATOS_HW:
            linhas.append(linha_recursos(rot_fmt(f, m), hw.get((arq_da(cond), f, m, "16 x 16"))))
        if n < len(ORDEM) - 1:
            linhas.append(r"\addlinespace")
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_recursos",
             r"Recursos, caminho crítico e intervalo entre inversões das arquiteturas otimizadas, por formato.",
             "tab:recursos", linhas,
             "Fonte: a autora. $16 \\times 16$. Entre parênteses, porcentagem do XCU50. BRAM de 18~Kb. --: não cabe no FPGA.",
             sep="3pt", fonte=r"\scriptsize", posicao="p", esticar="1.0")


def tabela_recursos_sem_otimizacao(hw):
    """Recursos da versão sem otimização, 16 x 16 e 32 x 32."""
    linhas = cabecalho_recursos("Format")
    for n, tam in enumerate(("16 x 16", "32 x 32")):
        linhas.append(r"\multicolumn{7}{l}{\textbf{" + tam.replace(" x ", r" $\times$ ") + r"}} \\")
        for f, m in FORMATOS_HW:
            linhas.append(linha_recursos(rot_fmt(f, m), hw.get(("sem_otimizacao", f, m, tam))))
        if n == 0:
            linhas.append(r"\addlinespace")
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_recursos_sem_otimizacao",
             r"Recursos, caminho crítico e intervalo entre inversões da versão sem otimização, por formato.",
             "tab:recursos-sem-otimizacao", linhas,
             "Fonte: a autora. Entre parênteses, a porcentagem do XCU50. BRAM em blocos de 18~Kb. "
             "--: sem medida.", sep="3pt", fonte=r"\scriptsize")


def tabela_faixa(hw):
    """Melhor e pior caso entre os formatos: menor e maior valor de cada coluna, por arquitetura."""
    cols = ["lut", "ff", "dsp", "bram_18k"]
    linhas = [r"\begin{tabular}{lccccccc}", r"\toprule",
              r"\textbf{Test condition} & " + " & ".join(r"\textbf{" + NOME_REC[c] + r" (\%)}" for c in cols)
              + r" & " + cab(r"\textbf{Critical}", r"\textbf{path (ns)}") + " & "
              + cab(r"\textbf{Interval}", r"\textbf{(cycles)}") + " & "
              + cab(r"\textbf{Limit}", r"\textbf{(cycles)}") + r" \\", r"\midrule"]

    def faixa(vs, fmt):
        a, b = min(vs), max(vs)
        return fmt(a) if fmt(a) == fmt(b) else f"{fmt(a)}--{fmt(b)}"

    def ciclos(x):
        return f"{x:,.0f}" if x == int(x) else f"{x:,.1f}"

    def linha(rot, arq, tam, lim):
        vs = [v for (ar, f, m, t), v in hw.items() if ar == arq and t == tam and v["lut"] is not None]
        cel = [faixa([100 * v[c] / DISPOSITIVO[c] for v in vs], lambda x: f"{x:.1f}") for c in cols]
        cel.append(faixa([v["caminho_critico_ns"] for v in vs], lambda x: f"{x:.2f}"))
        cel.append(faixa([v["intervalo_ciclos"] for v in vs if v["intervalo_ciclos"]], ciclos))
        return f"{rot} & " + " & ".join(cel) + f" & {lim}" + r" \\"
    for cond in ORDEM:
        linhas.append(linha(cond, arq_da(cond), "16 x 16", f"{LIMITE[cond]:,}"))
    linhas.append(r"\midrule")
    linhas.append(linha(r"Without opt., 16 $\times$ 16", "sem_otimizacao", "16 x 16", "--"))
    linhas.append(linha(r"Without opt., 32 $\times$ 32", "sem_otimizacao", "32 x 32", "--"))
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_recursos_faixa",
             "Menor e maior uso de recursos, caminho crítico e intervalo entre inversões de cada arquitetura, entre os formatos.",
             "tab:recursos-faixa", linhas,
             "Fonte: a autora. Recursos em porcentagem do XCU50. Em quase todos os casos, o menor valor vem do "
             "$\\langle 18,8\\rangle$ e o maior, do $\\langle 30,14\\rangle$ ($\\langle 28,14\\rangle$ na TDLB100-400). "
             "O caminho crítico não segue essa ordem. "
             "Em $32 \\times 32$, sem o intervalo do $\\langle 18,8\\rangle$ e do $\\langle 20,8\\rangle$, que não foram medidos.",
             sep="2pt")


def tabela_mais_usado(hw):
    """Recurso mais usado (% do dispositivo) por formato e arquitetura."""
    ab = {"lut": "L", "ff": "F", "dsp": "D", "bram_18k": "B"}
    linhas = [r"\begin{tabular}{l" + "c" * len(FORMATOS_HW) + "}", r"\toprule",
              r"\textbf{Test condition} & " + " & ".join(
                  r"\textbf{" + ltx_fmt(f, m) + "}" for f, m in FORMATOS_HW) + r" \\",
              r"\midrule"]
    for cond in ORDEM:
        cel = []
        for f, m in FORMATOS_HW:
            v = hw.get((arq_da(cond), f, m, "16 x 16"))
            if not v or v["lut"] is None:
                cel.append("--")
                continue
            k = max(DISPOSITIVO, key=lambda c: v[c] / DISPOSITIVO[c])
            cel.append(f"{100 * v[k] / DISPOSITIVO[k]:.1f} ({ab[k]})")
        linhas.append(f"{cond} & " + " & ".join(cel) + r" \\")
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_recurso_mais_usado",
             "Recurso mais usado do XCU50, em porcentagem, por formato e arquitetura.",
             "tab:recurso-mais-usado", linhas,
             "Fonte: a autora. Entre parênteses, o recurso: L = LUT, D = DSP, B = BRAM. "
             r"$^{*}$\texttt{AP\_TRN}/\texttt{AP\_SAT}; os outros, \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. "
             r"--: não cabe no FPGA.")


def tabela_compromisso(hw):
    """Formatos escolhidos dos grupos 1 e 3: pior aumento e potência dinâmica em cada condição."""
    n = 3 + len(ORDEM)
    linhas = [r"\begin{tabular}{llc" + "c" * len(ORDEM) + "}", r"\toprule",
              r"\textbf{Criterion} & \textbf{Format} & " + cab(r"\textbf{Worst}", r"\textbf{(dB)}")
              + " & " + " & ".join(cab(r"\textbf{" + c.split("-")[0] + "-}", r"\textbf{" + c.split("-")[1] + "}")
                                for c in ORDEM) + r" \\", r"\midrule"]
    rot_crit = {"Reaches": r"Reaches $10^{-2}$", "3 dB": "Up to 3 dB", "0.1 dB": "Up to 0.1 dB"}
    titulos = {"A-H": "all configurations (A to H)", "A-D": "IoTh of 10~dB (A to D)"}
    resumo = []
    blocos = [(g, sub) for sub in ("A-H", "A-D") for g in (1, 3)]
    for b, (g, subset) in enumerate(blocos):
        linhas.append(r"\multicolumn{" + str(n) + r"}{l}{\textbf{Group " + str(g) + ", "
                      + titulos[subset] + r"}} \\")
        for j, crit in enumerate(CRITERIOS):
            f = ESCOLHIDOS[subset][g][j]
            r = pior_todas(g, f, subset == "A-D")
            pw = [custo(hw, c, f, MODO_GRUPO[g][f]) for c in ORDEM]
            cel = [fmt_num(v["potencia_dinamica_w"] if v else None, 2) for v in pw]
            sr = "pend." if r == "pendente" else ("--" if r is None else f"{r[0]:.2f}")
            linhas.append(f"{rot_crit[crit]} & {ltx_fmt(f, MODO_GRUPO[g][f])} & {sr} & "
                          + " & ".join(cel) + r" \\")
            resumo.append((subset, g, crit, f, r, pw))
        if b < len(blocos) - 1:
            linhas.append(r"\midrule" if b == 1 else r"\addlinespace")
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_compromisso",
             "Pior aumento de SNR e potência dinâmica, em W, dos formatos escolhidos nos grupos 1 e 3.",
             "tab:compromisso", linhas,
             "Fonte: a autora. Pior aumento de SNR entre as configurações e as condições de teste do grupo. "
             "Potência dinâmica da arquitetura de cada condição de teste, em $16 \\times 16$. "
             r"$^{*}$\texttt{AP\_TRN}/\texttt{AP\_SAT}; os outros, \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. "
             r"--: não cabe no FPGA.",
             sep="2.7pt")
    return resumo


def escrever(nome, caption, label, corpo, legenda, sep="4pt", fonte=r"\footnotesize", posicao="htbp", esticar="1.2"):
    TABELAS.mkdir(parents=True, exist_ok=True)
    txt = "\n".join([r"\begin{table}[" + posicao + "]", r"\caption{\textcolor{red}{" + caption + "}}",
                     r"\label{" + label + "}",
                     r"\vspace{4pt} % a classe zera o espaço entre a caption e a tabela",
                     r"\centering", fonte, r"\color{red}",
                     r"\renewcommand{\arraystretch}{" + esticar + "}", r"\setlength{\tabcolsep}{" + sep + "}",
                     *corpo, r"\vspace{4pt}", r"\legend{\textcolor{red}{" + legenda + "}}",
                     r"\end{table}", ""])
    (TABELAS / f"{nome}.tex").write_text(txt)


def tabela_escolha_condicao(hw):
    """Formato escolhido em cada condição de teste (opção b): para cada grupo, IoTh e limite, o
    menor formato que cabe na arquitetura da condição e fica até o limite (escolha_cond), com o
    pior aumento e a potência dinâmica. Linhas agrupadas por perfil de mobilidade."""
    n = 1 + 12
    sub = r"\textbf{Format} & \textbf{dB} & \textbf{W}"
    linhas = [r"\begin{tabular}{l" + "ccc" * 4 + "}", r"\toprule",
              r" & \multicolumn{6}{c}{\textbf{IoTh of 10~dB (A to D)}} & "
              r"\multicolumn{6}{c}{\textbf{IoTh of 20~dB (E to H)}} \\",
              r"\cmidrule(lr){2-7}\cmidrule(lr){8-13}",
              r" & " + " & ".join([r"\multicolumn{3}{c}{\textbf{Up to 3 dB}}",
                                   r"\multicolumn{3}{c}{\textbf{Up to 0.1 dB}}"] * 2) + r" \\",
              r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}\cmidrule(lr){11-13}",
              r"\textbf{Test condition} & " + " & ".join([sub] * 4) + r" \\", r"\midrule"]
    for k, g in enumerate((1, 3)):
        M, C = GRUPOS[g]
        linhas.append(r"\multicolumn{" + str(n) + r"}{l}{\textbf{Group " + str(g) +
                      f" ($M$ = {M}, $C$ = {C})" + r"}} \\")
        for perfil, conds in PERFIS.items():
            linhas.append(r"\multicolumn{" + str(n) + r"}{l}{" + perfil + r"} \\")
            for c in conds:
                cel = []
                for iot in (10, 20):
                    for _, lim in LIMITES_COND:
                        e = escolha_cond(hw, g, c, iot, lim)
                        if e == "pendente":
                            cel += ["pend.", "", ""]
                        elif e is None:
                            cel += ["--", "--", "--"]
                        else:
                            f, d, w = e
                            cel += [ltx_fmt(f, MODO_GRUPO[g][f]),
                                    "$<$ 0.01" if d < 0.005 else f"{d:.2f}", f"{w:.2f}"]
                linhas.append(r"\quad " + c + " & " + " & ".join(cel) + r" \\")
        if k == 0:
            linhas.append(r"\midrule")
    linhas += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_escolha_condicao",
             "Formato de melhor compromisso em cada condição de teste, com o pior aumento de SNR, em dB, e a "
             "potência dinâmica, em W.",
             "tab:escolha-condicao", linhas,
             "Fonte: a autora. Menor formato que cabe na arquitetura da condição de teste e cujo "
             "pior aumento de SNR, entre as configurações com aquele IoTh, fica até o limite. "
             # só fala do asterisco se algum formato TRN/SAT foi escolhido (texto de 2026-11-09)
             + (r"$^{*}$\texttt{AP\_TRN}/\texttt{AP\_SAT}; os outros, \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. "
                if any("^{*}" in l for l in linhas) else r"Modo \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. ")
             + "--: nenhum formato que cabe no FPGA atende o limite.",
             sep="2.2pt", fonte=r"\scriptsize")


def tabela_perfis(hw):
    """Menor formato (menor W) que fica dentro do limite em todas as condições do perfil e
    cabe em todas as arquiteturas dele; pior aumento no perfil e potência relativa ao <24,12>."""
    def escolha(g, perfil, lim, so10):
        for f, *_ in FORMATOS:
            r = pior_perfil(g, perfil, f, so10)
            if r == "pendente":
                return "pendente"
            if not isinstance(r, tuple) or round(r[0], 2) > lim:
                continue
            if any(custo(hw, c, f, MODO_GRUPO[g][f]) is None for c in PERFIS[perfil]):
                continue
            return f, r[0], potencia_relativa(hw, g, f)[0]
        return None

    def cel(e):
        if e == "pendente":
            return r"\multicolumn{3}{c}{pendente}"
        if e is None:
            return r"\multicolumn{3}{c}{nenhum}"
        f, v, p = e
        return f"{ltx_fmt(f)} & {v:.2f} & {100 * p:.0f}"

    corpo = [r"\begin{tabular}{lll ccc ccc}", r"\toprule",
             r" & & & \multicolumn{3}{c}{\textbf{Até 3 dB}} & \multicolumn{3}{c}{\textbf{Até 0,1 dB}} \\",
             r"\cmidrule(lr){4-6}\cmidrule(lr){7-9}",
             r"\textbf{Grupo} & \textbf{Configurações} & \textbf{Perfil} & \textbf{Formato} & "
             r"\textbf{Pior (dB)} & \textbf{Pot. (\%)} & \textbf{Formato} & \textbf{Pior (dB)} & "
             r"\textbf{Pot. (\%)} \\", r"\midrule"]
    for g in (1, 3):
        for so10 in (False, True):
            for perfil in PERFIS:
                corpo.append(f"G{g} & {'A a D' if so10 else 'A a H'} & "
                             f"{'Lento' if perfil.startswith('Low') else 'Rápido'} & "
                             f"{cel(escolha(g, perfil, 3, so10))} & {cel(escolha(g, perfil, 0.1, so10))} \\\\")
        if g == 1:
            corpo.append(r"\midrule")
    corpo += [r"\bottomrule", r"\end{tabular}"]
    escrever("tabela_perfis", "Formato mais econômico por perfil de mobilidade.", "tab:formato-perfil",
             corpo, "Fonte: a autora. Formato de menor largura que fica dentro do limite em todas as "
             "condições de teste do perfil e cabe nas arquiteturas dele. Pior: maior aumento de SNR "
             "nas condições do perfil, arredondado para duas casas. Pot.: potência dinâmica relativa ao "
             r"$\langle 24,12\rangle$ na mesma arquitetura, média das arquiteturas otimizadas. "
             "Pendente: falta a rodada na grade inteira.")


# ----------------------------------------------------------------------------- resumo
def resumo_txt(hw, comp):
    s = []
    p = s.append
    p("== Formatos escolhidos: custo de 3 dB -> 0,1 dB (e de IoTh 10 dB) por condição")
    for subset in ("A-H", "A-D"):
        for g in (1, 3):
            f3, f01 = ESCOLHIDOS[subset][g][1], ESCOLHIDOS[subset][g][2]
            r3, r01 = pior_todas(g, f3, subset == "A-D"), pior_todas(g, f01, subset == "A-D")
            p(f"{subset} G{g}: {f3} (pior {r3}) -> {f01} (pior {r01})")
            for c in ORDEM:
                a, b = custo(hw, c, f3, MODO_GRUPO[g][f3]), custo(hw, c, f01, MODO_GRUPO[g][f01])
                if a and b:
                    p(f"   {c:12s} din {a['potencia_dinamica_w']:.3f} -> {b['potencia_dinamica_w']:.3f} W "
                      f"({100 * (b['potencia_dinamica_w'] / a['potencia_dinamica_w'] - 1):+.0f} %); "
                      f"E {a['energia_por_inversao_uj']:.2f} -> {b['energia_por_inversao_uj']:.2f} uJ "
                      f"({100 * (b['energia_por_inversao_uj'] / a['energia_por_inversao_uj'] - 1):+.0f} %); "
                      f"media {a['media_w']:.2f} -> {b['media_w']:.2f} W "
                      f"({100 * (b['media_w'] / a['media_w'] - 1):+.1f} %), estatica {100 * a['estatica_w'] / a['media_w']:.0f} %")
                else:
                    p(f"   {c:12s} sem hardware ({f3 if not a else f01})")
    p("\n== IoTh 10 dB (A-D) x todas (A-H), mesmo critério")
    for g in (1, 3):
        for j, crit in enumerate(CRITERIOS):
            fa, fd = ESCOLHIDOS["A-H"][g][j], ESCOLHIDOS["A-D"][g][j]
            ds = []
            for c in ORDEM:
                a, b = custo(hw, c, fa, MODO_GRUPO[g][fa]), custo(hw, c, fd, MODO_GRUPO[g][fd])
                if a and b:
                    ds.append(f"{c} {100 * (b['potencia_dinamica_w'] / a['potencia_dinamica_w'] - 1):+.0f}%")
            p(f"G{g} {crit}: {fa} -> {fd}: " + ", ".join(ds))
    p("\n== Escolha por condição (cada condição já tem a sua arquitetura): menor formato com "
      "hardware que cumpre o limite na condição")
    for subset in ("A-H", "A-D"):
        for g in (1, 3):
            for lim_nome, lim in (("3 dB", 3), ("0.1 dB", 0.1)):
                j = CRITERIOS.index(lim_nome)
                fg = ESCOLHIDOS[subset][g][j]
                partes = []
                for c in ORDEM:
                    esc = None
                    for f, *_ in FORMATOS:
                        r = pior(g, c, f, subset == "A-D")
                        if r == "pendente":
                            esc = "pend:" + f
                            break
                        if isinstance(r, tuple) and round(r[0], 2) <= lim:
                            esc = f
                            break
                    if esc and not esc.startswith("pend") and esc != fg:
                        a, b = custo(hw, c, fg, MODO_GRUPO[g][fg]), custo(hw, c, esc, MODO_GRUPO[g][esc])
                        dd = (f" din {a['potencia_dinamica_w']:.3f}->{b['potencia_dinamica_w']:.3f} W"
                              f" ({100 * (b['potencia_dinamica_w'] / a['potencia_dinamica_w'] - 1):+.0f}%)"
                              if a and b else "")
                        partes.append(f"{c}: {esc}{dd}")
                    else:
                        partes.append(f"{c}: {esc}")
                p(f"{subset} G{g} {lim_nome} (grupo: {fg}): " + "; ".join(partes))
    p("\n== Potência estática e fração estática na média, <24,12>")
    for c in ORDEM:
        v = custo(hw, c, "<24,12>")
        p(f"{c:12s} est {v['estatica_w']:.3f} W, din {v['potencia_dinamica_w']:.3f} W, media "
          f"{v['media_w']:.3f} W ({100 * v['estatica_w'] / v['media_w']:.0f} % estatica), ocupacao do tempo "
          f"{v['intervalo_ciclos'] / LIMITE[c]:.2f}, mais usado {NOME_REC[v['mais_usado']]} {v['mais_usado_pct']:.1f} %")
    p("\n== Inclinação: potência dinâmica por bit (de <18,8> a <28,14>, RND_ZERO/WRAP)")
    for c in ORDEM:
        a, b = custo(hw, c, "<18,8>"), custo(hw, c, "<28,14>")
        p(f"{c:12s} {(b['potencia_dinamica_w'] - a['potencia_dinamica_w']) / 10 * 1e3:.0f} mW/bit, "
          f"razao {b['potencia_dinamica_w'] / a['potencia_dinamica_w']:.2f}")
    (TABELAS / "resumo.txt").write_text("\n".join(s) + "\n")
    print("\n".join(s))


def main():
    hw = ler_hw()
    figura_potencia_formatos(hw)
    figura_aumento_perfis()
    for g in (1, 3):        # o G2 (32 x 32) não tem arquitetura que atenda o ritmo de nenhuma condição
        figura_quadrantes_cond(hw, g)
    tabela_por_formato(hw, "potencia_dinamica_w", 3, "tabela_potencia_dinamica",
                       "Fonte: a autora. Arquitetura de cada condição de teste em $16 \\times 16$. "
                       r"$^{*}$\texttt{AP\_TRN}/\texttt{AP\_SAT}; os outros, \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. "
                       "--: sem medida ou não cabe no FPGA.",
                       "Potência dinâmica, em W, por formato e arquitetura.", "tab:potencia-dinamica")
    tabela_por_formato(hw, "energia_por_inversao_uj", 2, "tabela_energia_inversao",
                       "Fonte: a autora. Cálculo na Seção~\\ref{subsec:hw-potencia}. "
                       r"$^{*}$\texttt{AP\_TRN}/\texttt{AP\_SAT}; os outros, \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. "
                       "--: sem medida ou não cabe no FPGA.",
                       "Energia por inversão, em $\\mu$J, por formato e arquitetura.", "tab:energia-inversao")
    tabela_recursos(hw)
    tabela_recursos_sem_otimizacao(hw)
    tabela_faixa(hw)
    tabela_mais_usado(hw)
    tabela_perfis(hw)
    tabela_escolha_condicao(hw)
    comp = tabela_compromisso(hw)
    resumo_txt(hw, comp)


if __name__ == "__main__":
    main()
