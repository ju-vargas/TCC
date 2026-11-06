# cholesky_hardware_diretivas_152_sistolico

VERSAO SALVA em 2026-10-30: arranjo sistolico linear, lote de 32 matrizes
em 2 vias. Intervalo de 128 ciclos por matriz (4.097 por lote) na
co-simulacao (<24,12> RND_ZERO/WRAP, 16 x 16), inversa igual ao original bit
a bit. Atende o TDLA30-300 (152 ciclos). Nao editar os fontes desta pasta.

Copia de ../cholesky_hardware_diretivas_455/ (versao salva: lote de 16
matrizes em 8 vias, 402 ciclos por matriz). O historico das alteracoes
anteriores esta nos LEIAME.md das pastas 9090 (cholesky_hardware_diretivas),
4545, 606 e 455. Aqui ficam so as alteracoes novas.

- Fontes do hardware: so cholesky.h e cholesky_top.cpp mudaram. Os outros
  fontes (lu_decomposition.cpp etc.) sao os da versao 455, usados so pelo
  cholesky_decomposition do testbench.
- comparar_com_original.py: confere que a inversa do topo e igual, bit a bit,
  a do codigo original (../cholesky_hardware_servidor/build/), nos tres
  formatos escolhidos, 16 x 16 e 32 x 32.

      taskset -c 4-5 ../../software/simulador/.venv/bin/python comparar_com_original.py --por-tamanho 1000 -j 2

- sintese/rodar.sh: sintese C, <24,12> RND_ZERO/WRAP, 16 x 16, nucleos 4 e 5.
- cosim/rodar.sh: sintese C + co-simulacao com lotes montados com as 20
  matrizes do TDLA30-5 da referencia (pelo menos 3 lotes). Conferir depois que
  a saida do RTL e igual a do C:

      cd cosim/w/hls/sim/tv
      for v in 0 1; do cmp cdatafile/c.cholesky_inverse.autotvout_inverse_$v.dat \
                           rtldatafile/rtl.cholesky_inverse.autotvout_inverse_$v.dat; done

  Com as portas partidas, a saida fica em um arquivo por porta (inverse_0,
  inverse_1).
- vivado/rodar.sh: sintese HLS + implementacao no Vivado, nucleos 6 e 7 (na
  fila de ../fila_vivado.txt).

# Alteracoes em relacao a versao 455

## 1. Arranjo sistolico linear nas etapas (2026-10-30)

Arquivos: cholesky.h (parametros) e cholesky_top.cpp (todas as etapas).

### Ideia

Na versao 455, cada laco de soma (k) roda um termo por ciclo, e as vias sao
matrizes diferentes. Aqui o laco de k vira MATRIX_DIM celulas lado a lado,
uma por k (o arranjo sistolico implicito do livro, cap. 10: um laco de
tamanho fixo, desenrolado, com guarda). A soma parcial passa de uma celula
para a seguinte em ordem de k, e a celula fora da faixa de k so repassa a
soma. Entao a ordem das somas e os tipos sao os mesmos do original.

| Etapa | Uma iteracao (um ciclo, por via) faz | Iteracoes por matriz |
|---|---|---|
| lote_lu | uma linha da LU numa coluna: a divisao L[line][c] e a atualizacao da linha inteira (16 celulas) | 120 |
| lote_g | uma raiz, depois uma linha inteira de G (16 celulas) | 16 + 16 |
| lote_fs | um G_inv[line][c]: a soma inteira (16 celulas) e a divisao | 136 |
| lote_inv | um inverse[line][column]: a soma inteira (16 celulas) | 256 |
| lote_ler, lote_gravar | um elemento por porta | 256 |

Cada via tem o seu divisor, as suas celulas e a sua porta. Com VIAS vias, o
tempo por matriz de cada etapa e a coluna da direita dividida por VIAS.

### Mudancas

1. cholesky.h: `CHOL_LOTE` 32, `CHOL_VIAS` 2, e dois parametros novos,
   `CHOL_PROF_LU` e `CHOL_PROF_FS` (ver o item 4).
2. Portas: `array_partition cyclic factor=VIAS dim=1` nos argumentos
   A_matrix e inverse do topo. Cada via ganha uma porta de entrada e uma de
   saida (a matriz m vai pela porta m % VIAS). O prototipo em C nao mudou,
   entao os testbenches sao os mesmos. SUPOSICAO DO SISTEMA (sem fonte): o
   resto do sistema entrega e recebe VIAS elementos por ciclo. Com uma porta
   so, ler 256 elementos por matriz ja passa de 152 ciclos.
3. Bancos: alem do banco por matriz (cyclic VIAS no indice da matriz), as
   linhas (L, G, A) ou colunas (G_inv) ficam em MATRIX_DIM bancos
   (`complete` na dimensao de k), para as 16 celulas lerem no mesmo ciclo.
   Na LU, U fica em duas copias iguais (Ua e Ub): cada iteracao le a linha,
   le a linha do pivo e grava a linha, e cada banco so tem duas portas.
4. Dependencia entre passos. A coluna c da LU le as linhas gravadas na coluna
   c - 1, e a linha i da substituicao le as linhas < i. As matrizes do lote
   alternam a cada ciclo, entao a mesma matriz volta depois de um passo
   inteiro. Os passos curtos (fim da LU, comeco da substituicao) ganham ciclos
   vazios ate `CHOL_PROF_*` ciclos, e o pragma `dependence ... dependent=false`
   diz ao HLS que nao ha dependencia entre iteracoes proximas. Isso so esta
   certo se a profundidade do pipeline for no maximo `CHOL_PROF_*`; se nao
   for, o RTL le um valor velho e a co-simulacao acusa (o cmp falha).
5. Zeramentos que mudaram (nao afetam a inversa):
   - L acima da diagonal nao e mais zerada, e a diagonal 1 de L nao e
     gravada: lote_g usa a constante (1, 0), o mesmo valor, na mesma conta.
     G acima da diagonal continua zero.
   - G_inv acima da diagonal nao e mais zerada. A inversao so le G_inv[k][i]
     com k >= i (diagonal e abaixo). Zerar custaria 16 ciclos por matriz.
   - U nao e mais copiada de A antes da LU: na coluna 0 as linhas vem direto
     de A. A diagonal de U (Ud) e gravada assim que fica pronta (a linha
     c + 1 nao muda depois da coluna c).

### Conferencia

- comparar_com_original.py --por-tamanho 1000: os 6 casos iguais
  (336/336 em 16 x 16 e 218/218 em 32 x 32, nos tres formatos).
- Teste negativo: com a guarda da substituicao trocada (`k > c` em vez de
  `k >= c`), 0/50 iguais em 16 x 16 e em 32 x 32. Codigo restaurado depois.

### Resultados

Sintese C (estimativa do HLS, 16 x 16, <24,12> RND_ZERO/WRAP, 100 MHz):

| Etapa | Ciclos por lote (32 matrizes) | Por matriz | Profundidade do pipeline | DSP |
|---|---|---|---|---|
| lote_ler | 4.098 | 128 | 2 | 0 |
| lote_lu | 2.433 | 76 | 79 | 560 |
| lote_g | 524 | 16 | 6 e 3 | 60 |
| lote_fs | 2.582 | 81 | 82 | 568 |
| lote_inv | 4.102 | 128 | 6 | 512 |
| lote_gravar | 4.098 | 128 | 2 | 0 |

- A profundidade real (79 na LU, 82 na substituicao) e menor que
  CHOL_PROF_LU = CHOL_PROF_FS = 110, entao os passos esticados estao certos.
- O HLS avisou "Found false inter dependency" para Ua e Ub: e o pragma
  dependence sendo aplicado, como esperado.
- Portas: A_matrix_0, A_matrix_1, inverse_0 e inverse_1 (o log mostra
  "Applying array_partition to 'A_matrix': Cyclic partitioning with factor 2").
  A tabela de pragmas do relatorio diz "Not implemented" para esse pragma,
  mas as portas sairam partidas.
- O arranjo existe de fato: 512 DSP na inversao = 2 vias x 16 celulas x 16
  DSP por multiplicacao complexa (na 455 eram 128 DSP para 8 vias de uma
  celula).

| | Versao 455 | Esta versao |
|---|---|---|
| DSP | 456 (7%) | 1.700 (28%) |
| LUT | 61.050 (7%) | 152.143 (17%) |
| FF | 47.003 (2%) | 121.716 (6%) |
| BRAM | 320 (11%) | 756 (28%) |

Co-simulacao (cosim/rodar.sh, 3 lotes de 32 com as matrizes do TDLA30-5):

| Latencia por lote (min / med / max) | 17.828 / 17.828 / 17.829 |
|---|---|
| Tempo total (3 lotes) | 26.021 |
| Intervalo por lote | (26.021 - 17.828) / 2 = 4.097 |
| Intervalo por matriz | 4.097 / 32 = 128 |

- Status Pass, e a saida do RTL e igual a do C byte a byte nas duas portas.
  Isso tambem confere que a profundidade suposta (110) e suficiente.
- A latencia nao cresce entre lotes, entao o intervalo e o da etapa mais
  lenta (leitura, inversao e gravacao empatam em cerca de 4.096).
- A latencia de um lote, 17.828 ciclos (178 us), fica abaixo de
  T_c = 152 x 275 = 41.800 ciclos.
- Nesta versao a etapa mais lenta e a das portas e da inversao, e as etapas
  com divisor (LU e substituicao) sobram. A celula da inversao fica ociosa
  em boa parte das iteracoes: das 256 x 16 celulas por matriz, so 1.496 tem
  termo (k >= max(line, column)).
