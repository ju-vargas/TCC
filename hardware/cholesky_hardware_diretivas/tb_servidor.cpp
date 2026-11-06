// Testbench "servidor": o hardware (cholesky_decomposition, os mesmos fontes de
// ../cholesky_hardware/) inverte as matrizes que o simulador envia, uma por vez,
// e devolve a inversa ao simulador. Sem arquivos: tudo pela entrada e pela saída
// padrão, em binário, para o processo ficar aberto durante a simulação inteira.
//
// Protocolo (little-endian), repetido até o fim da entrada:
//   entrada: int32 n, depois n*n pares (real, imag) em float64, linha por linha
//   saída:   uint8 status (0 = ok, 1 = divisão por zero, 2 = n diferente de
//            MATRIX_DIM), e, se ok,
//            n*n pares (real, imag) com o registrador cru de cada parte da
//            inversa, em int64 com sinal (fixed_t tem no máximo 64 bits)
// A conversão de float64 para fixed_t é a mesma do testbench original
// (fixed_t(double), com a quantização e o estouro do tipo). Uma divisão por
// zero (SIGFPE) termina o processo, como no testbench original, mas antes ele
// responde status 1, para sair sem core dump (que no Ubuntu leva cerca de 1 s);
// o simulador reinicia o servidor.
//
// Uso: csim.exe            servidor
//      csim.exe --tipos    imprime as linhas "TIPO ..." e sai (conferência)

#include <csignal>
#include <cstdint>
#include <unistd.h>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <vector>
#include "cholesky.h"

static const char* Q_NAMES[] = {"AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF",
                                "AP_RND_CONV", "AP_TRN", "AP_TRN_ZERO"};
static const char* O_NAMES[] = {"AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM"};

template <typename T>
static void print_type(const char* name) {
    std::cout << "TIPO " << name << " ap_fixed<" << T::width << "," << T::iwidth << ","
              << Q_NAMES[T::qmode] << "," << O_NAMES[T::omode] << ">" << std::endl;
}

static_assert(fixed_t::width <= 64, "o registrador precisa caber em int64");

static int64_t raw(const fixed_t& v) {
    ap_int<fixed_t::width> r;
    r.range(fixed_t::width - 1, 0) = v.range(fixed_t::width - 1, 0);
    return r.to_int64();
}

static bool read_all(void* buf, size_t bytes) {
    return std::fread(buf, 1, bytes, stdin) == bytes;
}

// Só chamadas seguras dentro de um tratador de sinal: write e _exit
static void divisao_por_zero(int) {
    const uint8_t status = 1;
    ssize_t r = write(STDOUT_FILENO, &status, 1);
    (void)r;
    _exit(1);
}

int main(int argc, char** argv) {
    std::signal(SIGFPE, divisao_por_zero);
    if (argc > 1 && std::strcmp(argv[1], "--tipos") == 0) {
        print_type<fixed_t>("fix");
        print_type<acc_fixed_t>("acc");
        std::cout << "N " << MATRIX_DIM << std::endl;
        return 0;
    }

    static complex_fixed_t A[MATRIX_DIM][MATRIX_DIM], L[MATRIX_DIM][MATRIX_DIM],
        U[MATRIX_DIM][MATRIX_DIM], D[MATRIX_DIM][MATRIX_DIM],
        S[MATRIX_DIM], G[MATRIX_DIM][MATRIX_DIM], G_inv[MATRIX_DIM][MATRIX_DIM],
        inverse[MATRIX_DIM][MATRIX_DIM];
    std::vector<double> entrada(2 * MATRIX_DIM * MATRIX_DIM);
    std::vector<int64_t> saida(2 * MATRIX_DIM * MATRIX_DIM);

    int32_t n;
    while (read_all(&n, sizeof n)) {
        if (n != MATRIX_DIM) {
            uint8_t status = 2;
            std::fwrite(&status, 1, 1, stdout);
            std::fflush(stdout);
            return 2;
        }
        if (!read_all(entrada.data(), entrada.size() * sizeof(double))) return 3;
        for (int i = 0; i < MATRIX_DIM; i++)
            for (int j = 0; j < MATRIX_DIM; j++) {
                A[i][j].real(fixed_t(entrada[2 * (i * MATRIX_DIM + j)]));
                A[i][j].imag(fixed_t(entrada[2 * (i * MATRIX_DIM + j) + 1]));
            }

        cholesky_decomposition(A, L, U, D, S, G, G_inv, inverse);

        for (int i = 0; i < MATRIX_DIM; i++)
            for (int j = 0; j < MATRIX_DIM; j++) {
                saida[2 * (i * MATRIX_DIM + j)] = raw(inverse[i][j].real());
                saida[2 * (i * MATRIX_DIM + j) + 1] = raw(inverse[i][j].imag());
            }
        uint8_t status = 0;
        std::fwrite(&status, 1, 1, stdout);
        std::fwrite(saida.data(), sizeof(int64_t), saida.size(), stdout);
        std::fflush(stdout);
    }
    return 0;
}
