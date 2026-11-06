# Testes do hardware

Os nomes das pastas começam pelo número do conjunto de testes da árvore
(`TCC/chapters/tabelas/arvore_testes_documento.tex`). Os conjuntos [1], [4] e [5]
ficam em `software/testes/` (ver o LEIAME de lá). O passo a passo da amostragem e da
validação está em `AMOSTRAGEM.md`.

## Pastas

| pasta | conjunto | o que tem | script que gerou |
|---|---|---|---|
| `2_amostra_matrizes/` | [2] amostra das matrizes | Matrizes G_c exportadas do simulador, por par (N, portadora) e tamanho: `amostras<N>_fc<GHz>GHz/16x16/` e `32x32/`, com um `indice.csv` (configuração, SNR, realização, cluster e métricas de cada matriz exportada) e um `indice_completo.csv` com as mesmas colunas para todas as matrizes da rodada, exportadas ou não (é dele que sai a métrica do ponto de operação, `software/testes/metrica_ponto_operacao.py`). A coluna `configuracao` usa a numeração do TCC; o nome do arquivo usa o rótulo interno (coluna `rotulo`), por exemplo `painel_11_...` é a configuração 15. | `exportar_matrizes.py --amostra` (chamado por `software/testes/gerar_testes.sh`) |
| `3_selecao_matrizes/` | entrada da [3] | As 554 matrizes escolhidas da amostra para a validação bit a bit, na mesma organização, com o motivo da escolha no `indice.csv`. | `selecionar_matrizes.py` |
| `3_validacao_bits/validacao_20261014-233452_16bits/` | [3] validação bit a bit | Hardware (C-simulation do Vitis) contra o modelo Python, etapa por etapa, com `ap_fixed<16,8>`. Resumo em `resumo.txt`. | `validar_bits.sh` |
| `3_validacao_bits/validacao_20261014-234204_64bits/` | [3] | O mesmo com `ap_fixed<64,32>` (cópia `cholesky_hardware_64bits`). | `validar_bits.sh -e parametros_64bits.env --manter-selecao` |
| `3_validacao_bits/conferir_nativo.csv` e `.log` | [3] | Compilação rápida (g++) contra a C-simulation, nos 35 modos. É o que garante que a [4] e a [5] usam os mesmos bits. | `conferir_nativo.py` |

## Sínteses HLS

Ficam em `../cholesky_hardware/sinteses/`, só com os relatórios e o log:

| pasta | o que é |
|---|---|
| `24-12_16x16_sem_otimizacao/` | `ap_fixed<24,12>`, 16 x 16, sem nenhuma diretiva (`hls_config_sintese_24_12.cfg`) |
| `24-12_32x32_sem_otimizacao/` | o mesmo em 32 x 32 (`hls_config_sintese_24_12_32.cfg`) |
| `24-12_16x16_pipeline_auto/` | 16 x 16 com o pipeline automático que o Vitis aplica sozinho (antes de `syn.compile.pipeline_loops=0`) |
| `formatos_16x16/` | 34 formatos, todos em AP_TRN/AP_SAT, sem diretivas, e `recursos.csv` com DSP, LUT, FF, BRAM, ciclos e frequência de cada um (`sintetizar_formatos.py`). Andamento em `log.txt`. |
| `modos_16x16/` | Sínteses por formato e modo de quantização e estouro, uma pasta `<I>_<F>_<quant>_<estouro>/` por síntese, e `recursos.csv` com as colunas `quant` e `overflow`. Dois grupos: (1) os 8 formatos da [4] v3 (`<22,10>`, `<24,12>`, `<26,10>`, `<28,12>`, `<30,14>`, `<32,12>`, `<34,14>`, `<36,12>`), 2026-10-27, andamento em `log_v3.txt`; (2) células (formato, modo) do mapa de perda da [4] v2: em cada linha do mapa (I com F = 32; F com I = 14), as colunas até a primeira com perda zero em tudo, inclusive, e nelas cada célula com perda <= 6 dB em algum caso (as que só dão × ficam de fora), andamento em `log_v2.txt` (`software/testes/sintetizar_v2.sh` e `celulas_sintese.py`). O AP_TRN/AP_SAT daqui bate com o de `formatos_16x16/`. Feito com `sintetizar_formatos.py --modos todos --paralelo 4` (grupo 1) e `sintetizar_formatos.py I:F:QUANT:ESTOURO ...` (grupo 2). Mapas de custo do grupo (1) em `figuras/` (`software/testes/figuras_recursos.py`). |
| `modos_32x32/` | O mesmo de `modos_16x16/` em 32 x 32 (G_c das configurações 9 a 12), para os 10 formatos da [4] v4 nos 35 modos (`software/testes/varredura4_v4.sh`). |
| `<W>-<I>_<n>x<n>_RND_ZERO_WRAP_vivado/` | Síntese HLS e implementação no Vivado (`rodar.sh`, com `vivado.flow=impl`) dos formatos do mapa de modo fixo até 3 dB, com 1 iteração: `<22,12>`, `<24,12>` e `<28,14>` em AP_RND_ZERO/AP_WRAP, em 16 x 16 e 32 x 32. Em `potencia/`, a potência com atividade real: co-simulação com `../tb_potencia.cpp` invertendo 20 matrizes G_c reais por cenário (de `2_amostra_matrizes`, configurações 1 a 8 em 16 x 16 e 9 a 12 em 32 x 32), a netlist roteada no lugar do RTL (`netlist.tcl`, `limpar_netlist.py`), o SAIF lido pelo `report_power` (`rodar_potencia.py`) e a tabela em `potencia.csv`. Depois, `potencia_corrigido.csv` (mesmas colunas, 2026-10-30): o mesmo `report_power` com o SAIF corrigido, sem simular de novo (`hardware/potencia_saif_corrigido.py`). No SAIF original, o `read_saif` lia o fim dos nomes escapados como um caractere nulo e de 14% a 19% das redes ficavam sem atividade; com a correção, 100% casam. `<24,12>` 16 x 16 foi o piloto, feito por etapas em 2026-10-28 (com `hierarquia.tcl` e `nomes.tcl` no lugar de `limpar_netlist.py`); `<28,14>` 16 x 16 em 2026-10-29 (`tudo.sh`). `<22,12>` 16 x 16 e os três 32 x 32: rodados em 2026-10-29 (`rodar.sh`, depois `tudo_potencia.sh`, encadeados por `potencia_modo_fixo.sh`, com no máximo 4 núcleos; depois da queda da sessão em 2026-10-30, `potencia_retomar.sh` terminou o `<24,12>` e o `<28,14>` 32 x 32). Feitos com o Vitis/Vivado 2026.1 local: os números de recursos e potência do TCC vêm das rodadas no servidor (Vivado 2023.2, `hardware/resultados_servidor/formatos/versoes/`, ainda rodando em 2026-10-31); estes ficam só para comparação. |

As pastas sem `_vivado` são só C synthesis do Vitis HLS (estimativas, sem implementação no Vivado), cada uma em cerca de 1 minuto. Todas na XCU50-FSVH2104-2-E, a 100 MHz, com `syn.compile.pipeline_loops=0`.

## Scripts

| script | para que serve |
|---|---|
| `exportar_matrizes.py` | exporta as matrizes que o BCD-MMSE do simulador inverte ([2]) |
| `selecionar_matrizes.py` | escolhe as matrizes da validação ([3]) |
| `validar_bits.sh` | roda a validação [3] inteira (seleção, hardware, comparação) |
| `rodar_inversoes.sh` | roda o hardware HLS nas matrizes de uma pasta |
| `inverter_no_simulador.py` | inverte as matrizes da seleção pelo caminho do simulador e compara bit a bit |
| `conferir_nativo.py` | compilação rápida contra C-simulation |
| `conferir_servidor.py` | confere o servidor do hardware (usado pela [4] e pela [5]) contra a C-simulation |
| `../cholesky_hardware/tb_potencia.cpp` | testbench da potência: inverte em sequência as matrizes de uma lista, para a co-simulação gravar a atividade (SAIF) |
| `../cholesky_hardware/sinteses/potencia_modo_fixo.sh` | espera as sínteses do modo fixo e roda a potência de cada uma, presa aos núcleos 0 a 3 |
| `../cholesky_hardware/sinteses/potencia_retomar.sh` | retoma a cadeia de `potencia_modo_fixo.sh` depois da queda de 2026-10-30 (potência do `<24,12>` 32 x 32 e o `<28,14>` 32 x 32 inteiro) |
| `../potencia_saif_corrigido.py` | refaz só o `report_power` das pastas `*_vivado/potencia/` com o SAIF corrigido e grava `potencia_corrigido.csv`, sem apagar o original |
| `../cholesky_hardware/sintetizar_formatos.py` | síntese HLS de uma lista de formatos (`I:F`). Sem opções, em AP_TRN/AP_SAT, para `formatos_16x16/`. Com `--modos todos`, nos 35 modos, para `modos_16x16/`. `--paralelo k` roda k sínteses ao mesmo tempo. Pula o que já tem relatório. |
