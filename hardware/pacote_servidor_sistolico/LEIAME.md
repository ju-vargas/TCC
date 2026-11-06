# pacote_servidor_sistolico

SUBSTITUIDO por ../pacote_servidor_2023/: o servidor da UFRGS so tem o
Vivado 2023.2, e este pacote precisa do Vitis 2026.1. Mantido so como
registro.

Pacote para rodar, em outra maquina, os testes das duas versoes com arranjo
sistolico. Montado em 2026-10-30. Nesta maquina (15 GB de memoria), o Vivado
da versao 152 foi parado por falta de memoria na sintese RTL.

| Versao | Alvo | Vias | Ciclos por matriz (co-simulacao) | DSP / LUT (estimativa HLS) |
|---|---|---|---|---|
| 152_sistolico | TDLA30-300, 152 ciclos | 2 | 128 | 1.700 / 152.143 |
| 114_sistolico | TDLB100-400, 114 ciclos | 4 | 64 | 3.400 / 345.876 |

As duas tem lote de 32 matrizes. As explicacoes do codigo e os resultados
estao em versoes/<versao>/LEIAME_original.md (copia do LEIAME.md da pasta
original, hardware/cholesky_hardware_diretivas_<alvo>_sistolico/).

## O que tem aqui

- versoes/152_sistolico/ e versoes/114_sistolico/: os fontes da sintese e o
  tb_potencia.cpp. Os dois cholesky.h so diferem em `CHOL_VIAS` (2 e 4).
- listas/lista_<cenario>.txt: as mesmas 20 matrizes por cenario da
  referencia (cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/potencia/),
  com caminhos relativos ao pacote.
- matrizes/: os 100 arquivos .bits dessas listas, copiados de
  hardware/testes/2_amostra_matrizes/ (mesmas subpastas).
- rodar.sh: roda as etapas (ver abaixo).
- potencia.py: a etapa de potencia (o mesmo fluxo de rodar_potencia.py da
  referencia e de hardware/potencia_versoes.py).
- saif_hierarquia.py: copia do da referencia.

## Como rodar

Precisa do Vitis/Vivado 2026.1 (o mesmo da referencia) e de python3. O
rodar.sh usa o settings64.sh que voce indicar. NUCLEOS e opcional (taskset).

    tar xzf pacote_servidor_sistolico.tar.gz
    cd pacote_servidor_sistolico
    VITIS_SETTINGS=/caminho/2026.1/Vitis/settings64.sh ./rodar.sh todas

Ou uma versao e uma etapa por vez:

    VITIS_SETTINGS=... ./rodar.sh 152_sistolico cosim
    VITIS_SETTINGS=... ./rodar.sh 152_sistolico vivado
    VITIS_SETTINGS=... ./rodar.sh 152_sistolico potencia

| Etapa | O que faz | Resultado |
|---|---|---|
| cosim | sintese C + co-simulacao com as 20 matrizes do TDLA30-5; confere que a saida do RTL e igual a do C byte a byte, em cada porta | versoes/<v>/trabalho/cosim/resumo.txt |
| vivado | sintese C + sintese RTL e implementacao no Vivado, 100 MHz | versoes/<v>/trabalho/vivado/resumo.txt (LUT, FF, DSP, BRAM, timing) |
| potencia | netlist roteada, simulacao com SAIF, report_power, nos 5 cenarios | versoes/<v>/trabalho/potencia/potencia.csv |

- Cada etapa que termina bem grava versoes/<v>/trabalho/<etapa>/FEITO, e a
  proxima chamada pula essa etapa. Para refazer, apagar esse FEITO.
- Se uma etapa falha, o rodar.sh para naquela versao e passa para a
  seguinte. O andamento fica em rodar.log.
- A etapa potencia precisa da etapa vivado feita.

## O que ja foi conferido

- Nesta maquina, com as pastas originais: inversa igual ao original bit a
  bit (comparar_com_original.py, 6 casos), teste negativo, sintese C e
  co-simulacao. Esses resultados estao nos LEIAME_original.md.
- O rodar.sh foi testado nesta maquina so na etapa cosim da 152: deu os
  mesmos numeros de antes (latencia 17.828, total 26.021, RTL igual ao C nas
  2 portas).
- As etapas vivado e potencia do pacote NAO foram testadas aqui com as
  versoes sistolicas (falta de memoria). O potencia.py tem a mesma logica do
  hardware/potencia_versoes.py, que passou na versao 4545 (com dataflow,
  como as sistolicas): a inversa da netlist roteada saiu igual a do C, e o
  report_power rodou. Duas correcoes vieram dessa rodada: o link tv para os
  vetores do testbench e o detector de deadlock vazio (ele olha sinais
  internos do RTL, que a netlist nao tem).
- Tempo: na 4545, a simulacao da netlist de um cenario levou cerca de 40 min.
  As sistolicas sao maiores e tem lotes de 32 (pelo menos 96 matrizes por
  cenario), entao devem levar mais.

## Memoria (estimativa, sem fonte)

Na versao 455 (cerca de 55 mil LUT), os picos foram de 4,4 GB na sintese RTL
e 7,1 GB na implementacao, mais cerca de 5 GB do processo do Vivado que
chama as duas. A 152 tem cerca de 2,7 vezes mais LUT, e a 114 cerca de 6
vezes. A memoria deve crescer junto, entao vale rodar uma versao de cada vez.
