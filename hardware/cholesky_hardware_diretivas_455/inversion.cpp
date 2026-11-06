#include "cholesky.h"
#include "cholesky_ops.h"

// A = G * G^H, entao A^-1 = (G^-1)^H * (G^-1).
// Com Y = G_inv:  inverse[i][j] = soma_k conj(Y[k][i]) * Y[k][j]
// Y eh triangular inferior, entao Y[k][i] so eh nao nulo para k >= i:
// a soma comeca no maior entre i e j.
void inversion(
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM]

) {
    int n = MATRIX_DIM;

    // Os lacos de line, column e k viram um laco so, para o pipeline nao
    // esvaziar a cada (line, column). O numero de termos de cada (line,
    // column) e n - max(line, column); somando todos da n(n+1)(2n+1)/6.
    const int n_terms = MATRIX_DIM * (MATRIX_DIM + 1) * (2 * MATRIX_DIM + 1) / 6;

    int line = 0;
    int column = 0;
    int k = 0;
    sum_complex_t sum_terms(0,0);

    for (int it = 0; it < n_terms; it++){
    #pragma HLS pipeline II=1
        acc_complex_t y_ki = (acc_complex_t)G_inv[k][line];
        acc_complex_t y_kj = (acc_complex_t)G_inv[k][column];
        sum_complex_t term = cmul<sum_t>(conj_t(y_ki), y_kj);
        sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                                  sum_t(sum_terms.imag() + term.imag()));

        // Ultimo termo de (line, column): grava, zera a soma e passa para o
        // proximo elemento, comecando em k = max(line, column)
        if (k == n - 1){
            inverse[line][column] = (complex_fixed_t)sum_terms;
            sum_terms = sum_complex_t(0,0);

            if (column == n - 1){
                column = 0;
                line++;
            } else {
                column++;
            }
            k = (line > column) ? line : column;
        } else {
            k++;
        }
    }
}
