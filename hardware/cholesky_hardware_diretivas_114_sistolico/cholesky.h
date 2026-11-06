#ifndef CHOLESKY_H
#define CHOLESKY_H

#include "ap_fixed.h"
#include <complex>


// ---------------------------------------------------------------------------
// Parametros do hardware
// ---------------------------------------------------------------------------
// Versao com todos os tipos configuraveis: dimensao, dados, acumulador e os
// intermediarios (cholesky_ops.h). A versao que parametriza so os ap_fixed
// (dimensao, dados e acumulador) fica em ../cholesky_hardware_apfixed/.
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

// Lote do topo cholesky_inverse: LOTE matrizes por chamada, processadas em
// VIAS vias paralelas. Cada via tem o seu divisor, as suas celulas de
// multiplicacao e a sua porta de entrada e de saida. As divisoes de cada via
// alternam entre as matrizes dela, uma por ciclo.
#ifndef CHOL_LOTE
#define CHOL_LOTE 32
#endif
#ifndef CHOL_VIAS
#define CHOL_VIAS 4
#endif
// Profundidade do pipeline (ciclos) suposta na LU e na substituicao direta.
// Cada passo (coluna da LU, linha da substituicao) dura pelo menos isso, para
// o passo seguinte so ler valores ja gravados (ver cholesky_top.cpp).
#ifndef CHOL_PROF_LU
#define CHOL_PROF_LU 110
#endif
#ifndef CHOL_PROF_FS
#define CHOL_PROF_FS 110
#endif
const int LOTE = CHOL_LOTE;
const int VIAS = CHOL_VIAS;
static_assert(CHOL_LOTE % CHOL_VIAS == 0, "LOTE precisa ser multiplo de VIAS");

typedef ap_fixed<CHOL_INT_BITS + CHOL_FRAC_BITS, CHOL_INT_BITS,
                 CHOL_QUANT, CHOL_OVERFLOW> fixed_t;
typedef std::complex<fixed_t> complex_fixed_t;

typedef ap_fixed<CHOL_ACC_INT_BITS + CHOL_ACC_FRAC_BITS, CHOL_ACC_INT_BITS,
                 CHOL_ACC_QUANT, CHOL_ACC_OVERFLOW> acc_fixed_t;
typedef std::complex<acc_fixed_t> acc_complex_t;

// ---------------------------------------------------------------------------
// Intermediarios (usados em cholesky_ops.h)
// ---------------------------------------------------------------------------
// O padrao reproduz o hardware sem tipos intermediarios: operandos dos
// multiplicadores sem conversao, produto e produto complexo do tamanho exato,
// numerador, divisor, quociente e soma iguais ao acumulador, todos com os
// modos do acumulador, e a raiz na largura dos dados. Cada um tem _INT_BITS,
// _FRAC_BITS, _QUANT e _OVERFLOW (a raiz so tem os bits).

// Operandos de cada multiplicador. Sem nenhum CHOL_MULIN_* definido, nao ha
// conversao: cada multiplicador usa o tipo dos proprios operandos (acc_fixed_t,
// ou fixed_t no g_step). Com algum definido, todos os multiplicadores recebem
// os operandos em mulin_t, e os campos que faltam vem do acumulador.
#if defined(CHOL_MULIN_INT_BITS) || defined(CHOL_MULIN_FRAC_BITS) || \
    defined(CHOL_MULIN_QUANT) || defined(CHOL_MULIN_OVERFLOW)
#define CHOL_HAS_MULIN 1
#ifndef CHOL_MULIN_INT_BITS
#define CHOL_MULIN_INT_BITS CHOL_ACC_INT_BITS
#endif
#ifndef CHOL_MULIN_FRAC_BITS
#define CHOL_MULIN_FRAC_BITS CHOL_ACC_FRAC_BITS
#endif
#ifndef CHOL_MULIN_QUANT
#define CHOL_MULIN_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_MULIN_OVERFLOW
#define CHOL_MULIN_OVERFLOW CHOL_ACC_OVERFLOW
#endif
#endif

// Cada produto real a*b
#ifndef CHOL_PROD_INT_BITS
#define CHOL_PROD_INT_BITS (2 * CHOL_ACC_INT_BITS)
#endif
#ifndef CHOL_PROD_FRAC_BITS
#define CHOL_PROD_FRAC_BITS (2 * CHOL_ACC_FRAC_BITS)
#endif
#ifndef CHOL_PROD_QUANT
#define CHOL_PROD_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_PROD_OVERFLOW
#define CHOL_PROD_OVERFLOW CHOL_ACC_OVERFLOW
#endif

// a*b - c*d e a*d + b*c do produto complexo (parte real e imaginaria)
#ifndef CHOL_CMUL_INT_BITS
#define CHOL_CMUL_INT_BITS (CHOL_PROD_INT_BITS + 1)
#endif
#ifndef CHOL_CMUL_FRAC_BITS
#define CHOL_CMUL_FRAC_BITS CHOL_PROD_FRAC_BITS
#endif
#ifndef CHOL_CMUL_QUANT
#define CHOL_CMUL_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_CMUL_OVERFLOW
#define CHOL_CMUL_OVERFLOW CHOL_ACC_OVERFLOW
#endif

// Numerador x*conj(y) da divisao complexa
#ifndef CHOL_NUM_INT_BITS
#define CHOL_NUM_INT_BITS CHOL_ACC_INT_BITS
#endif
#ifndef CHOL_NUM_FRAC_BITS
#define CHOL_NUM_FRAC_BITS CHOL_ACC_FRAC_BITS
#endif
#ifndef CHOL_NUM_QUANT
#define CHOL_NUM_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_NUM_OVERFLOW
#define CHOL_NUM_OVERFLOW CHOL_ACC_OVERFLOW
#endif

// |y|^2, o divisor da divisao complexa
#ifndef CHOL_NORM_INT_BITS
#define CHOL_NORM_INT_BITS CHOL_ACC_INT_BITS
#endif
#ifndef CHOL_NORM_FRAC_BITS
#define CHOL_NORM_FRAC_BITS CHOL_ACC_FRAC_BITS
#endif
#ifndef CHOL_NORM_QUANT
#define CHOL_NORM_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_NORM_OVERFLOW
#define CHOL_NORM_OVERFLOW CHOL_ACC_OVERFLOW
#endif

// Quociente da divisao. O dividendo e convertido para este tipo antes de
// dividir, entao o divisor gera CHOL_QUOT_FRAC_BITS bits fracionarios
// (truncados em direcao ao zero).
#ifndef CHOL_QUOT_INT_BITS
#define CHOL_QUOT_INT_BITS CHOL_ACC_INT_BITS
#endif
#ifndef CHOL_QUOT_FRAC_BITS
#define CHOL_QUOT_FRAC_BITS CHOL_ACC_FRAC_BITS
#endif
#ifndef CHOL_QUOT_QUANT
#define CHOL_QUOT_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_QUOT_OVERFLOW
#define CHOL_QUOT_OVERFLOW CHOL_ACC_OVERFLOW
#endif

// Soma acumulada (sum_terms) da substituicao direta e da inversao
#ifndef CHOL_SUM_INT_BITS
#define CHOL_SUM_INT_BITS CHOL_ACC_INT_BITS
#endif
#ifndef CHOL_SUM_FRAC_BITS
#define CHOL_SUM_FRAC_BITS CHOL_ACC_FRAC_BITS
#endif
#ifndef CHOL_SUM_QUANT
#define CHOL_SUM_QUANT CHOL_ACC_QUANT
#endif
#ifndef CHOL_SUM_OVERFLOW
#define CHOL_SUM_OVERFLOW CHOL_ACC_OVERFLOW
#endif

// Entrada e saida do hls::sqrt. So os bits: o hls::sqrt so tem overload para
// ap_fixed com os modos padrao (AP_TRN, AP_WRAP).
#ifndef CHOL_SQRT_INT_BITS
#define CHOL_SQRT_INT_BITS CHOL_INT_BITS
#endif
#ifndef CHOL_SQRT_FRAC_BITS
#define CHOL_SQRT_FRAC_BITS CHOL_FRAC_BITS
#endif

#ifdef CHOL_HAS_MULIN
typedef ap_fixed<CHOL_MULIN_INT_BITS + CHOL_MULIN_FRAC_BITS, CHOL_MULIN_INT_BITS,
                 CHOL_MULIN_QUANT, CHOL_MULIN_OVERFLOW> mulin_t;
#endif
typedef ap_fixed<CHOL_PROD_INT_BITS + CHOL_PROD_FRAC_BITS, CHOL_PROD_INT_BITS,
                 CHOL_PROD_QUANT, CHOL_PROD_OVERFLOW> prod_t;
typedef ap_fixed<CHOL_CMUL_INT_BITS + CHOL_CMUL_FRAC_BITS, CHOL_CMUL_INT_BITS,
                 CHOL_CMUL_QUANT, CHOL_CMUL_OVERFLOW> cmul_t;
typedef ap_fixed<CHOL_NUM_INT_BITS + CHOL_NUM_FRAC_BITS, CHOL_NUM_INT_BITS,
                 CHOL_NUM_QUANT, CHOL_NUM_OVERFLOW> num_t;
typedef ap_fixed<CHOL_NORM_INT_BITS + CHOL_NORM_FRAC_BITS, CHOL_NORM_INT_BITS,
                 CHOL_NORM_QUANT, CHOL_NORM_OVERFLOW> norm_t;
typedef ap_fixed<CHOL_QUOT_INT_BITS + CHOL_QUOT_FRAC_BITS, CHOL_QUOT_INT_BITS,
                 CHOL_QUOT_QUANT, CHOL_QUOT_OVERFLOW> quot_t;
typedef ap_fixed<CHOL_SUM_INT_BITS + CHOL_SUM_FRAC_BITS, CHOL_SUM_INT_BITS,
                 CHOL_SUM_QUANT, CHOL_SUM_OVERFLOW> sum_t;
typedef std::complex<sum_t> sum_complex_t;
typedef ap_fixed<CHOL_SQRT_INT_BITS + CHOL_SQRT_FRAC_BITS, CHOL_SQRT_INT_BITS> sqrt_t;

void LU_decomposition(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM]
);

// D guarda so a diagonal de U
void D_extraction(
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM]
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
    complex_fixed_t S[MATRIX_DIM],
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]
);

// Topo da sintese: as mesmas etapas, sem os intermediarios como portas, para
// um lote de LOTE matrizes independentes
void cholesky_inverse(
    complex_fixed_t A_matrix[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[LOTE][MATRIX_DIM][MATRIX_DIM]
);

#endif // CHOLESKY_H
