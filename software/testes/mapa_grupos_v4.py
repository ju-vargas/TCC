#!/usr/bin/env python3
"""
O mapa de aumento de SNR em SER = 10^-2 da [4] v4 (mapa_cenarios_v4.py --letras), separado
em três grupos pelo tamanho do arranjo e do cluster:

- grupo 1: M = 128, C = 8,  M_c = 16 (configurações 1A a 1H);
- grupo 2: M = 256, C = 8,  M_c = 32 (16-QAM: 2A, 2B, 2E, 2F; QPSK: 2C, 2D, 2G, 2H = 17 a 20);
- grupo 3: M = 256, C = 16, M_c = 16 (16-QAM: 3A, 3B, 3E, 3F; QPSK: 3C, 3D, 3G, 3H = 21 a 24).

As configurações 17 a 24 (QPSK com M = 256, params.QPSK_256_PANELS) vêm da [4] v5
(varredura4_v5_qpsk.sh); as outras, da v4. Cada mapa tem só as configurações do grupo, com os
nomes do padrão do grupo 1 (letras na ordem IoTh, depois 16-QAM antes de QPSK, depois K), que
é também a ordem das colunas. O modo fixo de cada formato é escolhido só com as
configurações do grupo (mesmo critério de mapa_cenarios_v4.modo_fixo); a legenda embaixo
perde as faixas da matriz invertida e de M, C, que são as mesmas no grupo todo.

Saída: <V4>/figuras/por_grupo/mapa_perda_modo_fixo_ate_3dB_iter1_grupo<1|2|3>_modo_por_grupo.png
e .pdf

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python mapa_grupos_v4.py
    ../simulador/.venv/bin/python mapa_grupos_v4.py --tcc

Com --tcc, sai a versão do TCC em TCC/Images/RESULTADOS/mapa_snr_grupo<g>.pdf: sem título
(ele vai na legenda da figura), textos maiores (a figura é reduzida à largura do texto), fonte
embutida como Type 42, sem o título da barra de cores (a legenda da figura diz que é o maior
aumento de SNR), legenda dos cenários num quadro dentro do mapa e
faixas de configuração com borda em vez de fundo cinza.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.text import Text

import mapa_cenarios_v4 as mc
import grade_inteira as gi
from figuras_formatos import ler, perdas
from pareto_v4 import CIRCUITOS, V4, ocupacao
from tabela_v4_configs import CONFIGS

V5 = V4.parent / "v5_qpsk_grupos_2_3"
GRUPOS = {1: (128, 8), 2: (256, 8), 3: (256, 16)}   # grupo -> (M, C)
LIMITE, T, POR = 3, 1, "I"
# Configurações da v5 e o circuito de cada uma (M_c = 32 no grupo 2, 16 no grupo 3)
NOVAS = {**{k: 32 for k in range(17, 21)}, **{k: 16 for k in range(21, 25)}}
# QPSK da v5: C, D (IoTh 10 dB) e G, H (IoTh 20 dB), como 1C, 1D, 1G, 1H no grupo 1
LETRAS_NOVAS = {17: "2C", 19: "2D", 18: "2G", 20: "2H", 21: "3C", 23: "3D", 22: "3G", 24: "3H"}
# Uma configuração da v5 só entra quando tem todas as rodadas (10 formatos x 35 modos x 5
# cenários); antes, o grupo dela sai só com as configurações da v4
COMPLETA = 10 * 35 * 5
NOVAS = {k: n for k, n in NOVAS.items()
         if len(list(V5.glob(f"dados/*/configuracao_{k}/*.json"))) == COMPLETA}


TCC = Path(__file__).resolve().parents[2] / "TG2_-__ECP_UFRGS" / "Images" / "RESULTADOS"
AMPLIA = 1.35         # fator dos textos na versão do TCC
ALTURA_TCC = 5.5     # altura da figura do TCC, em polegadas
AMPLIA_SIMBOLO = 1.2  # fator dos símbolos (cinco por célula: maiores que isso se encostam)


def ampliar(fig, f, f_simbolo):
    """Aumenta os textos da figura pelo fator f e os símbolos por f_simbolo."""
    for t in fig.findobj(Text):
        t.set_fontsize(t.get_fontsize() * f)
    for c in fig.findobj(PathCollection):
        c.set_sizes(c.get_sizes() * f_simbolo ** 2)
    for leg in fig.legends:
        for h in leg.legend_handles:
            if hasattr(h, "set_markersize"):
                h.set_markersize(h.get_markersize() * f_simbolo)


def aliviar_rotulos(ax):
    """Rótulos das linhas mais leves (2026-11-09): o formato numa linha só, no tamanho dos
    números das células; o modo mais comum do grupo sai do rótulo (vai para a legenda da
    figura) e só os outros modos ficam, menores e em cinza claro, embaixo do formato."""
    from collections import Counter
    eixo_y = ax.get_yaxis_transform()
    rot = [t for t in ax.texts if t.get_transform() == eixo_y]
    fmts = [t for t in rot if t.get_text().startswith("<")]
    modos = [t for t in rot if not t.get_text().startswith("<")]
    numero = next(t for t in ax.texts if t.get_transform() != eixo_y
                  and t.get_text().replace(".", "").isdigit())
    comum = Counter(t.get_text() for t in modos).most_common(1)[0][0]
    for f, m in zip(fmts, modos):
        i = round(f.get_position()[1] + 0.13)
        f.set_fontsize(numero.get_fontsize())
        f.set_color(mc.INK_PRIMARY)
        # 2026-11-10: o modo fica embaixo de todos os formatos, também o mais comum do grupo
        m.set_fontsize(numero.get_fontsize() * 0.85)
        m.set_color(mc.INK_SECONDARY)
    # nomes das configurações (1A a 1H) também no tamanho dos números das células
    for t in ax.get_xticklabels():
        t.set_fontsize(numero.get_fontsize())
    return comum


def legenda_no_mapa(fig):
    """Move a legenda dos cenários para um quadro acima do mapa, alinhado à direita.
    Com a grade inteira (rodada 6, 2026-11-09), as duas primeiras linhas de C e D passam a
    ter valores, e o quadro não pode mais ficar sobre o mapa."""
    velha = fig.legends[0]
    alcas, rotulos = velha.legend_handles, [t.get_text() for t in velha.get_texts()]
    velha.remove()
    ax = fig.axes[0]
    # Três colunas (3 + 2 + 2): as condições de teste nas duas primeiras, os limites na última
    ax.legend(alcas, rotulos, loc="lower right", bbox_to_anchor=(1, 1.01), ncol=3,
              frameon=True, facecolor=mc.SURFACE, edgecolor=mc.INK_MUTED, framealpha=1,
              fancybox=False, fontsize=7, labelcolor=mc.INK_SECONDARY, handlelength=1.2,
              handletextpad=0.35, columnspacing=0.8, borderpad=0.5,
              title="Test conditions above the limit", title_fontsize=8, alignment="left")


def main():
    tcc = "--tcc" in sys.argv
    if tcc:
        # Fonte padrão (DejaVu Sans, TrueType) embutida como Type 42 em vez de Type 3
        plt.rcParams["pdf.fonttype"] = 42
    mc.NOMES.update(mc.LETRAS)
    mc.NOMES.update(LETRAS_NOVAS)
    circuitos = {n: (*ks, *(k for k, m in NOVAS.items() if m == n)) for n, ks in CIRCUITOS.items()}
    mc.CIRCUITOS = circuitos
    mc.ESTREITO.append(True)
    mc.SEM_ATRIBUTOS.update({"Matrix", "$M$, $C$"})
    v5 = [d for d in ler(V5) if d["configuracao"] in NOVAS] if NOVAS else []
    p = perdas(ler(V4) + v5, f"BCD-MMSE (iter {T})")
    occ_n = {n: ocupacao(n) for n in circuitos}
    occ_k = {k: occ_n[n] for n, ks in circuitos.items() for k in ks}
    linhas = mc.ORDENS[POR]
    paineis = mc.paineis()
    ordem = sorted([*CONFIGS, *NOVAS], key=lambda k: (paineis[k].iot_db,
                                                      paineis[k].modulation != "16QAM",
                                                      paineis[k].K))
    saida = mc.SAIDA / "por_grupo"
    saida.mkdir(parents=True, exist_ok=True)
    for g, (M, C) in GRUPOS.items():
        ks = [k for k in ordem if (paineis[k].M, paineis[k].C) == (M, C)]
        # modo escolhido com a [4] v4/v5 (35 modos); células da grade inteira, como as barras
        cel_g, modos_g = mc.modo_fixo(p, occ_k, ks, linhas, LIMITE, p_celulas=gi.Perdas())
        # Um só circuito por grupo: o rótulo da linha mostra só o modo dele
        n = next(n for n, cs in circuitos.items() if ks[0] in cs)
        modos_g = [{16: e[n], 32: e[n]} for e in modos_g]
        # Margens em polegadas, para que os três grupos fiquem com o mesmo desenho
        folga = 0.3   # colunas: espaço entre IoTh 10 e 20 dB
        largura = 2.75 + 0.7 * (len(ks) + folga)
        mc.LAYOUT.clear()
        if tcc:
            # Margem esquerda menor (título do eixo perto dos rótulos): a figura fica mais
            # estreita e, reduzida à largura do texto, sai maior
            largura -= 0.6
            esq, dir_ = 1.35, 1.35          # polegadas à esquerda e à direita do mapa
            direita = 1 - dir_ / largura
            # A legenda vai para dentro do mapa: a figura perde a faixa de baixo
            # 2026-11-11: número e símbolos mais perto, e células mais baixas (era 7,05 pol.)
            mc.LAYOUT.update(figsize=(largura, ALTURA_TCC), ncol=4, folga_ioth=folga,
                             dy_numero=-0.13, dy_simbolo=0.2,
                             margens=dict(left=0.2, right=direita, top=0.93, bottom=0.075),
                             esquerda=esq / largura, legenda_x=direita, faixa_chave=True,
                             rotulo_y=-1.1 / (largura - esq - dir_))
        else:
            mc.LAYOUT.update(figsize=(largura, 7.0), ncol=4, folga_ioth=folga,
                             margens=dict(left=0.2, right=1 - 1.0 / largura, top=0.9, bottom=0.12),
                             esquerda=1.55 / largura,
                             rotulo_y=-1.28 / (largura - 2.55))
        fig = mc.mapa_modo_fixo(cel_g, modos_g, ks, ks, T, POR, LIMITE)
        if tcc:
            fig.axes[0].set_title("", loc="left")
            legenda_no_mapa(fig)
            ampliar(fig, AMPLIA, AMPLIA_SIMBOLO)
            mapa, faixas = fig.axes[0], fig.axes[1]
            aliviar_rotulos(mapa)
            mapa.set_ylabel("Fixed-point format", color=mc.INK_SECONDARY)
            # IoTh, Modulation e K no tamanho dos rótulos dos formatos (<24,12> etc.)
            formato = next(t for t in mapa.texts if t.get_text().startswith("<"))
            for t in faixas.get_yticklabels():
                t.set_fontsize(formato.get_fontsize())
            # Sem o título "Worst SNR increase" da barra de cores
            for eixo in fig.axes[2:]:
                eixo.set_title("", loc="left")
            # Barra de cores: números no tamanho dos números das células e um vão maior
            # entre ela e o mapa (2026-11-09)
            numero = formato.get_fontsize()
            for eixo in fig.axes[2:]:
                eixo.tick_params(labelsize=numero)
                b = eixo.get_position()
                eixo.set_position([b.x0 + 0.14 / largura, b.y0, b.width, b.height])
            TCC.mkdir(parents=True, exist_ok=True)
            fig.savefig(TCC / f"mapa_snr_grupo{g}.pdf", facecolor=mc.SURFACE, bbox_inches="tight")
            fig.savefig(mc.SAIDA / "por_grupo" / f"tcc_grupo{g}.png", facecolor=mc.SURFACE, dpi=150,
                        bbox_inches="tight")
            plt.close(fig)
            print(TCC / f"mapa_snr_grupo{g}.pdf")
            continue
        # Título da figura numa linha só, a partir da borda esquerda (o mapa dos grupos 2 e 3
        # é estreito demais para ele começar no eixo); M, C e M_c na linha de baixo
        fig.axes[0].set_title("", loc="left")
        fig.text(0.02, 0.975, "Worst SNR increase over float at SER = 10$^{-2}$ "
                 f"(BCD-MMSE, {mc.iteracoes(T)})", ha="left", va="top",
                 color=mc.INK_PRIMARY, fontsize=10)
        fig.text(0.02, 0.945, f"$M$ = {M}, $C$ = {C}, $M_c$ = {M // C}", ha="left", va="top",
                 color=mc.INK_PRIMARY, fontsize=10)
        nome = f"mapa_perda_modo_fixo_ate_3dB_iter{T}_grupo{g}_modo_por_grupo"
        for ext, extra in (("png", {"dpi": 300}), ("pdf", {})):
            fig.savefig(saida / f"{nome}.{ext}", facecolor=mc.SURFACE, **extra)
        plt.close(fig)
        print(saida / f"{nome}.png", "".join(mc.NOMES[k] for k in ks))


if __name__ == "__main__":
    main()
