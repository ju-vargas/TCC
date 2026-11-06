#include "cholesky.h"
#include "cholesky_ops.h"

void G_decomposition(
    complex_fixed_t S[MATRIX_DIM],
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM]
){
    int n = MATRIX_DIM;

    //comecar com a matriz G zerada
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++){
            G[i][j].real(0);
            G[i][j].imag(0);
        }
    }

    // S eh diagonal, entao cada coluna de L eh escalada por S[coluna]
    for (int l_line = 0; l_line < n; l_line++){
        for (int l_column = 0; l_column <= l_line; l_column++){
            G[l_line][l_column] = cmul<fixed_t>(L[l_line][l_column], S[l_column]);
        }
    }
}
