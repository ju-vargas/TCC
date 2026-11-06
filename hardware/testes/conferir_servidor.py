#!/usr/bin/env python3
"""
Confere o servidor HLS (cholesky_hardware_servidor) contra uma validação já feita:
para cada matriz da seleção, a inversa que o servidor devolve ao simulador tem que
ter exatamente os bits do hw_08_inverse.bits da C-simulation, e as matrizes em que a
C-simulation dividiu por zero têm que voltar como falha (NaN).

Uso (com o Python do simulador):
    ../../software/simulador/.venv/bin/python conferir_servidor.py \\
        3_validacao_bits/validacao_<data>_16bits [--selecao 3_selecao_matrizes]
"""

import argparse
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "software" / "simulador"))

from dbp_sim import hls_inverse, hw_inverse  # noqa: E402
from inverter_no_simulador import ler_env  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("validacao")
    parser.add_argument("--selecao", default=str(AQUI / "3_selecao_matrizes"))
    args = parser.parse_args()
    validacao = Path(args.validacao)
    env = ler_env(validacao / next(p.name for p in validacao.glob("parametros*.env")))
    I, F = int(env["CHOL_INT_BITS"]), int(env["CHOL_FRAC_BITS"])
    q, o = env["CHOL_QUANT"], env["CHOL_OVERFLOW"]
    inverter = hls_inverse.make_hls_inverter(I, F, q, o)
    modelo = hw_inverse._load()
    largura, escala = I + F, 2 ** F

    contagem = {"igual": 0, "falha_nos_dois": 0, "diferente": 0}
    for bits in sorted(Path(args.selecao).glob("*/*x*/*.bits")):
        par, tam = bits.parent.parent.name, bits.parent.name
        hw = (validacao / par / "hls" / f"q_{q}__o_{o}" / tam / "matrizes" / bits.stem
              / "hw" / "hw_08_inverse.bits")
        _, A = modelo.read_float_bits(str(bits))
        inv = inverter(np.array(A, dtype=complex))
        if not hw.exists():
            contagem["falha_nos_dois" if np.isnan(inv).all() else "diferente"] += 1
            continue
        esperado = [[tuple(int(p, 2) for p in e.split(":")) for e in l.split()]
                    for l in hw.read_text().splitlines()[1:] if l.strip()]
        mascara = (1 << largura) - 1
        obtido = [[(int(round(z.real * escala)) & mascara, int(round(z.imag * escala)) & mascara)
                   for z in linha] for linha in inv] if not np.isnan(inv).any() else None
        contagem["igual" if obtido == esperado else "diferente"] += 1
    hls_inverse.close_all()
    print(f"ap_fixed<{largura},{I},{q},{o}>: {contagem}; servidor: {hls_inverse.stats}")
    sys.exit(0 if contagem["diferente"] == 0 else 1)


if __name__ == "__main__":
    main()
