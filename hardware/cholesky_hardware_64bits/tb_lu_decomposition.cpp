#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <complex>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <sys/stat.h>
#include "cholesky.h"

// A C-simulation roda de dentro de hls/csim/build, entao todos os caminhos
// precisam ser absolutos.
static const std::string BASE_DIR = "/home/juliana/GitHub/TCC/hardware/";
static const std::string OUT_DIR  = BASE_DIR + "hw_results/";

// Mesma regra de casas decimais de golden.py (round(F * log10(2)) + 1), para os
// .txt serem legiveis lado a lado. A comparacao exata usa os .bits.
static const int OUT_DECIMALS =
    (int)((fixed_t::width - fixed_t::iwidth) * 0.30103 + 0.5) + 1;

// Maior valor do fixed_t: 2^(I-1) - 2^-F
static const double FIXED_MAX = std::ldexp(1.0, fixed_t::iwidth - 1)
                              - std::ldexp(1.0, -(fixed_t::width - fixed_t::iwidth));

// ---------------------------------------------------------------------------
// Tipos compilados
// ---------------------------------------------------------------------------

// Mesma ordem dos enums ap_q_mode e ap_o_mode (etc/ap_decl.h)
static const char* Q_NAMES[] = {"AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF",
                                "AP_RND_CONV", "AP_TRN", "AP_TRN_ZERO"};
static const char* O_NAMES[] = {"AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM"};

// Uma linha "TIPO <nome> ap_fixed<W,I,Q,O>", no mesmo texto que o
// golden_cholesky.py imprime, para um script conferir que os -D chegaram
template <typename T>
static void print_type(const char* name) {
    std::cout << "TIPO " << name << " ap_fixed<" << T::width << "," << T::iwidth << ","
              << Q_NAMES[T::qmode] << "," << O_NAMES[T::omode] << ">" << std::endl;
}

static void print_types() {
    print_type<fixed_t>("fix");
    print_type<acc_fixed_t>("acc");
#ifdef CHOL_HAS_MULIN
    print_type<mulin_t>("mulin");
#endif
#ifdef CHOL_PROD_INT_BITS
    print_type<prod_t>("prod");
    print_type<cmul_t>("cmul");
    print_type<num_t>("num");
    print_type<norm_t>("norm");
    print_type<quot_t>("quot");
    print_type<sum_t>("sum");
    print_type<sqrt_t>("sqrt");
#endif
}

// ---------------------------------------------------------------------------
// Leitura da matriz de entrada
// ---------------------------------------------------------------------------

// Um float64 em .bits: 64 caracteres '0'/'1', do bit mais significativo ao
// menos, com o padrao IEEE 754 (formato do exportar_matrizes.py)
static bool parse_float_bits(const std::string& s, double& out) {
    if (s.size() != 64 || s.find_first_not_of("01") != std::string::npos) return false;
    uint64_t raw = std::stoull(s, nullptr, 2);
    std::memcpy(&out, &raw, sizeof out);
    return true;
}

static bool ends_with(const std::string& s, const std::string& suffix) {
    return s.size() >= suffix.size() &&
           s.compare(s.size() - suffix.size(), suffix.size(), suffix) == 0;
}

// Entrada em texto (formato do A.txt, "re+imj") ou, se o arquivo terminar em
// .bits, com cada elemento "<64 bits>:<64 bits>" (parte real e imaginaria)
bool read_matrix_from_file(const std::string& filename, complex_fixed_t A_matrix[MATRIX_DIM][MATRIX_DIM]) {
    std::ifstream infile(filename.c_str());

    if (!infile.is_open()) {
        std::cerr << "Erro: Nao foi possivel abrir o arquivo " << filename << std::endl;
        return false;
    }

    int file_dim;
    if (!(infile >> file_dim)) {
        std::cerr << "Erro ao ler a dimensao no arquivo." << std::endl;
        return false;
    }

    if (file_dim != MATRIX_DIM) {
        std::cerr << "Erro: A dimensao no arquivo (" << file_dim
                  << ") nao corresponde ao MATRIX_DIM (" << MATRIX_DIM << ")." << std::endl;
        return false;
    }

    const bool bits_input = ends_with(filename, ".bits");

    std::string token;
    for (int line = 0; line < MATRIX_DIM; line++) {
        for (int column = 0; column < MATRIX_DIM; column++) {
            if (!(infile >> token)) {
                std::cerr << "Erro ao ler dados na posicao (" << line << ", " << column << ")." << std::endl;
                return false;
            }

            if (bits_input) {
                size_t sep = token.find(':');
                double re, im;
                if (sep == std::string::npos || !parse_float_bits(token.substr(0, sep), re) ||
                    !parse_float_bits(token.substr(sep + 1), im)) {
                    std::cerr << "Erro: elemento (" << line << ", " << column << ") nao tem a "
                              << "forma <64 bits>:<64 bits> de um float64." << std::endl;
                    return false;
                }
                A_matrix[line][column].real(fixed_t(re));
                A_matrix[line][column].imag(fixed_t(im));
                continue;
            }

            // Formato "real+imagj" ou "real-imagj"
            if (!token.empty() && token.back() == 'j') {
                token.pop_back();
            }

            // A busca comeca na posicao 1 para nao confundir com o sinal
            // negativo da propria parte real (ex: "-1+2j")
            size_t split_pos = token.find_first_of("+-", 1);

            if (split_pos != std::string::npos) {
                std::string real_str = token.substr(0, split_pos);
                std::string imag_str = token.substr(split_pos);

                A_matrix[line][column].real(fixed_t(std::stod(real_str)));
                A_matrix[line][column].imag(fixed_t(std::stod(imag_str)));
            } else {
                A_matrix[line][column].real(fixed_t(std::stod(token)));
                A_matrix[line][column].imag(fixed_t(0));
            }
        }
    }

    infile.close();
    return true;
}

// ---------------------------------------------------------------------------
// Escrita dos resultados
// ---------------------------------------------------------------------------

// Grava no mesmo formato de golden.py: primeira linha com n, depois as linhas
// da matriz com elementos "re+imj".
bool write_matrix_to_file(const std::string& filename, complex_fixed_t M[MATRIX_DIM][MATRIX_DIM]) {
    std::ofstream outfile(filename.c_str());
    if (!outfile.is_open()) {
        std::cerr << "Erro: Nao foi possivel escrever em " << filename << std::endl;
        return false;
    }

    outfile << MATRIX_DIM << "\n";
    outfile << std::fixed << std::setprecision(OUT_DECIMALS);

    for (int i = 0; i < MATRIX_DIM; i++) {
        for (int j = 0; j < MATRIX_DIM; j++) {
            double re = M[i][j].real().to_double();
            double im = M[i][j].imag().to_double();
            char sign = (im < 0) ? '-' : '+';
            outfile << re << sign << std::fabs(im) << "j";
            if (j < MATRIX_DIM - 1) outfile << " ";
        }
        outfile << "\n";
    }

    outfile.close();
    return true;
}

// S e um vetor com a diagonal, entao vai como uma unica linha de n elementos
bool write_vector_to_file(const std::string& filename, complex_fixed_t V[MATRIX_DIM]) {
    std::ofstream outfile(filename.c_str());
    if (!outfile.is_open()) {
        std::cerr << "Erro: Nao foi possivel escrever em " << filename << std::endl;
        return false;
    }

    outfile << MATRIX_DIM << "\n";
    outfile << std::fixed << std::setprecision(OUT_DECIMALS);

    for (int i = 0; i < MATRIX_DIM; i++) {
        double re = V[i].real().to_double();
        double im = V[i].imag().to_double();
        char sign = (im < 0) ? '-' : '+';
        outfile << re << sign << std::fabs(im) << "j";
        if (i < MATRIX_DIM - 1) outfile << " ";
    }
    outfile << "\n";

    outfile.close();
    return true;
}

// Os W bits do registrador (complemento de dois), do mais significativo para o
// menos. to_string(2) nao serve: corta os zeros a esquerda.
static std::string to_bits(const fixed_t& x) {
    const int W = fixed_t::width;
    ap_uint<fixed_t::width> raw = x.range(W - 1, 0);
    std::string s(W, '0');
    for (int i = 0; i < W; i++) {
        if (raw[W - 1 - i]) s[i] = '1';
    }
    return s;
}

// Formato .bits, usado na comparacao com golden_cholesky.py: primeira linha
// com n, depois um elemento "real:imag" por posicao, em bits crus.
bool write_matrix_bits_to_file(const std::string& filename, complex_fixed_t M[MATRIX_DIM][MATRIX_DIM]) {
    std::ofstream outfile(filename.c_str());
    if (!outfile.is_open()) {
        std::cerr << "Erro: Nao foi possivel escrever em " << filename << std::endl;
        return false;
    }

    outfile << MATRIX_DIM << "\n";
    for (int i = 0; i < MATRIX_DIM; i++) {
        for (int j = 0; j < MATRIX_DIM; j++) {
            outfile << to_bits(M[i][j].real()) << ":" << to_bits(M[i][j].imag());
            if (j < MATRIX_DIM - 1) outfile << " ";
        }
        outfile << "\n";
    }

    outfile.close();
    return true;
}

bool write_vector_bits_to_file(const std::string& filename, complex_fixed_t V[MATRIX_DIM]) {
    std::ofstream outfile(filename.c_str());
    if (!outfile.is_open()) {
        std::cerr << "Erro: Nao foi possivel escrever em " << filename << std::endl;
        return false;
    }

    outfile << MATRIX_DIM << "\n";
    for (int i = 0; i < MATRIX_DIM; i++) {
        outfile << to_bits(V[i].real()) << ":" << to_bits(V[i].imag());
        if (i < MATRIX_DIM - 1) outfile << " ";
    }
    outfile << "\n";

    outfile.close();
    return true;
}

void print_matrix(const char* name, complex_fixed_t M[MATRIX_DIM][MATRIX_DIM]) {
    std::cout << "\n--- " << name << " ---" << std::endl;
    for (int i = 0; i < MATRIX_DIM; i++) {
        for (int j = 0; j < MATRIX_DIM; j++) {
            std::cout << "(" << M[i][j].real() << ", " << M[i][j].imag() << ")  ";
        }
        std::cout << std::endl;
    }
}

void print_vector(const char* name, complex_fixed_t V[MATRIX_DIM]) {
    std::cout << "\n--- " << name << " ---" << std::endl;
    for (int i = 0; i < MATRIX_DIM; i++) {
        std::cout << "(" << V[i].real() << ", " << V[i].imag() << ")  ";
    }
    std::cout << std::endl;
}

// ---------------------------------------------------------------------------
// Verificacao (feita em double, fora do hardware)
// ---------------------------------------------------------------------------

typedef std::complex<double> cd;

static cd to_cd(const complex_fixed_t& z) {
    return cd(z.real().to_double(), z.imag().to_double());
}

// Maior modulo do triangulo estritamente superior (mede se M e triangular inferior)
static double max_strict_upper(complex_fixed_t M[MATRIX_DIM][MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++)
        for (int j = i + 1; j < MATRIX_DIM; j++)
            worst = std::max(worst, std::abs(to_cd(M[i][j])));
    return worst;
}

// Maior modulo do triangulo estritamente inferior (mede se M e triangular superior)
static double max_strict_lower(complex_fixed_t M[MATRIX_DIM][MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++)
        for (int j = 0; j < i; j++)
            worst = std::max(worst, std::abs(to_cd(M[i][j])));
    return worst;
}

// Maior modulo fora da diagonal (mede se M e diagonal)
static double max_off_diagonal(complex_fixed_t M[MATRIX_DIM][MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++)
        for (int j = 0; j < MATRIX_DIM; j++)
            if (i != j) worst = std::max(worst, std::abs(to_cd(M[i][j])));
    return worst;
}

// Maior erro de |X*Y - A|, com transpose_conj_y indicando se usa Y^H no lugar de Y
static double reconstruction_error(complex_fixed_t X[MATRIX_DIM][MATRIX_DIM],
                                   complex_fixed_t Y[MATRIX_DIM][MATRIX_DIM],
                                   complex_fixed_t A[MATRIX_DIM][MATRIX_DIM],
                                   bool transpose_conj_y) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++) {
        for (int j = 0; j < MATRIX_DIM; j++) {
            cd acc(0.0, 0.0);
            for (int k = 0; k < MATRIX_DIM; k++) {
                cd y = transpose_conj_y ? std::conj(to_cd(Y[j][k])) : to_cd(Y[k][j]);
                acc += to_cd(X[i][k]) * y;
            }
            worst = std::max(worst, std::abs(acc - to_cd(A[i][j])));
        }
    }
    return worst;
}

// S deve ser real (A hermitiana definida positiva)
static double max_abs_imag(complex_fixed_t V[MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++)
        worst = std::max(worst, std::fabs(V[i].imag().to_double()));
    return worst;
}

// S[i]^2 deve reproduzir D[i][i]; o desvio e so o erro de quantizacao da raiz
static double s_squared_error(complex_fixed_t S[MATRIX_DIM],
                              complex_fixed_t D[MATRIX_DIM][MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++) {
        double s = S[i].real().to_double();
        worst = std::max(worst, std::fabs(s * s - D[i][i].real().to_double()));
    }
    return worst;
}

// Maior modulo dos produtos L[i][j]*S[j] da etapa G, calculado em double.
// O fixed_t vai so ate FIXED_MAX e o estouro e silencioso (satura, zera ou da a
// volta, conforme o modo). Doolittle aqui nao tem pivotamento, entao uma matriz
// mal condicionada pode gerar L grande e cruzar esse limite.
static double max_g_product(complex_fixed_t L[MATRIX_DIM][MATRIX_DIM],
                            complex_fixed_t S[MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++)
        for (int j = 0; j <= i; j++)
            worst = std::max(worst, std::abs(to_cd(L[i][j]) * to_cd(S[j])));
    return worst;
}

// Maior erro de |X*Y - I|, para medir uma inversao
static double identity_error(complex_fixed_t X[MATRIX_DIM][MATRIX_DIM],
                             complex_fixed_t Y[MATRIX_DIM][MATRIX_DIM]) {
    double worst = 0.0;
    for (int i = 0; i < MATRIX_DIM; i++) {
        for (int j = 0; j < MATRIX_DIM; j++) {
            cd acc(0.0, 0.0);
            for (int k = 0; k < MATRIX_DIM; k++)
                acc += to_cd(X[i][k]) * to_cd(Y[k][j]);
            cd esperado = (i == j) ? cd(1.0, 0.0) : cd(0.0, 0.0);
            worst = std::max(worst, std::abs(acc - esperado));
        }
    }
    return worst;
}

// ---------------------------------------------------------------------------

// Sem argumentos usa A.txt e hw_results/, que e o que a C-simulation do Vitis
// faz. Aceitar os caminhos por argumento permite rodar o binario direto em
// outras matrizes sem recompilar.
int main(int argc, char** argv) {
    std::string in_path  = (argc > 1) ? argv[1] : (BASE_DIR + "A.txt");
    std::string out_dir  = (argc > 2) ? argv[2] : OUT_DIR;
    if (!out_dir.empty() && out_dir.back() != '/') out_dir += '/';

    print_types();

    complex_fixed_t A[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t L[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t U[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t S[MATRIX_DIM];
    complex_fixed_t G[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t G_inv[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t inverse[MATRIX_DIM][MATRIX_DIM];

    if (!read_matrix_from_file(in_path, A)) {
        return -1;
    }

    cholesky_decomposition(A, L, U, D, S, G, G_inv, inverse);

    // O topo da sintese tem que dar a mesma inversa, bit a bit
    complex_fixed_t inverse_top[MATRIX_DIM][MATRIX_DIM];
    cholesky_inverse(A, inverse_top);
    for (int i = 0; i < MATRIX_DIM; i++)
        for (int j = 0; j < MATRIX_DIM; j++)
            if (inverse_top[i][j] != inverse[i][j]) {
                std::cerr << "FALHA: cholesky_inverse difere de cholesky_decomposition em ("
                          << i << ", " << j << ")" << std::endl;
                return 1;
            }

    // O diretorio de saida nao e versionado, entao pode nao existir
    mkdir(out_dir.c_str(), 0775);

    // Uma etapa por arquivo, na ordem em que sao calculadas
    bool ok = true;
    ok &= write_matrix_to_file(out_dir + "hw_00_A.txt", A);  // A ja quantizada
    ok &= write_matrix_to_file(out_dir + "hw_01_L.txt", L);
    ok &= write_matrix_to_file(out_dir + "hw_02_U.txt", U);
    ok &= write_matrix_to_file(out_dir + "hw_03_D.txt", D);
    ok &= write_vector_to_file(out_dir + "hw_05_S.txt", S);
    ok &= write_matrix_to_file(out_dir + "hw_06_G.txt", G);
    ok &= write_matrix_to_file(out_dir + "hw_07_G_inv.txt", G_inv);
    ok &= write_matrix_to_file(out_dir + "hw_08_inverse.txt", inverse);

    // Os mesmos resultados em bits crus, para a comparacao bit a bit
    ok &= write_matrix_bits_to_file(out_dir + "hw_00_A.bits", A);
    ok &= write_matrix_bits_to_file(out_dir + "hw_01_L.bits", L);
    ok &= write_matrix_bits_to_file(out_dir + "hw_02_U.bits", U);
    ok &= write_matrix_bits_to_file(out_dir + "hw_03_D.bits", D);
    ok &= write_vector_bits_to_file(out_dir + "hw_05_S.bits", S);
    ok &= write_matrix_bits_to_file(out_dir + "hw_06_G.bits", G);
    ok &= write_matrix_bits_to_file(out_dir + "hw_07_G_inv.bits", G_inv);
    ok &= write_matrix_bits_to_file(out_dir + "hw_08_inverse.bits", inverse);

    if (!ok) {
        std::cerr << "Erro: o diretorio " << out_dir << " existe?" << std::endl;
        return -1;
    }

    print_matrix("Etapa 1: L", L);
    print_matrix("Etapa 1: U", U);
    print_matrix("Etapa 2: D", D);
    print_vector("Etapa 3: S = sqrt(D) (diagonal)", S);
    print_matrix("Etapa 4: G = L * S", G);
    print_matrix("Etapa 5: G_inv = G^-1", G_inv);
    print_matrix("Etapa 6: inverse = A^-1", inverse);

    // -----------------------------------------------------------------------
    // Relatorio de verificacao
    // -----------------------------------------------------------------------
    double l_upper   = max_strict_upper(L);
    double u_lower   = max_strict_lower(U);
    double d_offdiag = max_off_diagonal(D);
    double s_imag    = max_abs_imag(S);
    double s_err     = s_squared_error(S, D);
    double g_upper   = max_strict_upper(G);
    double g_prod    = max_g_product(L, S);
    double err_lu    = reconstruction_error(L, U, A, false);
    double err_gg    = reconstruction_error(G, G, A, true);
    double ginv_upper = max_strict_upper(G_inv);
    double err_ginv   = identity_error(G, G_inv);
    double err_inv    = identity_error(A, inverse);

    std::ofstream rep((out_dir + "hw_09_relatorio.txt").c_str());
    std::ostream* outs[2] = { &std::cout, &rep };

    for (int s = 0; s < 2; s++) {
        std::ostream& o = *outs[s];
        o << "\n=== Verificacao (tipo " << (fixed_t::width) << " bits, "
          << (fixed_t::iwidth) << " inteiros) ===\n";
        o << std::scientific << std::setprecision(4);
        o << "Estrutura (esperado ~0):\n";
        o << "  max |L| acima da diagonal      : " << l_upper   << "\n";
        o << "  max |U| abaixo da diagonal     : " << u_lower   << "   (residuo de truncamento da etapa LU)\n";
        o << "  max |D| fora da diagonal       : " << d_offdiag << "\n";
        o << "  max |Im(S)|                    : " << s_imag    << "\n";
        o << "  max |S[i]^2 - D[i][i]|         : " << s_err     << "   (erro de quantizacao da raiz)\n";
        o << "  max |G| acima da diagonal      : " << g_upper   << "\n";
        o << "  max |G_inv| acima da diagonal  : " << ginv_upper << "\n";
        o << "Faixa (fixed_t vai ate " << FIXED_MAX << "):\n";
        o << "  max |L[i][j]*S[j]| na etapa G  : " << g_prod    << "\n";
        o << "Reconstrucao (esperado ~0):\n";
        o << "  max |L*U - A|                  : " << err_lu    << "\n";
        o << "  max |G*G^H - A|                : " << err_gg    << "\n";
        o << "  max |G*G_inv - I|              : " << err_ginv  << "\n";
        o << "  max |A*A^-1 - I|               : " << err_inv   << "\n";
        o << std::fixed << std::setprecision(6);
        o << "Referencia: G[0][0] deve ser ~sqrt(A[0][0]) = "
          << std::sqrt(A[0][0].real().to_double())
          << ", obtido " << G[0][0].real().to_double() << "\n";
        o << "Referencia: S[0] deve ser ~sqrt(D[0][0]) = "
          << std::sqrt(D[0][0].real().to_double())
          << ", obtido " << S[0].real().to_double() << "\n";
    }
    rep.close();

    // Falhas estruturais sao bugs de codigo, nao erro de quantizacao
    const double STRUCT_TOL = 1e-9;
    if (l_upper > STRUCT_TOL || d_offdiag > STRUCT_TOL ||
        s_imag > STRUCT_TOL || g_upper > STRUCT_TOL || ginv_upper > STRUCT_TOL) {
        std::cerr << "\nFALHA: alguma matriz nao tem a estrutura esperada." << std::endl;
        return 1;
    }

    // O estouro de ap_fixed e silencioso, entao vale falhar em vez de gerar
    // um G com sinal trocado
    if (g_prod > FIXED_MAX) {
        std::cerr << "\nFALHA: L[i][j]*S[j] chegou a " << g_prod
                  << ", acima do limite " << FIXED_MAX
                  << " de ap_fixed<" << fixed_t::width << "," << fixed_t::iwidth
                  << ">. G vai estourar." << std::endl;
        return 1;
    }

    std::cout << "\nResultados gravados em " << out_dir << std::endl;
    return 0;
}
