# Amostragem das matrizes de teste

Registro de como foram obtidas as matrizes em `2_amostra_matrizes/`, usadas para testar a
inversão por Cholesky do hardware com os dados reais do simulador.

## 1. Que matrizes são

No BCD-MMSE, cada DU c inverte, a cada atualização, a matriz

    den = Es * H_c H_c^H + R_cc        (M_c x M_c, hermitiana definida positiva)

em que `H_c` é o canal das antenas do cluster c e `R_cc` é a covariância do ruído
estimada no cluster, com o condicionamento Ledoit-Wolf do simulador. É essa a
inversa M_c x M_c que o hardware vai calcular.

`den` não depende de W, então não muda entre as iterações do BCD. Cada DU só
precisa invertê-la uma vez por (realização, SNR).

### Condições de teste

As condições de teste 3GPP (`params.M1_Driver.test_conditions` no simulador)
mudam duas coisas nas matrizes:

- o número de amostras de ruído N usado para estimar `R_cc`, que vem do tempo de
  coerência (REs de DM-RS de um PRB dentro de T_c, no máximo 192);
- a portadora: 3,5 GHz nas condições de FR1 e 28 GHz nas de FR2. Os espalhamentos
  angulares do cenário UMa NLOS dependem da frequência, então os canais (e a
  correlação entre antenas) mudam. Os canais a 28 GHz são uma exportação própria
  do QuaDRiGa, com a mesma semente e as mesmas posições dos UEs.

A velocidade entra só pelo T_c, ou seja, pelo N: o canal é constante dentro do
bloco de coerência, sem Doppler. Condições com o mesmo par (N, portadora) dão as
mesmas matrizes, então cada par é exportado uma vez:

| Pasta | N | Portadora | Condições |
| :-- | :-- | :-- | :-- |
| `amostras192_fc3.5GHz/` | 192 | 3,5 GHz | TDLA30-5, TDLA30-10 |
| `amostras192_fc28GHz/` | 192 | 28 GHz | TDLA30-75 |
| `amostras168_fc28GHz/` | 168 | 28 GHz | TDLA30-300 |
| `amostras132_fc3.5GHz/` | 132 | 3,5 GHz | TDLC300-100 |
| `amostras24_fc3.5GHz/` | 24 | 3,5 GHz | TDLB100-400 |

N é o pior caso com DM-RS duplo, nos símbolos 2, 3, 10 e 11 (Tabela
`tab:n-condicao` do texto). HST350 e HST500 ficam de fora: no pior caso N = 0.
Com N = 24 e M_c = 32 (configurações 9 a 12), N é menor que M_c: o `R_cc` amostral não tem
inversa, e só o Ledoit-Wolf de cada bloco o torna inversível.

Configurações (numeração do texto, Tabela `tab:paineis`; o rótulo é o nome usado
no código e nos arquivos):

| Configuração | Rótulo | M | C | M_c | K | IoT (dB) | Modulação | Na amostra |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | a | 128 | 8 | 16 | 8 | 10 | 16-QAM | sim (referência) |
| 2 | f | 128 | 8 | 16 | 8 | 20 | 16-QAM | sim |
| 3 | e | 128 | 8 | 16 | 12 | 10 | 16-QAM | sim |
| 4 | 7 | 128 | 8 | 16 | 12 | 20 | 16-QAM | sim |
| 5 | g | 128 | 8 | 16 | 8 | 10 | QPSK | não: mesma matriz da 1 (ver seção 4) |
| 6 | 15 | 128 | 8 | 16 | 8 | 20 | QPSK | não: mesma matriz da 2 |
| 7 | 14 | 128 | 8 | 16 | 12 | 10 | QPSK | não: mesma matriz da 3 |
| 8 | 16 | 128 | 8 | 16 | 12 | 20 | QPSK | não: mesma matriz da 4 |
| 9 | b | 256 | 8 | 32 | 8 | 10 | 16-QAM | sim |
| 10 | 9 | 256 | 8 | 32 | 8 | 20 | 16-QAM | sim |
| 11 | 8 | 256 | 8 | 32 | 12 | 10 | 16-QAM | sim |
| 12 | 10 | 256 | 8 | 32 | 12 | 20 | 16-QAM | sim |
| 13 | c | 256 | 16 | 16 | 8 | 10 | 16-QAM | sim (16 clusters por ponto) |
| 14 | 12 | 256 | 16 | 16 | 8 | 20 | 16-QAM | sim |
| 15 | 11 | 256 | 16 | 16 | 12 | 10 | 16-QAM | sim |
| 16 | 13 | 256 | 16 | 16 | 12 | 20 | 16-QAM | sim |

Os nomes dos arquivos usam o rótulo: `painel_7_r003_snr+00_c01` é da configuração 4.
O rótulo não é o número da configuração: os rótulos 7 a 16 seguem a ordem em que as
configurações extras foram criadas, e a numeração do texto foi reordenada depois.

## 2. Como são obtidas

Script: `exportar_matrizes.py`.

O script roda o próprio simulador (`run_panel`, com a mesma semente) e, só na
memória do processo, troca a função de inversão do BCD por uma que guarda cada
`den` antes de inverter. Nenhum arquivo do simulador é alterado. Assim as
matrizes são exatamente as que o simulador inverte, na mesma sequência de
números aleatórios, sem reconstrução por fora.

Cada par (N, portadora) roda o simulador com esses valores (`n_noise_samples` e
`carrier_hz` do `SimConfig`). O simulador é rodado com 1 iteração do BCD. Cada ponto (realização, SNR) faz
então C inversões, uma por cluster e na ordem dos clusters, o que dá a origem
de cada matriz capturada. O script confere o total de inversões e para se ele
não bater.

Verificações feitas:

- recalculando `den` por fora do simulador, com a mesma fórmula e o mesmo
  consumo do gerador aleatório, as matrizes coincidem (diferença abaixo de
  10^-12, que foi o arredondamento usado nesse teste);
- o testbench do Vitis (compilado com g++ e os headers do Vitis, N = 16) e o
  `golden_cholesky.py` dão as 8 etapas iguais bit a bit nas matrizes exportadas
  que não estouram o formato.

## 3. Formato dos arquivos

Cada matriz vira dois arquivos, com o mesmo nome:

    painel_<p>_r<realização>_snr<SNR>_c<cluster>.txt
    painel_<p>_r<realização>_snr<SNR>_c<cluster>.bits

Exemplo: `painel_a_r000_snr+00_c00` = painel a, realização 0, SNR 0 dB, cluster 0.

- **`.txt`**: formato do `A.txt` (primeira linha com n, depois as linhas com
  `re+imj`). Cada número está em decimal **exato**: a leitura (`std::stod` no
  testbench, `complex()` no `golden_cholesky.py`) devolve exatamente o mesmo
  `float64` do simulador. O script relê cada arquivo e para se isso falhar.
  Não há notação científica nem hexfloat porque o testbench separa a parte real
  da imaginária pelo primeiro `+` ou `-` depois do início do número, e um
  expoente (`e-05`, `p+4`) quebraria essa separação.
- **`.bits`**: os 64 bits IEEE 754 de cada parte, `real:imag` por elemento, no
  mesmo layout dos `.bits` do hardware. É a representação completa do valor.

Os arquivos ficam em uma pasta por par (N, portadora) e, dentro dela, uma pasta
por tamanho de matriz: `2_amostra_matrizes/amostras24_fc3.5GHz/16x16/`,
`2_amostra_matrizes/amostras24_fc3.5GHz/32x32/` etc. Painéis diferentes com o mesmo M_c
dividem a pasta, por isso o painel faz parte do nome. O `indice.csv` tem a coluna `configuracao`,
com o número da configuração no texto, e a coluna `rotulo`, com o rótulo interno
que vai no nome do arquivo. Também tem as colunas `n_amostras`, `portadora_ghz` e `condicoes`. A coluna `n` continua
sendo a dimensão da matriz, como o `CHOL_N`.

## 4. Como a amostra é escolhida

Exportar tudo não é prático (cerca de 50 KB por matriz 16 x 16, e um painel
inteiro tem 100 realizações x 11 SNRs x C clusters). O modo `--amostra` faz:

A amostragem é feita separadamente para cada par (N, portadora). Assim os
extremos de um par (por exemplo, N = 12) não ocupam as vagas de extremo dos
outros.

1. Roda cada painel pedido com todas as realizações e calcula as métricas de
   **todas** as matrizes, sem gravá-las. As métricas vão para
   `indice_completo.csv` na pasta de cada tamanho.
2. Seleciona uma amostra por três critérios e grava só ela. O motivo de cada
   escolha fica na coluna `motivo` do `indice.csv`; quando uma matriz entra por
   mais de um motivo, eles aparecem juntos com `+`.

### Métricas

| Métrica | O que testa no hardware |
| :-- | :-- |
| `max_abs_parte` | maior parte real ou imaginária; acima de 2^(I-1) estoura os bits inteiros |
| `max_abs_inversa` | maior entrada da inversa; precisa caber no tipo de dados na saída |
| `menor_autovalor` | comparado com 2^-F, mostra quanta precisão sobra |
| `numero_condicao` | quanto o erro de arredondamento é amplificado |

### Critérios

| Motivo | Regra | Padrão |
| :-- | :-- | :-- |
| `cobertura` | sorteio de `--por-snr` matrizes (realização, cluster) para cada (painel, SNR) | 3 |
| `max_abs_parte`, `numero_condicao`, `max_abs_inversa` | as `--extremos` maiores de cada tamanho de matriz | 5 |
| `menor_autovalor` | as `--extremos` menores de cada tamanho de matriz | 5 |
| `estrato<k>` | `--por-estrato` sorteadas em cada uma das `--estratos` faixas de log10(número de condição) | desligado (0) |

A cobertura representa os pontos de operação que o simulador realmente
encontra; os extremos são os piores casos de faixa e de precisão.

As configurações 5 a 8 ficam fora por padrão: elas mudam só a
modulação (QPSK) em relação às configurações 1 a 4, com os mesmos canais, a
mesma IoT e o mesmo M_c. A modulação não entra em `den`, então as matrizes têm a
mesma distribuição.

### Reprodutibilidade

O sorteio usa `--semente` (padrão 0). A mesma chamada sempre escolhe as mesmas
matrizes. A cobertura de cada (painel, SNR) tem semente própria, derivada da
semente, do painel e do SNR, então a escolha de um painel não muda quando
outros painéis entram ou saem da chamada.

## 5. Amostra gerada

Comando (padrão: configurações 1 a 4 e 9 a 16, rótulos a, b, c, e, f, 7 a 13;
100 realizações; semente 0; todas as condições de teste):

    cd hardware/testes
    ../../software/simulador/.venv/bin/python exportar_matrizes.py --amostra

ou, junto com as curvas, `software/testes/gerar_testes.sh` (amostra de
2026-10-14, 23:07). Tempo: cerca de
3 minutos por par (N, portadora).

Universo de cada par: 105.600 matrizes 16 x 16 (a, e, f, 7: 8.800 cada; c, 11, 12,
13: 17.600 cada) e 35.200 matrizes 32 x 32 (b, 8, 9, 10: 8.800 cada). Em cada par e
tamanho, a amostra tem 264 (16 x 16) ou 132 (32 x 32) matrizes de cobertura (3 por
configuração e SNR) e até 20 extremos; uma matriz pode ser extremo
de mais de uma métrica, por isso o total varia.

| Par | Tamanho | Exportadas | `max_abs_parte` | `max_abs_inversa` | `menor_autovalor` | `numero_condicao` | Parte acima de 128 |
| :-- | :-- | --: | :-- | :-- | :-- | :-- | --: |
| `amostras192_fc3.5GHz` | 16 x 16 | 283 | 11,2 a 2.978 | 0,01 a 4,68 | 0,1 a 62,2 | 21,3 a 567 | 92 |
|  | 32 x 32 | 152 | 11,9 a 2.966 | 0,014 a 6,83 | 0,082 a 51,9 | 61,5 a 1.267 | 50 |
| `amostras192_fc28GHz` | 16 x 16 | 284 | 9,01 a 3.960 | 0,011 a 4,61 | 0,11 a 58,6 | 24,7 a 641 | 92 |
|  | 32 x 32 | 152 | 12,9 a 3.947 | 0,013 a 6,91 | 0,079 a 55,6 | 61,7 a 1.290 | 50 |
| `amostras168_fc28GHz` | 16 x 16 | 284 | 9 a 3.604 | 0,0092 a 4,43 | 0,11 a 71,7 | 24,8 a 630 | 94 |
|  | 32 x 32 | 152 | 11,6 a 3.483 | 0,013 a 6,43 | 0,083 a 59,3 | 61,2 a 1.405 | 51 |
| `amostras132_fc3.5GHz` | 16 x 16 | 284 | 11,1 a 2.906 | 0,0081 a 4,25 | 0,12 a 80,6 | 19,8 a 526 | 92 |
|  | 32 x 32 | 152 | 13,1 a 2.901 | 0,011 a 6,3 | 0,085 a 72,2 | 55,2 a 1.210 | 50 |
| `amostras24_fc3.5GHz` | 16 x 16 | 281 | 10,8 a 3.720 | 0,0025 a 2,82 | 0,19 a 320 | 7,41 a 342 | 89 |
|  | 32 x 32 | 150 | 13,5 a 3.428 | 0,0026 a 3,34 | 0,18 a 354 | 19,5 a 553 | 50 |

Onde estão os extremos: faixa (`max_abs_parte`) em SNR = -10 dB; precisão
(`numero_condicao`, `max_abs_inversa`, `menor_autovalor`) em SNR = +10 dB.

Com o formato atual do hardware, `ap_fixed<16,8>` (faixa até 128), as matrizes da
última coluna têm alguma parte acima de 128. Nessas, a inversão termina em
divisão por zero, tanto no C++ quanto no `golden_cholesky.py` (que sai com
código 2). Isso é limitação do formato, não erro de validação.

## 6. Como usar com o hardware

0. Escolher o par (N, portadora): `./rodar_inversoes.sh -m 2_amostra_matrizes/amostras24_fc3.5GHz`
   roda só as matrizes desse par (cada rodada grava em `3_validacao_bits/<data-hora>/`).
1. Ajustar `CHOL_N` ao tamanho da pasta: 16 para `16x16/`, 32 para `32x32/`
   (em `parametros.env` e nas linhas `syn.cflags`/`tb.cflags` do
   `hls_config.cfg`). O script avisa quando `CHOL_N` não bate.
2. Para cada matriz: rodar o binário da C-simulation com o `.txt` e uma pasta
   de saída, e depois
   `python3 golden_cholesky.py <matriz>.txt --compare <saída>` com os mesmos
   tipos e modos do `cholesky.h`.

### Validação bit a bit (`validar_bits.sh`)

    ./validar_bits.sh            # 3_validacao_bits/validacao_<data-hora>/

1. `selecionar_matrizes.py` copia para `3_selecao_matrizes/<par>/<n>x<n>/` uma parte da
   amostra: para cada configuração, uma matriz de cobertura em cada SNR de
   `--snr` (padrão -10, -6, -2, 2, 6 e 10 dB), mais todos os extremos.
2. `rodar_inversoes.sh` roda, em cada par, a C-simulation e o
   `golden_cholesky.py`, só com a quantização e o estouro do `parametros.env`, e
   guarda os `.bits` das 8 etapas (`--manter`).
3. `inverter_no_simulador.py` inverte cada matriz pelo caminho do simulador
   (`dbp_sim.hw_inverse.make_inverter`, com o formato do `parametros.env`),
   reconstrói os bits da inversa (cada valor é múltiplo exato de 2^-F) e grava
   `sim_08_inverse.bits`. Confere que o formato montado pelo simulador é o mesmo do
   hardware (as linhas `TIPO`) e compara a inversa com a do golden e com a da
   C-simulation. Escreve `relatorio.csv` (uma linha por matriz) e `resumo.txt`.

Resultado de cada matriz: `igual` (hardware = golden nas 8 etapas e simulador =
hardware na inversa), `ambos_div0` (os três dividem por zero, porque alguma parte
passa da faixa do tipo; não testa bits) ou `divergente`.

O relatório também compara a inversa do hardware com a inversão em float64 usada
nas curvas (`np.linalg.inv`, a mesma conta do `np.linalg.solve` do BCD-MMSE): erro
máximo em LSB, erro relativo de Frobenius e a fração de partes iguais à inversa em
float64 arredondada para o tipo. Aqui não se espera igualdade de bits: a
diferença é o erro de quantização do hardware.

Formato de 64 bits: `./validar_bits.sh -e parametros_64bits.env --manter-selecao`
roda as mesmas matrizes na cópia `../cholesky_hardware_64bits/` (fontes iguais aos
de `../cholesky_hardware/`), com `ap_fixed<64,32>`. É o maior formato que o modelo
reproduz bit a bit (o `hls::sqrt` só usa o algoritmo modelado com F <= 32 e
I <= 34). Acima de 53 bits a inversa em float64 do simulador não guarda o
registrador inteiro; os bits do simulador vêm do mesmo modelo, com o formato que
o simulador montou, e o script confere que o float do simulador é a conversão
desses bits.

O simulador usa o mesmo `golden_cholesky.py` que a C-simulation tem como
referência. A validação mostra que o hardware bate com esse modelo nas 8 etapas e
que o simulador monta o mesmo formato e preserva os bits na conversão para float;
não é um terceiro modelo independente.

## 7. Outros usos do script

Exportar matrizes específicas (modo manual):

    ../../software/simulador/.venv/bin/python exportar_matrizes.py --painel a \
        --realizacoes 0-4 --snr=-10,0,10 --clusters 0,1 --condicao TDLB100-400

Sem `--condicao`, usa os valores padrão do simulador (N = 192, 3,5 GHz).

O `--snr` precisa do `=` por causa do sinal de menos. Uma nova exportação
atualiza as linhas dos mesmos arquivos no `indice.csv` e mantém as outras.

## 8. Pendências

- A pasta `2_amostra_matrizes/` (cerca de 55 MB por par (N, portadora), cinco pares) ainda
  não está no git; falta decidir se entra no repositório ou vai para o
  `.gitignore`.
- Tamanho 8 x 8: possível com o canal M = 128 já exportado e C = 16, se o módulo
  usar M_c = 8; não está nos painéis da Fig. 8, então não é exportado.
- `parametros.env` está com `CHOL_N=8`, que não serve para nenhuma das pastas.
