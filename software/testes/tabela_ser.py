#!/usr/bin/env python3
"""
Junta todas as curvas de uma rodada de gerar_testes.sh em uma tabela só,
<rodada>/ser_todas.csv, com uma linha por (configuração, condição, SNR, curva):

  configuracao, rotulo, M, C, M_c, K, r, iot_db, modulacao,
  condicoes, n_amostras, portadora_ghz, snr_db, curva, ser

Lê os bcd_iterations_results.json das pastas <condições>_N<N>_<portadora>GHz de
todas as subpastas curvas*/ da rodada. Não simula nada.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python tabela_ser.py resultados/<data-hora>
"""

import csv
import json
import re
import sys
from pathlib import Path

SIMULADOR = Path(__file__).resolve().parent.parent / "simulador"
sys.path.insert(0, str(SIMULADOR))

from dbp_sim.params import ALL_PANELS, TCC_CONFIGURATION  # noqa: E402

PASTA = re.compile(r"^(?P<cond>.+)_N(?P<n>\d+)_(?P<fc>[\d.]+)GHz$")
STEM = "bcd_iterations"
MODULACAO = {"16QAM": "16-QAM", "QPSK": "QPSK"}
COLUNAS = ["configuracao", "rotulo", "M", "C", "M_c", "K", "r", "iot_db", "modulacao",
           "condicoes", "n_amostras", "portadora_ghz", "snr_db", "curva", "ser"]


def pastas_de_pares(rodada: Path) -> list[Path]:
    """As pastas <condições>_N<N>_<GHz>GHz da rodada (em curvas*/ ou na própria pasta)."""
    raizes = [rodada] + sorted(p for p in rodada.glob("curvas*") if p.is_dir())
    return sorted(p for r in raizes for p in r.iterdir()
                  if p.is_dir() and PASTA.match(p.name) and (p / f"{STEM}_results.json").exists())


def grade_snr(pasta: Path) -> list[float]:
    with open(pasta / f"{STEM}_data.csv", newline="") as fh:
        linhas = list(csv.DictReader(fh))
    return [float(l["snr_db"]) for l in linhas if l["panel"] == linhas[0]["panel"]]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    rodada = Path(sys.argv[1])
    paineis = {p.label: p for p in ALL_PANELS}
    linhas, vistos = [], set()
    for pasta in pastas_de_pares(rodada):
        m = PASTA.match(pasta.name)
        resultados = json.loads((pasta / f"{STEM}_results.json").read_text())
        snr = grade_snr(pasta)
        for rotulo, curvas in resultados.items():
            chave = (pasta.name, rotulo)
            if chave in vistos:
                raise SystemExit(f"{pasta.name}: configuração {rotulo} aparece duas vezes")
            vistos.add(chave)
            p = paineis[rotulo]
            for curva, valores in curvas.items():
                if not isinstance(valores, list):
                    continue
                for s, ser in zip(snr, valores):
                    linhas.append({
                        "configuracao": TCC_CONFIGURATION[rotulo], "rotulo": rotulo,
                        "M": p.M, "C": p.C, "M_c": p.M // p.C, "K": p.K, "r": p.r,
                        "iot_db": f"{p.iot_db:g}", "modulacao": MODULACAO.get(p.modulation,
                                                                           p.modulation),
                        "condicoes": m["cond"].replace("+", " "), "n_amostras": int(m["n"]),
                        "portadora_ghz": m["fc"], "snr_db": f"{s:g}", "curva": curva,
                        "ser": f"{ser:.6g}"})
    linhas.sort(key=lambda l: (l["configuracao"], -l["n_amostras"], float(l["portadora_ghz"]),
                               l["curva"], float(l["snr_db"])))
    saida = rodada / "ser_todas.csv"
    with open(saida, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)
    configs = sorted({l["configuracao"] for l in linhas})
    pares = sorted({(l["n_amostras"], l["portadora_ghz"]) for l in linhas}, reverse=True)
    print(f"{saida}: {len(linhas)} linhas; configurações {configs[0]} a {configs[-1]} "
          f"({len(configs)}); {len(pares)} pares (N, portadora)")


if __name__ == "__main__":
    main()
