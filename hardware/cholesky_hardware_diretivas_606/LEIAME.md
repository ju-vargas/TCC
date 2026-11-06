# cholesky_hardware_diretivas_606

VERSAO SALVA em 2026-10-30: alteracao 1 (opcao B, lote de 12 matrizes em 6
vias). Intervalo de 504 ciclos por matriz (6.047 por lote), deduzido da
co-simulacao (<24,12> RND_ZERO/WRAP, 16 x 16), inversa igual ao original bit
a bit. Atende o TDLA30-75 (606 ciclos).
Nao editar os fontes desta pasta; os testes seguintes ficam em
../cholesky_hardware_diretivas_455/.

Copia de ../cholesky_hardware_diretivas_4545/ (versao salva em 2026-10-30,
intervalo de 3.020 ciclos) para testar mudancas que levem ao TDLA30-75: 606
ciclos entre inversoes (T_c / N_PRB a 100 MHz).

Historico: as alteracoes 1 a 6 estao no LEIAME.md de
../cholesky_hardware_diretivas/, e as alteracoes 0 e 1 (servidor chamando o
topo e dataflow) no de ../cholesky_hardware_diretivas_4545/. Aqui ficam so as
alteracoes novas.

- Fontes do hardware: os mesmos da versao salva (com dataflow).
- comparar_com_original.py: confere que a inversa do topo cholesky_inverse e
  igual, bit a bit, a do codigo original (../cholesky_hardware_servidor/build/),
  nos tres formatos escolhidos, 16 x 16 e 32 x 32. O tb_servidor.cpp desta
  pasta chama o topo.

      taskset -c 4-7 ../../software/simulador/.venv/bin/python comparar_com_original.py --por-tamanho 1000

- sintese/rodar.sh: sintese C, <24,12> RND_ZERO/WRAP, 16 x 16, nucleos 4 a 7.
- cosim/rodar.sh: sintese C + co-simulacao com as 20 matrizes do TDLA30-5 da
  referencia. Conferir depois que a saida do RTL e igual a do C:

      cmp cosim/w/hls/sim/tv/cdatafile/c.cholesky_inverse.autotvout_inverse.dat \
          cosim/w/hls/sim/tv/rtldatafile/rtl.cholesky_inverse.autotvout_inverse.dat

## Ponto de partida

| | Referencia | Versao 9090 | Versao 4545 | Meta TDLA30-75 |
|---|---|---|---|---|
| Intervalo entre inversoes (co-simulacao) | 32.463 | 7.594 | 3.020 | 606 |
| Latencia de uma inversao (co-simulacao) | 32.463 | 7.593 | 7.904 | |
| DSP (estimativa HLS) | 94 | 106 | 106 | |
| LUT (estimativa HLS) | 12.079 | 36.995 | 36.962 | |
| FF (estimativa HLS) | 5.454 | 37.932 | 37.958 | |
| BRAM (estimativa HLS) | 11 | 11 | 19 | |

# Alteracoes em relacao a versao salva

## 1. Opcao B: lote de matrizes intercaladas (2026-10-30)

Motivo: para 606 ciclos, diretiva sozinha nao basta.
- A LU tem 15 colunas em sequencia, cada uma esperando pelo menos uma divisao
  de 78 ciclos: cerca de 1.200 ciclos para uma matriz, mesmo com recursos
  infinitos. Na substituicao direta, cerca de 1.250. Entao cada etapa precisa
  trabalhar em varias matrizes ao mesmo tempo.
- Em 606 ciclos, a LU precisa de pelo menos 3 multiplicadores complexos, a
  substituicao direta de 2 e a inversao de 3. Antes cada etapa tinha 1.

O que mudou:
- cholesky.h: o topo cholesky_inverse recebe um lote de LOTE matrizes,
  `A_matrix[LOTE][MATRIX_DIM][MATRIX_DIM]` e `inverse[LOTE][...][...]`.
  Novos parametros CHOL_LOTE (padrao 12) e CHOL_VIAS (padrao 6).
- cholesky_top.cpp: reescrito. Seis etapas em dataflow: lote_ler, lote_lu,
  lote_g, lote_fs, lote_inv e lote_gravar. As funcoes originais
  (LU_decomposition etc.) nao mudaram e continuam usadas por
  cholesky_decomposition.
- Dentro de cada etapa:
  - as divisoes alternam entre as 12 matrizes do lote, uma por ciclo. O
    divisor com pipeline nao espera o resultado anterior, e continua um so
    divisor por etapa;
  - as multiplicacoes rodam em 6 vias: 6 matrizes por ciclo, cada uma no seu
    banco de memoria (`array_partition cyclic factor=VIAS dim=1` no indice da
    matriz). A matriz m fica no banco m % 6; a via p trata as matrizes
    g * 6 + p;
  - as somas da substituicao direta e da inversao usam um laco so (como a
    alteracao 5 da versao 9090), com um acumulador por via.
- lote_ler e lote_gravar copiam entre as portas (um elemento por ciclo, como
  antes) e os bancos. A interface continua com uma porta de entrada e uma de
  saida.
- D nao e mais uma matriz dentro do topo: D_extraction so copiava a diagonal
  de U, e a raiz agora le direto essa diagonal (o mesmo valor). Os zeramentos
  de L, G e G_inv continuam.
- Testbenches desta pasta:
  - tb_servidor.cpp: a matriz pedida vai para uma posicao do lote que roda a
    cada pedido; as outras posicoes guardam matrizes anteriores, diferentes.
    Assim a conferencia acusa se uma via misturar dados de outra matriz. No
    primeiro pedido, todas as posicoes recebem a mesma matriz.
  - tb_potencia.cpp: monta lotes com as matrizes da lista (voltando ao inicio
    quando ela acaba), pelo menos 3 lotes.
  - tb_lu_decomposition.cpp: o lote recebe 12 copias da mesma matriz.

Por que o resultado nao muda: para cada matriz, as contas sao as mesmas das
funcoes originais, na mesma ordem: as divisoes de uma coluna antes da
atualizacao, a atualizacao de cada elemento na ordem das colunas, cada soma
com k em ordem crescente e no seu proprio acumulador. Mudam so a ordem entre
matrizes diferentes e o banco de memoria de cada uma.

Conferencia de bits (servidor com o lote rotativo, todas as matrizes da
selecao): igual nos 6 casos (336/336 e 218/218; 1 falha nos dois em <22,12>
16 x 16, a mesma de antes).

Teste negativo: fazer a inversao ler G_inv da matriz vizinha
(`G_inv[(m + 1) % LOTE]`) deu "diferente" em 19 de 20 matrizes nos dois
tamanhos (a unica igual e o primeiro pedido, com o lote todo igual). Depois o
arquivo voltou ao normal.

Sintese C, <24,12> RND_ZERO/WRAP, 16 x 16, LOTE = 12, VIAS = 6. Dataflow com
6 processos; todos os lacos com diretiva em II = 1. Levou cerca de 3,5 min.

| Etapa | Ciclos estimados por lote (pior caso) | DSP |
|---|---|---|
| lote_ler | 3.072 | 0 |
| lote_lu | 11.852 | 120 |
| lote_g | 1.192 | 12 |
| lote_fs | 12.932 | 152 |
| lote_inv | 3.029 | 96 |
| lote_gravar | 3.072 | 0 |

| | Versao 4545 | Opcao B |
|---|---|---|
| DSP | 106 (1%) | 380 (6%) |
| LUT | 36.962 (4%) | 57.020 (6%) |
| FF | 37.958 (2%) | 48.676 (2%) |
| BRAM | 19 (~0%) | 240 (8%) |

As BRAM vem dos bancos: cada array de 12 matrizes partido em 6 bancos, e os
canais entre etapas em ping-pong (dobro de memoria).

Co-simulacao (cosim/rodar.sh, 3 lotes de 12 com as matrizes do TDLA30-5;
cerca de 5 min):

| | Valor |
|---|---|
| Latencia por lote | 21.242, 24.217 (media) e 27.192 ciclos |
| Intervalo de entrada medido | 3.072 ciclos por lote |
| Tempo total dos 3 lotes | 33.336 ciclos |
| Status | Pass; saida do RTL igual a do C, byte a byte |

Como ler: o intervalo de 3.072 do relatorio e o da etapa de leitura, que
aceita um lote novo a cada 3.072 ciclos enquanto os buffers tem espaco. A
latencia cresce 2.975 ciclos a cada lote, porque a etapa mais lenta e mais
demorada que a leitura. O intervalo da etapa mais lenta e entao
3.072 + 2.975 = 6.047 ciclos por lote, e confere com o tempo total:
21.242 + 2 x 6.047 = 33.336. Por matriz: 6.047 / 12 = 504 ciclos.

| | Referencia | Versao 9090 | Versao 4545 | Opcao B |
|---|---|---|---|---|
| Intervalo por matriz (ciclos) | 32.463 | 7.594 | 3.020 | 504 |

- 504 ciclos por matriz (5,04 us a 100 MHz) atende o TDLA30-75 (606), com
  cerca de 17% de folga. Nao atende o TDLC300-100 (455).
- O valor de 504 foi tirado da latencia e do tempo total da co-simulacao, com
  3 lotes. Uma co-simulacao com mais lotes mediria o intervalo direto, no
  regime permanente.
- A latencia de um lote e de cerca de 21.000 ciclos (210 us). Para a meta isso
  nao importa, mas o sistema precisa juntar 12 matrizes antes de mandar o
  lote.

## Vivado (implementacao, 100 MHz)

Rodado nesta maquina em 2026-10-30 (fila ../fila_vivado.txt, Vivado 2026.1,
fluxo gerado pelo HLS). Valores depois do roteamento
(vivado/w/hls/impl/verilog/project.runs/impl_1/):

| LUT | FF | DSP | BRAM (BRAM_18K) | URAM | Caminho critico |
|---|---|---|---|---|---|
| 51.084 | 43.443 | 379 | 180 | 0 | 8,867 ns (folga de 1,133 ns) |

Atende os 100 MHz.


## Potencia (report_power, 36 matrizes por cenario)

Fluxo de ../potencia_versoes.py (Vivado 2026.1, nesta maquina, fila
../fila_potencia.log, de 2026-10-30 22:04 a 2026-10-31 01:23). O testbench
inverte lotes inteiros, entao sao 36 matrizes por cenario (3 lotes de 12).
Inversa da netlist igual a do C em todos. Tabela em potencia/potencia.csv.

| Cenario | Total (W) | Dinamica (W) | Ciclos medios na simulacao | Energia por inversao (uJ) |
|---|---|---|---|---|
| TDLA30-5 | 2,775 | 0,553 | 927 | 2,79 |
| TDLA30-75 | 2,775 | 0,553 | 927 | 2,79 |
| TDLA30-300 | 2,774 | 0,551 | 927 | 2,78 |
| TDLC300-100 | 2,773 | 0,550 | 927 | 2,77 |
| TDLB100-400 | 2,775 | 0,553 | 927 | 2,79 |

- Energia por inversao = potencia dinamica x intervalo em regime (504 ciclos
  por matriz, da co-simulacao) x 10 ns. O potencia.csv usa os ciclos medios
  (5,13 uJ no TDLA30-5).
- Ciclos medios na simulacao = duracao da simulacao / 36 matrizes. Inclui a
  latencia do primeiro lote, entao fica bem acima do intervalo. Nao quer dizer
  que a meta de 606 nao foi atingida: com as matrizes chegando sem parar, vale
  o intervalo.
- SAIF gravado escopo por escopo. Redes casadas: 169.162 de 169.186 em todos
  (o relatorio arredonda para 100%). As 24 que faltam nao foram investigadas.

## Servidor, todos os formatos (Vivado 2023.2)

Vivado e potencia no servidor da UFRGS (cadmicro-el8-03 e -04), com o
../pacote_servidor_formatos/ (versoes <formato>_606). Potencia so no cenario do alvo
desta arquitetura, TDLA30-75. Estes sao os numeros do TCC; os daqui (Vivado
2026.1) ficam so para comparacao. Copiado da secao "Resultados no servidor
(Vivado 2023.2)" de ../pacote_servidor_formatos/LEIAME.md, que tem o metodo
de cada coluna. Relatorios em ../resultados_servidor/formatos/versoes/.

| Formato | LUT | FF | DSP | BRAM_18K | Caminho critico | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|
| <24,12> RND_ZERO/WRAP | 51.087 | 43.450 | 379 | 180 | 8,404 ns | 0,546 | 2,768 | 504 | 2,75 |
| <22,12> RND_ZERO/WRAP | 40.337 | 35.826 | 377 | 180 | 8,814 ns | 0,474 | 2,695 | 494 | 2,34 |
| <28,14> RND_ZERO/WRAP | 63.997 | 56.982 | 471 | 180 | 7,867 ns | 0,647 | 2,872 | 519 | 3,36 |
| <26,12> RND_ZERO/WRAP | 59.133 | 52.228 | 459 | 180 | 8,526 ns | 0,618 | 2,842 | 514 | 3,18 |
| <30,14> TRN/SAT | 78.510 | 68.929 | 803 | 180 | 8,700 ns | 0,868 | 3,096 | 529 | 4,59 |

- Todos fecham os 100 MHz. Inversa da netlist igual a do C em todos.
- Intervalo: do log da simulacao da netlist no servidor (xsim_<cenario>.log).
- Energia por inversao = dinamica x intervalo x 10 ns.
