# PAPER LOG
 ---
Title: Design Trade-offs for Decentralized Baseband Processing in Massive MU-MIMO Systems

Authors: Kaipeng Li, James McNaney, Chance Tarver, Oscar Castañeda, Charles Jeon, Joseph R. Cavallaro, Christoph Studer

Venue / Year: 53rd Asilomar Conference on Signals, Systems, and Computers / 2019

DOI: não fornecido no paper

Pillar: [**A - inversion avoidance**] [**B - equalization matrix**] [**C - hardware / precision**]

Priority: [ 1 ]

## SETTING
  * **Antennas (M):** B antenas totais na BS, particionadas em C clusters com B_c antenas cada (sistema uplink: B=128, B_c=32, C=4 nos exemplos principais)
  * **Users (K or U):** U = 16 UEs com antena única
  * **Noise model:** n ∈ C^B i.i.d. ruído Gaussiano complexo circularmente simétrico com variância N_0 por entrada (AWGN)
  * **DBP architecture:** Feedforward (PD e FD); sem troca iterativa de consenso entre clusters
  * **Topology:** Star — todos os clusters enviam resultados locais a um processador centralizado (PD: adder tree; FD: fusion tree). Daisy chain não é proposta nem analisada neste paper; os autores citam [12] (Sanchez et al. 2019, arXiv) como referência para a arquitetura daisy chain, sem desenvolver.


## KEY TECHNIQUE

O paper propõe um **framework sistemático de trade-offs** em três níveis hierárquicos para arquiteturas DBP feedforward em massive MU-MIMO (uplink): (1) **nível de arquitetura** — escolha entre PD e FD em função do tempo de coerência do canal $N_\text{coh}$ e do tamanho de transferência de dados; (2) **nível de algoritmo** — escolha entre métodos de inversão explícita (Cholesky) e implícita (gradiente conjugado, descida por coordenadas) em função de $N_\text{coh}$ e da capacidade de reutilizar resultados intermediários entre símbolos dentro de um bloco de coerência; (3) **nível de precisão numérica** — redução de fp32 para fp8 com impacto quantificado em BER. A contribuição central é mostrar que $N_\text{coh}$ é o fator de design mais crítico: ele determina simultaneamente qual arquitetura é mais eficiente em transferência de dados e qual método de inversão tem menor complexidade por símbolo. O paper propõe integrar a decomposição de Cholesky implícita com a arquitetura PD (implicit PD-MMSE) como solução de menor complexidade que obtém o equalizador MMSE exato, ao contrário de métodos iterativos que produzem resultado aproximado.


## JUSTIFICATION

- **Simulação de BER:** Fig. 3(a) — PD-MMSE vs. FD-MMSE, canal Rayleigh i.i.d. e canal Quadriga NLOS urbano, sistema single-carrier, $B_c=32$, $C=4$, $U=16$, 16-QAM. PD supera FD em ambos os canais.
- **Análise de complexidade:** comparação analítica das expressões $n_\text{ex}$ (Eq. 6) e $n_\text{im}$ (Eq. 7) e Fig. 4 — implicit PD-MMSE sempre atinge menor complexidade que explicit PD-MMSE para qualquer $N_\text{coh}$.
- **Análise de tamanho de transferência:** Eq. (4) e (5) — PD é mais eficiente que FD quando $N_\text{coh} > U$; FD é mais eficiente quando $N_\text{coh} < U$.
- **Simulação de BER com precisão reduzida:** Fig. 6 — fp8 vs. fp32 para PD-MMSE e FD-MMSE, canal Quadriga NLOS, $C=4$, $U=16$, $B_c=32$, 16-QAM. fp8 implica perda de BER pequena em relação a fp32.
- **Fluxo de decisão prático:** Fig. 7 — sequência de seleção: arquitetura → algoritmo → precisão.


## LIMITATION / OPEN PROBLEM

- **Ruído AWGN exclusivamente:** toda a análise de complexidade, as expressões de tamanho de transferência, e as simulações de BER (inclusive a de precisão numérica) assumem ruído i.i.d. CN(0, N_0). Sob ruído colorido (interferência inter-celular, pilot contamination), a estrutura das matrizes $\mathbf{G} + \rho\mathbf{I}$ muda, o número de condição da matriz a ser invertida aumenta, e os word lengths recomendados (fp8) podem ser insuficientes — **este é o gap direto que o seu projeto endereça**.
- **Precisão numérica como simulação, não como análise analítica:** o paper avalia fp8 vs. fp32 empiricamente via BER, mas não fornece limites analíticos de número de condição nem análise de propagação de erro de arredondamento para a decomposição de Cholesky sob diferentes regimes de canal. Sua Fase 5 adiciona exatamente essa dimensão analítica.
- **Sem análise de FPGA ou ASIC:** os experimentos de complexidade são em contagem de multiplicações reais (timing complexity) e em GPU/CPU; não há síntese em hardware. O paper projeta implementação futura em FPGA/GPU reconfigurável.
- **Topologia daisy chain ausente:** o paper cita [12] mas não desenvolve análise para a topologia ring/daisy chain; a extensão dos trade-offs para essa topologia é trabalho em aberto.
- **Degradação de SINR com número de clusters:** o paper apresenta Fig. 3(a) mostrando que FD-MMSE tem BER pior que PD-MMSE, mas não fornece expressão analítica fechada para a degradação de SINR em função de C — esse resultado é o que Zhuang et al. 2025 formaliza.


## HARDWARE METRICS (Pillar C — precisão numérica)

  * **Matrix family:** Gram matrix regularizada $\mathbf{A} = \mathbf{G} + \rho\mathbf{I}$ (Hermitiana positiva definida, dimensão U×U)
  * **Matrix dimension:** U×U = 16×16 (nos experimentos)
  * **Fixed-point word length:** fp8 (1 bit sinal, 2 bits mantissa, 5 bits expoente) vs. fp32 (1 bit sinal, 23 bits mantissa, 8 bits expoente). Fp8 embala 4 valores em um registro fp32 para execução SIMD com redução de 4× em instruções e transações de memória.
  * **Technology node / FPGA family:** não especificado (implementação de referência em GPU/CPU; FPGA mencionado como trabalho futuro)
  * **Throughput:** não reportado numericamente neste paper (análise em timing complexity — contagem de multiplicações reais)
  * **Area:** não reportado
  * **Power:** não reportado
  * **Condition number analysis:** [ **no** ] — a análise de precisão é empírica (simulação de BER); sem bounds analíticos de número de condição


## QUOTE

> "Such implicit methods are unable to exploit the benefits of channel coherence since all iterative updates need to be computed for every symbol."


## CONNECTION TO YOUR WORK

Este paper define o estado da arte em trade-offs práticos de DBP feedforward sob AWGN e justifica o uso da decomposição de Cholesky implícita na arquitetura PD, mas não analisa como o número de condição da matriz de Gram — e portanto os requisitos de precisão numérica — se alteram sob ruído colorido, que é exatamente a lacuna que o seu projeto preenche.


---

## PAPER SPECIFIC QUESTIONS

**"Design Trade-offs for Decentralized Baseband Processing in Massive MU-MIMO Systems"** 53rd Asilomar Conference, 2019

**Narrative role:** Section 2 (practical design guidelines) + Section 5 (motivation for hardware analysis)

---

### Trade-off de Arquitetura: PD vs. FD em função de N_coh

**Tamanho de transferência de dados por símbolo (uplink):**

$$
m_\text{PD} = \frac{C \times (U^2 + 2 N_\text{coh} U)}{N_\text{coh}} \tag{4}
$$

$$
m_\text{FD} = 3CU \tag{5}
$$

**Regra de decisão:**
> "We find that at small coherence times $N_\text{coh}$, if $N_\text{coh} < U$, then $m_\text{FD} < m_\text{PD}$, which implies that one should select the FD rather than the PD architecture if the data fusion efficiency has higher priority than BER performance. If $N_\text{coh} > U$, then $m_\text{PD} < m_\text{FD}$, then the PD architecture is always preferred for both better data fusion efficiency and BER performance."

**Conclusão sobre BER:** PD-MMSE sempre supera FD-MMSE em BER (PD é suficiente estatístico para o sinal transmitido).

---

### Inversão Explícita vs. Implícita (Cholesky) — Complexidade por símbolo

**Contexto:** Ambos os métodos computam a inversão de uma matriz U×U Hermitiana positiva definida ($\mathbf{A} = \mathbf{G} + \rho\mathbf{I}$). A diferença está em como exploram $N_\text{coh}$.

**Inversão explícita (explicit PD-MMSE):**
- Decomposição de Cholesky de $\mathbf{A}$ (dominante: $\frac{10}{3}U^3 - \frac{4}{3}U$): reusável por $N_\text{coh}$ símbolos
- Multiplicação matriz-vetor $\hat{\mathbf{x}} = \mathbf{A}^{-1}\mathbf{y}^\text{MRC}$: $4U^2$ por símbolo

$$
n_\text{ex} = \left(2B_c U^2 + \frac{10}{3}U^3 - \frac{4}{3}U\right)/N_\text{coh} + 4B_c U + 4U^2 \tag{6}
$$

**Inversão implícita via Cholesky (implicit PD-MMSE):**
- Fatora $\mathbf{A} = \mathbf{L}\mathbf{L}^H$ (complexidade $\frac{2}{3}U^3 - \frac{2}{3}U$): reusável por $N_\text{coh}$ símbolos
- Resolve $\mathbf{L}\mathbf{z} = \mathbf{y}^\text{MRC}$ (forward) e $\mathbf{L}^H\hat{\mathbf{x}} = \mathbf{z}$ (backward): $4U^2$ operações por símbolo

$$
n_\text{im} = \left(2B_c U^2 + \frac{2}{3}U^3 - \frac{2}{3}U\right)/N_\text{coh} + 4B_c U + 4U^2 \tag{7}
$$

**Comparação direta:**
> "By comparing (6) and (7), we see that the $U^3$ term in $n_\text{ex}$ and $n_\text{im}$ dominates the complexity and $n_\text{im} < n_\text{ex}$ since $n_\text{im}$ has smaller constant associated with this term; this indicates that the implicit method can reduce complexity at no loss in terms of BER compared to the explicit method."

**Constante do termo U³:** explicit = $\frac{10}{3}$ ; implicit = $\frac{2}{3}$ → redução de **5×** no termo dominante.

**Métodos que evitam inversão (iterativos):** gradiente conjugado descentralizado [13] e coordinate descent [20].
> "Such iterative methods typically obtain an approximate result, which entails a small BER loss. Furthermore, such implicit methods are unable to exploit the benefits of channel coherence since all iterative updates need to be computed for every symbol."

→ **Desvantagem crítica dos métodos iterativos:** não conseguem reutilizar resultados entre símbolos dentro de um bloco de coerência.

---

### Reutilização de Resultados via Reciprocidade de Canal (fora de escopo)

O paper explora em detalhes (Seção III-B) como a reciprocidade TDD ($\mathbf{H}^\text{dl} = (\mathbf{H}^\text{ul})^T$, portanto $\mathbf{G}^\text{dl} = (\mathbf{G}^\text{ul})^T$) permite reutilizar a matriz de Gram e a fatoração de Cholesky computadas no uplink para o downlink. Como downlink está fora do escopo deste trabalho, essa análise não é detalhada aqui. O único ponto relevante para o uplink é que o paper confirma que $\mathbf{G}^\text{ul}$ e sua fatoração $\mathbf{L}$ podem ser armazenados e reutilizados por $N_\text{coh}$ símbolos — conclusão que já está capturada nas expressões $n_\text{ex}$ e $n_\text{im}$ acima.

---

### Precisão Numérica: fp8 vs. fp32

**Formato fp8:** 1 bit de sinal, 2 bits de mantissa, 5 bits de expoente.

**Benefícios de eficiência:**
> "When using 8-bit floating point (fp8), we can pack four fp8 values into a fp32 value and execute a vectorized computation instruction (such as vectorized addition, multiplication, etc) in a single-instruction-multiple-data (SIMD) manner to process four fp8 values in parallel within the single instruction, contributing to $4\times$ smaller number of instructions and memory transactions on the processor, and also reducing the inter-cluster bandwidth requirement by $4\times$ compared to corresponding fp32 design."

**Impacto em BER (Fig. 6):**
> "We see in Fig. 6 that fp8 precision only entails a small BER performance loss compared to fp32 precision."

Experimento: PD-MMSE e FD-MMSE, canal Quadriga NLOS, $C=4$, $U=16$, $B_c=32$, 16-QAM.

**O que o paper NÃO faz:** não analisa por que fp8 é ou não suficiente; não relaciona a perda de BER com o número de condição da matriz $\mathbf{A} = \mathbf{G} + \rho\mathbf{I}$; não estuda como esse resultado muda sob ruído colorido (onde $\mathbf{A}$ é diferente e potencialmente peor condicionada).

---

### Fluxo de Decisão Prático — Uplink (Fig. 7)

Sequência hierárquica de seleção (aplicável ao uplink; o paper também cobre downlink precoding, fora de escopo):
1. **Arquitetura (PD ou FD):** trade-off BER vs. tamanho de transferência de dados → guiado por $N_\text{coh}$ vs. $U$
2. **Algoritmo (explícito, implícito, iterativo):** trade-off BER vs. complexidade → guiado por $N_\text{coh}$
3. **Precisão (fp32 → fp8):** trade-off BER vs. eficiência → decisão final após fixar arquitetura e algoritmo

> "given certain system configurations and channel conditions, one should first select the PD or FD architecture by trading off BER vs. data transfer size, and then decide on the detection and precoding algorithms with the selected architecture according to the BER vs. complexity trade-off. Finally, one can lower numerical precision if higher efficiency is more important than BER performance."

**Todas as diretrizes assumem AWGN implicitamente** (ruído i.i.d. $N_0\mathbf{I}$ em todas as simulações e expressões). Sob ruído colorido, o fluxo de decisão não é diretamente aplicável sem reanálise das expressões de complexidade e dos word lengths adequados.

---

### Parâmetros de sistema — consistência com Jeon TSP 2019

| Parâmetro | Li et al. Asilomar 2019 | Jeon et al. TSP 2019 |
|---|---|---|
| B_c | 32 | 32 |
| U | 16 | 16 |
| C | 4 | 4, 8 |
| Canal AWGN | Rayleigh i.i.d. | Rayleigh i.i.d. (large-system limit) |
| Canal realista | Quadriga NLOS | WINNER II |
| Modulação | 16-QAM | 16-QAM |

→ Os parâmetros são consistentes; os dois papers compartilham a mesma base de código (mesmos autores).

---

### Observação sobre a referência daisy chain

O paper cita explicitamente:
> [12] J. Sanchez, F. Rusek, O. Edfors, M. Sarajlic, and L. Liu, "Decentralized Massive MIMO Processing Exploring Daisy-chain Architecture and Recursive Algorithms," arXiv preprint: 1905.03160, May 2019.

Essa referência aparece apenas na lista de trabalhos relacionados (Seção I-B), sem análise, comparação ou desenvolvimento. Confirma que a topologia daisy chain era um tópico ativo em 2019 mas **está fora do escopo deste paper**.