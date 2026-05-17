# Efficient LMMSE Equalization for Massive MIMO Systems Under Decentralized Baseband Processing Architecture

**Xiaotong Zhao, Mian Li, Bo Wang, Enbin Song, Tsung-Hui Chang, Fellow, IEEE, and Qingjiang Shi, Member, IEEE**

**Abstract**—Recently, the decentralized baseband processing (DBP) paradigm and relevant uplink detection methods have been proposed to enable extremely large-scale massive multiple-input multiple-output technology. Under the DBP architecture, base station antennas are divided into several independent clusters, each connected to a local computing fabric. However, current detection methods tailored to DBP only consider ideal white Gaussian noise scenarios, while in practice, the noise is often colored due to interference from neighboring cells. Moreover, in the DBP architecture, linear minimum mean-square error (LMMSE) detection methods require the knowledge of noise covariance matrix which must be estimated using distributedly stored noise samples. This presents a significant challenge for decentralized LMMSE-based equalizer design. To address this issue, this paper proposes decentralized LMMSE equalization methods under colored noise scenarios for both star and daisy chain DBP architectures. Specifically, we first propose two decentralized equalizers for the star DBP architecture based on dimensionality reduction techniques. Then, we derive an optimal decentralized equalizer using the block coordinate descent method for the daisy chain DBP architecture with a bandwidth reduction enhancement scheme based on decentralized low-rank decomposition. Finally, simulation results demonstrate that our proposed methods can achieve excellent detection performance while requiring much less communication bandwidth.

**Index Terms**— Massive MIMO, decentralized baseband processing, data detection, LMMSE, colored noise.

---

## I. INTRODUCTION

MASSIVE multiple-input multiple-output (MIMO) is a critical technology for both fifth-generation (5G) and sixth-generation systems due to its high spectral and power efficiency [2], [3], [4]. With extremely large-scale antenna arrays comprising hundreds or even thousands of antennas, a base station (BS) is capable of simultaneously serving multiple user equipments (UEs) within the same time-frequency resource. Data detection techniques are crucial in the uplink of massive MIMO systems. While the optimal detector is the nonlinear maximum-likelihood detector [5], its complexity grows exponentially with the number of transmit antennas, rendering it impractical for real-world systems. Consequently, low-complexity linear equalization-based detection methods such as maximum ratio combining (MRC), zero-forcing (ZF), and linear minimum mean-square error (LMMSE) detectors are preferred. Among these methods, the LMMSE detector is widely adopted due to its near-optimal detection performance [5].

Conventional LMMSE detection in practical massive MIMO systems relies on centralized baseband processing (CBP) in a single computing fabric. However, extremely large antenna array in the next generation wireless systems poses two major challenges: 1) Excessive communication bandwidth: The rapid growth in the number of BS antennas results in an exceedingly high amount of raw baseband data, including channel state information (CSI), received signal, and noise samples (for noise covariance estimation), that must be transferred between the radio-frequency (RF) chains and the centralized computing fabric [6], [7]. This issue is evident in a 256-antenna BS with an 80MHz bandwidth and 12-bit digital-to-analog converters, where the raw baseband data throughput reaches 1Tbps, greatly exceeding the existing capacity of BS internal interface standards [8]. 2) High computational complexity: Traditional LMMSE equalization requires a high-dimensional matrix inversion with a complexity cubic in the number of BS antennas. This results in a formidable requirement for computation capability, making the CBP architecture impractical for massive MIMO settings [6].

To address the limitations of traditional CBP architectures, recent studies have explored a promising next-generation transceiver architecture called decentralized baseband processing (DBP) [6], [7], [9]–[20]. DBP replaces the centralized computing fabric with multiple local computing fabrics called distributed units (DUs). Additionally, the BS antennas are divided into several independent clusters, each connected to a DU. The DUs communicate with each other through a topology such as a star or a daisy chain. As a result, each DU stores local information like CSI, received signals, and noise/interference samples. This setup enables decentralized data detection with moderate information exchange among DUs. Compared to CBP, the DBP paradigm effectively mitigates bandwidth and computation bottlenecks.

Numerous studies have investigated detection and equalization designs in DBP architectures. To simplify the complicated matrix inversion in centralized ZF and LMMSE equalizers, decentralized iterative methods were proposed. These methods, such as conjugate gradient [6], alternating direction method of multipliers [6], coordinate descent [10], and Newton methods [17], combined the local matched filter, local Gram matrix, and intermediate variables in a decentralized manner. Maximum a posterior estimation-based decentralized detection algorithms, such as large-MIMO approximate message passing [11], expectation propagation [12], [13], and Gaussian message passing [16], were proposed to attain higher detection performance at the expense of increased computational complexity. Notably, all the aforementioned methods aimed to estimate symbols rather than obtain an equalization matrix directly. However, equalization methods have a significant advantage over symbol estimation methods: the equalization matrix can be reused across multiple coherence blocks of channels. In contrast, the symbol estimation algorithms mentioned above must be performed for each channel, resulting in high computational complexity and communication bandwidth. Given this consideration, the authors in [9] presented a decentralized implementation that directly obtained MRC, ZF, and LMMSE equalization matrices in a feedforward DBP architecture. Meanwhile, a decentralized algorithm based on gradient descent was proposed in [7] to obtain the ZF equalization matrix for a daisy chain architecture. Recently, [18] proposed a parallel iterative MMSE equalizer in a decentralized bidirectional-chain equalizer architecture.

Prior works [6], [7], [9]–[19] all assumed that the BS receiver noise follows an ideal additive white Gaussian noise (AWGN) model with a diagonal covariance matrix. This naturally facilitates the distributed implementation of LMMSE equalization in DBP architectures using multiple diagonal submatrices. However, in practical systems, interference from other non-target UEs in neighboring cells must be modeled as part of the background noise [21], [22], i.e., results in colored noise with a non-diagonal covariance matrix. Moreover, the exact noise covariance matrix at the BS is unknown and needs to be estimated by averaging a finite number of noise samples. In DBP architectures, each DU has only local noise samples for the corresponding antenna cluster. Consequently, computing the non-diagonal covariance matrix of colored noise requires collecting noise samples from all clusters. However, this is hampered by prohibitively high communication bandwidth and computational complexity, as the sample dimension is related to the number of BS antennas (which can be extremely large). Therefore, LMMSE equalization in DBP architectures under the colored noise remains a significant challenge, necessitating a completely new algorithmic design that considers limited communication bandwidth and low computational complexity. This paper seeks to address this challenge.

In summary, our main contributions are given as follows:
* **Colored Noise and Covariance Estimation in DBP:** To the best of our knowledge, all the existing detection methods designed for DBP focus solely on ideal white Gaussian noise scenarios. We here for the first time consider the more practical colored noise case. Particularly, for the DBP architectures, we show how to efficiently and implicitly implement decentralized estimation of the noise covariance matrix during the LMMSE process through averaging distributedly stored noise samples.
* **Decentralized Equalization for the Star DBP Architecture:** By investigating the closed-form expression for the LMMSE equalization matrix, we propose two decentralized equalizers that employ dimensionality reduction (DR) techniques under the star DBP architecture. In both methods, each DU embeds its local information into a low-dimensional representation via linear transformation and transmits it to the CU. The CU then either superimposes or concatenates the compressed data to perform LMMSE equalization. Both methods reduce data transfer size from the number of BS antennas to the number of UEs, alleviating the bandwidth and computation bottlenecks, while achieving performance close to centralized LMMSE equalization.
* **Decentralized Equalization for the Daisy Chain DBP Architecture:** To obtain an optimal decentralized equalizer, we reshape the original optimization problem of LMMSE and investigate the distributed storage structure in the daisy chain DBP architecture. Then, we design an efficient decentralized iterative algorithm using the block coordinate descent (BCD) method [25] with guaranteed convergence. During the BCD iteration, data transfer size is significantly reduced, depending only on the number of UEs rather than BS antennas. To further reduce the data transfer size for the case when the number of noise samples is very large, we present an improved BCD-based decentralized LMMSE equalizer by deliberately using a low-rank approximation of the noise covariance matrix. While preserving near-optimal performance, this approach requires the data transfer size independent of the number of noise samples, significantly reducing the bandwidth and computation burden.

The remainder of this paper is organized as follows. Section II introduces the uplink system model and the DBP architectures. Section III proposes two decentralized equalization methods using DR techniques for the star architecture. Section IV develops a BCD-based decentralized equalization method for the daisy chain architecture and a low-rank decomposition scheme for noise covariance matrix to further reduce the communication bandwidth. Section V presents computational complexity and communication bandwidth analysis. The simulation results are provided in Section VI. Finally, this article is concluded in Section VII.

**Notations:** Throughout this paper, scalars are denoted by both lower and upper case letters, while vectors and matrices are denoted by boldface lower case and boldface upper case letters, respectively. For a matrix $A$, $A^{T}$, $A^{H}$, $A^{-1}$, $\text{Tr}(A)$ and $\mathcal{R}(A)$ denote its transpose, conjugate transpose, inverse, trace, and range space, respectively. The Euclidean norm of a vector $x$ is defined as $||x||_{2}=\sqrt{x^{H}x}$. In addition, $\mathbb{E}[\cdot]$ denotes the expectation operation. The notation $I$ is the identity matrix, and $\text{blkdiag}(A_{1},...,A_{C})$ denotes a block diagonal matrix with $A_{1},...,A_{C}$ being its diagonal blocks.

---

## II. SYSTEMS MODEL AND DBP ARCHITECTURES

This section introduces the uplink massive MIMO system model and the LMMSE equalization method. Two uplink DBP architectures are then presented along with the challenges posed by the decentralized LMMSE design.

### A. Uplink System Model and LMMSE Equalization

**1) Uplink System Model:** Consider an uplink massive MIMO system where $K$ target UEs, each with a single antenna, transmit data to a BS equipped with $M$ antennas, where $M \gg K$. The received signal $y \in \mathbb{C}^{M \times 1}$ at the BS is expressed as:

$$y = Hs + n \quad (1)$$

where $H \in \mathbb{C}^{M \times K}$ represents the channel matrix between the BS and UEs, $s \in \mathcal{S}^{K \times 1}$ denotes the transmitted symbol vector with $\mathcal{S}$ representing the constellation set for some modulation scheme (e.g., 16-QAM), and $n \sim \mathcal{CN}(0,R)$ denotes the additional white Gaussian noise (AWGN) with $R \triangleq \mathbb{E}[nn^{H}]$ being the covariance matrix.

**2) LMMSE Equalization:** Typically, the CSI is considered almost constant across several contiguous symbols [15], which enables the reuse of the equalization matrix. Consequently, it is more cost-effective to compute the equalization matrix and reuse it, rather than estimating symbols directly for each instance. Assuming the channel matrix $H$ is perfectly known, LMMSE equalization aims to find a linear estimate by solving the following problem:

$$\min_{W} \mathbb{E}[||Wy-s||_{2}^{2}] \quad (2)$$

which leads to the well-known LMMSE receiver [28]:

$$W_{MMSE} = (H^{H}R^{-1}H+\frac{1}{E_{s}}I)^{-1}H^{H}R^{-1}, \quad (3)$$

where $E_{s}$ denotes the average energy per symbol. The LMMSE estimate $\hat{s}_{MMSE}$ is obtained by applying the equalization matrix $W_{MMSE}$ to the received signal $y$, i.e., $\hat{s}_{MMSE} = W_{MMSE}y$. Finally, the detector quantizes each entry of $\hat{s}_{MMSE}$ to the nearest neighbor point in the constellation set $\mathcal{S}$.

In conventional centralized LMMSE equalization, computing the equalization matrix in (3) requires complete knowledge of $H \in \mathbb{C}^{M \times K}$ and $R \in \mathbb{C}^{M \times M}$ which must be collected from the RF chains to a centralized computing fabric. Furthermore, the $M$-dimensional matrix inversion operation $R^{-1}$ in (3) results in a computational complexity of $\mathcal{O}(M^{3})$. Consequently, centralized processing imposes significant bandwidth and computational demands that are unaffordable when $M$ is extremely large in massive MIMO settings. This motivates the decentralized design of the LMMSE equalization under certain decentralized baseband processing architecture, which is introduced in the sequel.

### B. Decentralized Baseband Processing: Architectures, Challenges, and A Baseline Solution

**1) DBP Architectures:** To address the complexity and bandwidth issues of traditional CBP architectures, recent studies (e.g., [6], [7]) have explored the DBP architecture. The uplink DBP architecture divides $M$ BS antenna elements into $C$ antenna clusters each with $M_{c}$ antennas (i.e., $\sum_{c=1}^{C}M_{c}=M$). In particular, each cluster has its own local RF and computing fabric called DU.

In this paper, we consider two DBP architectures: the star architecture and the daisy chain architecture. In the star architecture, all DUs are connected to a central unit (CU), and each DU performs data compression and subsequently transmits some message (i.e., intermediate results as required) to the CU in parallel for the final equalization operation. In contrast to the star architecture, there is no CU in the daisy chain architecture. Instead, the DUs are connected via unidirectional links, while an additional link connects the last and first DUs to form a ring. Only one DU outputs the symbol estimate and is directly linked to the decoder. The star architecture requires a higher communication bandwidth between the CU and DUs, resulting in complex chip input/output interfaces at the CU. Nevertheless, the star architecture has less latency than the daisy chain architecture since the star architecture enables parallel processing. In contrast, the interface design in the daisy chain architecture is simple, low-cost, and easier to extend but often has higher latency.

Under the DBP architectures, the received vector, channel matrix, and noise vector in Eq. (1) are accordingly partitioned as $y=[y_{1}^{T},y_{2}^{T},...,y_{C}^{T}]^{T}$, $H=[H_{1}^{T},H_{2}^{T},...,H_{C}^{T}]^{T}$, and $n=[n_{1}^{T},n_{2}^{T},...,n_{C}^{T}]^{T}$ respectively. Therefore, the local received signal $y_{c} \in \mathbb{C}^{M_{c} \times 1}$ at cluster $c$ is represented by

$$y_{c} = H_{c}s + n_{c}, \quad c=1,2,...,C \quad (4)$$

where $H_{c} \in \mathbb{C}^{M_{c} \times K}$ and $n_{c} \in \mathbb{C}^{M_{c} \times 1}$ denote the local channel matrix and the local noise vector with respect to cluster $c$, respectively. Note that, $H_{c}$ and $y_{c}$ are only known locally to the DU $c$ and are not allowed to be directly exchanged among DUs to save bandwidth overhead.

**2) Challenges Imposed by DBP on Decentralized LMMSE:** Previous works on decentralized equalization under DBP architectures all assumed AWGN noise with diagonal covariance matrix [6], [7], [9]–[17]. Under such an assumption, the noise covariance matrix can be naturally decomposed into multiple block diagonal submatrices that perfectly fit into the decentralized implementation of LMMSE equalization under DBP architectures. However, the noise at the BS is often colored due to the existence of interference signals from non-target UEs in neighboring cells [21], [22]. In interference scenarios, the baseband model in (1) can be expressed in more detail as follows:

$$y = Hs + \underbrace{\overline{H}\overline{s} + \overline{n}}_{\text{colored noise}} \quad (5)$$

where $\overline{H} \in \mathbb{C}^{M \times r}$ and $\overline{s} \in \mathcal{S}^{r \times 1}$ respectively denote the channel matrix and interference signals of $r$ non-target UEs, and $\overline{n} \in \mathbb{C}^{M \times 1}$ is the background AWGN with distribution $\mathcal{CN}(0,\sigma^{2}I)$. Then, the colored noise covariance matrix $R = \beta\overline{H}\overline{H}^{H} + \sigma^{2}I$, where $\beta$ is the power of interference signals. In this scenario, $R$ becomes non-block-diagonal. Moreover, the decentralized estimation of $R$ is not possible because directly exchanging interference signals among DUs is forbidden due to bandwidth limitation. This imposes a huge challenge for decentralized LMMSE equalization design.

To better understand the challenge mentioned above, we write down the best estimation of $R$ as [21], [22], and [29]:

$$R = \frac{1}{N} \sum_{i=1}^{N} n^{i}(n^{i})^{H}, \quad (6)$$

which is done by averaging the noise samples in $N$ pilot resource elements (REs). Here, $N \gg K$ holds to ensure the accuracy of estimation, and $n^{i} \in \mathbb{C}^{M \times 1}$ is the noise sample in the $i$-th pilot RE. Corresponding to the antennas clustering in DBP architectures, the $i$-th noise sample $n^{i}$ can be divided as $n^{i} = [(n_{1}^{i})^{T},(n_{2}^{i})^{T},...,(n_{C}^{i})^{T}]^{T}$ $\forall i$, where $\{n_{c}^{i}\}_{i=1}^{N}$ are stored in cluster $c$. Similarly, the noise covariance matrix $R$ can be regarded as a block matrix with $C \times C$ blocks, where the $(m, n)$-th block submatrix is denoted by $R_{mn} = \mathbb{E}[n_{m}n_{n}^{H}]$. Accurate estimation of $R$ is crucial for effective LMMSE equalization. However, only the diagonal blocks of $R$ (denoted by $\hat{R}_{cc}$) can be locally estimated by each cluster $c$ using $\hat{R}_{cc} = (1/N)\sum_{i=1}^{N}n_{c}^{i}(n_{c}^{i})^{H}$. The main challenge lies in accurately obtaining the off-diagonal blocks of $R$ (i.e., $R_{mn}, m \neq n$). Note that the direct exchange of noise samples among DUs would result in high-dimensional data transfer with size $M \times N$, which is prohibited for massive MIMO scenarios. Moreover, traditional whitening noise methods cannot be applied because they don't allow distributed implementation in DBP. As a result, decentralized computation of the LMMSE equalization matrix in (3) under stringent bandwidth constraints poses a significant challenge.

**3) A Baseline Solution:** We first propose a straightforward solution to roughly tackle this challenge, i.e., approximating $R$ with a block diagonal matrix, denoted by $R_{B} \triangleq \text{blkdiag}(R_{11},R_{22},...,R_{CC})$, where all off-diagonal blocks are set to zero. This approach enables the approximation of the LMMSE equalization matrix in (3) as:

$$(H^{H}R_{B}^{-1}H+\frac{1}{E_{s}}I)^{-1}H^{H}R_{B}^{-1} = (\sum_{c=1}^{C}H_{c}^{H}R_{cc}^{-1}H_{c}+\frac{1}{E_{s}}I)^{-1}[H_{1}^{H}R_{11}^{-1},...,H_{C}^{H}R_{CC}^{-1}]. \quad (7)$$

It is possible to implement (7) in a decentralized manner. Specifically, each DU $c=1,2,...,C$ first computes $H_{c}^{H}R_{cc}^{-1}H_{c}$ locally, which is then collected together for summation and inversion operations. Finally, the matrix inverse result is broadcasted to all DUs, allowing them to compute their local equalization matrices. This decentralized implementation of obtaining the approximate equalization matrix in (7) is called the block diagonal approximate covariance MMSE (BDAC-MMSE) equalizer. The transfer of only low-dimensional matrices with size $K \times K$ requires minimal communication bandwidth. Note that this simple approximation leads to a performance loss in colored noise scenarios. Therefore, algorithms with better performance will be proposed in the following sections. Nevertheless, BDAC-MMSE can serve as a good initial point for our proposed decentralized BCD-based equalizers in Section IV, as well as a baseline algorithm.

---

## III. DIMENSIONALITY REDUCTION MMSE EQUALIZATION FOR STAR DBP ARCHITECTURE

This section introduces the DR technique for the star DBP architecture and formulates the LMMSE problem under two types of compression matrices. Then, two DR-based decentralized equalization methods are designed.

### A. Dimensionality Reduction in DBP

To reduce the bandwidth burden in DBP architectures, a straightforward idea is to reduce the dimension of local information while preserving equalization performance, which matches the concept of the DR technique [30], [31]. Specifically, in the star DBP architecture, through a fat local compression matrix $Q_{c} \in \mathbb{C}^{L_{c} \times M_{c}}$, where $L_{c} < M_{c}$, each DU parallelly transfers the compressed local received vector $Q_{c}y_{c}$, channel matrix $Q_{c}H_{c}$, and noise samples $\{Q_{c}n_{c}^{i}\}_{i=1}^{N}$ to the CU. Based on these compressed data, an LMMSE estimate of $s$ is formed through an equalization matrix $W$. Since $L_{c} < M_{c}$, the bandwidth can be significantly reduced. We assume local compression dimension $L_{c}=L$ for brevity.

The compression matrix can be an arbitrary fat matrix. For the star DBP architecture, we focus on the following two scenarios of compression matrices:

**1) Superimposed Compression:** The compressed received signals from each DU are superimposed at the CU as:
$$\overline{y}(Q_{1},...,Q_{C}) = \sum_{c=1}^{C}Q_{c}y_{c} = [Q_{1},...,Q_{C}]y. \quad (8)$$

**2) Concatenated Compression:** The CU concatenates the compressed data of individual DUs to form a vector:
$$\tilde{y}(Q_{1},...,Q_{C}) = \text{blkdiag}(Q_{1},...,Q_{C})y. \quad (9)$$

The dimension of the compressed vector in the superimposed and concatenated scenarios are $L \times 1$ and $CL \times 1$, respectively. For both scenarios, we aim to design MSE optimal equalization matrices $W$ and local compression matrices $\{Q_{c}\}_{c=1}^{C}$ as follows:

$$\min_{W,\{Q_{c}\}_{c=1}^{C}} \mathbb{E}[||s-W\overline{y}(Q_{1},...,Q_{C})||_{2}^{2}]. \quad (10)$$

where $\overline{y}(Q_{1},...,Q_{C})$ is given by either (8) or (9).

**Theorem 1:** Consider system model (1), i.e., $y=Hs+n$. Denote $Q \in \mathbb{C}^{L \times M}$ as the global compression matrix. The minimal compression dimension without performance loss is $\text{rank}(H)=K$, and $Q=PH^{H}R^{-1} \in \mathbb{C}^{K \times M}$ for an arbitrary invertible matrix $P \in \mathbb{C}^{K \times K}$ is a lossless compression matrix.

*Proof: See Appendix A.*

Following Theorem 1, setting $P=I$ results in a lossless compression matrix $H^{H}R^{-1} \in \mathbb{C}^{K \times M}$. However, this cannot be utilized directly for the DBP architectures because $R^{-1}$ is unavailable without collecting $\{n_{c}^{i}\}_{i=1}^{N}$ from each DU to the CU, which is infeasible due to bandwidth limitations. Therefore, we use a lossy compromise by using $Q_{c}=H_{c}^{H}R_{cc}^{-1} \in \mathbb{C}^{K \times M_{c}}$ as a local compression matrix at each DU $c$.

### B. Superimposed DR-MMSE Equalization

We first consider the superimposed scenario. Adopting $Q_{c}=H_{c}^{H}R_{cc}^{-1}$ as the local compression matrix at DU $c$, the global superimposed compression matrix is given by:

$$Q = [Q_{1},Q_{2},...,Q_{C}] = [H_{1}^{H}R_{11}^{-1},H_{2}^{H}R_{22}^{-1},...,H_{C}^{H}R_{CC}^{-1}] \approx H^{H}R_{B}^{-1} \quad (11)$$

Applying the compression to (1), we obtain the effective compressed channel model at the CU as:

$$\tilde{y} = \tilde{H}s + \tilde{n}, \quad (12)$$

where
$$\tilde{y} = \tilde{Q}y = \sum_{c=1}^{C}Q_{c}y_{c}, \quad \tilde{H} = \tilde{Q}H = \sum_{c=1}^{C}Q_{c}H_{c}, \quad \tilde{n} = \tilde{Q}n = \sum_{c=1}^{C}Q_{c}n_{c}. \quad (13)$$

The effective noise covariance matrix can be expressed by:

$$\tilde{R} = \tilde{Q}R\tilde{Q}^{H} = \frac{1}{N}\sum_{m=1}^{C}\sum_{l=1}^{C}\sum_{i=1}^{N}Q_{m}n_{m}^{i}(Q_{l}n_{l}^{i})^{H}. \quad (14)$$

After the low-dimensional compressed information is collected from all the DUs, the CU calculates the equalization matrix as follows:

$$W_{sDR\_MMSE} = (\tilde{H}^{H}\tilde{R}^{-1}\tilde{H}+\frac{1}{E_{s}}I)^{-1}\tilde{H}^{H}\tilde{R}^{-1} \quad (15)$$

and the estimated symbol is given by:

$$\hat{s}_{sDR-MMSE} = W_{sDR-MMSE}\tilde{y}. \quad (16)$$

**Algorithm 1: The Proposed sDR-MMSE Equalization**
> **Input:** $y_{c}$, $H_{c}$, $\{n_{c}^{i}\}_{i=1}^{N}$, $c=1,2,...,C$, and $E_{s}$
> 1: **Decentralized preprocessing at each DU:**
> 2: **for** $c=1$ to $C$ **do**
> 3:     $Q_{c} \leftarrow H_{c}^{H}R_{cc}^{-1}$;
> 4:     Compute $Q_{c}y_{c}$, $Q_{c}H_{c}$, and $\{Q_{c}n_{c}^{i}\}_{i=1}^{N}$; // Send to CU
> 5: **end for**
> 6: **Central processing at the CU:**
> 7: Compute $\tilde{y}$ and $\tilde{H}$ via (13);
> 8: Compute $\tilde{R}$ via (14);
> 9: $W_{sDR-MMSE}$ is given by (15);
> 10: $\hat{s}_{sDR-MMSE}$ is given by (16);
> **Output:** $W_{sDR-MMSE}$ and $\hat{s}_{sDR-MMSE}$.

### C. Concatenated DR-MMSE Equalization

The sDR-MMSE equalization results in information loss due to the superimposition of information from each DU. A potential approach to improve performance is to concatenate compressed information instead of superimposing, although this comes at the cost of increased complexity. We consider the compression matrix in (9) using the local compression matrix $Q_{c} = H_{c}^{H}R_{cc}^{-1}$. The global concatenated compression matrix is given by:

$$\tilde{Q} = \text{blkdiag}(Q_{1}, Q_{2}, ..., Q_{C}) = \text{blkdiag}(H_{1}^{H}R_{11}^{-1},H_{2}^{H}R_{22}^{-1},...,H_{C}^{H}R_{CC}^{-1}). \quad (17)$$

Thus, the effective channel model at the CU is given by $\tilde{y} = \tilde{H}s + \tilde{n}$, where $\tilde{y}$ is a stacked vector of local compressed observations (18, 19). The effective noise covariance matrix can be expressed by:

$$\hat{R} = \begin{bmatrix} Q_{1}R_{11}Q_{1}^{H} & \cdots & Q_{1}R_{1C}Q_{C}^{H} \\ \vdots & \ddots & \vdots \\ Q_{C}R_{C1}Q_{1}^{H} & \cdots & Q_{C}R_{CC}Q_{C}^{H} \end{bmatrix} \quad (20)$$

where $Q_{m}R_{ml}Q_{l}^{H} = \frac{1}{N}\sum_{i=1}^{N}Q_{m}n_{m}^{i}(Q_{l}n_{l}^{i})^{H}$ (21).

Consequently, after collecting the compressed information, the CU calculates the equalization matrix as follows:

$$W_{cDR-MMSE} = (\tilde{H}^{H}\overline{R}^{-1}\overline{H}+\frac{1}{E_{s}}I)^{-1}\overline{H}^{H}\overline{R}^{-1} \quad (22)$$

and the estimated symbol is given by $\hat{s}_{cDR-MMSE} = W_{cDR-MMSE}\tilde{y}.$ (23).

**Algorithm 2: The Proposed cDR-MMSE Equalization**
> **Input:** $y_{c}$, $H_{c}$, $\{n_{c}^{i}\}_{i=1}^{N}$, $c=1,2,...,C$, and $E_{s}$.
> 1: **Decentralized preprocessing at each DU:**
> 2: **for** $c=1$ to $C$ **do**
> 3:     $Q_{c} \leftarrow H_{c}^{H}R_{cc}^{-1}$;
> 4:     Compute $Q_{c}y_{c}$, $Q_{c}H_{c}$, and $\{Q_{c}n_{c}^{i}\}_{i=1}^{N}$; // Send to CU
> 5: **end for**
> 6: **Central processing at the CU:**
> 7: Compute $\tilde{y}$ and $\tilde{H}$ via (19);
> 8: Compute $\hat{R}$ via (20);
> 9: $W_{cDR-MMSE}$ is given by (22);
> 10: $\hat{s}_{cDR-MMSE}$ is given by (23);
> **Output:** $W_{cDR-MMSE}$ and $\hat{s}_{cDR-MMSE}$.

**Proposition 1:** The MSE matrix $E_{sDR} \ge E_{cDR}$, where $E_{sDR} \triangleq \mathbb{E}[(\hat{s}_{sDR-MMSE}-s)(\hat{s}_{sDR-MMSE}-s)^{H}]$ and $E_{cDR} \triangleq \mathbb{E}[(\hat{s}_{cDR-MMSE}-s)(\hat{s}_{cDR-MMSE}-s)^{H}]$. Moreover, we have $\mathbb{E}[||\hat{s}_{sDR-MMSE}-s||_{2}^{2}] \ge \mathbb{E}[||\hat{s}_{cDR-MMSE}-s||_{2}^{2}]$.

*Proof: See Appendix B.*

---

## IV. BCD-BASED LMMSE EQUALIZATION FOR THE DAISY CHAIN ARCHITECTURE

### A. BCD-Based LMMSE Equalization

The DR-based LMMSE equalizers can be viewed as a decentralized implementation of the closed-form expression of the equalization matrix in (3). To design an optimal decentralized equalizer for the daisy chain architecture, we reformulate problem (2) equivalently as follows:

$$\min_{W} \frac{1}{N}\sum_{i=1}^{N}\mathbb{E}[||WHs+Wn^{i}-s||_{2}^{2}]. \quad (24)$$

We deliberately partition the equalization matrix $W$ into block matrix as $W=[W_{1},W_{2},...,W_{C}]$ with $W_{c} \in \mathbb{C}^{K \times M_{c}}$. Then, problem (24) can be rewritten as:

$$\min_{\mathcal{W}} \frac{1}{N}\sum_{i=1}^{N}\mathbb{E}[||W_{c}H_{c}s+\sum_{j=1,j \neq c}^{C}W_{j}H_{j}s+W_{c}n_{c}^{i}+\sum_{j=1,j \neq c}^{C}W_{j}n_{j}^{i}-s||_{2}^{2}]. \quad (25)$$

We then use the BCD method to optimize $\{W_{c}\}_{c=1}^{C}$, which is suitable for the decentralized daisy chain architecture. 

**Proposition 2:** While fixing $W_{j}$ ($j \neq c$) in problem (25), the optimal solution with respect to $W_{c}$ in closed form is given by:

$$W_{c}^{*} = \left(E_{s}(I_{K}-\sum_{j=1,j \neq c}^{C}W_{j}H_{j})H_{c}^{H}-\frac{1}{N}\sum_{i=1}^{N}\sum_{j=1,j \neq c}^{C}W_{j}n_{j}^{i}(n_{c}^{i})^{H}\right) \times \left(E_{s}H_{c}H_{c}^{H}+\frac{1}{N}\sum_{i=1}^{N}n_{c}^{i}(n_{c}^{i})^{H}\right)^{-1}. \quad (26)$$

*Proof: See Appendix C.*

Adopting the Gauss-Seidel update rule, at the $l$-th iteration, the local equalization matrix $W_{c}^{l}$ is updated. Define $A_{c}^{l} \in \mathbb{C}^{K \times K}$ and $\{b_{c,i}^{l} \in \mathbb{C}^{K \times 1}\}_{i=1}^{N}$ as the interaction variables at $c$-th DU and $l$-th iteration, updated recursively by:

$$A_{c}^{l} = A_{c-1}^{l} - W_{c}^{l-1}H_{c} + W_{c}^{l}H_{c} \quad (28)$$
$$b_{c,i}^{l} = b_{c,i}^{l-1} - W_{c}^{l-1}n_{c}^{i} + W_{c}^{l}n_{c}^{i}, \quad i=1,2,...,N \quad (29)$$

**Algorithm 3: The Proposed BCD-MMSE Equalization**
> **Input:** $y_{c}$, $H_{c}$, $\{n_{c}^{i}\}_{i=1}^{N}$, $c=1,2,...,C$, $E_{s}$, and total iteration number $T$.
> 1: **Preprocessing:**
> 2: Initialize $W^{0}$ using (7) in a decentralized manner;
> 3: $A_{0}^{0} \leftarrow 0$;
> 4: $b_{0,i}^{0} \leftarrow 0$, $i = 1,2,...,N$;
> 5: **for** $c=1$ to $C$ **do**
> 6:     $A_{0}^{0} \leftarrow A_{0}^{0} + W_{c}^{0}H_{c}$;
> 7:     $b_{0,i}^{0} \leftarrow b_{0,i}^{0} + W_{c}^{0}n_{c}^{i}$, $i=1,2,...,N$;
> 8: **end for**
> 9: **BCD iterations:**
> 10: **for** $l=1$ to $T$ **do**
> 11:     **for** $c=1$ to $C$ **do**
> 12:         Update $W_{c}^{l}$ via (30);
> 13:         Update $A_{c}^{l}$ via (28);
> 14:         Update $b_{c,i}^{l}$ via (29);
> 15:     **end for**
> 16: **end for**
> 17: **Equalizer filter:**
> 18: $\hat{s}_{BCD-MMSE} \leftarrow 0$;
> 19: **for** $c=1$ to $C$ **do**
> 20:     $\hat{s}_{BCD-MMSE} \leftarrow \hat{s}_{BCD-MMSE} + W_{c}y_{c}$;
> 21: **end for**
> **Output:** $W=[W_{1},W_{2},...,W_{C}]$ and $\hat{s}_{BCD-MMSE}$.

### B. Low-Rank Decomposition Based BCD-MMSE

The proposed optimal BCD-MMSE equalizer effectively mitigates the bandwidth and computation limitations. However, the communication bandwidth required for each iteration still depends on the number of noise samples ($N$). We present an improved BCD-MMSE equalization method for the case when $N$ is large. In interference scenarios, the covariance matrix $R = \beta\overline{H}\overline{H}^{H} + \sigma^{2}I$ can be deemed to be approximately low-rank (rank-$r$ matrix). We seek a low-rank substitute $G \in \mathbb{C}^{M \times r}$ such that $GG^{H}$ closely approximates $R$:

$$G = \arg\min_{\text{Rank}(G) \le r} ||R - GG^{H}||_{F}^{2} \quad (31)$$

Denote the SVD of $N$ (scaled noise samples) by $N = U\Sigma V^{H}$ (33). The optimal solution is given by $G = \tilde{U}\tilde{\Sigma} = N\tilde{V}$ (34). We summarize the proposed algorithm in Algorithm 4 (termed low-rank decomposition (LRD) algorithm). 

---

## V. COMPLEXITY AND BANDWIDTH ANALYSIS

### A. Computational Complexity Analysis

Throughout the section, we consider the common scenario where $\min\{M,N\} > M_{c} > K$. The computational complexity of the centralized LMMSE equalizer in (3) is $\mathcal{O}(M^{3} + NM^{2})$.

The computational complexity of the proposed sDR-MMSE and cDR-MMSE equalizers are $\mathcal{O}(MM_{c}^{2} + NMM_{c})$ and $\mathcal{O}(MM_{c}^{2} + NMM_{c} + K^{3}C^{3})$ respectively. They have the same preprocessing with a complexity of $\mathcal{O}(M_{c}^{3} + NM_{c}^{2})$ at each DU.

The per-iteration complexity of the BCD-MMSE equalization is $\mathcal{O}(NMK + MM_{c}K)$. Benefiting from the LRD algorithm, the per-iteration complexity of the BCD-MMSE (LRD) equalization is $\mathcal{O}(rMK + MM_{c}K)$, which is independent of $N$. The complexity of our proposed methods scales linearly with $M$ instead of $\mathcal{O}(M^{3})$.

### B. Communication Bandwidth Analysis

The communication bandwidth is evaluated by the total number of real-valued entries transferred among the DUs. We assume that the channel and noise covariance remain static across $N_{coh}$ contiguous symbols. The average data transfer size of the proposed BCD-MMSE method is $C(4K^{2}+2NK)/N_{coh} + 2TCK(N+K)/N_{coh} + 2CK$. Notably, the average data transfer size of the aforementioned methods is independent of $M$. All the proposed methods can achieve a decentralized baseband processing design with a relatively small communication bandwidth among DUs.

---

## VI. SIMULATION RESULTS

### A. Simulation Setup

We investigate a single-cell massive MIMO system comprising of a BS equipped with $M=128$ or 256 antennas, divided into $C=8$ or 16 clusters, where each cluster has $M_{c}=M/C$ antennas. The number of target and non-target UEs is both set to $K=8$ and there are $N=192$ noise samples. The colored noise is modeled as interference from non-target UEs plus background AWGN, where the non-target UEs are molded similarly to the target UEs. The interference over thermal (IoT) is used to measure the intensity of interference relative to background noise, i.e., $\text{IoT}=10 \log_{10}((\beta+N_{0})/\sigma^{2})$. $\text{IoT}=10$ dB is a default setting.

### B. SER Performance of the Proposed BCD-Based Equalizers

It can be observed that only 2 to 3 iterations are sufficient to approach the performance of the centralized LMMSE method for all cases. Even a single BCD iteration enables excellent SER performance. When the BS employs more antennas, the performance gap between the BCD-MMSE equalizer and LMMSE equalizer decreases.

### C. SER Performance of All the Proposed Equalizers

The proposed equalizers' performance ranking is BCD-MMSE (LRD), BCD-MMSE, cDR-MMSE, and sDR-MMSE. Generally speaking, BCD-MMSE and cDR-MMSE methods have comparable performance. With an increase in the number of UEs from 8 to 12, the cDR-MMSE equalizer's performance greatly improves due to the rising local compression dimension from 8 to 12.

### D. Fronthaul Data-Rate Comparison

Table 1 presents a comparison of the total fronthaul data rate between the centralized and our proposed decentralized algorithms. We observe that for most of the test cases, the DR-MMSE and BCD-MMSE, and BCD-MMSE (LRD) equalization schemes require 23%, 44%, and 37% of the data rate needed by centralized MMSE (C-MMSE) algorithm.

| Scenario | Case 1 | Case 2 | Case 3 |
| :--- | :--- | :--- | :--- |
| M | 128 | 128 | 256 |
| K | 8 | 8 | 8 |
| C | 2 | 4 | 4 |
| C-MMSE | 42.98 | 42.98 | 85.98 |
| DR-MMSE | 5.37 | 10.75 | 10.75 |
| BCD-MMSE | 15.71 | 31.43 | 31.43 |
| BCD-MMSE (LRD) | 12.27 | 25.34 | 27.78 |

---

## VII. CONCLUSION

This paper has investigated the decentralized LMMSE equalizer design under the DBP architectures. The existing decentralized equalization algorithms only considered ideal AWGN assumption, whereas colored noise exists in practice. Therefore, we have proposed DR-based and BCD-based equalizers for the star and daisy chain architectures, respectively. The data transfer size of these equalizers is independent of the number of BS antennas, significantly mitigating the bandwidth and computation bottlenecks encountered in centralized counterparts. In addition, the communication bandwidth of the BCD-MMSE equalizer can be reduced further by applying the LRD algorithm.

---

## APPENDIX A: PROOF OF THEOREM 1

The MSE matrix for the LMMSE estimate in (3) is given by:

$$E_{MMSE} \triangleq \mathbb{E}[(\hat{s}_{MMSE}-s)(\hat{s}_{MMSE}-s)^{H}] = E_{s}I - E_{s}H^{H}(HH^{H}+\frac{1}{E_{s}}R)^{-1}H. \quad (35)$$

Similarly, we obtain the MSE matrix for compression matrix $Q \in \mathbb{C}^{L \times M}$ as follows:

$$E_{C} = E_{s}I - E_{s}H^{H}Q^{H}(QHH^{H}Q^{H}+\frac{1}{E_{s}}R)^{-1}QH. \quad (36)$$

With these definitions, we prove that the minimal compression dimension without performance loss is $\text{rank}(H)=K$. Assume $Q \in \mathbb{C}^{L \times M}$ with $L < K$ is lossless (i.e., $E_{C}=E_{MMSE}$). This yields:

$$H^{H}(HH^{H}+\frac{1}{E_{s}}R)^{-1}H = H^{H}Q^{H}(QHH^{H}Q^{H}+\frac{1}{E_{s}}R)^{-1}QH. \quad (37)$$

However, the rank of the left-hand side and right-hand side of (37) is $K$ and $L$, respectively. This leads to a contradiction. Then we verify that $PH^{H}R^{-1}$ is a lossless compression matrix:

$$\hat{s}_{MMSE} = (H^{H}R^{-1}H+\frac{1}{E_{s}}I)^{-1}H^{H}R^{-1}y \quad (38)$$

The equivalence shows that $PH^{H}R^{-1}$ is a lossless compression matrix.

## APPENDIX B: PROOF OF PROPOSITION 1

From the definition of $E_{sDR}$, we have:

$$E_{sDR} = E_{s}I - E_{s}H^{H}\tilde{Q}^{H}(\tilde{Q}HH^{H}\tilde{Q}^{H}+\frac{1}{E_{s}}\tilde{Q}R\tilde{Q}^{H})^{-1}\tilde{Q}H. \quad (39)$$

By leveraging the Woodbury identity [37], one has:

$$E_{sDR}^{-1} = \frac{1}{E_{s}}I + H^{H}\tilde{Q}^{H}(\tilde{Q}R\tilde{Q}^{H})^{-1}\tilde{Q}H. \quad (40)$$

To prove $E_{cDR} \le E_{sDR}$, it is sufficient to show:

$$\tilde{Q}^{H}(\tilde{Q}R\tilde{Q}^{H})^{-1}\tilde{Q} \ge \tilde{Q}^{H}(\tilde{Q}R\tilde{Q}^{H})^{-1}\tilde{Q}. \quad (41)$$

We observe that $R^{\frac{1}{2}}\tilde{Q}^{H}(\tilde{Q}R\tilde{Q}^{H})^{-1}\tilde{Q}R^{\frac{1}{2}}$ is an orthogonal projection matrix with range space $\mathcal{R}(R^{\frac{1}{2}}\tilde{Q}^{H})$. Thus $Tr(E_{sDR}) \ge Tr(E_{cDR})$, leading to the conclusion.

## APPENDIX C: PROOF OF PROPOSITION 2

Since the objective function of problem (25) is convex in $W_{c}$, we obtain the optimal solution by setting the gradient equal to 0. The objective function can be rewritten as:

$$\frac{1}{N}\sum_{i=1}^{N}\mathbb{E}[||W_{c}H_{c}s+\sum_{j=1,j \neq c}^{C}W_{j}H_{j}s+W_{c}n_{c}^{i}+\sum_{j=1,j \neq c}^{C}W_{j}n_{j}^{i}-s||_{2}^{2}]$$
$$= \Re(\text{Tr}(E_{s}W_{c}H_{c}H_{c}^{H}W_{c}^{H} + 2E_{s}\sum_{j=1,j \neq c}^{C}W_{c}H_{c}H_{j}^{H}W_{j}^{H} - 2E_{s}W_{c}H_{c} + W_{c}(\frac{1}{N}\sum_{i=1}^{N}n_{c}^{i}(n_{c}^{i})^{H})W_{c}^{H} + 2\sum_{j=1,j \neq c}^{C}W_{c}(\frac{1}{N}\sum_{i=1}^{N}n_{j}^{i}(n_{c}^{i})^{H})W_{j}^{H})) + \text{const}. \quad (43)$$

Calculate its gradient w.r.t. $W_{c}$ yielding:

$$\nabla_{W_{c}}f(W_{c}) = 2E_{s}W_{c}H_{c}H_{c}^{H} + 2E_{s}\sum_{j=1,j \neq c}^{C}W_{j}H_{j}H_{c}^{H} - 2E_{s}H_{c}^{H} + 2W_{c}(\frac{1}{N}\sum_{i=1}^{N}n_{c}^{i}(n_{c}^{i})^{H}) + 2\sum_{j=1,j \neq c}^{C}W_{j}(\frac{1}{N}\sum_{i=1}^{N}n_{j}^{i}(n_{c}^{i})^{H}). \quad (44)$$

Letting $\nabla_{W_{c}}f(W_{c}^{*}) = 0$ we obtain the optimal solution $W_{c}^{*}$ in closed form as in (26).

---

## REFERENCES

[1] X. Zhao, X. Guan, M. Li, and Q. Shi, "Decentralized linear MMSE equalizer under colored noise for massive MIMO systems," in Proc. IEEE Global Commun. Conf. (GLOBECOM), Dec. 2021, pp. 1-6.
[2] J. Zhang, E. Björnson, M. Matthaiou, D. W. K. Ng. H. Yang, and D. J. Love, "Prospective multiple antenna technologies for beyond 5G," IEEE J. Sel. Areas Commun., vol. 38, no. 8, pp. 1637-1660, Aug. 2020.
[3] T. L. Marzetta and H. Q. Ngo, Fundamentals of Massive MIMO. Cambridge, U.K.: Cambridge Univ. Press, 2016.
[4] M. Wang. F. Gao, S. Jin, and H. Lin, "An overview of enhanced massive MIMO with array signal processing techniques." IEEE J. Sel. Topics Signal Process., vol. 13, no. 5, pp. 886-901, Sep. 2019.
[5] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays." IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40-60. Jan. 2013.
[6] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[7] J. Rodríguez Sánchez, F. Rusek, O. Edfors, M. Sarajlic, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms." IEEE Trans. Signal Process., vol. 68, pp. 687-700, 2020.
[8] (2019). Common Public Radio Interface. [Online]. Available: http://www.cpri.info
[9] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
[10] K. Li. O. Castañeda, C. Jeon, J. R. Cavallaro, and C. Studer, "Decentralized coordinate-descent data detection and precoding for massive MU-MIMO," in Proc. IEEE Int. Symp. Circuits Syst. (ISCAS), May 2019, pp. 1-5.
[11] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "On the achievable rates of decentralized equalization in massive MU-MIMO systems," in Proc. IEEE Int. Symp. Inf. Theory (ISIT), Jun. 2017, pp. 1102-1106.
[12] H. Wang, A. Kosasih, C.-K. Wen, S. Jin, and W. Hardjawana, "Expectation propagation detector for extra-large scale massive MIMO." IEEE Trans. Wireless Commun., vol. 19, no. 3, pp. 2036-2051. Mar. 2020.
[13] Z. Zhang, H. Li, Y. Dong, X. Wang, and X. Dai, "Decentralized signal detection via expectation propagation algorithm for uplink massive MIMO systems," IEEE Trans. Veh. Technol., vol. 69, no. 10, pp. 11233-11240, Oct. 2020.
[14] A. Amiri, C. N. Manchón, and E. De Carvalho, "Uncoordinated and decentralized processing in extra-large MIMO arrays," IEEE Wireless Commun. Lett., vol. 11, no. 1, pp. 81-85, Jan. 2022.
[15] J. R. Sánchez, J. Vidal Alegría, and F. Rusek, "Decentralized massive MIMO systems: Is there anything to be discussed?" in Proc. IEEE Int. Symp. Inf. Theory (ISIT), Jul. 2019, pp. 787-791.
[16] Z. Zhang Y. Dong, K. Long, X. Wang, and X. Dai, "Decentralized baseband processing with Gaussian message passing detection for uplink massive MU-MIMO systems," IEEE Trans. Veh. Technol., vol. 71, no. 2, pp. 2152-2157, Feb. 2022.
[17] A. Kulkarni, M. A. Quameur, and D. Massicotte, "Hardware topologies for decentralized large-scale MIMO detection using Newton method," IEEE Trans. Circuits Syst. 1, Reg. Papers, vol. 68, no. 9, pp. 3732-3745, Sep. 2021.
[18] S. Cui, J. Zhang, J. Wang, and X. Gao, "Decentralized bidirectional-chain equalizer for massive MIMO," in Proc. IEEE 97th Veh. Technol. Conf. (VTC-Spring), Jun. 2023, pp. 1-7.
[19] J. V. Alegría and F. Rusek, "Trade-offs in decentralized multi-antenna architectures: Sparse combining modules for WAX decomposition," IEEE Trans. Signal Process., vol. 71, pp. 2879-2894, 2023.
[20] X. Zhao, M. Li, Y. Liu, T.-H. Chang, and Q. Shi, "Communication-efficient decentralized linear precoding for massive MU-MIMO systems." IEEE Trans. Signal Process., vol. 71. pp. 4045-4059, 2023.
[21] Y. Liu, T. F. Wong, and W. W. Hager, "Training signal design for estimation of correlated MIMO channels with colored interference," IEEE Trans. Signal Process., vol. 55, no. 4, pp. 1486-1497, Apr. 2007.
[22] S. Tomasin, R. Hasler, A. M. Tulino, and M. Sánchez-Fernández, "Estimation of interference correlation in mmWave cellular systems," 2023, arXiv:2304.14871.
[23] K. W. Helmersson, P. Frenger, and A. Helmersson, "Uplink D-MIMO with decentralized subset combining," in Proc. IEEE Int. Conf. Commun. (ICC), May 2022, pp. 5134-5139.
[24] Z. H. Shaik, E. Björnson, and E. G. Larsson, "MMSE-optimal sequential processing for cell-free massive MIMO with radio stripes," IEEE Trans. Commun., vol. 69, no. 11, pp. 7775-7789, Nov. 2021.
[25] D. P. Bertsekas, Nonlinear Programming. Cambridge, MA, USA: MIT Press, 1999.
[26] Y. Xu, B. Wang, E. Song. Q. Shi, and T.-H. Chang, "Low-complexity channel estimation for massive MIMO systems with decentralized baseband processing." 2022, arXiv:2210.15917.
[27] A. Rajoriya, R. Budhiraja, and L. Hanzo, "Centralized and decentralized channel estimation in FDD multi-user massive MIMO systems," IEEE Trans. Veh. Technol., vol. 71, no. 7. pp. 7325-7342, Jul. 2022.
[28] S. M. Kay. Fundamentals of Statistical Signal Processing: Estimation Theory. Upper Saddle River, NJ, USA: Prentice-Hall, 1993.
[29] G. Barriac and U. Madhow, "Space-time communication for OFDM with implicit channel feedback," IEEE Trans. Inf. Theory, vol. 50, no. 12, pp. 3111-3129, Dec. 2004.
[30] L.D. Schizas, G. B. Giannakis, and Z.-Q. Luo, "Distributed estimation using reduced-dimensionality sensor observations," IEEE Trans. Signal Process., vol. 55, no. 8, pp. 4284-4299, Aug. 2007.
[31] E. Song, Y. Zhu, and J. Zhou, "Sensors' optimal dimensionality compression matrix in estimation fusion," Automatica, vol. 41, no. 12, pp. 2131-2139, Dec. 2005.
[32] M. Hong. X. Wang, M. Razaviyayn, and Z.-Q. Luo, "Iteration complexity analysis of block coordinate descent methods," Math. Program., vol. 163, no. 1, pp. 85-114, May 2017.
[33] D. Sun, K.-C. Toh, and L. Yang, "An efficient inexact ABCD method for least squares semidefinite programming." SIAM J. Optim., vol. 26. no. 2, pp. 1072-1100, Jan. 2016.
[34] D. Bertsekas and J. Tsitsiklis, Parallel and Distributed Computation: Numerical Methods. Englewood Cliffs, NJ, USA: Prentice-Hall, 1989.
[35] C. Eckart and G. Young. "The approximation of one matrix by another of lower rank," Psychometrika, vol. 1, no. 3, pp. 211-218, Sep. 1936.
[36] W. Xu, Z. Yang, D. W. K. Ng, M. Levorato, Y. C. Eldar, and M. Debbah, "Edge learning for B5G networks with distributed signal processing: Semantic communication, edge computing, and wireless sensing," IEEE J. Sel. Topics Signal Process., vol. 17, no. 1, pp. 9-39, Jan. 2023.
[37] K. B. Petersen and M. S. Pedersen, "The matrix cookbook," Tech. Univ. Denmark, Lyngby, Denmark, Tech. Rep., 2006.

---

### Author Biographies

**Xiaotong Zhao** received the B.S. and M.S. degrees from the School of Mathematics, Sichuan University, Chengdu, China, in 2015 and 2020, respectively. He is currently pursuing the Ph.D. degree with the School of Software Engineering, Tongji University, Shanghai, China. His research interests include optimization theory and algorithms, and their applications to signal processing for wireless communications.

**Mian Li** received the B.S. degree from the Huazhong University of Science and Technology, Wuhan, China, in 2021. He is currently pursuing the Ph.D. degree with the School of Science and Engineering. The Chinese University of Hong Kong, Shenzhen, China. His research interests include optimization theory and algorithms, as well as machine learning theory and applications.

**Bo Wang** received the B.S. and Ph.D. degrees in information engineering from Xi'an Jiaotong University, Xi'an, China, in 2010 and 2017, respectively. He is currently with the Wireless Network RAN Algorithm Department, Xi'an Huawei Technologies Company Ltd. His research interests include signal processing techniques in wireless communication systems.

**Enbin Song** received the B.S. degree from Shandong Normal University, Jinan, China, in 2002, and the Ph.D. degree from Sichuan University, Chengdu, China, in 2007. From 2007 to 2009, he was a Post-Doctoral Researcher with the College of Computer Science. After that, he was an Associate Professor moved to the College of Mathematics, and since 2014, he has been a Full Professor. From 2010 to 2011, he was a Post-Doctoral Researcher with the Department of Electrical and Computer Engineering, University of Minnesota, Minneapolis, MN, USA. From 2013 to 2014, he was a Visiting Scholar with the Department of Systems Engineering and Engineering Management, The Chinese University of Hong Kong, Hong Kong, China. He is currently with Sichuan University. His research interests include information processing and nonlinear optimization with an emphasis on the design, analysis, and applications of optimization algorithms for multi-sensor estimation and decision fusion, statistics, and multiuser wireless communication. He was a recipient of the National Excellent Doctoral Dissertation Nomination Award in 2009.

**Tsung-Hui Chang** (Fellow, IEEE) received the B.S. degree in electrical engineering and the Ph.D. degree in communications engineering from National Tsing Hua University (NTHU), Hsinchu, Taiwan, in 2003 and 2008, respectively. He is currently a Professor and the Associate Dean (Education) of the School of Science and Engineering (SSE), The Chinese University of Hong Kong, Shenzhen (CUHK-SZ), China, and the Associate Director of Guangdong Provincial Key Laboratory of Big Data Computing. Before joining the CUHK-SZ, he was with the NTHU, the University of California, Davis, and the National Taiwan University of Science and Technology (NTUST), as a Post-Doctoral Researcher and a Faculty Member, respectively. His research interests include signal processing and optimization methods for data communications and machine learning. He has been an Elected Member of the IEEE Signal Processing Society (SPS) Signal Processing for Communications and Networking Technical Committee (SPCOM TC) since January 2020. He received the Young Scholar Research Award of NTUST in 2014, the IEEE ComSoc Asian-Pacific Outstanding Young Researcher Award in 2015, the IEEE SPS Best Paper Awards in 2018 and 2021, and the Outstanding Faculty Research Award of SSE of CUHK-SZ in 2021. He is the Founding Chair of the IEEE SPS Integrated Sensing and Communication Technical Working Group (ISAC TWG). He has been the elected Regional Director-at-Large of Board of Governors of IEEE SPS since 2022. He has served on the editorial board for major SP journals, including an Associate Editor for IEEE TRANSACTIONS ON SIGNAL PROCESSING from August 2014 to December 2018, IEEE TRANSACTIONS ON SIGNAL AND INFORMATION PROCESSING OVER NETWORKS from January 2015 to December 2018, IEEE OPEN JOURNAL OF SIGNAL PROCESSING since January 2020, and a Senior Area Editor for IEEE TRANSACTIONS ON SIGNAL PROCESSING since February 2021.

**Qingjiang Shi** (Member, IEEE) received the Ph.D. degree in electronic engineering from Shanghai Jiao Tong University, Shanghai, China, in 2011. From September 2009 to September 2010, he visited Prof. Z.-Q. (Tom) Luo's Research Group. University of Minnesota, Twin Cities, MN, USA. In 2011, he was a Research Scientist with the Bell Laboratories, China. Since 2012, he has been with the School of Information and Science Technology, Zhejiang Sci-Tech University. From February 2016 to March 2017, he was a Research Fellow with Iowa State University, Ames, IA, USA. Since March 2018, he has been a Full Professor with the School of Software Engineering, Tongji University, Shanghai, China. He is also with Shenzhen Research Institute of Big Data. He has published more than 80 IEEE journals and filed about 40 national patents. His research interests include algorithm design and analysis with applications in machine learning, signal processing, and wireless networks. He was a recipient of the IEEE Signal Processing Society Best Paper Award in 2022, the Second Prize of Zhejiang Provincial Natural Science Award in 2023, the Excellent Technical Cooperation Award From Huawei Wireless Network Product Line in 2024, the Huawei Technical Cooperation Achievement Transformation Award (2nd Prize) in 2022, the Huawei Outstanding Technical Achievement Award in 2021, the Golden Medal at the 46th International Exhibition of Inventions of Geneva in 2018, the First Prize of Science and Technology Award from China Institute of Communications in 2017, the National Excellent Doctoral Dissertation Nomination Award in 2013, Shanghai Excellent Doctoral Dissertation Award in 2012, and the Best Paper Award from the IEEE PIMRC'09 Conference. He has served on the editorial board of IEEE TRANSACTIONS ON SIGNAL PROCESSING as an Associate Editor.