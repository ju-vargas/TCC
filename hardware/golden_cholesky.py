#!/usr/bin/env python3
"""
Modelo bit a bit da inversão por Cholesky de cholesky_hardware/, em Python.

O simulador (software/simulador/dbp_sim/hw_inverse.py) carrega este arquivo e
chama invert() na inversa M_c x M_c do BCD-MMSE.

Reproduz cada arredondamento do ap_fixed e do std::complex<ap_fixed> do Vitis
HLS (etc/ap_fixed_special.h), para que a saída seja igual à da C-simulation.

A etapa 2 (dv_step.cpp) só copia a diagonal de U para D, como no hardware.

Cadeia (mesma ordem de cholesky_decomposition.cpp):
  1. A     -> L, U        (LU sem pivotamento)
  2. U     -> D           (diagonal de U)
  3. D     -> S = sqrt(D)
  4. L, S  -> G = L * S   (A = G * G^H)
  5. G     -> G_inv       (substituição direta)
  6. G_inv -> inverse     (A^-1 = G_inv^H * G_inv)

Cada número é guardado como um inteiro V, com valor V / 2^F, onde F é o
número de bits fracionários do seu tipo. Um complexo é a tupla (re, im).
Contas com inteiros do Python são exatas, então o único arredondamento é o
que o ap_fixed faz na atribuição.
"""

import argparse
import math
import os
import struct
import sys
from dataclasses import dataclass


# --------------------------------------------------------------------------
# Tipos ap_fixed (cholesky.h)
# --------------------------------------------------------------------------

# Modos de ap_fixed (etc/ap_fixed_base.h: quantization_adjust e overflow_adjust)
QUANT_MODES = ("AP_TRN", "AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF",
               "AP_RND_INF", "AP_RND_CONV")
OVERFLOW_MODES = ("AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM")


@dataclass(frozen=True)
class FixedType:
    """ap_fixed<width, int_bits, q_mode, o_mode>; int_bits já inclui o sinal.

    O número de bits de saturação (_AP_N) é sempre 0, o padrão do ap_fixed.
    """
    width: int
    int_bits: int
    q_mode: str = "AP_TRN"
    o_mode: str = "AP_SAT"

    def __post_init__(self):
        if self.q_mode not in QUANT_MODES:
            raise ValueError(f"modo de quantização desconhecido {self.q_mode!r}; "
                             f"use um de {QUANT_MODES}")
        if self.o_mode not in OVERFLOW_MODES:
            raise ValueError(f"modo de estouro desconhecido {self.o_mode!r}; "
                             f"use um de {OVERFLOW_MODES}")

    @property
    def frac(self) -> int:
        return self.width - self.int_bits

    @property
    def max(self) -> int:
        return (1 << (self.width - 1)) - 1

    @property
    def min(self) -> int:
        return -(1 << (self.width - 1))

    def __str__(self) -> str:
        return f"ap_fixed<{self.width},{self.int_bits},{self.q_mode},{self.o_mode}>"


def fixed_type(int_bits: int, frac_bits: int, q_mode: str = "AP_TRN",
               o_mode: str = "AP_SAT") -> FixedType:
    """ap_fixed<int_bits + frac_bits, int_bits, q_mode, o_mode>."""
    return FixedType(int_bits + frac_bits, int_bits, q_mode, o_mode)


def default_acc(fix: FixedType) -> FixedType:
    """Acumulador com o dobro dos bits inteiros e fracionários, como em cholesky.h,
    e os mesmos modos do tipo de dados."""
    return fixed_type(2 * fix.int_bits, 2 * fix.frac, fix.q_mode, fix.o_mode)


# Formato atual de cholesky.h
FIX = fixed_type(8, 8)   # fixed_t     = ap_fixed<16, 8, AP_TRN, AP_SAT>
ACC = default_acc(FIX)   # acc_fixed_t = ap_fixed<32, 16, AP_TRN, AP_SAT>


@dataclass(frozen=True)
class Formats:
    """Todos os tipos do hardware (cholesky.h).

    fix    dados guardados entre etapas (fixed_t)
    acc    operandos das contas internas (acc_fixed_t)
    mulin  operandos de cada multiplicador (mulin_t); None = sem conversão,
           cada multiplicador usa o tipo dos próprios operandos
    prod   cada produto real a*b (prod_t)
    cmul   a*b - c*d e a*d + b*c do produto complexo (cmul_t)
    num    numerador x*conj(y) da divisão complexa (num_t)
    norm   |y|^2, o divisor da divisão complexa (norm_t)
    quot   quociente da divisão; o dividendo é convertido para ele antes de
           dividir, então o quociente sai com os bits fracionários dele (quot_t)
    sum    soma acumulada da substituição direta e da inversão (sum_t)
    sqrt   entrada e saída do hls::sqrt (sqrt_t); sempre AP_TRN e AP_WRAP,
           porque o hls::sqrt só aceita os modos padrão
    """
    fix: FixedType
    acc: FixedType
    mulin: FixedType | None
    prod: FixedType
    cmul: FixedType
    num: FixedType
    norm: FixedType
    quot: FixedType
    sum: FixedType
    sqrt: FixedType

    def __str__(self) -> str:
        return "\n".join(
            f"  {k:5s} = {getattr(self, k) if getattr(self, k) else 'sem conversão'}"
            for k in ("fix", "acc", "mulin", "prod", "cmul", "num", "norm", "quot",
                      "sum", "sqrt"))


def make_formats(fix: FixedType = FIX, acc: FixedType | None = None, **inter) -> Formats:
    """Monta os formatos com os padrões de cholesky.h.

    Sem acc, ele é default_acc(fix). Os intermediários que não forem passados
    ficam com o padrão, que reproduz o hardware sem tipos intermediários:
    mulin sem conversão, produto e produto complexo exatos, numerador, divisor,
    quociente e soma iguais ao acumulador, sempre com os modos do acumulador,
    e a raiz na largura dos dados.
    """
    acc = default_acc(fix) if acc is None else acc
    q, o = acc.q_mode, acc.o_mode
    prod = fixed_type(2 * acc.int_bits, 2 * acc.frac, q, o)
    defaults = {
        "mulin": None,
        "prod": prod,
        "cmul": fixed_type(prod.int_bits + 1, prod.frac, q, o),
        "num": acc, "norm": acc, "quot": acc, "sum": acc,
        "sqrt": sqrt_type(fix.int_bits, fix.frac),
    }
    unknown = set(inter) - set(defaults)
    if unknown:
        raise ValueError(f"intermediários desconhecidos: {sorted(unknown)}")
    defaults.update({k: v for k, v in inter.items() if v is not None})
    return Formats(fix=fix, acc=acc, **defaults)


def sqrt_type(int_bits: int, frac_bits: int) -> FixedType:
    """sqrt_t: o hls::sqrt só tem overload para ap_fixed com os modos padrão."""
    return fixed_type(int_bits, frac_bits, "AP_TRN", "AP_WRAP")


def check_formats(fmt: Formats):
    """Recusa formatos em que o modelo deixaria de ser igual ao hardware.

    hls::sqrt (etc/hls_sqrt_apfixed.h) só usa o algoritmo modelado em
    isqrt_fixed() fora destes casos: F = 0 com I <= 13 e F <= 4 com I <= 5
    usam tabelas; I > 34 ou F > 32 devolvem 0. I <= 0 tem tratamento próprio.
    """
    sq = fmt.sqrt
    I, F = sq.int_bits, sq.frac
    if I <= 0 or F < 0 or I > 34 or F > 32 or (F == 0 and I <= 13) or (F <= 4 and I <= 5):
        raise ValueError(
            f"sqrt ap_fixed<{sq.width},{I}>: hls::sqrt usa outro algoritmo neste formato "
            "e o modelo não seria bit a bit (precisa de 0 < I <= 34, 0 <= F <= 32, "
            "fora de F = 0 com I <= 13 e de F <= 4 com I <= 5)")
    fix, acc = fmt.fix, fmt.acc
    if acc.int_bits < fix.int_bits or acc.frac < fix.frac:
        raise ValueError(
            f"acumulador ap_fixed<{acc.width},{acc.int_bits}> menor que o tipo de "
            f"dados ap_fixed<{fix.width},{fix.int_bits}>")


FORMATS = make_formats()   # formato atual de cholesky.h

# Nome de cada intermediário na CLI (--<nome>-int-bits etc.) e em cholesky.h
INTERMEDIATES = {
    "mulin": "operandos de cada multiplicador (CHOL_MULIN_*)",
    "prod": "produto real a*b (CHOL_PROD_*)",
    "cmul": "a*b -/+ c*d do produto complexo (CHOL_CMUL_*)",
    "num": "numerador x*conj(y) da divisão complexa (CHOL_NUM_*)",
    "norm": "|y|^2, divisor da divisão complexa (CHOL_NORM_*)",
    "quot": "quociente da divisão (CHOL_QUOT_*)",
    "sum": "soma acumulada (CHOL_SUM_*)",
    "sqrt": "entrada e saída da raiz, só bits (CHOL_SQRT_*)",
}

# A raiz só aceita os modos padrão do ap_fixed
BITS_ONLY = {"sqrt"}


def resolve_intermediate(base: Formats, name: str, int_bits=None, frac_bits=None,
                         q_mode=None, o_mode=None) -> FixedType | None:
    """Tipo de um intermediário com os campos dados; os outros vêm do padrão.

    mulin sem nenhum campo continua sem conversão; com algum campo, os que
    faltam vêm do acumulador.
    """
    d = getattr(base, name)
    if d is None:
        if int_bits is None and frac_bits is None and q_mode is None and o_mode is None:
            return None
        d = base.acc
    if name in BITS_ONLY:
        if q_mode is not None or o_mode is not None:
            raise ValueError(f"{name}: só bits; os modos são fixos (AP_TRN, AP_WRAP)")
        return sqrt_type(d.int_bits if int_bits is None else int_bits,
                         d.frac if frac_bits is None else frac_bits)
    return fixed_type(d.int_bits if int_bits is None else int_bits,
                      d.frac if frac_bits is None else frac_bits,
                      q_mode or d.q_mode, o_mode or d.o_mode)


# Conta quantas atribuições ficaram fora da faixa do tipo (estouro), qualquer
# que seja o modo: saturação, zero ou volta.
_overflow_count = 0


def reset_overflow_count():
    global _overflow_count
    _overflow_count = 0


def get_overflow_count() -> int:
    return _overflow_count


# --------------------------------------------------------------------------
# Operações escalares
# --------------------------------------------------------------------------

def _quantize(v: int, shift: int, q_mode: str) -> int:
    """v / 2^shift (shift > 0) arredondado para inteiro (quantization_adjust).

    qb é o primeiro bit descartado, r diz se algum bit abaixo dele é 1 e s é
    o sinal da origem. Todos os modos partem do truncamento para -infinito.
    """
    base = v >> shift
    rem = v - (base << shift)            # bits descartados, 0 <= rem < 2^shift
    half = 1 << (shift - 1)
    qb = rem >= half
    r = (rem & (half - 1)) != 0
    s = v < 0
    if q_mode == "AP_TRN":
        inc = False
    elif q_mode == "AP_TRN_ZERO":
        inc = s and (qb or r)
    elif q_mode == "AP_RND":
        inc = qb
    elif q_mode == "AP_RND_ZERO":
        inc = qb and (s or r)
    elif q_mode == "AP_RND_MIN_INF":
        inc = qb and r
    elif q_mode == "AP_RND_INF":
        inc = qb and (not s or r)
    else:                                # AP_RND_CONV: empate vai para o par
        inc = qb and ((base & 1) == 1 or r)
    return base + inc


def _overflow(q: int, lD: int, T: FixedType) -> int:
    """Encaixa o inteiro q na faixa de T (overflow_adjust).

    lD é o bit logo acima do bit de sinal no valor de origem, antes do
    arredondamento; só AP_WRAP_SM usa.
    """
    global _overflow_count
    o = T.o_mode
    if T.min <= q <= T.max:
        # AP_SAT_SYM: a faixa é simétrica, o menor valor vira -max
        if o == "AP_SAT_SYM" and q == T.min:
            _overflow_count += 1
            return -T.max
        return q
    _overflow_count += 1
    if o == "AP_SAT":
        return T.max if q > 0 else T.min
    if o == "AP_SAT_SYM":
        return T.max if q > 0 else -T.max
    if o == "AP_SAT_ZERO":
        return 0
    W = T.width
    mask = (1 << W) - 1
    w = q & mask                         # AP_WRAP: só os W bits de baixo
    if o == "AP_WRAP_SM":
        # Sinal-magnitude: se o bit acima do sinal discorda do novo sinal,
        # inverte todos os bits e põe esse bit no lugar do sinal
        if lD != (w >> (W - 1)) & 1:
            w = (~w & mask & ~(1 << (W - 1))) | (lD << (W - 1))
    return w - (1 << W) if w >> (W - 1) else w


def to_type(v: int, frac: int, T: FixedType) -> int:
    """Atribui o valor exato v / 2^frac a uma variável do tipo T.

    Primeiro a quantização da parte fracionária (T.q_mode), depois o
    tratamento de estouro da parte inteira (T.o_mode).
    """
    shift = frac - T.frac
    if shift > 0:
        lD = (v >> (shift + T.width)) & 1
        q = _quantize(v, shift, T.q_mode)
    else:
        q = v << -shift
        lD = (q >> T.width) & 1
    return _overflow(q, lD, T)


def from_float(x: float, T: FixedType) -> int:
    """T(double), como o testbench faz ao ler A.txt. O double é exato em
    num / den com den potência de 2, então nenhum arredondamento extra entra."""
    num, den = x.as_integer_ratio()
    return to_type(num, den.bit_length() - 1, T)


def div_real(a: int, a_frac: int, b: int, b_frac: int) -> int:
    """Quociente a / b do ap_fixed, com a_frac bits fracionários (os do dividendo).

    O ap_fixed desloca o dividendo b_frac bits à esquerda e faz divisão inteira,
    que trunca em direção ao zero em qualquer modo de quantização. Quem chama
    atribui o resultado (com a_frac bits fracionários) ao tipo de destino.
    """
    if b == 0:
        raise ZeroDivisionError("divisão por zero em ponto fixo")
    num = a << b_frac
    q = abs(num) // abs(b)
    return -q if (num < 0) != (b < 0) else q


def isqrt_fixed(d: int, T: FixedType) -> int:
    """hls::sqrt em T (etc/hls_sqrt_apfixed.h).

    O sqrt_fixed do Vitis calcula a raiz bit a bit com F + 1 bits
    fracionários (truncada), soma meio LSB e trunca para F bits. O resultado
    é a raiz arredondada para o mais próximo, não a truncada.
    """
    if d < 0:                           # o hls::sqrt devolve 0 para negativo
        return 0
    t = math.isqrt(d << (T.frac + 2))   # sqrt(d / 2^F) * 2^(F+1), truncada
    return (t + 1) >> 1


# --------------------------------------------------------------------------
# Operações complexas (cholesky_ops.h)
# --------------------------------------------------------------------------
# O hardware não usa os operadores do std::complex<ap_fixed>: cada intermediário
# é uma variável com tipo próprio (Formats), para a síntese usar essas larguras.

def ccast(z, src: FixedType, dst: FixedType):
    """complex<dst>(z): converte parte real e imaginária separadamente."""
    return (to_type(z[0], src.frac, dst), to_type(z[1], src.frac, dst))


def cadd(x, y, T: FixedType):
    """Soma exata, atribuída a T (x e y já em T)."""
    return (to_type(x[0] + y[0], T.frac, T), to_type(x[1] + y[1], T.frac, T))


def csub(x, y, T: FixedType):
    """Subtração exata, atribuída a T (x e y já em T)."""
    return (to_type(x[0] - y[0], T.frac, T), to_type(x[1] - y[1], T.frac, T))


def cneg_to(x, src: FixedType, dst: FixedType):
    """-x (exato), atribuído a dst."""
    return (to_type(-x[0], src.frac, dst), to_type(-x[1], src.frac, dst))


def conj(x, T: FixedType):
    """conj(x) em T: -imag pode saturar (o menor valor não tem simétrico)."""
    return (x[0], to_type(-x[1], T.frac, T))


def _cmul_parts(x, tx: FixedType, y, ty: FixedType, fmt: Formats):
    """re = xr*yr - xi*yi e im = xr*yi + xi*yr, nos tipos cmul (produtos em prod).

    Com mulin, cada operando é convertido para ele antes de multiplicar.
    """
    if fmt.mulin is not None:
        x, tx = ccast(x, tx, fmt.mulin), fmt.mulin
        y, ty = ccast(y, ty, fmt.mulin), fmt.mulin
    pf = tx.frac + ty.frac
    rr = to_type(x[0] * y[0], pf, fmt.prod)
    ii = to_type(x[1] * y[1], pf, fmt.prod)
    ri = to_type(x[0] * y[1], pf, fmt.prod)
    ir = to_type(x[1] * y[0], pf, fmt.prod)
    re = to_type(rr - ii, fmt.prod.frac, fmt.cmul)
    im = to_type(ri + ir, fmt.prod.frac, fmt.cmul)
    return re, im


def cmul(x, tx: FixedType, y, ty: FixedType, out: FixedType, fmt: Formats):
    """cmul<out>(x, y): produto complexo atribuído a out."""
    re, im = _cmul_parts(x, tx, y, ty, fmt)
    return (to_type(re, fmt.cmul.frac, out), to_type(im, fmt.cmul.frac, out))


def cdiv(x, y, T: FixedType, fmt: Formats):
    """cdiv<T>(x, y), com x e y em T: x * conj(y) / |y|^2.

    O numerador x*conj(y) é guardado em num, |y|^2 em norm. O dividendo é
    convertido para quot antes de dividir, então o quociente tem os bits
    fracionários de quot; depois ele é atribuído a T.
    """
    cj = conj(y, T)
    a = cmul(x, T, cj, T, fmt.num, fmt)
    nr, _ = _cmul_parts(cj, T, y, T, fmt)
    n = to_type(nr, fmt.cmul.frac, fmt.norm)
    out = []
    for part in a:
        dividend = to_type(part, fmt.num.frac, fmt.quot)
        q = to_type(div_real(dividend, fmt.quot.frac, n, fmt.norm.frac),
                    fmt.quot.frac, fmt.quot)
        out.append(to_type(q, fmt.quot.frac, T))
    return tuple(out)


ZERO = (0, 0)


def one(T: FixedType):
    return (1 << T.frac, 0)


# --------------------------------------------------------------------------
# Etapas (uma função por arquivo .cpp)
# --------------------------------------------------------------------------

def lu_decomposition(A, fmt: Formats = FORMATS):
    """lu_decomposition.cpp"""
    fix, acc = fmt.fix, fmt.acc
    n = len(A)
    L = [[ZERO] * n for _ in range(n)]
    U = [list(row) for row in A]
    for i in range(n):
        L[i][i] = one(fix)

    for column in range(n):
        for line in range(column + 1, n):
            # Divisão no tipo do acumulador, resultado guardado no tipo de dados
            q = cdiv(ccast(U[line][column], fix, acc),
                     ccast(U[column][column], fix, acc), acc, fmt)
            L[line][column] = ccast(q, acc, fix)

            for k in range(column, n):
                temp_mult = cmul(ccast(L[line][column], fix, acc), acc,
                                 ccast(U[column][k], fix, acc), acc, acc, fmt)
                U[line][k] = csub(U[line][k], ccast(temp_mult, acc, fix), fix)
    return L, U


def d_extraction(U):
    """dv_step.cpp: D = diag(U)."""
    n = len(U)
    D = [[ZERO] * n for _ in range(n)]
    for i in range(n):
        D[i][i] = U[i][i]
    return D


def d_square_root(D, fmt: Formats = FORMATS):
    """s_step.cpp. Pivô <= 0 (truncamento) vira raiz zero, como no hardware.

    O pivô vai para sqrt (modos padrão), o hls::sqrt devolve em sqrt e o
    resultado é atribuído ao tipo de dados.
    """
    fix, sq = fmt.fix, fmt.sqrt
    S = []
    for i in range(len(D)):
        d = D[i][i][0]
        if d > 0:
            r = isqrt_fixed(to_type(d, fix.frac, sq), sq)
            S.append((to_type(r, sq.frac, fix), 0))
        else:
            S.append((0, 0))
    return S


def g_decomposition(S, L, fmt: Formats = FORMATS):
    """g_step.cpp: cada coluna de L escalada por S[coluna]."""
    fix = fmt.fix
    n = len(L)
    G = [[ZERO] * n for _ in range(n)]
    for line in range(n):
        for column in range(line + 1):
            G[line][column] = cmul(L[line][column], fix, S[column], fix, fix, fmt)
    return G


def forward_substitution(G, fmt: Formats = FORMATS):
    """foward_substitution.cpp: G * G_inv = I, uma coluna por vez."""
    fix, acc = fmt.fix, fmt.acc
    n = len(G)
    G_inv = [[ZERO] * n for _ in range(n)]
    aux = one(fix)

    for column in range(n):
        q = cdiv(ccast(aux, fix, acc), ccast(G[column][column], fix, acc), acc, fmt)
        G_inv[column][column] = ccast(q, acc, fix)

        for line in range(column + 1, n):
            sum_terms = ZERO
            for k in range(column, line):
                term = cmul(ccast(G[line][k], fix, acc), acc,
                            ccast(G_inv[k][column], fix, acc), acc, fmt.sum, fmt)
                sum_terms = cadd(sum_terms, term, fmt.sum)

            q = cdiv(cneg_to(sum_terms, fmt.sum, acc),
                     ccast(G[line][line], fix, acc), acc, fmt)
            G_inv[line][column] = ccast(q, acc, fix)
    return G_inv


def inversion(G_inv, fmt: Formats = FORMATS):
    """inversion.cpp: inverse[i][j] = soma_k conj(G_inv[k][i]) * G_inv[k][j]."""
    fix, acc = fmt.fix, fmt.acc
    n = len(G_inv)
    inverse = [[ZERO] * n for _ in range(n)]
    for line in range(n):
        for column in range(n):
            sum_terms = ZERO
            for k in range(max(line, column), n):
                y_ki = ccast(G_inv[k][line], fix, acc)
                y_kj = ccast(G_inv[k][column], fix, acc)
                term = cmul(conj(y_ki, acc), acc, y_kj, acc, fmt.sum, fmt)
                sum_terms = cadd(sum_terms, term, fmt.sum)
            inverse[line][column] = ccast(sum_terms, fmt.sum, fix)
    return inverse


def cholesky_decomposition(A_fixed, fmt: Formats = FORMATS):
    """cholesky_decomposition.cpp sem V. Recebe A já no tipo de dados (inteiros)."""
    check_formats(fmt)
    L, U = lu_decomposition(A_fixed, fmt)
    D = d_extraction(U)
    S = d_square_root(D, fmt)
    G = g_decomposition(S, L, fmt)
    G_inv = forward_substitution(G, fmt)
    inverse = inversion(G_inv, fmt)
    return {"A": A_fixed, "L": L, "U": U, "D": D, "S": S,
            "G": G, "G_inv": G_inv, "inverse": inverse}


# --------------------------------------------------------------------------
# Conversão de/para números complexos
# --------------------------------------------------------------------------

def quantize_matrix(A, T: FixedType = FIX):
    """Matriz de complexos (lista de listas ou numpy) -> inteiros do tipo T."""
    return [[(from_float(complex(z).real, T), from_float(complex(z).imag, T))
             for z in row] for row in A]


def to_complex(z, T: FixedType = FIX) -> complex:
    scale = 1 << T.frac
    return complex(z[0] / scale, z[1] / scale)


def to_complex_matrix(M, T: FixedType = FIX):
    return [[to_complex(z, T) for z in row] for row in M]


def invert(A, fmt: Formats = FORMATS):
    """A^-1 como o hardware calcularia, a partir de uma matriz de complexos.

    Monte fmt com make_formats() (tipos de dados, acumulador e intermediários).
    """
    result = cholesky_decomposition(quantize_matrix(A, fmt.fix), fmt)
    return to_complex_matrix(result["inverse"], fmt.fix)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

# Mesmos nomes do testbench (sem o 04, que era V). Cada etapa vira um .txt
# (decimal, para leitura) e um .bits (bits crus, usado na comparação).
OUTPUT_FILES = [
    ("A", "00_A"), ("L", "01_L"), ("U", "02_U"), ("D", "03_D"), ("S", "05_S"),
    ("G", "06_G"), ("G_inv", "07_G_inv"), ("inverse", "08_inverse"),
]


def to_bits(v: int, T: FixedType) -> str:
    """Os T.width bits do registrador, em complemento de dois."""
    return format(v & ((1 << T.width) - 1), f"0{T.width}b")


def print_types(fmt: Formats):
    """Uma linha "TIPO <nome> ap_fixed<W,I,Q,O>" por tipo, no mesmo texto que o
    testbench imprime, para um script conferir os dois com diff. mulin só
    aparece quando existe (sem ele não há conversão), como no testbench."""
    for name in ("fix", "acc", "mulin", "prod", "cmul", "num", "norm", "quot", "sum",
                 "sqrt"):
        T = getattr(fmt, name)
        if T is not None:
            print(f"TIPO {name} {T}")


def read_float_bits(path: str):
    """Lê uma matriz de entrada em .bits: n, depois "real:imag" por elemento,
    com os 64 bits IEEE 754 de cada parte (o formato do exportar_matrizes.py).

    Recusa qualquer outra largura: um .bits de saída do hardware tem a largura
    do fixed_t e não pode ser lido como entrada por engano.
    """
    with open(path) as f:
        linhas = [l.split() for l in f.read().splitlines() if l.strip()]
    if not linhas or len(linhas[0]) != 1:
        raise ValueError(f"{path}: a primeira linha deve ter só a dimensão n")
    n = int(linhas[0][0])
    if len(linhas) - 1 != n:
        raise ValueError(f"{path}: esperava {n} linhas de matriz, encontrou {len(linhas) - 1}")
    matrix = []
    for i, linha in enumerate(linhas[1:]):
        if len(linha) != n:
            raise ValueError(f"{path}: linha {i} tem {len(linha)} elementos, esperado {n}")
        row = []
        for tok in linha:
            partes = tok.split(":")
            if (len(partes) != 2 or any(len(p) != 64 or set(p) - {"0", "1"} for p in partes)):
                raise ValueError(f"{path}: elemento {tok[:20]}... não tem a forma "
                                 "<64 bits>:<64 bits> de um float64 IEEE 754")
            re, im = (struct.unpack("<d", struct.pack("<Q", int(p, 2)))[0] for p in partes)
            row.append(complex(re, im))
        matrix.append(row)
    return n, matrix


def read_input_matrix(path: str):
    """Matriz de entrada: .bits (float64 em bits) ou texto no formato do A.txt."""
    if path.endswith(".bits"):
        return read_float_bits(path)
    from golden import read_matrix
    return read_matrix(path)


def write_bits(path: str, n: int, rows, T: FixedType):
    """Formato .bits do testbench: n, depois "real:imag" por elemento."""
    with open(path, "w") as f:
        f.write(f"{n}\n")
        for row in rows:
            f.write(" ".join(f"{to_bits(z[0], T)}:{to_bits(z[1], T)}" for z in row) + "\n")


def compare_bits(ours_path: str, theirs_path: str):
    """Compara dois .bits. Devolve (n de elementos diferentes, descrição do 1o)."""
    with open(ours_path) as f:
        ours = [line.split() for line in f.read().split("\n")[1:] if line.strip()]
    with open(theirs_path) as f:
        theirs = [line.split() for line in f.read().split("\n")[1:] if line.strip()]
    if [len(r) for r in ours] != [len(r) for r in theirs]:
        return -1, "dimensões diferentes"
    n_diff, first = 0, ""
    for i, (ro, rt) in enumerate(zip(ours, theirs)):
        for j, (eo, et) in enumerate(zip(ro, rt)):
            if eo == et:
                continue
            n_diff += 1
            if not first:
                if len(eo) != len(et):
                    first = f"[{i}][{j}] larguras diferentes: py {eo} / hw {et}"
                else:
                    marks = "".join("^" if a != b else " " for a, b in zip(eo, et))
                    first = (f"[{i}][{j}] (real:imag)\n      py {eo}\n      hw {et}"
                             f"\n         {marks}")
    return n_diff, first


def main():
    # Só a CLI lê e grava arquivos; importar o módulo (ex.: pelo simulador) não
    # depende de golden.py.
    from golden import write_matrix

    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description="Modelo bit a bit da inversão por Cholesky do hardware.")
    parser.add_argument("input", nargs="?", default=os.path.join(here, "A.txt"),
                        help="Matriz A de entrada: .bits (float64 IEEE 754 em bits, como "
                             "os de testes/matrizes/) ou texto no formato do A.txt "
                             "(padrão: A.txt)")
    parser.add_argument("-o", "--out-dir", default=os.path.join(here, "golden_results"),
                        help="Pasta de saída (padrão: golden_results/)")
    parser.add_argument("--compare", metavar="HW_DIR",
                        help="Compara bit a bit cada etapa com hw_<nome>.bits desta "
                             "pasta (ex.: hw_results/)")
    parser.add_argument("--int-bits", type=int, default=FIX.int_bits,
                        help=f"Bits inteiros do tipo de dados, com o sinal "
                             f"(padrão: {FIX.int_bits})")
    parser.add_argument("--frac-bits", type=int, default=FIX.frac,
                        help=f"Bits fracionários do tipo de dados (padrão: {FIX.frac})")
    parser.add_argument("--acc-int-bits", type=int, default=None,
                        help="Bits inteiros do acumulador (padrão: o dobro de --int-bits)")
    parser.add_argument("--acc-frac-bits", type=int, default=None,
                        help="Bits fracionários do acumulador (padrão: o dobro de "
                             "--frac-bits)")
    parser.add_argument("--quant", choices=QUANT_MODES, default=FIX.q_mode,
                        help=f"Quantização da parte fracionária dos dados "
                             f"(padrão: {FIX.q_mode})")
    parser.add_argument("--overflow", choices=OVERFLOW_MODES, default=FIX.o_mode,
                        help=f"Estouro da parte inteira dos dados (padrão: {FIX.o_mode})")
    parser.add_argument("--acc-quant", choices=QUANT_MODES, default=None,
                        help="Quantização do acumulador (padrão: igual a --quant)")
    parser.add_argument("--acc-overflow", choices=OVERFLOW_MODES, default=None,
                        help="Estouro do acumulador (padrão: igual a --overflow)")
    inter = parser.add_argument_group(
        "intermediários (cholesky.h: CHOL_PROD_*, CHOL_CMUL_*, CHOL_NORM_*, CHOL_QUOT_*, "
        "CHOL_SUM_*); sem a opção, vale o padrão, que reproduz o hardware sem tipos "
        "intermediários; os modos padrão são os do acumulador")
    for name, what in INTERMEDIATES.items():
        inter.add_argument(f"--{name}-int-bits", type=int, help=f"{what}: bits inteiros")
        inter.add_argument(f"--{name}-frac-bits", type=int,
                           help=f"{what}: bits fracionários")
        if name in BITS_ONLY:
            continue
        inter.add_argument(f"--{name}-quant", choices=QUANT_MODES,
                           help=f"{what}: quantização")
        inter.add_argument(f"--{name}-overflow", choices=OVERFLOW_MODES,
                           help=f"{what}: estouro")
    args = parser.parse_args()

    fix = fixed_type(args.int_bits, args.frac_bits, args.quant, args.overflow)
    acc = default_acc(fix)
    acc = fixed_type(acc.int_bits if args.acc_int_bits is None else args.acc_int_bits,
                     acc.frac if args.acc_frac_bits is None else args.acc_frac_bits,
                     args.acc_quant or fix.q_mode, args.acc_overflow or fix.o_mode)
    base_fmt = make_formats(fix, acc)
    chosen = {name: resolve_intermediate(
                  base_fmt, name, getattr(args, f"{name}_int_bits"),
                  getattr(args, f"{name}_frac_bits"), getattr(args, f"{name}_quant", None),
                  getattr(args, f"{name}_overflow", None))
              for name in INTERMEDIATES}
    fmt = make_formats(fix, acc, **chosen)

    n, A = read_input_matrix(args.input)
    reset_overflow_count()
    try:
        result = cholesky_decomposition(quantize_matrix(A, fix), fmt)
    except ZeroDivisionError:
        # O C++ divide por zero no mesmo ponto (comportamento indefinido; na
        # C-simulation o programa termina com "Floating point exception")
        print_types(fmt)
        print(f"FALHA: divisão por zero (um pivô ficou <= 0 depois do truncamento e "
              f"dos estouros; {get_overflow_count()} valores estouraram a faixa antes). "
              "O hardware também divide por zero neste caso.")
        sys.exit(2)

    os.makedirs(args.out_dir, exist_ok=True)
    for key, name in OUTPUT_FILES:
        rows = result[key] if key != "S" else [result[key]]   # S vai em uma linha
        base = os.path.join(args.out_dir, "golden_" + name)
        write_matrix(base + ".txt", n, to_complex_matrix(rows, fix), fix.frac)
        write_bits(base + ".bits", n, rows, fix)

    print_types(fmt)
    n_ovf = get_overflow_count()
    print("Nenhum valor estourou a faixa." if n_ovf == 0
          else f"ATENCAO: {n_ovf} valores estouraram a faixa.")
    print(f"Resultados em {args.out_dir}/")

    if args.compare:
        # Comparação bit a bit pelos .bits (^ marca os bits que diferem)
        print(f"Comparação bit a bit com {args.compare}/hw_*.bits:")
        all_equal = True
        for _, name in OUTPUT_FILES:
            theirs = os.path.join(args.compare, "hw_" + name + ".bits")
            if not os.path.exists(theirs):
                print(f"  {name:12s} FALTA {theirs} (rode de novo a C-simulation com o "
                      "testbench atual, que grava os .bits)")
                all_equal = False
                continue
            n_diff, first = compare_bits(
                os.path.join(args.out_dir, "golden_" + name + ".bits"), theirs)
            all_equal &= n_diff == 0
            if n_diff == 0:
                print(f"  {name:12s} igual")
            elif n_diff < 0:
                print(f"  {name:12s} {first}")
            else:
                print(f"  {name:12s} {n_diff} elementos diferentes; primeiro em {first}")
        sys.exit(0 if all_equal else 1)


if __name__ == "__main__":
    main()
