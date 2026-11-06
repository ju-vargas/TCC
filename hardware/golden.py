#!/usr/bin/env python3
"""
Decomposição LU (Doolittle, sem pivotamento) para matrizes quadradas
N x N com entradas COMPLEXAS, simulando o comportamento exato do
ap_fixed do Vitis HLS (Truncamento, com Wrap-Around ou Saturação
selecionáveis) e usando registradores expandidos (32 bits) para as
multiplicações.
"""

import argparse
import sys
import math

# --------------------------------------------------------------------------
# Quantização em ponto fixo (Estilo Vitis HLS Nativo)
# --------------------------------------------------------------------------

# Políticas de estouro do ap_fixed
WRAP = "wrap"   # AP_WRAP: descarta os bits de cima, o valor dá a volta na faixa
SAT = "sat"     # AP_SAT: trava no limite da faixa

# Conta quantas vezes a saturação foi acionada, para saber se a política
# chegou a fazer diferença nesta rodada.
_sat_count = 0


def reset_sat_count():
    global _sat_count
    _sat_count = 0


def get_sat_count() -> int:
    return _sat_count


def quantize(x: float, int_bits: int, frac_bits: int, overflow: str = SAT) -> float:
    """Quantiza um número real simulando truncamento (AP_TRN) e a política de
    estouro de um tipo ap_fixed nativo: AP_WRAP ou AP_SAT.

    Em ap_fixed<W,I> a parte inteira I já inclui o bit de sinal, então
    int_bits + frac_bits = W. Para ap_fixed<16,8>: int_bits=8, frac_bits=8,
    faixa [-128, +127.99609375].
    """
    global _sat_count

    total_bits = int_bits + frac_bits
    scale = 1 << frac_bits

    # 1. Truncamento (AP_TRN): math.floor corta os bits excedentes em direção
    #    ao infinito negativo. Acontece antes do tratamento de estouro.
    val_int = math.floor(x * scale)

    max_int = (1 << (total_bits - 1)) - 1
    min_int = -(1 << (total_bits - 1))

    if overflow == SAT:
        # 2. Saturação (AP_SAT): trava no limite mais próximo
        if val_int > max_int:
            val_int = max_int
            _sat_count += 1
        elif val_int < min_int:
            val_int = min_int
            _sat_count += 1
    elif overflow == WRAP:
        # 2. Wrap-around (AP_WRAP): mantém só os bits de baixo
        mask = (1 << total_bits) - 1
        val_int = val_int & mask

        # 3. Extensão de sinal: se o MSB for 1, o número é negativo
        if val_int & (1 << (total_bits - 1)):
            val_int -= (1 << total_bits)
    else:
        raise ValueError(f"Política de estouro desconhecida: {overflow!r}")

    return val_int / scale


def quantize_complex(z: complex, int_bits: int, frac_bits: int,
                     overflow: str = SAT) -> complex:
    """Aplica quantize() separadamente à parte real e imaginária."""
    return complex(
        quantize(z.real, int_bits, frac_bits, overflow),
        quantize(z.imag, int_bits, frac_bits, overflow),
    )


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


def write_matrix(path: str, n: int, matrix, frac_bits: int):
    decimals = max(1, round(frac_bits * 0.30103) + 1) 
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
# Decomposição LU (Simulação exata do Hardware)
# --------------------------------------------------------------------------

def lu_decompose_fixed(A, n: int, int_bits: int, frac_bits: int,
                       overflow: str = SAT):
    # Inicializa as matrizes como no C++
    L = [[0j] * n for _ in range(n)]
    U = [[A[i][j] for j in range(n)] for i in range(n)] # U recebe A na inicialização

    for i in range(n):
        L[i][i] = 1 + 0j

    # Algoritmo espelhado do HLS C++
    for j in range(n):
        for i in range(j + 1, n):
            
            if U[j][j] == 0:
                raise ZeroDivisionError(f"Pivô nulo em U[{j}][{j}]")
                
            # Divisão salva no tipo original (16 bits)
            L[i][j] = quantize_complex(U[i][j] / U[j][j], int_bits, frac_bits, overflow)
            
            for k in range(j, n):
                # 1. Multiplicação protegida (Simula o cast para acc_complex_t de 32 bits)
                prod = L[i][j] * U[j][k]
                temp_mult = quantize_complex(prod, int_bits * 2, frac_bits * 2, overflow)
                
                # 2. Cast do multiplicador temporário de volta para 16 bits antes de subtrair
                temp_mult_16 = quantize_complex(temp_mult, int_bits, frac_bits, overflow)
                
                # 3. Subtração de U em 16 bits (truncamento e estouro ocorrem aqui)
                U[i][k] = quantize_complex(U[i][k] - temp_mult_16, int_bits, frac_bits, overflow)

    return L, U


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Decomposição LU de matriz complexa NxN com ponto fixo.")
    parser.add_argument("input", help="Arquivo de entrada com a matriz A")
    parser.add_argument("-l", "--out-l", default="L.txt", help="Arquivo de saída para L")
    parser.add_argument("-u", "--out-u", default="U.txt", help="Arquivo de saída para U")
    parser.add_argument("--int-bits", type=int, required=True, help="Bits inteiros")
    parser.add_argument("--frac-bits", type=int, required=True, help="Bits fracionários")
    parser.add_argument("--overflow", choices=[WRAP, SAT], default=SAT,
                        help="Política de estouro do ap_fixed (padrão: sat, "
                             "igual ao hardware atual)")
    args = parser.parse_args()

    n, A = read_matrix(args.input)

    reset_sat_count()

    # Quantiza a entrada inicial
    A = [[quantize_complex(z, args.int_bits, args.frac_bits, args.overflow) for z in row]
         for row in A]

    try:
        L, U = lu_decompose_fixed(A, n, args.int_bits, args.frac_bits, args.overflow)
    except ZeroDivisionError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

    write_matrix(args.out_l, n, L, args.frac_bits)
    write_matrix(args.out_u, n, U, args.frac_bits)

    total_bits = args.int_bits + args.frac_bits
    limite_max = ((1 << (total_bits - 1)) - 1) / (1 << args.frac_bits)
    limite_min = -(1 << (total_bits - 1)) / (1 << args.frac_bits)

    print(f"Tipo: ap_fixed<{total_bits},{args.int_bits}>, "
          f"faixa [{limite_min}, {limite_max}]")
    print(f"Política de estouro: {args.overflow}")
    if args.overflow == SAT:
        n_sat = get_sat_count()
        if n_sat == 0:
            print("Nenhum valor saturou: o resultado é igual ao de --overflow wrap.")
        else:
            print(f"ATENCAO: {n_sat} valores saturaram; a política mudou o resultado.")
    print(f"L escrita em {args.out_l}")
    print(f"U escrita em {args.out_u}")


if __name__ == "__main__":
    main()
