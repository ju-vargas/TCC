# cholesky_hardware_diretivas_114_sistolico

VERSAO SALVA em 2026-10-30: arranjo sistolico linear, lote de 32 matrizes
em 4 vias. Intervalo de 64 ciclos por matriz (2.049 por lote) na
co-simulacao (<24,12> RND_ZERO/WRAP, 16 x 16), inversa igual ao original bit
a bit. Atende o TDLB100-400 (114 ciclos). Nao editar os fontes desta pasta.

Copia de ../cholesky_hardware_diretivas_152_sistolico/ (versao salva no
mesmo dia: o mesmo codigo com 2 vias, 128 ciclos por matriz). O codigo e as
explicacoes estao no LEIAME.md de la. Aqui so muda o padrao de `CHOL_VIAS`
em cholesky.h, de 2 para 4. Nenhuma linha de cholesky_top.cpp mudou.

- comparar_com_original.py, sintese/rodar.sh, cosim/rodar.sh e
  vivado/rodar.sh: como na versao 152. A saida da co-simulacao fica em 4
  arquivos (inverse_0 a inverse_3):

      cd cosim/w/hls/sim/tv
      for v in 0 1 2 3; do cmp cdatafile/c.cholesky_inverse.autotvout_inverse_$v.dat \
                               rtldatafile/rtl.cholesky_inverse.autotvout_inverse_$v.dat; done

# Alteracao em relacao a versao 152

## 1. Quatro vias (2026-10-30)

Motivo: na versao 152 a etapa mais lenta (portas e inversao) gasta 128
ciclos por matriz, acima de 114. Com 4 vias, as portas e a inversao caem
para 64, e a LU e a substituicao (que ja sobravam) tambem ficam mais rapidas.
SUPOSICAO DO SISTEMA (sem fonte), como na versao 152: o resto do sistema
entrega e recebe 4 elementos por ciclo.

### Conferencia

- comparar_com_original.py --por-tamanho 1000: os 6 casos iguais
  (336/336 em 16 x 16 e 218/218 em 32 x 32, nos tres formatos).
- Teste negativo: com todas as vias da inversao lendo a matriz da via 0
  (`m = g * VIAS` em vez de `m = g * VIAS + p`), as inversas ficam
  diferentes em 16 x 16 e em 32 x 32 (13/50 iguais em 32 x 32). Codigo
  restaurado depois.

### Resultados

Sintese C (estimativa do HLS, 16 x 16, <24,12> RND_ZERO/WRAP, 100 MHz):

| Etapa | Ciclos por lote (32 matrizes) | Por matriz | Profundidade do pipeline | DSP |
|---|---|---|---|---|
| lote_ler | 2.050 | 64 | 2 | 0 |
| lote_lu | 1.851 | 58 | 79 | 1.120 |
| lote_g | 267 | 8 | | 120 |
| lote_fs | 1.872 | 59 | 82 | 1.136 |
| lote_inv | 2.053 | 64 | 5 | 1.024 |
| lote_gravar | 2.050 | 64 | 2 | 0 |

| | Versao 455 | Versao 152 | Esta versao |
|---|---|---|---|
| DSP | 456 (7%) | 1.700 (28%) | 3.400 (57%) |
| LUT | 61.050 (7%) | 152.143 (17%) | 345.876 (39%) |
| FF | 47.003 (2%) | 121.716 (6%) | 257.207 (14%) |
| BRAM | 320 (11%) | 756 (28%) | 488 (18%) |
| URAM | 0 | 0 | 8 (1%) |

- A folga de relogio estimada pelo HLS e de 0,01 ns (na 152, 0,13 ns). O
  Vivado pode nao fechar 100 MHz; ver vivado/log.txt.

Co-simulacao (cosim/rodar.sh, 3 lotes de 32 com as matrizes do TDLA30-5):

| Latencia por lote (min / med / max) | 10.134 / 10.134 / 10.135 |
|---|---|
| Tempo total (3 lotes) | 14.231 |
| Intervalo por lote | (14.231 - 10.134) / 2 = 2.049 |
| Intervalo por matriz | 2.049 / 32 = 64 |

- Status Pass, e a saida do RTL e igual a do C byte a byte nas 4 portas.
- A latencia de um lote, 10.134 ciclos (101 us), fica abaixo de
  T_c = 114 x 275 = 31.350 ciclos.
- 64 ciclos e bem menos que 114: esta versao gasta mais area do que o alvo
  pede. Uma opcao mais barata seria 3 vias (com LOTE multiplo de 3, por
  exemplo 36), com cerca de 86 ciclos por matriz nas portas e na inversao
  (256 / 3) e cerca de 3/4 dos DSP. Nao foi testada.
