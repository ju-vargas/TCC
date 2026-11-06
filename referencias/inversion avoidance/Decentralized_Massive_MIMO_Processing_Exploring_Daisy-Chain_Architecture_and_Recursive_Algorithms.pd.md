# Decentralized Massive MIMO Processing Exploring Daisy-Chain Architecture and Recursive Algorithms 

Jesús Rodríguez Sánchez ${ }^{(D)}$, Student Member, IEEE, Fredrik Rusek ${ }^{(D)}$, Member, IEEE, Ove Edfors ${ }^{(1)}$, Senior Member, IEEE, Muris Sarajlić ${ }^{(1)}$, and Liang Liu ${ }^{(1)}$, Member, IEEE


#### Abstract

Algorithms for Massive MIMO uplink detection and downlink precoding typically rely on a centralized approach, by which baseband data from all antenna modules are routed to a central node in order to be processed. In the case of Massive MIMO, where hundreds or thousands of antennas are expected in the basestation, said routing becomes a bottleneck since interconnection throughput is limited. This paper presents a fully decentralized architecture and an algorithm for Massive MIMO uplink detection and downlink precoding based on the Coordinate Descent (CD) method, which does not require a central node for these tasks. Through a recursive approach and very low complexity operations, the proposed algorithm provides a good trade-off between performance, interconnection throughput and latency. Further, our proposed solution achieves significantly lower interconnection data-rate than other architectures, enabling future scalability.


Index Terms-Massive MIMO, decentralized architecture, precoding, detection, zero-forcing, coordinate descent, kaczmarz, inter-connection data-rate, SINR.

## I. Introduction

MASSIVE MIMO is one of the most relevant technologies in wireless communications [3], [4]. Among the key features of this technology are high spectral efficiency and improved link reliability, making it a key enabler for 5 G . Massive MIMO exploits spatial diversity far beyond traditional MIMO systems by employing a large scale antenna array in the base-station (BS) with hundreds or possibly even thousands of elements. This large number of elements allows for unprecedented spatial resolution and high spectral efficiency, while providing simultaneous service to several users within the same time-frequency resource.

Despite all the advantages of Massive MIMO, there are still challenges from an implementation point of view. One of the most critical ones is sending data from the BS antennas to the central processing unit (CPU) and vice-versa, and the high interconnection throughput it requires. In current set-ups, uplink detection algorithms based on zero-forcing (ZF) equalizer

[^0]typically rely on a centralized architecture, shown in Fig. 1(a), where baseband samples are collected in the CPU for obtaining channel state information (CSI) and further matrix inversion, which allows data estimation and further detection. The same argument is valid for downlink precoding. In order to avoid dedicated links between antenna modules and CPU, a shared bus is typically used to exchange this data. In case of LuMaMi testbed [5], [6], the shared bus was reported to support an aggregated data-rate of 384 Gps , which exceed base-station internal interface standards such as eCPRI [7]. Additionally, the pin-count of integrated circuits (IC) limits the number of links the IC can handle simultaneously and thus the throughput. Due to this high data-rate, the power appears as another potential limitation. This combination of factors are considered as the main bottleneck in the system and a clear limitation for array scalability. In this paper we will address the inter-connection throughput limitation by decreasing its value per link and consequently reducing the impact of the other two (pin-count and power).

The inter-connection bottleneck has been noted in several previous studies on different architectures for Massive MIMO BSs [5], [8]-[13]. As a solution, most of these studies recommend moving to a decentralized approach where uplink estimation and downlink precoding can be performed locally in processing nodes close to the antennas (final detection can still be done in a CPU). However, to achieve that, CSI still needs to be collected in the CPU, where matrix inversion is performed [5], [8], [9], imposing an overhead in data shuffling.

The CSI problem is addressed in [11], where CSI is obtained and used only locally (not shared) for precoding and estimation, with performance close to MMSE. However, this architecture relies on the CPU for exchanging a certain amount of consensus information between the nodes, and this exchange negatively impacts the processing latency and throughput [12], and therefore limits the scalability of this solution. In order to solve these problems, feedforward architectures for detection [13] and precoding [12] have been proposed recently, where the authors present a partially decentralized (PD) architecture for detection and precoding, which achieves the same results as linear methods (MRC, ZF, L-MMSE), and therefore becomes optimal when $M$ is large enough. Partial Gramian matrices from antennas are added up before arriving to a processing unit where the Gramian is inverted.

In [8], a flat-tree structure with daisy-chained nodes was presented. The authors propose conjugate beamforming as a fully decentralized method with the corresponding penalty in system

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-02.jpg?height=635&width=1205&top_left_y=214&top_left_x=433)
Fig. 1. Comparison between base station receiver chain in centralized and fully decentralized architectures for Massive MIMO uplink. Antenna array with $M$ elements is divided into Remote Processing Units (RPUs), each containing a set of antennas. (a): Centralized architecture. Each RPU has one link to transfer baseband samples to the CPU, where the rest of processing tasks are done. (b): Fully decentralized architecture for detection. Each RPU performs RF, ADC, OFDM, channel estimation (CHEST) and data estimation (EST) locally. Detection (DET) and decoding (DEC) is centralized. RPUs are connected to each other by uni-directional links. Only one RPU has a direct connection with the CPU. Proposed algorithms are executed in EST blocks in parallel mode. The points where the interconnection data-rate is estimated are marked by circles and the value is denoted by $\mathrm{R}_{c}$ and $\mathrm{R}_{d}$ for centralized and decentralized respectively. The goal is to have $\mathrm{R}_{d} \ll \mathrm{R}_{c}$ without compromising performance and latency.

capacity. In the same work it is also pointed out that by following this topology the latency was being severely compromised. The more detailed analysis on latency is thus needed to evaluate the algorithm.

In this article we propose a fully decentralized architecture and a recursive algorithm for Massive MIMO detection and precoding, which is able to achieve very low inter-connection data-rate without compromising latency. The proposed algorithm is pipelined so that it runs in a distributed way at the antenna processing units, providing local vectors for estimation/detection that approximate to the zero-forcing solution. We make use of the Coordinate Descent (CD) algorithm, which is detailed in Section IV, to compute these vectors.

There is previous work based on CD, such as [14]. The main difference is that the coordinate update in [14] is done per user basis, i.e., a different user index is updated every iteration, while in our proposed method the coordinate update is done per antenna basis, updating all users at once.

We extend the work presented in [1] and [2], which are also based on decentralized daisy-chain architecture. The novelties of the present work compared to these two is as follows:

- A common strategy for downlink precoding and uplink equalization is presented, in contrast to [1] and [2], which only covers uplink and downlink separately.
- The algorithm has been modified that serial processing is only needed when new CSIs are estimated. The corresponding filtering phase can be conducted in parallel to reduce latency, in contrast to [1], where serial processing is always needed, which increases the latency.
- A recommended step-size is provided, in contrast to [1].
- An analytical expression for resulting SINR and a complete performance analysis is presented in this paper.
- Complexity analysis from a general point of view (not attached to any specific implementation) is provided, which includes: inter-connection data-rate, memory size and latency. In [1], only inter-connection data-rates are analyzed.

Decentralized architectures, as shown in Fig. 1(b), have several advantages compared to the centralized counterpart, as shown in Fig. 1(a). For example, they overcome bottlenecks by finding a more equal distribution of the system requirements among the processing nodes of the system. Apart from this, data localization is a key characteristic of decentralized architectures. In uplink, the architecture allows data to be consumed as close as possible to where it is generated, minimizing the amount to transfer, and therefore saving throughput and energy. To achieve data localization, processing nodes need to be located near the antenna, where they perform processing tasks locally such as channel and data estimation. Local CSI is estimated and stored locally in each, without any need to share it with any other nodes in the system. This approach has been suggested previously in [8]-[13], and we take advantage of it in the proposed solution.

The remainder of the paper is organized as follows. In Section II the preliminaries are presented, comprising the system model for uplink and downlink, together with an introduction to linear processing and the ZF method. Section III is dedicated to a comparison between the centralized and decentralized architectures and reasoning why the latter one is needed, together with an overview of the daisy-chain topology. The proposed algorithm, based on CD, is presented in Section IV. In V closed-form expressions of the SIR and SINR are provided for this algorithm, together with interconnection data-rates, latency and memory requirements of the proposed solution. Finally, Section VI summarizes the conclusions of this publication.

Notation: In this paper, lowercase, bold lowercase and upper bold face letters stand for scalar, column vector and matrix, respectively. The operations $(.)^{T},(.)^{*}$ and $(.)^{H}$ denote transpose, conjugate and conjugate transpose respectively. The $i$-th element of vector $\mathbf{h}$ is denoted as $h_{i}$. A vector $\mathbf{w}$ and a matrix $\mathbf{A}$ related to the $m$ th antenna is denoted by $\mathbf{w}_{m}$ and $\mathbf{A}_{m}$, respectively. $A_{i, j}$ denotes element $(i, j)$ of $\mathbf{A} . \mathbf{A}_{m}(i, j)$ denotes element $(i, j)$ of the $m$-th matrix in the sequence $\left\{\mathbf{A}_{m}\right\}$. The $k$ th coordinate
vector in $\mathbb{R}^{K}$ is defined as $\mathbf{e}_{k}$. Kronecker delta is represented as $\delta_{i j}$. Probability density function and cumulative density function are denoted respectively as $f_{\mathbf{X}}(x)$ and $F_{\mathbf{X}}(x)$. Computational complexity is measured in terms of the number of complexvalued multiplications.

## II. Background

## A. System Model

For uplink, we consider a scenario with $K$ single-antenna users transmitting to a BS with an antenna array with $M$ elements. Assuming time-frequency-based channel access, a Resource Element (RE) represents a unit in the time-frequency grid (also named subcarrier in OFDM) where the channel is expected to be approximately flat. Under this scenario, the input-output relation is

$$
\begin{equation*}
\mathbf{y}^{\mathrm{u}}=\mathbf{H} \mathbf{x}^{\mathrm{u}}+\mathbf{n}^{\mathrm{u}}, \tag{1}
\end{equation*}
$$

where $\mathbf{y}^{\mathrm{u}}$ is the $M \times 1$ received vector, $\mathbf{x}^{\mathrm{u}}$ is the transmitted user data vector $(K \times 1), \mathbf{H}=\left[\mathbf{h}_{1} \mathbf{h}_{2} \cdots \mathbf{h}_{M}\right]^{T}$ is the channel matrix ( $M \times K$ ) and $\mathbf{n}^{\mathrm{u}}$ an $M \times 1$ vector of white, zero-mean complex Gaussian noise. The entries of $\mathbf{H}$ are i.i.d. zero-mean circularly-symmetric complex-gaussian entries, with rows $\mathbf{h}_{i} \sim \mathcal{C} \mathcal{N}(0, \mathbf{I})$ for all $i$. The noise covariance at the receiver is $N_{0} \mathbf{I}$. The average transmitted power is assumed to be equal across all users and we assume, without any loss of generality, a unit transmit power. SNR is defined as $\frac{1}{N_{0}}$ and represents the average "transmit" signal-to-noise ratio.

For downlink, if Time Division Duplex (TDD) is assumed, then according to channel reciprocity principle and by employing reciprocity calibration techniques [15], it is assumed that within the same coherence time, the channel matrix is the same as in the uplink case, and the system model follows

$$
\begin{equation*}
\tilde{\mathbf{x}}^{\mathrm{d}}=\mathbf{H}^{T} \mathbf{y}^{\mathrm{d}}+\mathbf{n}^{\mathrm{d}}, \tag{2}
\end{equation*}
$$

for a RE, where $\mathbf{y}^{\mathrm{d}}$ is the $M \times 1$ transmitted vector, $\tilde{\mathbf{x}}^{\mathrm{d}}$ is the received data vector by users ( $K \times 1$ ), and $\mathbf{n}^{\mathrm{d}}$ samples of noise $(K \times 1)$.

Once the system model is established, we introduce the linear processing fundamentals used for downlink precoding and uplink estimation.

## B. Linear Processing

In this article we focus on linear estimators and precoders, because they show close to optimal performance in Massive MIMO regime while requiring low complexity.

A linear estimator provides $\hat{\mathbf{x}}^{\mathrm{u}}$, which is an estimate of $\mathbf{x}^{u}$, by applying an equalizer filter matrix $\mathbf{W}$ to the vector of observations, $\mathbf{y}^{\mathbf{u}}$ :

$$
\begin{align*}
\hat{\mathbf{x}}^{\mathrm{u}} & =\mathbf{W}^{H} \mathbf{y}^{\mathrm{u}} \\
& =\sum_{m=1}^{M} \mathbf{w}_{m}^{*} y_{m}^{\mathrm{u}}, \tag{3}
\end{align*}
$$

where $\mathbf{W}=\left[\begin{array}{llll}\mathbf{w}_{1} & \mathbf{w}_{2} & \cdots & \mathbf{w}_{M}\end{array}\right]^{T}$ is an $M \times K$ matrix, $\mathbf{w}_{m}$ is a $K \times 1$ filter vector related to antenna $m$ and $y_{m}^{\mathrm{u}}$ the observation at antenna $m$. As it can be seen the estimate $\hat{\mathbf{x}}^{\mathrm{u}}$ is computed by the sum of $M$ partial products. If $\mathbf{w}_{m}$ is obtained and stored
locally in the $\mathrm{m} t h$ antenna module, then the partial products can be computed with local data only, reducing the amount of data to exchange between nodes. From implementation point of view, the linear estimator relies on the accumulation of all partial results according to (3), which can be done centrally (fusion node) or distributed.

For downlink, the data vector intended to the users, $\mathbf{x}^{\mathrm{d}}$, is precoded with matrix $\mathbf{P}$ as

$$
\begin{equation*}
\mathbf{y}^{\mathrm{d}}=\mathbf{P} \mathbf{x}^{\mathrm{d}} \tag{4}
\end{equation*}
$$

where $\mathbf{P}=\left[\begin{array}{llll}\mathbf{p}_{1} & \mathbf{p}_{2} & \cdots & \mathbf{p}_{M}\end{array}\right]^{T}$ is an $M \times K$ matrix, which fulfills a power constraint $\|\mathbf{P}\|_{F}^{2} \leq P$, such that $P$ is the maximum transmitted power. Particularly for antenna $m$ we have

$$
\begin{equation*}
y_{m}^{\mathrm{d}}=\mathbf{p}_{m}^{T} \mathbf{x}^{\mathrm{d}} . \tag{5}
\end{equation*}
$$

Similarly to uplink, if $\mathbf{p}_{m}$ is obtained and stored locally at the $\mathrm{m} t h$ antenna module, then $y_{m}^{\mathrm{d}}$ can be computed only with local data after $\mathbf{x}^{d}$ is broadcasted to all antennas.

The zero-forcing (ZF) equalizer, which is one type of linear estimator, constitutes a reference in our analysis. It is defined for uplink estimation as

$$
\begin{equation*}
\mathbf{W}_{\mathrm{ZF}}^{H}=\left(\mathbf{H}^{H} \mathbf{H}\right)^{-1} \mathbf{H}^{H}, \tag{6}
\end{equation*}
$$

and $\mathbf{P}_{\mathrm{ZF}}=\mathbf{W}_{\mathrm{ZF}}^{*}$ for the downlink precoding.
ZF is able to completely cancel inter-user interference (IUI) and reach the promised spectral efficiency of Massive MIMO. However, as ZF is performed in a central processor, the Gramian matrix $\mathbf{H}^{H} \mathbf{H}$ needs to be collected and inverted, which increases the average inter-connection data-rate. The computational load is also increased due to the matrix inversion and posterior matrix multiplication during estimation phase. Taking this into consideration, we look for methods with IUI-cancellation capabilities but with lower requirements for the system.

## C. Uplink \& Downlink Reciprocity

Substituting (1) into (3) leads to

$$
\begin{equation*}
\hat{\mathbf{x}}^{\mathrm{u}}=\mathbf{E}_{\mathrm{u}} \mathbf{x}^{\mathrm{u}}+\mathbf{z}^{\mathrm{u}} \tag{7}
\end{equation*}
$$

for uplink, where $\mathbf{E}_{\mathrm{u}}=\mathbf{W}^{H} \mathbf{H}$ is a $K \times K$ matrix containing the equivalent uplink channel with IUI information and $\mathbf{z}^{u}$ is the $K \times 1$ post-equalization noise term.

On the other hand, in the downlink, substituting (4) into (2) leads to

$$
\begin{equation*}
\tilde{\mathbf{x}}^{\mathrm{d}}=\mathbf{E}_{\mathrm{d}} \mathbf{x}^{\mathrm{d}}+\mathbf{n}^{\mathrm{d}} \tag{8}
\end{equation*}
$$

where $\mathbf{E}_{\mathrm{d}}=\mathbf{H}^{T} \mathbf{P}$ is a $K \times K$ matrix containing the equivalent downlink channel with IUI information. For the particular case that $\mathbf{P}^{T}=\mathbf{W}^{H}$, we have $\mathbf{E}_{\mathrm{d}}=\mathbf{E}_{\mathrm{u}}^{T}$, meaning that both equivalent channels are transposed, and therefore experiment the same IUI cancellation properties. From this result it is clear that once an equalization matrix $\mathbf{W}$ is obtained for uplink detection, it can also be applied for downlink precoding with no extra effort. It is interesting to note that, since $\mathbf{P}^{T}=\mathbf{W}^{H}$, it follows that $\mathbf{p}_{i}=\mathbf{w}_{i}^{*}$, so each antenna node can re-use same vector for detection and precoding, ideally reducing complexity and storage needs by half. Said that, in this article we focus mainly on uplink estimation without limiting the results to downlink. In reality, there is a downlink power constraint as the total transmitted power, which is addressed in V.

## III. Centralized vs. Decentralized

In this section we describe the differences between centralized and decentralized Massive MIMO processing and the justification to study the later one.

Uplink estimation based on ZF equalization has two components that should be multiplied: $\mathbf{W}_{\mathrm{ZF}}$ and $\mathbf{y}^{\mathrm{u}}$. The former includes a $K \times K$ matrix inversion, which typically is done in one place, and for that, CSI from all antennas needs to be collected. Apart from that, the observation data vector, $\mathbf{y}^{\mathbf{u}}$, is also needed for estimation. This vector is $M \times 1$, increasing considerably the amount of data to transfer and limiting the scalability of the array. Based on those considerations, we can think of two possible architectures for the Massive MIMO base-station: centralized and decentralized.

Fig. 1(a) presents an architecture based on a central baseband processing node, where baseband samples are exchanged between Remote Processing Units (RPUs) and CPU. Each antenna is connected to a receiver and transmitter circuitry, which involves: RF front-end, $\mathrm{ADC} / \mathrm{DAC}$ and OFDM processing. For simplicity, only uplink is represented in this figure. We can identify some common tasks among these processing elements across different antennas, such as: time synchronization, automatic gain control, local oscillator generation, carrier frequency and sampling rate offset estimation, phase noise compensation, among others. Therefore, a few antennas (together with corresponding receivers/transmitters) can be grouped into one RPU for efficient implementation of such common tasks. However, for simplicity, in this work we only analyze the case where each RPU manages one antenna.

Dedicated physical links would easily exceed the number of I/O connections in current standards, in addition to the increment of the cost of adding a new RPUs when needed. To overcome this, we consider that RPUs are connected to the CPU node by a shared bus as shown in Fig. 1(a).

Even though, this approach can support ZF detection (and precoding) from a functionality point of view, from the implementation point of view, it requires a very high inter-connection data-rate in the bus and at the input of the CPU ( $R_{\mathrm{c}}$ in the figure). As an example, consider a 5G NR-based system with 128 antennas and OFDM as an access technology, then the average data-rate can be calculated as

$$
\begin{equation*}
R_{\mathrm{c}}=\frac{2 w M N_{\mathrm{u}}}{T_{\mathrm{OFDM}}}, \tag{9}
\end{equation*}
$$

where $N_{\mathrm{u}}$ is the number of active subcarriers, $w$ is the bit-width for the baseband samples (real/imaginary parts) after FFT, and $T_{\text {OFDM }}$ is the OFDM symbol duration. For $N_{\mathrm{u}}=3300, w=$ 12 and $T_{\text {OFDM }}=1 / 120 \mathrm{kHz}$ then $R_{\mathrm{c}}=1.2 \mathrm{Tbps}$. This result clearly exceed the limit data-rate for common interfaces, such as eCPRI [7] and PCIe, and furthermore, it is proportional to $M$, which clearly limits the scalability of the system.

As a solution to this limitation, we propose the fullydecentralized architecture for baseband detection and precoding shown in Fig. 1(b). We can observe that channel estimation and estimation/precoding have been moved from the CPU to the RPUs, with detection and decoding as a remaining task in the CPU from physical layer point of view. The benefit of this move
is manifold. Firstly, the inter-connection data-rate scales with $K$ instead of $M$. Secondly, the high complexity requirement in the CPU for channel estimation and data estimation/precoding is now equally distributed among RPUs, which highly simplifies the implementation and overcomes the computational bottleneck and, additionally, CSI is obtained and consumed locally in each RPU without the need for exchange, with the consequent reduction in the required inter-connection data-rate. In addition to the advantages already mentioned, which are common to other decentralized schemes, the proposed architecture presented in this work achieves an unprecedented low inter-connection datarate by the direct connection of RPUs forming a daisy-chain, where the CPU is at one of the ends.

In the daisy-chain, depicted in Fig. 1(b), nodes are connected serially to each other by a dedicated connection. All elements in the chain work simultaneously in pipeline mode, processing and transmitting/receiving to/from the respective next/previous neighbor in the chain. The data is passed through the nodes sequentially, being updated at every RPU. There is an unique connection to the root node where the last estimate is transmitted and therefore been detected by the CPU. An important remark is the average inter-connection data-rate between nodes is the same regardless of the number of elements in the chain. This topology was proposed in [8] and further studied in [1] and [2] with specific algorithms designed for this topology.

When the decentralized architecture in Fig. 1(b) needs to be deployed, antennas can be collocated in the same physical place or distributed over a large area. These antennas and therefore their corresponding RPUs can behave as nodes in the chain, whilst the CPU remains as the root node. There may be multiple chains in a network. The selection of the RPUs to form a chain may depend on the users they are serving. RPUs which serve the same set of users should be in the same chain, so they can work jointly to cancel IUI. This concept fits very well with the distributed wireless communication system [16], the recent cell-free Massive MIMO concept [17] and the promising large intelligent surface [18].

Decentralized architectures, such as the one shown in Fig. 1(b), require other type of algorithms compared to Fig. 1(a). In the next section we introduce our proposed algorithm, which is a method for obtaining $\mathbf{w}_{m}$ and $\mathbf{p}_{m}$ as the equalization and precoding vectors, respectively.

## IV. Coordinate Descent

Our proposed algorithm is an iterative algorithm based on the gradient descent (GD) optimization, in which the gradient information is approximated with a set of observations in every step. From this, each antenna can obtain its own equalization/precoding vector sequentially in a coordinate descent approach. The main advantage of this method is that it does not require access to all observations at each iteration, becoming an ideal choice for large scale distributed systems.

## A. Preliminaries

From (7) we know that in the non-IUI case, $\mathbf{E}_{\mathrm{u}}$ is a diagonal matrix, which is the case when zero-forcing (ZF) is applied. In
the general case, IUI is not zero and as consequence $\mathbf{E}_{u}$ contains non-zero entries outside the main diagonal.

The objective is to find a matrix $\mathbf{W}$, which cancels IUI to a high extent $\left(\mathbf{E}_{\mathrm{u}} \approx \mathbf{I}\right)$, while fulfilling the following conditions:

- Uses daisy-chain as a base topology, so we exploit the advantages seen in Section III.
- No exchange of CSI between nodes. Only local CSI.
- Limited amount of data to pass between antenna nodes. It should depend on $K$ instead of $M$, to enable scalability.
- Limit the dependency on the central processing unit in order to reduce data transfer, processing and memory requirements of that unit. One consequence of this is to avoid matrix inversion in the central unit.


## B. Algorithm Formulation

The algorithm setup is that one intends to solve the unconstrained Least Squares (LS) problem in the uplink

$$
\begin{equation*}
\hat{\mathbf{x}}=\underset{\mathbf{x}}{\arg \min }\|\mathbf{y}-\mathbf{H x}\|^{2} \tag{10}
\end{equation*}
$$

via a GD approach. The gradient of (10) equals $\nabla_{\mathbf{x}}=\mathbf{H}^{H} \mathbf{H x}- \mathbf{H}^{H} \mathbf{y}$. Even though $\mathbf{H}^{H} \mathbf{H}$ and $\mathbf{H}^{H} \mathbf{y}$ can be formulated in a decentralized way, the selection of $\mathbf{x}$ and the product with $\mathbf{H}^{H} \mathbf{H}$ is preferably done in a central processing unit to limit latency and inter-connection data-rates. Following the fullydecentralized approach and the intention to off-load the equalization/precoding computation from the CPU to the RPUs, we propose a different approach.

The proposed method can be derived as an approximate version of GD that can be operated in a decentralized architecture with minimum CPU intervention. It does so by computing, at each antenna, as much as possible of $\nabla_{\mathbf{x}}$ with the information available at the antenna. Then the estimate $\hat{\mathbf{x}}$ is updated by using a scaled version of the "local" gradient and the antenna passes the updated estimate on to the next antenna.

The above described procedure can, formally, be stated as

$$
\begin{align*}
& \varepsilon_{m}=y_{m}-\mathbf{h}_{m}^{T} \hat{\mathbf{x}}_{m-1} \\
& \hat{\mathbf{x}}_{m}=\hat{\mathbf{x}}_{m-1}+\mu_{m} \mathbf{h}_{m}^{*} \varepsilon_{m}, \tag{11}
\end{align*}
$$

for antenna $m$, where $\mu_{m}$ is a scalar step-size. The update rule in (11) corresponds to the Kaczmarz method [19], whose step-size is according to [20]

$$
\begin{equation*}
\mu_{m}=\frac{\mu}{\left\|\mathbf{h}_{m}\right\|^{2}}, \tag{12}
\end{equation*}
$$

where $\mu \in \mathbb{R}$ is a relaxation parameter. In case of consistent systems, this is $\mathbf{y}=\mathbf{H x}$ (if SNR is high enough or there is no noise), $\mu=1$ is optimum and the method converge to the unique solution. Otherwise, when the system is inconsistent, $\mu$ give us an extra degree of freedom, which allows to outperform the $\mu=1$ case, as we will see in Section V.

After $M$ iterations of (11) we have

$$
\begin{aligned}
\hat{\mathbf{x}}_{M}= & \prod_{m=1}^{M}\left(\mathbf{I}_{K}-\mu_{m} \mathbf{h}_{m}^{*} \mathbf{h}_{m}^{T}\right) \hat{\mathbf{x}}_{0} \\
& +\sum_{m=1}^{M} \prod_{i=m+1}^{M}\left(\mathbf{I}_{K}-\mu_{i} \mathbf{h}_{i}^{*} \mathbf{h}_{i}^{T}\right) \mu_{m} \mathbf{h}_{m}^{*} y_{m} .
\end{aligned}
$$

```
Algorithm 1: Proposed algorithm
    Input : $\mathbf{H}=\left[\mathbf{h}_{1}, \mathbf{h}_{2} \cdots \mathbf{h}_{M}\right]^{T}$
    Preprocessing:
    $\mathbf{A}_{0}=\mathbf{I}_{K}$
    for $m=1,2, \ldots, M$ do
        $\mathbf{w}_{m}=\mu_{m} \mathbf{A}_{m-1} \mathbf{h}_{m}$
        $\mathbf{A}_{m}=\mathbf{A}_{m-1}-\mathbf{w}_{m} \mathbf{h}_{m}^{H}$
    end
    Output : $\mathbf{W}=\left[\mathbf{w}_{1}, \mathbf{w}_{2} \cdots \mathbf{w}_{M}\right]^{T}$
```

If we assume $\hat{\mathbf{x}}_{0}=\mathbf{0}_{K \times 1},{ }^{1}$ then it is possible to express $\hat{\mathbf{x}}_{M}$ as linear combination of $\mathbf{y}$, in the same way as (3), and identify $\mathbf{w}_{m}$ (the equalization vector associated to antenna $m$ ) as

$$
\begin{equation*}
\mathbf{w}_{m}=\left[\prod_{i=m+1}^{M}\left(\mathbf{I}_{K}-\mu_{i} \mathbf{h}_{i} \mathbf{h}_{i}^{H}\right)\right] \mu_{m} \mathbf{h}_{m} . \tag{13}
\end{equation*}
$$

If (11) is applied in reverse antenna order ( $m=M \cdots 1$ ), then we obtain a different estimation. The expression for $\mathbf{w}_{m}$ when using the alternative approach is

$$
\begin{equation*}
\mathbf{w}_{m}=\mu_{m} \mathbf{A}_{m-1} \mathbf{h}_{m}, \tag{14}
\end{equation*}
$$

where matrix $\mathbf{A}_{m}$ is defined as

$$
\begin{equation*}
\mathbf{A}_{m}=\prod_{i=1}^{m}\left(\mathbf{I}_{K}-\mu_{i} \mathbf{h}_{i} \mathbf{h}_{i}^{H}\right) . \tag{15}
\end{equation*}
$$

It is important to remark that both approaches lead to different $\mathbf{w}_{m}$ sequences, however the overall performance should be the same if CSI in all antennas shows same statistical properties (stationarity across antennas).

## C. Algorithm Design and Pseudocode

In this subsection we derive an equivalent and more attractive form for the calculation of the weights of the algorithm in (14) in an easy and low-complexity way, suitable for hardware implementation.

The algorithm description is shown in Algorithm 1. The vector $\mathbf{w}_{m}$ is computed in each antenna, while the matrix $\mathbf{A}_{m-1}$ gets updated according to the recursive rule: $\mathbf{A}_{m}=\mathbf{A}_{m-1}- \mathbf{w}_{m} \mathbf{h}_{m}^{H}$. Then, $\mathbf{w}_{m}$ is stored for the detection and precoding phase, and $\mathbf{A}_{m}$ is passed to the next antenna node for further processing.

From Algorithm 1 we can observe that after $M$ steps we achieve the following expression: $\mathbf{A}_{M}=\mathbf{I}_{K}-\mathbf{E}_{\mathrm{u}}^{*}$. Then, if perfect IUI cancellation is achieved, $\mathbf{E}_{\mathrm{u}}=\mathbf{I}_{K}$ and therefore $\mathbf{A}_{M}=\mathbf{0}$. As a consequence we can take $\left\|\mathbf{A}_{m}\right\|^{2}$ as a metric for residual IUI. The interpretation of Algorithm 1 is as follows. $\left\|\mathbf{A}_{m}\right\|$ is reduced by subtracting from $\mathbf{A}_{m}$ a rank-1 approximation to itself. In order to achieve that, $\mathbf{A}_{m}$ is projected onto $\mathbf{h}_{m}$ to obtain $\mathbf{w}_{m}$, therefore $\mathbf{w}_{m} \mathbf{h}_{m}^{H}$ is the best rank-1 approximation to $\mathbf{A}_{m}$, having $\mathbf{h}_{m}$ as vector base. Ideally, if the channel is rich enough, vectors $\mathbf{h}_{m}$ are weakly correlated and assuming $M$ is

[^1]```
Algorithm 2: Proposed algorithm multiple iterations
    Input: $\mathbf{H}=\left[\mathbf{h}_{1}, \mathbf{h}_{2} \cdots \mathbf{h}_{M}\right]^{T}$
    Preprocessing:
    $\mathbf{A}_{0,1}=\mathbf{I}_{K}$
    $\mathbf{w}_{m, 1}=\mathbf{0}, m=1, \ldots, M$
    for $n=1,2, \ldots, n_{\text {iter }}$ do
        for $m=1,2, \ldots, M$ do
            $\mathbf{w}_{m, n}=\mathbf{w}_{m, n-1}+\mu_{m} \mathbf{A}_{m-1, n} \mathbf{h}_{m}$
            $\mathbf{A}_{m, n}=\mathbf{A}_{m-1, n}-\mathbf{w}_{m, n} \mathbf{h}_{m}^{H}$
        end
        $\mathbf{A}_{0, n+1}=\mathbf{A}_{M, n}$
    end
    Output $: \mathbf{W}=$
                $\left[\mathbf{w}_{1, n_{\text {iter }}}, \mathbf{w}_{2, n_{\text {iter }}} \cdots \mathbf{w}_{M, n_{\text {iter }}}\right]^{T}$
```

large (Massive MIMO scenario) then IUI can be canceled out to a high extent. ${ }^{2}$

The role of step-size $\mu$ is to control how much IUI is removed at every iteration. High values will tend to reduce IUI faster at the beginning when the amount to remove is high, but will lead to oscillating or unstable residual IUI after some iterations because the steps are too big, so the introduced error dominates. Low values for $\mu$ will ensure convergence of the algorithm and a relatively good IUI cancellation at the expense of a slower convergence.

## D. Multiple-Iterations Along the Array

Recalling from Section IV-C, Algorithm 1 reduces the norm of $\mathbf{A}$ at each step, providing as a result $\mathbf{A}_{M}$, which contains the residual IUI after the algorithm is run along the array. It is possible to expand the algorithm and apply $\mathbf{A}_{M}$ as initial value, $\mathbf{A}_{0}$ for a new iteration through the array, with the intention of decreasing even more the norm of $\mathbf{A}$. The pseudocode of the expanded version is shown in Algorithm 2, with $n_{\text {iter }}$ iterations, and as it can be seen, an increment of $\mathbf{w}_{m}$ is computed at each iteration. From topology point of view, it requires an extra connection between last and first RPUs, closing the daisy-chain and becoming a ring. It is expected to improve the performance at the expense of increasing the latency.

## V. Analysis

In this section we present an analysis of the proposed solution. The main points are:

- Performance analysis of the presented solution based on SIR, SINR and BER evaluation, and comparison with other methods.

[^2]TABLE I
Parameters
| Parameter | Description |
| :--- | :--- |
| $\alpha$ | $1-\frac{2 \mu}{K}+\frac{\mu^{2}}{K(K+1)}$ |
| $\beta$ | $\frac{\mu^{2}}{K(K+1)}$ |
| $\nu$ | $1-\frac{\mu}{K}$ |
| $\epsilon$ | $1-\frac{2 \mu}{K}+\frac{\mu^{2}}{K}$ |


- Complexity and timing analysis, including computational complexity, inter-connection throughput, memory requirement and latency.
As was commented in the Introduction, the analysis presented in this section is quite general and not dependent on any specific hardware implementation. The idea is to provide high level guidelines on algorithm-hardware trade-offs, system parameter selections, and hardware architectures. A more specific analysis can be performed when one has decided the dedicated implementation strategy.


## A. Performance

In this subsection we obtain and present different metrics to evaluate and compare the performance of the proposed algorithm. The analysis we present is divided as follows: Derivation of SIR and SINR closed form expressions, bit-error-rate (BER) analysis of the proposed algorithm based on ideal and measured channels and comparison with other methods, such as MF and ZF. The performance analysis that follows is focused on uplink, but it can be extended to downlink.

1) SIR \& SINR: Specifically for user $k$, (7) is reduced to

$$
\hat{x}_{k}^{\mathrm{u}}=E_{k, k} x_{k}^{\mathrm{u}}+\sum_{i=1, i \neq k}^{K} E_{k, i} x_{i}^{\mathrm{u}}+z_{k},
$$

where the first term represents the desired value to estimate (scaled version), the second one is the interference from other users and the third one is due to noise. The signal-to-interference ratio (SIR) for user $k$ is defined as

$$
\begin{equation*}
\mathrm{SIR}_{k}=\frac{\mathbb{E}\left|E_{k, k}\right|^{2}}{\mathbb{E}\left\{\sum_{i=1, i \neq k}^{K}\left|E_{k, i}\right|^{2}\right\}} . \tag{16}
\end{equation*}
$$

And for the signal-to-interference-and-noise ratio (SINR) we have

$$
\begin{equation*}
\operatorname{SINR}_{k}=\frac{\mathbb{E}\left|E_{k, k}\right|^{2}}{\mathbb{E}\left\{\sum_{i=1, i \neq k}^{K}\left|E_{k, i}\right|^{2}\right\}+\mathbb{E}\left|z_{k}\right|^{2}} . \tag{17}
\end{equation*}
$$

A list of parameters and their corresponding values are presented in Table I, which are used in the following propositions.

From (16) it is possible to obtain a closed-form expression of the SIR as follows:

Proposition 1: With perfect CSI and channel model as defined in Section II, SIR per user in uplink with CD algorithm for estimation is

$$
\begin{equation*}
\mathrm{SIR}=\frac{1-2 \nu^{M}+\alpha^{M}\left(1-\frac{1}{K}\right)+\epsilon^{M} \frac{1}{K}}{\left(1-\frac{1}{K}\right) \cdot\left(\epsilon^{M}-\alpha^{M}\right)}, \tag{18}
\end{equation*}
$$

which can be simplified in case of relatively large $M, K$, and $\frac{M}{K}$, which is the case of Massive MIMO, as

$$
\begin{equation*}
\mathrm{SIR} \approx e^{\mu(2-\mu) \frac{M}{K}} \tag{19}
\end{equation*}
$$

Proof: See Appendix-A. $\square$

The maximum value of (19) is achieved for $\mu=1$ and the SIR value only depends on the ratio $\frac{M}{K}$ in an exponential fashion, showing how fast the IUI is canceled as $M$ grows, and therefore ZF is approached. As an example, for a target value of SIR $= 40 \mathrm{~dB}, \frac{M}{K}=10$ meets the requirement, which is a typical ratio in Massive MIMO regime.

Regarding SINR, it can be derived based on previous results as

Proposition 2: With perfect CSI and channel model as defined in Section II, SINR per user in uplink with CD algorithm for estimation is given by

$$
\begin{equation*}
\mathrm{SINR}=\frac{1-2 \nu^{M}+\alpha^{M}\left(1-\frac{1}{K}\right)+\epsilon^{M} \frac{1}{K}}{\left(1-\frac{1}{K}\right)\left(\epsilon^{M}-\alpha^{M}\right)+\frac{N_{0}}{K-1}\left(\frac{\mu}{2-\mu}\right)\left(1-\epsilon^{M}\right)}, \tag{20}
\end{equation*}
$$

which can be simplified in case of relatively large $M, K$, and $\frac{M}{K}$, which is the case of Massive MIMO, as

$$
\begin{equation*}
\mathrm{SINR} \approx\left[e^{-\mu(2-\mu) \frac{M}{K}}+\frac{1}{K \cdot \mathrm{SNR}}\left(\frac{\mu}{2-\mu}\right)\right]^{-1} . \tag{21}
\end{equation*}
$$

Proof: See Appendix-B. $\square$

The first term in (21) represents SIR containing IUI information, while the second one takes into account the post-equalized noise power. For high SNR, the first term is dominant and SINR $\rightarrow e^{\mu(2-\mu) \frac{M}{K}}$, which depends on $\frac{M}{K}$ and $\mu$, but not on SNR. On the other hand, when SNR is low, the second term is dominant and SINR $\rightarrow \mathrm{SNR} \cdot K\left(\frac{2-\mu}{\mu}\right)$ as $M$ grows, which grows linearly with SNR and $K$ (up to certain value). This linear dependency on $K$ is due to the post-equalization noise is equally distributed among the users. While the noise power per antenna remains constant, the portion assigned to each user decays as $K$ grows, so the SINR per user grows linearly. However, as $K$ increases the IUI does so (first term in (21) grows), and both effects cancel out at some point, being IUI dominant afterwards, with the corresponding decay of SINR.

The optimal value of $\mu$, denoted as $\mu^{*}$, depends on $M, K$, and the specific channel. For the i.i.d. case, defined in Section II, it is possible to obtain $\mu^{*}$ by numerical optimization over (20). An approximate value, denoted as $\mu_{0}$, is presented as follows.

Proposition 3: A recommended value for $\mu_{0}$, in the vicinity of $\mu^{*}$, under CD and i.i.d. channel as defined in Section II, is given by

$$
\begin{equation*}
\mu_{0}=\frac{1}{2} \frac{K}{M} \log (4 M \cdot \mathrm{SNR}) . \tag{22}
\end{equation*}
$$

Proof: See Appendix-C. $\square$

As a side result, from the analysis performed in this section, we can extract interesting properties of the matrix $\mathbf{W}$, such the following one:

Proposition 4: The equalization matrix $\mathbf{W}$ as result of CD algorithm satisfies the next properties for $\mu \in[0,2)$

$$
\begin{equation*}
\mathbb{E}\|\mathbf{W}\|_{F}^{2}=\frac{K}{K-1} \cdot \frac{\mu}{2-\mu} \cdot\left(1-\epsilon^{M}\right) . \tag{23}
\end{equation*}
$$

Proof: See Appendix-D.

This result is relevant in downlink, where a transmission power budget is needed. Expression in (23) is a monotonically growing function of $\mu$. It can be shown that total transmitted mean power is bounded by $4 \frac{M}{K}$, reaching this value at $\mu=2$. However, as we will see in next section, optimal $\mu$ for i.i.d. Gaussian channel is within the range ( 0,1 ], therefore for a large enough $K$, we have $\mathbb{E}\|\mathbf{W}\|_{F}^{2} \leq 1$, which does not depend on $M$, therefore ensure the scalability of the proposed solution.

Expression (20) is plotted in Fig. 2(a) showing SINR vs $\mu$ for CD under different SNR values and step-size according to (12). As expected, optimal $\mu$ approaches 1 as SNR grows. Simulation results shows a good match with (20). The curve with $\mu_{0}$ values obtained from (22) is also plotted for a wide range of SNR. It is observed how the $\mu_{0}$ value is reasonably close to the optimum for the SNR range depicted. Furthermore, the result is much closer to ZF than MRC values, which are $\{40.5,30.5,20.5,10.5\} \mathrm{dB}$ and $\{9.0,9.0,8.8,6.8\} \mathrm{dB}$ respectively for the different SNR values used in the figure.

Fig. 2(b) shows simulation results for the CD algorithm performance under different channels. For some of them we use a model (i.i.d and WINNER II) and others are based on real measurements (Rich A and LOS A). For this comparison we use different $\frac{M}{K}$ ratio and the step-size according to (12). Rich A is non-line-of-sight (NLOS) channel, rich in scatters, while LOS A is predominantly line-of-sight (LOS) channel. WINNER II is obtained from a NLOS scenario with a uniform linear array at the BS, with M elements separated by $\lambda / 2$. Users are randomly located in a $300 \mathrm{~m} \times 300 \mathrm{~m}$ area, with the BS at the center. Carrier frequency is 2 GHz . It is noticed how rich channels (i.i.d and WINNER II) provide better performance. SINR levels reached by ZF are $\{20.9,20.9,19.8,17.6\} \mathrm{dB}$ and for MRC they are $\{14.3,15.2,7.8,4.8\} \mathrm{dB}$, in both cases for the i.i.d., WINNER II, Rich A and LOS A channels, respectively. It is also noticed that CD performance lies in between ZF and MRC for these scenarios.

Fig. 3 shows SINR versus $\frac{M}{K}$ for $M=128$ and SNR $=0 \mathrm{~dB}$. SINR for CD is shown comparing the effect of using $\mu^{*}$ and $\mu_{0}$ according to (22). We observe that $\frac{M}{K} \approx 10$ (equivalent to $K \approx 12)$ is the preferred working point, where SINR reaches the maximum value and $\mu_{0}$ gives the same result as $\mu^{*}$. We also compare the performance with ZF and MRC algorithms.

As presented in Subsection IV-D, the algorithm can be extended to perform multiple iterations through the array, in order to increase the performance. Figure 4 shows SINR versus $\mu$ for a different number of iterations through the array together with ZF for comparison. From the figure we can notice that the maximum SINR increases after each iteration, approaching to ZF. It is also relevant to note that $\mu^{*}$ changes with the number of iterations.
2) $B E R$ : $B E R$ versus SNR is shown in Fig. 5 under i.i.d. channel for three different methods: CD, ZF and MRC. CD is shown using two different values for $\mu: 1$ and $\mu^{*}$. It is noticeable the great impact of the selected $\mu$ and therefore the importance of selecting an appropriate value.

The effect of non-ideal CSI in the BER is shown in Fig. 6 for ZF and CD (for $\mu^{*}$ ). The non-ideal CSI is modeled as an idealCSI with a noise contribution (complex normal distributed) with a variance equal to $N_{0}$, therefore it depends inversely on SNR.

- No boosting in pilots is used. As it can be observed, for SNR <

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-08.jpg?height=789&width=1646&top_left_y=219&top_left_x=206)
Fig. 2. (a) SINR vs $\mu$ under different SNR. $\mathrm{M}=128$ and $\mathrm{K}=16$. (b) SINR vs $\mu$ under different channels. $\mathrm{M}=128$ and $\mathrm{K}=5$. SNR $=0 \mathrm{~dB}$.

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-08.jpg?height=744&width=762&top_left_y=1100&top_left_x=199)
Fig. 3. SINR(dB) versus $\frac{M}{K}$ for $\mathrm{SNR}=0 \mathrm{~dB}$ and $\mathrm{M}=128$. SINR for CD is plotted in the case of $\mu^{*}$ (dashed) and $\mu_{0}$ (solid) are used. i.i.d. channel.

0 dB the SNR gap is very small and increases as long as SNR increases too, in a similar fashion as the ideal CSI case. For SNR $>0$ the SNR gap in both cases is similar.

## B. Complexity \& Timing

In this subsection we analyze the complexity of the proposed solution from three different domains: computational complexity (data processing), inter-connection throughput (data movement) and memory (data storage). Timing in the form of total system latency is also analyzed.

For this analysis we assume a frame structure based on OFDM, which contains one dedicated OFDM symbol per frame for channel estimation based on orthogonal pilots, so each one

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-08.jpg?height=725&width=766&top_left_y=1095&top_left_x=1112)
Fig. 4. SINR vs. SNR for $M=128, K=16.16$ QAM. i.i.d. channel. SNR $=0 \mathrm{~dB}$. SINR after a certain number of iterations through the array. ZF added for comparison.

is dedicated to one of the users in a consecutive way. The other symbols convey users' data. Under the TDD assumption, some of them are used for DL and others for UL. We also assume that all RPUs perform IFFT/FFT in parallel with an output data-rate of $\frac{N_{\mathrm{u}}}{T_{\text {OFDM }}}$.

We can exploit channel correlation based on the Physical Resource Block (PRB) concept in 3 GPP. A PRB is a region in frequency-time domain where the channel response is assumed to be approximately constant across all subcarriers within that PRB. Within an OFDM symbol, the number of subcarriers in each PRB and the number of PRB per symbol, defined as $N_{\mathrm{sc}, \mathrm{PRB}}$ and $N_{\mathrm{PRB}}$ respectively, are related as follows: $N_{\mathrm{u}}=N_{\mathrm{PRB}} N_{\mathrm{sc}, \mathrm{PRB}}$. We define $T_{\mathrm{PRB}}$ as the time needed by $N_{\mathrm{sc}, \mathrm{PRB}}$ consecutive subcarriers to come out the FFT.

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-09.jpg?height=727&width=783&top_left_y=223&top_left_x=176)
Fig. 5. BER vs. SNR for $M=128, K=16.16$ QAM. i.i.d. channel.

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-09.jpg?height=731&width=785&top_left_y=1061&top_left_x=174)
Fig. 6. BER vs. SNR for $M=128, K=16.16$ QAM. i.i.d. channel. Comparison between ideal and non-ideal CSI.

For each PRB we have a different channel matrix and also MIMO model as in (1) and (2). Then, it is required to have a unique set of vectors $\mathbf{w}_{m}$ and $\mathbf{p}_{m}(m=1 \ldots M)$ per antenna, as in (3) and (5), for uplink detection and downlink precoding respectively. The phase where these vectors are computed is named formulation, while the phase where user's data is processed is named filtering and precoding for UL and DL respectively. To minimize data buffering, formulation needs to be completed before filtering/precoding starts. This imposes the constraint that the formulation phase needs to be finished within one OFDM symbol, or in other words, all antennas need to obtain these vectors and the matrix $\mathbf{A}$ needs also to pass through the array within one OFDM symbol. A diagram of the main activities involved and their timing relationship is shown in Fig. 7. The
analysis assumes that the processing and data transmission are pipelined in each RPU so they concurrently operate.

1) Computational Complexity:

- Formulation phase: The number of complex multiplications needed to formulate one precoding/filtering vector per antenna are $C_{\text {form }} \approx 2 K^{2}$, which represents the matrixvector product to obtain $\mathbf{w}_{m}$ and the outer product to update $\mathbf{A}_{m}$ according to algorithm 1. Other possible required operations such as norm, square root or division are assumed to be negligible.
- Filtering phase: During the filtering phase, each RPU performs the required operations for UL detection. Vectors $\mathbf{w}_{m}$ are applied to all observations (data subcarriers), $y_{m}^{\mathrm{u}}$, under the same PRB. The complexity measured in number of complex multiplications per antenna and per $N_{\mathrm{sc}, \mathrm{PRB}}$ subcarriers is $C_{\text {filt }}=K N_{\text {sc }, \text { PRB }}$.
- Precoding phase: During the precoding phase, each RPU performs the operations required by (5). Similarly to the filtering case, the same vector $\mathbf{p}_{m}$ is applied to all data vectors $y_{m}^{\mathrm{d}}$ under same PRB. The complexity measured in number of complex multiplications per antenna and PRB is $C_{\text {prec }}=K N_{\text {sc }, \text { PRB }}$.

2) Inter-Connection Data-Rate:

- Formulation phase: The average inter-connection data-rate during formulation can be calculated assuming that the average time to complete a transfer of a matrix $\mathbf{A}$ is $T_{\mathrm{PRB}}$, which leads to an average rate of

$$
R_{\mathrm{d}, \text { form }}=\frac{2 w_{\mathrm{A}} K^{2} N_{\mathrm{PRB}}}{T_{\mathrm{OFDM}}},
$$

where the numerator represents the amount of bits to transfer (all matrices $\mathbf{A}$ in a symbol) and $w_{\mathbf{A}}$ is the bit-width of A entries (real/imaginary parts).

- Filtering phase: Partial filtering results from each RPU are added up through the chain. The average inter-connection data-rate per dedicated link can be calculated as

$$
R_{\mathrm{d}, \mathrm{filt}}=\frac{2 w_{\mathrm{d}} K N_{\mathrm{u}}}{T_{\mathrm{OFDM}}},
$$

where $w_{\mathrm{d}}$ is the bit-width of baseband samples exchanged among RPUs.

- Precoding phase: In the precoding phase, the data vectors $\mathrm{x}^{\mathrm{d}}$ are passed through the array for processing. Each node receives a vector which is passed to next node without any required pause (broadcasting). This leads to the same datarate as in the filtering case.

3) Latency: The processing latency in the formulation phase for one antenna is given from next expression

$$
\begin{aligned}
T_{\mathrm{proc}, \mathrm{form}} & =\frac{C_{\mathrm{form}} T_{\mathrm{CLK}}}{N_{\mathrm{mult}}} \\
& \approx \frac{2 K^{2} T_{\mathrm{CLK}}}{N_{\mathrm{mult}}},
\end{aligned}
$$

where $N_{\text {mult }}$ is the number of multipliers available in each RPU that can be used in parallel, $T_{\text {CLK }}$ is the clock period and we assume that one complex multiplication can be done within one $T_{\text {CLK }}$. Total latency is expressed as

$$
\text { Lat }_{\text {form }}=M \cdot T_{\text {proc,form }}+\left(N_{\mathrm{RPU}}-1\right) \cdot T_{\text {trans }},
$$

![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-10.jpg?height=777&width=1741&top_left_y=223&top_left_x=165)
Fig. 7. Time diagram representing formulation and filtering/precoding activities performed in the antenna modules. Each OFDM symbol is split into $N_{\mathrm{PRB}}$ blocks ( $N$ in the figure) in the same order as data come out of any of the receiver FFT. Those blocks which contains pilots are shown as $P_{i}$, while those carrying data are denoted as $D_{i}$. Channel estimation is performed during $C_{i}$ blocks, while formulation is done in $\mathbf{w}_{i}$ blocks. Filtering/precoding data is carried out during the MIMO processing blocks, named $\mathrm{M}_{i}$. As it can be observed, all antennas perform their tasks simultaneously, while formulation is done sequentially as a matrix $\mathbf{A}^{(n)}$ passes through the array. In total, $N$ matrices are passed sequentially through antenna $m$, corresponding to $\mathbf{A}_{m}^{(n)}, n=1 \cdots N$. wi vectors need to be available in the antenna modules before the corresponding data comes out of the receiver FFT so it can be properly processed. Daisy-chain topology exploits the parallelism of the operations by allowing the pipeline of the operations and the fully usage of all dedicated links simultaneously.

where $N_{\text {RPU }}$ is the number of RPUs in the system, and $T_{\text {trans }}$ is the transmission latency between two consecutive RPUs. As said before, formulation needs to be finished within one $T_{\text {OFDM }}$, therefore the formulation latency is constrained as $L a t_{\text {form }}< T_{\mathrm{OFDM}}$. This leads to an upper limit for M as

$$
M<\frac{T_{\mathrm{OFDM}}+T_{\mathrm{trans}}}{T_{\mathrm{proc}, \text { form }}+\frac{T_{\mathrm{trans}}}{M_{\mathrm{RPU}}}},
$$

where $M_{\mathrm{RPU}}=\frac{M}{N_{\mathrm{RPU}}}$ is the number of antennas per RPU, which is considered as a design parameter. We can consider another limit, slightly lower than previous one but easier to extract conclusions as follows

$$
M<\frac{T_{\mathrm{OFDM}}}{T_{\text {proc,form }}+\frac{T_{\text {trans }}}{M_{\mathrm{RPU}}}} .
$$

We analyze three scenarios:

- $T_{\text {proc,form }} \rightarrow 0$ : When processing time is reduced, by increasing $N_{\text {mult }}$ or decreasing $T_{\text {CLK }}$, then transaction time becomes dominant and a reduction in the number of links allow for higher values of $M$. Formally, the upper value for $M$ scales proportionally to $M_{\text {RPU }}$ as follows

$$
M<M_{\mathrm{RPU}} \cdot \frac{T_{\mathrm{OFDM}}}{T_{\mathrm{trans}}} .
$$

- $T_{\text {trans }} \rightarrow 0$ : By decreasing the transaction time the upper limit of $M$ converges to a certain value, which is inversely proportional to the processing time as follows

$$
M<\frac{T_{\mathrm{OFDM}}}{T_{\mathrm{proc}, \mathrm{form}}} .
$$

- $M_{\text {RPU }} \gg \frac{T_{\text {trans }}}{T_{\text {proc,form }}}$. When $M_{\text {RPU }}$ increases beyond a certain value, processing time becomes dominant and we obtain the same limit as previous point.
In case of filtering, its related processing is done in parallel as soon as data comes out of the FFT. However, partial results needs to be accumulated through the array from RPU 1 to $N_{\text {RPU }}$. This latency is uniquely due to data transfer through the dedicated links, then

$$
\begin{align*}
L a t_{\mathrm{filt}} & =\left(N_{\mathrm{RPU}}-1\right) \cdot T_{\mathrm{trans}} \\
& <L a t_{\mathrm{form}} \\
& <T_{\mathrm{OFDM}} . \tag{24}
\end{align*}
$$

4) Memory: In terms of memory requirement, a centralized architecture requires to store the channel matrix $\mathbf{H}$ fully at the CPU, previous to the inversion. There is a channel matrix per PRB, so CSI storage requires $M_{\mathrm{H}}=2 w_{\mathrm{h}} M K N_{\mathrm{PRB}}$ bits, where $w_{\mathbf{h}}$ represents the bit-width of $\mathbf{H}$ entries (real/imaginary parts), and in order to store the resulting square matrix, $\left(\mathbf{H}^{H} \mathbf{H}\right)^{-1}$ requires $M_{\mathrm{inv}}=2 w_{\mathrm{h}} K^{2} N_{\mathrm{PRB}}$ and therefore the total requirement is: $M_{\text {central }}=M_{\mathrm{H}}+M_{\text {inv }} \approx M_{\mathrm{H}}$.

In the decentralized architecture, each antenna module needs to store the corresponding $\mathbf{h}$, which gets replaced by $\mathbf{w}$ after formulation. Both of them requires the same amount of memory if same bit-width is assumed, which is $M_{\mathrm{w}}=2 w_{\mathrm{h}} K N_{\mathrm{PRB}}$, and the total amount of memory in the system is: $M_{\text {daisy }}= M \cdot M_{\mathbf{w}} \approx M_{\text {central }}$. Therefore, the total amount of memory required for $\mathbf{H}$ and $\mathbf{W}$ is the same in both systems, however the daisy-chain allows a uniform distribution of the memory

TABLE II
Inter-Connection Data-Rate Comparison for Different System Parameters $[G b / s]$
| Scenario |  |  |  |  |
| :--- | :---: | :---: | :---: | :---: |
| $M$ | 32 | 64 | 128 | 256 |
| $K$ | 4 | 8 | 12 | 12 |
| $R_{\mathrm{d}, \text { form }}$ | 12.67 | 50.69 | 114.05 | 114.05 |
| $R_{\mathrm{d}, \text { filt/prec }}$ | 38.02 | 76.03 | 114.05 | 114.05 |
| $R_{\mathrm{c}}$ | 304.13 | 608.26 | 1216.51 | 2433.02 |


TABLE III
Computational Complexity Comparison for Different System Parameters [GOPS]
| Scenario |  |  |  |  |
| :--- | :---: | :---: | :---: | :---: |
| $M$ | 32 | 64 | 128 | 256 |
| $K$ | 4 | 8 | 12 | 12 |
| $C_{\mathrm{d}, \text { ant }}$ | 1.58 | 3.17 | 4.75 | 4.75 |
| $C_{\mathrm{C}}$ | 50.69 | 202.75 | 608.26 | 1216.51 |


requirements across all antenna modules, reducing design complexity, time and cost. As a drawback, we point out the need for data buffering during the filtering phase due to latency in the transfer of partial results, as discussed in the previous subsection (Latency). The buffer size for the RPU closest to the CPU (worst case) can, based on (24), be obtained as

$$
M_{\mathrm{buffer}}=\frac{2 w_{\mathrm{d}} K N_{\mathrm{u}} L a t_{\mathrm{filt}}}{T_{\mathrm{OFDM}}},
$$

which is shared by all antennas belonging to that RPU.

## C. Comparison

Table II shows a comparison of interconnection data-rate between daisy-chain and centralized architecture for different scenarios of $M$ and $K$. It is important to remark that $R_{\mathrm{c}}$ corresponds to the aggregated data/rate at the shared bus, while $R_{\mathrm{d}}$ is the average data/rate in each of the RPU-RPU dedicated links. For the centralized case, (9) is used, while for the daisy-chain case, data-rates are detailed according to the different tasks (formulation, filtering and precoding) as described in Section V-B2. For the numerical results we employ $T_{\text {CLK }}=1 \mathrm{~ns}$ and $w=12$. The rest of system parameters are as follows according to worst case in 5G NR: $N_{\mathrm{u}}=3300, N_{\mathrm{PRB}}=275, N_{\mathrm{sc}, \mathrm{PRB}}=12$ and $T_{\text {OFDM }}=\frac{1}{120 \mathrm{KHz}}$. We observe that for $M=128$ case, daisy-chain requires $\sim 10 \%$ of the inter-connection data-rate needed by the centralized case. This number can even decrease as $\frac{M}{K}$ grows. As it is observed, daisy-chain requires much lower inter-connection data-rates than the centralized counterpart. We remark that if we take into account the total inter-connection data-rate in the decentralized case, which is $N_{\mathrm{RPU}} R_{\mathrm{d}, \text { form }}$, may easily exceed the centralized counterpart $R_{\mathrm{c}}$, however the decentralized architecture is able to distribute this data-rate equally across all links, reducing considerably the requirements for each of them.

Table III shows a computational complexity comparison between centralized and decentralized architectures. $C_{\mathrm{d} \text {,ant }}$ represents complex multiplications per second and per antenna in the

TABLE IV
Latency Comparison for Different System Parameters
| Scenario |  |  |  |  |
| :--- | :---: | :---: | :---: | :---: |
| $M$ | 32 | 64 | 128 | 256 |
| $K$ | 4 | 8 | 12 | 12 |
| Lat $(\mu s)$ | 0.83 | 2.52 | 7.71 | 15.52 |
| Lat/T ${ }_{\text {OFDM }}$ | 0.10 | 0.30 | 0.92 | 1.86 |


TABLE V
Memory Requirement Comparison for Different System Parameters [kbits]
| Scenario |  |  |  |  |
| :--- | :--- | :--- | :--- | :--- |
| M | 32 | 64 | 128 | 256 |
| K | 4 | 8 | 12 | 12 |
| $M_{\mathbf{w}}$ (ant) | 26.4 | 52.8 | 79.2 | 79.2 |
| $M_{\text {buffer }}(R P U)$ | 26.6 | 114.1 | 353.6 | 718.5 |
| $M_{\mathrm{H}}$ | 844.8 | 3379.2 | 10137.6 | 20275.2 |
| $M_{\text {inv }}$ | 105.6 | 422.4 | 950.4 | 950.4 |


decentralized case, while $C_{\mathrm{c}}$ is the computational complexity required by CPU in centralized system. In both cases, only filtering/precoding is taken into account because formulation depends on how often channel estimation is available. The result of the comparison is meaningful. Even tough, the total complexity in the decentralized system is approximately equal to the centralized counterpart, this is $M \cdot C_{\mathrm{d}, \text { ant }} \approx C_{\mathrm{c}}$, our decentralized solution is able to divide equally the total computational complexity among all existing RPUs, relaxing considerably the requirements compared to the CPU in centralized case. The relatively low number obtained for the daisy-chain allows the employment of cheap and general processing units in each RPU, in opposite to the centralized architecture where the total complexity requirement is on the CPU.

Numerical results for latency are shown in Table IV for $N_{\text {mult }}=8, T_{\text {trans }}=100 n s$ and $N_{\text {RPU }}=\frac{M}{4}$. These design parameters meets the constraint $L a t<T_{\text {OFDM }}$ up to $M=128$. For larger arrays there are different solutions: allows the latency to increase and buffer the needed input data (need for larger memory), group more antennas in each RPU (which reduces the number of links but increase the complexity of the CPU controlling each RPU), and/or employ low-latency link connections (reducing $T_{\text {trans }}$ at the expense of higher cost). It is relevant to note that $T_{\text {OFDM }}$ value in the table is the worst case $1 / 120 \mathrm{KHz}$.

In Table V a comparison between both systems from memory perspective is shown. If $w_{\mathbf{h}}=12$ and $N_{\mathrm{PRB}}=275$ are assumed, then for the $M=128$ case, each antenna module in the daisychain only needs $\sim 80$ kbits of memory and each RPU needs at maximum 354 kbits for buffering, while in the centralized architecture, the central processor requires $\sim 11$ Mbits, which is a challenging number for a cache memory. The memory requirement grows proportionally to M in the centralized system, while that does not happen in $M_{\mathbf{w}}$. In order to reduce the buffer size we can group more antennas in each RPU, so all of them share the same buffer memory.

TABLE VI Properties
| $\mathbb{E}\left\{\frac{\mathbf{\mathbf { h h } ^ { H }}}{\\|\mathbf{h}\\|^{2}}\right\}$ $\mathbb{E}\left\{\frac{\mathbf{\mathbf { h h } ^ { H }}}{\\|\mathbf{h}\\|^{4}}\right\}$ | $\frac{1}{K} \mathbf{I}$, $\frac{1}{K(K-1)} \mathbf{I}$ | if $k=i=j$ if $k \neq i=j$ if $i \neq j$, |
| :--- | :--- | :--- |
|  |  |  |
| $\left[\mathbb{E}\left\{\frac{\left\|h_{k}\right\|^{2} \mathbf{h h}^{H}}{\\|\mathbf{h}\\|^{4}}\right\}\right]_{i, j}$ | $\left\{\begin{array}{l}\mathbb{E}\left\{\frac{\left\|h_{k}\right\|^{4}}{\\|\mathbf{h}\\|^{4}}\right\}=\frac{2}{K(K+1)} \\ \mathbb{E}\left\{\frac{\left\|h_{k}\right\|^{2}\left\|h_{i}\right\|^{2}}{\\|\mathbf{h}\\|^{4}}\right\}=\frac{1}{K(K+1)} \\ 0\end{array}\right.$ |  |
| $\mathbb{E}\left\{\mathbf{Q}_{m}\right\}$ | $\nu \mathbf{I}, \forall m$ |  |
| $\mathbb{E}\{\mathbf{A}\}$ | $\nu^{M} \mathbf{I}$ |  |


## VI. Conclusion

In this article we proposed an architecture for Massive MIMO base-station for uplink detection and downlink precoding, which is based on the fully distribution of the required baseband processing across all antenna modules in the system. The main goal is to reduce the inter-connection data-rate needed to carry out the processing tasks and enable the scalability needed in Massive MIMO. We continued our previous work in this topic [1], [2] by a detailed introduction to the CD algorithm and its application to the Massive MIMO case. We also presented an extensive analysis of the expected performance of the system, the inter-connection data-rate, complexity, latency and memory requirements. The results show that there is a performance loss compared to ZF, but unlike MF, our proposed method does not have an error floor, from which we can not recover, while the inter-connection data-rate is distributed avoiding the aggregation of the centralized approach. At the same time, complexity and memory requirements per antenna module are easy to meet with commercial off-the-self hardware, which proves the scalability of this solution.

## Appendix

In the appendix we present two propositions which are going to support the proof of propositions 1 and 2 seen in Section V. We start with some important considerations.

Let's define the random matrix $\mathbf{Q}_{i}$ as

$$
\begin{equation*}
\mathbf{Q}_{i} \triangleq \mathbf{I}_{K}-\mu_{i} \mathbf{h}_{i} \mathbf{h}_{i}^{H}, \tag{25}
\end{equation*}
$$

where $\mathbf{h}_{i} \sim \mathcal{C} \mathcal{N}(0, \mathbf{I})$ and independent CSI is assumed between antennas, this is $\mathbb{E}\left\{\mathbf{h}_{i}^{H} \mathbf{h}_{j}\right\}=\delta_{i j}, \forall i, j$. Additionally, based on (25) we can rewrite (15) as

$$
\begin{equation*}
\mathbf{A}_{m}=\mathbf{Q}_{1} \mathbf{Q}_{2} \cdots \mathbf{Q}_{m}, \tag{26}
\end{equation*}
$$

as well as (14), which can be expressed in the following form

$$
\begin{equation*}
\mathbf{w}_{m}=\mu_{m} \mathbf{Q}_{1} \mathbf{Q}_{2} \cdots \mathbf{Q}_{m-1} \mathbf{h}_{m} . \tag{27}
\end{equation*}
$$

We list in Table VI some useful properties which are used throughout this section.

The previous properties are based on the following proofs:

- $\mathbb{E}\left\{\frac{\mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{2}}\right\}=a \mathbf{I}$, where $a$ is a complex number, due to the i.i.d. property among elements in $\mathbf{h}$. Applying the trace operator to both sides of previous equality, it follows that $a=\frac{1}{K}$, which proves the property.
- $\mathbb{E}\left\{\frac{\mathbf{h h}^{H}}{\|\mathbf{h}\|^{4}}\right\}=a \mathbf{I}$, by the same principle as previous property. Applying trace to both sides leads to: $\mathbb{E}\left\{\frac{1}{\|\mathbf{h}\|^{2}}\right\}=a K$. Let
define the random variable $\mathbf{Y}=\|\mathbf{h}\|^{2}$, then $\mathbf{Y}$ follows a Chi-Square distribution with 2 K -degrees of freedom, this is $\mathbf{Y} \sim \chi^{2}(2 K)$, such that: $f_{\mathbf{Y}}(y)=\frac{1}{\Gamma(K)} y^{K-1} e^{-y}$. Then follows: $\quad \mathbb{E}\left\{\frac{1}{\mathbf{Y}}\right\}=\int_{0}^{\infty} y^{-1} f_{\mathbf{Y}}(y) d y=\frac{\Gamma(K-1)}{\Gamma(K)}=\frac{1}{K-1}$, therefore: $a=\frac{1}{K(K-1)}$, and proving the property.
- $\mathbb{E}\left\{\frac{\left|h_{k}\right|^{2} \mathbf{h h}^{H}}{\|\mathbf{h}\|^{4}}\right\}$ is also a diagonal matrix as previous properties. The values of the elements in the main diagonal can be obtained as follows: $1=\mathbb{E}\left\{\frac{\|\mathbf{h}\|^{4}}{\|\mathbf{h}\|^{4}}\right\}=K \mathbb{E}\left\{\frac{\left|h_{k}\right|^{4}}{\|\mathbf{h}\|^{4}}\right\}+ K(K-1) \mathbb{E}\left\{\frac{\left|h_{k}\right|^{2}\left|h_{i}\right|^{2}}{\|\mathbf{h}\|^{4}}\right\}$, where the next equality has been used: $\|\mathbf{h}\|^{4}=\sum_{k=1}^{K}\left|h_{k}\right|^{4}+\sum_{k=1}^{K} \sum_{i=1, i \neq k}^{K}\left|h_{k}\right|^{2}\left|h_{i}\right|^{2}$. Then deriving one of the expectations leads to the other one. Let's define the random variable $\mathbf{Z}= \frac{\|\mathbf{h}\|^{2}}{\left|h_{k}\right|^{2}}$ as: $\mathbf{Z}=1+\frac{\mathbf{Y}}{\mathbf{X}}$, where $\mathbf{X}=\left|h_{k}\right|^{2}$ and $\mathbf{Y}= \sum_{i \neq k}^{K}\left|h_{i}\right|^{2} . \mathbf{X}$ follows an exponential distribution, $f_{\mathbf{X}}(x)=e^{-x}$ and $\mathbf{Y} \sim \chi^{2}(2 K-2)$. To obtain $f_{\mathbf{Z}}(z)$, first we express $F_{Z}(z)=P(\mathbf{Z} \leq z)=P(\mathbf{Y} \leq \mathbf{X}(z- 1))=\int_{0}^{\infty} f_{\mathbf{X}}(x) \int_{0}^{x(z-1)} f_{\mathbf{Y}}(y) d y d x$. The derivative with respect to $z$ is: $f_{\mathbf{Z}}(z)=\int_{0}^{\infty} f_{\mathbf{X}}(x) f_{\mathbf{Y}}(x(z-1)) x d x= \frac{1}{\Gamma(K-1)}(z-1)^{K-2} \int_{0}^{\infty} x^{K-1} e^{-x z} d x=\frac{1}{z^{2}}\left(1-\frac{1}{z}\right)^{K-2} (K-1)$ for $z \geq 1$ and 0 otherwise, where the definition of gamma function based on improper integral has been used. Finally, $\mathbb{E}\left\{\frac{1}{\mathbf{Z}^{2}}\right\}=\int_{1}^{\infty} z^{-2} f_{\mathbf{Z}}(z) d z=\frac{2}{K(K+1)}$, proving the property.
- $\mathbb{E}\{\mathbf{Q}\}=\mathbf{I}-\mu \mathbb{E}\left\{\frac{\mathbf{h \mathbf { h } ^ { H }}}{\|\mathbf{h}\|^{2}}\right\}=\mathbf{I}-\mu \frac{1}{K}$, due to first property, where $\mu_{m}=\frac{\mu}{\left\|\mathbf{h}_{m}\right\|^{2}}$ has been used and the index $m$ in $\mathbf{Q}$ dropped for clarity.
- $\mathbb{E}\{\mathbf{A}\}=\mathbb{E}\left\{\prod_{m=1}^{M} \mathbf{Q}_{m}\right\}=\prod_{m=1}^{M} \mathbb{E} \mathbf{Q}_{m}$ due to statistical independence among antennas, then proving the property.
Proposition 5: For a matrix $\mathbf{Q}$ defined as in equation (25) and $\mu$ as in (12), the next result holds for any deterministic diagonal matrix $\mathbf{D}$

$$
\begin{equation*}
\mathbb{E}\left\{\mathbf{Q D Q}^{H}\right\}=\alpha \mathbf{D}+\beta \operatorname{Tr}(\mathbf{D}) \mathbf{I}, \tag{28}
\end{equation*}
$$

where $\alpha$ and $\beta$ are defined in Table I.
Proof: Let's define a deterministic diagonal matrix as $\mathbf{D}= \operatorname{diag}\left\{d_{1}, d_{2}, \ldots, d_{K}\right\}$ and a random matrix $\mathbf{Q}$ defined according to (25). Taking into account the properties in Table VI we can establish the following

$$
\begin{aligned}
& \mathbb{E}\left\{\mathbf{Q D Q}^{H}\right\} \\
& =\mathbb{E}\left\{\mathbf{D}-\mu \mathbf{D} \frac{\mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{2}}-\mu \frac{\mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{2}} \mathbf{D}+\mu^{2} \frac{\mathbf{h} \mathbf{h}^{H} \mathbf{D} \mathbf{h h}^{H}}{\|\mathbf{h}\|^{4}}\right\} \\
& =\mathbf{D}-2 \frac{\mu}{K} \mathbf{D}+\mu^{2} \mathbb{E}\left\{\frac{\mathbf{h} \mathbf{h}^{H} \mathbf{D} \mathbf{h h}^{H}}{\|\mathbf{h}\|^{4}}\right\},
\end{aligned}
$$

where

$$
\begin{aligned}
\mathbb{E}\left\{\frac{\mathbf{h} \mathbf{h}^{H} \mathbf{D} \mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{4}}\right\} & =\mathbb{E}\left\{\frac{\mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{4}}\left(\sum_{k=1}^{K} d_{k} \mathbf{e}_{k} \mathbf{e}_{k}^{T}\right) \mathbf{h} \mathbf{h}^{H}\right\} \\
& =\sum_{k=1}^{K} d_{k} \mathbb{E}\left\{\frac{\left|\mathbf{h}_{k}\right|^{2} \mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{4}}\right\}
\end{aligned}
$$

which can be simplified as follows taking into account properties in Table VI,

$$
\mathbb{E}\left\{\frac{\mathbf{h} \mathbf{h}^{H} \mathbf{D} \mathbf{h} \mathbf{h}^{H}}{\|\mathbf{h}\|^{4}}\right\}=\frac{1}{K(K+1)} \mathbf{D}+\frac{T r(\mathbf{D})}{K(K+1)} \mathbf{I},
$$

proving the proposition. $\square$

This proposition leads to a more general one.
Proposition 6: For a matrix $\mathbf{A}_{m}$ defined as in equation (26) the next result holds for any deterministic diagonal matrix $\mathbf{D}$

$$
\begin{equation*}
\mathbb{E}\left\{\mathbf{A}_{m} \mathbf{D} \mathbf{A}_{m}^{H}\right\}=\alpha^{m}\left[\mathbf{D}-\mathbf{D}_{a}\right]+\epsilon^{m} \mathbf{D}_{a}, \tag{29}
\end{equation*}
$$

where $\mathbf{D}_{a}=\frac{\operatorname{Tr}(\mathbf{D})}{K} \mathbf{I}$, and for the particular case of $\mathbf{D}=\mathbf{I}$ it reduces to $\mathbb{E}\left\{\mathbf{A}_{m} \mathbf{A}_{m}^{H}\right\}=\epsilon^{m} \mathbf{I}$, and for $\mathbf{D}=\mathbf{e}_{k}^{T} \mathbf{e}_{k}$ the following result applies

$$
\mathbf{e}_{k}^{T} \mathbb{E}\left\{\mathbf{A}_{m} \mathbf{e}_{k} \mathbf{e}_{k}^{T} \mathbf{A}_{m}^{H}\right\} \mathbf{e}_{k}=\alpha^{m}\left(1-\frac{1}{K}\right)+\epsilon^{m} \frac{1}{K} .
$$

Proof: Let's define a sequence of diagonal matrices $\left\{\mathbf{D}_{m}\right\}_{m=0, \ldots, M}$, which can be defined recursively as

$$
\mathbf{D}_{m}= \begin{cases}\mathbb{E}\left\{\mathbf{Q}_{m} \mathbf{D}_{m-1} \mathbf{Q}_{m}^{H}\right\} & \text { if } m>0 \\ \mathbf{D} & \text { if } m=0\end{cases}
$$

where $\mathbf{Q}$ is a matrix defined according to (25). From proposition 5 we know that

$$
\mathbf{D}_{m}=\alpha \mathbf{D}_{m-1}+\beta \operatorname{Tr}\left(\mathbf{D}_{m-1}\right) \mathbf{I},
$$

and therefore $\operatorname{Tr}\left(\mathbf{D}_{m}\right)=\epsilon \operatorname{Tr}\left(\mathbf{D}_{m-1}\right)$, following that $\operatorname{Tr}\left(\mathbf{D}_{m}\right)=\epsilon^{m} \operatorname{Tr}\left(\mathbf{D}_{0}\right)$,
which leads to

$$
\begin{aligned}
\mathbf{D}_{m} & =\alpha \mathbf{D}_{m-1}+\operatorname{Tr}\left(\mathbf{D}_{0}\right) \beta \epsilon^{m-1} \mathbf{I} \\
& =\alpha^{m} \mathbf{D}_{0}+\operatorname{Tr}\left(\mathbf{D}_{0}\right) \beta \epsilon^{m-1} \sum_{i=0}^{m-1} r^{i} \mathbf{I},
\end{aligned}
$$

for $m>0$, where $r=\frac{\alpha}{\epsilon}<1$, and finally taking into account that $\mathbf{D}_{m}=\mathbb{E}\left\{\mathbf{A}_{m} \mathbf{D}_{0} \mathbf{A}_{m}^{H}\right\}$ the proposition is proved. $\square$

## A. Proof of Proposition 1

We prove the proposition by derivation of analytical expressions for $\mathbb{E}\left|E_{k, k}\right|^{2}$ and $\mathbb{E}\left\{\sum_{i=1, i \neq k}^{K}\left|E_{k, i}\right|^{2}\right\}$. From the properties shown in Table VI, $\mathbb{E}\left|E_{k, k}\right|^{2}$ is expressed as

$$
\begin{align*}
& \mathbb{E}\left|E_{k, k}\right|^{2}=\mathbb{E}\left|\mathbf{e}_{k}^{T} \mathbf{E}_{\mathrm{u}} \mathbf{e}_{k}\right|^{2} \\
& =1-\mathbf{e}_{k}^{T} \mathbb{E}\{\mathbf{A}\} \mathbf{e}_{k}-\mathbf{e}_{k}^{T} \mathbb{E}\left\{\mathbf{A}^{H}\right\} \mathbf{e}_{k}+\mathbf{e}_{k}^{T} \mathbb{E}\left\{\mathbf{A} \mathbf{e}_{k} \mathbf{e}_{k}^{T} \mathbf{A}^{H}\right\} \mathbf{e}_{k} \\
& =1-2 \nu^{M}+\alpha^{M}\left(1-\frac{1}{K}\right)+\epsilon^{M} \frac{1}{K} \tag{30}
\end{align*}
$$

and for the IUI term

$$
\begin{align*}
& \mathbb{E}\left\{\sum_{i=1, i \neq k}^{K}\left|E_{k, i}\right|^{2}\right\}=\mathbb{E}\left\|\mathbf{e}_{k}^{T} \mathbf{E}_{\mathrm{u}}\right\|^{2}-\mathbb{E}\left|E_{k, k}\right|^{2} \\
& \quad=\mathbf{e}_{k}^{T} \mathbb{E}\left\{\mathbf{A} \mathbf{A}^{H}\right\} \mathbf{e}_{k}-\mathbf{e}_{k}^{T} \mathbb{E}\left\{\mathbf{A} \mathbf{e}_{k} \mathbf{e}_{k}^{T} \mathbf{A}^{H}\right\} \mathbf{e}_{k} \\
& \quad=\left(1-\frac{1}{K}\right) \cdot\left(\epsilon^{M}-\alpha^{M}\right), \tag{31}
\end{align*}
$$

which proves the first part of the proposition.
In the limit when $M \rightarrow \infty$, if the ratio $\frac{M}{K}$ is kept constant, then $\epsilon^{M} \rightarrow e^{-\mu(2-\mu) \frac{M}{K}}$. Similarly, for $\alpha$ we have $\alpha^{M} \rightarrow e^{-2 \mu \frac{M}{K}}$
under same conditions. Given that, we have that $\epsilon^{M}-\alpha^{M} \rightarrow e^{-2 \mu \frac{M}{K}}\left[e^{\mu^{2} \frac{M}{K}}-1\right]$. If we assume $\frac{M}{K}$ is large enough, such that $\mu^{2} \frac{M}{K} \gg 0$, then 1 is negligible in the second term (within brackets), and therefore $\left(1-\frac{1}{K}\right)\left(\epsilon^{M}-\alpha^{M}\right) \rightarrow e^{-\mu(2-\mu) \frac{M}{K}}$. In the numerator, assuming $\mu \frac{M}{K} \gg 0$, then $1-2 \nu^{M}+\alpha^{M}(1- \left.\frac{1}{K}\right)+\epsilon^{M} \frac{1}{K} \rightarrow 1$ when $M \rightarrow \infty$ and $\frac{M}{K}$ kept constant. Then, under previous assumptions regarding the ratio $\frac{M}{K}$, SIR → $e^{\mu(2-\mu) \frac{M}{K}}$ when $M \rightarrow \infty$. Based on this limit, we can establish the following approximation: SIR $\approx e^{\mu(2-\mu) \frac{M}{K}}=\mathrm{SIRa}$ for large values of $M$. To give an idea of the validity of this approximation, we give some numerical values. For example, for $M=128, K=16$ and $\mu=1$ leads to $\operatorname{SIR}(\mathrm{dB})=36.2 \mathrm{~dB}$, while $\operatorname{SIRa}(\mathrm{dB})=34.7 \mathrm{~dB}$, resulting in a relative error of $4 \%$. For $M=256, K=32$ and $\mu=1$, leads to an error of $2 \%$, while the error goes down to $1 \%$ for $M=512$ and $K=64$, approaching 0 in the limit, and proving the second part of the proposition.

## B. Proof of Proposition 2

The proof of the proposition is based on the corresponding proof to SIR expression (Appendix-A). The noise term, $\mathbb{E}\left|z_{k}\right|^{2}$, is the only term which has not been analyzed in the proof of Proposition A. This term can be computed as

$$
\begin{equation*}
\mathbb{E}\left|z_{k}\right|^{2}=N_{0} \mathbf{e}_{k}^{T} \sum_{m=1}^{M} \mathbb{E}\left\{\mathbf{w}_{m} \mathbf{w}_{m}^{H}\right\} \mathbf{e}_{k} . \tag{32}
\end{equation*}
$$

Recalling that $\mathbf{w}_{m}=\mu \mathbf{A}_{m-1} \frac{\mathbf{h}_{m}}{\left\|\mathbf{h}_{m}\right\|^{2}}$ and taking into account properties in Table VI, (32) can continue as

$$
\begin{align*}
\mathbb{E}\left|z_{k}\right|^{2} & =\frac{\mu^{2} N_{0}}{K(K-1)} \mathbf{e}_{k}^{T} \sum_{m=1}^{M} \mathbb{E}\left\{\mathbf{A}_{m-1} \mathbf{A}_{m-1}^{H}\right\} \mathbf{e}_{k} \\
& =\frac{N_{0}}{K-1} \cdot\left(\frac{\mu}{2-\mu}\right) \cdot\left(1-\epsilon^{M}\right) \tag{33}
\end{align*}
$$

where Proposition 6 has been used, and shows that the postprocessing noise power per user does not depend on $M$. This result, together with (17) and Proposition 1 leads to the final expression shown in (20), and proving the first part of the proposition.

In the limit, $\mathbb{E}\left|z_{k}\right|^{2} \rightarrow \frac{N_{0}}{K-1} \cdot \frac{\mu}{2-\mu}$ when $M \rightarrow \infty$. Based on this result, we can establish an approximation, similarly to the proof of Appendix-A, consisting of: $\mathbb{E}\left|z_{k}\right|^{2} \approx \frac{N_{0}}{K-1} \cdot \frac{\mu}{2-\mu}$ for large values of $M$. As an example of the validity of this approximation, let's consider a Massive MIMO scenario such as: $M=128, K=16, \mu=0.4$, and $N_{0}=1$. This leads to a relative error of $0.13 \%$ for magnitudes in dB . This approximation, together with the one in Proposition 1, provides (21). To check the validity for this approximation, for the same scenario as before, (20) and (21) provide 16.60 dB and 16.66 dB respectively, which leads to a relative error of $0.36 \%$. This completes the proof of current proposition.

## C. Proof of Proposition 3

If (21) is denoted as $\widetilde{\text { SINR }}$, then maximizing this value is equivalent to minimizing the inverse value, whose derivative is

$$
\frac{\partial \widetilde{\mathrm{SINR}}^{-1}}{\partial \mu}=-2(1-\mu) \frac{M}{K} e^{-\mu(2-\mu) \frac{M}{K}}+\frac{1}{K \cdot S N R} \frac{2}{(2-\mu)^{2}}
$$

and by setting to 0 leads to an expression which does not have closed form. However, which can be further simplified as: $4 M$. $\mathrm{SNR}=e^{2 \mu \frac{M}{K}}$, leading to (22) and proving the proposition.

## D. Proof of Proposition 4

From (32) and (33) we can derive the exact expression as

$$
\begin{align*}
\mathbb{E}\|\mathbf{W}\|_{F}^{2} & =\operatorname{Tr} \mathbb{E}\left\{\mathbf{W}^{H} \mathbf{W}\right\} \\
& =\frac{K}{K-1} \cdot \frac{\mu}{2-\mu} \cdot\left(1-\epsilon^{M}\right), \tag{34}
\end{align*}
$$

proving the proposition.

## References

[1] J. R. Sanchez, F. Rusek, M. Sarajlic, O. Edfors, and L. Liu, "Fully decentralized massive MIMO detection based on recursive methods," in Proc. IEEE Int. Workshop Signal Process. Syst., Oct. 2018, pp. 53-58.
[2] M. Sarajlic, F. Rusek, J. R. Sanchez, L. Liu, and O. Edfors, "Fully decentralized approximate zero-forcing precoding for massive MIMO systems," IEEE Wireless Commun. Letters, vol. 8, no. 3, pp. 773-776, Jun. 2019.
[3] T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Trans. Wireless Commun., vol. 9, no. 11, pp. 3590-3600, Nov. 2010.
[4] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays," IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40-60, Jan. 2013.
[5] S. Malkowsky et al., "The world's first real-time testbed for massive MIMO: Design, implementation, and validation," IEEE Access, vol. 5, pp. 9073-9088, 2017.
[6] J. Vieira et al., "A flexible 100-antenna testbed for massive mimo," in Proc. IEEE Globecom Workshops, Dec. 2014, pp. 287-293.
[7] "Common public radio interface: eCPRI interface specification," 2018. [Online]. Available: http://www.cpri.info/
[8] C. Shepard et al., "Argos: Practical many-antenna base stations," in Proc. 18th Annu. Int. Cofn. Mobile Comput. Netw., New York, NY, USA, 2012, pp. 53-64. [Online]. Available: http://doi.acm.org/10.1145/ 2348543.2348553
[9] E. Bertilsson, O. Gustafsson, and E. G. Larsson, "A scalable architecture for massive MIMO base stations using distributed processing," in Proc. 50th Asilomar Conf. Signals, Syst. Comput., Nov. 2016, pp. 864-868.
[10] A. Puglielli et al., "A scalable massive MIMO array architecture based on common modules," in Proc. IEEE Int. Conf. Commun. Workshop, Jun. 2015, pp. 1310-1315.
[11] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[12] K. Li, C. Jeon, J. R. Cavallaro, and C. Studer, "Feedforward architectures for decentralized precoding in massive MU-MIMO Systems," in Proc. 52nd Asilomar Conf. Signals, Syst., Comput., Oct. 2018, pp. 1659-1665.
[13] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
[14] K. Li, O. Castaeda, C. Jeon, J. R. Cavallaro, and C. Studer, "Decentralized coordinate-descent data detection and precoding for massive mu-MIMO," in Proc. IEEE Int. Symp. Circuits Syst., May 2019, pp. 1-5.
[15] J. Vieira, F. Rusek, O. Edfors, S. Malkowsky, L. Liu, and F. Tufvesson, "Reciprocity calibration for massive MIMO: Proposal, modeling, and validation," IEEE Trans. Wireless Commun., vol. 16, no. 5, pp. 3042-3056, May 2017.
[16] S. Zhou, M. Zhao, X. Xu, J. Wang, and Y. Yao, "Distributed wireless communication system: A new architecture for future public wireless access," IEEE Commun. Mag., vol. 41, no. 3, pp. 108-113, Mar. 2003.
[17] H. Q. Ngo, A. Ashikhmin, H. Yang, E. G. Larsson, and T. L. Marzetta, "Cell-free massive MIMO versus small cells," IEEE Trans. Wireless Commun., vol. 16, no. 3, pp. 1834-1850, Mar. 2017.
[18] S. Hu, F. Rusek, and O. Edfors, "Beyond massive MIMO: The potential of data transmission with large intelligent surfaces," IEEE Trans. Signal Process., vol. 66, no. 10, pp. 2746-2758, May 2018.
[19] S. Kaczmarz, "Angenaherte auflosung von systemen linearer gleichungen," 1937.
[20] Y. Censor, "Row-action methods for huge and sparse systems and their applications," SIAM Rev., vol. 23, no. 4, pp. 444-466, 1981. [Online]. Available: https://doi.org/10.1137/1023097
![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-14.jpg?height=325&width=265&top_left_y=597&top_left_x=1052)

Jesús Rodríguez Sánchez (Student Member, IEEE) received the bachelor's degree in telecommunication engineering and the master's degree in telecommunication technologies from the University of Málaga, Málaga, Spain, in 2007 and 2009, respectively. He is currently working toward the Ph.D. degree with the Department of Electrical and Information Technology (EIT), Lund University, Lund, Sweden. He has worked for more than ten years in the industry as a Physical Layer Engineer and RTL Designer, focused on diverse communication standards. His research interests include communication systems, distributed processing, low-complexity algorithms for efficient implementation, and performance-complexity trade-offs.
![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-14.jpg?height=324&width=265&top_left_y=1041&top_left_x=1052)

Fredrik Rusek (Member, IEEE) was born in Lund, Sweden, in 1978. He received the M.S. and Ph.D. degrees in electrical engineering from Lund University, Lund, Sweden, in 2003 and 2007, respectively. Since 2012, he has been an Associate Professor with the Department of Electrical and Information Technology, Lund Institute of Technology, Lund. His research interests include modulation theory, equalization, wireless communications, and applied information theory.
![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-14.jpg?height=321&width=261&top_left_y=1396&top_left_x=1054)

Ove Edfors (Senior Member, IEEE) is currently a Professor of radio systems with the Department of Electrical and Information Technology, Lund University, Lund, Sweden. His current research interests include statistical signal processing and lowcomplexity algorithms with applications in wireless communications. In the context of massive MIMO, his main research focus is on how realistic propagation characteristics influence system performance and baseband processing complexity.
![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-14.jpg?height=321&width=263&top_left_y=1748&top_left_x=1054)

Muris Sarajlić received the B.Eng. degree in electrical engineering from the University of Tuzla, Tuzla, Bosnia and Herzegovina, in 2010, the M.Sc. degree in wireless communications from Lund University, Lund, Sweden, in 2013, and the Ph.D. degree in electrical engineering from the Department of Electrical and Information Technology, Lund University. His research interests include energy efficiency and complexity aspects of hardware-constrained wireless communication systems.
![](https://cdn.mathpix.com/cropped/971a5e2d-015f-41ec-9e4d-bbb71eb4bcca-14.jpg?height=321&width=263&top_left_y=2096&top_left_x=1054)

Liang Liu (Member, IEEE) received the B.S. degree from the Department of Electronics Engineering, Fudan University, Shanghai, China, in 2005, and the Ph.D. degree from the Department of Microelectronics, Fudan University, in 2010. In 2010, he was with the Rensselaer Polytechnic Institute, USA, as a Visiting Researcher. He joined the Department of Electrical and Information Technology (EIT), Lund University, Lund, Sweden, where he held a postdoctoral position in 2010. Since 2016, he has been an Associate Professor with the Department of EIT, Lund University. His current research interests include wireless communication system, computer vision, and digital integrated circuits design. He is a Board Member of the IEEE Swedish SSC/CAS Chapter. He is also a member of the Technical Committee of VLSI systems and applications and CAS for communications of the IEEE Circuit and Systems Society.


[^0]:    Manuscript received May 7, 2019; revised October 11, 2019 and December 19, 2019; accepted December 21, 2019. Date of publication January 15, 2020; date of current version January 28, 2020. The associate editor coordinating the review of this manuscript and approving it for publication was Dr. Bruno Clerckx. This article was presented in part at IEEE International Workshop on Signal Processing Systems, Cape Town, South Africa. October 21-24, 2018. This work was supported by ELLIIT, the Excellence Center at Linköping-Lund in Information Technlology. (Corresponding author: Jesús Rodríguez Sánchez.)

    The authors are with the Electrical and Information Technology, Lund University, 22363 Lund, Sweden (e-mail: jesus.rodriguez@eit.lth.se; fredrik.rusek@eit.lth.se; ove.edfors@eit.lth.se; muris.sarajlic@eit.lth.se; liang. liu@eit.lth.se).

    Digital Object Identifier 10.1109/TSP.2020.2964496

[^1]:    ${ }^{1}$ If prior information of $\mathbf{x}$ is available, it can be used here.

[^2]:    ${ }^{2}$ The selection of Coordinate Descent as our method's name is because we consider the vectors $\left\{\mathbf{w}_{i}\right\}$ as the outcome of the method, and these can be seen as coordinates of a cost function to minimize. Such optimization problem can be written as: $\mathbf{w}_{m}=\arg \min _{z} f\left(\mathbf{w}_{1}, \ldots, \mathbf{w}_{m-1}, \mathbf{z}, \mathbf{w}_{m+1}, \ldots, \mathbf{w}_{M}\right)$, where $f=\left\|\mathbf{A}_{m-1}-\mathbf{z} \mathbf{h}_{m}^{H}\right\|_{F}^{2}$, and $\mathbf{A}_{m-1}=\mathbf{I}_{K}-\sum_{i \neq m} \mathbf{w}_{i} \mathbf{h}_{i}^{H}$. Each antenna solves this optimization problem in a sequential fashion, obtaining one coordinate as a result, while keeping the rest fixed. This is valid for single and multiple iterations to the array, which is presented in the next subsection.

