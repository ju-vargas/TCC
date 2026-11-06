# cholesky_hardware_diretivas_4545

VERSAO SALVA em 2026-10-30: alteracoes 0 e 1 (dataflow). Intervalo de 3.020
ciclos entre inversoes na co-simulacao (<24,12> RND_ZERO/WRAP, 16 x 16),
inversa igual ao original bit a bit. Atende o TDLA30-10 (4.545 ciclos).
Nao editar os fontes desta pasta; os testes seguintes ficam em
../cholesky_hardware_diretivas_606/.

Copia de ../cholesky_hardware_diretivas/ (versao salva em 2026-10-30, 7.593
ciclos por inversao) para testar diretivas que levem ao TDLA30-10: 4.545
ciclos por inversao (T_c / N_PRB a 100 MHz).

As alteracoes 1 a 6 (o que mudou, por que e as conferencias) estao no
LEIAME.md da pasta salva. Aqui ficam so as alteracoes novas.

- Fontes do hardware: os mesmos da versao salva.
- comparar_com_original.py: confere que a inversa e igual, bit a bit, a do
  codigo original (../cholesky_hardware_servidor/build/), nos tres formatos
  escolhidos, 16 x 16 e 32 x 32.

      taskset -c 4-7 ../../software/simulador/.venv/bin/python comparar_com_original.py --por-tamanho 1000

- sintese/rodar.sh: sintese C, <24,12> RND_ZERO/WRAP, 16 x 16, nucleos 4 a 7.
- cosim/rodar.sh: sintese C + co-simulacao com as 20 matrizes do TDLA30-5 da
  referencia. Conferir depois que a saida do RTL e igual a do C:

      cmp cosim/w/hls/sim/tv/cdatafile/c.cholesky_inverse.autotvout_inverse.dat \
          cosim/w/hls/sim/tv/rtldatafile/rtl.cholesky_inverse.autotvout_inverse.dat

## Ponto de partida

| | Referencia | Versao salva | Meta TDLA30-10 |
|---|---|---|---|
| Ciclos por inversao (co-simulacao) | 32.463 | 7.593 | 4.545 |
| DSP (estimativa HLS) | 94 | 106 | |
| LUT (estimativa HLS) | 12.079 | 36.995 | |
| FF (estimativa HLS) | 5.454 | 37.932 | |

# Alteracoes em relacao a versao salva

## 0. Servidor de conferencia chamando o topo (2026-10-30)

Arquivos: tb_servidor.cpp e compilar_servidor.sh (so as copias desta pasta).

Motivo: o servidor original chama cholesky_decomposition, que nao passa pelo
topo cholesky_inverse. O dataflow muda so o topo, entao a conferencia de bits
precisa chamar o topo para valer para o circuito sintetizado.

- tb_servidor.cpp: `cholesky_decomposition(A, L, U, D, S, G, G_inv, inverse);`
  virou `cholesky_inverse(A, inverse);`.
- compilar_servidor.sh: cholesky_top.cpp entrou na lista FONTES.

Antes de qualquer outra mudanca, a conferencia com o topo deu igual nos 6
casos.

## 1. Dataflow entre as etapas (2026-10-30)

Arquivo: cholesky_top.cpp.

Motivo: a meta e o intervalo entre inversoes, nao a latencia. Com dataflow,
cada etapa vira um processo, e etapas diferentes trabalham em matrizes
diferentes ao mesmo tempo. O intervalo passa a ser o da etapa mais lenta, nao a
soma das etapas (Livro, cap. 5 e 7).

Antes (versao salva): as seis funcoes chamadas em sequencia.

```cpp
void cholesky_inverse(A_matrix, inverse) {
    complex_fixed_t L[..], U[..], D[..], S[..], G[..], G_inv[..];

    LU_decomposition(A_matrix, L, U);
    D_extraction(U, D);
    D_square_root(D, S);
    G_decomposition(S, L, G);
    forward_substitution(G, G_inv);
    inversion(G_inv, inverse);
}
```

Agora: quatro etapas, cada uma numa funcao com `inline off`, e
`#pragma HLS dataflow` no topo.

```cpp
static void etapa_lu(A_matrix, L, U) {
#pragma HLS inline off
    complex_fixed_t U_local[MATRIX_DIM][MATRIX_DIM];
    LU_decomposition(A_matrix, L, U_local);
    for (int line = 0; line < MATRIX_DIM; line++){
    #pragma HLS pipeline II=1
        U[line][line] = U_local[line][line];
    }
}

static void etapa_g(U, L, G) {          // D, S e G juntas
#pragma HLS inline off
    complex_fixed_t D[MATRIX_DIM][MATRIX_DIM];
    complex_fixed_t S[MATRIX_DIM];
    D_extraction(U, D);
    D_square_root(D, S);
    G_decomposition(S, L, G);
}

static void etapa_fs(G, G_inv) { inline off; forward_substitution(G, G_inv); }
static void etapa_inv(G_inv, inverse) { inline off; inversion(G_inv, inverse); }

void cholesky_inverse(A_matrix, inverse) {
#pragma HLS dataflow
    complex_fixed_t L[..], U[..], G[..], G_inv[..];
    etapa_lu(A_matrix, L, U);
    etapa_g(U, L, G);
    etapa_fs(G, G_inv);
    etapa_inv(G_inv, inverse);
}
```

Por que assim:
- Dataflow exige um so produtor e um so consumidor por array (Livro, cap. 11).
  L sai da LU e so e lida em G_decomposition, pulando D e S. Juntar D, S e G
  numa etapa resolve isso.
- U local na LU: na primeira tentativa U era o canal entre etapas, e o laco de
  atualizacao da LU (duas leituras e uma escrita de U por ciclo) caiu para
  II = 2, por falta de portas de memoria (aviso HLS 200-885). Com U local, ele
  volta a II = 1. Para a etapa seguinte vai so a diagonal, porque
  D_extraction so le U[line][line]; o resto do canal U nao e escrito nem lido.

Por que o resultado nao muda: as seis funcoes sao as mesmas, chamadas na mesma
ordem, com os mesmos dados. O U local tem os mesmos valores que o U de antes, e
a diagonal copiada e a mesma.

Conferencia de bits (servidor chamando o topo, todas as matrizes da selecao):
igual nos 6 casos (336/336 e 218/218; 1 falha nos dois em <22,12> 16 x 16, a
mesma de antes).

Sintese C, <24,12> RND_ZERO/WRAP, 16 x 16. O dataflow foi aplicado com 4
processos, e todos os lacos com diretiva chegaram a II = 1.

| Etapa | Ciclos estimados (pior caso) |
|---|---|
| etapa_lu | 5.426 |
| etapa_g | 686 |
| etapa_fs | 6.645 |
| etapa_inv | 1.500 |

| | Versao salva | Com dataflow |
|---|---|---|
| DSP | 106 | 106 (1%) |
| LUT | 36.995 | 36.962 (4%) |
| FF | 37.932 | 37.958 (2%) |
| BRAM | 11 | 19 (~0%) |

As 8 BRAM a mais sao dos buffers ping-pong entre as etapas.

Co-simulacao (cosim/rodar.sh, as mesmas 20 matrizes do TDLA30-5, uma atras da
outra):

| | Referencia | Versao salva | Com dataflow |
|---|---|---|---|
| Intervalo entre inversoes | 32.463 | 7.594 | 3.020 |
| Latencia de uma inversao | 32.463 | 7.593 | 7.904 |
| 20 inversoes seguidas | | 151.879 | 65.284 |

- O intervalo de 3.020 ciclos (30,2 us a 100 MHz) atende o TDLA30-10 (4.545),
  com cerca de 34% de folga. E 10,7 vezes menor que a referencia.
- A latencia de uma inversao subiu um pouco (7.593 para 7.904), por causa da
  copia da diagonal e da troca de buffers entre etapas. Para a meta isso nao
  importa: o que conta e o intervalo.
- Os intervalos de todas as 20 inversoes foram iguais (min = medio = max).
- Status: Pass, e a saida do RTL e igual, byte a byte, a do C.
- O intervalo de 3.020 bate com a etapa mais lenta com os trip counts reais
  (a LU e a forward substitution ficam perto de 3.000 cada; estimativa minha).
- Proximo cenario, TDLA30-75: 606 ciclos, cerca de 5 vezes menos que agora.

## Vivado (implementacao, 100 MHz)

Rodado nesta maquina em 2026-10-30 (fila ../fila_vivado.txt, Vivado 2026.1,
fluxo gerado pelo HLS). Valores depois do roteamento
(vivado/w/hls/impl/verilog/project.runs/impl_1/):

| LUT | FF | DSP | BRAM (BRAM_18K) | URAM | Caminho critico |
|---|---|---|---|---|---|
| 35.853 | 35.727 | 106 | 22 | 0 | 7,545 ns (folga de 2,455 ns) |

Atende os 100 MHz.

## Potencia (report_power, 20 matrizes por cenario)

Fluxo de ../potencia_versoes.py: netlist roteada simulada no xsim com SAIF,
inversa da netlist igual a do C, SAIF corrigido (sem o "\ " no fim dos
nomes escapados; 100% das redes casadas). Tabela em potencia/potencia.csv.

| Cenario | Total (W) | Dinamica (W) | Ciclos medios na simulacao | Energia por inversao (uJ) |
|---|---|---|---|---|
| TDLA30-5 | 2,522 | 0,304 | 3.265 | 9,18 |
| TDLA30-75 | 2,522 | 0,305 | 3.265 | 9,21 |
| TDLA30-300 | 2,522 | 0,305 | 3.265 | 9,21 |
| TDLC300-100 | 2,522 | 0,304 | 3.265 | 9,18 |
| TDLB100-400 | 2,521 | 0,304 | 3.265 | 9,18 |

- Energia por inversao = potencia dinamica x intervalo em regime (3.020
  ciclos, da co-simulacao) x 10 ns.
- Ciclos medios na simulacao = duracao da simulacao / 20 matrizes. Inclui a
  latencia da primeira inversao, entao fica acima do intervalo. O
  potencia.csv usa esses ciclos na coluna energia_por_inversao_uj (9,93 uJ
  no TDLA30-5); a tabela acima usa o intervalo, que e o que vale com as
  matrizes chegando sem parar.
- A potencia dinamica e a media da simulacao inteira, com o enchimento do
  pipeline (sem fonte para quanto isso muda; deve ser pouco aqui).

## Servidor, todos os formatos (Vivado 2023.2)

Vivado e potencia no servidor da UFRGS (cadmicro-el8-03 e -04), com o
../pacote_servidor_formatos/ (versoes <formato>_4545). Potencia so no cenario do alvo
desta arquitetura, TDLA30-10. Estes sao os numeros do TCC; os daqui (Vivado
2026.1) ficam so para comparacao. Copiado da secao "Resultados no servidor
(Vivado 2023.2)" de ../pacote_servidor_formatos/LEIAME.md, que tem o metodo
de cada coluna. Relatorios em ../resultados_servidor/formatos/versoes/.

| Formato | LUT | FF | DSP | BRAM_18K | Caminho critico | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|
| <24,12> RND_ZERO/WRAP | 35.940 | 35.730 | 106 | 25 | 7,549 ns | 0,305 | 2,522 | 3.020 | 9,21 |
| <22,12> RND_ZERO/WRAP | 28.540 | 28.904 | 99 | 25 | 7,658 ns | 0,253 | 2,469 | 2.900 | 7,34 |
| <28,14> RND_ZERO/WRAP | 47.727 | 48.105 | 128 | 22 | 7,626 ns | 0,391 | 2,610 | 3.200 | 12,5 |
| <26,12> RND_ZERO/WRAP | 43.181 | 43.042 | 126 | 22 | 8,273 ns | 0,362 | 2,580 | 3.140 | 11,4 |
| <30,14> TRN/SAT | 56.852 | 56.671 | 220 | 25 | 8,106 ns | 0,496 | 2,717 | 3.320 | 16,5 |

- Todos fecham os 100 MHz. Inversa da netlist igual a do C em todos.
- Intervalo: do log da simulacao da netlist no servidor (xsim_<cenario>.log).
- Energia por inversao = dinamica x intervalo x 10 ns.
