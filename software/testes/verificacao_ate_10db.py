#!/usr/bin/env python3
"""
Verificação do × dos mapas: roda de novo, com a grade de SNR até 10 dB, os casos da [4] v4
(configurações 1 a 16) e v5 (17 a 24) em que o ponto fixo não atinge SER = 10^-2 dentro da
grade --snr-perto (que vai só de 4 a 7 dB além do cruzamento da referência float).

Só verificação: os resultados vão numa pasta separada e não entram nas figuras. Como a grade
original já vai pelo menos 4 dB além da referência, um × que passar a atingir 10^-2 continua
com aumento acima de 4 dB (os critérios de 3 dB e 0,1 dB não mudam).

Casos, na ordem:
  1. SER na última SNR abaixo de 0,5 (ainda caindo), da menor SER para a maior;
  2. SER na última SNR de 0,5 ou mais.
Ficam de fora os casos em que todas as inversões falharam no hardware.

Roda com poucos processos (padrão 2) e com prioridade baixa (nice), para não atrapalhar o
uso da máquina. Pode ser interrompido e retomado: as rodadas com JSON são puladas.

Uso (com o Python do simulador):
    nice -n 19 ../simulador/.venv/bin/python verificacao_ate_10db.py [-j 2] [--listar]
"""

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from varredura_formatos import (AQUI, grade_perto, rodar_formato,
                                rodar_referencia)

BCD1 = "BCD-MMSE (iter 1)"
VARREDURAS = AQUI / "resultados" / "4_varredura_formatos"
REFERENCIAS = {"v4_formatos_juntos_16_configs": AQUI / "resultados" / "1_referencia_float" / "curvas",
               "v5_qpsk_grupos_2_3": AQUI / "resultados" / "1_referencia_float" / "curvas_qpsk_256"}
SAIDA = VARREDURAS / "v6_verificacao_ate_10dB"
EXTRA = 20   # pontos à direita: a grade_perto corta no fim da grade da referência (10 dB)


def casos():
    """[(fase, ser_final, rotulo, condição, (I, F, q, o), pasta da referência)]"""
    lista = []
    for nome, ref in REFERENCIAS.items():
        for f in (VARREDURAS / nome / "dados").glob("*/*/*.json"):
            d = json.loads(f.read_text())
            s = d["ser"][BCD1][-1]
            if s < 1e-2 or d["falhas"] >= d["matrizes_no_hardware"]:
                continue
            lista.append((0 if s < 0.5 else 1, s, d["rotulo"], d["condicao"],
                          (d["int_bits"], d["frac_bits"], d["quant"], d["overflow"]), ref))
    return sorted(lista, key=lambda c: (c[0], c[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-j", "--jobs", type=int, default=2)
    ap.add_argument("--listar", action="store_true", help="só conta os casos")
    a = ap.parse_args()
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"
    lista = casos()
    fases = [sum(c[0] == i for c in lista) for i in (0, 1)]
    print(f"{len(lista)} casos (fase 1: {fases[0]}, fase 2: {fases[1]}) -> {SAIDA}", flush=True)
    if a.listar:
        return
    SAIDA.mkdir(parents=True, exist_ok=True)
    grades = {}
    for _, _, r, c, _, ref in lista:
        if (r, c) not in grades:
            grades[(r, c)] = grade_perto(r, c, EXTRA, ref)
    (SAIDA / "parametros.json").write_text(json.dumps({
        "extra_direita": EXTRA, "referencias": {k: str(v) for k, v in REFERENCIAS.items()},
        "grades": {f"{r}|{c}": g for (r, c), g in grades.items()},
        "casos": [[f, s, r, c, list(fmt)] for f, s, r, c, fmt, _ in lista]}, indent=1))
    t0 = time.time()
    with ProcessPoolExecutor(a.jobs) as ex:
        for linha in ex.map(rodar_referencia, [(r, c, g, SAIDA) for (r, c), g in grades.items()]):
            print(linha, flush=True)
        # rodar_formato pula as rodadas que já têm JSON (retomada)
        pendentes = [(fmt, [(r, c)], SAIDA, False, grades) for _, _, r, c, fmt, _ in lista]
        for i, log in enumerate(ex.map(rodar_formato, pendentes), 1):
            for linha in log:
                print(linha, flush=True)
            print(f"[{i}/{len(pendentes)}] {time.time() - t0:.0f} s", flush=True)
    (SAIDA / "FIM").touch()
    print("fim", time.strftime("%Y-%m-%dT%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
