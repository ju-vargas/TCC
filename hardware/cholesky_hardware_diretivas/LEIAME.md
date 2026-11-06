# cholesky_hardware_diretivas

VERSAO SALVA em 2026-10-30: alteracoes 1 a 3, 5 e 6 (a 4 foi desfeita).
7.593 ciclos por inversao na co-simulacao (<24,12> RND_ZERO/WRAP, 16 x 16),
inversa igual ao original bit a bit. Atende o TDLA30-5 (9.090 ciclos).
Nao editar os fontes desta pasta; os testes seguintes ficam em
../cholesky_hardware_diretivas_4545/.

Copia de ../cholesky_hardware/ (fontes de 2026-10-30) para testar diretivas HLS
sem mexer no codigo das sinteses de referencia nem no servidor das curvas de SER.

- Fontes do hardware: cholesky.h, cholesky_ops.h e os .cpp das etapas.
- tb_lu_decomposition.cpp e hls_config.cfg: C-simulation, como na pasta original.
- comparar_com_original.py: confere que a inversa destes fontes e igual, bit a bit,
  a do codigo original (servidor ja compilado em ../cholesky_hardware_servidor/build/),
  nos tres formatos escolhidos, 16 x 16 e 32 x 32. Usa tb_servidor.cpp e
  compilar_servidor.sh (copias de ../cholesky_hardware_servidor/), que compilam em build/.

      taskset -c 4-7 ../../software/simulador/.venv/bin/python comparar_com_original.py

- sintese/: sintese C de cholesky_inverse em <24,12> RND_ZERO/WRAP, 16 x 16, para
  comparar com ../cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/.
  Rodar com sintese/rodar.sh (nucleos 4 a 7).

# Alteracoes em relacao ao original

Original: ../cholesky_hardware/ (sem nenhuma diretiva). Referencia de sintese:
../cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/ (<24,12>
AP_RND_ZERO/AP_WRAP, 16 x 16, 100 MHz, pipeline_loops=0).

## 1. LU: divisoes separadas da atualizacao (2026-10-30)

Arquivo: lu_decomposition.cpp, laco principal (linhas 25 a 44).

Antes, cada linha fazia a divisao e logo depois a atualizacao. A divisao da
linha seguinte esperava a atualizacao terminar, e o divisor sequencial levava
76 ciclos por divisao.

```cpp
for (int column = 0; column < n; column++) {
    for (int line = column + 1; line < n; line++) {
        // Cast para o acumulador ANTES de dividir para evitar que (c^2 + d^2) estoure os bits inteiros do fixed_t
        L[line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
            (acc_complex_t)U[line][column], (acc_complex_t)U[column][column]);

        for (int k = column; k < n; k++) {
            acc_complex_t temp_mult = cmul<acc_fixed_t>(
                (acc_complex_t)L[line][column], (acc_complex_t)U[column][k]);
            complex_fixed_t t = (complex_fixed_t)temp_mult;
            U[line][k] = complex_fixed_t(fixed_t(U[line][k].real() - t.real()),
                                         fixed_t(U[line][k].imag() - t.imag()));
        }
    }
}
```

Agora, cada coluna tem dois lacos: primeiro todas as divisoes da coluna, em
fila no divisor (pipeline II=1); depois a atualizacao das linhas (pipeline
II=1 no laco de k).

```cpp
for (int column = 0; column < n; column++){
    for (int line = column + 1; line < n; line++){
    #pragma HLS pipeline II=1
        L[line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
            (acc_complex_t)U[line][column], (acc_complex_t)U[column][column]
            );
    }

    for (int line = column + 1; line < n; line++){
        for (int k = column; k < n; k++) {
    #pragma HLS pipeline II=1
            acc_complex_t temp_mult = cmul<acc_fixed_t>(
                (acc_complex_t)L[line][column], (acc_complex_t)U[column][k]
            );
            complex_fixed_t t = (complex_fixed_t)temp_mult;
            U[line][k] = complex_fixed_t(fixed_t(U[line][k].real() - t.real()),
                                         fixed_t(U[line][k].imag() - t.imag()));
        }
    }
}
```

Por que o resultado nao muda: as divisoes de uma mesma coluna leem so
U[line][column] e U[column][column], e a atualizacao de uma linha nao escreve
nesses valores das outras linhas. As contas sao as mesmas, na mesma ordem
para cada elemento. O comentario sobre o cast para o acumulador saiu junto.

Conferencia de bits (comparar_com_original.py, 30 matrizes por tamanho):
igual nos 6 casos (<22,12>, <24,12> e <28,14>, 16 x 16 e 32 x 32).

Sintese C (sintese/rodar.sh), contra a referencia. Ciclos estimados pelo
relatorio do HLS, que conta o pior caso dos lacos triangulares; a
co-simulacao ainda nao foi rodada.

| | Referencia | Com a alteracao 1 |
|---|---|---|
| Ciclos estimados, total | 69.532 | 46.057 |
| Ciclos estimados, LU | 29.168 | 5.693 |
| DSP | 94 | 106 |
| LUT | 12.079 | 24.357 (2%) |
| FF | 5.454 | 21.557 (1%) |
| BRAM | 11 | 11 |

- Laco das divisoes: II = 1, profundidade 78. O divisor em pipeline da LU
  custa 17.797 FF e 13.739 LUT.
- A ferramenta juntou sozinha os lacos de line e k da atualizacao num laco so
  (VITIS_LOOP_33_6_VITIS_LOOP_34_7), com II = 1.
- A forward substitution continua com o divisor sequencial
  (sdiv_72ns_48s_48_76_seq).
- Aviso novo no log: "may have out of bound array access on variable U"
  (lu_decomposition.cpp:29). A conferencia de bits passou; parece um aviso
  conservador da ferramenta, mas isso nao foi conferido.
- Pela recontagem com os trip counts reais (sem fonte, estimativa), a LU deve
  cair de cerca de 14.150 para cerca de 2.800 ciclos, e o total de cerca de
  32.500 para cerca de 21.000. Falta medir na co-simulacao.

## 2. Forward substitution: uma linha por vez, divisoes em fila (2026-10-30)

Arquivo: foward_substitution.cpp, laco principal (linhas 21 a 55).

Motivo: dentro de uma coluna ha uma cadeia, porque G_inv[line][column] depende
de G_inv[k][column] para todo k < line. Andando coluna por coluna, cada
divisao esperava a anterior, e as 136 divisoes rodavam em serie no divisor
sequencial (76 ciclos cada). Mas colunas diferentes sao independentes (cada
uma vem de uma coluna da identidade). Andando linha por linha, as divisoes de
todas as colunas de uma linha entram em fila no divisor com pipeline.

Antes (uma coluna por vez):

```cpp
for (int column = 0; column < n; column++){

    G_inv[column][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
        (acc_complex_t)aux, (acc_complex_t)G[column][column]);

    for (int line = column + 1; line < n; line++){
        sum_complex_t sum_terms(0,0);

        for (int k = column; k < line; k++){
            sum_complex_t term = cmul<sum_t>(
                (acc_complex_t)G[line][k], (acc_complex_t)G_inv[k][column]);
            sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                                      sum_t(sum_terms.imag() + term.imag()));
        }

        acc_complex_t neg_sum(acc_fixed_t(-sum_terms.real()),
                              acc_fixed_t(-sum_terms.imag()));
        G_inv[line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
            neg_sum, (acc_complex_t)G[line][line]);
    }

}
```

Agora (uma linha por vez; primeiro as somas de cada coluna, depois as
divisoes em fila):

```cpp
for (int line = 0; line < n; line++){
    sum_complex_t sums[MATRIX_DIM];

    for (int column = 0; column < line; column++){
        sum_complex_t sum_terms(0,0);

        for (int k = column; k < line; k++){
    #pragma HLS pipeline II=1
            sum_complex_t term = cmul<sum_t>(
                (acc_complex_t)G[line][k], (acc_complex_t)G_inv[k][column]);
            sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                                      sum_t(sum_terms.imag() + term.imag()));
        }

        sums[column] = sum_terms;
    }

    for (int column = 0; column <= line; column++){
    #pragma HLS pipeline II=1
        acc_complex_t num = (column == line)
            ? (acc_complex_t)aux
            : acc_complex_t(acc_fixed_t(-sums[column].real()),
                            acc_fixed_t(-sums[column].imag()));
        G_inv[line][column] = (complex_fixed_t)cdiv<acc_fixed_t>(
            num, (acc_complex_t)G[line][line]);
    }
}
```

Por que o resultado nao muda:
- G_inv[line][column] usa G_inv[k][column] com column <= k < line. Os de
  k < line ja foram calculados nas linhas anteriores, e G_inv[column][column]
  na linha column.
- Cada soma continua com k em ordem crescente, a partir de column, com os
  mesmos tipos (cmul<sum_t> e soma em sum_t).
- A diagonal 1 / G[line][line] entra no laco das divisoes, com numerador
  (acc_complex_t)aux, o mesmo de antes. Os elementos fora da diagonal usam o
  mesmo neg_sum de antes. Assim ha uma so chamada da cdiv e um so divisor em
  pipeline; duas chamadas virariam dois divisores, com o dobro do custo.
- O laco que zera G_inv nao mudou.

## 3. Inversao: pipeline no laco da soma (2026-10-30)

Arquivo: inversion.cpp, linha 21.

Motivo: o laco de k levava 3 ciclos por iteracao. Com pipeline II=1, uma
iteracao comeca a cada ciclo. Nao ha divisao aqui, e a soma em ponto fixo leva
1 ciclo, entao nao impede o II=1.

```cpp
for (int k = start; k < n; k++){
    #pragma HLS pipeline II=1          // linha nova; o resto nao mudou
    acc_complex_t y_ki = (acc_complex_t)G_inv[k][line];
    ...
}
```

Por que o resultado nao muda: so a diretiva entrou; as contas e a ordem de k
sao as mesmas.

## Conferencia das alteracoes 1 a 3

Bits (comparar_com_original.py --por-tamanho 1000, ou seja, todas as matrizes
de testes/3_selecao_matrizes: 336 de 16 x 16 e 218 de 32 x 32):

| Formato | 16 x 16 | 32 x 32 |
|---|---|---|
| <22,12> RND_ZERO/WRAP | igual, 336/336 (1 falha nos dois) | igual, 218/218 |
| <24,12> RND_ZERO/WRAP | igual, 336/336 | igual, 218/218 |
| <28,14> RND_ZERO/WRAP | igual, 336/336 | igual, 218/218 |

A "falha nos dois" e uma matriz em que o original tambem falha (divisao por
zero); o novo codigo falha na mesma matriz.

Teste negativo do script: trocar de proposito o conj na inversao
(cmul(y_ki, conj(y_kj))) deu "diferente" em 10 de 10 matrizes, nos dois
tamanhos. Depois o arquivo voltou ao normal e a conferencia acima foi refeita.

Sintese C (sintese/rodar.sh), <24,12> RND_ZERO/WRAP, 16 x 16. Ciclos estimados
pelo relatorio do HLS (pior caso dos lacos triangulares):

| | Referencia | So alteracao 1 | Alteracoes 1 a 3 |
|---|---|---|---|
| Ciclos estimados, total | 69.532 | 46.057 | 19.004 |
| LU | 29.168 | 5.693 | 5.693 |
| Forward substitution | 26.559 | 26.559 | 6.674 |
| Inversao | 12.833 | 12.833 | 5.665 |
| DSP | 94 | 106 | 106 (1%) |
| LUT | 12.079 | 24.357 | 36.379 (4%) |
| FF | 5.454 | 21.557 | 37.692 (2%) |
| BRAM | 11 | 11 | 11 |

- Todos os lacos com diretiva chegaram a II = 1 (log da sintese).
- Ha dois divisores em pipeline, um na LU e um na forward substitution, cada
  um com cerca de 14 mil LUT e 18 mil FF. Sao a maior parte do aumento.
- O aviso "may have out of bound array access on variable U"
  (lu_decomposition.cpp:29) continua. A conferencia de bits passou.
- Estimativa minha com os trip counts reais (sem co-simulacao): LU cerca de
  3.400, forward substitution cerca de 3.000, inversao cerca de 3.100 e o resto
  (lacos que zeram matrizes, raiz e G) cerca de 1.600 ciclos. Total de cerca
  de 11.000 ciclos, contra 32.463 medidos na referencia. Ainda acima dos 9.090
  do TDLA30-5. Falta medir na co-simulacao.
- O que sobra sem diretiva: os lacos que zeram L, D, G e G_inv, o laco de G e
  as saidas e entradas de cada (i, j) na inversao.

## 4. Sem os zeramentos que a inversa nao usa (2026-10-30)

DESFEITA em 2026-10-30. O ganho foi pequeno (cerca de 300 ciclos estimados) e
mudava os intermediarios de cholesky_decomposition. Os quatro lacos voltaram;
lu_decomposition.cpp, dv_step.cpp, g_step.cpp e foward_substitution.cpp estao
como nas alteracoes 1 a 3. Depois de desfazer: bits iguais ao original nos 6
casos (todas as matrizes) e sintese C de volta a 19.004 ciclos, 106 DSP,
36.379 LUT e 37.692 FF. O registro abaixo fica como historico.

Motivo: quatro lacos so escreviam zero em partes das matrizes que nenhuma
etapa le no caminho ate a inversa. Cada um custava cerca de 290 ciclos.

| Arquivo | Laco tirado | Por que nao faz falta |
|---|---|---|
| lu_decomposition.cpp:11-17 | L = 0 (o laco continua, so com a copia A -> U) | G_decomposition le L so na diagonal e abaixo; a diagonal recebe 1 e a parte de baixo e escrita pela LU |
| dv_step.cpp:12-17 | D = 0 | D_square_root le so D[line][line] |
| g_step.cpp:12-17 | G = 0 | forward_substitution le G[line][k] com k <= line; essa parte e toda escrita pelo laco G = L x S |
| foward_substitution.cpp:14-19 | G_inv = 0 | forward_substitution e inversion leem G_inv[k][c] so com k >= c; essa parte e toda escrita |

Antes (exemplo do G; os outros tres sao iguais, com L, D e G_inv):

```cpp
//comecar com a matriz G zerada
for (int i = 0; i < n; i++){
    for (int j = 0; j < n; j++){
        G[i][j].real(0);
        G[i][j].imag(0);
    }
}
```

Agora: o laco saiu, e um comentario no lugar diz por que.

O zeramento de S (s_step.cpp:12-15) ficou: quando o pivo sai <= 0,
S[line].real nao e escrito no laco da raiz e precisa valer zero.

Efeito colateral: em cholesky_decomposition, que expoe L, D, G e G_inv como
portas, a parte de cima dessas matrizes (e D fora da diagonal) fica com o que
o testbench tinha nelas antes, em vez de zero. A inversa nao muda. Os arquivos
de intermediarios do tb_lu_decomposition mudam nessas posicoes.

Conferencia de bits (todas as matrizes da selecao): igual nos 6 casos, com as
mesmas contagens da conferencia anterior (336/336 e 218/218; 1 falha nos dois
em <22,12> 16 x 16).

Sintese C, <24,12> RND_ZERO/WRAP, 16 x 16:

| | Alteracoes 1 a 3 | Alteracoes 1 a 4 |
|---|---|---|
| Ciclos estimados, total | 19.004 | 18.697 |
| DSP | 106 | 106 |
| LUT | 36.379 | 35.963 |
| FF | 37.692 | 37.626 |

O ganho foi menor que os cerca de 1.150 ciclos somados dos quatro lacos. Pelo
relatorio, a ferramenta ja rodava os zeramentos de D e G em paralelo com
outras etapas (eles nao dependem de nada), entao eles quase nao contavam no
total. O ganho real veio do zeramento de G_inv (288 ciclos, dentro da
forward substitution) e de parte do de L.

Estimativa minha com os trip counts reais (sem co-simulacao): cerca de 9.800
ciclos, contra 32.463 medidos na referencia e cerca de 11.000 antes desta
alteracao. Ainda um pouco acima dos 9.090 do TDLA30-5.

O que sobra sem diretiva: a copia A -> U na LU (544 ciclos, 2 por elemento), o
laco de G = L x S (cerca de 440 ciclos reais), a raiz (128) e as entradas e
saidas de cada (i, j) na inversao (cerca de 1.400 ciclos).

## 5. Inversao: os tres lacos juntados num so (opcao A, 2026-10-30)

Arquivo: inversion.cpp.

Motivo: depois da alteracao 3, o laco de k tinha pipeline, mas era curto
(1 a 16 iteracoes) e rodava 256 vezes, uma por (line, column). A cada vez o
pipeline enchia e esvaziava, cerca de 5 a 6 ciclos perdidos. Isso somava
cerca de 1.500 ciclos. A ferramenta nao junta os lacos sozinha, porque o
inicio de k depende de line e column. Juntando a mao (como o merge sort do
livro, cap. 10), o pipeline nao esvazia mais: um termo por ciclo, do comeco
ao fim.

Antes (alteracao 3):

```cpp
for (int line = 0; line < n; line++){
    for (int column = 0; column < n; column++){
        int start = (line > column) ? line : column;

        sum_complex_t sum_terms(0,0);
        for (int k = start; k < n; k++){
    #pragma HLS pipeline II=1
            acc_complex_t y_ki = (acc_complex_t)G_inv[k][line];
            acc_complex_t y_kj = (acc_complex_t)G_inv[k][column];
            sum_complex_t term = cmul<sum_t>(conj_t(y_ki), y_kj);
            sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                                      sum_t(sum_terms.imag() + term.imag()));
        }

        inverse[line][column] = (complex_fixed_t)sum_terms;
    }
}
```

Agora (um laco so, com line, column e k avancando por dentro):

```cpp
const int n_terms = MATRIX_DIM * (MATRIX_DIM + 1) * (2 * MATRIX_DIM + 1) / 6;

int line = 0;
int column = 0;
int k = 0;
sum_complex_t sum_terms(0,0);

for (int it = 0; it < n_terms; it++){
    #pragma HLS pipeline II=1
    acc_complex_t y_ki = (acc_complex_t)G_inv[k][line];
    acc_complex_t y_kj = (acc_complex_t)G_inv[k][column];
    sum_complex_t term = cmul<sum_t>(conj_t(y_ki), y_kj);
    sum_terms = sum_complex_t(sum_t(sum_terms.real() + term.real()),
                              sum_t(sum_terms.imag() + term.imag()));

    if (k == n - 1){
        inverse[line][column] = (complex_fixed_t)sum_terms;
        sum_terms = sum_complex_t(0,0);

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
```

- n_terms e o numero total de termos: cada (line, column) tem
  n - max(line, column) termos, e a soma de todos da n(n+1)(2n+1)/6 (1.496
  para 16 x 16 e 11.440 para 32 x 32).
- Quando k chega em n - 1, o elemento (line, column) terminou: grava a
  soma, zera, passa para o proximo (line, column) e volta k para
  max(line, column).

Por que o resultado nao muda: para cada (line, column), a soma comeca em
zero, percorre k de max(line, column) ate n - 1 em ordem crescente, com os
mesmos tipos (cmul<sum_t> e soma em sum_t), e e convertida para
complex_fixed_t do mesmo jeito. Muda so a forma de percorrer os indices.

Conferencia de bits (todas as matrizes da selecao): igual nos 6 casos
(336/336 e 218/218; 1 falha nos dois em <22,12> 16 x 16, a mesma de antes).

Sintese C, <24,12> RND_ZERO/WRAP, 16 x 16:

| | Alteracoes 1 a 3 | Alteracoes 1 a 3 e 5 |
|---|---|---|
| Ciclos estimados, total | 19.004 | 14.838 |
| Inversao | 5.665 (cerca de 3.100 reais) | 1.499 |
| DSP | 106 | 106 |
| LUT | 36.379 | 36.641 |
| FF | 37.692 | 37.823 |

- O laco unico chegou a II = 1, com 1.496 iteracoes e profundidade 4.
- O numero de iteracoes agora e fixo, entao os 1.499 ciclos da inversao no
  relatorio sao o valor real, nao um pior caso.
- Continua uma so unidade cmul (16 DSP); o custo extra foi de cerca de 260 LUT.
- Estimativa minha do total real (sem co-simulacao): cerca de 9.500 ciclos,
  contra cerca de 11.000 antes e 32.463 medidos na referencia. Ainda um pouco
  acima dos 9.090 do TDLA30-5.

## 6. Pipeline nos quatro lacos pequenos (2026-10-30)

Motivo: depois das alteracoes 1, 2, 3 e 5, estes lacos ainda levavam mais de
um ciclo por elemento. Em cada um entrou so a linha
`#pragma HLS pipeline II=1`, no laco de dentro; as contas nao mudaram.

| Arquivo:linha da diretiva | Laco | O que faz |
|---|---|---|
| lu_decomposition.cpp:13 | column, dentro de line | Zera L e copia A para U |
| g_step.cpp:22 | l_column, dentro de l_line | G = L x S |
| s_step.cpp:18 | line | Raiz da diagonal |
| foward_substitution.cpp:16 | column, dentro de line | Zera G_inv |

Exemplo (g_step.cpp; nos outros tres e igual, a linha nova logo abaixo do
`for`):

```cpp
for (int l_line = 0; l_line < n; l_line++){
    for (int l_column = 0; l_column <= l_line; l_column++){
    #pragma HLS pipeline II=1          // linha nova
        G[l_line][l_column] = cmul<fixed_t>(L[l_line][l_column], S[l_column]);
    }
}
```

Por que o resultado nao muda: so a diretiva entrou.

Conferencia de bits (todas as matrizes da selecao): igual nos 6 casos
(336/336 e 218/218; 1 falha nos dois em <22,12> 16 x 16, a mesma de antes).

Sintese C, <24,12> RND_ZERO/WRAP, 16 x 16. Todos os lacos com diretiva
chegaram a II = 1.

| Laco | Antes (ciclos) | Agora (ciclos) |
|---|---|---|
| Copia A -> U e zera L | 544 | 258 (a ferramenta juntou os dois lacos) |
| G = L x S | 800 no relatorio, cerca de 440 reais | 336 no relatorio, cerca de 220 reais |
| Raiz | 129 | 22 |
| Zera G_inv | 288 | 258 (a ferramenta juntou os dois lacos) |

| | Alteracoes 1 a 3 e 5 | Alteracoes 1 a 3, 5 e 6 |
|---|---|---|
| Ciclos estimados, total | 14.838 | 13.951 |
| DSP | 106 | 106 (1%) |
| LUT | 36.641 | 36.995 (4%) |
| FF | 37.823 | 37.932 (2%) |
| BRAM | 11 | 11 |

Estimativa minha do total real (sem co-simulacao): entre cerca de 8.300 e
8.900 ciclos, contra 32.463 medidos na referencia. Seria abaixo dos 9.090 do
TDLA30-5, mas com pouca folga, e a conta tem incerteza (a ferramenta roda
algumas etapas em paralelo). Precisa ser medido na co-simulacao.

## Co-simulacao das alteracoes 1 a 3, 5 e 6 (2026-10-30)

Pasta: cosim/ (rodar.sh, hls.cfg). Sintese C e co-simulacao RTL no xsim,
<24,12> AP_RND_ZERO/AP_WRAP, 16 x 16, 100 MHz, nucleos 4 a 7, cerca de 5 min.
Testbench: tb_potencia.cpp, com as mesmas 20 matrizes G_c do TDLA30-5 da
referencia (cosim/lista_TDLA30-5.txt, copia de
../cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/potencia/).

Relatorio: cosim/w/hls/sim/report/cholesky_inverse_cosim.rpt.

| | Referencia (medida) | Agora (co-simulacao) |
|---|---|---|
| Latencia por inversao | 32.463 ciclos | 7.593 ciclos (min = medio = max) |
| Intervalo entre inversoes | 32.463 ciclos | 7.594 ciclos |
| Tempo por inversao a 100 MHz | 324,6 us | 75,9 us |

- 4,3 vezes mais rapido que a referencia.
- Atende o TDLA30-5 (9.090 ciclos), com cerca de 16% de folga. Nao atende o
  TDLA30-10 (4.545) nem os cenarios mais rapidos.
- A minha estimativa era de 8.300 a 8.900 ciclos; o medido ficou abaixo. A
  ferramenta sobrepos mais etapas do que eu supus.
- Status da co-simulacao: Pass. O tb_potencia.cpp nao compara a saida, entao
  conferi a parte: o arquivo de saida do RTL
  (tv/rtldatafile/rtl.cholesky_inverse.autotvout_inverse.dat) e igual, byte a
  byte, ao do C (tv/cdatafile/c.cholesky_inverse.autotvout_inverse.dat), como
  no rodar_potencia.py da referencia.
- A referencia mediu os ciclos na netlist roteada do Vivado; aqui foi o RTL do
  HLS. Os ciclos devem ser os mesmos (o Vivado nao muda o escalonamento), mas
  os recursos e o caminho critico reais so saem com a implementacao no Vivado,
  que ainda nao foi rodada.

## Vivado (implementacao, 100 MHz)

Rodado nesta maquina em 2026-10-30 (fila ../fila_vivado.txt, Vivado 2026.1,
fluxo gerado pelo HLS). Valores depois do roteamento
(vivado/w/hls/impl/verilog/project.runs/impl_1/):

| LUT | FF | DSP | BRAM (BRAM_18K) | URAM | Caminho critico |
|---|---|---|---|---|---|
| 35.545 | 35.600 | 106 | 15 | 0 | 7,655 ns (folga de 2,345 ns) |

Atende os 100 MHz.


## Potencia (report_power, 20 matrizes por cenario)

Fluxo de ../potencia_versoes.py (Vivado 2026.1, nesta maquina, fila
../fila_potencia.log, terminou em 2026-10-30, 22:04): netlist roteada
simulada no xsim com SAIF, inversa da netlist igual a do C, SAIF corrigido.
Tabela em potencia/potencia.csv.

| Cenario | Total (W) | Dinamica (W) | Ciclos medios na simulacao | Energia por inversao (uJ) |
|---|---|---|---|---|
| TDLA30-5 | 2,450 | 0,233 | 7.595 | 17,7 |
| TDLA30-75 | 2,450 | 0,233 | 7.595 | 17,7 |
| TDLA30-300 | 2,449 | 0,233 | 7.595 | 17,7 |
| TDLC300-100 | 2,449 | 0,233 | 7.595 | 17,7 |
| TDLB100-400 | 2,449 | 0,233 | 7.595 | 17,7 |

- Energia por inversao = potencia dinamica x intervalo em regime (7.594
  ciclos, da co-simulacao) x 10 ns.
- Ciclos medios na simulacao = duracao da simulacao / 20 matrizes. Aqui fica
  igual ao intervalo, porque as inversoes nao se sobrepoem.
- Esta simulacao gravou o SAIF com o metodo antigo (get_objects -r). Na
  4545, o metodo antigo e o novo deram a mesma potencia.

## Servidor, todos os formatos (Vivado 2023.2)

Vivado e potencia no servidor da UFRGS (cadmicro-el8-03 e -04), com o
../pacote_servidor_formatos/ (versoes <formato>_9090). Potencia so no cenario do alvo
desta arquitetura, TDLA30-5. Estes sao os numeros do TCC; os daqui (Vivado
2026.1) ficam so para comparacao. Copiado da secao "Resultados no servidor
(Vivado 2023.2)" de ../pacote_servidor_formatos/LEIAME.md, que tem o metodo
de cada coluna. Relatorios em ../resultados_servidor/formatos/versoes/.

| Formato | LUT | FF | DSP | BRAM_18K | Caminho critico | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|
| <24,12> RND_ZERO/WRAP | 35.604 | 35.600 | 106 | 15 | 7,452 ns | 0,234 | 2,450 | 7.594 | 17,8 |
| <22,12> RND_ZERO/WRAP | 28.296 | 28.748 | 99 | 15 | 7,625 ns | 0,194 | 2,409 | 7.345 | 14,2 |
| <28,14> RND_ZERO/WRAP | 47.449 | 47.927 | 128 | 15 | 7,757 ns | 0,305 | 2,522 | 8.087 | 24,7 |
| <26,12> RND_ZERO/WRAP | 42.897 | 42.872 | 126 | 15 | 7,759 ns | 0,280 | 2,497 | 7.842 | 22,0 |
| <30,14> TRN/SAT | 57.285 | 56.508 | 220 | 15 | 9,033 ns | 0,377 | 2,595 | 8.627 | 32,5 |

- Todos fecham os 100 MHz. Inversa da netlist igual a do C em todos.
- Intervalo: do log da simulacao da netlist no servidor (xsim_<cenario>.log).
- Energia por inversao = dinamica x intervalo x 10 ns.
