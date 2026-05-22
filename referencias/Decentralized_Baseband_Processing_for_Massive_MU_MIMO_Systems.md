# Decentralized Baseband Processing for Massive MIMO Systems Under Decentralized Baseband Processing Architecture
Abstract:
Recently, the decentralized baseband processing (DBP) paradigm and relevant uplink detection methods have been proposed to enable extremely large-scale massive multiple-input multiple-output technology. Under the DBP architecture, base station antennas are divided into several independent clusters, each connected to a local computing fabric. However, current detection methods tailored to DBP only consider ideal white Gaussian noise scenarios, while in practice, the noise is often colored due to interference from neighboring cells. Moreover, in the DBP architecture, linear minimum mean-square error (LMMSE) detection methods require the knowledge of noise covariance matrix which must be estimated using distributedly stored noise samples. This presents a significant challenge for decentralized LMMSE-based equalizer design. To address this issue, this paper proposes decentralized LMMSE equalization methods under colored noise scenarios for both star and daisy chain DBP architectures. Specifically, we first propose two decentralized equalizers for the star DBP architecture based on dimensionality reduction techniques. Then, we derive an optimal decentralized equalizer using the block coordinate descent method for the daisy chain DBP architecture with a bandwidth reduction enhancement scheme based on decentralized low-rank decomposition. Finally, simulation results demonstrate that our proposed methods can achieve excellent detection performance while requiring much less communication bandwidth.

SECTION I.Introduction
Massive multiple-input multiple-output (MIMO) is a critical technology for both fifth-generation (5G) and sixth-generation systems due to its high spectral and power efficiency [2], [3], [4]. With extremely large-scale antenna arrays comprising hundreds or even thousands of antennas, a base station (BS) is capable of simultaneously serving multiple user equipments (UEs) within the same time-frequency resource. Data detection techniques are crucial in the uplink of massive MIMO systems. While the optimal detector is the nonlinear maximum-likelihood detector [5], its complexity grows exponentially with the number of transmit antennas, rendering it impractical for real-world systems. Consequently, low-complexity linear equalization-based detection methods such as maximum ratio combining (MRC), zero-forcing (ZF), and linear minimum mean-square error (LMMSE) detectors are preferred. Among these methods, the LMMSE detector is widely adopted due to its near-optimal detection performance [5].

Conventional LMMSE detection in practical massive MIMO systems relies on centralized baseband processing (CBP) in a single computing fabric, as shown in Fig. 1. However, extremely large antenna array in the next generation wireless systems poses two major challenges: 1) Excessive communication bandwidth: The rapid growth in the number of BS antennas results in an exceedingly high amount of raw baseband data, including channel state information (CSI), received signal, and noise samples (for noise covariance estimation), that must be transferred between the radio-frequency (RF) chains and the centralized computing fabric shown in Fig. 1 with red arrow lines [6], [7]. This issue is evident in a 256-antenna BS with an 80MHz bandwidth and 12-bit digital-to-analog converters, where the raw baseband data throughput reaches 1Tbps, greatly exceeding the existing capacity of BS internal interface standards [8]. 2) High computational complexity: Traditional LMMSE equalization requires a high-dimensional matrix inversion with a complexity cubic in the number of BS antennas. This results in a formidable requirement for computation capability, making the CBP architecture impractical for massive MIMO settings [6].

Fig. 1.
Block diagram of a centralized baseband processing architecture for the massive MU-MIMO uplink. “CHEST” is short for channel estimation.

To address the limitations of traditional CBP architectures, recent studies have explored a promising next-generation transceiver architecture called decentralized baseband processing (DBP) [6], [7], [9], [10], [11], [12], [13], [14], [15], [16], [17], [18], [19], [20]. As shown in Fig. 2, DBP replaces the centralized computing fabric with multiple local computing fabrics called distributed units (DUs). Additionally, the BS antennas are divided into several independent clusters, each connected to a DU. The DUs communicate with each other through a topology such as a star or a daisy chain, as shown in Fig. 2(a) and (b), respectively. As a result, each DU stores local information like CSI, received signals, and noise/interference samples. This setup enables decentralized data detection with moderate information exchange among DUs. Compared to CBP, the DBP paradigm effectively mitigates bandwidth and computation bottlenecks.


Fig. 2.
The DBP architectures in which the received signal y and each noise sample ni are both distributed over multiple DUs.

Numerous studies have investigated detection and equalization designs in DBP architectures. To simplify the complicated matrix inversion in centralized ZF and LMMSE equalizers, decentralized iterative methods were proposed. These methods, such as conjugate gradient [6], alternating direction method of multipliers [6], coordinate descent [10], and Newton methods [17], combined the local matched filter, local Gram matrix, and intermediate variables in a decentralized manner. Maximum a posterior estimation-based decentralized detection algorithms, such as large-MIMO approximate message passing [11], expectation propagation [12], [13], and Gaussian message passing [16], were proposed to attain higher detection performance at the expense of increased computational complexity. Notably, all the aforementioned methods aimed to estimate symbols rather than obtain an equalization matrix directly. However, equalization methods have a significant advantage over symbol estimation methods: the equalization matrix can be reused across multiple coherence blocks of channels. In contrast, the symbol estimation algorithms mentioned above must be performed for each channel, resulting in high computational complexity and communication bandwidth. Given this consideration, the authors in [9] presented a decentralized implementation that directly obtained MRC, ZF, and LMMSE equalization matrices in a feedforward DBP architecture. Meanwhile, a decentralized algorithm based on gradient descent was proposed in [7] to obtain the ZF equalization matrix for a daisy chain architecture. Recently, [18] proposed a parallel iterative MMSE equalizer in a decentralized bidirectional-chain equalizer architecture.

Prior works [6], [7], [9], [10], [11], [12], [13], [14], [15], [16], [17], [18], and [19] all assumed that the BS receiver noise follows an ideal additive white Gaussian noise (AWGN) model with a diagonal covariance matrix. This naturally facilitates the distributed implementation of LMMSE equalization in DBP architectures using multiple diagonal submatrices. However, in practical systems, interference from other non-target UEs in neighboring cells must be modeled as part of the background noise [21], [22], i.e., results in colored noise with a non-diagonal covariance matrix.1 Moreover, the exact noise covariance matrix at the BS is unknown and needs to be estimated by averaging a finite number of noise samples. In DBP architectures (see Fig. 2 below), each DU has only local noise samples for the corresponding antenna cluster. Consequently, computing the non-diagonal covariance matrix of colored noise requires collecting noise samples from all clusters. However, this is hampered by prohibitively high communication bandwidth and computational complexity, as the sample dimension is related to the number of BS antennas (which can be extremely large). Therefore, LMMSE equalization in DBP architectures under the colored noise remains a significant challenge, necessitating a completely new algorithmic design that considers limited communication bandwidth and low computational complexity. This paper seeks to address this challenge.

In summary, our main contributions are given as follows:
* Colored Noise and Covariance Estimation in DBP. To the best of our knowledge, all the existing detection methods designed for DBP focus solely on ideal white Gaussian noise scenarios. We here for the first time consider the more practical colored noise case. Particularly, for the DBP architectures, we show how to efficiently and implicitly implement decentralized estimation of the noise covariance matrix during the LMMSE process through averaging distributedly stored noise samples.

* Decentralized Equalization for the Star DBP Architecture. By investigating the closed-form expression for the LMMSE equalization matrix, we propose two decentralized equalizers that employ dimensionality reduction (DR) techniques under the star DBP architecture. In both methods, each DU embeds its local information into a low-dimensional representation via linear transformation and transmits it to the CU. The CU then either superimposes or concatenates the compressed data to perform LMMSE equalization. Both methods reduce data transfer size from the number of BS antennas to the number of UEs, alleviating the bandwidth and computation bottlenecks, while achieving performance close to centralized LMMSE equalization.

* Decentralized Equalization for the Daisy Chain DBP Architecture. To obtain an optimal decentralized equalizer, we reshape the original optimization problem of LMMSE and investigate the distributed storage structure in the daisy chain DBP architecture. Then, we design an efficient decentralized iterative algorithm using the block coordinate descent (BCD) method [25] with guaranteed convergence. During the BCD iteration, data transfer size is significantly reduced, depending only on the number of UEs rather than BS antennas. To further reduce the data transfer size for the case when the number of noise samples is very large, we present an improved BCD-based decentralized LMMSE equalizer by deliberately using a low-rank approximation of the noise covariance matrix. While preserving near-optimal performance, this approach requires the data transfer size independent of the number of noise samples, significantly reducing the bandwidth and computation burden.

The remainder of this paper is organized as follows. Section II introduces the uplink system model and the DBP architectures. Section III proposes two decentralized equalization methods using DR techniques for the star architecture. Section IV develops a BCD-based decentralized equalization method for the daisy chain architecture and a low-rank decomposition scheme for noise covariance matrix to further reduce the communication bandwidth. Section V presents computational complexity and communication bandwidth analysis. The simulation results are provided in Section VI. Finally, this article is concluded in Section VII.

Notations: Throughout this paper, scalars are denoted by both lower and upper case letters, while vectors and matrices are denoted by boldface lower case and boldface upper case letters, respectively. For a matrix A, AT , AH , A−1 , Tr(A) and R(A) denote its transpose, conjugate transpose, inverse, trace, and range space, respectively. The Euclidean norm of a vector x is defined as ∥x∥2=xHx−−−−√ . In addition, E[⋅] denotes the expectation operation. The notation I is the identity matrix, and blkdiag(A1,…,AC) denotes a block diagonal matrix with A1,…,AC being its diagonal blocks.



SECTION II.Systems Model and DBP Architectures
This section introduces the uplink massive MIMO system model and the LMMSE equalization method. Two uplink DBP architectures are then presented along with the challenges posed by the decentralized LMMSE design.

A. Uplink System Model and LMMSE Equalization
1) Uplink System Model:
Consider an uplink massive MIMO system where K target UEs, each with a single antenna, transmit data to a BS equipped with M antennas, where M≫K . The received signal y∈CM×1 at the BS is expressed as:
\begin{equation*} \mathbf {y}=\mathbf {H}\mathbf {s}+\mathbf {n}, \tag {1}\end{equation*}
where H∈CM×K represents the channel matrix between the BS and UEs, s∈SK×1 denotes the transmitted symbol vector with S representing the constellation set for some modulation scheme (e.g., 16-QAM), and n∼CN(0,R) denotes the additional white Gaussian noise (AWGN) with R≜E[nnH] being the covariance matrix.

2) LMMSE Equalization:
Typically, the CSI is considered almost constant across several contiguous symbols [15], which enables the reuse of the equalization matrix. Consequently, it is more cost-effective to compute the equalization matrix and reuse it, rather than estimating symbols directly for each instance. Therefore, we focus on obtaining an equalization matrix instead of directly estimating symbols.

Assuming the channel matrix H is perfectly known,2 LMMSE equalization aims to find a linear estimate by solving the following problem:
\begin{equation*} \min _{\mathbf {W}} \quad \mathbb {E}\left [{{\left \|{{ \mathbf {W} \mathbf {y}-\mathbf {s} }}\right \|_{2}^{2}}}\right ], \tag {2}\end{equation*}

which leads to the well-known LMMSE receiver [28]:
\begin{equation*} \mathbf {W}_{\text {MMSE}} =\left ({{\mathbf {H}^{H}\mathbf {R}^{-1}\mathbf {H}+\frac {1}{E_{s}}\mathbf {I}}}\right )^{-1}\mathbf {H}^{H}\mathbf {R}^{-1}, \tag {3}\end{equation*}
where Es denotes the average energy per symbol. The LMMSE estimate s^MMSE is obtained by applying the equalization matrix WMMSE to the received signal y, i.e., s^MMSE=WMMSEy . Finally, the detector quantizes each entry of s^MMSE to the nearest neighbor point in the constellation set S .

In conventional centralized LMMSE equalization, computing the equalization matrix in (3) requires complete knowledge of H∈CM×K and R∈CM×M , which must be collected from the RF chains to a centralized computing fabric. Furthermore, the M-dimensional matrix inversion operation R−1 in (3) results in a computational complexity of O(M3) . Consequently, centralized processing imposes significant bandwidth and computational demands that are unaffordable when M is extremely large in massive MIMO settings. This motivates the decentralized design of the LMMSE equalization under certain decentralized baseband processing architecture, which is introduced in the sequel.

B. Decentralized Baseband Processing: Architectures, Challenges, and A Baseline Solution
1) DBP Architectures:
To address the complexity and bandwidth issues of traditional CBP architectures, recent studies (e.g., [6], [7]) have explored the DBP architecture. As illustrated in Fig. 2, the uplink DBP architecture divides M BS antenna elements into C antenna clusters each with Mc antennas (i.e., ∑Cc=1Mc=M ). In particular, each cluster has its own local RF and computing fabric called DU.

In this paper, we consider two DBP architectures: the star architecture in Fig. 2(a) and the daisy chain architecture in Fig. 2(b). In the star architecture, all DUs are connected to a central unit (CU), and each DU performs data compression and subsequently transmits some message (i.e., intermediate results as required) to the CU in parallel for the final equalization operation. In contrast to the star architecture, there is no CU in the daisy chain architecture. Instead, the DUs are connected via unidirectional links, while an additional link connects the last and first DUs to form a ring. Only one DU outputs the symbol estimate and is directly linked to the decoder.

The star architecture requires a higher communication bandwidth between the CU and DUs, resulting in complex chip input/output interfaces at the CU. Nevertheless, the star architecture has less latency than the daisy chain architecture since the star architecture enables parallel processing. In contrast, the interface design in the daisy chain architecture is simple, low-cost, and easier to extend but often has higher latency.

Under the DBP architectures, the received vector, channel matrix, and noise vector in Eq. (1) are accordingly partitioned as y=[yT1,yT2,…,yTC]T , H=[HT1,HT2,…,HTC]T , and n=[nT1,nT2,…,nTC]T , respectively. Therefore, the local received signal yc∈CMc×1 at cluster c is represented by
\begin{equation*} \mathbf {y}_{c}=\mathbf {H}_{c} \mathbf {s}+\mathbf {n}_{c}, \quad c=1,2, \ldots , C, \tag {4}\end{equation*}

where Hc∈CMc×K and nc∈CMc×1 denote the local channel matrix and the local noise vector with respect to cluster c, respectively. Note that, Hc and yc are only known locally to the DU c and are not allowed to be directly exchanged among DUs to save bandwidth overhead.

2) Challenges Imposed by DBP on Decentralized LMMSE:
Previous works on decentralized equalization under DBP architectures all assumed AWGN noise with diagonal covariance matrix [6], [7], [9], [10], [11], [12], [13], [14], [15], [16], [17]. Under such an assumption, the noise covariance matrix can be naturally decomposed into multiple block diagonal submatrices that perfectly fit into the decentralized implementation of LMMSE equalization under DBP architectures.3 However, the noise at the BS is often colored due to the existence of interference signals from non-target UEs in neighboring cells [21], [22]. In interference scenarios, the baseband model in (1) can be expressed in more detail as follows:
\begin{equation*} \mathbf {y}=\mathbf {H}\mathbf {s}+\underbrace {\mathbf {n}}_{\text {colored noise}}=\mathbf {H}\mathbf {s}+\underbrace {\bar {\mathbf {H}}\bar {\mathbf {s}}}_{\text {interference}}+ \underbrace {\bar {\mathbf {n}}}_{\text {AWGN}}, \tag {5}\end{equation*}

where H¯∈CM×r and s¯∈Sr×1 respectively denote the channel matrix and interference signals of r non-target UEs, and n¯∈CM×1 is the background AWGN with distribution CN(0,σ2I) . Then, the colored noise covariance matrix R=βH¯H¯H+σ2I , where β is the power of interference signals. In this scenario, R becomes non-block-diagonal. Moreover, the decentralized estimation of R is not possible because directly exchanging interference signals among DUs is forbidden due to bandwidth limitation. This imposes a huge challenge for decentralized LMMSE equalization design.


To better understand the challenge mentioned above, we write down the best estimation4 of R as [21], [22], and [29]:
\begin{equation*} \hat {\mathbf {R}}=\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}(\mathbf {n}^{i})^{H}, \tag {6}\end{equation*}

which is done by averaging the noise samples in N pilot resource elements (REs). Here, N≫K holds to ensure the accuracy of estimation, and ni∈CM×1 is the noise sample in the i-th pilot RE.5

Corresponding to the antennas clustering in DBP architectures, the i-th noise sample ni can be divided as ni=[(ni1)T,(ni2)T,…,(niC)T]T,∀i , where {nic}Ni=1 are stored in cluster c (illustrated with orange color in Fig. 3). Similarly, the noise covariance matrix R can be regarded as a block matrix with C×C blocks, where the (m,n) -th block submatrix is denoted by Rmn=E[nmnHn] . Accurate estimation of R is crucial for effective LMMSE equalization. However, only the diagonal blocks of R (denoted by R^cc as illustrated in yellow in Fig. 3) can be locally estimated by each cluster c using R^cc=(1/N)∑Ni=1nic(nic)H . The main challenge lies in accurately obtaining the off-diagonal blocks of R (i.e., Rmn,m≠n illustrated in blue in Fig. 3). Note that the direct exchange of noise samples among DUs would result in high-dimensional data transfer with size M×N , which is prohibited for massive MIMO scenarios. Moreover, traditional whitening noise methods cannot be applied because they don’t allow distributed implementation in DBP. As a result, decentralized computation of the LMMSE equalization matrix in (3) under stringent bandwidth constraints poses a significant challenge.
Fig. 3.
An illustrative example of the colored noise assumption in a DBP architecture with C=4 . The computation of off-diagonal blocks of R requires data transfer among DUs.
3) A Baseline Solution:
We first propose a straightforward solution to roughly tackle this challenge, i.e., approximating R with a block diagonal matrix, denoted by RB≜blkdiag(R11,R22,…,RCC) , where all off-diagonal blocks are set to zero. Here, blkdiag(A1,…,AC) denotes a block diagonal matrix with A1,…,AC being its diagonal blocks. This approach enables the approximation of the LMMSE equalization matrix in (3) as
\begin{align*} & \hspace {-.5pc}\left ({{\mathbf {H}^{H}\mathbf {R}_{\text {B}}^{-1}\mathbf {H}+\frac {1}{E_{s}}\mathbf {I}}}\right )^{-1}\mathbf {H}^{H}\mathbf {R}_{\text {B}}^{-1} \\ & {=}\left ({{\sum _{c=1}^{C}\mathbf {H}_{c}^{H}\mathbf {R}_{cc}^{-1}\mathbf {H}_{c}{+}\frac {1}{E_{s}}\mathbf {I}\!}}\right )^{-1}\!\!\! \left [{{ \mathbf {H}_{1}^{H}\mathbf {R}_{11}^{-1}, {\ldots },\mathbf {H}_{C}^{H}\mathbf {R}_{CC}^{-1} }}\right ]. \tag {7}\end{align*}

It is possible to implement (7) in a decentralized manner. Specifically, each DU c=1,2,…,C first computes HHcR−1ccHc locally, which is then collected together for summation and inversion operations. Finally, the matrix inverse result is broadcasted to all DUs, allowing them to compute their local equalization matrices. This decentralized implementation of obtaining the approximate equalization matrix in (7) is called the block diagonal approximate covariance MMSE (BDAC-MMSE) equalizer. The transfer of only low-dimensional matrices with size K×K requires minimal communication bandwidth. Note that this simple approximation leads to a performance loss in colored noise scenarios. Therefore, algorithms with better performance will be proposed in the following sections. Nevertheless, BDAC-MMSE can serve as a good initial point for our proposed decentralized BCD-based equalizers in Section IV, as well as a baseline algorithm.

Remark 1::Recent works [23], [24] have investigated the design of MMSE receivers for cell-free massive MIMO systems under colored noise conditions, where geographically separated access points (APs) jointly receive signals from all mobile users. In this scenario, the APs can be seen as the DU in the DBP architecture. However, their problem formulations differ significantly from ours. Specifically, they considered colored noise caused by channel estimation error and employed a Kalman filtering-based method to provide a sequential implementation of centralized LMMSE using local noise covariance matrices. However, they assumed that the noise covariance matrix is a block diagonal matrix comprising multiple local covariance matrices, with each decentralized node having knowledge of its corresponding local covariance matrix. Consequently, the algorithms proposed in [23] and [24] for colored noise with block-diagonal covariance matrix are not suitable for our decentralized LMMSE equalization problem with more general noise covariance matrix.

SECTION III.Dimensionality Reduction MMSE Equalization for Star DBP Architecture
This section introduces the DR technique for the star DBP architecture and formulates the LMMSE problem under two types of compression matrices. Then, two DR-based decentralized equalization methods are designed.

A. Dimensionality Reduction in DBP
To reduce the bandwidth burden in DBP architectures, a straightforward idea is to reduce the dimension of local information while preserving equalization performance, which matches the concept of the DR technique [30], [31]. Specifically, in the star DBP architecture, through a fat local compression matrix Qc∈CLc×Mc , where Lc < Mc , each DU parallelly transfers the compressed local received vector Qcyc , channel matrix QcHc , and noise samples {Qcnic}Ni=1 to the CU. Based on these compressed data, an LMMSE estimate of s is formed through an equalization matrix W. Since Lc < Mc , the bandwidth can be significantly reduced. We assume local compression dimension Lc=L for brevity.

The compression matrix can be an arbitrary fat matrix. For the star DBP architecture, we focus on the following two scenarios of compression matrices:

Superimposed Compression: The compressed received signals from each DU are superimposed at the CU as
\begin{equation*} \tilde {\mathbf {y}}\left ({{\mathbf {Q}_{1},\ldots ,\mathbf {Q}_{C}}}\right ) = \sum _{c=1}^{C}\mathbf {Q}_{c}\mathbf {y}_{c}= \left [{{ \mathbf {Q}_{1}, \ldots ,\mathbf {Q}_{C} }}\right ]\mathbf {y}. \tag {8}\end{equation*}
Concatenated Compression: The CU concatenates the compressed data of individual DUs to form a vector
\begin{equation*} \tilde {\mathbf {y}}\left ({{\mathbf {Q}_{1},\ldots ,\mathbf {Q}_{C}}}\right ) = \text {blkdiag}(\mathbf {Q}_{1},\ldots ,\mathbf {Q}_{C})\mathbf {y}. \tag {9}\end{equation*}
The dimension of y~(Q1,…,QC) in the superimposed and concatenated scenarios are L×1 and CL×1 , respectively. [Q1,…,QC] and blkdiag(Q1,…,QC) are global compression matrices. For both scenarios, we aim to design MSE optimal equalization matrices W~ and local compression matrices {Qc}Cc=1 as follows:
\begin{equation*} \min _{\tilde {\mathbf {W}},\{\mathbf {Q}_{c}\}_{c=1}^{C}} \quad \mathbb {E}\left [{{\left \|{{ \mathbf {s} - \tilde {\mathbf {W}}\tilde {\mathbf {y}}(\mathbf {Q}_{1},\ldots ,\mathbf {Q}_{C}) }}\right \|_{2}^{2}}}\right ], \tag {10}\end{equation*}

where y~(Q1,…,QC) is given by either (8) or (9). In general, concatenating has a better performance but with higher complexity compared to superimposing. Although many articles have investigated problem (10), they all assumed that the statistical properties of the signal and noise are available at a central node [30], [31]. However, the biggest challenge in this paper is that the non-diagonal noise covariance matrix can only be estimated by the noise samples, which are separately stored at each DU. Thus, the global optimization methods in [31] for problem (10) will inevitably lead to a heavy bandwidth burden. Consequently, we need to reconsider the problem (10) and find a reasonable approximate solution with the trade-off between bandwidth and performance. Since the optimal W~ in problem (10) is obviously given by the LMMSE solution after {Qc}Cc=1 are obtained, we will focus on the design of compression matrices {Qc}Cc=1 .

A fundamental question is, under what conditions the compression is lossless? Here, lossless means no MSE performance gap exists between performing LMMSE equalization with compressed and uncompressed information. The following theorem answers this question:

Theorem 1::Consider system model (1), i.e., y=Hs+n . Denote Q∈CL×M as the global compression matrix. The minimal compression dimension without performance loss is rank(H)=K , and Q=PHHR−1∈CK×M for an arbitrary invertible matrix P∈CK×K is a lossless compression matrix.
Proof:See Appendix A.■
Following Theorem 1, setting P=I results in a lossless compression matrix HHR−1∈CK×M . However, this cannot be utilized directly for the DBP architectures because R−1 is unavailable without collecting {nic}Ni=1 from each DU to the CU, which is infeasible due to bandwidth limitations. Therefore, we use a lossy compromise by using Qc=HHcR−1cc∈CK×Mc as a local compression matrix at each DU c. The following subsections show that it will be a lossless local compression matrix when R=RB , and simulation results confirm its effectiveness. The subsequent two subsections derive the compression matrices and corresponding equalization methods for different scenarios.

B. Superimposed DR-MMSE Equalization
We first consider the superimposed scenario. Adopting Qc=HHcR−1cc as the local compression matrix at DU c, the global superimposed compression matrix is given by
\begin{align*} \check {\mathbf {Q}}& =[\mathbf {Q}_{1}, \mathbf {Q}_{2}, \ldots , \mathbf {Q}_{C}] \\ & = [\mathbf {H}_{1}^{H}\mathbf {R}_{11}^{-1}, \mathbf {H}_{2}^{H}\mathbf {R}_{22}^{-1}, \ldots , \mathbf {H}_{C}^{H}\mathbf {R}_{CC}^{-1}] \\ & =\mathbf {H}^{H}\mathbf {R}_{\text {B}}^{-1}, \tag {11}\end{align*}

which is an approximation to the lossless compression matrix HHR−1 . Applying the compression to (1), we obtain the effective compressed channel model at the CU as
\begin{equation*} \check {\mathbf {y}}= \check {\mathbf {H}}\mathbf {s}+\check {\mathbf {n}}, \tag {12}\end{equation*}
where
\begin{align*} \check {\mathbf {y}}& =\check {\mathbf {Q}} \mathbf {y} = \sum _{c=1}^{C} \mathbf {Q}_{c}\mathbf {y}_{c},~\check {\mathbf {H}}=\check {\mathbf {Q}} \mathbf {H} = \sum _{c=1}^{C} \mathbf {Q}_{c}\mathbf {H}_{c}, \tag {13a}\\ ~\check {\mathbf {n}}& =\check {\mathbf {Q}} \mathbf {n} =\sum _{c=1}^{C}\mathbf {Q}_{c}\mathbf {n}_{c}. \tag {13b}\end{align*}
The effective noise covariance matrix can be expressed by
\begin{align*} \check {\mathbf {R}} & =\check {\mathbf {Q}}\mathbf {R}\check {\mathbf {Q}}^{H} = \check {\mathbf {Q}} \left ({{ \frac {1}{N}\sum _{i=1}^{N} \mathbf {n}^{i}\left ({{\mathbf {n}^{i}}}\right )^{H} }}\right )\check {\mathbf {Q}}^{H} \\ & = \sum _{m=1}^{C}\sum _{l=1}^{C} \left ({{ \mathbf {Q}_{m} \left ({{ \frac {1}{N}\sum _{i=1}^{N} \mathbf {n}^{i}_{m}\left ({{\mathbf {n}^{i}_{l}}}\right )^{H} }}\right ) \mathbf {Q}_{l}^{H} }}\right ) \\ & = \frac {1}{N}\sum _{m=1}^{C}\sum _{l=1}^{C}\sum _{i=1}^{N} \mathbf {Q}_{m}\mathbf {n}^{i}_{m}(\mathbf {Q}_{l}\mathbf {n}^{i}_{l})^{H}. \tag {14}\end{align*}
After the low-dimensional compressed information Qcyc,QcHc , and {Qcnic}Ni=1 are collected from all the DUs, the CU calculates the equalization matrix as follows:
\begin{equation*} \mathbf {W}_{\text {sDR-MMSE}} = \left ({{ \check {\mathbf {H}}^{H}\check {\mathbf {R}}^{-1}\check {\mathbf {H}} + \frac {1}{E_{s}}\mathbf {I} }}\right )^{-1} \check {\mathbf {H}}^{H}\check {\mathbf {R}}^{-1}, \tag {15}\end{equation*}
and the estimated symbol is given by
\begin{equation*} \hat {\mathbf {s}}_{\text {sDR-MMSE}}=\mathbf {W}_{\text {sDR-MMSE}}\check {\mathbf {y}}. \tag {16}\end{equation*}


The proposed algorithm, named superimposed dimensionality reduction (sDR)-MMSE, is summarized in Algorithm 1. In the preprocessing phase, Qcyc , QcHc and {Qcnic}Ni=1 are calculated locally at each DU and then transmitted to the CU. Later in the equalization phase, the compressed information is superimposed to obtain the equalization matrix in (15). Finally, multiplying the compressed received signal provides the estimate of s in (16). Fig. 4 illustrates the information transfer in the proposed sDR-MMSE equalization. The data transfer size is independent of the number of BS antennas.

Fig. 4.
The communication and computation operations during the sDR-MMSE equalization process.

Algorithm 1 The Proposed sDR-MMSE Equalization
Input:
yc,Hc,{nic}Ni=1,c=1,2,…,C , and Es .

1:
Decentralized preprocessing at each DU:

2:
for c=1 to C do

3:
Qc←HHcR−1cc ;

4:
Compute Qcyc , QcHc , and {Qcnic}Ni=1 ; // Send to CU

5:
end for

6:
Central processing at the CU:

7:
Compute yˇ and Hˇ via (13);

8:
Compute Rˇ via (14);

9:
WsDR-MMSE is given by (15);

10:
s^sDR-MMSE is given by (16);

Output:
WsDR-MMSE and s^sDR-MMSE .

Remark 2:Since HHR−1 is a lossless compression matrix, the sDR-MMSE equalization is equivalent to the centralized LMMSE equalization when R=RB . Moreover, the performance degradation caused by compression will be minor if the off-diagonal elements of R are relatively small compared to the diagonal part. Fortunately, noise covariance matrix R often tends to block diagonally dominant in practical scenarios.
C. Concatenated DR-MMSE Equalization
The sDR-MMSE equalization results in information loss due to the superimposition of information from each DU. A potential approach to improve performance is to concatenate compressed information instead of superimposing, although this comes at the cost of increased complexity. Therefore, we consider scenario 2) of the compression matrix in (9).

We still adopt the local compression matrix as Qc=HHcR−1cc at the c-th DU. But different from (11), the global concatenated compression matrix is given by

\begin{align*} \tilde {\mathbf {Q}}& = \text {blkdiag} \left ({{\mathbf {Q}_{1}, \mathbf {Q}_{2}, \ldots , \mathbf {Q}_{C}}}\right ) \\ & =\text {blkdiag} \left ({{\mathbf {H}_{1}^{H}\mathbf {R}_{11}^{-1}, \mathbf {H}_{2}^{H}\mathbf {R}_{22}^{-1}, \ldots , \mathbf {H}_{C}^{H}\mathbf {R}_{CC}^{-1}}}\right ). \tag {17}\end{align*}

Thus, the effective channel model at the CU is given by
\begin{equation*} \tilde {\mathbf {y}}= \tilde {\mathbf {H}}\mathbf {s}+\tilde {\mathbf {n}}, \tag {18}\end{equation*}
where
\begin{align*} \tilde {\mathbf {y}} {=}\! \left [{{\begin{array}{c} \mathbf {Q}_{1}\mathbf {y}_{1} \\ \vdots \\ \mathbf {Q}_{C}\mathbf {y}_{C} \\ \end{array}}}\right ],~\tilde {\mathbf {H}} {=} \! \left [{{\begin{array}{c} \mathbf {Q}_{1}\mathbf {H}_{1} \\ \vdots \\ \mathbf {Q}_{C}\mathbf {H}_{C} \\ \end{array}}}\right ],~\tilde {\mathbf {n}} {=}\! \left [{{\begin{array}{c} \mathbf {Q}_{1}\mathbf {n}_{1} \\ \vdots \\ \mathbf {Q}_{C}\mathbf {n}_{C} \\ \end{array}}}\right ]. \tag {19}\end{align*}
The effective noise covariance matrix can be expressed by
\begin{align*} \mathbf {Q}_{m}\mathbf {R}_{ml}\mathbf {Q}^{H}_{l} & = \mathbf {Q}_{m}\left ({{ \frac {1}{N}\sum _{i=1}^{N} \mathbf {n}^{i}_{m}\left ({{\mathbf {n}^{i}_{l}}}\right )^{H} }}\right )\mathbf {Q}^{H}_{l} \\ & =\frac {1}{N}\sum _{i=1}^{N} \mathbf {Q}_{m}\mathbf {n}^{i}_{m}\left ({{\mathbf {Q}_{l}\mathbf {n}^{i}_{l}}}\right )^{H}. \tag {21}\end{align*}

Consequently, after collecting the compressed information Qcyc,QcHc , and {Qcnic}Ni=1 from all the DUs, the CU calculates the equalization matrix as follows:
\begin{equation*} \mathbf {W}_{\text {cDR-MMSE}} = \left ({{ \tilde {\mathbf {H}}^{H}\tilde {\mathbf {R}}^{-1}\tilde {\mathbf {H}} + \frac {1}{E_{s}}\mathbf {I} }}\right )^{-1} \tilde {\mathbf {H}}^{H}\tilde {\mathbf {R}}^{-1}, \tag {22}\end{equation*}
and the estimated symbol is given by
\begin{equation*} \hat {\mathbf {s}}_{\text {cDR-MMSE}}=\mathbf {W}_{\text {cDR-MMSE}}\tilde {\mathbf {y}}. \tag {23}\end{equation*}
The resulting algorithm is called concatenated dimensionality reduction (cDR)-MMSE equalization and is summarized in Algorithm 2. The preprocessing stage of cDR-MMSE equalization is the same as that of sDR-MMSE equalization, i.e., Qcyc , QcHc and {Qcnic}Ni=1 are calculated locally at each DU and then sent to the CU. Whereas at the CU, the compressed information is concatenated to obtain the LMMSE equalization matrix in (22) instead of being superimposed. The information transfer of the cDR-MMSE equalization is identical to that of the sDR-MMSE equalization illustrated in Fig. 4, except that the central processing at the CU should be replaced by (22) and (23).

The cDR-MMSE equalizer outperforms the sDR-MMSE equalizer due to the concatenation operation. Proposition 1 provides a rigorous analysis of this performance improvement. However, the cDR-MMSE equalizer has a higher computational complexity due to the high-dimensional matrix inversion R~−1 at the CU.

Proposition 1::The MSE matrix EsDR⪰EcDR , where EsDR≜E[(s^sDR-MMSE−s)(s^sDR-MMSE−s)H] and EcDR≜E[(s^cDR-MMSE−s)(s^cDR-MMSE−s)H] . Moreover, we have E[∥s^sDR-MMSE−s∥22]≥E[∥s^cDR-MMSE−s∥22] .
The proof is given in Appendix B. Here, A⪰0 is a generalized inequality meaning A is a positive semidefinite matrix. Proposition 1 shows that the MSE of the cDR-MMSE equalizer is no larger than that of the sDR-MMSE equalizer.

Remark 3 (Application in the Daisy Chain Architecture): The sDR-MMSE equalizer still works in the daisy chain architecture since the summation operation will not increase bandwidth and computational complexity. However, the sequential nature of the daisy chain architecture leads to increased latency. In contrast, the cDR-MMSE equalizer only works with the star architecture since the concatenation operation increases the bandwidth sharply in the daisy chain architecture due to the accumulation of information dimensions.
Algorithm 2 The Proposed cDR-MMSE Equalization
Input:
yc,Hc,{nic}Ni=1,c=1,2,…,C , and Es .

1:
Decentralized preprocessing at each DU:

2:
for c=1 to C do

3:
Qc←HHcR−1cc ;

4:
Compute Qcyc , QcHc , and {Qcnic}Ni=1 ; // Send to CU

5:
end for

6:
Central processing at the CU:

7:
Compute y~ and H~ via (19);

8:
Compute R~ via (20);

9:
WcDR-MMSE is given by (22);

10:
s^cDR-MMSE is given by (23);

Output:
WcDR-MMSE and s^cDR-MMSE .

SECTION IV.BCD-Based LMMSE Equalization for the Daisy Chain Architecture
This section proposes an optimal BCD-based LMMSE equalizer for the daisy chain architecture and improves it by utilizing a decentralized low-rank decomposition method for further bandwidth reduction.

A. BCD-Based LMMSE Equalization
The DR-based LMMSE equalizers can be viewed as a decentralized implementation of the closed-form expression of the equalization matrix in (3). Although the sDR-MMSE can be adapted for the daisy chain architecture, the DR-based equalizers are only suboptimal solutions to the original LMMSE problem (2). Therefore, we aim to design an optimal decentralized equalizer for the daisy chain architecture by reconsidering problem (2). Incorporating the baseband model (1) and covariance estimation (6) into problem (2), and considering the independence of n and s, we can reformulate problem (2) equivalently as follows:
\begin{equation*} \min _{\mathbf {W} } \quad \frac {1}{N}\sum _{i=1}^{N}\mathbb {E}\left [{{\left \|{{ \mathbf {W}\mathbf {H}\mathbf {s}+\mathbf {W}\mathbf {n}^{i} -\mathbf {s} }}\right \|_{2}^{2}}}\right ]. \tag {24}\end{equation*}

The objective function of the above problem has only one random variable s, and the other variables are deterministic. It should be noted that ni is stored separately at each DU. Thus we deliberately partition the equalization matrix W into block matrix as W=[W1,W2,…,WC] with Wc∈CK×Mc . Then, problem (24) can be rewritten as

\begin{align*} & \min _{\mathbf {W}} \quad \frac {1}{N}\sum _{i=1}^{N}\mathbb {E}\Bigg [\Big \| \mathbf {W}_{c}\mathbf {H}_{c}\mathbf {s}+\sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {H}_{j}\mathbf {s} \\ & \qquad \qquad +\mathbf {W}_{c}\mathbf {n}_{c}^{i}+ \sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {n}_{j}^{i}-\mathbf {s} \Big \|_{2}^{2}\Bigg ]. \tag {25}\end{align*}

We then use the BCD method [25] to optimize {Wc}Cc=1 , which is suitable for the decentralized daisy chain architecture. Importantly, Wc∈CK×Mc can be seen as a dimensionality reduction matrix that decreases the dimension of the intermediate variables. Specifically, the objective function in problem (25) is minimized with respect to one block variable Wc while fixing Wj,j≠c for c=1,2,…,C sequentially. The update of Wc is given by the following proposition.

Proposition 2::While fixing Wj,j≠c in problem (25), the optimal solution with respect to Wc in closed form is given by as in (26), shown at the bottom of the page.
\begin{equation*} \mathbf {W}_{c}^{\ast }= \left ({{E_{s}\left ({{\mathbf {I}_{K}-\sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {H}_{j}}}\right )\mathbf {H}_{c}^{H}-\frac {1}{N}\sum _{i=1}^{N}\sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {n}^{i}_{j}(\mathbf {n}^{i}_{c})^{H}}}\right )\times \left ({{E_{s}\mathbf {H}_{c}\mathbf {H}_{c}^{H}+\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}_{c}(\mathbf {n}^{i}_{c})^{H}}}\right )^{-1}. \tag {26}\end{equation*}

Proof:See Appendix C.■
We observe that ∑j≠cWjHj and {∑j≠cWjnij}Ni=1 is needed for computing W∗c , and all the other terms in (26) can be computed via local information at DU c. Therefore, based on (26) and (27), we derive a BCD-based LMMSE equalizer for the daisy chain architecture. Adopting the Gauss-Seidel update rule [32], at the l-th iteration, the local equalization matrix Wlc is updated by solving the following subproblem:

\begin{align*} \mathbf {W}_{c}^{l}\!=\!\arg \min _{\mathbf {W}_{c}}~~f\left ({{ \mathbf {W}_{1}^{l},\ldots ,\mathbf {W}_{c-1}^{l},\mathbf {W}_{c},\mathbf {W}_{c+1}^{l-1},\ldots ,\mathbf {W}_{C}^{l-1}}}\right ), \tag {27}\end{align*}
where f(⋅) denotes the objective function of (25). Define Alc∈CK×K and {blc,i∈CK×1}Ni=1 as the interaction variables at c-th DU and l-th iteration, which are updated recursively by
\begin{align*} \mathbf {A}^{l}_{c}& =\mathbf {A}^{l}_{c-1}-\mathbf {W}^{l-1}_{c}\mathbf {H}_{c}+\mathbf {W}^{l}_{c}\mathbf {H}_{c}, \tag {28}\\ \mathbf {b}_{c,i}^{l}& =\mathbf {b}_{c,i}^{l-1}-\mathbf {W}^{l-1}_{c}\mathbf {n}_{c}^{i}+\mathbf {W}^{l}_{c}\mathbf {n}_{c}^{i},i=1,2,\ldots ,N. \tag {29}\end{align*}
These communication variables can be seen as the summation of the compressed local channel matrices and compressed local noise samples, where the local equalization matrices act as local compression matrices. The initialization of these communication variables will be detailed in Algorithm 3. Specifically, the c-th DU receives the communication variables Alc−1 and {blc−1,i}Ni=1 from the previous DU.6 Then the local equalization matrix Wlc is updated by as in (30), shown at the bottom of the next page.

\begin{equation*} \mathbf {W}_{c}^{l} \!=\! \left ({{\!E_{s}\!\left ({{\mathbf {I}_{K}\!-\!\mathbf {A}^{l}_{c-1}\!+\!\mathbf {W}^{l-1}_{c}\mathbf {H}_{c}}}\right )\mathbf {H}_{c}^{H}\! -\frac {1}{N}\sum _{i=1}^{N}\left ({{\left ({{\mathbf {b}_{c-1,i}^{l}\!-\!\mathbf {W}_{c}^{l-1}\mathbf {n}_{c}^{i}}}\right )\!\left ({{\mathbf {n}_{c}^{i}}}\right )^{H}}}\right )\!}}\right ) \!\times \!\left ({{\!E_{s}\mathbf {H}_{c}\mathbf {H}_{c}^{H}\!+\!\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}_{c}(\mathbf {n}^{i}_{c})^{H}\!}}\right )^{-1}. \tag {30}\end{equation*}

Except for the information received from the previous DU, all other terms in (30) can be computed locally. Finally, the c-th DU updates Alc and blc,i by (28) and (29), respectively, and then transfers them to the next DU.


Algorithm 3 The Proposed BCD-MMSE Equalization
Input:
yc,Hc,{nic}Ni=1,c=1,2,…,C , Es , and total iteration number T.

1:
Preprocessing:

2:
Initialize W0 using (7) in a decentralized manner;

3:
A00←0 ;

4:
b00,i←0,i=1,2,…,N ;

5:
for c=1 to C do

6:
A00←A00+W0cHc ;

7:
b00,i←b00,i+W0cnic,i=1,2,…,N ;

8:
end for

9:
BCD iterations:

10:
for l=1 to T do

11:
for c=1 to C do

12:
Update Wlc via (30);

13:
Update Alc via (28);

14:
Update blc,i,i=1,2,…,N via (29);

15:
end for

16:
end for

17:
Equalizer filter:

18:
s^BCD-MMSE←0 ;

19:
for c=1 to C do

20:
s^BCD-MMSE←s^BCD-MMSE+Wcyc ;

21:
end for

Output:
W=[W1,W2,…,WC] and s^BCD-MMSE .

The BCD-based LMMSE equalization is summarized in Algorithm 3, termed BCD-MMSE equalization. Theoretically, the algorithm can be terminated if the objective function values at the two successive iterations are almost unchanged. In the simulation part, only the first four iterations of the BCD algorithms are considered due to bandwidth and computation limitations in practice. Thus the number T of iterations can be chosen according to both the above two factors. Fig. 5(a) shows the communication transfer in the iteration phase of the proposed BCD-MMSE method, where the superscript l is omitted for brevity. Fig. 5(b) shows the equalizer filter phase for estimating the transmitted symbol. Note that Wlc∈CK×Mc can be viewed as a dimensionality reduction matrix that reduces the dimension of Hc , nic , and yc before transferring since K < Mc . For example, to share the covariance matrix information among DUs, the BCD-MMSE equalization only requires exchanging blc,i∈CK×1 among DUs, which significantly reduces the bandwidth compared to directly exchanging nic∈CMc×1 . Therefore, the data transfer size of the BCD-MMSE equalizer is independent of the number of BS antennas.

Fig. 5.
The communication and computation operations during the BCD-MMSE equalization process.

Theorem 2:(Convergence Results of the BCD-MMSE Algorithm) The proposed BCD-MMSE algorithm is guaranteed to converge to the global minimum of problem (2).
Proof:Since the objective function of (25) is a continuously differentiable and strongly convex function with respect to Wc . According to [25], The BCD-MMSE algorithm is guaranteed to converge to the global minimum of problem (2).■
Remark 4 (Extension to Other DBP Architectures):Although the BCD-MMSE equalizer was originally proposed for the unidirectional daisy chain architecture shown in Fig. 2(b), it can be applied to other DBP architectures by modifying the update rule in (27). For instance, the symmetric Gauss-Seidel update rule [33] is suitable for the bidirectional daisy chain architecture without a ring, where DUs are connected through bidirectional links, and there is no link between the last DU and the first DU. Furthermore, this update rule has a guaranteed convergence to global optima. Regarding the star DBP architecture depicted in Fig. 2(a), we could use the Jacobi update rule [34] for BCD iterations.
B. Low-Rank Decomposition Based BCD-MMSE
The proposed optimal BCD-MMSE equalizer effectively mitigates the bandwidth and computation limitations inherent in traditional centralized algorithm designs. However, the communication bandwidth required for each iteration still depends on the number of noise samples (N), which may be very large and even exceed the number of BS antennas (M) in certain scenarios. One straightforward way to address this issue is to reduce the number of noise samples used for covariance estimation. Unfortunately, this approach results in significant performance degradation since it leads to poor accuracy of covariance estimation. We below present an improved BCD-MMSE equalization method with lower bandwidth consumption for the case when N is large.

Let us recall the interference scenario, where the noise covariance matrix R=βH¯H¯H+σ2I with H¯∈CM×r . Note that the number of non-target UEs in communication systems is limited such that r≪min(M,N) . Moreover, the interference power is generally much greater than the background AWGN power, i.e., β≫σ2 . Consequently, the covariance matrix R can be deemed to be approximately low-rank, i.e., a rank-r matrix, implying that, we may obtain its rank-r approximation instead of estimating R.7 As seen below, this way brings the benefit of low-interaction decentralized algorithm design for BCD-MMSE with possibly minor performance degradation.

Given a positive semidefinite matrix R∈CM×M , its rank-r approximation seeks a low-rank substitute G∈CM×r of its square root such that GGH closely approximates R, i.e.,
\begin{equation*} \mathbf {G} =\arg \min _{\text {Rank}(\mathbf {G})\leq r} \|\mathbf {R}-\mathbf {G}\mathbf {G}^{H}\|_{F}^{2}, \tag {31}\end{equation*}
which can be efficiently solved. Firstly, define N≜1/N−−√ [n1,…,nN] and rewrite the estimation of R in (6) as
\begin{align*} \hat {\mathbf {R}}=\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}(\mathbf {n}^{i})^{H} = \mathbf {N}\mathbf {N}^{H}=\left ({{\begin{array}{c} \mathbf {N}_{1} \\ \vdots \\ \mathbf {N}_{C} \\ \end{array}}}\right ) \left ({{\mathbf {N}_{1}^{H}, \ldots ,\mathbf {N}_{C}^{H}}}\right ), \tag {32}\end{align*}
where Nc∈CMc×N is the local (scaled) noise samples stored at the c-th DU. Then, denote the SVD of N∈CM×N by
\begin{equation*} \mathbf {N} = \mathbf {U}\boldsymbol {\Sigma }\mathbf {V}^{H}, \tag {33}\end{equation*}
where Σ∈CM×M is a diagonal matrix with positive singular values sorted in descending order, U∈CM×M and V∈CN×M are matrices containing the left and right singular vectors of N as their columns, respectively. According to Eckart-Young-Mirsky Theorem [35], the optimal solution to the rank-r approximation problem (31) is given by
\begin{equation*} \mathbf {G}=\tilde {\mathbf {U}}\tilde {\boldsymbol {\Sigma }}=\mathbf {N}\tilde {\mathbf {V}}, \tag {34}\end{equation*}

where Σ~∈Cr×r is a diagonal matrix consisting of the r largest singular values of N, U~∈CM×r and V~∈CN×r being associated left and right singular vectors corresponding with singular values in Σ~ . In addition, we call U~Σ~V~ the rank-r decomposition of N.

We aim to replace N with G in the proposed BCD-MMSE algorithm, which can reduce the bandwidth burden at each iteration since r≪N . Specifically, we focus on finding G=NV~ in a decentralized manner, i.e., computing Gc=NcV~ at DU c with appropriate communication among DUs. The crucial step is to determine V~ since Nc is known at DU c.

Algorithm 4 The Proposed LRD Algorithm
Input:
N=[NT1,NT2,…,NTC]T .

1:
for c=1 to C−1 do

2:
if c=1 then

3:
N~0←∅ ;

4:
else

5:
N~c−1←Dc−1VHc−1 ;

6:
end if

7:
Compute rank-r decomposition of [N~Tc−1,NTc]T as =UcΣcVHc ;

8:
Dc←UcΣc ;

9:
Transfer Dc and Vc to the next DU;

10:
end for

11:
At the C-th DU:

12:
Compute rank-r decomposition of [N~TC−1,NTC]T as UCΣCVHC ;

13:
Broadcast and local computation:

14:
Broadcast VC to each DU, and compute Gc←NcVC at each DU;

Output:
G=[GT1,GT2,…,GTC]T .

Traditionally, computing the SVD of matrix N needs to collect all noise samples. Specifically, the c-th DU needs to transmit [NT1,…,NTc]T∈CcMc×N to the next DU. However, this results in a significant bandwidth burden due to the large data transfer size of M×N at the last DU. To address this issue, at the c-th DU, we transmit the rank-r decomposition (i.e., UcΣcVHc ) of an approximation of [NT1,…,NTc]T , which significantly reduces the bandwidth requirements with only minor performance degradation due to the approximately low-rank property of R. We summarize the proposed algorithm in Algorithm 4 and term it low-rank decomposition (LRD) algorithm. Note that the c-th DU transmits Dc≜UcΣc∈CcMc×r and Vc∈CN×r to the next DU, with a size proportional to (M+N)×r , which is far less than M×N . In practice, the value of r is unknown but can be determined by the number of large singular values of N.

Based on the above discussions, we can represent the N noise samples with the r column vectors of G with little loss. Specifically, we first perform the LRD algorithm and then carry out the BCD-MMSE equalization by replacing N with G. We refer to it as BCD-MMSE (LRD) equalization, which has a small bandwidth cost at each iteration.

SECTION V.Complexity and Bandwidth Analysis
A. Computational Complexity Analysis
Throughout the section, we consider the common scenario where min{M,N}>Mc>K . The computational complexity of the centralized LMMSE equalizer in (3) is O(M3+NM2) . Since M can be extremely large, the cubic complexity is impractical for massive MIMO systems.

The computational complexity of the proposed sDR-MMSE and cDR-MMSE equalizers are O(MM2c+NMMc) and O(MM2c+NMMc+K3C3) , respectively. They have the same preprocessing with a complexity of O(M3c+NM2c) at each DU. The complexity of cDR-MMSE equalization is much higher than that of sDR-MMSE equalization because the concatenating and superimposing operation at the CU leads to a CK×CK and K×K matrix inversion, respectively.

The complexity of initializing the proposed BCD-MMSE and BCD-MMSE (LRD) equalization, known as the BDAC-MMSE algorithm, is dominated by O(MM2c+NMMc) . The proposed LRD algorithm only needs to be executed once and has a complexity of O(min(M2N,N2M)) . The per-iteration complexity of the BCD-MMSE equalization is O(NMK+MMcK) . Benefiting from the LRD algorithm, the per-iteration complexity of the BCD-MMSE (LRD) equalization is O(rMK+MMcK) , which is independent of N, where r≪N . Therefore, increasing the number of iterations of the BCD-MMSE (LRD) algorithm requires only a small amount of computation.

The complexity of our proposed methods, except for the BCD-MMSE (LRD) method, scales linearly with M instead of O(M3) . The BCD-MMSE (LRD) method has low per-iteration complexity that is independent of both M and N. Therefore, all the proposed algorithms significantly alleviate the computational bottleneck in massive MIMO systems.

B. Communication Bandwidth Analysis
The communication bandwidth is evaluated by the total number of real-valued entries transferred among the DUs. We assume that the channel and noise covariance remain static across Ncoh contiguous symbols. This means that the equalization matrix and covariance estimation can be reused for different symbols, although they will change with every coherence block. Thus the data required for computing the equalization matrix is transferred only once for Ncoh symbols, while the received signal y must be transferred for each symbol.

The average data transfer size of the centralized LMMSE method is 2M(Ncoh+K+N)/Ncoh . The proposed sDR-MMSE and cDR-MMSE methods have the same average data transfer size of 2CK(Ncoh+K+N)/Ncoh . The average data transfer size of the proposed BCD-MMSE method is C(4K2+2NK)/Ncoh+2TCK(N+K)/Ncoh+2CK , where the three terms are induced by preprocessing, T iterations for computing equalization matrix, and symbol estimation, respectively. Notably, the average data transfer size of the aforementioned methods is independent of M. Additionally, the proposed BCD-MMSE (LRD) method only needs to transfer ((C−1)Mr+4CNr)/Ncoh+C(4K2+2Kr)/Ncoh+2TCK(r+K)/Ncoh+2CK entries. The first term is caused by the LRD algorithm, the second term is due to the preprocessing, the third term is induced by the iteration of the BCD-MMSE (LRD) method, and the last term is due to symbol estimation. Interestingly, the data transfer size at each iteration of the BCD-MMSE (LRD) method is independent of both M and N. Therefore, all the proposed methods can achieve a decentralized baseband processing design with a relatively small communication bandwidth among DUs.

SECTION VI.Simulation Results
A. Simulation Setup
We investigate a single-cell massive MIMO system comprising of a BS equipped with M=128 or 256 antennas, divided into C=8 or 16 clusters, where each cluster has Mc=M/C antennas. The number of target and non-target UEs is both set to K=8 , and there are N=192 noise samples. The channel matrix is generated from the QuaDRiGa platform, which considers both large and small-scale fading. UEs are uniformly distributed within a 120° sector of radius 50∼100 m centered at BS. The signal-to-noise ratio (SNR) is defined as SNR=10log10(Es/σ2) , where σ2 is the power of background AWGN. The colored noise is modeled as interference from r non-target UEs plus background AWGN, where the non-target UEs are molded similarly to the target UEs. Specifically, the distribution of the colored noise follows a complex Gaussian distribution, denoted as CN(0,βH¯H¯H+σ2I) , where H¯∈CM×r denotes the channel matrix of r non-target UEs, and β signifies the power of non-target UEs. The interference over thermal (IoT) is used to measure the intensity of interference relative to background noise, i.e., IoT=10log10((β+N0)/σ2) . Large IoT leads to significant interference, i.e., the off-diagonal elements of the noise covariance matrix are more prominent. IoT=10 dB is a default setting in the simulation since it is a typical scenario in practical systems. Under our settings, the noise covariance is approximately low-rank. The simulation results are averaged over 100 randomly generated channel realizations, and 480 symbols are drawn independently from the 16-QAM constellation for each channel.

B. SER Performance of the Proposed BCD-Based Equalizers With Different Number of Iterations
This subsection evaluates the symbol error rate (SER) performance of the proposed BCD-based equalizers. Due to bandwidth and computation limitations, only the first four iterations of the BCD algorithms are considered. Four baselines are evaluated: the centralized ZF method, the centralized LMMSE method, the MMSE(AWGN), which denotes the LMMSE equalizer considering only AWGN, and the proposed intuitive BDAC-MMSE method that serves as the initial point for the BCD-based algorithms.

Fig. 6 presents the SER performance of the first four iterations of the proposed BCD-MMSE equalizer. It can be observed that only 2 to 3 iterations are sufficient to approach the performance of the centralized LMMSE method for all cases.8 Even a single BCD iteration enables excellent SER performance. In addition, Fig. 6(a) and (b) illustrate that when the BS employs more antennas, the performance gap between the BCD-MMSE equalizer and LMMSE equalizer decreases, and all the equalizers attain better performance. Thus, the BCD-MMSE equalizer is suitable for extremely large antenna arrays. As the number of clusters increases, the BDAC-MMSE equalizer utilizes a smaller portion of the covariance matrix for decentralized processing, which incurs larger performance loss. Hence the performance of the BCD-MMSE equalizer decreases slightly, as shown in Fig. 6(a) and (c). Moreover, it can be seen that the performance of MMSE(AWGN) and ZF equalizers is close, and both are far worse than other algorithms. Therefore, the proposed methods are no longer compared to MMSE(AWGN) in subsequent simulations.

Fig. 6.
SER performance versus SNR for the first four iterations of the proposed BCD-MMSE equalizer.

Fig. 7 illustrates the SER performance of the first four iterations of the BCD-MMSE (LRD) equalizer. The value of r is selected as the number of non-target UEs, i.e., K=8 . The performance of the BCD-MMSE (LRD) algorithm is almost the same as the BCD-MMSE algorithm in Fig. 6. According to the complexity and bandwidth analysis in Section V, the LRD algorithm significantly reduces the dimension of communication variables. Thus, the complexity and bandwidth at each iteration are considerably reduced.

Fig. 7.
SER performance versus SNR for the first four iterations of the proposed BCD-MMSE (LRD) equalizer.

C. SER Performance of All the Proposed Equalizers
Fig. 8 shows the SER performance of all the proposed methods, including sDR-MMSE, cDR-MMSE, BCD-MMSE, and BCD-MMSE (LRD) equalizers. Considering the bandwidth limitation in practical systems, we run the BCD-MMSE and the BCD-MMSE (LRD) equalizers for one and four iterations, respectively, resulting in similar levels of communication bandwidth. Furthermore, we set r=K for the LRD algorithm.

Fig. 8.
SER versus SNR of the baselines and all the proposed equalizers.

As shown in Fig. 8, the proposed equalizers’ performance ranking is BCD-MMSE (LRD), BCD-MMSE, cDR-MMSE, and sDR-MMSE. Generally speaking, BCD-MMSE and cDR-MMSE methods have comparable performance. Specifically, Fig. 8(a) and (b) show that all methods achieve better performance with increasing the number of BS antennas. Fig. 8(b) and (c) imply that more clusters lead to a lower SER performance, as only a small portion of the covariance matrix becomes locally available. Additionally, Fig. 8(a) and (e) demonstrate that, with an increase in the number of UEs from 8 to 12, the cDR-MMSE equalizer’s performance greatly improves due to the rising local compression dimension from 8 to 12. Finally, Fig. 8(f) shows SER performance under IoT=20 dB, where the performance of all equalizers is significantly degraded due to stronger interference in colored noise. Moreover, Fig. 8(g) compares the proposed equalizers’ performance using QPSK modulation, which results in fewer error symbols than 16-QAM modulation.

To summarize, for the daisy chain architecture, the BCD-MMSE equalizer is an efficient algorithm with fast convergence and near-optimal SER performance. The LRD enhancement further improves the BCD-MMSE equalizer’s performance with the same level of bandwidth. For the star architecture, the cDR-MMSE equalizer has better performance but higher complexity than the sDR-MMSE equalizer.


D. Fronthaul Data-Rate Comparison
To evaluate the required data rate of the proposed decentralized equalization algorithms, we consider a frame structure in orthogonal frequency-division multiplexing (OFDM) systems. Specifically, we leverage channel correlation based on the physical resource block (PRB) concept outlined in the third-generation partnership project (3GPP) technical standards. A PRB is defined as a frequency-time stripe over which the wireless channel remains constant across all subcarriers. Within an OFDM symbol, the number of subcarriers in each PRB and the number of PRBs per symbol are specified as Nsc,PRB and NPRB , respectively. Each symbol contains Nu≜Nsc,PRB×NPRB subcarriers (a resource element in OFDM system) to carry user data within a duration of TOFDM . Each PRB corresponds to a different channel matrix in the baseband model in (1).

Formulation phase: Define A as the set of all matrices transmitted during the equalization matrix formulation phase for a decentralized scheme. For example, A includes {QcHc,{Qcnic}Ni=1}Cc=1 for DR-MMSE.7 The average fronthaul data rate during the formulation phase can be calculated using the following equation:
\begin{equation*} R_{\text {form }}=\frac{w S_{\mathrm{A}} N_{\mathrm{PRB}}}{T_{\mathrm{OFDM}}}\end{equation*}

where w is the bit-width of each element in A (including both real and imaginary parts), SA is the total number of real elements in A, and the numerator represents the total number of bits required to transfer A within one OFDM symbol.

Filtering phase: The local processing results (e.g., {Qcyc}Cc=1 for DR-MMSE.) are collected to obtain the final estimate. The average fronthaul data rate during the filtering phase can be calculated as
\begin{equation*} R_{\mathrm{fil}}=\frac{w S_{\mathrm{s}} N_{\mathrm{u}}}{T_{\mathrm{OFDM}}} \end{equation*}
where Ss denotes number of real elements in local processing results. The total data rate is given by

\begin{equation*}R_{\text {total }}=R_{\text {form }}+R_{\text {fil }} . \end{equation*}

For the numerical results, we set N=192 , r=8 , and w=12 . The remaining system parameters are configured as follows according to the worst case in 5G NR: Nu=3300 , NPRB=275 , Nsc,PRB=12 and TOFDM=1120 KHz . Table I presents a comparison of the total fronthaul data rate between the centralized and our proposed decentralized algorithms under the DBP architectures for different settings of M, K, and C. The iteration number of the BCD-MMSE and BCD-MMSE (LRD) algorithms are both set to 2. We observe that for most of the test cases, the DR-MMSE and BCD-MMSE, and BCD-MMSE (LRD) equalization schemes require 23%, 44%, and 37% of the data rate needed by centralized MMSE (C-MMSE) algorithm. This portion can be further decreased as the ratio M/K grows. Additionally, we find that the fronthaul data rates of the DR-MMSE and BCD-MMSE algorithms are independent of M, making them particularly beneficial for massive MIMO settings. In contrast to the BCD-MMSE algorithm, the fronthaul data-rate in BCD-MMSE (LRD) increases slowly with the number of iterations.

TABLE I Total Fronthaul Data Rate Comparison For Different SystemParameters [Tbps]

SECTION VII.Conclusion
This paper has investigated the decentralized LMMSE equalizer design under the DBP architectures. The existing decentralized equalization algorithms only considered ideal AWGN assumption, whereas colored noise exists in practice. Therefore, we have proposed DR-based and BCD-based equalizers for the star and daisy chain architectures, respectively. The data transfer size of these equalizers is independent of the number of BS antennas, significantly mitigating the bandwidth and computation bottlenecks encountered in centralized counterparts. In addition, the communication bandwidth of the BCD-MMSE equalizer can be reduced further by applying the LRD algorithm. Extensive simulation results have shown the excellent performance of the proposed algorithms. Future work includes extending our decentralized equalization methods to other decentralized architectures such as cell-free massive MIMO systems. Additionally, deep learning techniques [36] may help mitigate bandwidth and computation limitations in our design.


Appendix BProof of Proposition 1
Proof:From the definition of EsDR , we have
\begin{align*} \mathbf {E}_{\text {sDR}}& =E_{s}\mathbf {I}-E_{s}\mathbf {H}^{H}\check {\mathbf {Q}}^{H} \\ & \quad \times \left ({{\check {\mathbf {Q}}\mathbf {H}\mathbf {H}^{H}\check {\mathbf {Q}}^{H}+\frac {1}{E_{s}}\check {\mathbf {Q}}\mathbf {R}\check {\mathbf {Q}}^{H}}}\right )^{-1}\check {\mathbf {Q}}\mathbf {H}. \tag {39}\end{align*}

By leveraging the Woodbury identity [37], one has
\begin{equation*} \mathbf {E}_{\text {sDR}}^{-1}=\frac {1}{E_{s}}\mathbf {I}+\mathbf {H}^{H}\check {\mathbf {Q}}^{H}\left ({{\check {\mathbf {Q}}\mathbf {R}\check {\mathbf {Q}}^{H}}}\right )^{-1}\check {\mathbf {Q}}\mathbf {H}. \tag {40}\end{equation*}

Similarly, we can obtain E−1cDR by substituting the Qˇ in (40) with Q~ . To prove EcDR⪯EsDR , it is equivalent to show E−1cDR⪰E−1sDR . Further, it is sufficient to show
\begin{equation*} \tilde {\mathbf {Q}}^{H}\left ({{\tilde {\mathbf {Q}}\mathbf {R}\tilde {\mathbf {Q}}^{H}}}\right )^{-1}\tilde {\mathbf {Q}} \succeq \check {\mathbf {Q}}^{H}\left ({{\check {\mathbf {Q}}\mathbf {R}\check {\mathbf {Q}}^{H}}}\right )^{-1}\check {\mathbf {Q}}, \tag {41}\end{equation*}

which is equivalent to
\begin{equation*} \mathbf {R}^{\frac {1}{2}}\tilde {\mathbf {Q}}^{H}\!\!\left ({{\tilde {\mathbf {Q}}\mathbf {R}\tilde {\mathbf {Q}}^{H}\!}}\right )^{-1}\!\!\tilde {\mathbf {Q}}\mathbf {R}^{\frac {1}{2}} {\succeq } \mathbf {R}^{\frac {1}{2}}\check {\mathbf {Q}}^{H}\!\left ({{\check {\mathbf {Q}}\mathbf {R}\check {\mathbf {Q}}^{H}}}\right )^{-1}\!\check {\mathbf {Q}}\mathbf {R}^{\frac {1}{2}}. \tag {42}\end{equation*}

We observe that R12Q~H(Q~RQ~H)−1Q~R12 is an orthogonal projection matrix with range space R(R12Q~H) , and R(R12Q~H)⊇R(R12QˇH) holds obviously (Notice that the opposite is not necessarily true). Therefore, (42) must hold. Thus we have EsDR⪰EcDR , which immediately implies Tr(EsDR)≥Tr(EcDR) . Further combining with Tr(EsDR)=E[∥s^sDR-MMSE−s∥22] . The proof is concluded.■

Appendix CProof of Proposition 2
Proof:Since the objective function of problem (25) is convex in Wc , we could obtain the optimal solution by setting the gradient equal to 0. Note that the expectation in problem (25) is taken with respect to s, it can be rewritten as

\begin{align*} & \hspace {-.2pc}\frac {1}{N}\sum _{i=1}^{N}\mathbb {E}\Bigg [\Bigg \| \mathbf {W}_{c}\mathbf {H}_{c}\mathbf {s}+\sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {H}_{j}\mathbf {s}+\mathbf {W}_{c}\mathbf {n}_{c}^{i} \\ & \qquad \qquad \qquad \qquad \quad + \sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {n}_{j}^{i}-\mathbf {s} \Bigg \|_{2}^{2}\Bigg ] \\ & =\Re e\Bigg (\rm {Tr}\Bigg (E_{s}\mathbf {W}_{c}\mathbf {H}_{c}\mathbf {H}_{c}^{H}\mathbf {W}_{c}^{H} \!+ \!2E_{s}\sum _{j=1,j \neq c}^{C}\!\!\mathbf {W}_{c}\mathbf {H}_{c}\mathbf {H}_{j}^{H}\mathbf {W}_{j}^{H} \\ & \quad -2E_{s}\mathbf {W}_{c}\mathbf {H}_{c}+\mathbf {W}_{c}\left ({{\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}_{c}(\mathbf {n}^{i}_{c})^{H}}}\right )\mathbf {W}_{c}^{H} \\ & \quad +2\sum _{j=1,j \neq c}^{C}\mathbf {W}_{c}\left ({{\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}_{j}(\mathbf {n}^{i}_{c})^{H}}}\right )\mathbf {W}_{j}^{H}\Bigg )\Bigg )+\text {const}, \tag {43}\end{align*}

where Re(a) is the real part of a complex scalar a, “const” denotes the terms independent of Wc , and the equality is due to the independence of s and n. Denote f(⋅) as the function in (43) and calculate its gradient w.r.t. Wc , yielding

\begin{align*} \nabla _{\mathbf {W}_{c}}f(\mathbf {W}_{c})& =2E_{s}\mathbf {W}_{c}\mathbf {H}_{c}\mathbf {H}_{c}^{H}+2E_{s}\sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\mathbf {H}_{j}\mathbf {H}_{c}^{H} \\ & \quad -2E_{s}\mathbf {H}_{c}^{H} +2\mathbf {W}_{c}\left ({{\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}_{c}(\mathbf {n}^{i}_{c})^{H}}}\right ) \\ & \quad +2\sum _{j=1,j \neq c}^{C}\mathbf {W}_{j}\left ({{\frac {1}{N}\sum _{i=1}^{N}\mathbf {n}^{i}_{j}(\mathbf {n}^{i}_{c})^{H}}}\right ). \tag {44}\end{align*}
Letting ∇Wcf(W∗c)=0 , we obtain the optimal solution W∗c in closed form as in (26).■
