#!/usr/bin/env python3
"""
Perda total do BCD-MMSE (1 iteração) com a inversa em ponto fixo para o LMMSE, dividida em
duas partes, em SER = 1e-2:

- perda da descentralização = SNR do BCD-MMSE em float - SNR do LMMSE (float);
- perda do formato = SNR do BCD-MMSE no formato - SNR do BCD-MMSE em float (a mesma perda
  dos mapas de modo fixo).

Barra empilhada: o zero é uma base de verdade (é uma perda, não uma SNR). Os formatos
<22,12> e <24,12> lado a lado (colunas, mesmo eixo x), um painel por grupo (G1 16-QAM, G1 QPSK, G2, G3), todos no mesmo cenário:
TDLA30-5 por padrão (N = 192, o N padrão do artigo; os 4 cenários com N de 132 a 192 dão
quase o mesmo resultado). O eixo x é o mesmo em todos os painéis, para comparar os grupos.

Quando o LMMSE já está abaixo de 1e-2 em -10 dB, a SNR dele é presa em -10 dB e a perda da
descentralização é só um limite inferior: a parte azul fica hachurada (quase todo o G1
QPSK). Os valores de todos os grupos e cenários vão em tabela_descentralizacao_formato.csv.

Saída: resultados/5_candidatos/modo_fixo_3dB/figuras/descentralizacao/ (png, pdf, _data.csv).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_descentralizacao.py [--cenario TDLB100-400] [--com-28-14]
    ../simulador/.venv/bin/python figuras_descentralizacao.py --tcc

Com --tcc: uma figura por grupo (figura_grupo_tcc), com os formatos escolhidos do grupo e o
mesmo eixo x nas três, em TCC/Images/RESULTADOS/descentralizacao_grupo<g>.pdf.
A parte do formato, quase sempre fina demais para ver, vai escrita em azul na ponta da barra.
"""

import argparse
import csv
import json
from functools import lru_cache

import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
from matplotlib import transforms
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle

import figuras_analise_grupos as fag
from dbp_sim.params import QPSK_256_PANELS
from figuras_formatos import ALVO, snr_no_alvo
from mapa_grupos_v4 import LETRAS_NOVAS
from pathlib import Path

from figuras_analise_grupos import legenda_quadro
from figuras_analise_grupos import (ALL_PANELS, CENARIOS, FORMATOS, INK_MUTED, INK_PRIMARY,
                                    INK_SECONDARY, LARGURA, LETRAS, PASTA, SURFACE,
                                    TCC_CONFIGURATION, carregar, eixos, estado_snr, num,
                                    perda, salvar)

PAINEIS = {TCC_CONFIGURATION[p.label]: p for p in ALL_PANELS + QPSK_256_PANELS}
# <18,8>: formato escolhido só com IoTh de 10 dB no grupo 1 (fora da [5])
FORMATOS = {**FORMATOS, (8, 10): ("<18,8>", "AP_RND_ZERO_AP_WRAP", "18-8")}
# QPSK dos grupos 2 e 3 (17 a 24): só nas figuras do TCC. O LMMSE e o BCD-MMSE em float vêm
# de curvas_qpsk_256 (grade de -20 a 10 dB); a parte do formato vem da grade inteira
# (modo_fixo_3dB_qpsk_256) quando ela existe, senão da [4] v5 (grade curta, a do mapa)
LETRAS = {**LETRAS, **LETRAS_NOVAS}
QPSK_256 = {"G2": range(17, 21), "G3": range(21, 25)}
REF_QPSK_256 = PASTA.parents[1] / "1_referencia_float" / "curvas_qpsk_256"
DADOS_V5 = PASTA.parents[1] / "4_varredura_formatos" / "v5_qpsk_grupos_2_3" / "dados"
# grade inteira (-20 a 10 dB) das rodadas modo_fixo_3dB_qpsk_256; a v5 fica como reserva
INTEIRA_QPSK_256 = PASTA.parent / "modo_fixo_3dB_qpsk_256" / "dados"
ESTACAO = {"G1": (128, 8), "G2": (256, 8), "G3": (256, 16)}
# formato = azul do mapa de perda (o ponto fixo é azul em todas as figuras principais);
# descentralização = cinza quente, como contexto. validate_palette.js: CVD pior 24,7,
# visão normal 28,8 (o cinza falha só no piso de croma, de propósito).
COR_DESC = "#eda100"   # amarelo forte: BCD-MMSE (escolha da autora, 2026-11-02)
COR_FMT = "#1c5cab"
# A parte do formato segue o degradê do mapa de pior aumento de SNR (mapa_cenarios_v4.py):
# a mesma cor quer dizer o mesmo valor em dB nas duas figuras
from mapa_cenarios_v4 import DEGRADE, FAIXA, NORMA


def cor_formato(f):
    return DEGRADE(NORMA(max(f, NORMA.vmin)))


class AlcaDegrade(HandlerBase):
    """Alça da legenda com o degradê do mapa em três faixas (0,01, 0,1 e 1 dB)."""

    def create_artists(self, legend, orig, x0, y0, w, h, fontsize, trans):
        return [Rectangle((x0 + i * w / 3, y0), w / 3, h, facecolor=cor_formato(v),
                          edgecolor="none", transform=trans)
                for i, v in enumerate((0.01, 0.1, 1))]
ALTURA_BARRA = 0.72
# limite inferior = hachura (a autora preferiu à textura de pontos)
TEXTURA_LIMITE = "////"
GRUPOS = (("G1", "16QAM"), ("G1", "QPSK"), ("G2", None), ("G3", None))
# textos da figura em inglês, com ponto decimal (pedido da autora, 2026-11-02)
CENARIO_EN = {"TDLA30-5": "TDLA30-5 and TDLA30-10, $N$ = 192, 3.5 GHz",
              "TDLA30-75": "TDLA30-75, $N$ = 192, 28 GHz",
              "TDLA30-300": "TDLA30-300, $N$ = 168, 28 GHz",
              "TDLC300-100": "TDLC300-100, $N$ = 132, 3.5 GHz",
              "TDLB100-400": "TDLB100-400, $N$ = 24, 3.5 GHz"}
# fonte padrão do matplotlib, sem negrito e sem itálico nas letras de fórmula
plt.rcParams["mathtext.default"] = "regular"


def ponto(v, casas=1):
    return f"{v:.{casas}f}"


def configs(g, mod):
    ks = list({"G1": range(1, 9), "G2": range(9, 13), "G3": range(13, 17)}[g])
    if mod:
        ks = [k for k in ks + list(QPSK_256.get(g, ())) if PAINEIS[k].modulation == mod]
    # IoTh 10 antes de IoTh 20; dentro de cada IoTh, K = 8 antes de K = 12
    return sorted(ks, key=lambda k: (PAINEIS[k].iot_db, PAINEIS[k].K))


def partes(r, fmt):
    xl, el = estado_snr(r["LMMSE"])
    xb, _ = estado_snr(r["BCD"])
    f, f_lim = perda(r, fmt)
    return xb - xl, el == "abaixo", f, f_lim


# QPSK do grupo 1 (5 a 8) a partir de -20 dB (rodada5_qpsk_128.sh): usado quando a rodada
# terminou (FIM); antes, o grupo 1 usa a [1] e a [5] (grade -10 a 10, LMMSE limite inferior)
REF_QPSK_128 = PASTA.parents[1] / "1_referencia_float" / "curvas_qpsk_128"
INTEIRA_QPSK_128 = PASTA.parent / "modo_fixo_3dB_qpsk_128"
QPSK_128 = (5, 6, 7, 8)


def usa_qpsk_128(k):
    return k in QPSK_128 and (INTEIRA_QPSK_128 / "FIM").exists()


@lru_cache(maxsize=None)
def partes_qpsk_256(cenario, k, fmt):
    """partes() para as configurações 17 a 24 (e 5 a 8, com usa_qpsk_128), cada parte na
    grade da sua simulação."""
    ref_dir = REF_QPSK_128 if k in QPSK_128 else REF_QPSK_256
    pasta = next(p for p in ref_dir.iterdir()
                 if cenario in p.name.split("_")[0].split("+"))
    ref = json.loads((pasta / "bcd_iterations_results.json").read_text())
    r = ref[PAINEIS[k].label]
    d = (snr_no_alvo(ref["snr_db"], r[fag.BCD1])
         - snr_no_alvo(ref["snr_db"], r["LMMSE"]))
    _, modo, _ = FORMATOS[fmt]
    nome = f"{fmt[0]}_{fmt[1]}_{modo}.json"
    inteira = ((INTEIRA_QPSK_128 / "dados") if k in QPSK_128 else INTEIRA_QPSK_256) \
        / cenario / f"configuracao_{k}" / nome
    if not inteira.exists():
        # formatos que só a rodada 6 tem na grade inteira (o <26,12> do grupo 1 com QPSK)
        inteira = PASTA.parent / "modo_fixo_mapa" / "dados" / cenario / f"configuracao_{k}" / nome
    if inteira.exists():
        # grade inteira, mesma semente da referência: como a [5] das configurações 1 a 16
        sh = json.loads(inteira.read_text())["ser"][fag.BCD1]
        xb = snr_no_alvo(ref["snr_db"], r[fag.BCD1])
        xh = snr_no_alvo(ref["snr_db"], sh)
        f = None if xb is None or xh is None else max(0.0, xh - xb)
        f_lim = f is not None and r[fag.BCD1][0] < ALVO and sh[0] >= ALVO
        return d, r["LMMSE"][0] < ALVO, f, f_lim
    v5 = json.loads((DADOS_V5 / cenario / f"configuracao_{k}" / nome).read_text())
    sr, sh = v5["ser_referencia"][fag.BCD1], v5["ser"][fag.BCD1]
    xr, xh = snr_no_alvo(v5["snr_db"], sr), snr_no_alvo(v5["snr_db"], sh)
    f = None if xr is None or xh is None else max(0.0, xh - xr)
    f_lim = f is not None and sr[0] < ALVO and sh[0] >= ALVO
    return d, r["LMMSE"][0] < ALVO, f, f_lim


IOT10 = PASTA.parent / "modo_fixo_3dB_iot10" / "dados"   # <18,8> na grade inteira
V4_DADOS = PASTA.parents[1] / "4_varredura_formatos" / "v4_formatos_juntos_16_configs" / "dados"
_cache_perto = {}


def partes_perto(ser, cenario, k, fmt):
    """partes() de um formato fora da [5] (o <18,8>): o ponto fixo vem da rodada
    modo_fixo_3dB_iot10 (grade inteira) quando ela existe; senão da [4] v4 (grade curta, a do
    mapa, com a referência float simulada junto)."""
    chave = (cenario, k, fmt)
    if chave not in _cache_perto:
        r = ser[(cenario, k)]
        xl, el = estado_snr(r["LMMSE"])
        xb, eb = estado_snr(r["BCD"])
        nome = f"{fmt[0]}_{fmt[1]}_{FORMATOS[fmt][1]}.json"
        arq = IOT10 / cenario / f"configuracao_{k}" / nome
        if arq.exists():
            sh = json.loads(arq.read_text())["ser"][fag.BCD1]
            xf = snr_no_alvo(fag.GRADE, sh)
            f = None if xf is None or xb is None else max(0.0, xf - xb)
            f_lim = f is not None and eb == "abaixo" and sh[0] >= ALVO
        else:
            j = json.loads((V4_DADOS / cenario / f"configuracao_{k}" / nome).read_text())
            sr, sh = j["ser_referencia"][fag.BCD1], j["ser"][fag.BCD1]
            xr, xf = snr_no_alvo(j["snr_db"], sr), snr_no_alvo(j["snr_db"], sh)
            f = None if xr is None or xf is None else max(0.0, xf - xr)
            f_lim = f is not None and sr[0] < ALVO and sh[0] >= ALVO
        _cache_perto[chave] = (xb - xl, el == "abaixo", f, f_lim)
    return _cache_perto[chave]


def partes_k(ser, cenario, k, fmt):
    if (k in PAINEIS and k >= 17) or usa_qpsk_128(k):
        return partes_qpsk_256(cenario, k, fmt)
    if fmt not in ser[(cenario, k)]:
        return partes_perto(ser, cenario, k, fmt)
    return partes(ser[(cenario, k)], fmt)


# Faixas de IoTh e K à esquerda das letras, como as do mapa de perda: x em pontos a partir
# da borda esquerda do painel (não depende da largura dele); (início, largura) de cada coluna
COLUNAS_FAIXA = (("IoTh", -94, 42), ("$K$", -46, 26))
# versão do TCC (chave=True): colunas estreitas, IoTh só com o número (unidade no cabeçalho)
COLUNAS_CHAVE = (("IoTh\n[dB]", -58, 22), ("$K$", -34, 16))


def faixas_esquerda(ax, ks, cabecalho, chave=False):
    """IoTh e K de cada barra em caixas cinza (FAIXA do mapa), juntando as barras seguidas
    com o mesmo valor; K não passa da divisa do IoTh, como no mapa. A ordem não muda.
    Com chave=True, em vez da caixa, uma linha fina vertical à direita do texto, com as
    pontas dobradas para a esquerda (como as chaves embaixo do mapa no TCC)."""
    fig = ax.figure
    tx = (transforms.Affine2D().scale(1 / 72) + fig.dpi_scale_trans
          + transforms.ScaledTranslation(0, 0, ax.transAxes))
    trans = transforms.blended_transform_factory(tx, ax.transData)
    atributos = ([f"{PAINEIS[k].iot_db:g}" if chave else f"{PAINEIS[k].iot_db:g} dB"
                  for k in ks], [str(PAINEIS[k].K) for k in ks])
    colunas_faixa = COLUNAS_CHAVE if chave else COLUNAS_FAIXA
    for c, ((nome, x0, w), valores) in enumerate(zip(colunas_faixa, atributos)):
        chaves = list(zip(*atributos[:c + 1]))
        a = 0
        while a < len(chaves):
            b = a
            while b + 1 < len(chaves) and chaves[b + 1] == chaves[a]:
                b += 1
            if chave:
                xd, y0, y1 = x0 + w - 2, a - 0.36, b + 0.36
                ax.plot([xd - 3, xd, xd, xd - 3], [y0, y0, y1, y1], transform=trans,
                        color=INK_MUTED, lw=0.9, solid_joinstyle="miter", clip_on=False)
                ax.text(x0 + w / 2 - 3, (a + b) / 2, valores[a], transform=trans,
                        ha="center", va="center", fontsize=7, color=INK_PRIMARY,
                        clip_on=False)
            else:
                ax.add_patch(FancyBboxPatch((x0, a - 0.3), w, b - a + 0.6,
                                            boxstyle="square,pad=0",
                                            mutation_aspect=1 / 72, transform=trans,
                                            facecolor=FAIXA, edgecolor="none", clip_on=False))
                ax.text(x0 + w / 2, (a + b) / 2, valores[a], transform=trans, ha="center",
                        va="center", fontsize=7, color=INK_PRIMARY, clip_on=False)
            a = b + 1
        if cabecalho:
            ax.text(x0 + w / 2, -0.75, nome, transform=trans, ha="center", va="bottom",
                    fontsize=7.5, color=INK_SECONDARY, clip_on=False)


def painel(ax, ser, g, mod, cenario, fmt, linhas, rotulo_direita, marcar=None):
    """Barras de um grupo num formato: só a letra à esquerda; K e IoTh (interference over thermal) à direita do painel
    quando rotulo_direita (a última coluna). marcar = índice da barra em que uma seta mostra
    que o fim da parte azul é a SNR do BCD-MMSE em float."""
    eixos(ax, grade_x=True, grade_y=False)
    ks = configs(g, mod)
    for y, k in enumerate(ks):
        d, d_lim, f, f_lim = partes(ser[(cenario, k)], fmt)
        ax.barh(y, d, height=ALTURA_BARRA, color=COR_DESC, edgecolor=SURFACE, lw=1.0,
                hatch=TEXTURA_LIMITE if d_lim else None, zorder=3)
        if f is not None:
            ax.barh(y, f, left=d, height=ALTURA_BARRA, color=cor_formato(f), edgecolor=SURFACE,
                    lw=1.0, zorder=3)
        if y == marcar:
            ax.annotate("BCD-MMSE (float)", xy=(d, y - ALTURA_BARRA / 2),
                        xytext=(d + 0.45, y - 1.15), textcoords="data", ha="left", va="center",
                        fontsize=7, color=INK_PRIMARY, zorder=5,
                        arrowprops=dict(arrowstyle="->", color=INK_PRIMARY, lw=0.8,
                                        shrinkA=1, shrinkB=0))
        p = PAINEIS[k]
        linhas.append([FORMATOS[fmt][0], g + (f" {mod}" if mod else ""), cenario, LETRAS[k],
                       k, p.K, p.iot_db, f"{d:.3f}", "limite_inferior" if d_lim else "",
                       "nao_atinge" if f is None else f"{f:.3f}",
                       "limite_inferior" if f_lim else ""])
    ax.set_yticks(range(len(ks)), [LETRAS[k] for k in ks], fontsize=7.5, color=INK_PRIMARY)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(len(ks) - 0.5, -0.5)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", labelbottom=True, labelsize=7)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: ponto(v)))


def figura(ser, fmts, cenario):
    alturas = [len(configs(g, mod)) for g, mod in GRUPOS]
    fig, axs = plt.subplots(len(GRUPOS), len(fmts), figsize=(LARGURA, 0.32 * sum(alturas) + 2.6),
                            sharex=True, squeeze=False,
                            gridspec_kw={"height_ratios": alturas})
    fig.patch.set_facecolor(SURFACE)
    linhas = []
    for i, (g, mod) in enumerate(GRUPOS):
        for j, fmt in enumerate(fmts):
            painel(axs[i][j], ser, g, mod, cenario, fmt, linhas, j == len(fmts) - 1,
                   marcar=None)
        faixas_esquerda(axs[i][0], configs(g, mod), cabecalho=i == 0)
        M, C = ESTACAO[g]
        nome = {"16QAM": "16-QAM", "QPSK": "QPSK"}.get(mod)
        # M_c = M / C: antenas por cluster, o tamanho da matriz invertida
        axs[i][0].set_title(f"{nome + ': ' if nome else ''}$M$ = {M}, $C$ = {C}, "
                            f"$M_c$ = {M // C}", loc="left", fontsize=8,
                            color=INK_PRIMARY, pad=6)
    topo = max(float(l[7]) + (float(l[9]) if l[9] != "nao_atinge" else 0) for l in linhas)
    axs[0][0].set_xlim(0, topo * 1.04)
    for j, fmt in enumerate(fmts):
        rot, modo, _ = FORMATOS[fmt]
        axs[-1][j].set_xlabel("SNR increase over LMMSE [dB]",
                              color=INK_SECONDARY, fontsize=7.5)
        # nome do formato acima da coluna, na altura do título do primeiro grupo
        # o modo de quantização e overflow fica embaixo, menor e mais fino
        axs[0][j].annotate(rot, (0.5, 1), xycoords="axes fraction",
                           xytext=(0, 31), textcoords="offset points", ha="center",
                           va="bottom", fontsize=8.5, color=INK_PRIMARY)
        axs[0][j].annotate(fag.MODO[modo], (0.5, 1), xycoords="axes fraction",
                           xytext=(0, 22), textcoords="offset points", ha="center",
                           va="bottom", fontsize=7, fontweight="light", color=INK_SECONDARY)
    fig.suptitle(f"BCD-MMSE (iter 1) at SER = $10^{{-2}}$, {CENARIO_EN[cenario]}",
                 fontsize=9, color=INK_PRIMARY, y=0.997)
    h = [Patch(facecolor=COR_DESC,
               label="BCD-MMSE (float) over LMMSE"),
         Patch(facecolor=COR_DESC, edgecolor=SURFACE, hatch=TEXTURA_LIMITE,
               label="LMMSE already below $10^{-2}$"),
         Patch(facecolor=COR_FMT,
               label="BCD-MMSE (fixed point) over BCD-MMSE (float)")]
    fig.legend(handles=h, handler_map={h[2]: AlcaDegrade()}, loc="lower center", ncol=3, frameon=False, fontsize=7, columnspacing=1.2, handletextpad=0.5,
               labelcolor=INK_SECONDARY, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.035, 0.99, 0.975), h_pad=1.4, w_pad=1.2)
    nomes = "_".join(FORMATOS[f][2] for f in fmts)
    salvar(fig, f"descentralizacao_formato_{cenario}_{nomes}", linhas,
           ["formato", "grupo", "cenario", "letra", "configuracao", "K", "iot_db",
            "perda_descentralizacao_db", "descentralizacao_limite", "perda_formato_db",
            "formato_limite"])


# Versão do TCC (--tcc): uma figura por grupo, com os formatos escolhidos do grupo (Tabela
# tab:formatos-escolhidos do TCC; cada formato com o seu modo, como em FORMATOS). Os grupos 2
# e 3 incluem as QPSK (17 a 24), com os dados de partes_qpsk_256.
TCC = Path(__file__).resolve().parents[2] / "TG2_-__ECP_UFRGS" / "Images" / "RESULTADOS"
# 2026-11-09: sem o critério "atinge SER = 10^-2"; grupo 1 com 0,1 dB no <26,12> (grade inteira)
FORMATOS_GRUPO = {"G1": ((12, 12), (12, 14)),
                  "G2": ((14, 14), (14, 16)),
                  "G3": ((12, 12), (14, 16))}
# Formatos escolhidos só com IoTh de 10 dB (configurações A a D) que não estão acima: uma
# coluna a mais, à esquerda, só com essas configurações
FORMATO_IOT10 = {"G1": (8, 10), "G2": (12, 10), "G3": (12, 10)}


def colunas(g):
    return (FORMATO_IOT10[g], *FORMATOS_GRUPO[g])


def so_iot10(g, fmt):
    return fmt == FORMATO_IOT10[g]


# Condição de cada barra no TCC: a do pior caso, como no mapa (a de maior parte do formato;
# "não atinge" conta como a pior; empate, como 0,00 dB em todas, pelo maior aumento total).
# A parte da descentralização vem da mesma condição. Nome curto ao lado da barra.
CURTO = {"TDLA30-5": "A30-5", "TDLA30-75": "A30-75", "TDLA30-300": "A30-300",
         "TDLC300-100": "C300-100", "TDLB100-400": "B100-400"}


def pior_cenario(ser, k, fmt):
    def chave(c):
        d, _, f, _ = partes_k(ser, c, k, fmt)
        return (f is None, round(f or 0, 3), d + (f or 0))
    return max(CENARIOS, key=chave)


def topo_comum(ser, cenario):
    """Maior barra (descentralização + formato) entre todos os grupos e formatos do TCC,
    para as três figuras terem o mesmo eixo x."""
    t = 0
    for g, fmts in FORMATOS_GRUPO.items():
        for mod in ("16QAM", "QPSK"):
            for k in configs(g, mod):
                for fmt in colunas(g):
                    if so_iot10(g, fmt) and PAINEIS[k].iot_db != 10:
                        continue
                    c = pior_cenario(ser, k, fmt) if cenario == "pior" else cenario
                    d, _, f, _ = partes_k(ser, c, k, fmt)
                    t = max(t, d + (f or 0))
    return t


# Figuras do TCC: a parte do formato quase sempre fica abaixo de 0,2 dB e quase não aparece
# no eixo de 0 a 4 dB; por isso o valor dela vai escrito em azul na ponta da barra quando
# a parte azul é menor que ROTULO_ATE (acima disso ela já se vê)
ROTULO_ATE = 0.3
COR_HACHURA = "#8a5a00"   # hachura do limite inferior, laranja escuro sobre o amarelo
COR_ROTULO = "#1c5cab"
# barras mais finas que as de figura(): com 4 barras por painel, 0,72 deixava tudo alto
ALTURA_BARRA_TCC = 0.5


def painel_tcc(ax, ser, gg, mod, cenario, fmt, linhas, letras, iot10=False):
    eixos(ax, grade_x=True, grade_y=False)
    ks = configs(gg, mod)
    for y, k in enumerate(ks):
        if iot10 and PAINEIS[k].iot_db != 10:
            continue   # coluna do caso base: só as configurações com IoTh de 10 dB
        c = pior_cenario(ser, k, fmt) if cenario == "pior" else cenario
        d, d_lim, f, f_lim = partes_k(ser, c, k, fmt)
        ax.barh(y, d, height=ALTURA_BARRA_TCC, color=COR_DESC, edgecolor="none", zorder=3)
        if d_lim:
            ax.barh(y, d, height=ALTURA_BARRA_TCC, facecolor="none", edgecolor=COR_HACHURA,
                    hatch="//", lw=0, zorder=4)
        fim = d
        if f is not None:
            ax.barh(y, f, left=d, height=ALTURA_BARRA_TCC, color=COR_FMT, edgecolor="none",
                    zorder=3)
            fim = d + f
            rot = ax.text(fim + 0.08, y, f"+{f:.2f}" if f < ROTULO_ATE else "", ha="left",
                          va="center", fontsize=6.5, color=COR_ROTULO, zorder=5)
            if cenario == "pior":
                # nome da condição logo depois do valor, em cinza
                ax.annotate(f" {CURTO[c]}", xy=(1, 0.5), xycoords=rot, ha="left",
                            va="center", fontsize=5.5, color=INK_SECONDARY, zorder=5)
        else:
            ax.text(d + 0.08, y, "not reached", ha="left", va="center", fontsize=6.5,
                    color=INK_SECONDARY, zorder=5)
        p = PAINEIS[k]
        linhas.append([FORMATOS[fmt][0], gg + (f" {mod}" if mod else ""), c, LETRAS[k],
                       k, p.K, p.iot_db, f"{d:.3f}", "limite_inferior" if d_lim else "",
                       "nao_atinge" if f is None else f"{f:.3f}",
                       "limite_inferior" if f_lim else ""])
    # coluna só com IoTh de 10 dB: só as letras das barras que existem; as outras colunas
    # levam a legenda completa
    pos = [y for y, k in enumerate(ks) if not (iot10 and PAINEIS[k].iot_db != 10)]
    ax.set_yticks(pos, [LETRAS[ks[y]] for y in pos], fontsize=7.5, color=INK_PRIMARY)
    ax.tick_params(axis="y", length=0, labelleft=letras)
    ax.set_ylim(len(ks) - 0.5, -0.5)
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.tick_params(axis="x", labelbottom=True, labelsize=7)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: ponto(v, 0)))


def figura_grupo_tcc(ser, g, cenario, topo):
    grupos = [(g, "16QAM"), (g, "QPSK")]
    fmts = colunas(g)
    alturas = [len(configs(*gm)) for gm in grupos]
    altura = 0.24 * sum(alturas) + 0.75 * len(grupos) + 1.0
    fig, axs = plt.subplots(len(grupos), len(fmts), figsize=(LARGURA, altura), sharex=True,
                            squeeze=False,
                            gridspec_kw={"height_ratios": alturas})
    fig.patch.set_facecolor(SURFACE)
    linhas = []
    for i, (gg, mod) in enumerate(grupos):
        for j, fmt in enumerate(fmts):
            painel_tcc(axs[i][j], ser, gg, mod, cenario, fmt, linhas, letras=j <= 1,
                       iot10=so_iot10(g, fmt))
        # sem as colunas de IoTh e K (pedido da autora: tiravam largura do eixo x); o texto
        # remete à Tabela tab:paineis
        if mod:
            axs[i][0].set_title({"16QAM": "16-QAM", "QPSK": "QPSK"}[mod], loc="left",
                                fontsize=8, color=INK_PRIMARY, pad=4)
    axs[0][0].set_xlim(0, topo + 1.1 if cenario == "pior" else topo * 1.04)
    for j, fmt in enumerate(fmts):
        rot, modo, _ = FORMATOS[fmt]
        # com 3 colunas estreitas, o rótulo do eixo x só na do meio (senão se encostam)
        if len(fmts) < 3 or j == 1:
            axs[-1][j].set_xlabel("SNR increase over LMMSE [dB]", color=INK_SECONDARY,
                                  fontsize=7.5)
        axs[0][j].annotate(rot, (0.5, 1), xycoords="axes fraction", xytext=(0, 39),
                           textcoords="offset points", ha="center", va="bottom",
                           fontsize=8.5, color=INK_PRIMARY)
        axs[0][j].annotate(fag.MODO[modo], (0.5, 1), xycoords="axes fraction",
                           xytext=(0, 30), textcoords="offset points", ha="center",
                           va="bottom", fontsize=7, fontweight="light", color=INK_SECONDARY)
        axs[0][j].annotate("IoTh 10 dB only" if so_iot10(g, fmt) else "All configurations",
                           (0.5, 1), xycoords="axes fraction", xytext=(0, 20),
                           textcoords="offset points", ha="center", va="bottom",
                           fontsize=8.5, color=INK_PRIMARY)
    h = [Patch(facecolor=COR_DESC, label="BCD-MMSE (float) over LMMSE"),
         Patch(facecolor=COR_FMT, label="BCD-MMSE (fixed point) over BCD-MMSE (float)")]
    if any(l[8] for l in linhas):
        h.insert(1, Patch(facecolor=COR_DESC, edgecolor=COR_HACHURA, hatch="//", lw=0,
                          label="Lower bound: LMMSE already below $10^{-2}$"))
    fig.tight_layout(rect=(0.0, 0.55 / altura, 0.99, 1 - 0.55 / altura), h_pad=1.2,
                     w_pad=1.2)
    legenda_quadro(fig, axs[-1][-1], h, ncol=2, fontsize=6.5, columnspacing=1.0,
                   handletextpad=0.5)
    TCC.mkdir(parents=True, exist_ok=True)
    nome = f"descentralizacao_grupo{g[1]}"
    fig.savefig(TCC / f"{nome}.pdf", facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(fag.SAIDA / f"tcc_{nome}.png", facecolor=SURFACE, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(TCC / f"{nome}.pdf")
    return linhas


def tabela(ser):
    """Todos os grupos, cenários e configurações, nos formatos <22,12> e <24,12>, para
    montar tabelas depois (independe do cenário escolhido para a figura)."""
    cab = ["formato", "grupo", "cenario", "letra", "configuracao", "M", "C", "K", "iot_db",
           "modulacao", "snr_lmmse_db", "estado_lmmse", "snr_bcd_float_db",
           "estado_bcd_float", "snr_bcd_formato_db", "estado_bcd_formato",
           "perda_descentralizacao_db", "descentralizacao_limite", "perda_formato_db",
           "formato_limite", "diferenca_formato_sem_piso_db", "perda_total_db"]
    linhas = []
    for fmt in ((12, 10), (12, 12)):
        for g, mod in GRUPOS:
            for c in CENARIOS:
                for k in configs(g, mod):
                    r, p = ser[(c, k)], PAINEIS[k]
                    xl, el = estado_snr(r["LMMSE"])
                    xb, eb = estado_snr(r["BCD"])
                    xh, eh = estado_snr(r[fmt])
                    d, d_lim, f, f_lim = partes(r, fmt)
                    v = lambda x: "" if x is None else f"{x:.4f}"
                    linhas.append([FORMATOS[fmt][0], g + (f" {mod}" if mod else ""), c,
                                   LETRAS[k], k, p.M, p.C, p.K, f"{p.iot_db:g}", p.modulation,
                                   v(xl), el, v(xb), eb, v(xh), eh, v(d),
                                   "limite_inferior" if d_lim else "",
                                   "nao_atinge" if f is None else v(f),
                                   "limite_inferior" if f_lim else "",
                                   "" if xh is None else v(xh - xb),
                                   "" if f is None else v(d + f)])
    fag.SAIDA.mkdir(parents=True, exist_ok=True)
    arq = fag.SAIDA / "tabela_descentralizacao_formato.csv"
    with open(arq, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cab)
        w.writerows(linhas)
    print(arq, f"({len(linhas)} linhas)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--com-28-14", action="store_true",
                    help="também o <28,14> (perda abaixo de 0,035 dB em todos os casos)")
    ap.add_argument("--cenario", default=None, choices=[*CENARIOS, "pior"],
                    help="padrão: TDLA30-5; com --tcc, pior (a condição do pior caso de cada "
                         "barra, como no mapa)")
    ap.add_argument("--tcc", action="store_true",
                    help="uma figura por grupo, com os formatos escolhidos do grupo, sem "
                         "título e com fonte Type 42, em TCC/Images/RESULTADOS")
    a = ap.parse_args()
    fag.SAIDA = PASTA / "figuras" / "descentralizacao"
    ser = carregar()
    if a.tcc:
        plt.rcParams["pdf.fonttype"] = 42
        a.cenario = a.cenario or "pior"
        topo = topo_comum(ser, a.cenario)
        linhas = []
        for g in FORMATOS_GRUPO:
            linhas += figura_grupo_tcc(ser, g, a.cenario, topo)
        with open(fag.SAIDA / "tcc_descentralizacao_data.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["formato", "grupo", "cenario", "letra", "configuracao", "K", "iot_db",
                        "perda_descentralizacao_db", "descentralizacao_limite",
                        "perda_formato_db", "formato_limite"])
            w.writerows(linhas)
        return
    tabela(ser)
    figura(ser, ((12, 10), (12, 12)) + (((14, 14),) if a.com_28_14 else ()),
           a.cenario or "TDLA30-5")


if __name__ == "__main__":
    main()
