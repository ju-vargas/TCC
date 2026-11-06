#!/usr/bin/env python3
"""
Métrica do ponto de operação para as configurações QPSK com M = 256 (17 a 24 = 2C, 2G, 2D,
2H, 3C, 3G, 3D, 3H), com o mesmo cálculo de metrica_ponto_operacao.py, e a ordenação dos
120 casos (24 configurações x 5 pares) junto com os 80 casos já calculados.

Para cada caso:
  1. o ponto de operação é a SNR em que a referência ideal cruza SER = 10^-2 com 1 iteração,
     na grade de -20 a 10 dB de resultados/1_referencia_float/curvas_qpsk_256/;
  2. roda o simulador só nos dois pontos da grade em volta dele (100 realizações x C DUs por
     ponto) e guarda cada G_c antes da inversão (exportar_matrizes.capturar);
  3. de cada matriz, o maior |parte real ou imaginária|;
  4. desses valores, o percentil 99.

Diferença do cálculo das 16 configurações: lá as matrizes vinham dos indice_completo.csv,
gerados com a grade inteira de -10 a 10 dB; aqui o simulador roda só nos dois pontos, então
a sequência aleatória é outra (mesma distribuição). Não grava matrizes.

Uso: ../simulador/.venv/bin/python metrica_ponto_operacao_qpsk256.py [-j 8]
Saídas: resultados/4_varredura_formatos/metrica_ponto_operacao_qpsk256.csv (os 40 casos) e
        resultados/4_varredura_formatos/metrica_ponto_operacao_24_configs.csv (os 120 casos).
"""

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))
sys.path.insert(0, str(AQUI.parent.parent / "hardware" / "testes"))

from dbp_sim.m1_driver import SimConfig  # noqa: E402
from dbp_sim.params import PANELS_BY_LABEL  # noqa: E402
from exportar_matrizes import capturar, grupos_de_condicoes  # noqa: E402
from figuras_formatos import snr_no_alvo  # noqa: E402

REF = AQUI / "resultados" / "1_referencia_float" / "curvas_qpsk_256"
SAIDA = AQUI / "resultados" / "4_varredura_formatos"
ANTIGA = SAIDA / "metrica_ponto_operacao.csv"
ROTULOS = [str(k) for k in range(17, 25)]


def caso(args):
    rotulo, grupo = args
    painel = PANELS_BY_LABEL[rotulo]
    n, fc = grupo["n_noise_samples"], grupo["carrier_hz"]
    pasta = next(p for p in REF.iterdir() if p.is_dir() and f"_N{n}_" in p.name
                 and p.name.endswith(f"_{fc / 1e9:g}GHz"))
    ref = json.loads((pasta / "bcd_iterations_results.json").read_text())
    grade = ref["snr_db"]
    x = snr_no_alvo(grade, ref[rotulo]["BCD-MMSE (iter 1)"])
    if x is None:
        return None
    lo = max([g for g in grade if g <= x], default=grade[0])
    hi = min(g for g in grade if g >= x)
    snrs = (lo, hi) if lo != hi else (lo, lo + 2)
    cfg = SimConfig.from_panel(painel, n_realizations=100, bcd_iteration_list=(1,),
                               n_noise_samples=n, carrier_hz=fc, snr_db_grid=snrs)
    dens = capturar(cfg)
    v = [float(np.abs(np.concatenate([d.real.ravel(), d.imag.ravel()])).max()) for d in dens]
    return {"configuracao": int(rotulo), "n_amostras": n, "portadora_ghz": fc / 1e9,
            "M_c": painel.M // painel.C, "modulacao": painel.modulation,
            "ponto_operacao_db": round(x, 2), "snrs": "/".join(str(s) for s in snrs),
            "matrizes": len(v), "gc_p99": round(float(np.percentile(v, 99)), 1)}


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("-j", type=int, default=8)
    a = p.parse_args()
    grupos = grupos_de_condicoes("all", "pior")
    tarefas = [(r, g) for r in ROTULOS for g in grupos]
    with ProcessPoolExecutor(a.j) as ex:
        novos = [d for d in ex.map(caso, tarefas) if d]
    campos = ["configuracao", "n_amostras", "portadora_ghz", "M_c", "modulacao",
              "ponto_operacao_db", "snrs", "matrizes", "gc_p99"]
    with open(SAIDA / "metrica_ponto_operacao_qpsk256.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(novos)
    antigos = [{k: v for k, v in d.items() if k != "posicao"} for d in csv.DictReader(open(ANTIGA))]
    todos = sorted(antigos + novos, key=lambda d: -float(d["gc_p99"]))
    with open(SAIDA / "metrica_ponto_operacao_24_configs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["posicao"] + campos)
        w.writeheader()
        for i, d in enumerate(todos, 1):
            w.writerow({"posicao": i, **{k: d[k] for k in campos}})
    print(f"{len(novos)} casos novos; {len(todos)} casos ordenados")


if __name__ == "__main__":
    main()
