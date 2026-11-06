// Testbench da estimativa de potencia: inverte, uma atras da outra, as matrizes
// G_c reais de uma lista (um caminho de .bits por linha, de
// hardware/testes/2_amostra_matrizes). Na co-simulacao, cada chamada do
// cholesky_inverse vira uma transacao do RTL, e a atividade dos sinais vai para
// o SAIF que o report_power do Vivado le. O tb_lu_decomposition.cpp continua
// sendo o testbench da validacao [3].
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include "cholesky.h"

// Mesmo formato do exportar_matrizes.py: a dimensao, depois cada elemento
// "<64 bits>:<64 bits>" (float64 IEEE 754 da parte real e da imaginaria)
static bool ler_bits(const std::string& arquivo, complex_fixed_t A[MATRIX_DIM][MATRIX_DIM]) {
    std::ifstream in(arquivo.c_str());
    int n;
    if (!(in >> n) || n != MATRIX_DIM) {
        std::cerr << "Erro: " << arquivo << " nao abre ou nao tem dimensao " << MATRIX_DIM << std::endl;
        return false;
    }
    std::string t;
    for (int i = 0; i < MATRIX_DIM; i++)
        for (int j = 0; j < MATRIX_DIM; j++) {
            size_t sep;
            if (!(in >> t) || (sep = t.find(':')) != 64 || t.size() != 129) {
                std::cerr << "Erro: elemento (" << i << ", " << j << ") de " << arquivo << std::endl;
                return false;
            }
            double v[2];
            for (int k = 0; k < 2; k++) {
                uint64_t raw = std::stoull(t.substr(k * 65, 64), nullptr, 2);
                std::memcpy(&v[k], &raw, sizeof(double));
            }
            A[i][j].real(fixed_t(v[0]));
            A[i][j].imag(fixed_t(v[1]));
        }
    return true;
}

// argv[1]: arquivo com a lista das matrizes
int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Uso: tb_potencia <lista de .bits>" << std::endl;
        return 1;
    }
    std::ifstream lista(argv[1]);
    std::vector<std::string> arquivos;
    for (std::string linha; std::getline(lista, linha);)
        if (!linha.empty()) arquivos.push_back(linha);
    if (arquivos.empty()) {
        std::cerr << "Erro: lista vazia ou nao encontrada: " << argv[1] << std::endl;
        return 1;
    }
    // O topo inverte um lote de LOTE matrizes por chamada. Os lotes sao
    // montados com as matrizes da lista, em ordem, voltando ao inicio quando
    // ela acaba; sao pelo menos 3 lotes, para a co-simulacao medir o
    // intervalo entre lotes.
    static complex_fixed_t A[LOTE][MATRIX_DIM][MATRIX_DIM];
    static complex_fixed_t inversa[LOTE][MATRIX_DIM][MATRIX_DIM];
    size_t lotes = (arquivos.size() + LOTE - 1) / LOTE;
    if (lotes < 3) lotes = 3;
    for (size_t b = 0; b < lotes; b++) {
        for (int m = 0; m < LOTE; m++)
            if (!ler_bits(arquivos[(b * LOTE + m) % arquivos.size()], A[m])) return 1;
        cholesky_inverse(A, inversa);
    }
    std::cout << "POTENCIA " << lotes * LOTE << " matrizes invertidas em " << lotes
              << " lotes de " << LOTE << std::endl;
    return 0;
}
