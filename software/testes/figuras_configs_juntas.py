#!/usr/bin/env python3
"""
SER x SNR com as 16 configurações num gráfico só: uma figura por formato e cenário. Para
cada configuração, LMMSE e ZF da referência float64 e BCD-MMSE com 1 iteração com a inversa
do hardware HLS no formato (rodada de figuras_modo_fixo.py). Cores das figuras
bcd_iterations: LMMSE vermelho, ZF rosa, BCD-MMSE (iter 1) laranja; a cor diz o detector,
e cada configuração é uma linha. Na segunda figura (ser_configs_agrupadas), as curvas de um
mesmo detector que ficam perto umas das outras viram uma faixa só, que vai da menor à maior
SER do grupo em cada SNR (a largura que o grupo ocupa no gráfico), com a média geométrica
por cima e os números das configurações ao lado.

Agrupamento pela distância que se vê no papel: cada curva vira uma linha no plano do
gráfico (SNR e log10 da SER, com a SER presa em 1e-4, o fundo do eixo), em polegadas do
desenho; a distância entre duas curvas é a de Hausdorff (o ponto de uma que fica mais longe
da outra). Assim, numa queda íngreme, duas curvas deslocadas de pouco na SNR ficam perto,
mesmo com SERs bem diferentes na mesma SNR. Ligação completa: todas as curvas de um grupo
ficam a no máximo LIMIAR polegadas umas das outras.

Saída: <pasta>/figuras/configs_juntas/<W>-<I>_<Q>_<O>/<cenário>_N<N>_<GHz>GHz/
ser_configs_juntas.{png,pdf} e ser_configs_agrupadas.{png,pdf} (e o _data.csv de cada).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_configs_juntas.py [pasta]
"""

import csv
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

import matplotlib                                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                         # noqa: E402
import numpy as np                                      # noqa: E402
from scipy.cluster.hierarchy import fcluster, linkage   # noqa: E402

from dbp_sim.params import M1_Driver, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (BCD_ITERATION_MARKERS, BCD_ITERATION_RAMP,  # noqa: E402
                              INK_SECONDARY, ITERATION_ZF_COLOR, SERIES_STYLE, SURFACE,
                              _style_axes)
from figuras_modo_fixo import PASTA, pasta_referencia   # noqa: E402

STEM = "ser_configs_juntas"
BCD1 = "BCD-MMSE (iter 1)"
# detector -> (cor, marcador)
CURVAS = {"LMMSE": SERIES_STYLE["LMMSE"],
          "ZF": (ITERATION_ZF_COLOR, SERIES_STYLE["ZF"][1]),
          BCD1: (BCD_ITERATION_RAMP[0], BCD_ITERATION_MARKERS[0])}
# Formatos (I, F) com AP_RND_ZERO/AP_WRAP
FORMATOS = ((12, 10), (12, 12), (14, 14))
PISO = 1e-4          # fundo do eixo; abaixo dele as curvas nao aparecem
LIMIAR = 0.35       # polegadas no desenho para juntar duas curvas (escolha visual, sem fonte)
# Polegadas por dB e por decada de SER no desenho (eixo de 7,5 x 5,5 polegadas: cerca de
# 6,4 polegadas para 22 dB e 4,3 para 4 decadas)
POL_DB = 6.4 / 22
POL_DECADA = 4.3 / 4


def main() -> None:
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else PASTA
    condicoes = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}
    for I, F in FORMATOS:
        nome = f"{I + F}-{I}_RND_ZERO_WRAP"
        for cond in sorted(p.name for p in (pasta / "dados").iterdir()):
            ref_pasta = pasta_referencia(cond)
            ref = json.loads((ref_pasta / "bcd_iterations_results.json").read_text())
            resultados, grade = {}, None
            for rotulo in ref:
                k = TCC_CONFIGURATION[rotulo]
                arq = pasta / "dados" / cond / f"configuracao_{k}" / f"{I}_{F}_AP_RND_ZERO_AP_WRAP.json"
                d = json.loads(arq.read_text())
                if grade is None:
                    grade = d["snr_db"]
                # Mesma grade e mesmos sorteios da referência: a comparação ponto a ponto vale
                assert d["snr_db"] == grade and len(ref[rotulo]["LMMSE"]) == len(grade), arq
                resultados[k] = {"LMMSE": ref[rotulo]["LMMSE"], "ZF": ref[rotulo]["ZF"],
                                 BCD1: d["ser"][BCD1]}
            saida = pasta / "figuras" / "configs_juntas" / nome / ref_pasta.name
            resultados = dict(sorted(resultados.items()))
            desenhar(resultados, grade, saida, cond, *condicoes[cond], I, F)
            desenhar_agrupado(resultados, grade, saida, cond, *condicoes[cond], I, F)


def _linha(snr: np.ndarray, ser) -> np.ndarray:
    """Pontos da curva no desenho (polegadas), com 20 pontos por segmento."""
    y = np.log10(np.maximum(np.asarray(ser, dtype=float), PISO))
    t = np.linspace(0, len(snr) - 1, 20 * (len(snr) - 1) + 1)
    i = np.arange(len(snr))
    return np.column_stack((np.interp(t, i, snr) * POL_DB, np.interp(t, i, y) * POL_DECADA))


def _hausdorff(a: np.ndarray, b: np.ndarray) -> float:
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    return max(d.min(axis=1).max(), d.min(axis=0).max())


def agrupar(curvas: dict[int, list[float]], snr) -> list[list[int]]:
    """Grupos de configuracoes com curvas a no maximo LIMIAR polegadas umas das outras."""
    ks = list(curvas)
    if len(ks) == 1:
        return [ks]
    snr = np.asarray(snr, dtype=float)
    linhas = [_linha(snr, curvas[k]) for k in ks]
    dist = [_hausdorff(linhas[i], linhas[j]) for i in range(len(ks)) for j in range(i + 1, len(ks))]
    rotulos = fcluster(linkage(dist, method="complete"), t=LIMIAR, criterion="distance")
    grupos = {}
    for k, g in zip(ks, rotulos):
        grupos.setdefault(g, []).append(k)
    return sorted(grupos.values())


def desenhar_agrupado(resultados, grade, saida: Path, cond: str, n: int, fc: float,
                      I: int, F: int) -> None:
    stem = "ser_configs_agrupadas"
    snr = np.asarray(grade, dtype=float)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    fig.patch.set_facecolor(SURFACE)
    _style_axes(ax)
    linhas = []
    for curva, (cor, marcador) in CURVAS.items():
        for i, g in enumerate(agrupar({k: r[curva] for k, r in resultados.items()}, grade)):
            ys = np.asarray([resultados[k][curva] for k in g], dtype=float)
            y = np.exp(np.mean(np.log(np.maximum(ys, PISO / 10)), axis=0))
            y = np.where(np.all(ys <= 0, axis=0), np.nan, y)   # eixo log: tira os pontos sem erro
            if len(g) > 1:
                # Faixa da menor a maior SER do grupo; SER zero vai para baixo do eixo
                baixo = np.maximum(ys, PISO / 10)
                ax.fill_between(snr, baixo.min(axis=0), baixo.max(axis=0), color=cor,
                                alpha=0.35, linewidth=0, zorder=2)
            ax.plot(snr, y, color=cor, marker=marcador, markersize=3.5, linewidth=1.1,
                    alpha=0.9, markeredgecolor=SURFACE, markeredgewidth=0.4,
                    label=curva if i == 0 else None, zorder=3)
            # Numeros das configuracoes no ultimo ponto visivel da linha
            vis = np.flatnonzero(np.isfinite(y) & (y >= PISO))
            if vis.size:
                j = vis[-1]
                ax.annotate(",".join(map(str, g)), (snr[j], y[j]), xytext=(3, 2),
                            textcoords="offset points", fontsize=6.5, color=cor, zorder=4)
            linhas.append((curva, g, y))
    ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)
    ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=3, frameon=False,
              fontsize=9.5, labelcolor=INK_SECONDARY)
    titulo = (f"Condição de teste: {cond.replace('+', ', ')}   |   $N$ = {n}   |   "
              + f"$f_c$ = {fc / 1e9:g} GHz".replace(".", ",")
              + f"\nconfigurações 1 a 16, curvas próximas no desenho juntas (número = configurações)"
              + f"\nBCD-MMSE com inversa hls ap_fixed<{I + F},{I},AP_RND_ZERO,AP_WRAP>; "
              "LMMSE e ZF em float64")
    ax.set_title(titulo, fontsize=9, color=INK_SECONDARY, pad=8)
    fig.tight_layout()
    png = saida / f"{stem}.png"
    fig.savefig(png, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(saida / f"{stem}.pdf", facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    with open(saida / f"{stem}_data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["curva", "configuracoes", *[f"{s:g}" for s in grade]])
        for curva, g, y in linhas:
            w.writerow([curva, " ".join(map(str, g)), *[f"{v:.6g}" for v in y]])
    print(png)


def desenhar(resultados, grade, saida: Path, cond: str, n: int, fc: float,
             I: int, F: int) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    snr = np.asarray(grade, dtype=float)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    fig.patch.set_facecolor(SURFACE)
    _style_axes(ax)
    for curva, (cor, marcador) in CURVAS.items():
        for i, (k, r) in enumerate(resultados.items()):
            y = np.asarray(r[curva], dtype=float)
            y = np.where(y <= 0, np.nan, y)          # eixo log: tira os pontos sem erro
            ax.plot(snr, y, color=cor, marker=marcador, markersize=3.5, linewidth=1.1,
                    alpha=0.75, markeredgecolor=SURFACE, markeredgewidth=0.4,
                    label=curva if i == 0 else None, zorder=3)
    ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)
    ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=3, frameon=False,
              fontsize=9.5, labelcolor=INK_SECONDARY)
    titulo = (f"Condição de teste: {cond.replace('+', ', ')}   |   $N$ = {n}   |   "
              + f"$f_c$ = {fc / 1e9:g} GHz".replace(".", ",")
              + f"\nconfigurações 1 a 16   |   BCD-MMSE com inversa hls "
              f"ap_fixed<{I + F},{I},AP_RND_ZERO,AP_WRAP>; LMMSE e ZF em float64")
    ax.set_title(titulo, fontsize=9, color=INK_SECONDARY, pad=8)
    fig.tight_layout()
    png = saida / f"{STEM}.png"
    fig.savefig(png, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(saida / f"{STEM}.pdf", facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    with open(saida / f"{STEM}_data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["configuracao", "curva", *[f"{s:g}" for s in grade]])
        for k, r in resultados.items():
            for curva in CURVAS:
                w.writerow([k, curva, *r[curva]])
    print(png)


if __name__ == "__main__":
    main()
