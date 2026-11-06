#!/usr/bin/env python3
"""
Decomposição LU (Doolittle, sem pivotamento) para matrizes quadradas
N x N com entradas COMPLEXAS.

Versão EXATA (Ponto Flutuante / Float64 nativo do Python).
Nenhum truncamento, arredondamento forçado ou overflow é aplicado.
"""

import argparse
import sys

# --------------------------------------------------------------------------
# Leitura / escrita de matrizes
# --------------------------------------------------------------------------

def read_matrix(path: str):
    with open(path, "r") as f:
        tokens_by_line = [line.split() for line in f if line.strip() != ""]

    if not tokens_by_line:
        raise ValueError("Arquivo de entrada vazio.")

    n = int(tokens_by_line[0][0])
    rows = tokens_by_line[1:]

    if len(rows) != n:
        raise ValueError(f"Esperava {n} linhas de matriz, encontrou {len(rows)}.")

    matrix = []
    for i, row in enumerate(rows):
        if len(row) != n:
            raise ValueError(f"Linha {i} tem {len(row)} elementos, esperado {n}.")
        matrix.append([complex(tok) for tok in row])

    return n, matrix


def write_matrix(path: str, n: int, matrix, decimals: int):
    with open(path, "w") as f:
        f.write(f"{n}\n")
        for row in matrix:
            formatted = []
            for z in row:
                re = f"{z.real:.{decimals}f}"
                im = f"{abs(z.imag):.{decimals}f}"
                sign = "-" if z.imag < 0 else "+"
                formatted.append(f"{re}{sign}{im}j")
            f.write(" ".join(formatted) + "\n")


# --------------------------------------------------------------------------
# Decomposição LU (Matemática Exata)
# --------------------------------------------------------------------------

def lu_decompose_exact(A, n: int):
    """
    Decomposição LU usando a aritmética nativa do Python (double precision).
    """
    # Inicializa as matrizes
    L = [[0j] * n for _ in range(n)]
    U = [[A[i][j] for j in range(n)] for i in range(n)]

    for i in range(n):
        L[i][i] = 1 + 0j

    # Algoritmo clássico de eliminação
    for j in range(n):
        for i in range(j + 1, n):
            if U[j][j] == 0:
                raise ZeroDivisionError(f"Pivô nulo em U[{j}][{j}]")
                
            # Divisão exata (Ponto flutuante)
            L[i][j] = U[i][j] / U[j][j]
            
            for k in range(j, n):
                # Multiplicação e subtração exatas (Ponto flutuante)
                U[i][k] = U[i][k] - (L[i][j] * U[j][k])

    return L, U


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Decomposição LU Exata de matriz complexa NxN.")
    parser.add_argument("input", help="Arquivo de entrada com a matriz A")
    parser.add_argument("-l", "--out-l", default="L_exact.txt", help="Arquivo de saída para L")
    parser.add_argument("-u", "--out-u", default="U_exact.txt", help="Arquivo de saída para U")
    parser.add_argument("-d", "--decimals", type=int, default=8, help="Número de casas decimais para imprimir nos arquivos txt (padrão: 8)")
    args = parser.parse_args()

    n, A = read_matrix(args.input)

    try:
        L, U = lu_decompose_exact(A, n)
    except ZeroDivisionError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

    write_matrix(args.out_l, n, L, args.decimals)
    write_matrix(args.out_u, n, U, args.decimals)

    print(f"L (exata) escrita em {args.out_l}")
    print(f"U (exata) escrita em {args.out_u}")


if __name__ == "__main__":
    main()
