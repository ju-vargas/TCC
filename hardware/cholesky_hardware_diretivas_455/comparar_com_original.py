#!/usr/bin/env python3
"""
Confere que os fontes desta pasta dão a mesma inversa, bit a bit, que os fontes
originais: as mesmas matrizes de testes/3_selecao_matrizes vão para o servidor
original (../cholesky_hardware_servidor/build/, já compilado) e para um servidor
compilado agora com os fontes desta pasta. As falhas (divisão por zero) também têm
que coincidir.

Uso (com o Python do simulador, nesta pasta):
    ../../software/simulador/.venv/bin/python comparar_com_original.py \\
        [--formatos 12:10,12:12,14:14] [--modo AP_RND_ZERO:AP_WRAP] [--por-tamanho 30] [-j 4]
"""

import argparse
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TESTES = AQUI.parent / "testes"
ORIGINAL = AQUI.parent / "cholesky_hardware_servidor" / "build"
sys.path.insert(0, str(TESTES))

from conferir_nativo import inverter_todas, matrizes  # noqa: E402


def compilar_novo(I, F, q, o, n) -> Path:
    # O compilar_servidor.sh não recompila se o executável existe; os fontes mudam
    # entre rodadas, então a pasta do formato é apagada antes.
    shutil.rmtree(AQUI / "build" / f"{I}_{F}_{q}_{o}_{n}", ignore_errors=True)
    r = subprocess.run([str(AQUI / "compilar_servidor.sh"), str(I), str(F), q, o, str(n)],
                       capture_output=True, text=True, check=True)
    return Path(r.stdout.strip().splitlines()[-1])


def comparar(tarefa):
    (I, F, q, o, n), As = tarefa
    original = ORIGINAL / f"{I}_{F}_{q}_{o}_{n}"
    if not (original / "csim.exe").exists():
        return f"{I},{F},{q},{o},{n},sem_original,,"
    try:
        novo = compilar_novo(I, F, q, o, n)
    except subprocess.CalledProcessError:
        return f"{I},{F},{q},{o},{n},erro_compilacao,,"
    a = inverter_todas(original, n, F, As)
    b = inverter_todas(novo, n, F, As)
    iguais = sum(1 for x, y in zip(a, b) if (x is None and y is None) or
                 (x is not None and y is not None and (x == y).all()))
    falhas = sum(1 for x in a if x is None)
    return (f"{I},{F},{q},{o},{n},{'igual' if iguais == len(a) else 'diferente'},"
            f"{iguais}/{len(a)},{falhas}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--formatos", default="12:10,12:12,14:14",
                        help="I:F separados por vírgula (padrão: os três escolhidos)")
    parser.add_argument("--modo", default="AP_RND_ZERO:AP_WRAP")
    parser.add_argument("--por-tamanho", type=int, default=30)
    parser.add_argument("-j", "--jobs", type=int, default=4)
    args = parser.parse_args()
    q, o = args.modo.split(":")
    As = matrizes(args.por_tamanho)
    tarefas = [((I, F, q, o, n), As[n])
               for I, F in (tuple(int(x) for x in f.split(":")) for f in args.formatos.split(","))
               for n in (16, 32)]
    linhas = ["int_bits,frac_bits,quant,overflow,n,resultado,iguais,falhas"]
    with ProcessPoolExecutor(args.jobs) as ex:
        for linha in ex.map(comparar, tarefas):
            linhas.append(linha)
            print(linha, flush=True)
    dif = [l for l in linhas[1:] if ",igual," not in l]
    print(f"\n{len(linhas) - 1} casos; {len(dif)} diferentes ou com erro")
    sys.exit(1 if dif else 0)


if __name__ == "__main__":
    main()
