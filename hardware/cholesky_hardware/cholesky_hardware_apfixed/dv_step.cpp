#include "cholesky.h"

// Separa U em D (diagonal) e V (triangular superior com diagonal unitaria),
// de forma que U = D * V.
void DV_decomposition(
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t V[MATRIX_DIM][MATRIX_DIM]
){
    int n = MATRIX_DIM;

    for (int line = 0; line < n; line++){
        for (int column = 0; column < n; column++){
            D[line][column].real(0);
            D[line][column].imag(0);
            V[line][column].real(0);
            V[line][column].imag(0);
        }
    }

    for (int line = 0; line < n; line++){
        D[line][line] = U[line][line];

        // A diagonal de V e 1 por definicao;
        V[line][line].real(1);
        V[line][line].imag(0);

        // U eh diagonal superior
        for (int column = line + 1; column < n; column++){
            V[line][column] = (complex_fixed_t)( (acc_complex_t)U[line][column] / (acc_complex_t)U[line][line] );
        }
    }
}
