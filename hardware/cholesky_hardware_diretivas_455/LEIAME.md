# cholesky_hardware_diretivas_455

VERSAO SALVA em 2026-10-30: alteracao 1 (lote de 16 matrizes em 8 vias).
Intervalo de 402 ciclos por matriz (6.437 por lote), deduzido da
co-simulacao (<24,12> RND_ZERO/WRAP, 16 x 16), inversa igual ao original bit
a bit. Atende o TDLC300-100 (455 ciclos). Nao editar os fontes desta pasta.

Copia de ../cholesky_hardware_diretivas_606/ (versao salva em 2026-10-30,
opcao B: lote de 12 matrizes em 6 vias, 504 ciclos por matriz) para testar
mudancas que levem ao TDLC300-100: 455 ciclos por matriz (T_c / N_PRB a
100 MHz).

Historico: as alteracoes 1 a 6 estao no LEIAME.md de
../cholesky_hardware_diretivas/, as alteracoes 0 e 1 (servidor chamando o
topo e dataflow) no de ../cholesky_hardware_diretivas_4545/, e a opcao B no de
../cholesky_hardware_diretivas_606/. Aqui ficam so as alteracoes novas.

- Fontes do hardware: os mesmos da versao salva. O topo cholesky_inverse
  recebe um lote de CHOL_LOTE matrizes (padrao 12), processadas em CHOL_VIAS
  vias (padrao 6); os dois sao parametros em cholesky.h.
- comparar_com_original.py: confere que a inversa do topo e igual, bit a bit,
  a do codigo original (../cholesky_hardware_servidor/build/), nos tres
  formatos escolhidos, 16 x 16 e 32 x 32. O tb_servidor.cpp desta pasta poe
  cada matriz numa posicao diferente do lote.

      taskset -c 4-7 ../../software/simulador/.venv/bin/python comparar_com_original.py --por-tamanho 1000

- sintese/rodar.sh: sintese C, <24,12> RND_ZERO/WRAP, 16 x 16, nucleos 4 a 7
  (cerca de 3,5 min).
- cosim/rodar.sh: sintese C + co-simulacao com lotes montados com as 20
  matrizes do TDLA30-5 da referencia (pelo menos 3 lotes; cerca de 5 min).
  Conferir depois que a saida do RTL e igual a do C:

      cmp cosim/w/hls/sim/tv/cdatafile/c.cholesky_inverse.autotvout_inverse.dat \
          cosim/w/hls/sim/tv/rtldatafile/rtl.cholesky_inverse.autotvout_inverse.dat

  Com poucos lotes, o "Interval" do relatorio e o da etapa de leitura. O
  intervalo da etapa mais lenta sai do crescimento da latencia entre lotes
  (ver o LEIAME.md da versao 606).

## Ponto de partida

| | Referencia | Versao 9090 | Versao 4545 | Versao 606 | Meta TDLC300-100 |
|---|---|---|---|---|---|
| Intervalo por matriz (co-simulacao) | 32.463 | 7.594 | 3.020 | 504 | 455 |
| DSP (estimativa HLS) | 94 | 106 | 106 | 380 (6%) | |
| LUT (estimativa HLS) | 12.079 | 36.995 | 36.962 | 57.020 (6%) | |
| FF (estimativa HLS) | 5.454 | 37.932 | 37.958 | 48.676 (2%) | |
| BRAM (estimativa HLS) | 11 | 11 | 19 | 240 (8%) | |

# Alteracoes em relacao a versao salva

## 1. Lote de 16 matrizes em 8 vias (2026-10-30)

Arquivo: cholesky.h. So os padroes mudaram: `CHOL_LOTE` de 12 para 16 e
`CHOL_VIAS` de 6 para 8. Nenhuma linha de cholesky_top.cpp mudou.

Motivo: pela conta da versao 606, a etapa mais lenta gastava por matriz
cerca de 227 ciclos nas multiplicacoes (1.360 / 6 vias), 120 nas divisoes (uma
por ciclo), cerca de 100 enchendo o divisor (15 colunas x cerca de 80 ciclos /
12 matrizes) e cerca de 50 em copias e outros lacos. Mais vias reduzem as
multiplicacoes e as copias; um lote maior divide o enchimento do divisor por
mais matrizes. Estimativa: cerca de 400 ciclos por matriz.

Conferencia de bits (servidor com o lote rotativo, todas as matrizes da
selecao): igual nos 6 casos (336/336 e 218/218; 1 falha nos dois em <22,12>
16 x 16, a mesma de antes).

Sintese C, <24,12> RND_ZERO/WRAP, 16 x 16. Todos os lacos com diretiva em
II = 1.

| Etapa | Ciclos estimados por lote (pior caso) | DSP |
|---|---|---|
| lote_ler | 4.096 | 0 |
| lote_lu | 12.662 | 152 |
| lote_g | 1.192 | 16 |
| lote_fs | 13.908 | 160 |
| lote_inv | 3.037 | 128 |
| lote_gravar | 4.096 | 0 |

| | Versao 606 (12 x 6) | Lote 16, 8 vias |
|---|---|---|
| DSP | 380 (6%) | 456 (7%) |
| LUT | 57.020 (6%) | 61.050 (7%) |
| FF | 48.676 (2%) | 47.003 (2%) |
| BRAM | 240 (8%) | 320 (11%) |

Co-simulacao (3 lotes de 16 com as matrizes do TDLA30-5):

| | Valor |
|---|---|
| Latencia por lote | 24.172, 26.513 (media) e 28.854 ciclos |
| Intervalo de entrada medido | 4.096 ciclos por lote (etapa de leitura) |
| Tempo total dos 3 lotes | 37.046 ciclos |
| Status | Pass; saida do RTL igual a do C, byte a byte |

A latencia cresce 2.341 ciclos por lote, entao a etapa mais lenta leva
4.096 + 2.341 = 6.437 ciclos por lote; confere com o total
(24.172 + 2 x 6.437 = 37.046). Por matriz: 6.437 / 16 = 402 ciclos.

| | Referencia | 9090 | 4545 | 606 | 455 |
|---|---|---|---|---|---|
| Intervalo por matriz (ciclos) | 32.463 | 7.594 | 3.020 | 504 | 402 |

- 402 ciclos por matriz (4,02 us a 100 MHz) atende o TDLC300-100 (455), com
  cerca de 12% de folga. Nao atende o TDLA30-300 (152).
- O sistema precisa juntar 16 matrizes por lote. A latencia de um lote e de
  cerca de 24.000 ciclos (240 us).

## Vivado (implementacao, 100 MHz)

Rodado nesta maquina em 2026-10-30 (fila ../fila_vivado.txt, Vivado 2026.1,
fluxo gerado pelo HLS). Valores depois do roteamento
(vivado/w/hls/impl/verilog/project.runs/impl_1/):

| LUT | FF | DSP | BRAM (BRAM_18K) | URAM | Caminho critico |
|---|---|---|---|---|---|
| 55.448 | 44.110 | 456 | 240 | 0 | 9,169 ns (folga de 0,831 ns) |

Atende os 100 MHz.


## Potencia (report_power, 48 matrizes por cenario)

Fluxo de ../potencia_versoes.py (Vivado 2026.1, nesta maquina, fila
../fila_potencia.log, de 2026-10-31 01:23 a 04:24). O testbench inverte
lotes inteiros, entao sao 48 matrizes por cenario (3 lotes de 16). Inversa
da netlist igual a do C em todos. Tabela em potencia/potencia.csv.

| Cenario | Total (W) | Dinamica (W) | Ciclos medios na simulacao | Energia por inversao (uJ) |
|---|---|---|---|---|
| TDLA30-5 | 2,899 | 0,674 | 772 | 2,71 |
| TDLA30-75 | 2,897 | 0,672 | 772 | 2,70 |
| TDLA30-300 | 2,896 | 0,672 | 772 | 2,70 |
| TDLC300-100 | 2,893 | 0,669 | 772 | 2,69 |
| TDLB100-400 | 2,896 | 0,672 | 772 | 2,70 |

- Energia por inversao = potencia dinamica x intervalo em regime (402 ciclos
  por matriz, da co-simulacao) x 10 ns. O potencia.csv usa os ciclos medios
  (5,20 uJ no TDLA30-5).
- Ciclos medios na simulacao = duracao da simulacao / 48 matrizes. Inclui a
  latencia do primeiro lote, entao fica acima do intervalo; nao quer dizer
  que a meta de 455 nao foi atingida.
- SAIF gravado escopo por escopo. Redes casadas: 184.593 de 184.625 em todos
  (o relatorio arredonda para 100%). As 32 que faltam nao foram investigadas.

## Servidor, todos os formatos (Vivado 2023.2)

Vivado e potencia no servidor da UFRGS (cadmicro-el8-03 e -04), com o
../pacote_servidor_formatos/ (versoes <formato>_455). Potencia so no cenario do alvo
desta arquitetura, TDLC300-100. Estes sao os numeros do TCC; os daqui (Vivado
2026.1) ficam so para comparacao. Copiado da secao "Resultados no servidor
(Vivado 2023.2)" de ../pacote_servidor_formatos/LEIAME.md, que tem o metodo
de cada coluna. Relatorios em ../resultados_servidor/formatos/versoes/.

| Formato | LUT | FF | DSP | BRAM_18K | Caminho critico | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|
| <24,12> RND_ZERO/WRAP | 55.482 | 44.110 | 456 | 240 | 8,948 ns | 0,666 | 2,891 | 402 | 2,68 |
| <22,12> RND_ZERO/WRAP | 43.487 | 36.344 | 456 | 240 | 9,371 ns | 0,573 | 2,797 | 395 | 2,26 |
| <28,14> RND_ZERO/WRAP | 68.616 | 57.333 | 576 | 240 | 7,790 ns | 0,805 | 3,032 | 414 | 3,33 |
| <26,12> RND_ZERO/WRAP | 63.231 | 53.101 | 560 | 240 | 8,692 ns | 0,759 | 2,986 | 410 | 3,11 |
| <30,14> TRN/SAT | 84.536 | 69.741 | 1.004 | 240 | 9,258 ns | 1,037 | 3,268 | 421 | 4,37 |

- Todos fecham os 100 MHz. Inversa da netlist igual a do C em todos.
- Intervalo: do log da simulacao da netlist no servidor (xsim_<cenario>.log).
- Energia por inversao = dinamica x intervalo x 10 ns.
