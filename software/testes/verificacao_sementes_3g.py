#!/usr/bin/env python3
"""
Verificação do aumento de SNR de 3G (configuração 22) no <24,12> RND_ZERO/WRAP, TDLA30-300.

O mapa (varredura [4] v5, grade curta) dá 1,91 dB e as barras (rodada [5], grade inteira
desde -20 dB) dão 2,70 dB. Os 100 canais do QuaDRiGa são os mesmos nas duas; o que muda são
os sorteios de ruído e símbolos (o simulador sorteia SNR a SNR, então outra grade dá outros
sorteios). Aqui a grade inteira roda com sementes 0 a N, em float64 e no formato, para ver a
dispersão do aumento entre sorteios. A semente 0 deve reproduzir a rodada das barras.

Só verificação: saída em resultados/5_candidatos/verificacao_sementes_3G/, fora das figuras.
Retomável: rodadas com JSON são puladas.

Uso: nice -n 19 ionice -c3 ../simulador/.venv/bin/python verificacao_sementes_3g.py [-j 2] [-n 10]
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

SAIDA = AQUI / "resultados" / "5_candidatos" / "verificacao_sementes_3G"
ROTULO, COND = "22", "TDLA30-300"
FMT = (12, 12, "AP_RND_ZERO", "AP_WRAP")
GRADE = tuple(range(-20, 11, 2))
ITERACOES = (1, 2, 3, 4)


def rodar(tarefa):
    semente, tipo = tarefa
    destino = SAIDA / f"semente_{semente:02d}_{tipo}.json"
    if destino.exists():
        return f"{destino.name}: já existe"
    from dbp_sim import hls_inverse
    from dbp_sim.m1_driver import SimConfig, run_panel
    from dbp_sim.params import M1_Driver, PANELS_BY_LABEL
    n, fc = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}[COND]
    extra = {}
    if tipo == "formato":
        I, F, q, o = FMT
        extra = dict(bcd_inverse="hls", hw_int_bits=I, hw_frac_bits=F, hw_quant=q,
                     hw_overflow=o)
    cfg = SimConfig.from_panel(PANELS_BY_LABEL[ROTULO], n_noise_samples=n, carrier_hz=fc,
                               bcd_iteration_list=ITERACOES, skip_reference_curves=True,
                               snr_db_grid=GRADE, seed=semente, **extra)
    t0 = time.time()
    ser = run_panel(cfg)
    if tipo == "formato":
        hls_inverse.close_all()
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    tmp.write_text(json.dumps({"semente": semente, "tipo": tipo, "rotulo": ROTULO,
                               "condicao": COND, "formato": list(FMT) if tipo == "formato" else None,
                               "snr_db": list(GRADE),
                               "ser": {c: list(map(float, v)) for c, v in ser.items()},
                               "segundos": round(time.time() - t0, 1)}))
    tmp.replace(destino)
    return f"{destino.name}: {time.time() - t0:.0f} s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-j", "--jobs", type=int, default=2)
    ap.add_argument("-n", "--sementes", type=int, default=10, help="sementes 0 a N")
    a = ap.parse_args()
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"
    tarefas = [(s, t) for s in range(a.sementes + 1) for t in ("float", "formato")]
    with ProcessPoolExecutor(a.jobs) as ex:
        for linha in ex.map(rodar, tarefas):
            print(linha, flush=True)
    (SAIDA / "FIM").touch()
    print("fim", time.strftime("%Y-%m-%dT%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
