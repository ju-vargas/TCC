# Contexto: pragmas HLS para atingir os ciclos por cenário

Resumo para abrir uma conversa sobre a otimização com pragmas do inversor de G_c.
Estado em 2026-10-29.

## Projeto

- Inversor de matriz hermitiana por Cholesky em Vitis HLS 2026.1, neste diretório
  (`hardware/cholesky_hardware/`). A função topo é `cholesky_inverse`.
- Arquivos: `cholesky.h`, `cholesky_ops.h`, `cholesky_decomposition.cpp`,
  `lu_decomposition.cpp`, `dv_step.cpp`, `s_step.cpp`, `g_step.cpp`,
  `foward_substitution.cpp`, `inversion.cpp` e `cholesky_top.cpp`.
- O formato e o tamanho entram por macros:
  `-DCHOL_N=16|32 -DCHOL_INT_BITS=I -DCHOL_FRAC_BITS=F -DCHOL_QUANT=... -DCHOL_OVERFLOW=...`.
- FPGA: XCU50-FSVH2104-2-E (Alveo U50), com clock de 10 ns (100 MHz).
- Formatos escolhidos, todos em AP_RND_ZERO/AP_WRAP: `ap_fixed<22,12>`, `<24,12>` e
  `<28,14>`. São dois tamanhos de matriz: 16 x 16 nas configurações 1 a 8 e 13 a 16, e
  32 x 32 nas 9 a 12.

## Estado atual: sem nenhuma diretiva

- O código não tem nenhum `#pragma HLS`.
- As sínteses usam `syn.compile.pipeline_loops=0`, que desliga o pipeline automático. A
  ferramenta ainda faz o inlining automático de funções pequenas, e a `hls::sqrt` traz
  pragmas próprios da biblioteca.
- As sínteses de referência, com implementação no Vivado, ficam em
  `sinteses/<W>-<I>_<n>x<n>_RND_ZERO_WRAP_vivado/`, cada uma com `hls.cfg` e `rodar.sh`.
- Pela análise HLS, LU e forward substitution dominam a latência.

| Formato | Matriz | LUT | FF | DSP | BRAM | Caminho crítico | Ciclos estimados pelo HLS | Ciclos medidos na co-simulação |
|---|---|---|---|---|---|---|---|---|
| <22,12> | 16 x 16 | 4.800 | 2.980 | 87 | 13 | 7,83 ns | 65.788 | 30.399 |
| <24,12> | 16 x 16 | 6.371 | 3.331 | 94 | 11 | 7,99 ns | 69.532 | 32.463 |
| <28,14> | 16 x 16 | 6.975 | 3.863 | 117 | 11 | 7,98 ns | 74.899 | 35.415 |
| <22,12> | 32 x 32 | 4.866 | 3.053 | 87 | 18 | 8,05 ns | 399.708 | 159.087 |
| <24,12> | 32 x 32 | 6.342 | 3.406 | 94 | 18 | 8,01 ns | 415.372 | ainda não medido |
| <28,14> | 32 x 32 | 6.975 | 3.940 | 117 | 18 | 8,08 ns | 437.859 | ainda não medido |

A medida na co-simulação, com 20 matrizes G_c reais (`sinteses/*_vivado/potencia/potencia.csv`),
dá cerca de metade da estimativa do HLS. A explicação provável é que o relatório do HLS
conta o pior caso dos laços, mas isso ainda não foi conferido.

## Meta: intervalo entre inversões (II), não latência

Cada módulo de inversão precisa de II_inv <= T_c / N_PRB, com N_PRB = 275
(`TCC/chapters/METODOLOGIA/requisitos-tempo.tex`, linhas 40 a 44). A 100 MHz:

| Cenário | T_c / N_PRB | Ciclos de 10 ns |
|---|---|---|
| TDLA30-5 | 90,91 µs | 9.090 |
| TDLA30-10 | 45,45 µs | 4.545 |
| TDLA30-75 | 6,06 µs | 606 |
| TDLC300-100 | 4,55 µs | 455 |
| TDLA30-300 | 1,52 µs | 152 |
| TDLB100-400 | 1,14 µs | 114 |

Hoje nenhum formato atende nem o TDLA30-5. No 16 x 16, o II precisa cair cerca de 3,5
vezes para o TDLA30-5, cerca de 55 vezes para o TDLA30-75 e cerca de 280 vezes para o
TDLB100-400.

## Restrições

1. **Não mudar a aritmética.** O resultado tem que continuar idêntico, bit a bit, ao da
   C-simulation, para todas as curvas de SER continuarem valendo. As verificações
   existentes são:
   - `hardware/testes/conferir_nativo.py`;
   - `hardware/testes/conferir_servidor.py`;
   - o `potencia/rodar_potencia.py`, que compara a netlist com o C byte a byte.

   Pragmas de pipeline, unroll, partição de memória e dataflow podem entrar. Mudar a
   ordem das somas ou o formato dos valores intermediários, não.
2. **Comparar sempre com a síntese de referência.** Mesmo formato, mesmo modo, mesmo
   tamanho e mesmo clock. Medir o II e a latência, não só a estimativa do relatório, e os
   recursos em % da XCU50.
3. **A autora decide quais diretivas testar.** Primeiro ela quer entender as opções e o
   custo de cada uma em recursos.
4. **A máquina está ocupada.** Até cerca de 8h de 2026-10-30, o testbench de potência dos
   32 x 32 roda nos núcleos 0 a 3. Não mexer nas pastas `sinteses/*_vivado/`, usar no
   máximo os núcleos 4 a 7 e não iniciar rodadas longas sem perguntar.
5. **Estilo de resposta:** em português, com frases curtas e sem emojis. Toda afirmação
   técnica deve trazer fonte (documentação da AMD/Xilinx, livro ou artigo). O que não
   tiver fonte deve vir marcado.

## Perguntas para começar

1. Quais laços dominam o II de verdade, e quais dependências entre iterações
   (recorrências) impedem o pipeline em cada etapa: Cholesky, LU, forward substitution e
   inversão?
2. Que combinação de pipeline, unroll e partição de arrays é realista para chegar a
   9.090 ciclos, depois a 606, e assim por diante? Quanto cada uma custa em DSP, LUT e
   BRAM, sabendo que hoje o inversor usa cerca de 1% da XCU50?
3. Vale usar `dataflow` entre as etapas para reduzir o II, já que a meta é intervalo e
   não latência?
4. Os cenários mais rápidos (152 e 114 ciclos) são viáveis com uma única instância, ou
   exigem várias instâncias em paralelo?
