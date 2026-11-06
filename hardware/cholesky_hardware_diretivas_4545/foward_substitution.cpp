#include "cholesky.h"
#include "cholesky_ops.h"

// Resolve G * G_inv = I por substituicao direta.
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
    #pragma HLS pipeline II=1
            G_inv[line][column].real(0);
            G_inv[line][column].imag(0);
        }
    }

    // Uma linha por vez: as colunas sao independentes entre si, entao as
    // divisoes de uma linha entram em fila no divisor. G_inv[line][column]
    // depende de G_inv[k][column] com k < line, ja calculados nas linhas
    // anteriores.
    for (int line = 0; line < n; line++){
        sum_complex_t sums[MATRIX_DIM];

        for (int column = 0; column < line; column++){
            // Acumula em sum_t: sao ate n - 1 parcelas e truncar cada soma
            // parcial no fixed_t custaria precisao no resultado, que eh pequeno
            sum_complex_t sum_terms(0,0);

            for (int k = column; k < line; k++){
    #pragma HLS pipeline II=1
                sum_complex_t term = cmul<sum_t>(
                    (acc_complex_t)G[line][k], (acc_complex_t)G_inv[k][column]);
                sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                                          sum_t(sum_terms.imag() + term.imag()));
            }

            sums[column] = sum_terms;
        }

        // A diagonal (column == line) entra no mesmo laco, com numerador 1,
        // para haver uma so chamada da cdiv (um so divisor)
        for (int column = 0; column <= line; column++){
    #pragma HLS pipeline II=1
            acc_complex_t num = (column == line)
                ? (acc_complex_t)aux
                : acc_complex_t(acc_fixed_t(-sums[column].real()),
                                acc_fixed_t(-sums[column].imag()));
            G_inv[line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
                num, (acc_complex_t)G[line][line]);
        }
    }

}
