#ifndef CHOLESKY_H
#define CHOLESKY_H

#include "ap_fixed.h"
#include <complex>


// ---------------------------------------------------------------------------
// Parametros do hardware
// ---------------------------------------------------------------------------
// Versao que parametriza so os ap_fixed (dimensao, dados e acumulador). As
// contas usam os operadores do std::complex<ap_fixed>, entao os intermediarios
// seguem as regras do Vitis. A versao com todos os intermediarios
// configuraveis fica em ../cholesky_hardware/.
//
// Cada parametro tem um padrao aqui e pode ser trocado sem editar este arquivo,
// com -D no compilador. No Vitis, em hls_config.cfg, a mesma lista vai em
// syn.cflags (codigo do hardware) e em tb.cflags (testbench); as duas precisam
// ser iguais. Ex.: -DCHOL_N=16 -DCHOL_INT_BITS=10 -DCHOL_FRAC_BITS=12
//
// golden_cholesky.py recebe os mesmos parametros (--int-bits, --frac-bits,
// --quant, --overflow e --acc-*); a dimensao sai da matriz de entrada.

// Dimensao da matriz (M_c no BCD-MMSE)
#ifndef CHOL_N
#define CHOL_N 8
#endif

// Tipo de dados: bits inteiros (com o sinal) e fracionarios
#ifndef CHOL_INT_BITS
#define CHOL_INT_BITS 8
#endif
#ifndef CHOL_FRAC_BITS
#define CHOL_FRAC_BITS 8
#endif

// Modos do tipo de dados. AP_SAT em vez do AP_WRAP padrao: no estouro o valor
// trava no limite da faixa em vez de dar a volta e trocar de sinal. Custa um
// comparador por operacao, mas o erro fica limitado.
#ifndef CHOL_QUANT
#define CHOL_QUANT AP_TRN
#endif
#ifndef CHOL_OVERFLOW
#define CHOL_OVERFLOW AP_SAT
#endif

// Acumulador: por padrao o dobro de bits do tipo de dados e os mesmos modos
#ifndef CHOL_ACC_INT_BITS
#define CHOL_ACC_INT_BITS (2 * CHOL_INT_BITS)
#endif
#ifndef CHOL_ACC_FRAC_BITS
#define CHOL_ACC_FRAC_BITS (2 * CHOL_FRAC_BITS)
#endif
#ifndef CHOL_ACC_QUANT
#define CHOL_ACC_QUANT CHOL_QUANT
#endif
#ifndef CHOL_ACC_OVERFLOW
#define CHOL_ACC_OVERFLOW CHOL_OVERFLOW
#endif

const int MATRIX_DIM = CHOL_N;

typedef ap_fixed<CHOL_INT_BITS + CHOL_FRAC_BITS, CHOL_INT_BITS,
                 CHOL_QUANT, CHOL_OVERFLOW> fixed_t;
typedef std::complex<fixed_t> complex_fixed_t;

typedef ap_fixed<CHOL_ACC_INT_BITS + CHOL_ACC_FRAC_BITS, CHOL_ACC_INT_BITS,
                 CHOL_ACC_QUANT, CHOL_ACC_OVERFLOW> acc_fixed_t;
typedef std::complex<acc_fixed_t> acc_complex_t;

void LU_decomposition(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM]
);

void DV_decomposition(
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t V[MATRIX_DIM][MATRIX_DIM]
);

// S guarda apenas os valores da diagonal
void D_square_root(
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t S[MATRIX_DIM]
);

void G_decomposition(
    complex_fixed_t S[MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM]
);

// G * G_inv = I por substituicao direta
void forward_substitution(
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM]
);

// A^-1 = (G^-1)^H * (G^-1)
void inversion(
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]
);

void cholesky_decomposition(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t V[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t S[MATRIX_DIM],
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]
);

#endif // CHOLESKY_H
