#include "cholesky.h"

// Resolve G * G_inv = I por substituicao direta, uma coluna por vez.
// G eh triangular inferior, entao G_inv tambem eh.
void forward_substitution(
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM]
) {
    int n = MATRIX_DIM;
    complex_fixed_t aux(1,0);

    // Acima da diagonal nada eh escrito no laco abaixo, entao precisa zerar
    for (int line = 0; line < n; line++){
        for (int column = 0; column < n; column++){
            G_inv[line][column].real(0);
            G_inv[line][column].imag(0);
        }
    }

    for (int column = 0; column < n; column++){

        G_inv[column][column] = (complex_fixed_t)( (acc_complex_t)aux / (acc_complex_t)G[column][column] );

        for (int line = column + 1; line < n; line++){
            // Acumula no acumulador: sao ate n - 1 parcelas e truncar cada
            // soma parcial no fixed_t custaria precisao no resultado, que eh pequeno
            acc_complex_t sum_terms(0,0);

            for (int k = column; k < line; k++){
                sum_terms += (acc_complex_t)G[line][k] * (acc_complex_t)G_inv[k][column];
            }

            G_inv[line][column] = (complex_fixed_t)( -sum_terms / (acc_complex_t)G[line][line] );
        }

    }

}
