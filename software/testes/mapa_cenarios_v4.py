#!/usr/bin/env python3
"""
Mapas de calor da [4] v4: formato (linha, por I e depois F) contra configuração (coluna), com
um modo de quantização e estouro fixo por formato, um para 16 x 16 e outro para 32 x 32
(modo_fixo: o que fica até o limite em mais cenários, somando as configurações do circuito; no
empate, a menor ocupação). O modo fica embaixo do formato, no rótulo da linha.

- mapa_perda_modo_fixo_ate_<3|01>dB_iter<1|4>_escada_por_I: a cor é a pior perda em dB entre
  os 5 cenários, num degradê (escala log), com 0,1 e 3 dB marcados na
  barra; um símbolo amarelo para cada cenário fora de algum limite, vazado se passa de 0,1 dB
  e cheio se passa de 3 dB. × é a célula em que, nesse modo, algum cenário não chega a
  SER = 10^-2 nas SNRs simuladas (perda maior que a folga da grade, pelo menos 4 dB); ela
  fica sem símbolos;
- mapa_recurso_modo_fixo_ate_<3|01>dB_iter<1|4>_escada_por_I: os mesmos modos e células, mas a cor e
  o número são a maior ocupação da XCU50 (e qual recurso).

As colunas vão da configuração mais folgada para a mais restrita (a "escada", pelos cenários
até 0,1 dB e até o limite nas células do modo fixo), em grupos pela Interference over Thermal,
modulação, tamanho da matriz, M e C, e K.

Com --letras, grava só o mapa_perda até 3 dB com 1 iteração, com as configurações nomeadas
por nome (LETRAS: 1A a 1H, 2A, 2B, 2E, 2F, 3A, 3B, 3E, 3F), num desenho mais estreito (legenda dos
cenários embaixo do mapa), em ..._letras.png e .pdf.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python mapa_cenarios_v4.py [--letras]
"""

import argparse


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch

from figuras_formatos import OVERFLOWS, QUANTS, ler, perdas
from pareto_modos import ABREV
from pareto_v4 import CIRCUITOS, FORMATOS, V4, ocupacao
from tabela_v4_configs import CENARIOS, CONFIGS, MODOS
from dbp_sim.plotting import INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE

SAIDA = V4 / "figuras"
# Ordens das linhas: por bits de fração (F) e depois de inteiro (I), ou por I e depois F
ORDENS = {"F": sorted(FORMATOS, key=lambda f: (f[1], f[0])),
          "I": sorted(FORMATOS, key=lambda f: (f[0], f[1]))}
# Pior perda num degradê de um só tom, do claro (perda perto de 0) ao escuro (perda alta);
# escala log para que 0,1 dB e 3 dB fiquem visíveis na mesma barra
DEGRADE = LinearSegmentedColormap.from_list("perda", ["#cde2fb", "#86b6ef", "#3987e5",
                                                      "#1c5cab", "#0d366b"])
NORMA = LogNorm(vmin=0.01, vmax=5, clip=True)
MODULACAO = {"16QAM": "16-QAM", "QPSK": "QPSK"}
FAIXA = "#e4e3df"   # fundo das faixas da legenda das configurações
# Um símbolo por cenário, na ordem de CENARIOS
SIMBOLOS = ("o", "^", "s", "D", "v")
NOMES_CENARIOS = {"TDLA30-5": "TDLA30-5 and -10"}
# Limites do modo fixo: um par de mapas (perda e recurso) para cada um
LIMITES = (3, 0.1)
FORA = "#ff3d9a"   # rosa forte dos cenários fora do limite (amarelo = BCD-MMSE; vermelho lembra erro)
# Ocupação num degradê de outro tom (roxo), para não confundir com o da perda; escala linear
DEGRADE_OCUPACAO = LinearSegmentedColormap.from_list("ocupacao", ["#ece6fb", "#c3b2f0",
                                                                  "#9474de", "#6a45bf", "#3f2380"])
# Os modos escolhidos ocupam de 0,9% a 3,1% da XCU50
NORMA_OCUPACAO = Normalize(vmin=0.5, vmax=3.5, clip=True)
# Nomes das configurações (--letras): número do grupo + letra
# (G1: M = 128, C = 8; G2: M = 256, C = 8; G3: M = 256, C = 16), na ordem IoTh, modulação, K
# dentro do grupo (Tabela tab:paineis do TCC)
LETRAS = {1: "1A", 3: "1B", 5: "1C", 7: "1D", 2: "1E", 4: "1F", 6: "1G", 8: "1H",
          9: "2A", 11: "2B", 10: "2E", 12: "2F",
          13: "3A", 15: "3B", 14: "3E", 16: "3F"}
NOMES = {}   # configuração -> rótulo da coluna; vazio = o número
ESTREITO = []   # não vazio: desenho estreito (--letras)
# Ajustes de quem importa este módulo (mapa_grupos_v4): atributos que saem da legenda das
# configurações, tamanho e margens da figura e colunas da legenda dos cenários
SEM_ATRIBUTOS = set()
LAYOUT = {}
VERMELHO = "#d03b3b"   # cor do × (nenhum modo chega a SER = 10^-2 em todos os cenários)
# Textos da figura em inglês, ponto decimal, sem itálico nas letras de fórmula
# (MANUAL_GRAFICOS.md)
plt.rcParams["mathtext.default"] = "regular"


def matriz(celulas, limite):
    """Cenários (0 a 5) dentro do limite em cada célula do modo fixo (× conta como fora)."""
    return [[sum(v is not None and round(v, 2) <= limite for v in vs) for _, vs, _ in linha]
            for linha in celulas]


def posicoes(configs):
    """x de cada coluna: uma por unidade, mais LAYOUT["folga_ioth"] onde o IoTh muda."""
    folga, xs = LAYOUT.get("folga_ioth", 0), []
    for k in configs:
        if xs and folga and paineis()[k].iot_db != paineis()[anterior].iot_db:
            xs.append(xs[-1] + 1 + folga)
        else:
            xs.append(xs[-1] + 1 if xs else 0)
        anterior = k
    return xs


def blocos(xs):
    """Trechos de colunas seguidas sem folga: listas de índices."""
    trechos = []
    for j, x in enumerate(xs):
        if trechos and x - xs[j - 1] == 1:
            trechos[-1].append(j)
        else:
            trechos.append([j])
    return trechos


def pintar(ax, xs, valores, **kw):
    """pcolormesh por trecho, para a folga ficar vazia."""
    for tr in blocos(xs):
        ax.pcolormesh(np.arange(len(tr) + 1) + xs[tr[0]] - 0.5,
                      np.arange(len(valores) + 1) - 0.5,
                      np.ma.masked_invalid([[linha[j] for j in tr] for linha in valores]), **kw)


def paineis():
    from dbp_sim.params import PANELS_BY_LABEL, TCC_CONFIGURATION
    return {TCC_CONFIGURATION[r]: p for r, p in PANELS_BY_LABEL.items()}


def atributos(configs):
    """Linhas da legenda das configurações: (nome, valor de cada configuração)."""
    painel = [paineis()[k] for k in configs]
    linhas = (("IoTh" if ESTREITO else "Interference over thermal (IoTh)",
             [f"{q.iot_db:g} dB" for q in painel]),
            ("Modulation", [MODULACAO.get(q.modulation, q.modulation) for q in painel]),
            ("Matrix" if ESTREITO else "Inverted matrix", [f"{q.M // q.C} × {q.M // q.C}" for q in painel]),
            ("$M$, $C$", [f"{q.M}, {q.C}" for q in painel]),
            ("$K$", [str(q.K) for q in painel]))
    return tuple(a for a in linhas if a[0] not in SEM_ATRIBUTOS)


def faixas(valores):
    """Trechos seguidos com o mesmo valor: (primeira coluna, última coluna, valor)."""
    trechos = []
    for j, v in enumerate(valores):
        if trechos and trechos[-1][2] == v:
            trechos[-1][1] = j
        else:
            trechos.append([j, j, v])
    return trechos


def modo_fixo(p, occ_k, configs, linhas, limite):
    """Um modo por formato e por circuito (16 x 16 e 32 x 32), com o critério de
    perda_ocupacao somado nas configurações do circuito: mais pares (configuração, cenário)
    dentro do limite (× conta como fora); depois a menor ocupação, AP_RND_ZERO, a menor pior
    perda e a ordem dos modos. Devolve as células (pior perda ou None se o modo tem × em algum cenário, perdas
    nos 5 cenários, ocupação) e {circuito: modo} de cada formato."""
    celulas, modos = [], []
    for I, F in linhas:
        escolha = {}
        for n, ks in CIRCUITOS.items():
            ks = [k for k in ks if k in configs]
            if not ks:
                continue
            def chave(m):
                vs = [p[(k, c, I, F, *m)] for k in ks for c in CENARIOS]
                return (-sum(v is not None and round(v, 2) <= limite for v in vs),
                        round(occ_k[ks[0]][(I, F, *m)][0], 3), m[0] != "AP_RND_ZERO",
                        max((v for v in vs if v is not None), default=float("inf")),
                        MODOS.index(m))
            escolha[n] = min(MODOS, key=chave)
        linha = []
        for k in configs:
            m = escolha[next(n for n, ks in CIRCUITOS.items() if k in ks)]
            vs = [p[(k, c, I, F, *m)] for c in CENARIOS]
            linha.append((None if None in vs else max(vs), vs, occ_k[k][(I, F, *m)]))
        celulas.append(linha)
        modos.append(escolha)
    return celulas, modos


def cheio(limite):
    """Perda acima da qual o símbolo é cheio: o limite, ou 3 dB se o limite é 0,1 dB (aí o
    vazado já marca o que passa do limite)."""
    return limite if limite > 0.1 else 3


def estado(v, limite):
    """0: até 0,1 dB; 1: até o limite; 2: passa do limite ou falha."""
    if v is None or round(v, 2) > limite:
        return 2
    return 0 if round(v, 2) <= 0.1 else 1


def num(v):
    return f"{v:.2f}"


def niveis(n01, n3):
    return [[3 if a == 5 else 2 if b == 5 else 1 if b > 0 else 0 for a, b in zip(la, lb)]
            for la, lb in zip(n01, n3)]


def escada(n01, n3, configs):
    """Colunas da configuração mais folgada (mais formatos atendidos, e nos formatos menores)
    para a mais restrita: os cinzas vão para cima e para a direita."""
    nivel = niveis(n01, n3)
    coluna = {k: [linha[j] for linha in nivel] for j, k in enumerate(configs)}
    return k_crescente(sorted(configs, key=lambda k: (-sum(coluna[k]), [-v for v in coluna[k]])))


def k_crescente(ordem):
    """Colunas vizinhas que só diferem em K ficam sempre com K = 8 antes de K = 12, como nos
    outros grupos (no QPSK com IoTh 20 dB a escada punha K = 12 primeiro)."""
    ordem = list(ordem)
    chave = lambda k: (paineis()[k].iot_db, paineis()[k].modulation, paineis()[k].M,
                       paineis()[k].C)
    for i in range(len(ordem) - 1):
        a, b = ordem[i], ordem[i + 1]
        if chave(a) == chave(b) and paineis()[a].K > paineis()[b].K:
            ordem[i], ordem[i + 1] = b, a
    return ordem


def base(configs, linhas, por, titulo, rotulos=None):
    """Figura com o mapa vazio, os rótulos e, embaixo, uma faixa por atributo da configuração
    que junta as colunas vizinhas com o mesmo valor. Devolve a figura e o eixo do mapa."""
    attrs = atributos(configs)
    xs = posicoes(configs)
    fig, (ax, leg) = plt.subplots(2, 1, figsize=LAYOUT.get("figsize", (9.6, 7.75) if ESTREITO
                                                    else (13.5, 7.6)),
                                  facecolor=SURFACE, sharex=True,
                                  gridspec_kw={"height_ratios": (len(linhas), 0.62 * len(attrs)),
                                               "hspace": 0.08})
    ax.set_facecolor(SURFACE)
    ax.set_xticks([xs[j] + 0.5 for tr in blocos(xs) for j in tr[:-1]], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(linhas))], minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    ax.tick_params(which="minor", length=0)
    # O número da configuração fica logo abaixo do mapa, em cima das faixas
    ax.set_xticks(xs, [NOMES.get(k, str(k)) for k in configs])
    ax.tick_params(axis="x", which="major", labelbottom=True, colors=INK_SECONDARY,
                   labelsize=9)
    ax.set_yticks(range(len(linhas)), rotulos or
                  [f"<{I + F},{I}>" + ("" if por == "I" else f"  F = {F}") for I, F in linhas],
                  color=INK_SECONDARY, fontsize=8.5 if rotulos else None)
    ax.tick_params(which="major", length=0)
    ax.set_ylabel("Fixed-point format (ap_fixed)", color=INK_SECONDARY)
    ax.set_title(titulo, loc="left", color=INK_PRIMARY, pad=10)
    leg.set_facecolor(SURFACE)
    leg.set_ylim(len(attrs) - 0.5, -0.5)
    for r in range(len(attrs)):
        # Uma faixa não passa da divisa das faixas de cima (os grupos ficam encaixados)
        chaves = list(zip(*(valores for _, valores in attrs[:r + 1])))
        for a, b, chave in faixas(chaves):
            # retângulo reto, um pouco mais justo ao texto
            leg.add_patch(FancyBboxPatch((xs[a] - 0.5 + 0.05, r - 0.3), xs[b] - xs[a] + 1 - 0.1, 0.6,
                                         boxstyle="square,pad=0",
                                         facecolor=FAIXA, edgecolor="none"))
            leg.text((xs[a] + xs[b]) / 2, r, chave[-1], ha="center", va="center",
                     fontsize=7.5 if ESTREITO else 8.5,
                     color=INK_PRIMARY)
    leg.set_yticks(range(len(attrs)), [nome for nome, _ in attrs], color=INK_SECONDARY)
    leg.tick_params(which="both", length=0, labelbottom=False)
    leg.set_xlabel("Configuration", color=INK_SECONDARY)
    for eixo in (ax, leg):
        for lado in eixo.spines.values():
            lado.set_visible(False)
    if ESTREITO:
        fig.subplots_adjust(**LAYOUT.get("margens", dict(left=0.12, right=0.86, top=0.95,
                                                         bottom=0.115)))
    else:
        fig.subplots_adjust(left=0.12, right=0.8, top=0.94, bottom=0.11)
    return fig, ax


def barra(fig, ax, norma, cores, ticks, rotulos, titulo):
    pos = ax.get_position()
    b = fig.colorbar(plt.cm.ScalarMappable(norm=norma, cmap=cores), ticks=ticks,
                     cax=fig.add_axes((pos.x1 + 0.012, pos.y0, 0.014, 0.9 * pos.height)))
    b.ax.set_yticklabels(rotulos, fontsize=8.5, color=INK_SECONDARY)
    b.ax.minorticks_off()
    b.ax.tick_params(which="both", length=0)
    b.outline.set_visible(False)
    b.ax.set_title(titulo, fontsize=8.5, color=INK_SECONDARY, loc="left", pad=14)
    return b


def colunas(m, j):
    return [[linha[x] for x in j] for linha in m]


def mapa_perda(celulas, ordem, configs, por, titulo, nota, limite):
    """Pior perda em degradê (escala log), com as colunas na ordem dada e um símbolo por
    cenário embaixo do número."""
    j = [configs.index(k) for k in ordem]
    celulas = colunas(celulas, j)
    fig, ax = base(ordem, ORDENS[por], por, titulo, [""] * len(ORDENS[por]))
    valores = [[float("nan") if v is None else max(v, NORMA.vmin) for v, *_ in linha]
               for linha in celulas]
    # Células como vetor (pcolormesh), não como imagem: no PDF elas não borram ao ampliar
    xs = posicoes(ordem)
    pintar(ax, xs, valores, cmap=DEGRADE, norm=NORMA)
    ax.set_xlim(-0.5, xs[-1] + 0.5)
    ax.set_ylim(len(valores) - 0.5, -0.5)
    dy = -0.17
    for i, linha in enumerate(celulas):
        for jj, (v, vs, *_) in enumerate(linha):
            j = xs[jj]
            escuro = v is not None and NORMA(max(v, NORMA.vmin)) > 0.55
            tinta = SURFACE if escuro else INK_PRIMARY
            if v is None:
                ax.text(j, i, "×", ha="center", va="center", fontsize=9, color=VERMELHO)
                tinta = INK_MUTED
            else:
                ax.text(j, i + dy, num(v), ha="center", va="center",
                        fontsize=7 if ESTREITO else 8, color=tinta)
            if v is not None:
                # Só os cenários fora de algum limite: vazado passa de 0,1 dB, cheio passa
                # do limite. A célula × fica sem símbolos (nela já há cenário acima do limite)
                for c, (marca, vc) in enumerate(zip(SIMBOLOS, vs)):
                    if (e := estado(vc, cheio(limite))) == 0:
                        continue
                    ax.scatter(j + 0.17 * (c - 2), i + 0.24, s=11 if ESTREITO else 20,
                               marker=marca, facecolors=FORA if e == 2 else "none",
                               edgecolors=FORA, linewidths=0.9 if ESTREITO else 1.1)
    # sem nota de rodapé: o × e a definição do aumento de SNR ficam no texto do TCC
    rotulos_barra = ["≤ 0.01", "0.03", "0.1", "0.3", "1", "3"]
    if ESTREITO:
        rotulos_barra[2], rotulos_barra[5] = "0.1 dB", "3 dB"
    b = barra(fig, ax, NORMA, DEGRADE, [0.01, 0.03, 0.1, 0.3, 1, 3], rotulos_barra,
              "Worst SNR\nincrease")
    for marca_db in (0.1, cheio(limite)):
        b.ax.axhline(marca_db, color=INK_PRIMARY, linewidth=1.2)
        if not ESTREITO:
            b.ax.text(2.6, marca_db, f"{texto_limite(marca_db)} limit",
                      transform=b.ax.get_yaxis_transform(), va="center", fontsize=8,
                      color=INK_PRIMARY)
    marca = lambda m, color=INK_PRIMARY, **kw: Line2D([], [], marker=m, linestyle="none",
                                                      markersize=6, color=color, **kw)
    alcas = [marca(m, markerfacecolor="none") for m in SIMBOLOS]
    rotulos = [NOMES_CENARIOS.get(c, c) for c in CENARIOS]
    alcas += [Patch(facecolor="none", edgecolor=FORA, lw=1.1), Patch(facecolor=FORA, edgecolor=FORA)]
    rotulos += ["above 0.1 dB", f"above {texto_limite(cheio(limite))}"]
    if ESTREITO:
        # embaixo, numa linha só
        fig.legend(alcas, rotulos, loc="lower center", bbox_to_anchor=(0.5, 0.01),
                   ncol=LAYOUT.get("ncol", len(alcas)), frameon=False, fontsize=7, labelcolor=INK_SECONDARY,
                   handlelength=1.2, handletextpad=0.35, columnspacing=1.0,
                   title="Test conditions above the limit", title_fontsize=8)
        return fig
    fig.legend(alcas, rotulos, loc="upper left", bbox_to_anchor=(0.808, ax.get_position().y0),
               frameon=False, fontsize=8, labelcolor=INK_SECONDARY, handletextpad=0.4,
               title="Test conditions above the limit\n(no symbol: up to 0.1 dB)", title_fontsize=8.5,
               alignment="left")
    return fig


def rotular(fig, linhas, modos):
    """Rótulo de cada linha escrito à mão: o formato em cima e o modo fixo embaixo, menor (os
    dois modos, se 16 x 16 e 32 x 32 diferem)."""
    ax = fig.axes[0]
    nome = lambda m: f"{ABREV[m[0]]}/{ABREV[m[1]]}"
    for i, ((I, F), e) in enumerate(zip(linhas, modos)):
        modo = (nome(e[16]) if e[16] == e[32]
                else f"{nome(e[16])} (16 × 16)\n{nome(e[32])} (32 × 32)")
        ax.text(-0.008, i - 0.13, f"<{I + F},{I}>", transform=ax.get_yaxis_transform(),
                ha="right", va="bottom", fontsize=9 if ESTREITO else 10, color=INK_SECONDARY)
        ax.text(-0.008, i - 0.09, modo, transform=ax.get_yaxis_transform(), ha="right",
                va="top", fontsize=6.5 if ESTREITO else 7.5, color=INK_SECONDARY,
                linespacing=1.1)
    fig.subplots_adjust(left=LAYOUT.get("esquerda", 0.2 if ESTREITO else 0.16))
    # Sem rótulos nos ticks, o título do eixo vem para perto do mapa: volta para a esquerda
    ax.yaxis.set_label_coords(LAYOUT.get("rotulo_y", -0.21 if ESTREITO else -0.17), 0.5)


def nota_modo(limite, inicio):
    """Nota de rodapé: inicio, o critério do modo fixo e o que é o ×."""
    modo = ("one quantization and overflow mode per format (one for 16 × 16 and one for "
            f"32 × 32): the one within {texto_limite(limite)} in the most test conditions, summed over "
            "the configurations; ties go to the lowest occupancy.")
    return (inicio + modo + "\n×: in this mode, some test condition does not reach SER = 10$^{-2}$ "
            "within the simulated SNRs, i.e. it needs more than 4 dB extra (the smallest margin "
            "between float64 and the highest simulated SNR).")


def mapa_modo_fixo(celulas, modos, ordem, configs, t, por, limite):
    """mapa_perda com um modo fixo por formato e circuito (modo_fixo), escrito no rótulo."""
    fig = mapa_perda(celulas, ordem, configs, por,
                     f"Worst SNR increase over float at SER = 10$^{{-2}}$ per format "
                     f"(BCD-MMSE, {iteracoes(t)})" if ESTREITO else
                     f"Worst SNR increase over float at SER = 10$^{{-2}}$, fixed mode per format "
                     f"(BCD-MMSE, {iteracoes(t)})",
                     "",
                     limite)
    rotular(fig, ORDENS[por], modos)
    return fig


def mapa_recurso(celulas, modos, ordem, configs, t, por, limite):
    """Nos moldes do mapa_modo_fixo, mas a cor e o número são a maior ocupação da XCU50 (o
    recurso que mais ocupa, entre LUT, DSP, FF e BRAM) do modo fixo; os símbolos continuam
    sendo os cenários fora do limite, e o × é o mesmo."""
    j = [configs.index(k) for k in ordem]
    celulas = colunas(celulas, j)
    fig, ax = base(ordem, ORDENS[por], por,
                   f"Highest XCU50 occupancy, fixed mode per format (BCD-MMSE, {iteracoes(t)})",
                   [""] * len(ORDENS[por]))
    valores = [[float("nan") if v is None else o[0] for v, _, o in linha] for linha in celulas]
    xs = posicoes(ordem)
    pintar(ax, xs, valores, cmap=DEGRADE_OCUPACAO, norm=NORMA_OCUPACAO)
    ax.set_xlim(-0.5, xs[-1] + 0.5)
    ax.set_ylim(len(valores) - 0.5, -0.5)
    for i, linha in enumerate(celulas):
        for jj, (v, vs, o) in enumerate(linha):
            j = xs[jj]
            if v is None:
                ax.text(j, i, "×", ha="center", va="center", fontsize=9, color=VERMELHO)
                continue
            tinta = SURFACE if NORMA_OCUPACAO(o[0]) > 0.55 else INK_PRIMARY
            ax.text(j, i - 0.17, f"{num(o[0])} {o[1]}", ha="center", va="center",
                    fontsize=7.5, color=tinta)
            for c, (marca, vc) in enumerate(zip(SIMBOLOS, vs)):
                if (e := estado(vc, cheio(limite))) == 0:
                    continue
                ax.scatter(j + 0.16 * (c - 2), i + 0.24, s=20, marker=marca,
                           facecolors=FORA if e == 2 else "none", edgecolors=FORA,
                           linewidths=1.1)
    fig.text(0.02, 0.01, nota_modo(limite, "Occupancy: highest % of the XCU50 among LUT, DSP, "
                                           "FF and BRAM, and which resource (HLS synthesis "
                                           "16 × 16; 32 × 32 in configurations 9 to 12).\nMode: "),
             fontsize=7.5, color=INK_MUTED, va="bottom")
    barra(fig, ax, NORMA_OCUPACAO, DEGRADE_OCUPACAO, [0.5, 1, 1.5, 2, 2.5, 3, 3.5],
          ["0.5", "1", "1.5", "2", "2.5", "3", "3.5"], "Highest occupancy\n(% of XCU50)")
    marca = lambda m, color=INK_PRIMARY, **kw: Line2D([], [], marker=m, linestyle="none",
                                                      markersize=6, color=color, **kw)
    alcas = [marca(m, markerfacecolor="none") for m in SIMBOLOS]
    rotulos = [NOMES_CENARIOS.get(c, c) for c in CENARIOS]
    alcas += [Patch(facecolor="none", edgecolor=FORA, lw=1.1), Patch(facecolor=FORA, edgecolor=FORA)]
    rotulos += ["above 0.1 dB", f"above {texto_limite(cheio(limite))}"]
    fig.legend(alcas, rotulos, loc="upper left", bbox_to_anchor=(0.808, ax.get_position().y0),
               frameon=False, fontsize=8, labelcolor=INK_SECONDARY, handletextpad=0.4,
               title="Test conditions above the limit\n(no symbol: up to 0.1 dB)", title_fontsize=8.5,
               alignment="left")
    rotular(fig, ORDENS[por], modos)
    return fig


def texto_limite(limite):
    return f"{num(limite).rstrip('0').rstrip('.')} dB"


def iteracoes(t):
    return f"{t} {'iterations' if t > 1 else 'iteration'}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--letras", action="store_true",
                        help="só o mapa_perda até 3 dB, 1 iteração, configurações por letra")
    args = parser.parse_args()
    if args.letras:
        NOMES.update(LETRAS)
        ESTREITO.append(True)
    rodadas = ler(V4)
    configs = list(CONFIGS)
    occ_n = {n: ocupacao(n) for n in CIRCUITOS}
    occ_k = {k: occ_n[n] for n, ks in CIRCUITOS.items() for k in ks}
    SAIDA.mkdir(exist_ok=True)
    por = "I"
    linhas = ORDENS[por]
    for t in ((1,) if args.letras else (1, 4)):
        p = perdas(rodadas, f"BCD-MMSE (iter {t})")
        for limite in ((3,) if args.letras else LIMITES):
            celulas, modos = modo_fixo(p, occ_k, configs, linhas, limite)
            ordem = escada(matriz(celulas, 0.1), matriz(celulas, cheio(limite)), configs)
            sufixo = (f"modo_fixo_ate_{texto_limite(limite).replace(',', '')[:-3]}dB"
                      f"_iter{t}_escada_por_{por}")
            for nome, fig in ((f"mapa_perda_{sufixo}",
                               mapa_modo_fixo(celulas, modos, ordem, configs, t, por, limite)),
                              (f"mapa_recurso_{sufixo}",
                               mapa_recurso(celulas, modos, ordem, configs, t, por, limite))):
                if args.letras:
                    if not nome.startswith("mapa_perda"):
                        plt.close(fig)
                        continue
                    nome += "_letras"
                for ext, extra in (("png", {"dpi": 300}), ("pdf", {})):
                    fig.savefig(SAIDA / f"{nome}.{ext}", facecolor=SURFACE, **extra)
                plt.close(fig)
                print(SAIDA / f"{nome}.png")


if __name__ == "__main__":
    main()
