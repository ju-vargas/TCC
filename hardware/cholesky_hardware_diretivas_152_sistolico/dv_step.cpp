#include "cholesky.h"
#include "cholesky_ops.h"

// Copia a diagonal de U para D. Como U = D * L^H, a parte de U acima da
// diagonal nao e usada nas etapas seguintes.
void D_extraction(
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM]
){
    int n = MATRIX_DIM;

    for (int line = 0; line < n; line++){
        for (int column = 0; column < n; column++){
            D[line][column].real(0);
            D[line][column].imag(0);
        }
    }

    for (int line = 0; line < n; line++){
        D[line][line] = U[line][line];
    }
}
