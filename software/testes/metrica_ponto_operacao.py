#!/usr/bin/env python3
"""
Métrica do ponto de operação: ordena os 80 casos (16 configurações x 5 pares (N, portadora))
pelo tamanho das matrizes G_c que o hardware inverte perto de SER = 10^-2. Escolheu as
configurações da varredura [4] v2 (1, 6, 8, 10 e 12).

Para cada caso:
  1. o ponto de operação é a SNR em que a referência ideal [1] cruza SER = 10^-2, com 1 iteração;
  2. pega todas as G_c dos dois pontos da grade em volta dele (100 realizações x C DUs por ponto);
  3. de cada matriz, o maior |parte real ou imaginária| (max_abs_parte do indice_completo.csv);
  4. desses valores, o percentil 99.
As configurações 5 a 8 (QPSK) usam as matrizes das 1 a 4: a modulação não muda G_c.

Não roda simulação: lê resultados/1_referencia_float e os indice_completo.csv de
hardware/testes/2_amostra_matrizes.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python metrica_ponto_operacao.py [-o CSV]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION  # noqa: E402
from figuras_formatos import REFERENCIA, snr_no_alvo  # noqa: E402

AMOSTRA = AQUI.parent.parent / "hardware" / "testes" / "2_amostra_matrizes"
GRADE = list(range(-10, 11, 2))
SAIDA = AQUI / "resultados" / "4_varredura_formatos" / "metrica_ponto_operacao.csv"


def casos():
    rotulo = {k: r for r, k in TCC_CONFIGURATION.items()}
    painel = {p.label: p for p in ALL_PANELS}
    for pasta in sorted(p for p in REFERENCIA.iterdir() if p.is_dir()):
        n = int(pasta.name.split("_N")[1].split("_")[0])
        fc = float(pasta.name.split("_")[-1].replace("GHz", ""))
        ref = json.loads((pasta / "bcd_iterations_results.json").read_text())
        linhas = [l for f in (AMOSTRA / f"amostras{n}_fc{fc:g}GHz").glob("*/indice_completo.csv")
                  for l in csv.DictReader(open(f))]
        for k in range(1, 17):
            x = snr_no_alvo(GRADE, ref[rotulo[k]]["BCD-MMSE (iter 1)"])
            if x is None:
                continue
            lo = max([g for g in GRADE if g <= x], default=GRADE[0])
            hi = min(g for g in GRADE if g >= x)
            snrs = {lo, hi} if lo != hi else {lo, lo + 2}
            k_matriz = k - 4 if 5 <= k <= 8 else k
            v = [float(l["max_abs_parte"]) for l in linhas
                 if int(l["configuracao"]) == k_matriz and int(l["snr_db"]) in snrs]
            p = painel[rotulo[k]]
            yield {"configuracao": k, "n_amostras": n, "portadora_ghz": fc,
                   "M_c": p.M // p.C, "modulacao": p.modulation,
                   "ponto_operacao_db": round(x, 2), "snrs": "/".join(map(str, sorted(snrs))),
                   "matrizes": len(v), "gc_p99": round(float(np.percentile(v, 99)), 1)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("-o", "--saida", type=Path, default=SAIDA)
    args = parser.parse_args()
    res = sorted(casos(), key=lambda c: -c["gc_p99"])
    for pos, c in enumerate(res, 1):
        c["posicao"] = pos
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.saida, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["posicao", "configuracao", "n_amostras", "portadora_ghz",
                                          "M_c", "modulacao", "ponto_operacao_db", "snrs",
                                          "matrizes", "gc_p99"])
        w.writeheader()
        w.writerows(res)
    for c in res[:20]:
        print(f"{c['posicao']:2d}  config. {c['configuracao']:2d}  "
              f"({c['n_amostras']}; {c['portadora_ghz']:g} GHz)  p99 {c['gc_p99']:7.0f}")
    print(f"{len(res)} casos em {args.saida}")


if __name__ == "__main__":
    main()
