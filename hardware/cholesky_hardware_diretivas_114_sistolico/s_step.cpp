#include "cholesky.h"
#include "hls_math.h"

// Para uma matriz hermitiana definida positiva a diagonal eh sempre real e positiva
// S guarda apenas os valores da diagonal
void D_square_root(
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t S[MATRIX_DIM]
){
    int n = MATRIX_DIM;

    for (int i = 0; i < n; i++){
        S[i].real(0);
        S[i].imag(0);
    }

    for (int line = 0; line < n; line++){
    #pragma HLS pipeline II=1
        fixed_t d = D[line][line].real();

        // O truncamento do ponto fixo pode empurrar um pivo quase nulo para
        // negativo; a raiz nesse caso nao existe e o valor e fixado em zero.
        if (d > (fixed_t)0) {
            // hls::sqrt so tem overload para ap_fixed<W,I> com as politicas
            // padrao, entao a raiz e calculada em sqrt_t (largura em
            // CHOL_SQRT_*, modos AP_TRN e AP_WRAP) e o resultado volta para o
            // fixed_t
            sqrt_t d_plain = d;
            S[line].real(fixed_t(hls::sqrt(d_plain)));
        }
        S[line].imag(0);
    }
}
