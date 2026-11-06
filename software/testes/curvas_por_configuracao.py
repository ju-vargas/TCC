#!/usr/bin/env python3
"""
Uma figura por configuração (Tabela tab:paineis do texto), com um gráfico para
cada par (N, portadora) da rodada: LMMSE, ZF e BCD-MMSE com 1 a 4 iterações.

Lê os bcd_iterations_results.json das pastas <condições>_N<N>_<portadora>GHz de
todas as subpastas curvas*/ de uma rodada de gerar_testes.sh, juntando as
configurações de um mesmo par que estejam em subpastas diferentes; não simula
nada. Grava em <rodada>/por_configuracao/:
  configuracao_<k>.png, .pdf  a figura
  configuracao_<k>_data.csv   os valores desenhados (tabela de apoio da figura)

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python curvas_por_configuracao.py resultados/<data-hora>
(também aceita resultados/<data-hora>/curvas)
"""

import csv
import json
import re
import sys
from pathlib import Path

SIMULADOR = Path(__file__).resolve().parent.parent / "simulador"
sys.path.insert(0, str(SIMULADOR))

import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402

from dbp_sim.m1_driver import SimConfig, curve_names  # noqa: E402
from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import (INK_PRIMARY, INK_SECONDARY, SURFACE,  # noqa: E402
                              _style_axes, configuration_title, series_styles)
from tabela_ser import pastas_de_pares                # noqa: E402

PASTA = re.compile(r"^(?P<cond>.+)_N(?P<n>\d+)_(?P<fc>[\d.]+)GHz$")
STEM = "bcd_iterations"
ITERACOES = (1, 2, 3, 4)


def ler_rodada(rodada: Path) -> list[dict]:
    """Cada par (N, portadora) da rodada, do maior N para o menor (3,5 GHz antes de 28),
    com as configurações de todas as subpastas curvas*/ juntas."""
    por_nome: dict[str, dict] = {}
    for p in pastas_de_pares(rodada):
        m = PASTA.match(p.name)
        par = por_nome.setdefault(p.name, {
            "cond": m["cond"].replace("+", ", ").replace("-media", " (média)"),
            "n": int(m["n"]), "fc": float(m["fc"]), "res": {}, "pasta": p})
        novos = json.loads((p / f"{STEM}_results.json").read_text())
        repetidos = set(novos) & set(par["res"])
        if repetidos:
            raise SystemExit(f"{p.name}: configurações {sorted(repetidos)} em mais de uma subpasta")
        par["res"].update(novos)
    pares = list(por_nome.values())
    if not pares:
        raise SystemExit(f"nenhuma pasta <condições>_N<N>_<GHz>GHz com {STEM}_results.json "
                         f"em {rodada}")
    return sorted(pares, key=lambda q: (-q["n"], q["fc"]))


def grade_snr(pasta: Path) -> np.ndarray:
    """Grade de SNR da rodada, lida do _data.csv (o --rapido usa uma grade menor)."""
    arq = pasta / f"{STEM}_data.csv"
    with open(arq, newline="") as fh:
        linhas = list(csv.DictReader(fh))
    primeiro = linhas[0]["panel"]
    return np.array([float(l["snr_db"]) for l in linhas if l["panel"] == primeiro])


def ghz(fc: float) -> str:
    return f"{fc:g}".replace(".", ",")


def figura(painel, pares, snr, curvas, estilos, saida: Path) -> Path:
    k = TCC_CONFIGURATION[painel.label]
    ncols = 3
    nrows = int(np.ceil((len(pares) + 1) / ncols))      # +1: espaço da legenda
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.1 * ncols, 3.4 * nrows),
                             squeeze=False, sharex=True, sharey=True)
    fig.patch.set_facecolor(SURFACE)

    for i, par in enumerate(pares):
        ax = axes[i // ncols][i % ncols]
        _style_axes(ax)
        ax.set_xlim(snr[0] - 0.5, snr[-1] + 0.5)
        for c in curvas:
            cor, marcador = estilos[c]
            y = np.asarray(par["res"][painel.label][c], dtype=float)
            y = np.where(y <= 0, np.nan, y)               # eixo log: sem os pontos com 0 erros
            ax.plot(snr, y, color=cor, marker=marcador, markersize=5, linewidth=1.8,
                    markeredgecolor=SURFACE, markeredgewidth=0.6, label=c, zorder=3)
        ax.set_title(f"$N$ = {par['n']}, $f_c$ = {ghz(par['fc'])} GHz\n{par['cond']}",
                     fontsize=9, color=INK_PRIMARY, pad=6)
        ax.tick_params(labelleft=True, labelbottom=True)
        if i % ncols == 0:
            ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
        ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)

    # A legenda ocupa o primeiro espaço vazio; os outros somem
    vazios = [axes[j // ncols][j % ncols] for j in range(len(pares), nrows * ncols)]
    handles, labels = axes[0][0].get_legend_handles_labels()
    vazios[0].axis("off")
    vazios[0].legend(handles, labels, loc="center", frameon=False, fontsize=10,
                     labelcolor=INK_SECONDARY, handlelength=2.4)
    for ax in vazios[1:]:
        ax.set_visible(False)

    fig.suptitle(configuration_title(painel).replace("\n", ": "), fontsize=11,
                 color=INK_PRIMARY)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    png = saida / f"configuracao_{k}.png"
    fig.savefig(png, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    fig.savefig(png.with_suffix(".pdf"), facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    with open(saida / f"configuracao_{k}_data.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["configuracao", "n_amostras", "portadora_ghz", "condicoes", "snr_db",
                    *curvas])
        for par in pares:
            for j, s in enumerate(snr):
                w.writerow([k, par["n"], f"{par['fc']:g}", par["cond"], f"{s:g}"] +
                           [f"{par['res'][painel.label][c][j]:.6g}" for c in curvas])
    return png


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    raiz = Path(sys.argv[1])
    rodada = raiz.parent if raiz.name.startswith("curvas") else raiz
    pares = ler_rodada(rodada)
    paineis = [p for p in ALL_PANELS
               if all(p.label in q["res"] for q in pares)]
    cfg = SimConfig.from_panel(paineis[0], bcd_iteration_list=ITERACOES)
    snr = grade_snr(pares[0]["pasta"])
    curvas = curve_names(cfg)
    estilos = series_styles(curvas, ITERACOES)
    saida = rodada / "por_configuracao"
    saida.mkdir(exist_ok=True)
    for painel in paineis:
        print(f"  {figura(painel, pares, snr, curvas, estilos, saida)}")


if __name__ == "__main__":
    main()
