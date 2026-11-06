# pacote_servidor_formatos_18_20

Pacote para rodar o Vivado e a potencia de todas as arquiteturas em <18,8>
(RND_ZERO/WRAP e TRN/SAT) e <20,8> (RND_ZERO/WRAP), no servidor (Vivado
2023.2). Montado em 2026-11-03 pelo ../montar_pacote_formatos.py, o mesmo do
../pacote_servidor_formatos/ (ver o LEIAME dele). Os scripts do servidor
(rodar.sh, vivado.tcl, potencia.py, resumo_vivado.py) sao copias dos de la.

## O que entra

| Nome no pacote | Formato | Modo | I | F |
|---|---|---|---|---|
| 18-8 | <18,8> | RND_ZERO/WRAP | 8 | 10 |
| 18-8-TRN-SAT | <18,8> | TRN/SAT | 8 | 10 |
| 20-8 | <20,8> | RND_ZERO/WRAP | 8 | 12 |

- Arquiteturas e cenarios da potencia: os mesmos do primeiro pacote
  (sem_otimizacao com os 5 cenarios; 9090 TDLA30-5, 4545 TDLA30-10, 606
  TDLA30-75, 152_sistolico TDLA30-300, 455 TDLC300-100, 114_sistolico
  TDLB100-400).
- Por ultimo, a versao sem otimizacao em 32 x 32 nos 3 formatos. No primeiro
  pacote, a potencia de cada uma dessas levou de 11 a 16 horas no servidor
  (rodar.log de la, com 4 versoes ao mesmo tempo).
- Nome de cada versao: <nome>_<arquitetura>[_32x32], em versoes/. fila.txt
  tem a ordem.

Antes de entrar no pacote, cada versao passa por:
1. Sintese C, com o corte da XCU50 pela estimativa do HLS (viabilidade.csv).
2. Arquiteturas otimizadas: conferencia bit a bit contra os fontes
   originais, 16 x 16 e 32 x 32 (../conferir_formatos_novos.sh;
   conferencia.log e conferencia_*.txt na pasta de cada arquitetura). So
   entra sem diferencas.
3. Nenhum desses formatos tinha sintese anterior para comparar o RTL.

## Divisao por zero (I = 8)

Com I = 8, parte das matrizes faz o |y|^2 do cdiv dar zero: 93 de 336 em
16 x 16 e 62 de 218 em 32 x 32 no <18,8> RND_ZERO/WRAP (conferencia_*.txt).
Nas listas de potencia, de 3 a 9 das 20 matrizes de cada cenario. O C
morria com SIGFPE e a cosimulacao nao gerava os vetores (primeira tentativa:
_montagem/montagem_falhou_sigfpe.log). Nos outros formatos isso nao acontece
nas listas de potencia (<22,12> tem 1 falha em 336 matrizes, fora delas).

- O RTL nao para: o divisor sequencial (cholesky_inverse_sdiv_*_seq_1.v)
  da quociente -1 LSB (dividendo >= 0) ou +1 LSB (dividendo < 0).
- O cholesky_ops.h de cada arquitetura ganhou esse mesmo valor para o C,
  so com -DCHOL_DIV0_COMO_RTL e fora da sintese (#ifndef __SYNTHESIS__).
  O montar_pacote_formatos.py liga a macro. O servidor da varredura
  (../cholesky_hardware_servidor) nao mudou: la a falha continua NaN e
  conta como erro na SER.
- Conferido em 2026-11-03 com 18-8_sem_otimizacao, TDLA30-5 (7 das 20 dividem
  por zero), em _montagem/teste_div0/: o RTL com a macro e igual ao de sem
  ela (25 arquivos, so mudam os numeros de linha nos nomes dos sinais); a
  cosimulacao completa deu PASS e as inversas do RTL iguais as do C, byte a
  byte.
- As 20 matrizes de cada cenario sao as mesmas dos outros formatos. As que
  funcionam dao a mesma inversa da varredura V4; as que dividem por zero
  dao o valor do circuito, onde a V4 tem NaN.

## Montagem (2026-11-03)

- 24 versoes no pacote (fila.txt), todas cabem na XCU50 pela estimativa do
  HLS (viabilidade.csv). A maior: 18-8-TRN-SAT_114_sistolico, 3.352 DSP e
  358.992 LUT.
- Conferencia bit a bit das 6 arquiteturas otimizadas nos 3 formatos, 16 x 16
  e 32 x 32: igual ao original em todas (conferencia.log).

## Resultados (16 x 16, 2026-11-04)

Copiados para ../resultados_servidor/formatos_18_20/ (relatorios) e
../resultados_servidor/xsim/pacote_servidor_formatos_18_20/ (logs do xsim).
Tabela completa em ../resultados_servidor/resultados_vivado_servidor.csv.

- Primeira rodada: a potencia de 17 versoes falhou no xsim ("Failed to compile
  generated C file"), porque o / do servidor (onde fica o /tmp) estava 100%
  cheio. Rodadas de novo em 2026-11-04 com `export TMPDIR=~/TCC/tmp` antes do
  rodar.sh. Todas deram ok.
- As 21 versoes de 16 x 16 fecham o timing a 100 MHz (WNS de 0,344 a 2,759 ns).
- As inversas da netlist sao iguais as do C, byte a byte, em todos os
  cenarios (o potencia.py para se nao forem). Isso inclui as matrizes que
  dividem por zero.
- 0 erros nos logs do xsim.

| Formato | Arquitetura | LUT | DSP | Dinamica (W) | Intervalo (ciclos) | Energia (uJ) |
|---|---|---|---|---|---|---|
| <18,8> | sem_otimizacao | 4.095 | 87 | 0,031 | 26.702 | 8,28 |
| <18,8> | 9090 | 21.577 | 99 | 0,151 | 7.081 | 10,69 |
| <18,8> | 4545 | 21.779 | 99 | 0,209 | 2.780 | 5,81 |
| <18,8> | 606 | 31.951 | 377 | 0,369 | 483,9 | 1,79 |
| <18,8> | 455 | 34.515 | 456 | 0,452 | 387,3 | 1,75 |
| <18,8> | 152_sistolico | 95.842 | 1.702 | 1,368 | 128 | 1,75 |
| <18,8> | 114_sistolico | 240.836 | 3.404 | 2,908 | 64 | 1,86 |
| <18,8> TRN/SAT | sem_otimizacao | 4.920 | 83 | 0,034 | 26.735 | 9,09 |
| <18,8> TRN/SAT | 9090 | 22.731 | 99 | 0,158 | 7.342 | 11,60 |
| <18,8> TRN/SAT | 4545 | 22.736 | 99 | 0,208 | 2.765 | 5,75 |
| <18,8> TRN/SAT | 606 | 34.717 | 377 | 0,400 | 483,9 | 1,94 |
| <18,8> TRN/SAT | 455 | 38.237 | 456 | 0,482 | 387,3 | 1,87 |
| <18,8> TRN/SAT | 152_sistolico | 112.100 | 1.702 | 1,425 | 128 | 1,82 |
| <18,8> TRN/SAT | 114_sistolico | 277.257 | 3.404 | 3,167 | 64 | 2,03 |
| <20,8> | sem_otimizacao | 4.597 | 87 | 0,035 | 30.398 | 10,64 |
| <20,8> | 9090 | 27.571 | 99 | 0,187 | 7.346 | 13,74 |
| <20,8> | 4545 | 27.825 | 99 | 0,252 | 2.900 | 7,31 |
| <20,8> | 606 | 39.080 | 377 | 0,450 | 493,9 | 2,22 |
| <20,8> | 455 | 42.135 | 456 | 0,570 | 394,8 | 2,25 |
| <20,8> | 152_sistolico | 116.952 | 1.714 | 1,679 | 128 | 2,15 |
| <20,8> | 114_sistolico | 289.316 | 3.428 | 3,313 | 64 | 2,12 |

- Energia = dinamica x intervalo x 10 ns. O intervalo e a diferenca mais comum
  entre as marcas do log do xsim, dividida pelo lote (606: 12; 455: 16; 152 e
  114: 32).
- sem_otimizacao: a potencia dos 5 cenarios fica entre 0,031 e 0,036 W; a
  tabela usa a do TDLA30-5.
- 114_sistolico: 94% a 95% das redes casadas no SAIF, como nos outros
  formatos.
- 32 x 32 sem otimizacao: Vivado pronto (timing fechado, WNS de 1,675 a 1,971
  ns); potencia ainda rodando.

## Como rodar

Copiar para uma pasta NOVA no servidor:

    tar xzf pacote_servidor_formatos_18_20.tar.gz
    cd pacote_servidor_formatos_18_20
    module load vivado/2023.2-enterprise
    nohup ./rodar.sh todas > /dev/null 2>&1 &

- JOBS versoes rodam ao mesmo tempo (padrao 4). Ex.: `JOBS=6 ./rodar.sh todas`.
- Uma versao ou uma etapa: `./rodar.sh 18-8_9090 -- vivado`.
- Andamento em rodar.log. Resultados em versoes/<v>/trabalho/vivado/resumo.txt
  e versoes/<v>/trabalho/potencia/potencia.csv.
