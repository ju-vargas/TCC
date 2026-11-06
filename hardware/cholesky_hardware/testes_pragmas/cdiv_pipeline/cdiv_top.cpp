#include "cholesky.h"
#include "cholesky_ops.h"

// Teste isolado da cdiv: N_DIV divisoes independentes, com a mesma chamada da
// LU (operandos em complex_fixed_t convertidos para o acumulador). Com
// -DCDIV_PIPE o laco ganha pipeline II=1; sem ele, fica sequencial.
#define N_DIV 16

void cdiv_top(
    complex_fixed_t x[N_DIV],
    complex_fixed_t y[N_DIV],
    complex_fixed_t q[N_DIV]
) {
    for (int i = 0; i < N_DIV; i++) {
#ifdef CDIV_PIPE
#pragma HLS pipeline II=1
#endif
        q[i] = (complex_fixed_t)cdiv<acc_fixed_t>((acc_complex_t)x[i], (acc_complex_t)y[i]);
    }
}
