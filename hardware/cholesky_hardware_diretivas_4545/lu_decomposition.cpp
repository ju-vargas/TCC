#include "cholesky.h"
#include "cholesky_ops.h"

void LU_decomposition(
    complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM]
) {
    int n = MATRIX_DIM;

    for (int line = 0; line < n; line++) {
        for (int column = 0; column < n; column++) {
    #pragma HLS pipeline II=1
            L[line][column].real(0);
            L[line][column].imag(0);
            U[line][column] = A_matrix[line][column];
        }
    }

    for (int line = 0; line < n; line++) {
        L[line][line].real(1);
        L[line][line].imag(0);
    }


    for (int column = 0; column < n; column++){
        for (int line = column + 1; line < n; line++){
    #pragma HLS pipeline II=1
            L[line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
                (acc_complex_t)U[line][column], (acc_complex_t)U[column][column]
                );
        }

        for (int line = column + 1; line < n; line++){
            for (int k = column; k < n; k++) {
    #pragma HLS pipeline II=1
                acc_complex_t temp_mult = cmul<acc_fixed_t>(
                    (acc_complex_t)L[line][column], (acc_complex_t)U[column][k]
                );
                complex_fixed_t t = (complex_fixed_t)temp_mult;
                U[line][k] = complex_fixed_t(fixed_t(U[line][k].real() - t.real()),
                                             fixed_t(U[line][k].imag() - t.imag()));
            }
        }
    }
}
