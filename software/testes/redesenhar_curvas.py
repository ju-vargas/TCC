#!/usr/bin/env python3
"""
Redesenha as figuras de uma rodada já feita, sem simular de novo.

Lê o bcd_iterations_results.json de cada pasta <condições>_N<N>_<portadora>GHz
(saída de gerar_testes.sh) e grava de novo o .png, o .pdf e o _data.csv com o
formato atual do simulador (numeração das configurações do texto, condição de
teste, N e portadora acima da figura).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python redesenhar_curvas.py resultados/<data-hora>/curvas
"""

import csv
import json
import re
import sys
from pathlib import Path

SIMULADOR = Path(__file__).resolve().parent.parent / "simulador"
sys.path.insert(0, str(SIMULADOR))

from dbp_sim.m1_driver import SimConfig, curve_names  # noqa: E402
from dbp_sim.params import ALL_PANELS              # noqa: E402
from dbp_sim.plotting import save_figure8              # noqa: E402
from run_figure8 import figure_subtitle                # noqa: E402

PASTA = re.compile(r"^(?P<cond>.+)_N(?P<n>\d+)_(?P<fc>[\d.]+)GHz$")
STEM = "bcd_iterations"
ITERACOES = (1, 2, 3, 4)


def redesenhar(pasta: Path) -> None:
    m = PASTA.match(pasta.name)
    if not m:
        raise SystemExit(f"{pasta.name}: nome fora do padrão <condições>_N<N>_<GHz>GHz")
    resultados = json.loads((pasta / f"{STEM}_results.json").read_text())
    paineis = [p for p in ALL_PANELS if p.label in resultados]
    cfg = SimConfig.from_panel(paineis[0], n_noise_samples=int(m["n"]),
                               carrier_hz=float(m["fc"]) * 1e9,
                               bcd_iteration_list=ITERACOES)
    with open(pasta / f"{STEM}_data.csv", newline="") as fh:
        linhas = list(csv.DictReader(fh))
    snr = [float(l["snr_db"]) for l in linhas if l["panel"] == linhas[0]["panel"]]
    png, _ = save_figure8(resultados, paineis, snr, pasta,
                          subtitle=figure_subtitle(cfg, m["cond"]),
                          curves=curve_names(cfg), bcd_iterations=ITERACOES, stem=STEM)
    print(f"  {png}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    raiz = Path(sys.argv[1])
    pastas = sorted(p for p in raiz.iterdir() if (p / f"{STEM}_results.json").exists())
    if not pastas:
        raise SystemExit(f"nenhuma pasta com {STEM}_results.json em {raiz}")
    for p in pastas:
        redesenhar(p)


if __name__ == "__main__":
    main()
