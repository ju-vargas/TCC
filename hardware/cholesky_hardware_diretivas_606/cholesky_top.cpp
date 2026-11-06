#include "cholesky.h"
#include "cholesky_ops.h"
#include "hls_math.h"

// Topo da sintese para um lote de LOTE matrizes independentes. Para cada
// matriz, as contas sao as mesmas de cholesky_decomposition, na mesma ordem,
// entao cada inversa tem os mesmos bits (o testbench confere).
//
// Com dataflow, cada etapa vira um processo, e o intervalo entre lotes e o da
// etapa mais lenta. Dentro de cada etapa:
// - as divisoes alternam entre as matrizes do lote, uma por ciclo, entao o
//   divisor com pipeline (78 ciclos de latencia) fica ocupado sem esperar o
//   resultado anterior. Ha um so divisor por etapa;
// - as multiplicacoes rodam em VIAS vias: VIAS matrizes por ciclo, cada uma no
//   seu banco de memoria (array_partition cyclic no indice da matriz). A
//   matriz m fica no banco m % VIAS, e a via p trata as matrizes g * VIAS + p.
// Cada array entre etapas tem um so produtor e um so consumidor.

static const int GRUPOS = LOTE / VIAS;

// Copia o lote da porta de entrada (um elemento por ciclo) para os bancos
static void lote_ler(
    complex_fixed_t A_matrix[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t A_ch[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    for (int m = 0; m < LOTE; m++){
        for (int line = 0; line < MATRIX_DIM; line++){
            for (int column = 0; column < MATRIX_DIM; column++){
    #pragma HLS pipeline II=1
                A_ch[m][line][column] = A_matrix[m][line][column];
            }
        }
    }
}

// LU_decomposition para o lote. Entrega L e a diagonal de U (a unica parte de
// U que as etapas seguintes leem).
static void lote_lu(
    complex_fixed_t A_ch[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t Ud[LOTE][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    complex_fixed_t U[LOTE][MATRIX_DIM][MATRIX_DIM];
#pragma HLS array_partition variable=U cyclic factor=VIAS dim=1

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
            for (int column = 0; column < n; column++){
    #pragma HLS pipeline II=1
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    L[m][line][column].real(0);
                    L[m][line][column].imag(0);
                    U[m][line][column] = A_ch[m][line][column];
                }
            }
        }
    }

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
    #pragma HLS pipeline II=1
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                L[m][line][line].real(1);
                L[m][line][line].imag(0);
            }
        }
    }

    for (int column = 0; column < n; column++){
        // Divisoes da coluna, alternando as matrizes do lote
        for (int line = column + 1; line < n; line++){
            for (int m = 0; m < LOTE; m++){
    #pragma HLS pipeline II=1
                L[m][line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
                    (acc_complex_t)U[m][line][column], (acc_complex_t)U[m][column][column]);
            }
        }

        // Atualizacao das linhas, VIAS matrizes por ciclo
        for (int line = column + 1; line < n; line++){
            for (int k = column; k < n; k++){
                for (int g = 0; g < GRUPOS; g++){
    #pragma HLS pipeline II=1
                    for (int p = 0; p < VIAS; p++){
                        int m = g * VIAS + p;
                        acc_complex_t temp_mult = cmul<acc_fixed_t>(
                            (acc_complex_t)L[m][line][column], (acc_complex_t)U[m][column][k]);
                        complex_fixed_t t = (complex_fixed_t)temp_mult;
                        U[m][line][k] = complex_fixed_t(fixed_t(U[m][line][k].real() - t.real()),
                                                        fixed_t(U[m][line][k].imag() - t.imag()));
                    }
                }
            }
        }
    }

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
    #pragma HLS pipeline II=1
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                Ud[m][line] = U[m][line][line];
            }
        }
    }
}

// D_extraction, D_square_root e G_decomposition para o lote. D so guardava a
// diagonal de U, entao a raiz le direto de Ud (o mesmo valor de D[line][line]).
static void lote_g(
    complex_fixed_t Ud[LOTE][MATRIX_DIM],
    complex_fixed_t L[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    complex_fixed_t S[LOTE][MATRIX_DIM];
#pragma HLS array_partition variable=S cyclic factor=VIAS dim=1

    // Uma so raiz, alternando as matrizes do lote
    for (int line = 0; line < n; line++){
        for (int m = 0; m < LOTE; m++){
    #pragma HLS pipeline II=1
            complex_fixed_t s(0, 0);
            fixed_t d = Ud[m][line].real();
            if (d > (fixed_t)0) {
                sqrt_t d_plain = d;
                s.real(fixed_t(hls::sqrt(d_plain)));
            }
            S[m][line] = s;
        }
    }

    for (int g = 0; g < GRUPOS; g++){
        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){
    #pragma HLS pipeline II=1
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    G[m][i][j].real(0);
                    G[m][i][j].imag(0);
                }
            }
        }
    }

    for (int g = 0; g < GRUPOS; g++){
        for (int l_line = 0; l_line < n; l_line++){
            for (int l_column = 0; l_column <= l_line; l_column++){
    #pragma HLS pipeline II=1
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    G[m][l_line][l_column] = cmul<fixed_t>(L[m][l_line][l_column], S[m][l_column]);
                }
            }
        }
    }
}

// forward_substitution para o lote
static void lote_fs(
    complex_fixed_t G[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    complex_fixed_t aux(1,0);
    sum_complex_t sums[LOTE][MATRIX_DIM];
#pragma HLS array_partition variable=sums cyclic factor=VIAS dim=1
    sum_complex_t acc[VIAS];
#pragma HLS array_partition variable=acc complete

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
            for (int column = 0; column < n; column++){
    #pragma HLS pipeline II=1
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    G_inv[m][line][column].real(0);
                    G_inv[m][line][column].imag(0);
                }
            }
        }
    }

    for (int line = 0; line < n; line++){
        // Somas de cada coluna < line, com k de column ate line - 1 em ordem.
        // Os lacos de g, column e k viram um so, para o pipeline nao esvaziar
        // a cada coluna; cada via acumula num registrador.
        const int n_it = GRUPOS * line * (line + 1) / 2;
        int g = 0;
        int column = 0;
        int k = 0;
        for (int p = 0; p < VIAS; p++){
            acc[p] = sum_complex_t(0,0);
        }
        for (int it = 0; it < n_it; it++){
    #pragma HLS pipeline II=1
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                sum_complex_t term = cmul<sum_t>(
                    (acc_complex_t)G[m][line][k], (acc_complex_t)G_inv[m][k][column]);
                acc[p] = sum_complex_t(sum_t(acc[p].real() + term.real()),
                                       sum_t(acc[p].imag() + term.imag()));
            }

            if (k == line - 1){
                for (int p = 0; p < VIAS; p++){
                    sums[g * VIAS + p][column] = acc[p];
                    acc[p] = sum_complex_t(0,0);
                }
                if (column == line - 1){
                    column = 0;
                    g++;
                } else {
                    column++;
                }
                k = column;
            } else {
                k++;
            }
        }

        // Divisoes da linha, alternando as matrizes do lote; a diagonal
        // (column == line) tem numerador 1
        for (int c = 0; c <= line; c++){
            for (int m = 0; m < LOTE; m++){
    #pragma HLS pipeline II=1
                acc_complex_t num = (c == line)
                    ? (acc_complex_t)aux
                    : acc_complex_t(acc_fixed_t(-sums[m][c].real()),
                                    acc_fixed_t(-sums[m][c].imag()));
                G_inv[m][line][c] = (complex_fixed_t)cdiv<acc_fixed_t>(
                    num, (acc_complex_t)G[m][line][line]);
            }
        }
    }
}

// inversion para o lote: o mesmo laco unico sobre (line, column, k), com
// VIAS matrizes por ciclo
static void lote_inv(
    complex_fixed_t G_inv[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t Inv_ch[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    const int n_terms = MATRIX_DIM * (MATRIX_DIM + 1) * (2 * MATRIX_DIM + 1) / 6;
    sum_complex_t acc[VIAS];
#pragma HLS array_partition variable=acc complete

    for (int g = 0; g < GRUPOS; g++){
        int line = 0;
        int column = 0;
        int k = 0;
        for (int p = 0; p < VIAS; p++){
            acc[p] = sum_complex_t(0,0);
        }

        for (int it = 0; it < n_terms; it++){
    #pragma HLS pipeline II=1
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                acc_complex_t y_ki = (acc_complex_t)G_inv[m][k][line];
                acc_complex_t y_kj = (acc_complex_t)G_inv[m][k][column];
                sum_complex_t term = cmul<sum_t>(conj_t(y_ki), y_kj);
                acc[p] = sum_complex_t(sum_t(acc[p].real() + term.real()),
                                       sum_t(acc[p].imag() + term.imag()));
            }

            if (k == n - 1){
                for (int p = 0; p < VIAS; p++){
                    Inv_ch[g * VIAS + p][line][column] = (complex_fixed_t)acc[p];
                    acc[p] = sum_complex_t(0,0);
                }
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
}

// Copia o lote dos bancos para a porta de saida (um elemento por ciclo)
static void lote_gravar(
    complex_fixed_t Inv_ch[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    for (int m = 0; m < LOTE; m++){
        for (int line = 0; line < MATRIX_DIM; line++){
            for (int column = 0; column < MATRIX_DIM; column++){
    #pragma HLS pipeline II=1
                inverse[m][line][column] = Inv_ch[m][line][column];
            }
        }
    }
}

void cholesky_inverse(
    complex_fixed_t A_matrix[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS dataflow
    complex_fixed_t A_ch[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t L[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t Ud[LOTE][MATRIX_DIM];
    complex_fixed_t G[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t G_inv[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t Inv_ch[LOTE][MATRIX_DIM][MATRIX_DIM];
#pragma HLS array_partition variable=A_ch cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=L cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=Ud cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=G cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=G_inv cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=Inv_ch cyclic factor=VIAS dim=1

    lote_ler(A_matrix, A_ch);
    lote_lu(A_ch, L, Ud);
    lote_g(Ud, L, G);
    lote_fs(G, G_inv);
    lote_inv(G_inv, Inv_ch);
    lote_gravar(Inv_ch, inverse);
}
