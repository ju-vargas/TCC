#include "cholesky.h"

// Topo da sintese: so A entra e so a inversa sai. As matrizes intermediarias
// ficam dentro da funcao e nao viram portas. As etapas sao as mesmas de
// cholesky_decomposition, na mesma ordem, entao a inversa tem os mesmos bits
// (o testbench confere).
//
// Com dataflow, cada etapa vira um processo: enquanto a inversao trabalha numa
// matriz, a substituicao direta trabalha na seguinte e a LU na outra. O
// intervalo entre inversoes passa a ser o da etapa mais lenta. Cada array
// entre etapas tem um so produtor e um so consumidor; por isso D, S e G ficam
// numa etapa so (L sai da LU e so e lida em G_decomposition).

// A LU trabalha num U local: como canal entre etapas, U teria menos portas, e
// a atualizacao (duas leituras e uma escrita de U por ciclo) cairia para
// II = 2. So a diagonal vai para a etapa seguinte, porque D_extraction so le
// U[line][line].
static void etapa_lu(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    complex_fixed_t U_local[MATRIX_DIM][MATRIX_DIM];

    LU_decomposition(A_matrix, L, U_local);

    for (int line = 0; line < MATRIX_DIM; line++){
    #pragma HLS pipeline II=1
        U[line][line] = U_local[line][line];
    }
}

static void etapa_g(
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t S[MATRIX_DIM];

    D_extraction(U, D);
    D_square_root(D, S);
    G_decomposition(S, L, G);
}

static void etapa_fs(
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    forward_substitution(G, G_inv);
}

static void etapa_inv(
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    inversion(G_inv, inverse);
}

void cholesky_inverse(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS dataflow
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM];

    etapa_lu(A_matrix, L, U);
    etapa_g(U, L, G);
    etapa_fs(G, G_inv);
    etapa_inv(G_inv, inverse);
}
