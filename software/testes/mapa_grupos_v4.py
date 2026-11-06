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
"""

import matplotlib.pyplot as plt

import mapa_cenarios_v4 as mc
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


def main():
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
        cel_g, modos_g = mc.modo_fixo(p, occ_k, ks, linhas, LIMITE)
        # Um só circuito por grupo: o rótulo da linha mostra só o modo dele
        n = next(n for n, cs in circuitos.items() if ks[0] in cs)
        modos_g = [{16: e[n], 32: e[n]} for e in modos_g]
        # Margens em polegadas, para que os três grupos fiquem com o mesmo desenho
        folga = 0.3   # colunas: espaço entre IoTh 10 e 20 dB
        largura = 2.75 + 0.7 * (len(ks) + folga)
        mc.LAYOUT.clear()
        mc.LAYOUT.update(figsize=(largura, 7.0), ncol=4, folga_ioth=folga,
                         margens=dict(left=0.2, right=1 - 1.0 / largura, top=0.9, bottom=0.12),
                         esquerda=1.55 / largura,
                         rotulo_y=-1.28 / (largura - 2.55))
        fig = mc.mapa_modo_fixo(cel_g, modos_g, ks, ks, T, POR, LIMITE)
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
