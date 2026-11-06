# viabilidade_32x32

Sintese C (HLS 2026.1, estimativa) das 6 arquiteturas otimizadas em 32 x 32,
<24,12> RND_ZERO/WRAP, feita em 2026-11-02 (rodar.sh, de 03:2x a 04:01).
Fontes das pastas das versoes; o hls.cfg e o da sintese 16 x 16 de cada uma
(vivado/hls.cfg), so com CHOL_N=32. LOTE e VIAS sao os mesmos de 16 x 16.
Ate aqui as arquiteturas so tinham a conferencia bit a bit em C em 32 x 32
(LEIAME de cada versao); nunca tinham sido sintetizadas nesse tamanho.

## Area

| Arquitetura | DSP | LUT | FF | BRAM_18K | URAM | Cabe? |
|---|---|---|---|---|---|---|
| 9090 | 106 | 37.097 | 38.016 | 22 | 0 | sim |
| 4545 | 106 | 37.064 | 38.045 | 58 | 0 | sim |
| 606 | 380 | 57.298 | 48.831 | 192 | 48 | sim |
| 455 | 456 | 61.360 | 47.191 | 256 | 64 | sim |
| 152_sistolico | 3.300 | 245.242 | 184.809 | 1.888 | 0 | sim |
| 114_sistolico | 6.600 | 478.403 | 363.035 | 2.792 | 0 | nao |

Limites da XCU50 (utilizacao.rpt do servidor): 5.952 DSP, 871.680 LUT,
1.344 blocos de BRAM de 36 kb (2.688 BRAM_18K) e 640 URAM.

- A 114 passa no DSP (6.600) e no BRAM (2.792 BRAM_18K).
- A 152 usa 55% do DSP e 70% do BRAM. Na 16 x 16 o BRAM do Vivado ficou
  acima do HLS (926 contra 756), entao a margem de BRAM e menor do que
  parece.
- DSP e LUT das 4 primeiras quase nao mudam com N: o paralelismo vem das
  diretivas, nao do tamanho da matriz.

## Ciclos por matriz (estimativa do HLS)

Intervalo do topo (csynth.xml, Interval-min e Interval-max), dividido pelo
LOTE nas versoes com lote (12 na 606, 16 na 455, 32 na 152 e na 114).
Entre parenteses, o mesmo para 16 x 16 e o intervalo medido na
co-simulacao 16 x 16.

| Arquitetura | Alvo | 32 x 32, min a max | 16 x 16, min a max (co-simulacao) |
|---|---|---|---|
| 9090 | 9.090 | 16.835 a 88.631 | 3.691 a 13.951 (7.594) |
| 4545 | 4.545 | 11.445 a 40.422 | 1.606 a 6.646 (3.020) |
| 606 | 606 | 1.910 a 6.763 | 256 a 1.078 (504) |
| 455 | 455 | 1.433 a 5.322 | 256 a 869 (402) |
| 152_sistolico | 152 | 512 | 128 (128) |
| 114_sistolico | 114 | 256 | 64 (64) |

- Nenhuma atende o alvo em 32 x 32: ate o minimo estimado passa do alvo.
  Na 16 x 16, o intervalo da co-simulacao ficou sempre entre o minimo e o
  maximo do HLS (e igual nas sistolicas), entao o minimo serve de limite de
  baixo.
- Nas sistolicas o intervalo e exato e cresce 4 vezes (N^2): 128 para 512 e
  64 para 256.
- Para atender os alvos em 32 x 32 seria preciso outra arquitetura (mais
  vias, por exemplo), com mais area. Nao foi testado.
