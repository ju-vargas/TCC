# pacote_servidor_formatos

Pacote para rodar o Vivado e a potencia de todas as arquiteturas, nos 5
formatos, no servidor (Vivado 2023.2). Montado a partir de 2026-10-31 por
../montar_pacote_formatos.py. Mesmo fluxo do ../pacote_servidor_2023/ (ver o
LEIAME.md dele): o HLS 2026.1 roda aqui, e o servidor roda so o Vivado e o
xsim.

## O que entra

Formatos (16 x 16):

| Formato | Modo |
|---|---|
| <24,12> | RND_ZERO/WRAP (estudo principal, primeiro na fila) |
| <22,12> | RND_ZERO/WRAP |
| <28,14> | RND_ZERO/WRAP |
| <26,12> | RND_ZERO/WRAP |
| <30,14> | TRN/SAT |

Arquiteturas, com o cenario da potencia:

| Arquitetura | Pasta | Cenario |
|---|---|---|
| sem_otimizacao | ../cholesky_hardware (sem diretivas de ciclo) | os 5 |
| 9090 | ../cholesky_hardware_diretivas | TDLA30-5 |
| 4545 | ../cholesky_hardware_diretivas_4545 | TDLA30-10 (matrizes do TDLA30-5) |
| 606 | ../cholesky_hardware_diretivas_606 | TDLA30-75 |
| 152_sistolico | ../cholesky_hardware_diretivas_152_sistolico | TDLA30-300 |
| 455 | ../cholesky_hardware_diretivas_455 | TDLC300-100 |
| 114_sistolico | ../cholesky_hardware_diretivas_114_sistolico | TDLB100-400 |

- O TDLA30-10 usa as mesmas matrizes do TDLA30-5: mesmo N (192) e mesma
  portadora (3,5 GHz) (../testes/AMOSTRAGEM.md, tabela das pastas).
- Por ultimo, a versao sem otimizacao em 32 x 32, nos 5 formatos.
- <24,12> 152_sistolico e 114_sistolico ficam de fora: ja rodaram com o
  ../pacote_servidor_2023/.
- Nome de cada versao: <formato>_<arquitetura>[_32x32], em versoes/.
  fila.txt tem a ordem.

Antes de entrar no pacote, cada versao passa por:
1. Sintese C. Se a estimativa do HLS passar de 5.952 DSP ou de 90% dos
   871.680 LUT da XCU50, fica de fora (viabilidade.csv, "nao cabe"). O DSP
   do HLS bateu com o do Vivado nas 6 arquiteturas em <24,12>; no LUT, o
   Vivado deu ate 7,8% acima (LEIAME do pacote_servidor_2023).
2. RTL igual ao de uma sintese ja feita com os mesmos fontes e o mesmo
   syn.cflags, quando existe (<24,12> e a versao sem otimizacao em <22,12>,
   <24,12> e <28,14>).
3. <26,12> e <30,14> nas arquiteturas otimizadas: so com a conferencia bit a
   bit sem diferencas (../conferir_formatos_novos.sh). Senao, "sem
   conferencia bit a bit" no viabilidade.csv.

## Montagem (2026-10-31)

- 37 versoes no pacote (fila.txt), viabilidade.csv com a estimativa do HLS
  de cada uma.
- Fora: 30-14_114_sistolico, 7.512 DSP pela estimativa do HLS (limite 5.952).
- Conferencia bit a bit de <26,12> RND_ZERO/WRAP e <30,14> TRN/SAT nas 6
  arquiteturas otimizadas, 16 x 16 e 32 x 32: igual ao original em todas
  (../conferir_formatos_novos.log; conferencia_*.txt na pasta de cada
  arquitetura).
- RTL igual ao de uma sintese ja feita: as 5 de <24,12>, e a sem otimizacao
  em <22,12> e <28,14> (16 x 16 e 32 x 32). As outras nao tinham sintese
  anterior.

## Andamento (2026-11-03)

- Tudo pronto no servidor (Vivado e potencia): as 16 x 16 nos 5 formatos e
  as 32 x 32 sem otimizacao nos 5 formatos. A ultima terminou em
  2026-11-02 09:10 (rodar.log). Secao "Resultados no servidor".

## Como rodar

Copiar para uma pasta NOVA no servidor (nao em cima do pacote_servidor_2023,
que pode estar rodando):

    tar xzf pacote_servidor_formatos.tar.gz
    cd pacote_servidor_formatos
    module load vivado/2023.2-enterprise
    nohup ./rodar.sh todas > /dev/null 2>&1 &

- JOBS versoes rodam ao mesmo tempo (padrao 4). Ex.: `JOBS=6 ./rodar.sh todas`.
- Uma versao ou uma etapa: `./rodar.sh 24-12_9090 -- vivado`.
- Andamento em rodar.log. Cada etapa que termina grava FEITO e e pulada na
  proxima chamada; uma versao que falha nao para as outras.
- Resultados: versoes/<v>/trabalho/vivado/resumo.txt e
  versoes/<v>/trabalho/potencia/potencia.csv.

## Quantos trabalhos ao mesmo tempo

Servidor em 2026-10-31: 64 vCPUs, 188 GB (70 GB disponiveis), 7 usuarios,
carga perto de 6, swap cheio.

- Um Vivado ja usa o maximo de threads: o log diz "a maximum of 8 CPUs" no
  place e no phys_opt, e 8 e o limite do general.maxThreads no 2023.2
  (UG904 2023.2, "Multithreading with the Vivado Tools"). A sintese RTL
  pede 4 processos (UG901 2023.2), mas nos logs o tempo de CPU ficou igual
  ao tempo real (15:16 contra 15:33 na 152): roda praticamente serial.
- O xsim: o -mt do xelab paraleliza so a compilacao (UG900). Para a
  simulacao em si, sem fonte.
- Por isso o ganho vem de rodar varias versoes juntas (JOBS). Com 4: ate 32
  threads e, pelo pico da 114 em <24,12> (16 GB), uns 40 a 50 GB no pior
  caso (estimativa minha). Formatos maiores devem usar mais memoria.

## Resultados no servidor (Vivado 2023.2)

Todos os numeros desta secao sao do servidor (cadmicro-el8-03 e -04, Vivado
2023.2), nao das rodadas locais com o 2026.1. Arquivos copiados em
../resultados_servidor/: formatos/versoes/ (vivado e potencia),
xsim/ (logs da simulacao da netlist) e versoes/ (152 e 114 em <24,12>, do
../pacote_servidor_2023/). Copias de 2026-10-31 ~18:00, 2026-11-01 ~12:00 e 2026-11-03
(32 x 32).

Como cada coluna foi tirada:
- LUT, FF, DSP, BRAM_18K e caminho critico: resumo.txt (utilizacao.rpt e
  timing.rpt depois do roteamento). Todas fecham os 100 MHz.
- Dinamica e total: report_power com o SAIF da netlist roteada, no cenario
  do alvo (sem otimizacao: os 5 deram o mesmo valor; fica o TDLA30-5).
  Inversa da netlist igual a do C em todas.
- Intervalo: da propria simulacao da netlist no servidor (xsim_<cenario>.log).
  O testbench marca o instante em que cada matriz (ou lote) termina
  ("RTL Simulation : k / n @ tempo"); o intervalo e a diferenca entre duas
  marcas seguidas, dividida pelas matrizes do lote (12 na 606, 16 na 455, 32
  na 152 e na 114). As diferencas foram iguais em todas as marcas (na 152,
  4.096 ou 4.097 ciclos por lote). Em <24,12>, bate com a co-simulacao do
  HLS (LEIAME de cada arquitetura).
- Energia por inversao = dinamica x intervalo x 10 ns. Nao e a coluna
  energia_por_inversao_uj do potencia.csv, que usa os ciclos medios da
  simulacao (com a latencia do primeiro lote).
- O intervalo muda com o formato (a profundidade dos pipelines muda), entao o
  de um formato nao vale para outro.

### <24,12> RND_ZERO/WRAP

| Arquitetura | LUT | FF | DSP | BRAM_18K | Caminho critico | Cenario | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|---|
| sem_otimizacao | 6.378 | 3.399 | 94 | 11 | 7,841 ns | os 5 | 0,041 | 2,254 | 32.462 | 13,3 |
| 9090 | 35.604 | 35.600 | 106 | 15 | 7,452 ns | TDLA30-5 | 0,234 | 2,450 | 7.594 | 17,8 |
| 4545 | 35.940 | 35.730 | 106 | 25 | 7,549 ns | TDLA30-10 | 0,305 | 2,522 | 3.020 | 9,21 |
| 606 | 51.087 | 43.450 | 379 | 180 | 8,404 ns | TDLA30-75 | 0,546 | 2,768 | 504 | 2,75 |
| 455 | 55.482 | 44.110 | 456 | 240 | 8,948 ns | TDLC300-100 | 0,666 | 2,891 | 402 | 2,68 |
| 152_sistolico | 154.016 | 103.627 | 1.700 | 926 | 8,820 ns | TDLA30-300 | 1,973 | 4,223 | 128 | 2,53 |
| 114_sistolico | 372.697 | 234.826 | 3.400 | 532 | 9,742 ns | TDLB100-400 | 4,062 | 6,350 | 64 | 2,60 |

### <22,12> RND_ZERO/WRAP

| Arquitetura | LUT | FF | DSP | BRAM_18K | Caminho critico | Cenario | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|---|
| sem_otimizacao | 4.907 | 3.063 | 87 | 13 | 8,088 ns | os 5 | 0,037 | 2,249 | 30.398 | 11,2 |
| 9090 | 28.296 | 28.748 | 99 | 15 | 7,625 ns | TDLA30-5 | 0,194 | 2,409 | 7.345 | 14,2 |
| 4545 | 28.540 | 28.904 | 99 | 25 | 7,658 ns | TDLA30-10 | 0,253 | 2,469 | 2.900 | 7,34 |
| 606 | 40.337 | 35.826 | 377 | 180 | 8,814 ns | TDLA30-75 | 0,474 | 2,695 | 494 | 2,34 |
| 455 | 43.487 | 36.344 | 456 | 240 | 9,371 ns | TDLC300-100 | 0,573 | 2,797 | 395 | 2,26 |
| 152_sistolico | 120.871 | 80.557 | 1.706 | 922 | 9,541 ns | TDLA30-300 | 1,753 | 4,000 | 128 | 2,24 |
| 114_sistolico | 299.409 | 187.085 | 3.412 | 524 | 9,402 ns | TDLB100-400 | 3,477 | 5,754 | 64 | 2,23 |

### <28,14> RND_ZERO/WRAP

| Arquitetura | LUT | FF | DSP | BRAM_18K | Caminho critico | Cenario | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|---|
| sem_otimizacao | 7.027 | 4.089 | 117 | 11 | 8,363 ns | os 5 | 0,048 | 2,261 | 35.414 | 17,0 |
| 9090 | 47.449 | 47.927 | 128 | 15 | 7,757 ns | TDLA30-5 | 0,305 | 2,522 | 8.087 | 24,7 |
| 4545 | 47.727 | 48.105 | 128 | 22 | 7,626 ns | TDLA30-10 | 0,391 | 2,610 | 3.200 | 12,5 |
| 606 | 63.997 | 56.982 | 471 | 180 | 7,867 ns | TDLA30-75 | 0,647 | 2,872 | 519 | 3,36 |
| 455 | 68.616 | 57.333 | 576 | 240 | 7,790 ns | TDLC300-100 | 0,805 | 3,032 | 414 | 3,33 |
| 152_sistolico | 184.816 | 121.813 | 2.156 | 936 | 8,727 ns | TDLA30-300 | 2,180 | 4,434 | 128 | 2,79 |
| 114_sistolico | 444.699 | 278.059 | 4.312 | 544 | 9,381 ns | TDLB100-400 | 4,703 | 7,003 | 64 | 3,01 |

### <26,12> RND_ZERO/WRAP

| Arquitetura | LUT | FF | DSP | BRAM_18K | Caminho critico | Cenario | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|---|
| sem_otimizacao | 6.824 | 3.839 | 111 | 11 | 8,180 ns | os 5 | 0,046 | 2,259 | 34.374 | 15,8 |
| 9090 | 42.897 | 42.872 | 126 | 15 | 7,759 ns | TDLA30-5 | 0,280 | 2,497 | 7.842 | 22,0 |
| 4545 | 43.181 | 43.042 | 126 | 22 | 8,273 ns | TDLA30-10 | 0,362 | 2,580 | 3.140 | 11,4 |
| 606 | 59.133 | 52.228 | 459 | 180 | 8,526 ns | TDLA30-75 | 0,618 | 2,842 | 514 | 3,18 |
| 455 | 63.231 | 53.101 | 560 | 240 | 8,692 ns | TDLC300-100 | 0,759 | 2,986 | 410 | 3,11 |
| 152_sistolico | 175.047 | 110.964 | 2.092 | 932 | 9,210 ns | TDLA30-300 | 2,087 | 4,340 | 128 | 2,67 |
| 114_sistolico | 421.164 | 251.084 | 4.184 | 536 | 9,420 ns | TDLB100-400 | 4,456 | 6,751 | 64 | 2,85 |

### <30,14> TRN/SAT

| Arquitetura | LUT | FF | DSP | BRAM_18K | Caminho critico | Cenario | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|---|
| sem_otimizacao | 9.086 | 4.297 | 184 | 13 | 9,150 ns | os 5 | 0,059 | 2,272 | 38.567 | 22,8 |
| 9090 | 57.285 | 56.508 | 220 | 15 | 9,033 ns | TDLA30-5 | 0,377 | 2,595 | 8.627 | 32,5 |
| 4545 | 56.852 | 56.671 | 220 | 25 | 8,106 ns | TDLA30-10 | 0,496 | 2,717 | 3.320 | 16,5 |
| 606 | 78.510 | 68.929 | 803 | 180 | 8,700 ns | TDLA30-75 | 0,868 | 3,096 | 529 | 4,59 |
| 455 | 84.536 | 69.741 | 1.004 | 240 | 9,258 ns | TDLC300-100 | 1,037 | 3,268 | 421 | 4,37 |
| 152_sistolico | 236.708 | 147.578 | 3.756 | 940 | 9,258 ns | TDLA30-300 | 3,065 | 5,335 | 128 | 3,92 |
| 114_sistolico | fora: nao cabe (7.512 DSP na estimativa do HLS) | | | | | TDLB100-400 | | | | |

### 32 x 32, sem otimizacao

| Formato | LUT | FF | DSP | BRAM_18K | Caminho critico | Cenario | Dinamica (W) | Total (W) | Intervalo (ciclos) | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|---|---|---|
| <24,12> RND_ZERO/WRAP | 6.351 | 3.474 | 94 | 18 | 8,026 ns | os 5 | 0,046 | 2,259 | 167.310 | 77,0 |
| <22,12> RND_ZERO/WRAP | 4.971 | 3.136 | 87 | 18 | 7,723 ns | os 5 | 0,040 | 2,253 | 159.086 | 63,6 |
| <28,14> RND_ZERO/WRAP | 7.058 | 4.166 | 117 | 18 | 8,429 ns | os 5 | 0,053 | 2,266 | 179.102 | 94,9 |
| <26,12> RND_ZERO/WRAP | 6.855 | 3.916 | 111 | 18 | 8,581 ns | os 5 | 0,051 | 2,264 | 174.974 | 89,2 |
| <30,14> TRN/SAT | 9.042 | 4.372 | 184 | 18 | 8,541 ns | os 5 | 0,065 | 2,278 | 194.367 | 126 |

Observacoes:
- Todas as versoes fecham os 100 MHz (caminho critico de 7,45 a 9,74 ns) e
  atendem o alvo de ciclos. O intervalo de cada arquitetura cresce um pouco
  com o formato (pipelines mais fundos), menos na 152 e na 114, que ficam em
  128 e 64 em todos.
- Inversa da netlist igual a do C em todas as rodadas (o potencia.py para se
  diferir; nenhum log.txt tem esse erro).
- Sem otimizacao: os 5 cenarios deram a mesma potencia em todos os formatos.
- Redes casadas no SAIF (report_power, "Design Nets Matched"), quantas
  faltaram: nenhuma na sem otimizacao (2 em <22,12>, 16 x 16 e 32 x 32), na
  9090 e na 4545; 24 a 36 na 606; 32 a 240 na 455; 704 a 960 na 152
  (99,8%); 48.092 a 61.184 na 114 (95%). Nao investigado.
- <30,14> 114_sistolico nao foi sintetizada: 7.512 DSP na estimativa do HLS,
  acima dos 5.952 da XCU50 (viabilidade.csv).
- 32 x 32 sem otimizacao: a inversao leva 5,0 a 5,2 vezes os ciclos da
  16 x 16 (ex.: 167.310 contra 32.462 em <24,12>) e gasta 5,5 a 5,8 vezes a
  energia. A area quase nao muda (mesmo DSP; BRAM_18K de 11-13 para 18).
- 32 x 32: dinamica igual nos 5 cenarios, menos <24,12> TDLB100-400 (0,047
  contra 0,046 W). Nos logs do xsim, 19 das 20 diferencas entre marcas dao o
  intervalo da tabela e uma da 3 ciclos a mais.
- A 152 e a 114 em <24,12> rodaram com o ../pacote_servidor_2023/ (mesmos
  scripts de Vivado e potencia).

### Comparacao com o Vivado 2026.1 daqui (so <24,12>)

So para conferencia; os numeros do TCC sao os do servidor, acima. Fluxo do HLS, LEIAME de cada
arquitetura; sem otimizacao em ../cholesky_hardware/sinteses/
24-12_16x16_RND_ZERO_WRAP_vivado/):

| Arquitetura | LUT 2026.1 / 2023.2 | FF 2026.1 / 2023.2 | BRAM_18K | Caminho critico 2026.1 / 2023.2 | Dinamica 2026.1 / 2023.2 (W) |
|---|---|---|---|---|---|
| sem_otimizacao | 6.371 / 6.378 | 3.331 / 3.399 | 11 / 11 | 7,993 / 7,841 ns | 0,041 a 0,042 / 0,041 |
| 9090 | 35.545 / 35.604 | 35.600 / 35.600 | 15 / 15 | 7,655 / 7,452 ns | 0,233 / 0,234 |
| 4545 | 35.853 / 35.940 | 35.727 / 35.730 | 22 / 25 | 7,545 / 7,549 ns | 0,304 (TDLA30-5) / 0,305 (TDLA30-10) |
| 606 | 51.084 / 51.087 | 43.443 / 43.450 | 180 / 180 | 8,867 / 8,404 ns | 0,553 / 0,546 (TDLA30-75) |
| 455 | 55.448 / 55.482 | 44.110 / 44.110 | 240 / 240 | 9,169 / 8,948 ns | 0,669 / 0,666 (TDLC300-100) |

DSP igual em todas. LUT e FF mudam ate 2% (FF da sem otimizacao); a potencia
dinamica, ate 1,3% (606). O caminho critico muda ate 0,46 ns (606), e todas
atendem os 10 ns nas duas versoes do Vivado.
