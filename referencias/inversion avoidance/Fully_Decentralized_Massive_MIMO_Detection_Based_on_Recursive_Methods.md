# Fully Decentralized Massive MIMO Detection Based on Recursive Methods 

Jesús Rodríguez Sánchez, Fredrik Rusek, Muris Sarajlić, Ove Edfors and Liang Liu<br>Department of Electrical and Information Technology, Lund University, Sweden<br>\{jesus.rodriguez, fredrik.rusek, muris.sarajlic, ove.edfors, liang.liu\}@eit.lth.se


#### Abstract

Algorithms for Massive MIMO uplink detection typically rely on a centralized approach, by which baseband data from all antennas modules are routed to a central node in order to be processed. In case of Massive MIMO, where hundreds or thousands of antennas are expected in the base-station, this architecture leads to a bottleneck, with critical limitations in terms of interconnection bandwidth requirements. This paper presents a fully decentralized architecture and algorithms for Massive MIMO uplink based on recursive methods, which do not require a central node for the detection process. Through a recursive approach and very low complexity operations, the proposed algorithms provide a sequence of estimates that converge asymptotically to the zero-forcing solution, without the need of specific hardware for matrix inversion. The proposed solution achieves significantly lower interconnection data-rate than other architectures, enabling future scalability.


Index Terms-Massive MIMO, Stochastic Approximation, Gradient Descent, Recursive Least Squares, Decentralized, Detection and zero-forcing

## I. Introduction

Massive multi-user (MU) multiple-input multiple-output (MIMO) is one of the most promising technologies in the wireless area [1]. High spectral efficiency and improved link reliability are among the key features of this technology, making it a key enabler to exploit spatial diversity far beyond traditional MIMO systems by employing a large scale antenna array with hundreds or thousands of elements. This allows for unprecedented spatial resolution and high spectral efficiency, while providing simultaneous service to several users within the same time-frequency resource.

Despite all advantages of Massive MIMO, there are challenges from an implementation point of view. Uplink detection algorithms like zero-forcing (ZF) typically rely on a centralized architecture, shown in Figure 1a, where baseband samples and channel state information (CSI) are collected in the central node for further matrix inversion and detection. Dedicated links are needed between antenna modules and central node to carry this data. This approach, that is perfectly valid for a relatively low number of antennas, shows critical limitations when the array size increases, with interconnection bandwidth quickly becoming a bottleneck in the system.

Previous work has been done proposing different architectures for Massive MIMO base-stations [2]-[6]. All of them conclude by pointing to the interconnection bandwidth as the main implementation bottleneck and a limiting factor for array scalability. Most of them recommend moving to a
decentralized approach where uplink detection and downlink precoding can be performed locally in processing nodes close to the antennas. However, to achieve that, CSI still needs to be collected in a central node, where matrix inversion is done and the result distributed back to all modules [2], [3], [5]. A further step has been made in [6], where CSI is obtained and used only locally (not shared) for precoding and detection. This architecture relies on a central node only for processing partial results. This dependency on a central node limits the scalability of this solution as will be shown in section IV.

In this paper we propose a fully decentralized architecture and recursive algorithms for Massive MIMO uplink detection. Antennas in the array are grouped into clusters. Apart from antennas, clusters contain RF, Analog-to-Digital Converters (ADC), OFDM receiver, channel estimation and detection blocks. The decentralized topology is based on the direct connection of clusters forming a daisy-chain structure as shown in Figure 1b. The proposed algorithms are pipelined so that they run in a distributed way at the cluster nodes, providing a sequence of estimates that converge asymptotically to the zero-forcing solution. We will make use of the following algorithms: Recursive Least Square (RLS), Stochastic Gradient Descent (SGD) and Averaged Stochastic Gradient Descent (ASGD), which are detailed in section III.

Decentralized architectures overcome bottlenecks by finding a more equal distribution of the system requirements among the processing nodes of the system. Apart from this, data localization is a key characteristic of decentralized architectures. This architecture allows data to be consumed as close as possible to where it is generated, minimizing the amount to transfer, and therefore saving bandwidth and energy. Following this idea, processing nodes need to be located near the antenna. Further, they perform tasks such as channel estimation and detection locally. Local CSI is estimated and stored locally in each, without any need to share it with any other nodes in the system.

The remainder of the paper is organized as follows. The system model for MIMO uplink is presented in section II. In section III we introduce the proposed algorithms. In IV we analyze the performance of these algorithms, present the advantages of the daisy-chain topology, and analyze interconnection data-rates. Finally, section V presents the conclusions of this publication.

Notation: In this paper, lowercase, bold lowercase and

![](https://cdn.mathpix.com/cropped/4cb60caf-d806-4796-a4fe-e8e77d7fe26a-2.jpg?height=774&width=1475&top_left_y=210&top_left_x=324)
Fig. 1. Comparison between base station receiver chain in centralized and fully decentralized architectures for Massive MIMO uplink. Antenna array with M elements is divided into C clusters, each containing B antennas. (a): Centralized architecture. Clusters contain RF amplifiers and frequency down-conversion (RF) elements, analog-to-digital converters (ADC) and OFDM receivers. Each cluster has one link to transfer baseband samples to a central baseband processing node, where the rest of processing tasks are done. (b): Fully decentralized architecture for detection. Clusters performs RF, ADC, OFDM, channel estimation (CHEST) and detection (DET) locally. Decoding (DEC) is centralized. Clusters are connected to each other by uni-directional links. Only one cluster has a direct connection with central node. Proposed algorithms are executed in DET blocks in parallel mode. The points where the interconnection data-rate is estimated are marked by circles and the value is denoted by $R$.

upper bold face letters stand for scalar, column vector and matrix, respectively. The operations (.)T , (.)* and (.) ${ }^{H}$ denote transpose, conjugate and conjugate transpose respectively. The vector $\mathbf{s}$ in the $n$th iteration is $\mathbf{s}_{n}$. Computational complexity is measured in terms of the number of complex-valued multiplications.

## II. System model and detection algorithms

In this section we present the system model for MIMO uplink and introduce the ZF equalizer.

We consider a scenario with $K$ single-antenna users transmitting to an antenna array with $M$ elements. The input-output relation for uplink is

$$
\begin{equation*}
\mathbf{y}=\mathbf{H} \mathbf{s}+\mathbf{v}, \tag{1}
\end{equation*}
$$

where $\mathbf{y}$ is the $M \times 1$ received vector, $\mathbf{s}$ is the transmitted user data vector $(K \times 1), \mathbf{H}=\left[\begin{array}{llll}\mathbf{h}_{1} & \mathbf{h}_{2} & \cdots & \mathbf{h}_{M}\end{array}\right]^{T}$ is the channel matrix ( $M \times K$ ) and $\mathbf{v}$ samples of noise ( $M \times 1$ ). Under the Massive MIMO assumption, $M \gg K$.

Assuming time-frequency-based channel access, a Resource Element (RE) represents a slot in the time-frequency grid. Within each RE, the channel model follows (1).

A least-squares (LS) estimate of $\mathbf{s}$ is obtained as

$$
\begin{equation*}
\hat{\mathbf{s}}_{\mathrm{ZF}}=\left(\mathbf{H}^{H} \mathbf{H}\right)^{-1} \mathbf{H}^{H} \mathbf{y} . \tag{2}
\end{equation*}
$$

This method, commonly referred to as ZF , requires a central architecture as in Figure 1a because the complete matrix $\mathbf{H}$ needs to be collected in the central node before the Gramian
matrix ( $\mathbf{H}^{H} \mathbf{H}$ ) and its inverse can be computed. Decentralized architectures, such as the one shown in Figure 1b, require other type of algorithms.

## III. Proposed Algorithms

In this section we propose three algorithms for MIMO decentralized uplink detection.

Depending on the situation some algorithms are more appropriate than others. If full knowledge of matrix $\mathbf{H}$ and $\mathbf{y}$ is available at a single node, direct methods such as ZF can be applied (2). However, there are situations when the cost of collecting all knowledge at a single node is too high. For those cases, a different approach has to be used.

The goal of the proposed algorithms for uplink detection is the estimation of the transmitted user data vector, $\mathbf{s}$ in (1), based on knowledge of $\mathbf{H}$ and $\mathbf{y}$ that is distributed among nodes. These algorithms provide a sequence of estimates, which converge to $\hat{\mathbf{s}}_{Z F}$ as more knowledge of $\mathbf{H}$ and $\mathbf{y}$ is obtained. Estimation is done in a sequential manner, by which the estimate is passed from one antenna to the next one, being updated every time based on the previous estimate $\left(\hat{\mathbf{s}}_{n-1}\right)$, local CSI ( $\mathbf{h}_{n}$ ) and antenna observation ( $y_{n}$ ). This can be summarized as $\hat{\mathbf{s}}_{n}=f\left(\hat{\mathbf{s}}_{n-1}, \mathbf{h}_{n}, y_{n}\right)$, which can be seen as a recursive form. This approach is in accordance with the data localization principle, which is a key characteristic of decentralized systems. In the Massive MIMO case, data is consumed close to where it is generated, namely at the antennas. This makes it possible that neither $\mathbf{h}_{n}$ nor $y_{n}$ are shared, since only the estimate is.

These algorithms are flexible enough to work in clusters of antennas (see Figure 1b), whose size can vary from 1 up to $M$, the last case being equivalent to a centralized system.

The first recursive algorithm to be presented is the Recursive Least Square (RLS) method, which is a recursive form of (2). Uplink detection can be also seen as a regression parameter estimation - a problem well studied in the area of stochastic approximation methods. Stochastic Gradient Descent (SGD) and its averaged version (ASGD) fall within this group, and are based on a Gradient Descent algorithm in which the gradient is partially known.

In Section III-A we present RLS applied to MIMO uplink detection, which provides approximate ZF performance at the expense of a preprocessing stage. Afterwards, we present the SGD algorithm and its enhanced version, the Averaged SGD (ASGD), which increases robustness of SGD while achieving performance close to ZF for very large arrays.

Before we describe the algorithms we clarify the role played by the variable $B$, i.e., the number of antennas per cluster. Our algorithms are in fact independent of the value of $B$, therefore we present them with notation tailored to the choice $B=1$. However, $B>1$ is still of importance from an implementation point of view since each cluster may be implemented with a single processing unit. Thus, with $M=100$ antennas, the choice $B=1$ requires 100 processing units, while $B=10$ merely requires 10 such units. Nevertheless, performance of our algorithms remains the same. $B$ therefore takes a trade-off role: The larger the $B$, the less number of processing units, but meanwhile, the architecture becomes more centralized.

## A. Recursive Least-Squares (RLS)

RLS is the recursive version of the LS algorithm. It can be shown [7] that the $\mathrm{ZF} / \mathrm{LS}$ estimate, i.e., the l.h.s. of (2), can be approximated by the RLS as $\hat{\mathbf{s}}_{\mathrm{ZF}} \approx \hat{\mathbf{s}}_{M}$ where $\hat{\mathbf{s}}_{n}$ is recursively found as follows

$$
\begin{align*}
\varepsilon_{n} & =y_{n}-\mathbf{h}_{n}^{T} \hat{\mathbf{s}}_{n-1} \\
\boldsymbol{\Gamma}_{n} & =\boldsymbol{\Gamma}_{n-1}-\frac{\boldsymbol{\Gamma}_{n-1} \mathbf{h}_{n}^{*} \mathbf{h}_{n}^{T} \boldsymbol{\Gamma}_{n-1}}{1+\mathbf{h}_{n}^{T} \boldsymbol{\Gamma}_{n-1} \mathbf{h}_{n}^{*}}  \tag{3}\\
\hat{\mathbf{s}}_{n} & =\hat{\mathbf{s}}_{n-1}+\boldsymbol{\Gamma}_{n} \mathbf{h}_{n}^{*} \varepsilon_{n}
\end{align*}
$$

The quality of the approximation depends on the initial value of $\hat{\mathbf{s}}_{0}$. Nevertheless, for a randomly chosen $\hat{\mathbf{s}}_{0}$, the impact of $\hat{\mathbf{s}}_{0}$ quickly fades out over the index $n$ and it can be shown that $s_{M} \rightarrow \hat{\mathbf{s}}_{\mathrm{ZF}}$ as $M \rightarrow \infty$ with probability one. In (3), $\hat{\mathbf{s}}_{n}$ is a $K \times 1$ vector and is the output of cluster $n, y_{n}$ is the observation at the $n$th antenna, $\varepsilon_{n}$ is the prediction error and $\boldsymbol{\Gamma}_{n}$ is a $K \times K$ matrix. As a side comment, we remark that $\hat{\mathbf{s}}_{n}$ is an approximate LS solution up to the $n$th antenna element.

In view of Figure 1b, increasing the iteration number in (3) from $n$ to $n+1$ corresponds to passing on information from cluster $n$ to cluster $n+1$. Each cluster receives an estimate of the transmitted data vector from previous cluster, $\hat{\mathbf{s}}_{n-1}$, and compute a new estimate $\hat{\mathbf{s}}_{n}$ based on local CSI, $\mathbf{h}_{n}$, and a local observation, $y_{n}$.

Under the block fading channel model, multiple Resource Elements (RE) in a certain region of the time-frequency grid
experience identical channels. We name this region Coherence Block (CB), and following this model it is possible to re-use same CSI for all REs in the same CB.

Straightforward implementation of (3) at every RE is not efficient. In fact, a hefty share of the operations associated to (3) can be reused within the CB , namely those associated to computation of $\boldsymbol{\Gamma}_{n}$. Defining $\boldsymbol{\Gamma}_{0}=\mathbf{I}_{K}$ and

$$
\begin{aligned}
\mathbf{z}_{n} & =\boldsymbol{\Gamma}_{n-1} \mathbf{h}_{n}^{*} \\
\alpha_{n} & =\frac{1}{1+\mathbf{h}_{n}^{T} \mathbf{z}_{n}} \\
\boldsymbol{\Gamma}_{n} & =\boldsymbol{\Gamma}_{n-1}-\alpha_{n} \mathbf{z}_{n} \mathbf{z}_{n}^{H}, \quad n=1,2, \ldots, M
\end{aligned}
$$

we see that at each RE it suffices to compute

$$
\begin{aligned}
& \varepsilon_{n}=y_{n}-\mathbf{h}_{n}^{T} \hat{\mathbf{s}}_{n-1} \\
& \hat{\mathbf{s}}_{n}=\hat{\mathbf{s}}_{n-1}+\alpha_{n} \mathbf{z}_{n} \varepsilon_{n}, \quad n=1,2, \ldots, M
\end{aligned}
$$

in order to execute (3). It is easily verifiable that the complexity of preprocessing is $\mathcal{O}\left(K^{2}\right)$, whilst the complexity is $\mathcal{O}(K)$ at every RE.

## B. Stochastic Gradient Descent (SGD)

The setup in SGD [8] is that one intends to solve the unconstrained LS problem

$$
\begin{equation*}
\min _{\mathbf{s}}\|\mathbf{y}-\mathbf{H s}\|^{2} \tag{4}
\end{equation*}
$$

via a gradient descent (GD) approach. The gradient of (4) equals $\nabla_{\mathbf{s}}=\mathbf{H}^{H} \mathbf{H s}-\mathbf{H}^{H} \mathbf{y}$. An immediate consequence is that GD is only feasible in a centralized approach.

SGD is an approximate version that can be operated in a decentralized architecture. It does so by computing, at each cluster, as much as possible of $\nabla_{\mathbf{s}}$ with the information available at the cluster. Then the cluster updates the estimate $\hat{\mathbf{s}}$ using a scaled version of the "local" gradient and passes the updated estimate on to the next cluster.

The above described procedure can, formally, be stated as

$$
\begin{align*}
& \varepsilon_{n}=y_{n}-\mathbf{h}_{n}^{T} \hat{\mathbf{s}}_{n-1}  \tag{5}\\
& \hat{\mathbf{s}}_{n}=\hat{\mathbf{s}}_{n-1}+\mu_{n} \mathbf{h}_{n}^{*} \varepsilon_{n}
\end{align*}
$$

where $\left\{\mu_{n}\right\}$ is a sequence of scalar step-sizes.

## C. Averaged Stochastic Gradient Descent (ASGD)

Selection of optimum values $\mu_{n}$ in SGD is not trivial. Even though we take $\mu_{n}=\mu$ for simplification, the optimum value will depend on $M, K$ and channel properties, where the latter may be unknown in many cases. An inappropriate selection of $\mu$ can lead to severe performance degradation depending on the scenario. Averaging a SGD sequence provides an asymptotically optimal convergence rate provided that the noise $\mathbf{v}$ is Gaussian [9], which increases robustness to the step-size selection. In the ASGD algorithm there are three sequences defined as follows

$$
\begin{align*}
& \varepsilon_{n}=y_{n}-\mathbf{h}_{n}^{T} \hat{\mathbf{x}}_{n-1} \\
& \hat{\mathbf{x}}_{n}=\hat{\mathbf{x}}_{n-1}+\mu_{n} \mathbf{h}_{n}^{*} \varepsilon_{n} \\
& \hat{\mathbf{s}}_{n}= \begin{cases}\hat{\mathbf{x}}_{n} & \text { if } n<n_{0} \\
\frac{1}{n-n_{0}+1} \sum_{k=n_{0}}^{n} \hat{\mathbf{x}}_{k} & \text { if } n \geq n_{0},\end{cases} \tag{6}
\end{align*}
$$

where $\hat{\mathbf{x}}_{n}$ takes the role of the SGD output $\hat{\mathbf{s}}_{n}$ in (5). The ASGD output $\hat{\mathbf{s}}_{n}$ thereby becomes an averaged SGD sequence, where $n_{0}$ determines the onset of the averaging procedure.

The averaged sequence can be written more conveniently as

$$
\hat{\mathbf{s}}_{n}= \begin{cases}\hat{\mathbf{x}}_{n} & \text { if } n<n_{0}  \tag{7}\\ \hat{\mathbf{s}}_{n-1}+\frac{1}{n^{\prime}}\left(\hat{\mathbf{x}}_{n}-\hat{\mathbf{s}}_{n-1}\right) & \text { if } n \geq n_{0},\end{cases}
$$

where $n^{\prime}=n-n_{0}+1$. As will be seen in our numerical results, the ASGD grossly relaxes the need for careful selection of $\mu$.

## IV. Analysis

In this section we analyze the proposed solution. First, the performance of the presented algorithms will be shown and compared with each other. Second, a few strong points of the daisy-chain topology are given. Finally, an analysis of interconnection bandwidth is presented, followed by a comparison for four different configurations.

## A. Detection Performance

In this section, we present performance results for all algorithms. Reported metrics are Mean-Square-Error (MSE) and Bit-Error-Rate (BER) in block faded Rayleigh channels.

We report MSE, measured between $\hat{\mathbf{s}}$ and $\mathbf{s}$, as a function of the number of iterations (antenna index). The reported signal-to-noise ratio (SNR) is the average receive power at any base station antenna, divided by the noise variance.

MSE results for SGD are shown in Figure 2 for three different step-size values. As can be observed, step-size plays a critical role in the convergence speed of the algorithm. High step-size values provide faster convergence but high steadystate MSE, and low values may not even enter into the steadystate within the array. Given a certain $M$ and $K$, it is possible to find an optimum step-size which provides the lowest MSE.

![](https://cdn.mathpix.com/cropped/4cb60caf-d806-4796-a4fe-e8e77d7fe26a-4.jpg?height=506&width=581&top_left_y=1658&top_left_x=298)
Fig. 2. MSE vs antenna index for three different step-size values in SGD.

We now turn our attention towards Figures 3 and 4 which compare RLS, SGD, and ASGD. When the SGD sequence is averaged, MSE and BER curves get closer for different stepsizes, making the algorithm robust against non-optimal stepsize selection. The selection of $n_{0}$ also has an impact, but less compared to non-optimal step-size in SGD. As shown in

Figure 4, RLS meets ZF (2) performance, as it is optimal for a Gaussian noise source [9]. For large $M$, performance of RLS and ASGD converge due to ASGD's asymptotically optimal rate property.

## B. Strengths of Daisy-Chain Topology

Ostensibly, it may come across as if our daisy-chain solution incurs a latency penalty. This is, however, not the case as the detection process over time and/or frequency can be pipelined. While cluster 2 is processing data at subcarrier, say, $f_{0}$, cluster 1 can process data at subcarrier $f_{0}+1$. In the next iteration, cluster 2 processes data at subcarrier $f_{0}+1$, etc. See Figure 5 for a graphical visualization of the pipelining procedure.

Further, our daisy-chain solution allows for a power save since if a cluster $n$ regards its incoming estimate to be sufficiently good, then it can do one out of at least two things, 1) set $\hat{\mathbf{s}}_{n+1}=\hat{\mathbf{s}}_{n}$, or 2) send the incoming estimate $\hat{\mathbf{s}}_{n}$ to the baseband processing node, thereby terminating the detection procedure. The former has the advantage over the latter that only the last cluster needs to be connected to the baseband processing unit. Further, an indication whether or not the incoming estimate is of sufficiently good quality can be obtained, e.g. for RLS, by the value $\varepsilon_{n}$ in (3).

Finally, our topology is flexible so that additional antenna clusters can be added in a plug-and-play fashion. For example, in order to double the number of antennas, it is merely required to disconnect the cable between the last cluster and the baseband processing unit, connect that very cable to the last cluster of the added antenna array, and connect the two arrays. This will solely impact software scheduling at the baseband processing unit, but not the hardware as would have been the case for the centralized topology in Figure 1a.

## C. Interconnection Data-Rate

In order to estimate the expected data-rate in the proposed architecture, we can assume an OFDM-based frame structure based on slots. Each slot is made by $N_{\text {slot }}$ consecutive OFDM symbols with duration $T_{\text {ofdm }}$. Each symbol contains $N_{\mathrm{u}}$ subcarriers (an RE in OFDM) to carry user data. We can determine the average input/output data rate in the uplink for each of the clusters during a certain slot for SGD as follows

$$
\begin{equation*}
\bar{R}_{\mathrm{SGD}}=\frac{K \cdot w_{\mathrm{s}} \cdot N_{\mathrm{u}} \cdot N_{\mathrm{UL}}}{T_{\mathrm{slot}}}=\alpha \cdot \frac{K \cdot w_{\mathrm{s}} \cdot N_{\mathrm{u}}}{T_{\mathrm{ofdm}}}, \tag{8}
\end{equation*}
$$

where $T_{\text {slot }}$ is the slot duration, $N_{\text {UL }}$ is the number of OFDM symbols allocated for UL data in a slot, $w_{\mathrm{s}}$ is the number of bits used to represent each element in the sequence of estimates ( $\hat{\mathbf{s}}_{n}$ ) and $\alpha=\frac{N_{\mathrm{UL}}}{T_{\text {slot }}}$ represents the fraction of time spent in UL within the slot, so $0 \leq \alpha \leq 1$. In Figure 1b, $\bar{R}_{\mathrm{SGD}}$ corresponds to R .

This analysis does not take into account the total amount of data that is generated (which depends on $M$ ) and needs to move through the structure, but only the data that moves between clusters (which depends on $K$ ) because it is the one that imposes physical constraints in the inter-cluster connections and may limit the scalability.

![](https://cdn.mathpix.com/cropped/4cb60caf-d806-4796-a4fe-e8e77d7fe26a-5.jpg?height=591&width=1411&top_left_y=232&top_left_x=345)
Fig. 3. MSE vs antenna index for RLS, SGD and ASGD for different step-size values. Left: $\mathrm{M}=256 . n_{0}=150$ and 75 for $\mu=0.02$ and 0.04 respectively. Right: $\mathrm{M}=2048 . n_{0}=1000$ and 400 for $\mu=0.004$ and 0.008 respectively. $\mathrm{K}=16$ and $\mathrm{SNR}=12 \mathrm{~dB}$ in all cases.

![](https://cdn.mathpix.com/cropped/4cb60caf-d806-4796-a4fe-e8e77d7fe26a-5.jpg?height=583&width=1387&top_left_y=1001&top_left_x=343)
Fig. 4. BER vs SNR for RLS, ASGD and ZF. Left: M=256, 16QAM. Right: M=2048, 64QAM. K=16 and SNR=12dB for both cases.

For ASGD, the averaged data rate is expected to be twice the one in SGD, because for each sequence element, two previous elements, $\hat{\mathbf{x}}_{n}$ and $\hat{\mathbf{s}}_{n-1}$, are needed as can be observed in (7), and therefore

$$
\begin{equation*}
\bar{R}_{\mathrm{ASGD}}=2 \cdot \bar{R}_{\mathrm{SGD}} . \tag{9}
\end{equation*}
$$

For RLS, the data-rate has two components, one due to the preprocessing stage and the other one due to each RE. During the first stage, matrix $\boldsymbol{\Gamma}$ is passed from cluster to cluster. During the RE processing stage, data rate is the same as in SGD. The averaged data rate for RLS is calculated as

$$
\begin{align*}
\bar{R}_{\mathrm{RLS}} & =\frac{N_{\mathrm{CB}} \cdot K^{2} \cdot w_{\gamma}}{T_{\mathrm{slot}}}+\frac{K \cdot w_{\mathrm{s}} \cdot N_{\mathrm{u}} \cdot N_{\mathrm{UL}}}{T_{\mathrm{slot}}} \\
& =\frac{N_{\mathrm{u}} \cdot N_{\mathrm{slot}}}{S_{\mathrm{CB}}} \cdot \frac{K^{2} \cdot w_{\gamma}}{T_{\mathrm{ofdm}} \cdot N_{\mathrm{slot}}}+\alpha \cdot \frac{K \cdot w_{\mathrm{s}} \cdot N_{\mathrm{u}}}{T_{\mathrm{ofdm}}}  \tag{10}\\
& =\alpha \cdot \frac{K \cdot w_{\mathrm{s}} \cdot N_{\mathrm{u}}}{T_{\mathrm{ofdm}}} \cdot\left(1+\frac{\beta}{\alpha} \cdot \frac{K}{S_{\mathrm{CB}}}\right),
\end{align*}
$$

where $N_{\mathrm{CB}}$ is the number of CBs per slot, $S_{\mathrm{CB}}$ the number of REs in each CB, $w_{\gamma}$ the number of bits to represent each
element in $\boldsymbol{\Gamma}$ and $\beta=\frac{w_{\gamma}}{w_{\mathrm{s}}}$. From (10) it can be seen that $\bar{R}_{\mathrm{RLS}}>\bar{R}_{\mathrm{SGD}}$.

We can compare our proposed solution with another clusterbased decentralized architecture, but which relies on a central node to collect partial results, performing a low complexity operation, such as averaging, and broadcasting back the result to the clusters according to an iterative algorithm. This star topology has been proposed in [6]. In this case, the central node will have $C$ bi-directional links with an average aggregated data rate per direction of

$$
\begin{equation*}
\bar{R}_{\mathrm{star}}=C \cdot n_{\mathrm{iter}} \cdot \bar{R}_{\mathrm{SGD}}, \tag{11}
\end{equation*}
$$

where $n_{\text {iter }}$ is the number of iterations for the selected detection algorithm. From (11) we can observe that typically $\bar{R}_{\text {star }} \gg \bar{R}_{\mathrm{SGD}}$.

In case of a fully centralized architecture as the one in [5], the interconnection data-rate depends linearly on $M$ as follows

$$
\begin{equation*}
\bar{R}_{\mathrm{central}}=\frac{M \cdot N_{\mathrm{u}} \cdot N_{\mathrm{UL}} \cdot w_{\mathrm{sc}}}{T_{\mathrm{slot}}}=\alpha \cdot \frac{M \cdot N_{\mathrm{u}} \cdot w_{\mathrm{sc}}}{T_{\mathrm{ofdm}}}, \tag{12}
\end{equation*}
$$

![](https://cdn.mathpix.com/cropped/4cb60caf-d806-4796-a4fe-e8e77d7fe26a-6.jpg?height=514&width=1402&top_left_y=180&top_left_x=365)
Fig. 5. Time diagram representing cluster activities during one uplink slot with 4 OFDM symbol: one pilot and three data symbols. Only cluster 1 and C (last one) are represented for simplicity. Two types of activities are shown per cluster. The first one represents Pre-processing stage (PREP), only if RLS is used. The second one is the MIMO activity, which involves detection. First cluster start processing first RE after complete reception of Data 1. Once such RE is processed, it is then passed to next cluster for further processing and this is repeated successively through all clusters. As it is shown in the figure, there is a delay (T) for the starting time in cluster C compared to first cluster. T needs to be small enough to meet latency constraints.

TABLE I
Data Rate comparison for different topologies / algorithms
| M | 128 | 256 | 512 | 1024 |
| :--- | :--- | :--- | :--- | :--- |
| K | 16 | 32 | 64 | 128 |
| C | 8 | 8 | 16 | 16 |
| B | 16 | 32 | 32 | 64 |
| $\bar{R}_{\mathrm{SGD}}$ | $439 \mathrm{MB} / \mathrm{s}$ | $879 \mathrm{MB} / \mathrm{s}$ | $1.7 \mathrm{~GB} / \mathrm{s}$ | $3.4 \mathrm{~GB} / \mathrm{s}$ |
| $\bar{R}_{\text {RLS }}$ | $470 \mathrm{MB} / \mathrm{s}$ | $1.0 \mathrm{~GB} / \mathrm{s}$ | $2.2 \mathrm{~GB} / \mathrm{s}$ | $5.3 \mathrm{~GB} / \mathrm{s}$ |
| $\bar{R}_{\text {ASGD }}$ | $879 \mathrm{MB} / \mathrm{s}$ | $1.7 \mathrm{~GB} / \mathrm{s}$ | $3.4 \mathrm{~GB} / \mathrm{s}$ | $6.8 \mathrm{~GB} / \mathrm{s}$ |
| $\bar{R}_{\text {star }}$ [6] | $10.3 \mathrm{~GB} / \mathrm{s}$ | $10.3 \mathrm{~GB} / \mathrm{s}$ | $20.6 \mathrm{~GB} / \mathrm{s}$ | $20.6 \mathrm{~GB} / \mathrm{s}$ |
| $\bar{R}_{\text {central }}$ [5] | $5.1 \mathrm{~GB} / \mathrm{s}$ | $10.2 \mathrm{~GB} / \mathrm{s}$ | $20.4 \mathrm{~GB} / \mathrm{s}$ | $40.8 \mathrm{~GB} / \mathrm{s}$ |


where $w_{\mathrm{sc}}$ is the number of bits representing a sample of the received signal $\mathbf{y}$. It is seen that (12) cannot scale easily. $\bar{R}_{\text {central }}$ corresponds to R in Figure 1a. Going from (12) to (8), roughly reduces the data-rate by a factor $\frac{M}{K}$ (typically $\geq 10$ in Massive MIMO).

Table I shows date-rates for four scenarios. We assume the following parameters: $T_{\text {slot }}=500 \mu s, w_{\mathrm{s}}=16, w_{\mathrm{sc}}=24$, $N_{\mathrm{u}}=1200, N_{\text {slot }}=7, N_{\text {UL }}=6, \alpha=6 / 7, \beta=3 / 2$, $S_{\mathrm{CB}}=400$ and $n_{\text {iter }}=3$. We can observe that the analyzed topology and algorithms achieve significantly lower interconnection data-rate than other architectures [5] [6], enabling future scalability. As observed, for very-large arrays, RLS and ASGD require similar data-rates and have similar performance, but RLS requires a pre-processing stage and matrix manipulation that ASGD does not.

## V. Conclusions

In this article we have introduced a base station uplink architecture for Massive MIMO and analyzed the main implementation bottleneck, the interconnection data-rate. We have proposed three algorithms and a fully decentralized topology for uplink detection, which alleviate this limitation. One of
the algorithms (RLS) achieves approximate zero-forcing performance, while another (ASGD) is an approximation which converges to the former one for very large arrays. All of them are of low-complexity and do not require matrix inversion. An estimate of data-rate is also presented and compared with other architectures for different array-sizes and configurations, showing the benefits of the proposed solution.

## Acknowledgment

This work was supported by ELLIIT, the Excellence Center at Linkping-Lund in Information Technlology.

## References

[1] T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Transactions on Wireless Communications, vol. 9, no. 11, pp. 3590-3600, November 2010.
[2] C. Shepard et al., "Argos: Practical many-antenna base stations," in Proceedings of the 18th Annual International Conference on Mobile Computing and Networking (Mobicom), New York, NY, USA, 2012, pp. 53-64. [Online]. Available: http://doi.acm.org/10.1145/2348543.2348553
[3] E. Bertilsson, O. Gustafsson, and E. G. Larsson, "A scalable architecture for massive MIMO base stations using distributed processing," in 2016 50th Asilomar Conference on Signals, Systems and Computers, Nov 2016, pp. 864-868.
[4] A. Puglielli et al., "Design of energy- and cost-efficient massive MIMO arrays," Proceedings of the IEEE, vol. 104, no. 3, pp. 586-606, March 2016.
[5] S. Malkowsky et al., "The world's first real-time testbed for massive MIMO: Design, implementation, and validation," IEEE Access, vol. 5, pp. 9073-9088, 2017.
[6] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE Journal on Emerging and Selected Topics in Circuits and Systems, vol. 7, no. 4, pp. 491-507, Dec 2017.
[7] L. Ljung and T. Söderström, Theory and Practice of Recursive Identification. The MIT Press, 1983.
[8] H. J. Kushner and G. G. Yin, Stochastic Approximation and Recursive Algorithms and Applications, 2nd ed. Springer, 2003.
[9] B. Polyak and A. B. Juditsky, "Acceleration of stochastic approximation by averaging," SIAM Journal on Control and Optimization, vol. 30, pp. 838-855, July 1992.
[10] B. Polyak and Y. Z. Tsypkin, "Adaptive estimation algorithms (convergence, optimality, stability)," Automation and Remote Control, vol. 40, pp. 378-390, March 1979.

