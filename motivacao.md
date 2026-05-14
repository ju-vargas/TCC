# Motivação do TCC: Implementação e Comparação de Métodos de Inversão de Matrizes em FPGA para Equalização Descentralizada em Sistemas Massive MIMO

---

## 1. Contexto Geral

Massive MIMO é uma tecnologia central em sistemas 5G e será ainda mais relevante em 6G, permitindo que estações base (BS) equipadas com centenas ou milhares de antenas atendam simultaneamente múltiplos usuários com alta eficiência espectral. À medida que o número de antenas cresce, o processamento centralizado de banda base torna-se inviável, pois as taxas de dados brutas entre as cadeias de radiofrequência e o hardware de processamento superam os limites das interfaces de interconexão existentes.

O artigo de Li et al. (2017) estabelece a arquitetura de **Processamento de Banda Base Descentralizado (DBP)** como solução a esse problema. O artigo de Zhao et al. (2025) estende essa arquitetura para o cenário de **ruído colorido**, presente em sistemas reais devido à interferência de células vizinhas. A operação de **inversão de matrizes** é o núcleo computacional comum a ambos os trabalhos, e sua implementação eficiente em hardware é uma lacuna explícita na literatura — lacuna que este TCC se propõe a preencher.

---

## 2. Motivação a partir do Artigo de 2017 (Li et al.)

### 2.1 A Arquitetura DBP e a Necessidade de Inversões Locais

O artigo de 2017 propõe particionar o array de antenas da BS em *C* clusters independentes, cada um com seu próprio hardware de processamento local. Isso distribui a complexidade computacional e reduz as taxas de dados de interconexão. A detecção de dados no uplink é realizada de forma descentralizada via algoritmos ADMM e Gradiente Conjugado (CG).

No algoritmo ADMM, a etapa central de processamento local (Etapa E1) corresponde a um problema de mínimos quadrados resolvido em forma fechada em cada cluster, exigindo a inversão de uma matriz local. O artigo descreve:

> *"This step corresponds to a least-squares (LS) problem that can be solved in closed form and independently on each cluster."*
>
> — Seção III-C-1

A inversão pode assumir duas formas, escolhidas pela identidade de Woodbury para minimizar o custo computacional:

> *"To reduce the amount of recurrent computations, we can precompute B⁻¹c and reuse the result in each iteration. For situations where the cluster size S is smaller than the number of users U, we can use the Woodbury matrix identity to derive the following equivalent update."*
>
> — Seção III-C-1

Isso estabelece o precedente fundamental: **inversões locais de matrizes são o núcleo computacional da detecção descentralizada**, e o pré-cômputo é a estratégia natural para amortizar esse custo ao longo das iterações.

### 2.2 A Implementação em GPU como Prova de Conceito, Não como Solução Final

O artigo implementa os algoritmos em um cluster de GPUs (Cray XC30 com GPUs Tesla K40) e é explícito sobre as limitações dessa abordagem:

> *"We emphasize these GPU cluster implementations serve as a proof-of-concept to showcase the efficacy and design scalability of DBP to large BS antenna arrays. The achieved throughputs are by no means high enough for 5G wireless systems, which is mainly a result of the relatively high interconnect latency."*
>
> — Seção VI-B, Remark 2

E aponta diretamente FPGA e ASIC como o caminho necessário:

> *"We expect that DBP achieves throughputs in the Gb/s regime if implemented on FPGA or ASIC clusters, which offer higher computing efficiency and lower interconnect latency than that of GPU clusters."*
>
> — Seção VII (Conclusions)

**Contribuição para a motivação:** Os próprios autores do artigo fundador da arquitetura DBP identificam FPGA e ASIC como o caminho necessário para implementações práticas em 5G — e nenhum dos dois artigos realiza isso. O TCC preenche exatamente essa lacuna.

### 2.3 A Métrica de Complexidade É Reconhecidamente Grosseira

Ao analisar a complexidade computacional dos algoritmos na Tabela I, o artigo admite:

> *"We ignore data-dependencies or other operations, such as additions, divisions, etc. While this complexity measure is rather crude, it enables insights into the pros and cons of decentralized baseband processing."*
>
> — Seção V-A

**Contribuição para a motivação:** Uma análise em termos de latência real em ciclos de clock, área em FPGA e representação numérica em ponto fixo é uma contribuição necessária e não redundante com o que já foi feito em 2017.

### 2.4 Cholesky como Método de Inversão na Implementação em GPU

Na descrição da implementação em GPU, o artigo revela qual método de inversão foi utilizado:

> *"We use cublasCgetrfBatched and cublasCgetriBatched to perform fast matrix inversions via the Cholesky factorization followed by forward-backward substitution."*
>
> — Seção VI-A-1

**Contribuição para a motivação:** Isso valida Cholesky como escolha natural para essa operação e mostra que em GPU são utilizadas bibliotecas prontas (cuBLAS). Em FPGA, o método precisa ser implementado explicitamente — o que abre espaço para comparar alternativas como LU e série de Neumann, e para analisar o impacto da representação em ponto fixo.

### 2.5 Eficiência Energética como Motivação Adicional para FPGA

> *"Power efficiency is another key aspect of practical BS designs. The thermal design power (TDP) of the Tesla K40 GPU used in our implementation is 235W, leading to a maximum power dissipation of C×235W with C fully-utilized GPUs. While this is a pessimistic power estimate, we expect that dedicated implementations on FPGA or ASIC will yield orders-of-magnitude better performance per watt."*
>
> — Seção VI-B, Remark 3

**Contribuição para a motivação:** Além da latência, a eficiência energética reforça a necessidade de implementações em FPGA para tornar a arquitetura DBP viável em sistemas reais.

---

## 3. Motivação a partir do Artigo de 2025 (Zhao et al.)

### 3.1 Ruído Colorido é Realista e Exige LMMSE com Covariância Completa

O artigo critica que todos os trabalhos anteriores de DBP assumem ruído branco — premissa irrealista em sistemas práticos:

> *"Prior works [...] all assumed that the BS receiver noise follows an ideal additive white Gaussian noise (AWGN) model with a diagonal covariance matrix [...] However, in practical systems, interference from other non-target UEs in neighboring cells must be modeled as part of the background noise, i.e., results in colored noise with a non-diagonal covariance matrix."*
>
> — Seção I, Introduction

E no abstract:

> *"current detection methods tailored to DBP only consider ideal white Gaussian noise scenarios, while in practice, the noise is often colored due to interference from neighboring cells."*
>
> — Abstract

**Contribuição para a motivação:** O equalizador LMMSE com covariância completa R é necessário para desempenho ótimo em cenários reais de interferência — e é justamente essa covariância que torna a inversão de matrizes mais complexa numericamente do que no artigo de 2017.

### 3.2 A Covariância Não-Diagonal Torna o Problema Difícil em DBP

O desafio central que motiva todos os métodos propostos é descrito na Seção II-B-2:

> *"only the diagonal blocks of R [...] can be locally estimated by each cluster c [...] The main challenge lies in accurately obtaining the off-diagonal blocks of R [...] the direct exchange of noise samples among DUs would result in high-dimensional data transfer with size M×N, which is prohibited for massive MIMO scenarios."*
>
> — Seção II-B-2

**Contribuição para a motivação:** A impossibilidade de trocar amostras brutas de ruído entre clusters força o projeto de novos algoritmos que propagam indiretamente a informação de covariância cruzada — todos dependendo de inversões locais de matrizes Mc×Mc que incluem a covariância empírica do ruído.

### 3.3 Onde a Inversão de Matriz Ocorre em Cada Método

#### BDAC-MMSE (baseline)
Cada cluster inverte Rcc localmente para formar HcᴴRcc⁻¹Hc, conforme a equação (7):

> *(ΣHcᴴRcc⁻¹Hc + (1/Es)I)⁻¹ [Hc₁ᴴRcc₁⁻¹, ..., HcCᴴRccC⁻¹]*
>
> — Equação (7), Seção II-B-3

#### sDR-MMSE e cDR-MMSE (arquitetura estrela)
A compressão local Qc = HcᴴRcc⁻¹ exige a inversão de Rcc em cada cluster. Nos Algoritmos 1 e 2, linha 3:

> *"Qc ← HcᴴRcc⁻¹"*
>
> — Algoritmos 1 e 2, Seção III

#### BCD-MMSE (arquitetura daisy chain)
A atualização de Wlc na equação (30) exige a inversão de (EsHcHcᴴ + (1/N)Σ nᵢcnᵢcᴴ) em cada cluster a cada iteração. O Algoritmo 3, linha 12, referencia essa equação diretamente.

> *"W∗c = (Es(IK − Σj≠c WjHj)HcH − (1/N)Σ Σj≠c Wjnᵢj(nᵢc)H) × (EsHcHcH + (1/N)Σ nᵢc(nᵢc)H)⁻¹"*
>
> — Equação (26), Seção IV-A

### 3.4 A Inversão Ocorre por Bloco de Coerência — Com Frequência Determinada pelo Padrão

O artigo é explícito sobre quando a inversão precisa ser refeita:

> *"We assume that the channel and noise covariance remain static across Ncoh contiguous symbols. This means that the equalization matrix and covariance estimation can be reused for different symbols, although they will change with every coherence block."*
>
> — Seção V-B

Os parâmetros do pior caso em 5G NR são definidos como:

> *"Nu = 3300, NPRB = 275, Nsc,PRB = 12 and TOFDM = 1/120KHz"*
>
> — Seção VI-D

Com espaçamento de subportadora de 120 KHz (numerologia µ=3 do 5G NR), o tempo de símbolo OFDM é aproximadamente **8,9 µs**, definindo um deadline apertado para a inversão. No artigo de 2017, com LTE de 20 MHz e Nsym = 7 símbolos por slot, o deadline é de aproximadamente **71 µs por símbolo** dentro de um slot de 0,5 ms.

### 3.5 O Condicionamento Numérico Varia com o Cenário de Interferência

> *"The interference over thermal (IoT) is used to measure the intensity of interference relative to background noise [...] Large IoT leads to significant interference, i.e., the off-diagonal elements of the noise covariance matrix are more prominent."*
>
> — Seção VI-A

E os resultados com IoT = 20 dB mostram degradação de desempenho de todos os equalizadores:

> *"Fig. 8(f) shows SER performance under IoT = 20 dB, where the performance of all equalizers is significantly degraded due to stronger interference in colored noise."*
>
> — Seção VI-C

**Contribuição para a motivação:** O número de condição da matriz invertida varia com o cenário de interferência. Isso torna a escolha do método de inversão e da representação numérica não trivial — e justifica a comparação entre métodos e entre ponto fixo e ponto flutuante.

### 3.6 Nenhuma Implementação em Hardware Foi Realizada

A análise de complexidade na Seção V é inteiramente em termos de operações aritméticas (O(Mc³), etc.), sem qualquer discussão de latência em ciclos de clock, área em FPGA ou representação numérica. As direções de trabalho futuro são:

> *"Future work includes extending our decentralized equalization methods to other decentralized architectures such as cell-free massive MIMO systems. Additionally, deep learning techniques may help mitigate bandwidth and computation limitations in our design."*
>
> — Seção VII (Conclusion)

**Contribuição para a motivação:** Implementação em hardware não é mencionada como trabalho futuro — a lacuna existe mas não foi sequer identificada pelos autores. Qualquer resultado nessa direção é uma contribuição genuinamente nova.

---

## 4. A Operação Escolhida e sua Justificativa

### 4.1 Qual operação

A operação alvo é a **inversão (ou fatoração equivalente) de matrizes hermitianas positivas definidas de tamanho Mc×Mc**, que ocorre localmente em cada cluster em todos os métodos de equalização descentralizada propostos no artigo de 2025.

### 4.2 Por que essa operação é mais relevante em 2025 do que em 2017

| Aspecto | Artigo de 2017 | Artigo de 2025 |
|---|---|---|
| Matriz invertida | (HcHcᴴ + ρI) | (EsHcHcᴴ + (1/N)Σ nᵢcnᵢcᴴ) |
| Componentes | Apenas canal Hc e escalar ρ | Canal Hc e covariância empírica do ruído |
| Condicionamento | Garantido por ρI (fixo) | Depende do IoT (variável por cenário) |
| Atualização | Apenas Hc muda por bloco de coerência | Hc e covariância do ruído mudam por bloco |
| Complexidade numérica | Simples, bem condicionada | Potencialmente mal condicionada com IoT alto |
| Deadline (LTE/5G NR) | ~71 µs (LTE, slot de 0,5 ms) | ~8,9 µs (5G NR, µ=3) |

No artigo de 2017, a matriz é estruturalmente simples e bem condicionada por construção. No artigo de 2025, a inclusão da covariância empírica do ruído torna a matriz numericamente mais desafiadora e variável entre blocos de coerência — justificando a análise de métodos de inversão e representação numérica que o TCC propõe.

### 4.3 Em quais métodos a inversão ocorre

A tabela a seguir resume todas as inversões nos dois artigos:

| Método | Artigo | Arquitetura | Matriz invertida | Dimensão | Complexidade | Quando ocorre | Bloco de coerência | Local ou Central |
|---|---|---|---|---|---|---|---|---|
| ADMM-UL (S≤U) | 2017 | Estrela | (HcHcᴴ + ρIs) | S×S | O(S³) | Pré-cômputo, uma vez por bloco | Nsym=7, Nsc=1200, LTE 20MHz | Local |
| ADMM-UL (S>U) | 2017 | Estrela | (HcᴴHc + ρIu) | U×U | O(U³) | Pré-cômputo, uma vez por bloco | Idem | Local |
| ADMM-DL (S≤U) | 2017 | Estrela | (HcᴴHc + ρ⁻¹Is) | S×S | O(S³) | Pré-cômputo, uma vez por bloco | Idem | Local |
| ADMM-DL (S>U) | 2017 | Estrela | (HcHcᴴ + ρ⁻¹Iu) | U×U | O(U³) | Pré-cômputo, uma vez por bloco | Idem | Local |
| CG-UL | 2017 | Estrela | Nenhuma | — | — | — | Idem | — |
| BDAC-MMSE (local) | 2025 | Estrela e Daisy chain | Rcc | Mc×Mc | O(Mc³) | Uma vez por bloco | Ncoh símbolos; 5G NR: TOFDM=1/120KHz | Local |
| BDAC-MMSE (central) | 2025 | Estrela e Daisy chain | (ΣHcᴴRcc⁻¹Hc + (1/Es)I) | K×K | O(K³) | Uma vez por bloco | Idem | Central |
| sDR-MMSE (local) | 2025 | Estrela | Rcc | Mc×Mc | O(Mc³) | Uma vez por bloco | Idem | Local |
| sDR-MMSE (central) | 2025 | Estrela | HˇᴴRˇ⁻¹Hˇ + (1/Es)I | K×K | O(K³) | Uma vez por bloco | Idem | Central (CU) |
| cDR-MMSE (local) | 2025 | Estrela | Rcc | Mc×Mc | O(Mc³) | Uma vez por bloco | Idem | Local |
| cDR-MMSE (central) | 2025 | Estrela | H˜ᴴR˜⁻¹H˜ + (1/Es)I | CK×CK | O(C³K³) | Uma vez por bloco | Idem | Central (CU) |
| BCD-MMSE | 2025 | Daisy chain | (EsHcHcᴴ + (1/N)Σnᵢcnᵢcᴴ) | Mc×Mc | O(Mc³) fatoração + O(Mc²)/iteração | Fatoração uma vez por bloco; substituição por iteração | Idem | Local |
| BCD-MMSE (LRD) | 2025 | Daisy chain | (EsHcHcᴴ + GcGcᴴ) | Mc×Mc | O(Mc³) fatoração + O(Mc²)/iteração | Fatoração uma vez por bloco; substituição por iteração | Idem | Local |

---

## 5. Proposta do TCC

### 5.1 Objetivo

Implementar e comparar em FPGA três métodos de inversão de matrizes — **Cholesky**, **LU** e **Série de Neumann** — para a operação Mc×Mc presente em todos os equalizadores descentralizados do artigo de 2025, sob representação em **ponto fixo** e **ponto flutuante**, avaliando latência, área e impacto no BER do sistema.

### 5.2 Parâmetros do sistema alvo

Os valores de Mc relevantes, extraídos diretamente das simulações do artigo de 2025, são Mc = 16 (para M=128, C=8 ou M=256, C=16) e Mc = 32 (para M=256, C=8). O número de usuários é K = 8.

### 5.3 Deadline de hardware

Com clock de 200 MHz em FPGA Xilinx:

- **LTE (artigo de 2017):** deadline ≈ 71 µs → até **14.200 ciclos** disponíveis
- **5G NR µ=3 (artigo de 2025):** deadline ≈ 8,9 µs → até **1.780 ciclos** disponíveis

### 5.4 Lacuna preenchida

Nenhum dos dois artigos analisa a implementação em hardware da inversão de matrizes no contexto DBP. O artigo de 2017 aponta FPGA como necessário mas não implementa. O artigo de 2025 introduz uma inversão mais complexa numericamente mas não analisa hardware nem representação numérica. O TCC fecha essa lacuna dupla, produzindo um resultado diretamente aplicável à implementação prática dos equalizadores propostos em 2025.

---

## 6. Referências Base

- K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," *IEEE Journal on Emerging and Selected Topics in Circuits and Systems*, vol. 7, no. 4, pp. 491–507, Dec. 2017.

- X. Zhao, M. Li, B. Wang, E. Song, T.-H. Chang, and Q. Shi, "Efficient LMMSE equalization for massive MIMO systems under decentralized baseband processing architecture," *IEEE Journal on Selected Areas in Communications*, vol. 43, no. 3, pp. 736–751, Mar. 2025.