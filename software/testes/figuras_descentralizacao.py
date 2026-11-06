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
"""

import argparse
import csv

import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
from matplotlib import transforms
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle

import figuras_analise_grupos as fag
from figuras_analise_grupos import (ALL_PANELS, CENARIOS, FORMATOS, INK_PRIMARY,
                                    INK_SECONDARY, LARGURA, LETRAS, PASTA, SURFACE,
                                    TCC_CONFIGURATION, carregar, eixos, estado_snr, num,
                                    perda, salvar)

PAINEIS = {TCC_CONFIGURATION[p.label]: p for p in ALL_PANELS}
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
    ks = {"G1": range(1, 9), "G2": range(9, 13), "G3": range(13, 17)}[g]
    if mod:
        ks = [k for k in ks if PAINEIS[k].modulation == mod]
    # IoTh 10 antes de IoTh 20; dentro de cada IoTh, K = 8 antes de K = 12
    return sorted(ks, key=lambda k: (PAINEIS[k].iot_db, PAINEIS[k].K))


def partes(r, fmt):
    xl, el = estado_snr(r["LMMSE"])
    xb, _ = estado_snr(r["BCD"])
    f, f_lim = perda(r, fmt)
    return xb - xl, el == "abaixo", f, f_lim


# Faixas de IoTh e K à esquerda das letras, como as do mapa de perda: x em pontos a partir
# da borda esquerda do painel (não depende da largura dele); (início, largura) de cada coluna
COLUNAS_FAIXA = (("IoTh", -94, 42), ("$K$", -46, 26))


def faixas_esquerda(ax, ks, cabecalho):
    """IoTh e K de cada barra em caixas cinza (FAIXA do mapa), juntando as barras seguidas
    com o mesmo valor; K não passa da divisa do IoTh, como no mapa. A ordem não muda."""
    fig = ax.figure
    tx = (transforms.Affine2D().scale(1 / 72) + fig.dpi_scale_trans
          + transforms.ScaledTranslation(0, 0, ax.transAxes))
    trans = transforms.blended_transform_factory(tx, ax.transData)
    atributos = ([f"{PAINEIS[k].iot_db:g} dB" for k in ks], [str(PAINEIS[k].K) for k in ks])
    for c, ((nome, x0, w), valores) in enumerate(zip(COLUNAS_FAIXA, atributos)):
        chaves = list(zip(*atributos[:c + 1]))
        a = 0
        while a < len(chaves):
            b = a
            while b + 1 < len(chaves) and chaves[b + 1] == chaves[a]:
                b += 1
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
    ap.add_argument("--cenario", default="TDLA30-5", choices=list(CENARIOS))
    a = ap.parse_args()
    fag.SAIDA = PASTA / "figuras" / "descentralizacao"
    ser = carregar()
    tabela(ser)
    figura(ser, ((12, 10), (12, 12)) + (((14, 14),) if a.com_28_14 else ()), a.cenario)


if __name__ == "__main__":
    main()
