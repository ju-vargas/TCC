# PAPER LOG
 ---
Title: Decentralized Massive MIMO Systems: Is There Anything to be Discussed?

Authors: Jesús Rodríguez Sánchez, Juan Vidal Alegría, Fredrik Rusek

Venue / Year: IEEE International Symposium on Information Theory (ISIT), Paris / 2019

DOI: não fornecido no paper

Pillar: [**B — equalization matrix**] *(contribuição ao pilar B é estreita e estrutural; v. advertência abaixo)*

Priority: [ 1 ]

> ⚠️ **ADVERTÊNCIA DE ESCOPO:** Este é um paper difícil de enquadrar. A maior parte do conteúdo — "a hefty share of the paper is devoted to (iv)" — trata de estimação de canal da matriz de Gram a partir de observações ruidosas (estimadores ML, MAP, MMSE para G via distribuição de Wishart não-central). Essa seção está **fora do escopo** do projeto. O que está **em escopo** é restrito e preciso: o argumento estrutural de que inversão de matriz K×K é inevitável em ZF mesmo em um sistema totalmente descentralizado onde nenhum nó possui a matriz de canal completa (feature (v) do abstract). Adicionalmente: o termo "MMSE" neste paper **não designa o equalizador L-MMSE** — designa o estimador MMSE da matriz de Gram G a partir da observação ruidosa R. Este ponto é crítico para não confundir com a literatura Li/Studer/Jeon.


## SETTING

  * **Antennas (M):** M antenas na BS (experimentos: M = 100)
  * **Users (K or U):** K UEs com antena única (experimentos: K = 16); notação K neste paper (equivale a U nos papers Li/Studer/Jeon)
  * **Noise model:** n ~ CN(0, N_0 * I) — ruído AWGN i.i.d. em toda a análise. Durante estimação de canal, a covariância de ruído de piloto é Σ = N_0 * I (pilotos de igual potência, |p_k| = 1 para todo k). Não há análise de ruído colorido em nenhuma seção.
  * **DBP architecture:** Arquitetura descentralizada própria do grupo Sánchez/Rusek/Lund — **sem conceito de cluster**. Cada antena processa individualmente: estimação LS local, contribuição de rank-1 para a matriz de Gram, filtragem casada local. Central node (CU): recebe a Gram agregada R e os vetores MRC agregados; realiza estimação de G e inversão K×K.
  * **Topology:** Star implícita — cada antena conectada ao CU; sem comunicação inter-antenas ("there is no inter-communication among antennas"). Sem topologia daisy chain neste paper. O próprio primeiro autor (Sánchez) é co-autor dos papers de daisy chain [6,7] citados nas referências, mas este paper apresenta uma abordagem **distinta** daquela.


## KEY TECHNIQUE

O paper propõe uma arquitetura descentralizada em que a fase de dados (payload) e a fase de treinamento (training) compartilham o mesmo hardware de interconexão. Durante a fase de payload, cada antena $m$ computa o produto interno local $\mathbf{w}_m = \mathbf{h}_m^* \cdot y_m$ (filtragem casada local, K×1) e os M resultados são somados no CU. Durante os K slots de treinamento não utilizados para payload, cada antena computa a contribuição de rank-1 $\mathbf{R}_m = \hat{\mathbf{h}}_m^* \hat{\mathbf{h}}_m^T$ (K×K), e a soma $\mathbf{R} = \sum_{m=1}^M \mathbf{R}_m$ é acumulada e transferida ao CU via K transmissões de K×1 vetores — mesma capacidade de transmissão já necessária para o payload. No CU, a tarefa restante é inversão de $\hat{\mathbf{G}}$ (K×K) e multiplicação do vetor MRC agregado. A contribuição em escopo do projeto está no argumento estrutural de que essa inversão K×K é **irredutível** em qualquer esquema ZF descentralizado que respeite a definição do paper — ela não pode ser eliminada do CU, apenas reduzida em dimensão (K×K, independente de M). A seção majoritária do paper deriva estimadores ML, MAP e MMSE para G a partir da distribuição posterior de G|R (Wishart não-central), que está fora do escopo do projeto.


## JUSTIFICATION

  * **Argumento estrutural (Seção III):** demonstração construtiva de que a transferência da Gram K×K reutiliza exatamente a capacidade de interconexão já necessária para payload, sem aumento de banda. Argumento lógico, não simulação.
  * **Análise de erro de estimação (Fig. 1 — fora de escopo):** erro relativo de estimação ε_Q vs. nível de ruído N_0 para estimadores LS e MMSE de G; M=100, K=16. Fora do escopo do projeto.
  * **Simulação de sum-rate (Fig. 2 — fora de escopo):** taxa ergódica vs. K/M para ZF com estimadores LS e MMSE de G; M=100, SNR no receptor. Fora do escopo do projeto.
  * **Conclusão principal:** o paper conclui que a inversão K×K no CU é de complexidade não-proibitiva comparada às demais tarefas do CU (demodulação, decodificação, HARQ), e que a transferência de Gram K×K sem aumento de banda é condição suficiente para classificar o sistema como descentralizado.


## LIMITATION / OPEN PROBLEM

  * **Ruído AWGN exclusivamente (gap direto para o projeto):** toda a análise — a definição de descentralizado, os estimadores de G, os resultados de sum-rate — assume Σ = N_0 * I. Sob ruído colorido (Σ ≠ N_0 * I), a distribuição posterior de G|R muda (a covariância da Wishart não-central deixa de ser N_0 * I), o estimador MMSE de G (Eq. 13) assume forma diferente, e o número de condição de G_hat a ser invertido pode aumentar. O paper não trata desse caso em nenhuma parte.
  * **Sem análise de precisão numérica, Cholesky, ou word lengths:** o paper não discute implementação em hardware, decomposição de Cholesky, aritmética de ponto fixo ou número de condição da matriz a ser invertida. Toda a análise é no domínio analítico/probabilístico (distribuições de Wishart).
  * **Sem análise de tempo de coerência (N_coh) como parâmetro de design:** o Coherence Block (CB) é mencionado como o período de validade de W (Seção II-A), mas não há análise de trade-off envolvendo N_coh análoga à de Li et al. Asilomar 2019.
  * **Seção de estimação de canal (IV) — fora de escopo, não é limitação:** os estimadores ML/MAP/MMSE para G via Wishart não-central são o corpo principal do paper mas não têm relação direta com o projeto. Registrado aqui apenas para clareza de escopo.
  * **Sem análise do equalizador L-MMSE:** o paper cita [5] (Jeon/Li/Cavallaro/Studer) como já tendo resolvido PD para MRC, ZF e L-MMSE. Este paper trata apenas ZF com G estimada.
  * **Paradigma de descentralização diferente de Li/Studer:** sem cluster, sem arquitetura feedforward por cluster. Não há comparação quantitativa com PD/FD do grupo Lund/Rice.


## HARDWARE METRICS (Pillar C only)

  * **Matrix family:** não analisado
  * **Matrix dimension:** não analisado
  * **Fixed-point word length:** não analisado
  * **Technology node / FPGA family:** não analisado
  * **Throughput:** não analisado
  * **Area:** não analisado
  * **Power:** não analisado
  * **Condition number analysis:** [ **no** ]


## QUOTE

> "a matrix inversion is needed (in case of zero-forcing) at said processing node"


## CONNECTION TO YOUR WORK

Este paper fornece o âncora teórico para a afirmação de que inversão de matriz K×K é estruturalmente inevitável em qualquer detecção ZF descentralizada onde nenhum nó possui a matriz de canal completa, mas não analisa como a estrutura dessa inversão — e seus requisitos de precisão numérica — se alteram quando o ruído deixa de ser AWGN.


---

## PAPER SPECIFIC QUESTIONS

---

### Definição de "descentralizado" adotada pelo paper

> "here we define the term [decentralized] as a system where the volume of the data provided during the training phase to the processing node is independent of M. Our definition allows for the Gramian to be transferred, since it is of dimension K × K."

Esta definição é **mais permissiva** que o consenso na literatura: ela permite transferir a Gram K×K ao CU (o que no grupo Li/Studer corresponde à arquitetura PD), mas **proíbe** transferir a matriz de canal completa H (M×K). Sob essa definição, PD-MMSE e PD-ZF do grupo Jeon/Li 2019 são classificados como descentralizados.

> "One of our main messages we try to convey is that, in our view, meeting 2) [not expand interconnections beyond what is needed for payload data] is sufficient for a scheme to be classified as non-centralized"

---

### Feature (v): inversão de matriz — forma exata e dimensão

O equalizador ZF é:

$$
\mathbf{W}_\text{ZF} = \mathbf{G}^{-1} \mathbf{H}^H \quad \text{(Eq. 3)}
$$

No sistema descentralizado proposto, as duas partes têm implementações distintas:

- **Parte MRC** $\hat{\mathbf{H}}^H$: implementada **de forma descentralizada** pelas antenas (cada antena $m$ aplica $\hat{\mathbf{h}}_m^*$ ao sinal recebido $y_m$).
- **Parte ZF** $\hat{\mathbf{G}}^{-1}$: **realizada no CU** — inversão de uma matriz K×K (Hermitiana positiva semi-definida).

> "The ZF equalization matrix is made up of two parts (3). The first part (or MRC part), $\hat{\mathbf{H}}^H$, that is implemented in a decentralized form by the antenna modules, and the second part, $\hat{\mathbf{G}}^{-1}$, that is performed in a central processing unit."

**Dimensão da inversão:** K×K — independente de M. Esta é a afirmação estrutural central do paper: a inversão não pode ser distribuída pelas antenas; ela reside irredutível no CU. Para K=16 (experimentos): inversão 16×16.

O paper define dois equalizadores ZF de acordo com o estimador de G utilizado:

$$
\mathbf{W}_\text{MMSE} = \hat{\mathbf{G}}_\text{MMSE}^{-1} \hat{\mathbf{H}}_\text{LS}^H, \qquad \mathbf{W}_\text{LS} = \hat{\mathbf{G}}_\text{LS}^{-1} \hat{\mathbf{H}}_\text{LS}^H
$$

> ⚠️ **O "MMSE" aqui NÃO é o equalizador L-MMSE** de Jeon et al. (que tem forma $(\mathbf{G} + \rho\mathbf{I})^{-1} \mathbf{y}^\text{MRC}$). Aqui, "MMSE" refere-se exclusivamente ao **estimador MMSE da matriz de Gram G** a partir da observação ruidosa R (Eq. 13/14). O equalizador aplicado é sempre ZF — a única diferença está em qual estimativa de G é invertida.

---

### Modelo de ruído e AWGN — onde aparece

O ruído AWGN (CN(0, N_0 * I)) aparece em **três lugares**:

1. **Modelo do sistema uplink (Eq. 1):** n ~ CN(0, N_0 * I) — covariância diagonal. É essa estrutura que garante a separabilidade por antena durante a fase de payload.

2. **Fase de estimação de canal:** durante o treinamento, cada antena $m$ recebe $\mathbf{z}_m = \mathbf{P} \mathbf{h}_m + \mathbf{n}_m$, com n_m ~ CN(0, N_0 * I). Assumindo pilotos de igual potência (|p_k| = 1), a covariância de ruído de estimação é **Σ = N_0 * I** — diagonal. É esta hipótese que simplifica a distribuição posterior de G|R para o caso tratável (Eq. 13, 14).

3. **Estimador MMSE de G (Eq. 13/14):** a forma fechada do estimador MMSE depende de Σ = N_0 * I:

$$
\hat{\mathbf{G}}_\text{MMSE} = \frac{h_\text{pow} N_0}{h_\text{pow} + N_0} M \mathbf{I} + \left(\frac{h_\text{pow}}{h_\text{pow} + N_0}\right)^2 \mathbf{R} \quad \text{(Eq. 14)}
$$

Sob ruído colorido (Σ ≠ N_0 * I), a expressão geral é Eq. (13): $\hat{\mathbf{G}}_\text{MMSE} = M\boldsymbol{\Sigma}\mathbf{A} + \mathbf{A}\mathbf{R}\mathbf{A}$, com $\mathbf{A} = (\mathbf{I} + \mathbf{C}^{-1}\boldsymbol{\Sigma})^{-1}$ — e a G que precisa ser invertida muda de forma. Esta é a conexão direta com o gap do projeto: o número de condição de $\hat{\mathbf{G}}$ sob Σ colorido não é analisado em nenhum ponto do paper.

---

### Mecanismo de transferência da Gram sem aumento de banda (argumento em escopo)

> "Since matched filtering is information lossless, we can, without any loss of generality, assume that such operation is performed. This implies that, for each channel observation, each antenna should multiply its observed signal with a K×1 vector, and that the M resulting K×1 vectors should be summed and passed to the central node by specific hardware that has to be in place."

> "For K single-antenna users, there are K slots per CB where the payload data phase is inactive. This releases K usages of the hardware mentioned just above. [...] such transfer can be done via K transmissions of K×1 vectors. Since the Gramian can be written as a sum over the M outer products of the antennas' channel vectors, we can conclude that the hardware used in the payload data phase is, 1) sufficient to transfer the Gramian, and 2) unoccupied for a duration sufficient for the transmission of the Gramian."

Ou seja: cada antena $m$ computa $\mathbf{R}_m = \hat{\mathbf{h}}_m^* \hat{\mathbf{h}}_m^T$ (K×K, rank-1). A soma $\mathbf{R} = \sum_{m=1}^M \mathbf{R}_m = \hat{\mathbf{H}}_\text{LS}^H \hat{\mathbf{H}}_\text{LS}$ (estimativa LS da Gram) é acumulada e transferida ao CU em K transmissões de K×1, durante os K slots de treinamento. Nenhum hardware adicional é necessário.

> "Under assumption that matched filtering is applied at each antenna, it remains for the central node during the payload data phase to invert the Gramian, and apply the inverse to its K×1 input vectors. We claim that this is of non-prohibitive complexity when taking its other tasks into account."

---

### Coherence Block (CB) — papel no paper

O CB é definido implicitamente como o período em que o canal pode ser considerado aproximadamente constante, durante o qual W permanece válida (Seção II-A). A única referência quantitativa ao CB no contexto de complexidade é o argumento de que os K slots de treinamento "inativos" por CB são suficientes para transferir a Gram. Não há análise de trade-off envolvendo N_coh como em Li et al. Asilomar 2019.

---

### O que este paper NÃO contém (confirmação explícita)

| Tópico | Presente no paper? |
|---|---|
| Decomposição de Cholesky | Não |
| Precisão numérica / word length | Não |
| Análise de número de condição | Não |
| Equalizador L-MMSE (G+ρI)^{-1} | Não — "MMSE" = estimador de G |
| Topologia daisy chain | Não (citada como trabalho alheio [6,7]) |
| Análise de ruído colorido | Não |
| Trade-off de complexidade vs. N_coh | Não |
| Hardware / FPGA / ASIC | Não |
| Arquitetura com clusters | Não |

---

### Posicionamento em relação aos outros papers do repositório

| Aspecto | Sánchez/Rusek (este paper) | Jeon/Li/Studer TSP 2019 | Li et al. Asilomar 2019 |
|---|---|---|---|
| Paradigma de descentralização | Por antena individual; sem cluster | Por cluster (PD/FD) | Por cluster (PD/FD) |
| Dado transferido ao CU | Gram K×K + vetores MRC K×1 | Gram local U×U + y^MRC (PD) ou z + σ² (FD) | Mesmo que Jeon TSP 2019 |
| Equalizadores suportados | ZF apenas (com G estimada) | MRC, ZF, L-MMSE, LAMA | MRC, ZF, L-MMSE, LAMA |
| Inversão no CU | $\hat{\mathbf{G}}^{-1}$ (K×K) | $\mathbf{G}^{-1}$ ou $(\mathbf{G}+\rho\mathbf{I})^{-1}$ (U×U) | $(\mathbf{G}+\rho\mathbf{I})^{-1}$ (U×U, Cholesky) |
| Canal assumido | Rayleigh IID | Rayleigh IID (+ Quadriga/WINNER em simulações) | Rayleigh IID (+ Quadriga em simulações) |
| Ruído | AWGN | AWGN | AWGN |
| Topologia física | Star (implícita) | Star | Star |

O paper cita [5] (Jeon/Li/Studer ArXiv 2018) reconhecendo que PD já resolve ZF e L-MMSE de forma descentralizada. Este paper não supera nem estende Jeon/Li/Studer em desempenho — sua contribuição é diferente: argumento de irredutibilidade da inversão + estimação de G.