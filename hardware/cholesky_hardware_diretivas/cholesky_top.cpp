#include "cholesky.h"

// Topo da sintese: so A entra e so a inversa sai. As matrizes intermediarias
// ficam dentro da funcao e nao viram portas. As etapas sao as mesmas de
// cholesky_decomposition, na mesma ordem, entao a inversa tem os mesmos bits
// (o testbench confere).
void cholesky_inverse(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]
) {
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t S[MATRIX_DIM];
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM];

    LU_decomposition(A_matrix, L, U);
    D_extraction(U, D);
    D_square_root(D, S);
    G_decomposition(S, L, G);
    forward_substitution(G, G_inv);
    inversion(G_inv, inverse);
}
