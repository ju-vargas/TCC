#ifndef CHOLESKY_OPS_H
#define CHOLESKY_OPS_H

#include "cholesky.h"

// Operacoes complexas com cada intermediario em uma variavel de tipo proprio
// (mulin_t, prod_t, cmul_t, num_t, norm_t, quot_t; ver cholesky.h). Os operadores do
// std::complex<ap_fixed> do Vitis escolhem esses tipos sozinhos, entao a
// largura dos intermediarios nao seria configuravel.

// conj(x) em T. -imag pode saturar: o menor valor nao tem simetrico.
template <typename T>
static inline std::complex<T> conj_t(const std::complex<T>& x) {
    return std::complex<T>(x.real(), T(-x.imag()));
}

// Operando de um multiplicador: em mulin_t se ele existir, senao o proprio valor
#ifdef CHOL_HAS_MULIN
template <typename T>
static inline mulin_t mul_operand(const T& v) { return mulin_t(v); }
#else
template <typename T>
static inline const T& mul_operand(const T& v) { return v; }
#endif

// re = xr*yr - xi*yi e im = xr*yi + xi*yr, com cada produto em prod_t e cada
// soma em cmul_t
template <typename TX, typename TY>
static inline void cmul_parts(const std::complex<TX>& x, const std::complex<TY>& y,
                              cmul_t& re, cmul_t& im) {
    prod_t rr = mul_operand(x.real()) * mul_operand(y.real());
    prod_t ii = mul_operand(x.imag()) * mul_operand(y.imag());
    prod_t ri = mul_operand(x.real()) * mul_operand(y.imag());
    prod_t ir = mul_operand(x.imag()) * mul_operand(y.real());
    re = rr - ii;
    im = ri + ir;
}

// x * y, atribuido a TO
template <typename TO, typename TX, typename TY>
static inline std::complex<TO> cmul(const std::complex<TX>& x, const std::complex<TY>& y) {
    cmul_t re, im;
    cmul_parts(x, y, re, im);
    return std::complex<TO>(TO(re), TO(im));
}

// x / y = x * conj(y) / |y|^2, com x e y em T. O numerador fica em num_t e
// |y|^2 em norm_t. O dividendo e convertido para quot_t antes de dividir, entao o
// quociente tem os bits fracionarios de quot_t; depois ele e atribuido a T.
template <typename T>
static inline std::complex<T> cdiv(const std::complex<T>& x, const std::complex<T>& y) {
    std::complex<T> cj = conj_t(y);
    std::complex<num_t> a = cmul<num_t>(x, cj);
    cmul_t norm_re, norm_im;
    cmul_parts(cj, y, norm_re, norm_im);
    norm_t n = norm_re;
    quot_t q_re = quot_t(a.real()) / n;
    quot_t q_im = quot_t(a.imag()) / n;
    return std::complex<T>(T(q_re), T(q_im));
}

#endif // CHOLESKY_OPS_H
