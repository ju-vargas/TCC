#include "cholesky.h"

// Encadeia as etapas na ordem correta:
//   1. A   -> L, U
//   2. U   -> D, V
//   3. D   -> S = sqrt(D)
//   4. L,S -> G = L * S      (A = G * G^H)
//   5. G   -> G_inv          (substituicao direta)
//   6. G_inv -> inverse      (A^-1 = G_inv^H * G_inv)
// Os intermediarios sao portas de saida para que o testbench possa gravar
// o resultado de cada etapa em arquivo.
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
) {
    LU_decomposition(A_matrix, L, U);
    DV_decomposition(U, D, V);
    D_square_root(D, S);
    G_decomposition(S, L, G);
    forward_substitution(G, G_inv);
    inversion(G_inv, inverse);
}
