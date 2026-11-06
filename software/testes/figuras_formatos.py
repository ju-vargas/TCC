#!/usr/bin/env python3
"""
Figuras e tabela da varredura de formatos (varredura_formatos.py).

Para um modo (quantização, estouro), uma figura por configuração, com uma linha por
condição de teste e uma coluna por varredura:
  coluna 1: bits inteiros I variando, com F = 32 (mostra a saturação)
  coluna 2: bits fracionários F variando, com I = 14 (mostra a quantização)
Cada gráfico tem a SER do BCD-MMSE (1 iteração, ou --iteracao) com a inversa do
hardware HLS, para 5 níveis de bits, e a referência ideal (float64, linha tracejada).

Também grava <varredura>/ser_formatos.csv com todas as rodadas já feitas (todos os
modos), uma linha por (formato, modo, configuração, condição, SNR, curva).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_formatos.py resultados/4_varredura_formatos/<pasta>
        [--modo AP_TRN:AP_SAT] [--iteracao 1]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib.pyplot as plt                       # noqa: E402
import numpy as np                                    # noqa: E402

from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (INK_MUTED, INK_PRIMARY, INK_SECONDARY, SURFACE,  # noqa: E402
                              _style_axes, configuration_title)

REFERENCIA = AQUI / "resultados" / "1_referencia_float" / "curvas"

#: Rampa ordinal de um tom (validada: node scripts/validate_palette.js
#: "#86b6ef,#3987e5,#256abf,#184f95,#0d366b" --mode light --ordinal -> ALL CHECKS PASS).
#: Mais bits = mais escuro. A referência é preta e tracejada.
RAMPA = ("#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b")
MARCADORES = ("v", "^", "s", "D", "o")
REF_COR = "#0b0b0b"
VARREDURAS = (
    ("Bits inteiros (F = 32)", [(i, 32) for i in (6, 8, 10, 12, 32)], "I"),
    ("Bits fracionários (I = 14)", [(14, f) for f in (8, 10, 12, 16, 32)], "F"),
)


def ler(varredura: Path) -> list[dict]:
    return [json.loads(f.read_text()) for f in sorted(varredura.glob("dados/*/*/*.json"))]


def condicoes(rodadas) -> list[str]:
    """Condições presentes nas rodadas, da maior para a menor N e, com a mesma N, por portadora."""
    chave = {d["condicao"]: (-d["n_amostras"], d["portadora_ghz"]) for d in rodadas}
    return sorted(chave, key=chave.get)


def referencia(d, curva):
    """(SNRs, SER) da referência ideal (float64) da rodada d. Com a grade reduzida, a
    referência foi simulada junto, nas mesmas SNRs e com os mesmos sorteios
    (ser_referencia); senão vem da rodada completa em REFERENCIA."""
    if "ser_referencia" in d:
        return d["snr_db"], d["ser_referencia"][curva]
    from dbp_sim.params import M1_Driver
    n, fc = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}[d["condicao"]]
    pasta = next(p for p in REFERENCIA.iterdir()
                 if p.name.endswith(f"_N{n}_{fc / 1e9:g}GHz")
                 and d["condicao"] in p.name.split("_")[0].split("+"))
    j = json.loads((pasta / "bcd_iterations_results.json").read_text())
    return list(range(-10, 11, 2)), j[d["rotulo"]][curva]


def tabela(rodadas: list[dict], saida: Path):
    colunas = ["largura", "int_bits", "frac_bits", "quant", "overflow", "configuracao",
               "condicao", "n_amostras", "portadora_ghz", "snr_db", "curva", "ser",
               "falhas", "matrizes_no_hardware"]
    with open(saida, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=colunas)
        w.writeheader()
        for d in rodadas:
            for curva, serie in d["ser"].items():
                for s, v in zip(d["snr_db"], serie):
                    w.writerow({"largura": d["int_bits"] + d["frac_bits"],
                                "int_bits": d["int_bits"], "frac_bits": d["frac_bits"],
                                "quant": d["quant"], "overflow": d["overflow"],
                                "configuracao": d["configuracao"], "condicao": d["condicao"],
                                "n_amostras": d["n_amostras"],
                                "portadora_ghz": f"{d['portadora_ghz']:g}", "snr_db": s,
                                "curva": curva, "ser": f"{v:.6g}", "falhas": d["falhas"],
                                "matrizes_no_hardware": d["matrizes_no_hardware"]})


def figura(rodadas, painel, q, o, curva, saida: Path):
    k = TCC_CONFIGURATION[painel.label]
    indice = {(d["condicao"], d["int_bits"], d["frac_bits"]): d for d in rodadas
              if d["configuracao"] == k and d["quant"] == q and d["overflow"] == o}
    conds = condicoes(rodadas)
    fig, axes = plt.subplots(len(conds), 2, figsize=(10.5, 3.9 * len(conds)),
                             squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for li, cond in enumerate(conds):
        d_ref = next((d for (c, _, _), d in indice.items() if c == cond), None)
        if d_ref is None:
            continue
        snr_ref, ref = referencia(d_ref, curva)
        for ci, (titulo, formatos, letra) in enumerate(VARREDURAS):
            ax = axes[li][ci]
            _style_axes(ax)
            snr = None
            for j, (I, F) in enumerate(formatos):
                d = indice.get((cond, I, F))
                if d is None:
                    continue
                snr = np.asarray(d["snr_db"], dtype=float)
                y = np.asarray(d["ser"][curva], dtype=float)
                y = np.where(y <= 0, np.nan, y)
                bits = I if letra == "I" else F
                ax.plot(snr, y, color=RAMPA[j], marker=MARCADORES[j], markersize=5,
                        linewidth=1.8, markeredgecolor=SURFACE, markeredgewidth=0.6,
                        label=f"{letra} = {bits}  (ap_fixed<{I + F},{I}>)", zorder=3)
            snr_r = np.asarray(snr_ref, dtype=float)
            yr = np.where(np.asarray(ref) <= 0, np.nan, ref)
            ax.plot(snr_r, yr, color=REF_COR, linestyle="--", linewidth=1.6,
                    label="referência ideal (float64)", zorder=4)
            ax.set_xlim(snr_r[0] - 0.5, snr_r[-1] + 0.5)
            dados_cond = [d for (c, _, _), d in indice.items() if c == cond]
            if dados_cond:
                d0 = dados_cond[0]
                sub = f"$N$ = {d0['n_amostras']}, $f_c$ = {d0['portadora_ghz']:g} GHz".replace(".", ",")
            else:
                sub = cond
            ax.set_title(f"{titulo}\n{cond}: {sub}", fontsize=9, color=INK_PRIMARY, pad=6)
            if ci == 0:
                ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
            ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)
            if li == len(conds) - 1:     # legenda da coluna, embaixo, fora dos dados
                ax.legend(fontsize=8, frameon=False, labelcolor=INK_SECONDARY, ncol=2,
                          loc="upper center", bbox_to_anchor=(0.5, -0.2), columnspacing=1.2)
    fig.suptitle(f"{configuration_title(painel).replace(chr(10), ': ')}\n"
                 f"{curva}, inversa no hardware HLS, quantização {q}, estouro {o}",
                 fontsize=10.5, color=INK_PRIMARY)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    png = saida / f"configuracao_{k}.png"
    fig.savefig(png, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return png


ALVO = 1e-2          # SER em que a perda de SNR é medida
LIMIAR_DB = 0.1      # perda abaixo disso conta como "igual à referência"
DESTAQUE = "#fbd9c4"  # fundo do rótulo do melhor modo nos mapas (tom claro do laranja #eb6834)
QUANTS = ("AP_TRN", "AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF",
          "AP_RND_CONV")
OVERFLOWS = ("AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM")
#: Rampa sequencial de um tom (magnitude: perda de SNR), do claro ao escuro
SEQ = ("#e8f1fc", "#b7d3f6", "#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b")
NAO_ATINGE = "#8a8983"


def snr_no_alvo(snr, ser, alvo=ALVO):
    """Primeiro SNR em que a SER cai abaixo do alvo (interpolação em log10 da SER), ou
    None se não cai na grade."""
    snr, ser = np.asarray(snr, float), np.asarray(ser, float)
    for i in range(1, len(ser)):
        if ser[i] < alvo <= ser[i - 1]:
            a, b = np.log10(max(ser[i - 1], 1e-12)), np.log10(max(ser[i], 1e-12))
            return snr[i - 1] + (np.log10(alvo) - a) / (b - a) * (snr[i] - snr[i - 1])
    return snr[0] if ser[0] < alvo else None


def perdas(rodadas, curva):
    """{(config, cond, I, F, q, o): perda em dB, ou None se não atinge o alvo}"""
    saida = {}
    for d in rodadas:
        r = snr_no_alvo(*referencia(d, curva))
        x = snr_no_alvo(d["snr_db"], d["ser"][curva])
        saida[(d["configuracao"], d["condicao"], d["int_bits"], d["frac_bits"],
               d["quant"], d["overflow"])] = None if (x is None or r is None) else max(0.0, x - r)
    return saida


SINTESES_MODOS = AQUI.parent.parent / "hardware" / "cholesky_hardware" / "sinteses" / "modos_16x16"
GARGALO = ("LUT", "DSP", "FF", "BRAM_18K")   # recursos comparados (URAM é zero em todas)


def ocupacao() -> dict:
    """{(I, F, quant, estouro): maior % da XCU50 entre GARGALO} das sínteses HLS de
    modos_16x16 (C synthesis, sem diretivas). O total de cada recurso vem do próprio
    relatório do HLS (AvailableResources)."""
    import xml.etree.ElementTree as ET
    xml = next(SINTESES_MODOS.glob("*/csynth.xml"), None)
    if xml is None:
        return {}
    disp = {e.tag: float(e.text)
            for e in ET.parse(xml).getroot().find("AreaEstimates/AvailableResources")}
    with open(SINTESES_MODOS / "recursos.csv") as fh:
        return {(int(r["int_bits"]), int(r["frac_bits"]), r["quant"], r["overflow"]):
                max(100 * float(r[c]) / disp[c] for c in GARGALO) for r in csv.DictReader(fh)}


def texto_ocupacao(v1, v2=None):
    """Texto da maior ocupação, ou da faixa "x a y" quando v2 é dado e difere."""
    if v2 is None or f"{v1:.1f}" == f"{v2:.1f}":
        return f"{v1:.1f}%"
    return f"{v1:.1f} a {v2:.1f}%"


def mapa_calor(rodadas, painel, curva, saida: Path):
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.patches import Rectangle
    k = TCC_CONFIGURATION[painel.label]
    p = perdas(rodadas, curva)
    occ = ocupacao()
    modos = [(q, o) for q in QUANTS for o in OVERFLOWS]
    eixos = (("Bits inteiros I (F = 32)", [(i, 32) for i in (6, 8, 10, 12, 14, 16, 20, 24, 32)], 0),
             ("Bits fracionários F (I = 14)", [(14, f) for f in (4, 6, 8, 10, 12, 14, 16, 20, 24, 32)], 1))
    limites = [0, 0.1, 0.5, 1, 2, 3, 5, 10, 1e9]
    cmap, norm = ListedColormap(SEQ), BoundaryNorm(limites, len(SEQ))
    conds = condicoes(rodadas)
    # Todos os mapas têm o mesmo número de linhas e de colunas no desenho, para que as
    # células tenham o mesmo tamanho em todos os painéis e em todas as configurações
    n_o, n_q = len(OVERFLOWS), len(QUANTS)
    N_LIN, N_COL = max(n_o, n_q), max(len(e[1]) for e in eixos)

    def coluna_rotulos(ax, cabecalho, rotulos, destaques):
        """Uma coluna de tabela, com uma célula com borda por rótulo, nas mesmas linhas do
        mapa ao lado. destaques: células com fundo colorido."""
        borda = dict(fill=False, edgecolor=INK_MUTED, linewidth=0.7, clip_on=False)
        folga = 0.05
        ax.set_xlim(0, 1)
        ax.set_ylim(len(rotulos) - 0.5, -0.5)
        ax.axis("off")
        ax.add_patch(Rectangle((0, -1.15), 1, 0.65, **borda))
        ax.text(folga, -0.825, cabecalho, ha="left", va="center", fontsize=7.5,
                color=INK_PRIMARY, fontweight="bold")
        for r, (rotulo, destaque) in enumerate(zip(rotulos, destaques)):
            if destaque:
                ax.add_patch(Rectangle((0, r - 0.5), 1, 1, facecolor=DESTAQUE,
                                       edgecolor="none", clip_on=False))
            ax.add_patch(Rectangle((0, r - 0.5), 1, 1, **borda))
            ax.text(folga, r, rotulo, ha="left", va="center", fontsize=7,
                    color=INK_PRIMARY if destaque else INK_SECONDARY)

    def matriz(cond, formatos):
        """(formatos, M, cortou): M tem uma linha por modo; cortou diz se a última coluna
        é a primeira em que tudo fica abaixo de 0,05 dB."""
        M = np.full((len(modos), len(formatos)), np.nan)
        for a, (q, o) in enumerate(modos):
            for b, (I, F) in enumerate(formatos):
                v = p.get((k, cond, I, F, q, o), "falta")
                M[a, b] = -1 if v is None else (np.nan if v == "falta" else v)
        # Corta depois da primeira coluna com perda abaixo de 0,05 dB em todos os
        # modos: as colunas seguintes só repetem os zeros
        zerada = [b for b in range(len(formatos))
                  if not np.all(np.isnan(M[:, b])) and np.nanmax(M[:, b]) < 0.05
                  and np.nanmin(M[:, b]) >= 0]
        if zerada:
            return formatos[:zerada[0] + 1], M[:, :zerada[0] + 1], True
        return formatos, M, False

    def chave(M, cortou):
        """Resultado de uma linha, para comparar modos: os valores mostrados (2 casas), da
        coluna de menos bits para a de mais, sem a coluna em que tudo é zero (ali só o número
        de bits importa); × e falta contam como infinito. Menor = melhor."""
        cols = M[:, :-1] if cortou else M
        return lambda a: tuple(np.inf if (np.isnan(v) or v < 0) else round(v, 2)
                               for v in cols[a])

    texto = lambda v: "×" if v < 0 else (f"{v:.2f}" if v < 10 else f"{v:.1f}")
    valor_txt = lambda v: "" if np.isnan(v) else texto(v)

    def cor(v):
        return NAO_ATINGE if v < 0 else cmap(norm(v))

    def colapsa(M, grupos):
        """Junta as linhas de M de cada grupo numa linha só. Onde as linhas do grupo dão
        valores mostrados diferentes, a célula fica com o pior caso, o texto "x a y" e os
        extremos (menor, maior) para a cor."""
        V = np.full((len(grupos), M.shape[1]), np.nan)
        textos, extremos = {}, {}
        for g, linhas in enumerate(grupos):
            for b in range(M.shape[1]):
                col = M[linhas, b]
                if len({valor_txt(v) for v in col}) == 1:
                    V[g, b] = col[0]
                    continue
                ok = col[~np.isnan(col)]
                pior = -1 if (ok < 0).any() else ok.max()
                num = ok[ok >= 0]
                V[g, b] = pior
                textos[(g, b)] = (f"{texto(num.min()) if len(num) else '×'} a "
                                  f"{'×' if (ok < 0).any() else texto(num.max())}")
                extremos[(g, b)] = (num.min() if len(num) else -1, pior)
        return V, textos, extremos

    def ocupacoes(formatos, grupos):
        """{(linha, coluna): texto da maior ocupação} das linhas de cada grupo; a faixa
        "x a y" quando os modos do grupo diferem. Sem texto onde nenhum modo foi sintetizado."""
        textos = {}
        for g, linhas in enumerate(grupos):
            for b, (I, F) in enumerate(formatos):
                vs = [occ[(I, F) + modos[a]] for a in linhas if (I, F) + modos[a] in occ]
                if vs:
                    textos[(g, b)] = texto_ocupacao(min(vs), max(vs))
        return textos

    def desenha(ax, V, textos, extremos, ocup):
        """Uma célula com borda por valor. textos: {(linha, coluna): texto} no lugar do
        valor. extremos: {(linha, coluna): (menor, maior)}; quando os dois caem em faixas
        de cor diferentes, a célula é dividida na diagonal, com a cor do menor em cima e a
        do maior embaixo. ocup: {(linha, coluna): maior ocupação}, embaixo da perda."""
        from matplotlib.patches import Polygon
        for a in range(V.shape[0]):
            for b in range(V.shape[1]):
                v = V[a, b]
                if np.isnan(v):
                    continue
                x0, x1, y0, y1 = b - 0.5, b + 0.5, a - 0.5, a + 0.5
                v1, v2 = extremos.get((a, b), (v, v))
                if cor(v1) != cor(v2):
                    ax.add_patch(Polygon([(x0, y0), (x1, y0), (x0, y1)], closed=True,
                                         facecolor=cor(v1), edgecolor="none"))
                    ax.add_patch(Polygon([(x1, y0), (x1, y1), (x0, y1)], closed=True,
                                         facecolor=cor(v2), edgecolor="none"))
                else:
                    ax.add_patch(Rectangle((x0, y0), 1, 1, facecolor=cor(v), edgecolor="none"))
                ax.add_patch(Rectangle((x0, y0), 1, 1, fill=False, edgecolor=SURFACE,
                                       linewidth=2))
                cor_txt = SURFACE if (v < 0 or v >= 2) else INK_PRIMARY
                dy = 0.17 if (a, b) in ocup else 0
                ax.text(b - 0.42, a - dy, textos.get((a, b), texto(v)), ha="left", va="center",
                        fontsize=7, color=cor_txt)
                if (a, b) in ocup:
                    ax.text(b - 0.42, a + 0.22, ocup[(a, b)], ha="left", va="center",
                            fontsize=5.5, color=cor_txt)
        ax.set_xlim(-0.5, N_COL - 0.5)
        ax.set_ylim(V.shape[0] - 0.5, -0.5)
        ax.set_facecolor(SURFACE)

    def destaques(V, cortou):
        """Modos com o melhor resultado; nenhum quando todos empatam."""
        res = [chave(V, cortou)(a) for a in range(V.shape[0])]
        melhor = min(res)
        return [False] * len(res) if all(r == melhor for r in res) else [r == melhor for r in res]

    # Colunas: rótulos do estouro, varredura de I, rótulos da quantização, varredura de F.
    # O estouro vai ao lado dos bits inteiros e a quantização ao lado dos fracionários,
    # porque é neles que cada modo age. Os rótulos ficam sempre na mesma ordem.
    # A altura da figura sai da largura de uma célula, para que as células sejam quadradas.
    # Margens em polegadas
    larguras, wspace, hspace = [0.25, 1, 0.25, 1], 0.04, 0.45
    largura_fig, topo, base = 6 * sum(larguras), 2.55, 0.6
    util = 0.98 * largura_fig
    lado = util / (sum(larguras) + wspace * (len(larguras) - 1) * np.mean(larguras)) / N_COL
    alt_eixo = N_LIN * lado
    n_c = len(conds)
    altura = n_c * alt_eixo + (n_c - 1) * hspace * alt_eixo + topo + base
    fig, eixos_fig = plt.subplots(n_c, len(larguras), figsize=(largura_fig, altura), squeeze=False,
                                  gridspec_kw={"width_ratios": larguras, "wspace": wspace})
    fig.patch.set_facecolor(SURFACE)

    def acabamento(ax, rotulos_x, titulo, cond=None):
        ax.set_xticks(range(len(rotulos_x)))
        ax.set_xticklabels(rotulos_x, fontsize=8, color=INK_SECONDARY)
        ax.set_yticks([])
        ax.set_xlabel(titulo, fontsize=9, color=INK_SECONDARY, loc="left")
        if cond:
            d0 = next((d for d in rodadas if d["condicao"] == cond), None)
            sub = (f"$N$ = {d0['n_amostras']}, $f_c$ = {d0['portadora_ghz']:g} GHz".replace(".", ",")
                   if d0 else "")
            ax.set_title(f"{cond}: {sub}", fontsize=9.5, color=INK_PRIMARY, pad=6, loc="left")
        for lado in ax.spines.values():
            lado.set_visible(False)
        ax.tick_params(length=0)

    for li, cond in enumerate(conds):
        # Varredura de I (F = 32): uma linha por estouro, juntando as quantizações.
        # Varredura de F (I = 14): uma linha por quantização, juntando os estouros.
        fmt_i, MI, cortou_i = matriz(cond, eixos[0][1])
        fmt_f, MF, cortou_f = matriz(cond, eixos[1][1])
        grupos_i = [[q * n_o + o for q in range(n_q)] for o in range(n_o)]
        grupos_f = [[q * n_o + o for o in range(n_o)] for q in range(n_q)]
        VI, txt_i, ext_i = colapsa(MI, grupos_i)
        VF, txt_f, ext_f = colapsa(MF, grupos_f)
        coluna_rotulos(eixos_fig[li][0], "Estouro", OVERFLOWS, destaques(VI, cortou_i))
        desenha(eixos_fig[li][1], VI, txt_i, ext_i, ocupacoes(fmt_i, grupos_i))
        acabamento(eixos_fig[li][1], [str(f[0]) for f in fmt_i], eixos[0][0], cond)
        coluna_rotulos(eixos_fig[li][2], "Quantização", QUANTS, destaques(VF, cortou_f))
        desenha(eixos_fig[li][3], VF, txt_f, ext_f, ocupacoes(fmt_f, grupos_f))
        acabamento(eixos_fig[li][3], [str(f[1]) for f in fmt_f], eixos[1][0], cond)
    fig.suptitle(f"{configuration_title(painel).replace(chr(10), ': ')}\n"
                 f"Perda de SNR do {curva} em SER = $10^{{-2}}$, em dB, em relação à referência "
                 f"ideal (float64); × = não chega a $10^{{-2}}$ nas SNRs simuladas\n"
                 f"Fundo laranja no rótulo: o modo com o melhor resultado (estouro: pela varredura "
                 f"de I; quantização: pela varredura de F), comparando de menos bits para mais, "
                 f"sem contar a coluna em que tudo é zero\nFaixa \"x a y\": o outro modo muda o valor (a quantização no mapa de I, o "
                 f"estouro no mapa de F); se os dois extremos têm cores diferentes, a célula é dividida na "
                 f"diagonal (em cima, a cor do menor; embaixo, a do maior)\nEmbaixo da perda: maior ocupação da XCU50 entre LUT, DSP, FF e BRAM (síntese HLS, sem "
                 f"diretivas), no mesmo formato e modo; sem número onde o formato e o modo não foram sintetizados",
                 fontsize=10, color=INK_PRIMARY, y=1 - 0.25 / fig.get_figheight())
    # tight_layout não lida com o eixo da tabela de rótulos (desenhado fora dos limites);
    # as margens vão em polegadas, convertidas para a altura da figura
    # Legenda das cores, logo abaixo do título: uma faixa de perda por cor
    num = lambda x: f"{x:g}".replace(".", ",")
    faixas_leg = [f"< {num(limites[1])} dB"] + [
        f"{num(a)} a {num(b)} dB" for a, b in zip(limites[1:-2], limites[2:-1])] + [
        f"> {num(limites[-2])} dB"]
    alcas = [Rectangle((0, 0), 1, 1, facecolor=c, edgecolor=INK_MUTED, linewidth=0.5)
             for c in SEQ]
    alcas += [Rectangle((0, 0), 1, 1, facecolor=NAO_ATINGE, edgecolor=INK_MUTED, linewidth=0.5),
              Rectangle((0, 0), 1, 1, facecolor=DESTAQUE, edgecolor=INK_MUTED, linewidth=0.5)]
    fig.legend(alcas, faixas_leg + ["× não chega a $10^{-2}$", "rótulo do melhor modo"],
               loc="upper center", bbox_to_anchor=(0.5, 1 - 1.45 / altura), ncol=len(alcas),
               frameon=False, fontsize=9, labelcolor=INK_SECONDARY, handlelength=1.6,
               title="Perda de SNR (dB)", title_fontsize=9)
    fig.subplots_adjust(left=0.01, right=0.99, top=1 - topo / altura, bottom=base / altura,
                        hspace=hspace, wspace=wspace)
    # O mapa de I tem menos linhas que o de F: os eixos dele (e os rótulos do estouro)
    # encolhem por baixo, para que a escala de bits fique logo abaixo das células
    for linha in eixos_fig:
        for ax in linha[:2]:
            pos = ax.get_position()
            h = pos.height * n_o / N_LIN
            ax.set_position([pos.x0, pos.y1 - h, pos.width, h])
    png = saida / f"mapa_perda_configuracao_{k}.png"
    fig.savefig(png, dpi=180, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return png


def tabela_minimos(rodadas, curva, saida: Path):
    """Menor I (com F = 32) e menor F (com I = 14) com perda < LIMIAR_DB, por modo,
    configuração e condição."""
    p = perdas(rodadas, curva)
    linhas = []
    for (q, o) in [(q, o) for q in QUANTS for o in OVERFLOWS]:
        for k in sorted({d["configuracao"] for d in rodadas}):
            for cond in condicoes(rodadas):
                def menor(formatos, idx):
                    ok = [f[idx] for f in formatos
                          if p.get((k, cond, f[0], f[1], q, o)) is not None
                          and p[(k, cond, f[0], f[1], q, o)] < LIMIAR_DB]
                    return min(ok) if ok else ""
                linhas.append({"quant": q, "overflow": o, "configuracao": k, "condicao": cond,
                               "menor_I_com_F32": menor([(i, 32) for i in (6, 8, 10, 12, 14, 16, 20, 24, 32)], 0),
                               "menor_F_com_I14": menor([(14, f) for f in (4, 6, 8, 10, 12, 14, 16, 20, 24, 32)], 1)})
    with open(saida, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    return linhas


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("varredura")
    parser.add_argument("--modo", default="AP_TRN:AP_SAT")
    parser.add_argument("--iteracao", type=int, default=1)
    parser.add_argument("--mapas", action="store_true",
                        help="Também os mapas de perda de SNR dos 35 modos e a tabela do "
                             "menor formato por modo")
    args = parser.parse_args()
    varredura = Path(args.varredura)
    rodadas = ler(varredura)
    tabela(rodadas, varredura / "ser_formatos.csv")
    print(f"{varredura / 'ser_formatos.csv'}: {len(rodadas)} rodadas")
    q, o = args.modo.split(":")
    curva = f"BCD-MMSE (iter {args.iteracao})"
    saida = varredura / "figuras" / f"{q}_{o}" / f"iter{args.iteracao}"
    saida.mkdir(parents=True, exist_ok=True)
    paineis = {p.label: p for p in ALL_PANELS}
    rotulos = sorted({d["rotulo"] for d in rodadas}, key=lambda r: TCC_CONFIGURATION[r])
    for rotulo in rotulos:
        print(f"  {figura(rodadas, paineis[rotulo], q, o, curva, saida)}")
    if args.mapas:
        destino = varredura / "figuras" / f"mapas_iter{args.iteracao}"
        destino.mkdir(parents=True, exist_ok=True)
        for rotulo in rotulos:
            print(f"  {mapa_calor(rodadas, paineis[rotulo], curva, destino)}")
        tab = destino / "menor_formato_por_modo.csv"
        tabela_minimos(rodadas, curva, tab)
        print(f"  {tab}")


if __name__ == "__main__":
    main()
