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

    for (int line = 0; line < n; line++){
        for (int column = 0; column < n; column++){
            int start = (line > column) ? line : column;

            sum_complex_t sum_terms(0,0);
            for (int k = start; k < n; k++){
                acc_complex_t y_ki = (acc_complex_t)G_inv[k][line];
                acc_complex_t y_kj = (acc_complex_t)G_inv[k][column];
                sum_complex_t term = cmul<sum_t>(conj_t(y_ki), y_kj);
                sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                                          sum_t(sum_terms.imag() + term.imag()));
            }

            inverse[line][column] = (complex_fixed_t)sum_terms;
        }
    }
}
