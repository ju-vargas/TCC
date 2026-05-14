### Siglas
* **M**: número total de antenas na estação base
    * no artigo, M = 128 e M = 256
* **K**: número total de usuários sendo atendidos simultaneamente  
    * no artigo, K = 8 
* **C**: número de clusters em que as antenas são divididas
    * no artigo, C = 8 ou C = 16

* **Mc**: número de antenas por clusters. 
    * $Mc = M/C$
    * No artigo, $Mc = {18,32}$

* **N**: número de amostras de ruído para estimar a covariância R
    * No artigo, $N = 192$
    * Essas amostras são coletadas durante os símbolos piloto
* **Bloco de Coerência**: intervalo de tempo durante o qual o canal $H$ e a covariância de ruído $R$ permanecem aproximadamente constantes. Durante esse intervalo, a mesma matriz de equalização $W$ pode ser reutilizado para todos os símbolos

* **W**: matriz de equalização

* **Ncoh**: número de símbolos OFDM dentro de um bloco de coerênca

* **Subportadora**: cada uma das frequências paralelas usadas em OFDM
    * em LTE com 20Mhz, há 1200 suportadoras ativas
    * em 5G NR com os parâmetros do artigo, há 3300
    * cada subportadora tem sua própria matriz de canal H e sua própria inversão a ser feita

### Overview

#### Detecção centralizada não funciona em Massive MIMO
Detecção centralizada não funciona em Massive MIMO
Problemas: 
 * Banda: mover os dados para o ponto central é inviável 
 * Inverter uma matriz MxM tem custo  $O(M)^3$


>"extremely large antenna array in the next generation wireless systems poses two major challenges: 1) Excessive communication bandwidth: The rapid growth in the number of BS antennas results in an exceedingly high amount of raw baseband data, including channel state information (CSI), received signal, and noise samples (for noise covariance estimation), that must be transferred between the radio-frequency (RF) chains and the centralized computing fabric [...] This issue is evident in a 256-antenna BS with an 80MHz bandwidth and 12-bit digital-to-analog converters, where the raw baseband data throughput reaches 1Tbps, greatly exceeding the existing capacity of BS internal interface standards. 2) High computational complexity: Traditional LMMSE equalization requires a high-dimensional matrix inversion with a complexity cubic in the number of BS antennas."
— Seção I, Introduction


#### Modelo do sistema uplink

* y é o sinal recebido pela $BS$ (dimensão $M$)
* H é a matriz do canal ($M \times N$) 
* s é o que os usuários transmitiram (dimensão $K$)
* n é o ruído (dimenão $M$) 

Equalizador estima $s$ a partir de $y$ conhecendo $H$. 
Matriz $R$ é a covariância do ruído: descreve como o ruído se distribui e colorrelaciona entre as M antenas

>"Consider an uplink massive MIMO system where K target UEs, each with a single antenna, transmit data to a BS equipped with M antennas, where M ≫ K. The received signal y ∈ Cᴹˣ¹ at the BS is expressed as: y = Hs + n, where H ∈ Cᴹˣᴷ represents the channel matrix between the BS and UEs, s ∈ Sᴷˣ¹ denotes the transmitted symbol vector [...] and n ∼ CN(0, R) denotes the additional white Gaussian noise (AWGN) with R ≜ E[nnᴴ] being the covariance matrix."
— Seção II-A-1


#### Equalizador LMMSE centralizado

* Equalizador LMMSE: matriz $W$ que quando multiplicada pelo sinal $y$ produz a melhor estimativa linear de $s$
* Tem duas inversões: 
    
    * R⁻¹ (inversão da covariância do ruído, dimensão $M×M$) 
    * $(HᴴR⁻¹H + (1/Es)I)⁻¹$ 

* A inversão $M \times M$ é p problema, pois $M$ pode ser 256 ou mais

> "LMMSE equalization aims to find a linear estimate by solving the following problem: min_W E[‖Wy − s‖²₂], which leads to the well-known LMMSE receiver: W_MMSE = (HᴴR⁻¹H + (1/Es)I)⁻¹ HᴴR⁻¹"
— Seção II-A-2, Equação (3)

>"computing the equalization matrix in (3) requires complete knowledge of H ∈ Cᴹˣᴷ and R ∈ Cᴹˣᴹ, which must be collected from the RF chains to a centralized computing fabric. Furthermore, the M-dimensional matrix inversion operation R⁻¹ in (3) results in a computational complexity of O(M³)."
— Seção II-A-2

#### Arquitetura DPB e problema distribuído
Propõe solucionar o problema dividindo as $M$ antenas em $C$ clusters, cada um com $Mc$ antenas e com seu hardware local DU. 

Duas topologias: 
> "In the star architecture, all DUs are connected to a central unit (CU), and each DU performs data compression and subsequently transmits some message (i.e., intermediate results as required) to the CU in parallel for the final equalization operation. In contrast to the star architecture, there is no CU in the daisy chain architecture. Instead, the DUs are connected via unidirectional links, while an additional link connects the last and first DUs to form a ring."
— Seção II-B-1

* Na estrela, todos nós falam com um nó central em paralelo
* Na Dayse Chain, os cluster formam um anel e a informação flui sequencialmente de um para o próximo. 

Assim, o sinal recebido, o canal e o ruído se dividem por cluster: 
> "the received vector, channel matrix, and noise vector in Eq. (1) are accordingly partitioned as y = [y₁ᵀ, y₂ᵀ, ..., yᴄᵀ]ᵀ, H = [H₁ᵀ, H₂ᵀ, ..., Hᴄᵀ]ᵀ, and n = [n₁ᵀ, n₂ᵀ, ..., nᴄᵀ]ᵀ [...] the local received signal yc ∈ Cᴹᶜˣ¹ at cluster c is represented by yc = Hcs + nc"
— Seção II-B-1, Equação (4)

Cada cluster $c$ vê apenas $yc$, $Hc$ e $nc$. 


#### Adição de ruído colorido 
O ruído branco ($R = σ²I$) é diagonal e funciona bem porque $R$ se decompõe nos blocos locais. 

Com ruído colorido o cenário muda:

> "However, in practical systems, interference from other non-target UEs in neighboring cells must be modeled as part of the background noise [...] results in colored noise with a non-diagonal covariance matrix."
— Seção I

Modelo do ruído colorido: 
> "y = Hs + n = Hs + H̄s̄ + n̄, where H̄ ∈ Cᴹˣʳ and s̄ ∈ Sʳˣ¹ respectively denote the channel matrix and interference signals of r non-target UEs, and n̄ ∈ Cᴹˣ¹ is the background AWGN [...] Then, the colored noise covariance matrix R = βH̄H̄ᴴ + σ²I"
— Seção II-B-2, Equação (5)


* O ruído total é a soma de: 
    
    * interferência de r usuários não-alvo $H̄s̄$ 
    * ruído térmico de fundo $n̄$ 

A covariância resultante ($ R = βH̄H̄ᴴ + σ²I $)  não é diagonal porque $H̄H̄ᴴ$ acompla as $M$ antenas.  

Isso cria um problema para DBP: 
> "only the diagonal blocks of R (denoted by R̂cc [...]) can be locally estimated by each cluster c using R̂cc = (1/N)Σᵢ nⁱc(nⁱc)ᴴ. The main challenge lies in accurately obtaining the off-diagonal blocks of R (i.e., Rmn, m≠n [...])."
— Seção II-B-2

Trocar amostrar brutas é muito custoso:
> "the direct exchange of noise samples among DUs would result in high-dimensional data transfer with size M×N, which is prohibited for massive MIMO scenarios."
— Seção II-B-2

Cada cluster só consegue estimar a parte da covariância equivalente às suas próprias antenas:
 
 * bloco diagonal $Rcc$ de tamanho $Mc \times Mc$ 

Os blocos de fora da diagonal 
* $Rmn$, que capturam correlação entre antenas de clusters diferentes 

exigiriam trocar amostras de ruído entre as antenas, com custo $M \times N $

#### Solução baseline BDAC-MMSE 
A primeira solução do artigo propõe zerar os blocos que não são diagonais
> "approximating R with a block diagonal matrix, denoted by R_B ≜ blkdiag(R₁₁, R₂₂, ..., R_CC), where all off-diagonal blocks are set to zero."
— Seção II-B-3

Gerando o equalizador: 
>(HᴴR_B⁻¹H + (1/Es)I)⁻¹ HᴴR_B⁻¹ = (Σc HcᴴRcc⁻¹Hc + (1/Es)I)⁻¹ [H₁ᴴR₁₁⁻¹, ..., HcᴴRcc⁻¹]
— Seção II-B-3, Equação (7)

* cada cluster calcula $HcᴴRcc⁻¹Hc$ localmente

    * Inversão local de $Rcc$, de tamanho $Mc \times Mc$ 
* resultados são somandos centralmente
* uma inversão $K \times K$ conclui o equalizador

Essa é uma solução limitada:
> "Note that this simple approximation leads to a performance loss in colored noise scenarios."
— Seção II-B-3


#### Métodos DR para arquitetura estrela
Para melhorar o desempenho, o artigo propõe métodos de redução de dimensionalidade (DR), comprimindo a informação antes de enviá-la ao nó central: 


Teorema que justifica qual a compressão ótima:
> "through a fat local compression matrix Qc ∈ Cᴸᶜˣᴹᶜ, where Lc < Mc, each DU parallelly transfers the compressed local received vector Qcyc, channel matrix QcHc, and noise samples {Qcnⁱc}ᴺᵢ₌₁ to the CU."
— Seção III-A


Compressão possível: 
> "The minimal compression dimension without performance loss is rank(H) = K, and Q = PHᴴR⁻¹ ∈ Cᴷˣᴹ for an arbitrary invertible matrix P ∈ Cᴷˣᴷ is a lossless compression matrix."
— Seção III-A, Teorema 1
* $Qc = HcᴴRcc⁻¹$, que usa a inversão $Rcc (Mc \times Mc) $

> "the sDR-MMSE equalization is equivalent to the centralized LMMSE equalization when R = R_B."
— Seção III-B, Remark 2


Assim, os dois novos métodos propostos são: 

* sDR-MMSR, onde o nó central soma  as informações
    * faz inversão $K \times K$ no nó central  
* cDR-MMSE, onde as informações são concatenas
    * faz inversão $ CK \times CK$ no nó central. Mais custosa e com melhor desempenho

Esse métodos são sub-ótimos, porque aproximam $R$

#### BDC-MMSE para arquitetura daisy-chain
O problema é reformulado em termos das amostras de ruído: 
> "Incorporating the baseband model (1) and covariance estimation (6) into problem (2), [...] we can reformulate problem (2) equivalently as follows: min_W (1/N) Σᵢ E[‖WHs + Wnⁱ − s‖²₂]"
— Seção IV-A, Equação (24)

As amostras estão disponíveis em cada cluster, mesmo que a covariância não esteja. 

A matriz $W$ é particionada em blocos por cluster:
>"we deliberately partition the equalization matrix W into block matrix as W = [W₁, W₂, ..., Wc] with Wc ∈ Cᴷˣᴹᶜ"
— Seção IV-A

Um bloco $Wc$ é otimizado por vez, mantendo os outros fixos. A solução para cada bloco é:
> "W∗c = (Es(Iᴷ − Σj≠c WjHj)Hcᴴ − (1/N)Σ Σj≠c Wjnⁱj(nⁱc)ᴴ) × (EsHcHcᴴ + (1/N)Σ nⁱc(nⁱc)ᴴ)⁻¹"
— Seção IV-A, Equação (26)

* Aqui, a matriz que precisa ser invertida é $ (EsHcHcᴴ + (1/N)Σ nⁱc(nⁱc)ᴴ)$, de tamanho $Mc \times Mc$

> "Except for the information received from the previous DU, all other terms in (30) can be computed locally."
— Seção IV-A

A convergência ao ótimo global é garantida pelo teorema apresentado no artigo: 
> "The proposed BCD-MMSE algorithm is guaranteed to converge to the global minimum of problem (2). Proof: Since the objective function of (25) is a continuously differentiable and strongly convex function with respect to Wc."
— Seção IV-A, Teorema 2


#### Frequência da Inversão 
* A inversão de $(EsHcHcᴴ + (1/N)Σ nⁱcnⁱcᴴ)$ ocorre a cada atualização de $Wc$ no algoritmo 3. 
* Dentro de um bloco de coerência, a matriz não muda: apenas $Hc$ e as amostras de ruído ${n^ic}$ determinam seu valor
* Da para pré computar e reutilizar nas iterações. 
 > "We assume that the channel and noise covariance remain static across Ncoh contiguous symbols. This means that the equalization matrix and covariance estimation can be reused for different symbols, although they will change with every coherence block."
— Seção V


Fatoração da matriz $Mc \times Mc$ ocorre uma vez por bloco de coerência por cluster por subportadora. Custo $O(Mc^3)$

| Bloco de Coerência | |
| :--- | :--- |
| **Cálculo de Matrizes** | 3300 subportadoras × 8 clusters = 26.400 inversões de matrizes 16×16 |
| **Complexidade Aritmética** | cada com custo O(16³) = 4.096 operações |

| Restrições de Deadline | |
| :--- | :--- |
| **Símbolo OFDM** | 1 símbolo OFDM = 8,9 µs |
| **Clock do Sistema** | @ 200 MHz FPGA = 1.780 ciclos |
| **Paralelismo** | Com 8 clusters paralelos: ~4 ciclos por inversão por cluster |

| Frequência de Renovação | |
| :--- | :--- |
| **Intervalo de Coerência** | Bloco de coerência: ~1-5 ms (ambiente urbano)|
| **Taxa de Update** | 200 a 1000 renovações por segundo |
| **Throughput Total** | até 26,4 milhões de inversões por segundo |


#### Cenário da interferência 
O  artigo define o IoT como métrica de intensidade de interferência:

> "The interference over thermal (IoT) is used to measure the intensity of interference relative to background noise, i.e., IoT = 10log₁₀((β + N₀)/σ²). Large IoT leads to significant interference, i.e., the off-diagonal elements of the noise covariance matrix are more prominent."
— Seção VI-A

E mostra que com IoT alto o sistema degrada: 
> "Fig. 8(f) shows SER performance under IoT = 20 dB, where the performance of all equalizers is significantly degraded due to stronger interference in colored noise."
— Seção VI-C


Com a interferência alta, a covariância do ruído tem elementos mais pronunciados fora da diagonal. 
Isso torna a inversão numericamente mais desafiadora, especialmente em ponto fixo (por causa de erros de quatização).

#### Resultados do artigo 
* Todos as figuras do artigo SER(Symbol Error Rate) no eixo vertical e SNR (Signal-to-Noise Ratio) em dB no eixo horizontal. 

* Curvas mais as esquerdas são melhores. A referência de desempenho centralizado é o LMMSE centralizado. 
* Artigo usa 16-QAM como padrão nas figuras 6-7
* Usa QSPK na figura 8
* Para todos, usa IoT = 10dB

##### Figuras 6 e 7
* Mostra que o BCD-MMSE coverge rápido, assim o custo de comunicação é baixo e o deadline do bloco de coerência é respeitado. 

* BCD-MMSE melhora com mais antenas 

* BCD-MMSE degrada com mais cluster
![Figuras 6 e 7](/figs6-7.png)


##### Figura 8 
* Faz comparativo entre todos os métodos
* BCD-MMSE (LDR) tem melhor desempenho (usa mesma inversão que BCD-MMSE)

* (a e b) Mais antenas beneficiam todos os métodos 

* M(antenas) maior diminui diferença entre métodos descentralizados e LMMSE centralizado

* (b e c) Dividir em mais clusters reduz o desempenho 

* (e) BCD-MMSE Não é sensível ao número de usuários K 

* (f) Com interferência mais forte, todos os métodos pioram

* (g) QPSK tem constelação menor e é mais robusto a ruído e interferência. Hierarquia de desempenho entre os métodos se mantém independente da modulação. 


![Figura 8](/fig8.png)


##### Tabela I

* Todos os métodos desentalizados propostos reduzem a taxa de dados em relação ao LMMSE centralizado. 
> "we observe that for most of the test cases, the DR-MMSE and BCD-MMSE, and BCD-MMSE (LRD) equalization schemes require 23%, 44%, and 37% of the data rate needed by centralized MMSE (C-MMSE) algorithm. This portion can be further decreased as the ratio M/K grows."
— Seção VI-D


* A taxa de dados não cresce com M
> "the fronthaul data rates of the DR-MMSE and BCD-MMSE algorithms are independent of M, making them particularly beneficial for massive MIMO settings."
— Seção VI-D


### BCD - MMSE

* É o único método que converge ao LMMSE centralizado ótimo 

* Converge em 2-3 iterações para os cenários testados

* Não exige inversão centralizada no nó central. A complexidade está toda nas inversãos $Mc \times Mc$

* Arquitetura daisy chain é mais simples
> "the interface design in the daisy chain architecture is simple, low-cost, and easier to extend but often has higher latency."
— Seção II-B-1

* O único gargalo pe a inversão $Mc \times Mc$ por bloco de coerência