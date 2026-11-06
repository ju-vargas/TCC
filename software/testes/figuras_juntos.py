#!/usr/bin/env python3
"""
Mapas de perda da varredura [4] v3 (formatos juntos, varredura4_juntos.sh).

Uma figura por configuração, com um mapa por par (N, portadora), lado a lado. Cada mapa
tem uma linha por modo (7 quantizações x 5 estouros) e uma coluna por formato do par.
A célula é a perda de SNR em SER = 10^-2 em relação à referência ideal (float64). O
rótulo do modo com o melhor resultado de cada par tem fundo laranja.

Também uma figura com o pior caso das configurações (mapa_perda_pior_configuracao), que
é o que vale para escolher o formato e o modo de um hardware que atende todas.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_juntos.py resultados/4_varredura_formatos/v3_formatos_juntos
        [--iteracao 1]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Rectangle

from figuras_formatos import (ALVO, DESTAQUE, INK_MUTED, INK_PRIMARY, INK_SECONDARY,
                              NAO_ATINGE, OVERFLOWS, QUANTS, SEQ, SURFACE, condicoes, ler,
                              ocupacao, perdas, texto_ocupacao)
from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION
from dbp_sim.plotting import configuration_title

LIMITES = [0, 0.1, 0.5, 1, 2, 3, 5, 10, 1e9]
CMAP, NORM = ListedColormap(SEQ), BoundaryNorm(LIMITES, len(SEQ))
MODOS = [(q, o) for q in QUANTS for o in OVERFLOWS]
# Tamanhos em polegadas: lado da célula, largura das colunas de rótulo, folgas
LADO, L_QUANT, L_ESTOURO, ENTRE, TOPO, BASE, MARGEM = 0.5, 1.05, 0.9, 0.45, 2.85, 0.3, 0.2


def texto(v):
    return "×" if v < 0 else (f"{v:.2f}" if v < 10 else f"{v:.1f}")


def cor(v):
    return NAO_ATINGE if v < 0 else CMAP(NORM(v))


def melhores(M):
    """Modos com o melhor resultado: os valores mostrados (2 casas), da coluna de menos bits
    para a de mais, sem as colunas em que todos os modos ficam abaixo de 0,05 dB (ali o
    modo não importa); × conta como infinito. Nenhum quando todos empatam."""
    cols = [b for b in range(M.shape[1]) if not (np.nanmin(M[:, b]) >= 0 and np.nanmax(M[:, b]) < 0.05)]
    chave = [tuple(np.inf if (np.isnan(v) or v < 0) else round(v, 2) for v in M[a, cols])
             for a in range(M.shape[0])]
    melhor = min(chave)
    if all(c == melhor for c in chave):
        return set()
    return {a for a, c in enumerate(chave) if c == melhor}


def painel(fig, x0, y_topo, M, formatos, titulo, texto_f=texto, cor_f=cor, claro=None,
           destaque=None, ocup=None):
    """Desenha um par: colunas de rótulo (quantização, estouro) e o mapa. x0 e y_topo em
    polegadas, a partir da esquerda e do alto da figura. texto_f e cor_f: texto e cor de
    cada valor; claro(v): o texto vai em branco; destaque: modos com fundo laranja (padrão:
    melhores(M)); ocup: matriz da maior ocupação (%), do tamanho de M, escrita embaixo do
    valor (NaN: sem número)."""
    if claro is None:
        claro = lambda v: v < 0 or v >= 2
    W, H = fig.get_figwidth(), fig.get_figheight()
    n = len(MODOS)
    largura = L_QUANT + L_ESTOURO + len(formatos) * LADO
    ax = fig.add_axes([x0 / W, (H - y_topo - n * LADO) / H, largura / W, n * LADO / H])
    # Eixo em polegadas na horizontal e em linhas na vertical
    ax.set_xlim(0, largura)
    ax.set_ylim(n, 0)
    ax.axis("off")
    borda = dict(fill=False, edgecolor=INK_MUTED, linewidth=0.7, clip_on=False)
    folga = 0.05
    # Cabeçalho: nomes das colunas de rótulo e os formatos
    for xa, la, nome in ((0, L_QUANT, "Quantização"), (L_QUANT, L_ESTOURO, "Estouro")):
        ax.add_patch(Rectangle((xa, -1.2), la, 1.2, **borda))
        ax.text(xa + folga, -0.6, nome, ha="left", va="center", fontsize=7.5,
                color=INK_PRIMARY, fontweight="bold")
    x_mapa = L_QUANT + L_ESTOURO
    for b, (I, F) in enumerate(formatos):
        ax.text(x_mapa + (b + 0.5) * LADO, -0.6, f"<{I + F},{I}>", ha="center", va="center",
                fontsize=6.5, color=INK_PRIMARY, fontweight="bold")
    ax.text(0, -1.6, titulo, ha="left", va="bottom", fontsize=9.5, color=INK_PRIMARY)
    # Rótulos: a quantização numa célula da altura dos 5 estouros
    destaque = melhores(M) if destaque is None else destaque
    n_o = len(OVERFLOWS)
    for g, q in enumerate(QUANTS):
        ax.add_patch(Rectangle((0, g * n_o), L_QUANT, n_o, **borda))
        ax.text(folga, g * n_o + n_o / 2, q, ha="left", va="center", fontsize=7,
                color=INK_SECONDARY)
    for a, (q, o) in enumerate(MODOS):
        if a in destaque:
            ax.add_patch(Rectangle((L_QUANT, a), L_ESTOURO, 1, facecolor=DESTAQUE,
                                   edgecolor="none", clip_on=False))
        ax.add_patch(Rectangle((L_QUANT, a), L_ESTOURO, 1, **borda))
        ax.text(L_QUANT + folga, a + 0.5, o, ha="left", va="center", fontsize=7,
                color=INK_PRIMARY if a in destaque else INK_SECONDARY)
    # Mapa: uma célula com borda branca por valor; borda mais larga entre quantizações
    for a in range(n):
        for b in range(len(formatos)):
            v = M[a, b]
            if np.isnan(v):
                continue
            x = x_mapa + b * LADO
            ax.add_patch(Rectangle((x, a), LADO, 1, facecolor=cor_f(v), edgecolor=SURFACE,
                                   linewidth=1.5))
            cor_txt = SURFACE if claro(v) else INK_PRIMARY
            tem = ocup is not None and not np.isnan(ocup[a, b])
            ax.text(x + 0.04, a + (0.33 if tem else 0.5), texto_f(v), ha="left", va="center",
                    fontsize=6.5, color=cor_txt)
            if tem:
                ax.text(x + 0.04, a + 0.72, texto_ocupacao(ocup[a, b]), ha="left",
                        va="center", fontsize=5, color=cor_txt)
    for g in range(1, len(QUANTS)):
        ax.plot([x_mapa, x_mapa + len(formatos) * LADO], [g * n_o, g * n_o], color=SURFACE,
                linewidth=4, solid_capstyle="butt")
    return largura


def figura(casos, titulo, saida: Path, iteracao: int):
    """casos: [(condição, formatos, M, limite_inferior)], um por par."""
    larguras = [L_QUANT + L_ESTOURO + len(c[1]) * LADO for c in casos]
    W = 2 * MARGEM + sum(larguras) + ENTRE * (len(casos) - 1)
    H = TOPO + len(MODOS) * LADO + BASE
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(SURFACE)
    x = MARGEM
    occ = ocupacao()
    for (cond, formatos, M, limite), largura in zip(casos, larguras):
        titulo_par = cond + (" *" if limite else "")
        O = np.array([[occ.get((I, F, q, o), np.nan) for I, F in formatos] for q, o in MODOS])
        painel(fig, x, TOPO, M, formatos, titulo_par, ocup=O)
        x += largura + ENTRE
    linhas = [titulo,
              f"Perda de SNR do BCD-MMSE ({iteracao} {'iterações' if iteracao > 1 else 'iteração'}) "
              f"em SER = $10^{{-2}}$, em dB, em relação à referência ideal (float64); "
              f"× = não chega a $10^{{-2}}$ nas SNRs simuladas",
              "Fundo laranja no rótulo: o modo com o melhor resultado no par, comparando do formato "
              "com menos bits para o de mais, sem contar as colunas em que todos os modos ficam "
              "abaixo de 0,05 dB",
              "Embaixo da perda: maior ocupação da XCU50 entre LUT, DSP, FF e BRAM (síntese HLS, "
              "sem diretivas), no mesmo formato e modo"]
    if any(c[3] for c in casos):
        linhas.append("* a referência já está abaixo de $10^{-2}$ no primeiro SNR simulado: "
                      "a perda é um limite inferior")
    fig.text(0.5, 1 - 0.15 / H, "\n".join(linhas), ha="center", va="top", fontsize=10,
             color=INK_PRIMARY)
    num = lambda v: f"{v:g}".replace(".", ",")
    rotulos = [f"< {num(LIMITES[1])} dB"] + [
        f"{num(a)} a {num(b)} dB" for a, b in zip(LIMITES[1:-2], LIMITES[2:-1])] + [
        f"> {num(LIMITES[-2])} dB"]
    alcas = [Rectangle((0, 0), 1, 1, facecolor=c, edgecolor=INK_MUTED, linewidth=0.5)
             for c in (*SEQ, NAO_ATINGE, DESTAQUE)]
    fig.legend(alcas, rotulos + ["× não chega a $10^{-2}$", "rótulo do melhor modo"],
               loc="upper center", bbox_to_anchor=(0.5, 1 - 1.4 / H), ncol=len(alcas),
               frameon=False, fontsize=8.5, labelcolor=INK_SECONDARY, handlelength=1.4,
               title="Perda de SNR (dB)", title_fontsize=8.5)
    fig.savefig(saida, dpi=180, facecolor=SURFACE)
    fig.savefig(saida.with_suffix(".pdf"), facecolor=SURFACE)
    plt.close(fig)
    return saida


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("varredura")
    parser.add_argument("--iteracao", type=int, default=1)
    args = parser.parse_args()
    varredura = Path(args.varredura)
    rodadas = ler(varredura)
    curva = f"BCD-MMSE (iter {args.iteracao})"
    p = perdas(rodadas, curva)
    destino = varredura / "figuras" / f"mapas_iter{args.iteracao}"
    destino.mkdir(parents=True, exist_ok=True)
    conds = condicoes(rodadas)
    formatos = {c: sorted({(d["int_bits"], d["frac_bits"]) for d in rodadas if d["condicao"] == c},
                          key=lambda f: (f[0] + f[1], f[0])) for c in conds}
    configs = sorted({d["configuracao"] for d in rodadas})
    # Referência abaixo do alvo já no primeiro SNR: a perda medida é um limite inferior
    limite = {(d["configuracao"], d["condicao"]): d["ser_referencia"][curva][0] < ALVO
              for d in rodadas}

    def matriz(k, cond):
        M = np.full((len(MODOS), len(formatos[cond])), np.nan)
        for a, (q, o) in enumerate(MODOS):
            for b, (I, F) in enumerate(formatos[cond]):
                v = p.get((k, cond, I, F, q, o), "falta")
                M[a, b] = -1 if v is None else (np.nan if v == "falta" else v)
        return M

    paineis = {TCC_CONFIGURATION[pn.label]: pn for pn in ALL_PANELS}
    for k in configs:
        casos = [(c, formatos[c], matriz(k, c), limite.get((k, c), False)) for c in conds]
        titulo = configuration_title(paineis[k]).replace("\n", ": ")
        print(f"  {figura(casos, titulo, destino / f'mapa_perda_configuracao_{k}.png', args.iteracao)}")
    # Pior caso das configurações: × ganha de qualquer número
    casos = []
    for c in conds:
        Ms = np.stack([matriz(k, c) for k in configs])
        pior = np.where((Ms < 0).any(axis=0), -1, np.nanmax(np.where(Ms < 0, np.nan, Ms), axis=0))
        casos.append((c, formatos[c], pior, any(limite.get((k, c), False) for k in configs)))
    titulo = ("Pior caso das configurações " + ", ".join(map(str, configs[:-1]))
              + f" e {configs[-1]}")
    print(f"  {figura(casos, titulo, destino / 'mapa_perda_pior_configuracao.png', args.iteracao)}")


if __name__ == "__main__":
    main()
