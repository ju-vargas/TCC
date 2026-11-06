#!/usr/bin/env python3
"""
Referência ideal (inversão em float64) das configurações 17 a 24 (QPSK com M = 256,
params.QPSK_256_PANELS), numa grade de SNR que começa mais embaixo que a das 16 configurações
(-10 a 10 dB): com QPSK e M = 256, o BCD-MMSE chega a SER = 10^-2 abaixo de -10 dB. Ela só
serve para varredura_formatos.py --snr-perto --referencia escolher as SNRs em volta do
cruzamento; a varredura simula de novo a referência nas SNRs escolhidas.

Saída, no mesmo formato de resultados/1_referencia_float/curvas (um par N, portadora por
pasta), mais a grade em "snr_db":
    resultados/1_referencia_float/curvas_qpsk_256/<condições>_N<N>_<GHz>GHz/bcd_iterations_results.json
Os resultados das 16 configurações não são tocados.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python referencia_qpsk_256.py [-j 8] [--min -20]
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

SAIDA = AQUI / "resultados" / "1_referencia_float" / "curvas_qpsk_256"
ITERACOES = (1, 2, 3, 4)


def pares():
    """{(N, portadora): [condições]}, só as condições com N > 0 (o HST fica de fora)."""
    from dbp_sim.params import M1_Driver
    grupos = {}
    for c, n, _, fc in M1_Driver.test_conditions.value:
        if n > 0:
            grupos.setdefault((n, fc), []).append(c)
    return grupos


def rodar(tarefa):
    rotulo, n, fc, grade = tarefa
    from dbp_sim.m1_driver import SimConfig, run_panel
    from dbp_sim.params import PANELS_BY_LABEL
    cfg = SimConfig.from_panel(PANELS_BY_LABEL[rotulo], n_noise_samples=n, carrier_hz=fc,
                               bcd_iteration_list=ITERACOES, snr_db_grid=grade)
    t0 = time.time()
    ser = run_panel(cfg)
    return rotulo, n, fc, {c: list(map(float, v)) for c, v in ser.items()}, time.time() - t0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count())
    parser.add_argument("--min", type=int, default=-20, help="SNR mais baixa da grade (dB)")
    args = parser.parse_args()
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"
    from dbp_sim.params import QPSK_256_PANELS
    grade = tuple(range(args.min, 11, 2))
    grupos = pares()
    tarefas = [(p.label, n, fc, grade) for (n, fc) in grupos for p in QPSK_256_PANELS]
    resultados = {}
    with ProcessPoolExecutor(args.jobs) as ex:
        for rotulo, n, fc, ser, s in ex.map(rodar, tarefas):
            resultados.setdefault((n, fc), {})[rotulo] = ser
            print(f"{rotulo} N = {n} {fc / 1e9:g} GHz: {s:.0f} s", flush=True)
    for (n, fc), por_rotulo in resultados.items():
        pasta = SAIDA / f"{'+'.join(grupos[(n, fc)])}_N{n}_{fc / 1e9:g}GHz"
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "bcd_iterations_results.json").write_text(
            json.dumps({"snr_db": list(grade), **por_rotulo}, indent=1))
        print(pasta)


if __name__ == "__main__":
    main()
