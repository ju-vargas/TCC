#include "cholesky.h"
#include "cholesky_ops.h"
#include "hls_math.h"

// Topo da sintese para um lote de LOTE matrizes independentes, com arranjos
// sistolicos lineares. Para cada matriz, as contas sao as mesmas de
// cholesky_decomposition, na mesma ordem, entao cada inversa tem os mesmos
// bits (o testbench confere).
//
// Com dataflow, cada etapa vira um processo, e o intervalo entre lotes e o da
// etapa mais lenta. As matrizes ficam em VIAS bancos (array_partition cyclic
// no indice da matriz): a matriz m fica no banco m % VIAS, e a via p trata as
// matrizes g * VIAS + p. Cada via tem o seu divisor.
//
// Arranjo sistolico: o laco de k (a soma ou a linha inteira) vira MATRIX_DIM
// celulas lado a lado, uma por k, com a soma parcial passando de uma celula
// para a seguinte em ordem de k. A celula fora da faixa de k so repassa a
// soma. Assim cada ciclo faz uma linha inteira da LU, ou uma soma inteira da
// substituicao direta e da inversao, com a mesma ordem de somas do original.
// As linhas e colunas ficam em MATRIX_DIM bancos (array_partition complete),
// para as celulas lerem todos os k no mesmo ciclo.
//
// Na LU e na substituicao direta, cada passo depende do anterior (a coluna c
// da LU le as linhas gravadas na coluna c - 1; a linha i da substituicao le as
// linhas < i). As matrizes do lote alternam a cada ciclo, entao a distancia
// entre a gravacao e a leitura da mesma matriz e o tamanho do passo. Os
// passos curtos (fim da LU, comeco da substituicao) sao esticados com ciclos
// vazios ate CHOL_PROF_* ciclos, e o pragma dependence diz ao HLS que nao ha
// dependencia entre iteracoes proximas. Se a profundidade real do pipeline
// passar de CHOL_PROF_*, o resultado do RTL fica errado; a co-simulacao
// confere isso.

static const int GRUPOS = LOTE / VIAS;

constexpr int maior(int a, int b) { return a > b ? a : b; }

// Ciclos da coluna c da LU: uma linha por ciclo para cada grupo. A linha
// gravada na coluna c - 1 e lida na coluna c, GRUPOS ciclos antes do fim do
// passo, por isso o minimo e CHOL_PROF_LU + GRUPOS.
constexpr int lu_passo(int c) {
    return maior((MATRIX_DIM - 1 - c) * GRUPOS, CHOL_PROF_LU + GRUPOS);
}
constexpr int lu_total(int c) {
    return c >= MATRIX_DIM - 1 ? 0 : lu_passo(c) + lu_total(c + 1);
}

// Ciclos da linha i da substituicao direta: uma coluna (0 a i) por ciclo
// para cada grupo
constexpr int fs_passo(int line) {
    return maior((line + 1) * GRUPOS, CHOL_PROF_FS);
}
constexpr int fs_total(int line) {
    return line >= MATRIX_DIM ? 0 : fs_passo(line) + fs_total(line + 1);
}

// Totais calculados na compilacao (o HLS nao aceita chamada recursiva no
// hardware)
constexpr int LU_ITER = lu_total(0);
constexpr int FS_ITER = fs_total(0);

// Copia o lote das portas de entrada (VIAS portas, um elemento por ciclo em
// cada) para os bancos
static void lote_ler(
    complex_fixed_t A_matrix[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t A_ch[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < MATRIX_DIM; line++){
            for (int column = 0; column < MATRIX_DIM; column++){
    #pragma HLS pipeline II=1
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    A_ch[m][line][column] = A_matrix[m][line][column];
                }
            }
        }
    }
}

// LU_decomposition para o lote. Cada iteracao faz uma linha de uma matriz
// numa coluna: a divisao L[line][c] = U[line][c] / U[c][c] e a atualizacao da
// linha inteira, U[line][k] -= L[line][c] * U[c][k] para k >= c, uma celula
// por k. Na coluna 0 as linhas vem direto de A. U fica em duas copias iguais
// (Ua para a linha atualizada, Ub para a linha do pivo), porque cada banco so
// tem duas portas: com uma copia, seriam duas leituras e uma gravacao.
// Entrega L abaixo da diagonal (a diagonal, 1, e posta em lote_g) e a
// diagonal de U, gravada assim que fica pronta.
static void lote_lu(
    complex_fixed_t A_ch[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t L[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t Ud[LOTE][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    complex_fixed_t Ua[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t Ub[LOTE][MATRIX_DIM][MATRIX_DIM];
#pragma HLS array_partition variable=Ua cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=Ua complete dim=3
#pragma HLS array_partition variable=Ub cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=Ub complete dim=3

    int c = 0;
    int line = 1;
    int g = 0;
    int idx = 0;
    int reais = (n - 1) * GRUPOS;
    int passo = lu_passo(0);

    for (int it = 0; it < LU_ITER; it++){
    #pragma HLS pipeline II=1
    #pragma HLS dependence variable=Ua type=inter dependent=false
    #pragma HLS dependence variable=Ub type=inter dependent=false
        if (idx < reais){
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                complex_fixed_t row[MATRIX_DIM];
                complex_fixed_t piv[MATRIX_DIM];
    #pragma HLS array_partition variable=row complete
    #pragma HLS array_partition variable=piv complete
                for (int k = 0; k < n; k++){
                    row[k] = (c == 0) ? A_ch[m][line][k] : Ua[m][line][k];
                    piv[k] = (c == 0) ? A_ch[m][0][k] : Ub[m][c][k];
                }

                complex_fixed_t l = (complex_fixed_t)cdiv<acc_fixed_t>(
                    (acc_complex_t)row[c], (acc_complex_t)piv[c]);
                L[m][line][c] = l;

                for (int k = 0; k < n; k++){
                    complex_fixed_t novo = row[k];
                    if (k >= c){
                        acc_complex_t temp_mult = cmul<acc_fixed_t>(
                            (acc_complex_t)l, (acc_complex_t)piv[k]);
                        complex_fixed_t t = (complex_fixed_t)temp_mult;
                        novo = complex_fixed_t(fixed_t(row[k].real() - t.real()),
                                               fixed_t(row[k].imag() - t.imag()));
                    }
                    Ua[m][line][k] = novo;
                    Ub[m][line][k] = novo;
                    // A linha c + 1 nao muda mais depois da coluna c
                    if (k == line && line == c + 1){
                        Ud[m][line] = novo;
                    }
                }
                // U[0][0] e o proprio A[0][0]
                if (c == 0 && line == 1){
                    Ud[m][0] = piv[0];
                }
            }
        }

        if (idx == passo - 1){
            c++;
            line = c + 1;
            g = 0;
            idx = 0;
            reais = (n - 1 - c) * GRUPOS;
            passo = lu_passo(c);
        } else {
            idx++;
            if (g == GRUPOS - 1){
                g = 0;
                line++;
            } else {
                g++;
            }
        }
    }
}

// D_extraction, D_square_root e G_decomposition para o lote. D so guardava a
// diagonal de U, entao a raiz le direto de Ud (o mesmo valor de D[line][line]).
// G sai uma linha por ciclo; acima da diagonal, zero, como no original.
static void lote_g(
    complex_fixed_t Ud[LOTE][MATRIX_DIM],
    complex_fixed_t L[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    complex_fixed_t S[LOTE][MATRIX_DIM];
#pragma HLS array_partition variable=S cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=S complete dim=2

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
    #pragma HLS pipeline II=1
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                complex_fixed_t s(0, 0);
                fixed_t d = Ud[m][line].real();
                if (d > (fixed_t)0) {
                    sqrt_t d_plain = d;
                    s.real(fixed_t(hls::sqrt(d_plain)));
                }
                S[m][line] = s;
            }
        }
    }

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
    #pragma HLS pipeline II=1
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                for (int j = 0; j < n; j++){
                    complex_fixed_t gv(0, 0);
                    if (j < line){
                        gv = cmul<fixed_t>(L[m][line][j], S[m][j]);
                    } else if (j == line){
                        complex_fixed_t um(1, 0);
                        gv = cmul<fixed_t>(um, S[m][j]);
                    }
                    G[m][line][j] = gv;
                }
            }
        }
    }
}

// forward_substitution para o lote. Cada iteracao faz G_inv[line][c] de uma
// matriz: a soma de G[line][k] * G_inv[k][c] para k de c ate line - 1, uma
// celula por k, e a divisao por G[line][line]. Na diagonal (c == line) o
// numerador e 1. Acima da diagonal G_inv nao e gravada: a inversao nao le
// essa parte.
static void lote_fs(
    complex_fixed_t G[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t G_inv[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;
    complex_fixed_t aux(1,0);

    int line = 0;
    int c = 0;
    int g = 0;
    int idx = 0;
    int reais = GRUPOS;
    int passo = fs_passo(0);

    for (int it = 0; it < FS_ITER; it++){
    #pragma HLS pipeline II=1
    #pragma HLS dependence variable=G_inv type=inter dependent=false
        if (idx < reais){
            for (int p = 0; p < VIAS; p++){
                int m = g * VIAS + p;
                sum_complex_t acc(0,0);
                for (int k = 0; k < n; k++){
                    if (k >= c && k < line){
                        sum_complex_t term = cmul<sum_t>(
                            (acc_complex_t)G[m][line][k], (acc_complex_t)G_inv[m][k][c]);
                        acc = sum_complex_t(sum_t(acc.real() + term.real()),
                                            sum_t(acc.imag() + term.imag()));
                    }
                }
                acc_complex_t num = (c == line)
                    ? (acc_complex_t)aux
                    : acc_complex_t(acc_fixed_t(-acc.real()),
                                    acc_fixed_t(-acc.imag()));
                G_inv[m][line][c] = (complex_fixed_t)cdiv<acc_fixed_t>(
                    num, (acc_complex_t)G[m][line][line]);
            }
        }

        if (idx == passo - 1){
            line++;
            c = 0;
            g = 0;
            idx = 0;
            reais = (line + 1) * GRUPOS;
            passo = fs_passo(line);
        } else {
            idx++;
            if (g == GRUPOS - 1){
                g = 0;
                c++;
            } else {
                g++;
            }
        }
    }
}

// inversion para o lote. Cada iteracao faz inverse[line][column] de uma
// matriz: a soma de conj(G_inv[k][line]) * G_inv[k][column] para k de
// max(line, column) ate n - 1, uma celula por k.
static void lote_inv(
    complex_fixed_t G_inv[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t Inv_ch[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    const int n = MATRIX_DIM;

    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < n; line++){
            for (int column = 0; column < n; column++){
    #pragma HLS pipeline II=1
                const int k_ini = (line > column) ? line : column;
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    sum_complex_t acc(0,0);
                    for (int k = 0; k < n; k++){
                        if (k >= k_ini){
                            acc_complex_t y_ki = (acc_complex_t)G_inv[m][k][line];
                            acc_complex_t y_kj = (acc_complex_t)G_inv[m][k][column];
                            sum_complex_t term = cmul<sum_t>(conj_t(y_ki), y_kj);
                            acc = sum_complex_t(sum_t(acc.real() + term.real()),
                                                sum_t(acc.imag() + term.imag()));
                        }
                    }
                    Inv_ch[m][line][column] = (complex_fixed_t)acc;
                }
            }
        }
    }
}

// Copia o lote dos bancos para as portas de saida (VIAS portas)
static void lote_gravar(
    complex_fixed_t Inv_ch[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
#pragma HLS inline off
    for (int g = 0; g < GRUPOS; g++){
        for (int line = 0; line < MATRIX_DIM; line++){
            for (int column = 0; column < MATRIX_DIM; column++){
    #pragma HLS pipeline II=1
                for (int p = 0; p < VIAS; p++){
                    int m = g * VIAS + p;
                    inverse[m][line][column] = Inv_ch[m][line][column];
                }
            }
        }
    }
}

void cholesky_inverse(
    complex_fixed_t A_matrix[LOTE][MATRIX_DIM][MATRIX_DIM],
    complex_fixed_t inverse[LOTE][MATRIX_DIM][MATRIX_DIM]
) {
// Uma porta de entrada e uma de saida por via
#pragma HLS array_partition variable=A_matrix cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=inverse cyclic factor=VIAS dim=1
#pragma HLS dataflow
    complex_fixed_t A_ch[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t L[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t Ud[LOTE][MATRIX_DIM];
    complex_fixed_t G[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t G_inv[LOTE][MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t Inv_ch[LOTE][MATRIX_DIM][MATRIX_DIM];
#pragma HLS array_partition variable=A_ch cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=A_ch complete dim=3
#pragma HLS array_partition variable=L cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=L complete dim=3
#pragma HLS array_partition variable=Ud cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=Ud complete dim=2
#pragma HLS array_partition variable=G cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=G complete dim=3
#pragma HLS array_partition variable=G_inv cyclic factor=VIAS dim=1
#pragma HLS array_partition variable=G_inv complete dim=2
#pragma HLS array_partition variable=Inv_ch cyclic factor=VIAS dim=1

    lote_ler(A_matrix, A_ch);
    lote_lu(A_ch, L, Ud);
    lote_g(Ud, L, G);
    lote_fs(G, G_inv);
    lote_inv(G_inv, Inv_ch);
    lote_gravar(Inv_ch, inverse);
}
