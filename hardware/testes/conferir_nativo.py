#!/usr/bin/env python3
"""
Confere que o servidor nativo (g++ -O2 com os cabeçalhos do Vitis) dá os mesmos bits
que o servidor compilado pela C-simulation do Vitis, para cada formato e modo pedido:
as mesmas matrizes da seleção vão para os dois, e as inversas (registradores crus) e
as falhas (divisão por zero) têm que coincidir.

Uso (com o Python do simulador):
    ../../software/simulador/.venv/bin/python conferir_nativo.py \\
        [--formatos 8:8,14:32] [--por-tamanho 30] [-j 8]
Sem --modos, usa as 35 combinações de quantização e estouro.
"""

import argparse
import itertools
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "software" / "simulador"))

from dbp_sim import hls_inverse, hw_inverse  # noqa: E402

QUANTS = ("AP_TRN", "AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF",
          "AP_RND_CONV")
OVERFLOWS = ("AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM")
COMPILAR = hls_inverse.SERVER_DIR / "compilar_servidor.sh"


def matrizes(por_tamanho: int) -> dict[int, list[np.ndarray]]:
    modelo = hw_inverse._load()
    saida = {}
    for tam, n in (("16x16", 16), ("32x32", 32)):
        arquivos = sorted(Path(AQUI / "3_selecao_matrizes").glob(f"*/{tam}/*.bits"))
        passo = max(1, len(arquivos) // por_tamanho)
        saida[n] = [np.array(modelo.read_float_bits(str(f))[1], dtype=complex)
                    for f in arquivos[::passo][:por_tamanho]]
    return saida


def inverter_todas(pasta: Path, n: int, frac: int, As) -> list:
    servidor = hls_inverse._Server(pasta, n, frac, timeout_s=60.0)
    resultado = []
    for A in As:
        inv = servidor.invert(A)
        if np.isnan(inv).any():
            resultado.append(None)
            continue
        escala = 2 ** frac
        resultado.append(np.stack([np.round(inv.real * escala), np.round(inv.imag * escala)])
                         .astype(np.int64))
    servidor._stop()
    return resultado


def conferir(tarefa):
    (I, F, q, o), As = tarefa
    linhas = []
    for n, lista in As.items():
        pastas = {}
        for modo in ("vitis", "nativo"):
            cmd = [str(COMPILAR)] + (["--vitis"] if modo == "vitis" else []) + \
                  [str(I), str(F), q, o, str(n)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                return [f"{I},{F},{q},{o},{n},erro_compilacao_{modo},,"]
            pastas[modo] = Path(r.stdout.strip().splitlines()[-1])
        v = inverter_todas(pastas["vitis"], n, F, lista)
        nt = inverter_todas(pastas["nativo"], n, F, lista)
        iguais = sum(1 for a, b in zip(v, nt) if (a is None and b is None) or
                     (a is not None and b is not None and np.array_equal(a, b)))
        falhas = sum(1 for a in v if a is None)
        linhas.append(f"{I},{F},{q},{o},{n},{'igual' if iguais == len(v) else 'diferente'},"
                      f"{iguais}/{len(v)},{falhas}")
    return linhas


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--formatos", default="8:8,14:32",
                        help="I:F separados por vírgula (padrão: 8:8,14:32)")
    parser.add_argument("--por-tamanho", type=int, default=30)
    parser.add_argument("-j", "--jobs", type=int, default=8)
    parser.add_argument("-o", "--saida", default=str(AQUI / "3_validacao_bits" / "conferir_nativo.csv"))
    args = parser.parse_args()
    As = matrizes(args.por_tamanho)
    formatos = [tuple(int(x) for x in f.split(":")) for f in args.formatos.split(",")]
    tarefas = [((I, F, q, o), As) for (I, F), q, o in itertools.product(formatos, QUANTS, OVERFLOWS)]
    linhas = ["int_bits,frac_bits,quant,overflow,n,resultado,iguais,falhas"]
    with ProcessPoolExecutor(args.jobs) as ex:
        for resultado in ex.map(conferir, tarefas):
            linhas += resultado
            for l in resultado:
                print(l, flush=True)
    Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.saida).write_text("\n".join(linhas) + "\n")
    dif = [l for l in linhas[1:] if ",igual," not in l]
    print(f"\n{len(linhas) - 1} casos; {len(dif)} diferentes ou com erro -> {args.saida}")
    sys.exit(1 if dif else 0)


if __name__ == "__main__":
    main()
