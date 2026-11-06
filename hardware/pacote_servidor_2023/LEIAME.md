# pacote_servidor_2023

Pacote para rodar o Vivado e a potencia das versoes sistolicas no servidor,
que so tem o Vivado/Vitis 2023.2. Montado em 2026-10-30. Substitui o
pacote_servidor_sistolico, que precisa do Vitis 2026.1 no servidor.

A parte do HLS foi feita aqui, com o Vitis 2026.1 (o mesmo das outras
versoes): o RTL e os vetores de teste de cada cenario ja vem prontos. No
servidor rodam so o Vivado e o xsim.

| Versao | Para que | Vias | Matrizes por cenario |
|---|---|---|---|
| 455 | calibracao (ja tem resultados com o Vivado 2026.1) | 8 | 48 |
| 152_sistolico | alvo TDLA30-300, 152 ciclos | 2 | 96 |
| 114_sistolico | alvo TDLB100-400, 114 ciclos | 4 | 96 |

O testbench inverte lotes inteiros (pelo menos 3), entao o numero de
matrizes passa das 20 da lista de cada cenario.

## Como rodar

    tar xzf pacote_servidor_2023.tar.gz
    cd pacote_servidor_2023
    module load vivado/2023.2-enterprise
    ./rodar.sh todas

Ou uma versao e uma etapa por vez (NUCLEOS e opcional, usa o taskset):

    NUCLEOS=0-7 ./rodar.sh 455 vivado
    ./rodar.sh 455 potencia

Ordem sugerida: primeiro a 455 completa. Se ela der certo, a 152 e depois a
114 (a maior).

| Etapa | O que faz | Resultado |
|---|---|---|
| vivado | sintese RTL e implementacao fora de contexto, 100 MHz (vivado.tcl) | versoes/<v>/trabalho/vivado/resumo.txt |
| potencia | simulacao da netlist roteada com SAIF, confere a saida com a do C, report_power, nos 5 cenarios (potencia.py) | versoes/<v>/trabalho/potencia/potencia.csv |

- Cada etapa que termina bem grava versoes/<v>/trabalho/<etapa>/FEITO, e a
  proxima chamada pula essa etapa. Para refazer, apagar esse FEITO.
- Se uma etapa falha, o rodar.sh para naquela versao e passa para a
  seguinte. O andamento fica em rodar.log; o log do Vivado em
  versoes/<v>/trabalho/vivado/log.txt.
- Se a netlist der uma inversa diferente da do C, a etapa potencia para com
  "as inversas da netlist diferem das do C".

## O que tem aqui

- versoes/<v>/rtl/: o RTL que o HLS 2026.1 gerou (syn/verilog), igual
  arquivo por arquivo ao das sinteses ja feitas nas pastas
  hardware/cholesky_hardware_diretivas_<v>/, mais o xdc (relogio de 10 ns).
- versoes/<v>/sim/: o testbench da co-simulacao do HLS, sem o RTL. O
  potencia.py poe a netlist roteada no lugar dele.
- versoes/<v>/cenarios/<cenario>/: os vetores de entrada e as inversas do C
  (tv/cdatafile) e o numero de matrizes. Sao as mesmas 20 matrizes por
  cenario da referencia.
- vivado.tcl, potencia.py, resumo_vivado.py, rodar.sh: os scripts.
- O pacote foi montado por hardware/montar_pacote_2023.py.

## Calibracao com a 455

A 455 roda no servidor com os mesmos scripts das sistolicas. Comparando com
os resultados dela feitos aqui, da para ver quanto a versao do Vivado muda
os numeros. Resultados da 455 aqui (Vivado 2026.1, fluxo do HLS):

| | LUT | FF | DSP | BRAM (blocos de 36 kb) | URAM | Caminho critico |
|---|---|---|---|---|---|---|
| 455, 2026.1 | 55.448 | 44.110 | 456 | 120 | 0 | 9,169 ns |

Duas diferencas entre o fluxo daqui e o do servidor:

1. A versao do Vivado (2026.1 aqui, 2023.2 no servidor).
2. O topo. O HLS poe o inversor dentro de um block design (bd_0_wrapper).
   O vivado.tcl sintetiza o cholesky_inverse direto. As opcoes sao as mesmas
   do script que o HLS gerou: synth_design -directive
   sdx_optimization_effort_high -mode out_of_context, e opt_design,
   place_design, phys_opt_design e route_design com as opcoes padrao.

Para separar as duas diferencas, o vivado.tcl tambem rodou aqui, com o
Vivado 2026.1 (2026-10-30). No servidor, rodou com o 2023.2 (17 min):

| 455 | LUT | FF | DSP | BRAM | URAM | Caminho critico |
|---|---|---|---|---|---|---|
| 2026.1, fluxo do HLS | 55.448 | 44.110 | 456 | 120 | 0 | 9,169 ns |
| 2026.1, vivado.tcl | 55.453 | 44.110 | 456 | 120 | 0 | 9,269 ns |
| 2023.2, vivado.tcl (servidor) | 55.482 | 44.110 | 456 | 120 | 0 | 8,948 ns |

FF, DSP, BRAM e URAM iguais nos tres. LUT muda menos de 0,1%. O caminho
critico varia entre 8,9 e 9,3 ns, e os tres atendem os 10 ns. Aqui, o
vivado.tcl teve pico de 7,1 GB de memoria (route_design) e levou cerca de
28 min (dividindo os nucleos com outras simulacoes).

## O que foi conferido aqui

- RTL de cada versao igual, arquivo por arquivo, ao da sintese ja feita na
  pasta da versao (montar_pacote_2023.py confere).
- vivado.tcl na 455, com o Vivado 2026.1 (tabela acima).
- potencia.py com a netlist roteada da 455 (fluxo do HLS), xsim 2026.1,
  TDLA30-5: o testbench sem o RTL elabora com as bibliotecas reduzidas, e a
  inversa da netlist sai igual a do C.
- Gravacao do SAIF escopo por escopo, na 4545 (TDLB100-400): mesma potencia
  do SAIF antigo (2,521 W total, 0,304 W dinamica) e inversa igual a do C.
  Com current_scope, casam 115.449 de 115.449 redes, como no SAIF antigo
  (conferido com uma simulacao curta, de 2 us).
- Nao testados aqui: o POST_SYN (so as sistolicas tem o verificador de
  dependencias, e nao ha netlist delas aqui) e o read_saif com o caminho de
  dois niveis sobre o roteado.dcp do vivado.tcl. Os dois funcionaram no
  servidor, na 152 (secao seguinte).

## Resultados do Vivado no servidor (2026-10-30)

| Versao | LUT | FF | DSP | BRAM (blocos de 36 kb) | URAM | Caminho critico | Tempo | Pico de memoria |
|---|---|---|---|---|---|---|---|---|
| 455 | 55.482 | 44.110 | 456 | 120 | 0 | 8,948 ns | 17 min | |
| 152_sistolico | 154.016 | 103.627 | 1.700 | 463 | 0 | 8,820 ns | 50 min | 9,9 GB |
| 114_sistolico | 372.697 | 234.826 | 3.400 | 266 | 0 | 9,742 ns | 1 h 54 min | 15,8 GB |

Relatorios em ../resultados_servidor/. A memoria ficou bem abaixo da
estimativa da secao seguinte (cerca de 20 GB na 152 e 40 GB na 114).

## Potencia no servidor

| Versao | Cenario | Matrizes | Total (W) | Dinamica (W) | Ciclos medios na simulacao | Intervalo em regime | Energia por inversao (uJ) |
|---|---|---|---|---|---|---|---|
| 152_sistolico | TDLA30-300 | 96 | 4,223 | 1,973 | 271 | 128 | 2,53 |
| 114_sistolico | TDLB100-400 | 96 | 6,350 | 4,062 | 148 | 64 | 2,60 |

- 152: os 5 cenarios terminaram em 2026-10-31 07:23 (tabela completa no
  LEIAME da 152); fica aqui o do alvo, TDLA30-300. Inversa igual a do C,
  99,85% das redes casadas, confianca High.
- 114: so o cenario do alvo (potencia.py --cenarios TDLB100-400), no
  cadmicro-el8-04; terminou em 2026-10-31 21:59. Inversa igual a do C,
  confianca High, mas so 95% das redes casadas (1.078.715 de 1.131.451),
  menos que na 152. Nao investigado.
- A coluna energia_por_inversao_uj do potencia.csv usa os ciclos medios, que
  incluem a latencia do primeiro lote (sao so 3 lotes). A tabela acima usa o
  intervalo em regime, tirado do log da simulacao da netlist no servidor
  (xsim_<cenario>.log, diferenca entre as marcas de fim de lote / 32). Na
  114: 2.048 e 2.049 ciclos por lote, 64 por matriz, igual a co-simulacao.
  Logs em ../resultados_servidor/xsim/pacote_servidor_2023/.

## Estimativa do HLS e resultado do Vivado (<24,12>, 16 x 16)

Estimativa da sintese C do HLS 2026.1 e valor depois do roteamento (LEIAME de
cada versao). Vivado 2026.1 aqui da 9090 a 455; 2023.2 no servidor na 152 e
na 114. Entre parenteses, quanto o Vivado ficou acima (+) ou abaixo (-) do
HLS.

| Versao | DSP (HLS / Vivado) | LUT (HLS / Vivado) | FF (HLS / Vivado) | BRAM_18K (HLS / Vivado) |
|---|---|---|---|---|
| 9090 | 106 / 106 | 36.995 / 35.545 (-3,9%) | 37.932 / 35.600 (-6,1%) | 11 / 15 |
| 4545 | 106 / 106 | 36.962 / 35.853 (-3,0%) | 37.958 / 35.727 (-5,9%) | 19 / 22 |
| 606 | 380 / 379 | 57.020 / 51.084 (-10,4%) | 48.676 / 43.443 (-10,8%) | 240 / 180 |
| 455 | 456 / 456 | 61.050 / 55.448 (-9,2%) | 47.003 / 44.110 (-6,2%) | 320 / 240 |
| 152_sistolico | 1.700 / 1.700 | 152.143 / 154.016 (+1,2%) | 121.716 / 103.627 (-14,9%) | 756 / 926 |
| 114_sistolico | 3.400 / 3.400 | 345.876 / 372.697 (+7,8%) | 257.207 / 234.826 (-8,7%) | 488 / 532 |

- DSP: o HLS acerta (igual em 5, 1 a menos na 606).
- LUT: o HLS superestima nas versoes menores (3 a 10%) e subestima nas
  sistolicas (ate 7,8% na 114).
- FF: o HLS sempre superestima (6 a 15%).
- BRAM: erra para os dois lados. URAM da 114: 8 no HLS, 0 no Vivado.
- Por isso a sintese C serve para decidir se uma versao cabe na XCU50 pelo
  DSP (5.952 no dispositivo, utilizacao.rpt). No LUT (871.680), dar uns 10%
  de margem sobre o HLS.

## Memoria (estimativa feita antes de rodar, sem fonte)

Aqui, na 455, o Vivado do HLS teve picos de 6,0 GB na sintese RTL e 7,1 GB
na implementacao (logs do synth_1 e do impl_1). O vivado.tcl roda tudo num
processo so. A 152 tem cerca de 2,7 vezes mais LUT que a 455 e a 114 cerca de
6 vezes (estimativa do HLS), entao a memoria deve crescer junto. Vale rodar
uma versao de cada vez.
