# PAPER LOG
Title: Decentralized Equalization With Feedforward Architectures for Massive MU-MIMO

Authors: Charles Jeon, Kaipeng Li, Joseph R. Cavallaro, Christoph Studer

Venue / Year: IEEE Transactions on Signal Processing / 2019

DOI: 10.1109/TSP.2019.2928947

Pillar:  [ B - equalization matrix ]

Priority: [ 1 ] 

## SETTING
  * Antennas (M): B (total BS antennas), partitioned into C clusters each with B_c = w_c · B antennas

  * Users (K or U): U single-antenna UEs
  
  * Noise model:
  n ∈ C^B is i.i.d. circularly symmetric complex Gaussian noise
  with variance N_0 per complex entry.

  * Channel Model: Rayleigh fading — H ∈ C^{B×U} with i.i.d. CN(0, 1/B) entries. SINR analysis is conducted in the large-system limit, fixing β = U/B as U, B → ∞.

  * DBP architecture: Feedforward (one-shot message passing; no iterative consensus exchange among clusters)
  
  * Topology: C independent antenna clusters, each with local RF and CHEST. Results fused at a master/centralized unit via a feedforward adder tree (PD) or fusion tree (FD).



## KEY TECHNIQUE

O paper propõe duas **feedforward architectures** para

PD: Partially decentralized equalization

FD: Fully decentralized equalization


Para ambas arquiteturas, investiga a eficácia da equalização utilizando os algoritmos:
* MRC
* ZF
* L-MMSE 
* LAMA (Large-MIMO approximate message passing)


### Arquitetura PD 

**Passo 1**: 
Cada cluster calcula paralelamente:

* U-dimensional local MRC vector $\mathbf{y}^\text{MRC}_c = \mathbf{H}^H_c \mathbf{y}_c$
* U×U local Gram matrix $\mathbf{G}_c = \mathbf{H}^H_c \mathbf{H}_c$

**Passo 2**: 
_Feedforward_ adder tree (operador ⊕) calcula os vetores completos:

$$
\mathbf{y}^\text{MRC} = \sum_{c=1}^C \mathbf{y}^\text{MRC}_c \quad \text{and} \quad \mathbf{G} = \sum_{c=1}^C \mathbf{G}_c \tag{4}
$$

**Passo 3**: 
Equalização linear ou não linear na unidade centralizada para calcular a tupla de saída:
* estimativa $\mathbf{z} \in \mathbb{C}^U$
* post-equalization error variance vector $\boldsymbol{\sigma}^2 \in \mathbb{C}^U$

> **Observação de interconexão:** A PD transmite para a unidade central tanto $\mathbf{y}^\text{MRC}_c$ (U-dimensional) quanto $\mathbf{G}_c$ (U×U), resultando em um tamanho de mensagem total $m_\text{PD} = U^2 \times N_{sc} \times C + U \times N_{sc} \times N_{sym} \times C$. Esta é a arquitetura equivalente à **star topology**: todos os clusters enviam dados a um nó central (master GPU).


#### Equalization Algorithms (PD)

Todos operam sobre $\mathbf{y}^\text{MRC}$ e $\mathbf{G}$ na unidade centralizada.

**MRC:**

$$
\mathbf{z}^\text{MRC} = \operatorname{diag}(\mathbf{G})^{-1} \mathbf{y}^\text{MRC}
$$

Error variance:

$$
\boldsymbol{\sigma}^2_\text{MRC} = \operatorname{diag}\!\left(\operatorname{diag}(\mathbf{G})^{-1} \mathbf{G}\, \operatorname{diag}(\mathbf{G})^{-H} N_0 + \left(\operatorname{diag}(\mathbf{G})^{-1}\mathbf{G} - \mathbf{I}_U\right)\!\left(\operatorname{diag}(\mathbf{G})^{-1}\mathbf{G} - \mathbf{I}_U\right)^H E_s\right)
$$

> Inversão envolvida: diagonal de G (U inversões escalares); sem inversão de matriz densa.

**ZF:**

$$
\mathbf{z}^\text{ZF} = \mathbf{G}^{-1} \mathbf{y}^\text{MRC}
$$

Error variance:

$$
\boldsymbol{\sigma}^2_\text{ZF} = \operatorname{diag}(\mathbf{G}^{-1})\, N_0
$$

> Inversão envolvida: $\mathbf{G}^{-1}$, dimensão U×U, Hermitiana positiva definida.

**L-MMSE:**

$$
\mathbf{z}^\text{L\text{-}MMSE} = \left(\mathbf{G} + \rho\, \mathbf{I}_U\right)^{-1} \mathbf{y}^\text{MRC}, \quad \rho = N_0/E_s
$$

Error variance:

$$
\boldsymbol{\sigma}^2_\text{L\text{-}MMSE} = \operatorname{diag}\!\left(\left(\mathbf{G}+\rho\mathbf{I}_U\right)^{-1}\mathbf{G}\left(\mathbf{G}+\rho\mathbf{I}_U\right)^{-H} N_0 + \left(\left(\mathbf{G}+\rho\mathbf{I}_U\right)^{-1}\mathbf{G} - \mathbf{I}_U\right)\!\left(\left(\mathbf{G}+\rho\mathbf{I}_U\right)^{-1}\mathbf{G} - \mathbf{I}_U\right)^H E_s\right)
$$

> Inversão envolvida: $(\mathbf{G} + \rho\mathbf{I}_U)^{-1}$, dimensão U×U, Hermitiana positiva definida.

**LAMA-PD** (Algorithm 1 — opera sobre $\mathbf{y}^\text{MRC}$ e $\mathbf{G}$):

Inicializar $s_\ell = \mathbb{E}_S[S]$, $\phi^{(1)} = \operatorname{Var}_S[S]$, $\mathbf{v}^{(1)} = \mathbf{0}$. Para cada iteração $t$:

$$
\mathbf{z}^t = \mathbf{y}^\text{MRC} + (\mathbf{I} - \mathbf{G})\mathbf{s}^t + \mathbf{v}^t
$$
$$
\mathbf{s}^{t+1} = \mathrm{F}\!\left(\mathbf{z}^t,\, N_0 + \beta\phi^t\right)
$$
$$
\phi^{t+1} = \left\langle \mathrm{G}\!\left(\mathbf{z}^t,\, N_0 + \beta\phi^t\right) \right\rangle
$$
$$
\mathbf{v}^{t+1} = \frac{\beta\phi^{t+1}}{N_0 + \beta\phi^t}\left(\mathbf{z}^t - \mathbf{s}^t\right) \tag{8}
$$

> Sem inversão de matriz; operações de multiplicação matriz-vetor e operações vetoriais. Saída: $\mathbf{z}^t$ e $\sigma^2_{t,\text{LAMA}} = N_0 + \beta\phi^t$.


#### SINR Analysis — PD Architecture (Corollary 2, Theorem 1)

A análise usa o large-system limit ($\beta = U/B$, $U,B \to \infty$) e canais Rayleigh fading. O SINR é definido como $\text{sinr} \triangleq E_s / \sigma^2$, onde $\sigma^2$ é a decoupled noise variance solução da fixed-point equation $\sigma^2_\text{PD} = N_0 + \beta\,\Psi(\sigma^2_\text{PD})$.

Closed-form expressions (Corollary 2):

$$
\text{sinr}^\text{MRC}_\text{PD} = \frac{E_s/N_0}{1 + \beta\,E_s/N_0}
$$

$$
\text{sinr}^\text{ZF}_\text{PD} = \frac{E_s}{N_0}(1 - \beta), \quad \text{para } \beta < 1
$$

$$
\text{sinr}^\text{L\text{-}MMSE}_\text{PD} = \frac{1}{2}\left(\sqrt{\left(1 - \frac{E_s}{N_0}(1-\beta)\right)^2 + 4\frac{E_s}{N_0}} - \left(1 - \frac{E_s}{N_0}(1-\beta)\right)\right)
$$

Para LAMA-PD: $\sigma^2$ rastreado pela state evolution recursion $\sigma^2_t = N_0 + \beta\,\Psi(\sigma^2_{t-1})$ com MSE function $\Psi(\sigma^2) = \mathbb{E}_{S,Z}\!\left[|\mathrm{F}(S + \sigma_{t-1}Z, \sigma^2_{t-1}) - S|^2\right]$ (Theorem 3). Sem expressão fechada; calculado numericamente.

> **O desempenho PD é idêntico ao centralizado** para MRC, ZF, L-MMSE e LAMA-PD, pois $\mathbf{y}^\text{MRC}$ é estatística suficiente para $\mathbf{s}_0$.


### Arquitetura FD 

**Passo 1**: Cada cluster em paralelo executa CHEST, preprocessing e equalization:

* Gera estimativa local $\mathbf{z}_c \in \mathbb{C}^U$
* Gera local post-equalization error variance vector $\boldsymbol{\sigma}^2_c \in \mathbb{C}^U$

**Passo 2**: _Feedforward_ fusion tree (operador •) combina as estimativas locais $\mathbf{z}_c$ usando $\boldsymbol{\sigma}^2_c$ para gerar a tupla de saída $\{\mathbf{z}, \boldsymbol{\sigma}^2\}$.

> **Observação de interconexão:** A FD transmite apenas $\mathbf{z}_c$ (U-dimensional) e $\boldsymbol{\sigma}^2_c$ (U-dimensional) — não transmite as matrizes de Gram locais. Tamanho de mensagem total $m_\text{FD} = U \times N_{sc} \times N_{sym} \times C$, que é substancialmente menor que $m_\text{PD}$.


#### Nodo de fusão (Lemma 4, Eq. 13 e 19)

A fusão é linear ponderada por UE:

$$
z_u = \sum_{c=1}^C \nu_{c,u}\, z_{c,u}, \quad u = 1, \ldots, U \tag{12}
$$

com pesos ótimos (maximizam o SINR pós-fusão sujeito a $\sum_c \nu_{c,u} = 1$):

$$
\nu_{c,u} = \frac{1/\sigma^2_{c,u}}{\displaystyle\sum_{c'=1}^C 1/\sigma^2_{c',u}} \tag{13/19}
$$

> **Sem inversão de matriz densa** no nodo de fusão: apenas U inversões escalares ($1/\sigma^2_{c,u}$) e somas. A fusão é uma média harmônica ponderada por UE.

A decoupled noise variance pós-fusão é (Theorem 6):

$$
\sigma^2_\text{FD} = \left(\sum_{c=1}^C \frac{1}{\sigma^2_c}\right)^{-1} = N_0 + \beta \sum_{c=1}^C \nu_c\,\Psi(\sigma^2_c) \tag{14}
$$

A per-cluster decoupled noise variance $\sigma^2_c$ satisfaz a fixed-point equation (Lemma 5):

$$
w_c\,\sigma^2_c = N_0 + \beta\,\Psi(\sigma^2_c)
$$


#### Equalization Algorithms (FD)

Cada cluster $c$ opera sobre seu par local $(\mathbf{y}_c, \mathbf{H}_c)$ e computa localmente as mesmas estimativas. As equações de equalização são as mesmas da PD, mas aplicadas ao sub-sistema local de dimensão $B_c \times U$.

**MRC local:** $\mathbf{z}^\text{MRC}_c = \operatorname{diag}(\mathbf{G}_c)^{-1} \mathbf{y}^\text{MRC}_c$, com $\sigma^2_c$ dado por Lemma 5 com $\Psi(\sigma^2) = E_s$.

**ZF local:** $\mathbf{z}^\text{ZF}_c = \mathbf{G}_c^{-1} \mathbf{y}^\text{MRC}_c$, com $\sigma^2_c$ dado por Lemma 5 com $\Psi(\sigma^2) = \sigma^2$. Requer $w_c > \beta$ (sub-sistema local sobredeterminado).

**L-MMSE local:** $\mathbf{z}^\text{L\text{-}MMSE}_c = (\mathbf{G}_c + \rho\mathbf{I}_U)^{-1} \mathbf{y}^\text{MRC}_c$, com $\sigma^2_c$ dado por Lemma 5 com $\Psi(\sigma^2) = \frac{E_s}{E_s + \sigma^2}\sigma^2$.

**LAMA-FD:** Algorithm 1 executado localmente em cada cluster sobre $\mathbf{y}^\text{MRC}_c$ e $\mathbf{G}_c$; saídas $\mathbf{z}_c$ e $\sigma^2_{c} = N_0 + \beta\phi^t$ são enviadas ao nodo de fusão.

> Em todos os casos da FD, a inversão de matriz local é de dimensão U×U (igual à PD), mas acontece em C clusters em paralelo em vez de em uma unidade central.


#### SINR Analysis — FD Architecture

Para ZF (Lemma 8, com $w_c \geq \beta$ para todo $c$):

$$
\text{sinr}^\text{ZF}_\text{FD} = \frac{E_s}{N_0}(1 - C\beta) \tag{15}
$$

Para L-MMSE (Lemma 9):

$$
\text{sinr}^\text{L\text{-}MMSE}_\text{FD} = \frac{1}{2}\sum_{c=1}^C \sqrt{\left(1 - \frac{E_s}{N_0}(w_c - \beta)\right)^2 + 4\frac{E_s}{N_0}w_c} - \frac{1}{2}\left(C - \frac{E_s}{N_0}(1-C\beta)\right) \tag{16}
$$

Com distribuição uniforme de antenas ($w_c = 1/C$), o lower bound (Lemma 11) é:

$$
\text{sinr}^\text{L\text{-}MMSE}_\text{FD} \geq \frac{1}{2}\sqrt{\left(1 - \frac{E_s}{N_0}(1-C\beta)\right)^2 + 4\frac{E_s}{N_0}C} - \frac{1}{2}\left(C - \frac{E_s}{N_0}(1-C\beta)\right) \tag{17}
$$

Para MRC: $\text{sinr}^\text{MRC}_\text{FD} = \text{sinr}^\text{MRC}_\text{PD}$ (Lemma 7).

Para LAMA-FD: calculado numericamente via state evolution com $w_c\sigma^2_c = N_0 + \beta\Psi(\sigma^2_c)$ e Theorem 6.

**Ordenamento geral (Lemma 7):** $\text{sinr}_\text{FD} \leq \text{sinr}_\text{PD}$ para todo equalizer. Igualdade somente para MRC, $\beta \to 0$, ou $C=1$.

**Particionamento ótimo para L-MMSE FD (Lemma 10):** Concentrar todas as antenas em um único cluster ($w_c = 1$ para algum $c$) — trivialmente indesejável. Clusters uniformes ($w_c = 1/C$) são os piores, mas ainda superam ZF em termos de SINR (Lemma 9 vs. Lemma 8).


## JUSTIFICATION
  (theorem / simulation / approximation bound)

- **Teoremas analíticos** (Corollary 2, Lemmas 4–11, Theorem 6): provam expressões fechadas ou fixed-point equations para o SINR no large-system limit com canais Rayleigh fading.
- **Simulações de SER** (Fig. 3): validam as expressões assintóticas em sistema finito com $B=256$, $U=16$, $C=8$.
- **Simulações de PER em sistema LTE-like** (Fig. 4): $B=64$, $U=16$, $C=2$, canal WINNER II outdoor-to-indoor, OFDM 16-QAM, código convolucional rate-5/6.
- **Resultados de implementação em multi-GPU** (Tables I–III): latência e throughput medidos na plataforma Nvidia DGX-1 (8× Tesla V100, NvLink 300 GB/s).

Esse artigo é construído a partir do artigo que propõe Decentralized Baseband Processing em 2017 [Li et al., JETCAS 2017]. A motivação central é que os métodos iterativos de consensus-sharing daquele trabalho apresentam latência de transferência que limita o throughput ("implementation results on a GPU cluster revealed that the transfer latency of such consensus-sharing methods are limiting the achievable throughput").

Objetivo: mitigar gargalos de interconexão, I/O, latência e computation via arquiteturas feedforward (one-shot, não-iterativas).


## LIMITATION / OPEN PROBLEM

- **Ruído AWGN assumido (i.i.d. CN(0, N_0)):** toda a análise de SINR e a estrutura das matrizes de equalização pressupõem covariância de ruído diagonal (N_0 · I). Sob ruído colorido (inter-cell interference, pilot contamination), a decomposição da matriz de Gram por clusters deixa de ser válida, e o modelo de equalização proposto não se aplica diretamente.
- **Sem análise de implementação em FPGA/ASIC:** os resultados de referência são em GPU (floating-point). O paper reconhece que implementações em FPGA ou ASIC são o alvo prático mas não as fornece.
- **Sem análise de aritmética de ponto fixo:** word lengths, condition numbers, ou degradação de BER por quantização não são investigados.
- **Canal Rayleigh i.i.d.:** a análise de SINR usa a large-system limit com entradas i.i.d. CN(0,1/B); canais com correlação espacial (e.g., mmWave, canais direcionais) são apontados como trabalho futuro.
- **Inversão U×U não investigada para hardware:** o paper usa inversão de $\mathbf{G}$ ou $(\mathbf{G}+\rho\mathbf{I}_U)$ de dimensão U×U sem discutir qual família de inversão é adequada para implementação eficiente.


## QUOTE (if needed — max 1 per paper, under 15 words)

"feedforward architectures that minimize the transfer latency"


## CONNECTION TO YOUR WORK

Este paper estabelece a forma exata das matrizes de equalização (inversão U×U de $\mathbf{G}$ ou $(\mathbf{G}+\rho\mathbf{I}_U)$) que seu projeto FPGA deve implementar na arquitetura PD, mas não aborda a validade dessas estruturas sob ruído colorido nem a implementação em hardware de ponto fixo.


## PAPER SPECIFIC QUESTIONS

### Forma da matriz de equalização em cada cluster e o que é enviado ao nodo de fusão

| Algoritmo | Arq. PD — computa no cluster | Arq. PD — envia ao centro | Arq. FD — computa no cluster | Arq. FD — envia ao nodo de fusão |
|---|---|---|---|---|
| MRC | $\mathbf{y}^\text{MRC}_c$, $\mathbf{G}_c$ | $\mathbf{y}^\text{MRC}_c$ (U×1), $\mathbf{G}_c$ (U×U) | $\mathbf{z}^\text{MRC}_c = \operatorname{diag}(\mathbf{G}_c)^{-1}\mathbf{y}^\text{MRC}_c$, $\boldsymbol{\sigma}^2_c$ | $\mathbf{z}_c$ (U×1), $\boldsymbol{\sigma}^2_c$ (U×1) |
| ZF | $\mathbf{y}^\text{MRC}_c$, $\mathbf{G}_c$ | $\mathbf{y}^\text{MRC}_c$ (U×1), $\mathbf{G}_c$ (U×U) | $\mathbf{z}^\text{ZF}_c = \mathbf{G}_c^{-1}\mathbf{y}^\text{MRC}_c$, $\boldsymbol{\sigma}^2_c$ | $\mathbf{z}_c$ (U×1), $\boldsymbol{\sigma}^2_c$ (U×1) |
| L-MMSE | $\mathbf{y}^\text{MRC}_c$, $\mathbf{G}_c$ | $\mathbf{y}^\text{MRC}_c$ (U×1), $\mathbf{G}_c$ (U×U) | $\mathbf{z}^\text{L-MMSE}_c = (\mathbf{G}_c+\rho\mathbf{I})^{-1}\mathbf{y}^\text{MRC}_c$, $\boldsymbol{\sigma}^2_c$ | $\mathbf{z}_c$ (U×1), $\boldsymbol{\sigma}^2_c$ (U×1) |
| LAMA | $\mathbf{y}^\text{MRC}_c$, $\mathbf{G}_c$ | $\mathbf{y}^\text{MRC}_c$ (U×1), $\mathbf{G}_c$ (U×U) | Executa Algorithm 1 localmente; $\mathbf{z}^t_c$, $\sigma^2_c$ | $\mathbf{z}_c$ (U×1), $\boldsymbol{\sigma}^2_c$ (U×1) |

### Operação de fusão na unidade central (por algoritmo)

| Algoritmo | Arq. PD — operação central | Inversão? Dimensão? | Arq. FD — operação de fusão | Inversão? |
|---|---|---|---|---|
| MRC | $\mathbf{z} = \operatorname{diag}(\mathbf{G})^{-1}\mathbf{y}^\text{MRC}$ | Inversão diagonal: U escalares | Média ponderada $\nu_{c,u} = (1/\sigma^2_{c,u})/\sum_{c'}(1/\sigma^2_{c',u})$ | Não; apenas U inversões escalares |
| ZF | $\mathbf{z} = \mathbf{G}^{-1}\mathbf{y}^\text{MRC}$ | **Inversão densa U×U** (HPD) | Idem MRC fusion | Não |
| L-MMSE | $\mathbf{z} = (\mathbf{G}+\rho\mathbf{I}_U)^{-1}\mathbf{y}^\text{MRC}$ | **Inversão densa U×U** (HPD) | Idem MRC fusion | Não |
| LAMA | Algoritmo 1 completo sobre $\mathbf{y}^\text{MRC}$, $\mathbf{G}$ (sem inversão explícita) | Não | Idem MRC fusion | Não |

### Performance Benchmarks (GPU — Table I, $U=16$, $B_c=32$)

| Equalizer | PD: Latência / Throughput ($C=2/4/8$) | FD: Latência / Throughput ($C=2/4/8$) |
|---|---|---|
| LAMA ($T_\text{max}=1$) | 0.651/1.76 — 0.677/1.69 — 0.785/1.46 ms/Gb/s | 0.591/1.94 — 0.599/1.91 — 0.672/1.71 ms/Gb/s |
| L-MMSE | 0.719/1.60 — 0.745/1.54 — 0.856/1.34 ms/Gb/s | 0.666/1.72 — 0.676/1.70 — 0.751/1.53 ms/Gb/s |
| ZF | 0.690/1.66 — 0.717/1.61 — 0.827/1.39 ms/Gb/s | 0.635/1.81 — 0.643/1.79 — 0.715/1.61 ms/Gb/s |
| MRC | 0.411/2.79 — 0.421/2.72 — 0.499/2.30 ms/Gb/s | 0.411/2.79 — 0.421/2.72 — 0.499/2.30 ms/Gb/s |

FD atinge throughput maior que PD (menor volume de mensagens); ambas superam os métodos consensus-sharing de [8] (D-ADMM/D-CG < 1.47 Gb/s para $T_\text{max}=2$).

### As duas arquiteturas feedforward — interconexão e correspondência à topologia star

- **PD ↔ Star topology:** cada cluster envia $\mathbf{y}^\text{MRC}_c$ e $\mathbf{G}_c$ a um único nó central (master GPU), que realiza toda a equalização. Volume de mensagem: $m_\text{PD} = U^2 \times N_{sc} \times C + U \times N_{sc} \times N_{sym} \times C$. Para $N_{sc}=1200$, $N_{sym}=14$, $U=16$, $C=4$: $m_\text{PD} = 17.58$ MB.
- **FD:** cada cluster envia apenas $\mathbf{z}_c$ e $\boldsymbol{\sigma}^2_c$ ao master. Volume: $m_\text{FD} = U \times N_{sc} \times N_{sym} \times C$ — para os mesmos parâmetros: $m_\text{FD} = 8.20$ MB (metade de $m_\text{PD}$). Consensus-sharing de [8] requer $m_\text{CS} = 2\,m_\text{FD}$ **por iteração**.

### Suposição de AWGN — onde aparece

A suposição de ruído i.i.d. CN(0, N_0) (AWGN) aparece em **dois lugares distintos**:

1. **Estrutura da matriz de equalização:** a forma $(\mathbf{G} + \rho\mathbf{I}_U)^{-1}$ com $\rho = N_0/E_s$ é a equação L-MMSE *somente* quando a covariância do ruído é $N_0\mathbf{I}_B$ (diagonal). Sob ruído colorido com covariância $\mathbf{R} \neq N_0\mathbf{I}$, o equalizador MMSE ótimo tem forma diferente e não se fatora por clusters.

2. **Expressões de SINR (large-system limit):** Theorem 1 (Tse-Hanly) e todos os Corollaries/Lemmas subsequentes pressupõem canais AWGN decoupled após a large-system limit, o que requer a diagonal dominance garantida por $N_0\mathbf{I}$. Sob ruído colorido, os canais não decouplam na forma escalar de (5), e as fixed-point equations não são válidas.