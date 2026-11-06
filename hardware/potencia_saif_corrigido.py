#!/usr/bin/env python3
"""
Refaz só o report_power das sínteses de referência (cholesky_hardware/sinteses/*_vivado/potencia/)
com o SAIF corrigido, sem simular de novo.

Correção: tira o "\\ " do fim dos nomes escapados no SAIF (ver corrigir_saif em
potencia_versoes.py). O read_saif lia esse fim como um caractere nulo, e essas redes ficavam sem
atividade (81% a 86% de redes casadas). No 24-12 16 x 16, com a correção, 100%.

Não apaga nada: para cada cenário do potencia.csv grava atividade_<cenário>_corrigido.saif,
potencia_<cenário>_corrigido.rpt e vivado_<cenário>_corrigido.log, e a tabela vai para
potencia_corrigido.csv (mesmas colunas). Usa o potencia.tcl de cada pasta (o mesmo dcp roteado).
Uso (em hardware/):
    python3 potencia_saif_corrigido.py [--nucleos 4-5] [--sinteses 24-12_16x16_RND_ZERO_WRAP_vivado,...]
"""

import argparse
import csv
import re
import subprocess
from pathlib import Path

from potencia_versoes import PERIODO_NS, VITIS, ler_relatorio

HW = Path(__file__).resolve().parent
SINTESES = HW / "cholesky_hardware" / "sinteses"


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--nucleos", default="4-5")
    p.add_argument("--sinteses", default=",".join(sorted(d.name for d in SINTESES.glob("*_vivado"))))
    a = p.parse_args()
    for nome in a.sinteses.split(","):
        pot = SINTESES / nome / "potencia"
        linhas = list(csv.DictReader(open(pot / "potencia.csv")))
        tabela = []
        for r in linhas:
            cen = r["cenario"]
            t = (pot / f"atividade_{cen}.saif").read_text()
            n = t.count("\\ ")
            saif = pot / f"atividade_{cen}_corrigido.saif"
            saif.write_text(t.replace("\\ ", ""))
            rpt = pot / f"potencia_{cen}_corrigido.rpt"
            with open(pot / f"vivado_{cen}_corrigido.log", "w") as fh:
                ret = subprocess.run(
                    ["bash", "-c", f"source {VITIS} >/dev/null 2>&1 && taskset -c {a.nucleos} "
                     f"vivado -mode batch -nojournal -nolog -source {pot / 'potencia.tcl'} "
                     f"-tclargs {saif} {rpt}"],
                    cwd=pot, stdout=fh, stderr=subprocess.STDOUT).returncode
            if ret != 0:
                raise SystemExit(f"{nome} {cen}: report_power falhou (ver vivado_{cen}_corrigido.log)")
            k = int(r["matrizes"])
            duracao_ps = int(re.search(r"\(DURATION\s+(\d+)\)", t).group(1))
            d = {"cenario": cen, "matrizes": k, **ler_relatorio(rpt),
                 "ciclos_medios": round(duracao_ps / 1000 / PERIODO_NS / k)}
            d["energia_por_inversao_uj"] = round(d["dinamica_w"] * d["ciclos_medios"] * PERIODO_NS * 1e-3, 2)
            # Os ciclos sao os mesmos da tabela original (mesmo SAIF)
            assert d["ciclos_medios"] == int(r["ciclos_medios"]), (nome, cen)
            tabela.append(d)
            print(f"{nome} {cen}: {n} nomes corrigidos, {d['redes_casadas_pct']}% casadas, "
                  f"dinamica {r['dinamica_w']} -> {d['dinamica_w']} W", flush=True)
        with open(pot / "potencia_corrigido.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(tabela[0]))
            w.writeheader()
            w.writerows(tabela)


if __name__ == "__main__":
    main()
