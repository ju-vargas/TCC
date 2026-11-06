# viabilidade_30_14

Sintese C (HLS 2026.1, estimativa) da 152_sistolico e da 114_sistolico em
<30,14> TRN/SAT, 16 x 16, feita em 2026-10-31 para ver se cabem na XCU50
antes de montar o pacote do servidor (rodar.sh; fontes das pastas das
versoes, so o syn.cflags trocado).

| Versao | DSP | LUT | FF | BRAM_18K | URAM | Cabe? |
|---|---|---|---|---|---|---|
| 152_sistolico | 3.756 (63%) | 215.735 (25%) | 124.850 | 756 | 0 | sim |
| 114_sistolico | 7.512 (126%) | 472.748 (54%) | 261.979 | 488 | 8 | nao |

Limites da XCU50 (utilizacao.rpt do servidor): 5.952 DSP, 871.680 LUT.

- A 114 em <30,14> passa de 5.952 DSP, entao fica fora do pacote. O DSP do
  HLS bateu com o do Vivado nas 6 versoes em <24,12>
  (../pacote_servidor_2023/LEIAME.md).
- Em <24,12>, a 152 tem 1.700 DSP e a 114 tem 3.400. Em <30,14>, os dois
  sobem 2,2 vezes.

## Resultado no servidor (2026-11-01)

A 152 em <30,14> rodou no servidor (Vivado 2023.2, ../pacote_servidor_formatos/,
versao 30-14_152_sistolico):

| | Estimativa do HLS | Vivado (depois do roteamento) |
|---|---|---|
| DSP | 3.756 | 3.756 |
| LUT | 215.735 | 236.708 (+9,7%) |
| FF | 124.850 | 147.578 (+18,2%) |
| BRAM_18K | 756 | 940 |

- DSP igual, como nas outras. Cabe na XCU50 e fecha os 100 MHz (caminho
  critico 9,258 ns).
- Aqui o Vivado deu mais FF que o HLS; em <24,12> o HLS sempre
  superestimava o FF (../pacote_servidor_2023/LEIAME.md).
