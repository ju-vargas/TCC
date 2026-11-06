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
    complex_fixed_t A[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t inversa[MATRIX_DIM][MATRIX_DIM];
    for (size_t m = 0; m < arquivos.size(); m++) {
        if (!ler_bits(arquivos[m], A)) return 1;
        cholesky_inverse(A, inversa);
    }
    std::cout << "POTENCIA " << arquivos.size() << " matrizes invertidas" << std::endl;
    return 0;
}
