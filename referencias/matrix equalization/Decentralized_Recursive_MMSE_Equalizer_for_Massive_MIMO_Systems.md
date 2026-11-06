# Decentralized Recursive MMSE Equalizer for Massive MIMO Systems 

Kang Zheng ${ }^{* \ddagger}$, Hao Gao*, Shuai Cui* ${ }^{*}$, Jiaheng Wang* ${ }^{*}$, Yongming Huang* ${ }^{*}$<br>*National Mobile Communications Research Laboratory, Southeast University, Nanjing 210096, China<br>${ }^{\dagger}$ Purple Mountain Laboratories, Nanjing 211100, China<br>${ }^{\ddagger}$ China Mobile Innovation Institute, Nanjing 211899, China<br>\{francis.zk.nj@gmail.com, gaohao_seu@seu.edu.cn, cuishuai@seu.edu.cn, jhwang@seu.edu.cn, huangym@seu.edu.cn\}


#### Abstract

In massive multiple-input multiple-output (MIMO) systems, linear equalizers such as zero-forcing (ZF) and minimum mean-square error (MMSE) equalizers are often used and implemented in a centralized way. As the antenna number increases, the centralized equalization requires a huge data exchange rate as well as intensive central processing capability. Decentralized equalization can alleviate this bottleneck by partitioning the antenna array into multiple clusters and conducting equalization separately and locally. In this paper, we design a decentralized MMSE equalizer based on the chain architecture. The proposed equalizer is conducted in a recursive manner through a chain and generates a sequence of estimated signals that converge to the MMSE solution. Furthermore, we also propose an early termination strategy according to channel quality, thus reducing complexity and data exchange rate. Simulation results illustrate that the proposed recursive MMSE equalizer outperforms the existing decentralized equalizer, and achieves the same BER performance as the centralized MMSE equalizer with a lower data exchange rate.


Index Terms-Decentralized equalizer, massive MIMO, MMSE, chain architecture.

## I. Introduction

Massive MIMO technology plays an important role in improving spectrum efficiency and link reliability in newgeneration wireless communication systems. By deploying many antennas at the base station (BS), the spatial resolution is improved without increasing the bandwidth so that the base station can serve more users simultaneously [1]. More importantly, such benefits can be achieved by using relatively simple transceivers, e.g., linear transceivers, in massive MIMO systems [2], [3]. In practice, the zero-forcing (ZF) and minimum mean-square error (MMSE) equalizers are often used at the receiver of a massive MIMO system due to their balance of complexity and performance.

Most existing massive MIMO equalizers, including the ZF and MMSE equalizers, are implemented in a centralized way. However, the centralized architecture has several inherent limitations. First, centralized baseband data processing must collect each antenna's received signal and channel state information (CSI). As the scale of the antenna array increases, the data exchange limitations becomes the main implementation bottleneck. The aggregate data rate between the antenna units and the central processing unit (CPU) could easily reach hundreds of Gbps or even more. Second, the BS must support
various applications in different antenna scale scenarios. The centralized massive MIMO transceivers usually have a fixed structure, which is inflexible and costly for system expansion. Third, the centralized data processing is quite demanding on the performance of CPUs, which increases the difficulty and cost of designing and manufacturing microchips for massive MIMO systems. Therefore, the centralized architecture may become a bottleneck restricting massive MIMO applications in the future.

For these reasons, decentralized massive MIMO architectures, where antennas in BS are partitioned into several clusters, each of which has independent radio-frequency (RF) and computing hardware to carry out local RF processing, channel estimation (CHEST), and signal equalization, becomes attractive. In particular, the authors of [4]-[9] proposed the tree architecture, which performs uplink equalization locally in each cluster but still needs a central unit to collect all processing results and conduct the final equalization. In the ring architecture proposed in [10], [11], the multiple clusters are connected end to end to form a ring. Each cluster in the ring performs a block gradient descent to update a part of the equalization matrix and deliver interaction information to its adjacent cluster. Such methods usually need a number of iterations, which could result in non-negligible processing latency. In [12], [13], the chain architecture was proposed, in which the connected clusters form a chain and the entire signal equalization is processed through the chain with a stable inter-cluster flow. Among several decentralized architectures, the chain architecture is favorable due to its fully distributed, non-iterative and low-interaction features and thus has wider application prospects.

In this paper, we propose a novel decentralized equalizer based on the chain architecture for massive MIMO systems. Specifically, we exploit the hidden recursive property of the MMSE equalization and invoke the Gaussian elimination to implement it over the chain architecture. In our equalizer, each cluster utilizes the gram matrix received from the previous cluster and the local channel state information to form the equalization matrix, with which the residual error is filtered to modify the old estimate recursively through the chain. We also propose an early termination strategy that selects the appropriate number of clusters to work and thus reduces complexity

![](https://cdn.mathpix.com/cropped/b8932a0a-651c-4878-8d36-d92dde9091fa-2.jpg?height=729&width=796&top_left_y=180&top_left_x=197)
Fig. 1. The chain architecture for decentralized equalization.

and data exchange. The computational complexity and data exchange rate of the proposed recursive MMSE equalizer are analyzed and compared with the existing ones. Simulation results show that the proposed decentralized equalizer outperforms the existing decentralized equalizer and achieves the same performance as the centralized MMSE equalizer but with lower data exchange.

## II. System Model

Consider the uplink of a massive MIMO system, where the BS is equipped with $M$ antennas and serves $K$ single-antenna users. The signal model is given by

$$
\begin{equation*}
\mathbf{y}=\mathbf{H} \mathbf{x}+\mathbf{n} \tag{1}
\end{equation*}
$$

where $\mathbf{y} \in \mathbb{C}^{M \times 1}$ is the received signal at the BS, $\mathbf{x} \in \mathbb{C}^{K \times 1}$ is the transmitted signal with $E\left\{\mathbf{x x}^{H}\right\}=\mathbf{I}, \mathbf{n} \in \mathbb{C}^{M \times 1}$ is the i.i.d. circularly-symmetric complex Gaussian noise with $E\left\{\mathbf{n n}^{H}\right\}=\sigma^{2} \mathbf{I}$, and $\mathbf{H}$ is the channel matrix which is assumed to be perfectly known by the BS .

In practice, two common linear equalizers are often used at the BS . One this is the ZF equalizer

$$
\begin{align*}
\widehat{\mathbf{x}}_{Z F} & =\mathbf{W}_{Z F} \mathbf{y} \\
& =\left(\mathbf{H}^{H} \mathbf{H}\right)^{-1} \mathbf{H}^{H} \mathbf{y} \tag{2}
\end{align*}
$$

and the other is the MMSE equalizer

$$
\begin{align*}
\widehat{\mathbf{x}}_{M M S E} & =\mathbf{W}_{M M S E} \mathbf{y} \\
& =\mathbf{H}^{H}\left(\mathbf{H} \mathbf{H}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \mathbf{y} \tag{3}
\end{align*}
$$

These two equalizers need to collect the complete matrix $\mathbf{H}$ and calculate (2) and (3) in a centralized way, leading to excessive data exchange and high computation capacity for the central processing unit (CPU).

## III. Decentralized Chain Architecture

In order to reduce data exchange in baseband processing, we consider signal equalization in a decentralized architecture, called the chain architecture, as shown in Fig. 1. In this architecture, The $M$ BS antennas are partitioned into $C$ clusters, each having $L=M / C$ antennas. These clusters are connected serially by a dedicated connection, forming a chain architecture.

Each cluster can individually receive the uplink signal, perform RF processing, and conduct local channel estimation. More importantly, each cluster can perform local signal equalization using massages from the previous cluster in the chain and transmits necessary massages to the next cluster. The intermediately estimated signal is passed through the chain during the entire signal equalization process, being updated at every cluster and finally output by the last cluster. It deserves noting that the data exchange rate between clusters remains constant no matter how the number of antennas changes, which benefits the expansion of the BS antennas.

To perform signal equalization in the above architecture, the GD algorithm is proposed in [13]. It is essentially based on the ZF equalizer and solves the following unconstrained problem

$$
\begin{equation*}
\underset{\mathbf{x}}{\operatorname{minimize}} f(\mathbf{x})=\|\mathbf{y}-\mathbf{H} \mathbf{x}\|^{2} \tag{4}
\end{equation*}
$$

via the gradient descent algorithm. In order to operate it in decentralized way, the algorithm calculates the gradient of $f(\mathbf{x})$ in a greedy way with the information available at the local cluster. The procedure can be described as follows

$$
\begin{gather*}
\varepsilon_{m}=y_{m}-\mathbf{h}_{m}^{T} \mathbf{x}_{m-1}  \tag{5}\\
\mathbf{x}_{m}=\mathbf{x}_{m-1}+\mu_{m} \mathbf{h}_{m}^{*} \varepsilon_{m} \tag{6}
\end{gather*}
$$

where $\mathbf{h}_{m}$ and $y_{m}$ represent the channel vector and received signal of the antenna $m$ respectively. In (6), $\mu_{m}$ is a sequence of step sizes and can be obtained by

$$
\begin{equation*}
\mu_{m}=\frac{1}{2} \frac{N}{M} \log (4 M \cdot S N R) \tag{7}
\end{equation*}
$$

for block faded Rayleigh channels according to [13].

## IV. Decentralized MMSE Equalization

In this section, we propose a decentralized MMSE equalizer, which is applicable to the aforementioned chain architecture.

## A. Recursive MMSE Equalization

We first divide the channel matrix $\mathbf{H}$ and received signal $\mathbf{y}$ into $\mathbf{H}=\left[\mathbf{H}_{1}^{H}, \mathbf{H}_{2}^{H}, \ldots, \mathbf{H}_{C}^{H}\right]^{H}$ and $\mathbf{y}=\left[\mathbf{y}_{1}, \mathbf{y}_{2}, \ldots, \mathbf{y}_{C}\right]$, respectively, and define

$$
\begin{gathered}
\overline{\mathbf{H}}_{c} \triangleq\left[\mathbf{H}_{1}^{H}, \mathbf{H}_{2}^{H}, \ldots ; \mathbf{H}_{c}^{H}\right]^{H} \in \mathbb{C}^{c L \times K} \\
\overline{\mathbf{y}}_{c} \triangleq\left[\mathbf{y}_{1} ; \mathbf{y}_{2} ; \ldots ; \mathbf{y}_{c}\right] \in \mathbb{C}^{c L \times 1}
\end{gathered}
$$

Then, the output estimate of cluster $c$ in the chain is given by

$$
\begin{equation*}
\widehat{\mathbf{x}}^{(c)}=\overline{\mathbf{H}}_{c}^{H}\left(\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \overline{\mathbf{y}}_{c} \tag{8}
\end{equation*}
$$

Similarly, the output estimate of cluster $c+1$ is given by

$$
\begin{equation*}
\widehat{\mathbf{x}}^{(c+1)}=\overline{\mathbf{H}}_{c+1}^{H}\left(\overline{\mathbf{H}}_{c+1} \overline{\mathbf{H}}_{c+1}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \overline{\mathbf{y}}_{c+1} \tag{9}
\end{equation*}
$$

According to the definition of $\overline{\mathbf{H}}_{c}, \overline{\mathbf{y}}_{c}$, (9) can be rewritten into

$$
\widehat{\mathbf{x}}^{(c+1)}=\left[\overline{\mathbf{H}}_{c}^{H} \mathbf{H}_{c+1}^{H}\right]\left[\begin{array}{l}
\mathbf{a}_{1}  \tag{10}\\
\mathbf{a}_{2}
\end{array}\right]
$$

where $\mathbf{a}_{1} \in \mathbb{C}^{c L \times 1}, \mathbf{a}_{2} \in \mathbb{C}^{L \times 1}$ and

$$
\left[\begin{array}{l}
\mathbf{a}_{1}  \tag{11}\\
\mathbf{a}_{2}
\end{array}\right]=\left[\begin{array}{cc}
\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I} & \overline{\mathbf{H}}_{c} \mathbf{H}_{c+1}^{H} \\
\mathbf{H}_{c+1} \overline{\mathbf{H}}_{c}^{H} & \mathbf{H}_{c+1} \mathbf{H}_{c+1}^{H}+\sigma^{2} \mathbf{I}
\end{array}\right]^{-1}\left[\begin{array}{c}
\overline{\mathbf{y}}_{c} \\
\mathbf{y}_{c+1}
\end{array}\right]
$$

We futher rewrite (11) into

$$
\left[\begin{array}{cc}
\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I} & \overline{\mathbf{H}}_{c} \mathbf{H}_{c+1}^{H}  \tag{12}\\
\mathbf{H}_{c+1} \overline{\mathbf{H}}_{c}^{H} & \mathbf{H}_{c+1} \mathbf{H}_{c+1}^{H}+\sigma^{2} \mathbf{I}
\end{array}\right]\left[\begin{array}{l}
\mathbf{a}_{1} \\
\mathbf{a}_{2}
\end{array}\right]=\left[\begin{array}{c}
\overline{\mathbf{y}}_{c} \\
\mathbf{y}_{c+1}
\end{array}\right]
$$

Then, solving the above equations through the Gaussian elimination, we obtain

$$
\begin{gather*}
\mathbf{a}_{1}=\left(\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I}\right)^{-1}\left(\overline{\mathbf{y}}_{c}-\left(\overline{\mathbf{H}}_{c} \mathbf{H}_{c+1}^{H}\right) \mathbf{a}_{2}\right)  \tag{13}\\
\mathbf{a}_{2}=\left(\mathbf{H}_{c+1} \mathbf{H}_{c+1}^{H}+\sigma^{2} \mathbf{I}-\mathbf{H}_{c+1} \mathbf{S}_{c} \mathbf{H}_{c+1}^{H}\right)^{-1} \epsilon^{(c+1)} \tag{14}
\end{gather*}
$$

where

$$
\begin{gather*}
\mathbf{S}_{c}=\overline{\mathbf{H}}_{c}^{H}\left(\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \overline{\mathbf{H}}_{c}  \tag{15}\\
\epsilon^{(c+1)}=\mathbf{y}_{c+1}-\mathbf{H}_{c+1} \widehat{\mathbf{x}}^{(c)} \tag{16}
\end{gather*}
$$

Substituting (13) and (14) into (10), we have the following recursive form of MMSE equalization:

$$
\begin{equation*}
\widehat{\mathbf{x}}^{(c+1)}=\widehat{\mathbf{x}}^{(c)}+\mathbf{E}^{(c+1)} \epsilon^{(c+1)} \tag{17}
\end{equation*}
$$

where

$$
\begin{equation*}
\mathbf{E}^{(c+1)}=\left(\mathbf{I}-\mathbf{S}_{c}\right) \mathbf{H}_{c+1}^{H}\left(\mathbf{H}_{c+1}\left(\mathbf{I}-\mathbf{S}_{c}\right) \mathbf{H}_{c+1}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \tag{18}
\end{equation*}
$$

This form of the MMSE equalizer can be applied in the chain architecture in Fig. 1. Specifically, according to (18), cluster $c+1$ needs to know the knowledge of $\mathbf{S}_{c}$ and $\widehat{\mathbf{x}}^{(c)}$ for local signal equalization. Note that $\mathbf{S}_{c}$ can be calculated as

$$
\begin{aligned}
\mathbf{S}_{c} & =\overline{\mathbf{H}}_{c}^{H}\left(\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \overline{\mathbf{H}}_{c} \\
& =\overline{\mathbf{H}}_{c}^{H} \overline{\mathbf{H}}_{c}\left(\overline{\mathbf{H}}_{c}^{H} \overline{\mathbf{H}}_{c}+\sigma^{2} \mathbf{I}\right)^{-1} \\
& =\sum_{i=1}^{c} \mathbf{H}_{c}^{H} \mathbf{H}_{c}\left(\sum_{i=1}^{c} \mathbf{H}_{c}^{H} \mathbf{H}_{c}+\sigma^{2} \mathbf{I}\right)^{-1} .
\end{aligned}
$$

Hence, cluster $c$ should provide $\overline{\mathbf{H}}_{c}^{H} \overline{\mathbf{H}}_{c}$ and $\widehat{\mathbf{x}}^{(c)}$ to cluster $c+1$. Consequently, the recursive MMSE equalization can be performed in the chain architecture as stated in Algorithm 1. Compared to the traditional centralized MMSE equalizer, the recursive MMSE equalizer only computes $\mathbf{E}$ in each cluster instead of calculating the whole equalization matrix.

Algorithm 1 Recursive MMSE Equalization.

## Preprocessing phase:

1) The first cluster calculates $\mathbf{H}_{1}^{H} \mathbf{H}_{1}$ and then transmits $\mathbf{H}_{1}^{H} \mathbf{H}_{1}$ to the cluster 2;
2) After receiving $\sum_{i=1}^{c-1} \mathbf{H}_{i}^{H} \mathbf{H}_{i}$, the cluster c calculates $\sum_{i=1}^{c} \mathbf{H}_{i}^{H} \mathbf{H}_{i}$ and then transmits $\sum_{i=1}^{c} \mathbf{H}_{i}^{H} \mathbf{H}_{i}$ to next cluster until $c=C$.

## Filtering phase:

1) The first cluster calculates (17) with setting $\widehat{\mathbf{x}}^{(0)}= 0, \mathbf{S}_{0}=0$ and transmits $\widehat{\mathbf{x}}^{(1)}$ to the cluster 2;
2) After receiving $\widehat{\mathbf{x}}^{(c-1)}$, the cluster c calculates (17) and send $\widehat{\mathbf{x}}^{(c)}$ to cluster $(c+1)$ until $c=C$.
Output $\widehat{\mathbf{x}}^{(C)}$.

## B. Early Termination

In (17), the new estimate is the sum of the old estimate and a correction term. If the correction term is small enough, the old estimate is close to the new one and does not need to be updated. Then the following clusters perform

$$
\widehat{\mathbf{x}}^{(c)}=\widehat{\mathbf{x}}^{(c-1)}
$$

to terminate the equalization procedure.
There are two strategies to determine when to terminate the recursion.

- Strategy 1: Terminate the recursion when the norm of $\epsilon^{(c)}$ in (16) is small enough. This means

$$
\mathbf{y}^{(c)} \approx \mathbf{H}_{c}^{H} \widehat{\mathbf{x}}^{(c-1)}
$$

i.e., the SNR is high enough and the estimate from cluster $c-1$ is sufficiently accurate.

- Strategy 2: Terminate the recursion when the trace of $\left(\mathbf{I}-\mathbf{S}_{c}\right)$ is small enough. This is equivalent to using $E\left\{\operatorname{Tr}\left(\widehat{\mathbf{x}}^{(c)}-\mathbf{x}\right)\left(\widehat{\mathbf{x}}^{(c)}-\mathbf{x}\right)^{H}\right\}$ as an indicator to judge whether the estimate from cluster $c-1$ is of sufficiently good quality because

$$
\begin{align*}
& E\left\{\left(\widehat{\mathbf{x}}^{(c)}-\mathbf{x}\right)\left(\widehat{\mathbf{x}}^{(c)}-\mathbf{x}\right)^{H}\right\} \\
= & \mathbf{I}-\overline{\mathbf{H}}_{c}^{H}\left(\overline{\mathbf{H}}_{c} \overline{\mathbf{H}}_{c}^{H}+\sigma^{2} \mathbf{I}\right)^{-1} \overline{\mathbf{H}}_{c}  \tag{19}\\
= & \mathbf{I}-\mathbf{S}_{c}
\end{align*}
$$

If $\operatorname{Tr}\left(\mathbf{I}-\mathbf{S}_{c}\right)$ is less than a certain threshold, the following clusters will no longer calculate $\mathbf{E}$, lessening the calculation and transmission of the Gram matrix.
Generally, with a large number of BS antennas or high SNR, the equalization procedure can be earlier terminated, thus reducing the computational complexity and data exchange in the following clusters.

## V. Numerical Analysis

In this section, we analyze the proposed recursive MMSE equalizer (r-MMSE) by comparing it with the centralized MMSE equalizer (c-MMSE) and the GD algorithm [13] in

Table I
Complexity of Three Algorithms
| Algorithm | Complex multiplications | Example |
| :---: | :---: | :---: |
| c-MMSE | $2 K^{2} M+\alpha K M+\frac{1}{3} K^{3}$ | 8874.7 |
| r-MMSE | $\frac{1}{3} K^{3}(4 C-3)+K^{2} L(3 C-1)$ | 31274.7 |
| GD | $+K L^{2}(2 C-2)+\frac{1}{3} L^{3}(C-1)+\alpha K L(2 C-1)$ | 1024 |


Table II
Average Data Rate Per Cluster of Three Algorithms
| Algorithm | $M=64$ | $M=128$ | $M=512$ |
| :---: | :---: | :---: | :---: |
|  | $K=6$ | $K=12$ | $K=48$ |
| c-MMSE | $8.8 G B / s$ | $17.7 G B / s$ | $70.8 G B / s$ |
| r-MMSE | $802 M B / s$ | $2.1 G B / s$ | $20.3 G B / s$ |
| GD | $553 M B / s$ | $1.1 G B / s$ | $4.4 G B / s$ |


terms of the computational complexity, data exchange between clusters, and BER performance. From a practical point of view, we consider the massive MIMO system using orthogonal frequency division multiplexing (OFDM) for high-speed transmission. The OFDM frame structure is based on slots. Each slot consists of $N_{U L}$ consecutive OFDM symbols for uplink data, each symbol containing $N_{u}$ subcarriers. The channel response on adjacent $\alpha$ frequency-time domains, forming one Physical Resource Block (PRB), is approximately constant. Moreover, the user data in $\alpha$ frequency-time domains are handled by the same equalization matrix.

## A. Computational Complexity

The complexity of complex multiplications required to formulate one equalization matrix is $K^{2} L+\frac{1}{3} K^{3}$ in the first cluster and $\frac{4}{3} K^{3}+2 K^{2} L+2 K L^{2}+\frac{1}{3} L^{3}$ in other clusters. Furthermore, during the filtering phase, each cluster calculates $\epsilon^{(c)}$ and applies $\mathbf{E}_{c}$ to it. Each cluster's complexity of complex multiplications is $2 K L$, except for the first cluster, which needs $K L$ complex multiplications.

The total complex multiplications of three equalizers are listed in Table I, in which the number of frequency-time domains in one PRB is $\alpha=1$, the number of single-antenna users is $K=8$, the number of clusters is $C=4$, the number of antennas of each cluster is $L=16$, and the number of BS antennas $M=64$. As shown in Table I, the r-MMSE equalizer introduces additional complexity compared to the cMMSE equalizer, which is a natural cost of decentralization. Furthermore, the complexity of the decentralized equalizers, both r-MMSE and GD, increases as the number of clusters increases. In particular, the r-MMSE equalizer is equivalent to the c-MMSE equalizer when $C=1$.

On the other hand, the complexity per cluster in a decentralized equalizer is $1 / C$ times the total complex multiplications, which is significantly lower than the total complex multiplications of the centralized equalizer. It means that the computational complexity of each cluster in a decentralized equalizer is far lower than that of a centralized one.

## B. Data Exchange Rate

The r-MMSE equalizer requires the exchange of the $K \times K$ dimensional matrix between the clusters to calculate the filter matrix and the $K$ dimensional estimate vector during the filtering phase. The data exchange rate per cluster and per slot is

$$
\begin{equation*}
R_{r-M M S E}=\frac{2 \omega_{A} K^{2} N_{u} N_{U L}}{\alpha T_{\text {slot }}}+\frac{2 \omega_{x} K N_{u} N_{U L}}{T_{\text {slot }}} \tag{20}
\end{equation*}
$$

![](https://cdn.mathpix.com/cropped/b8932a0a-651c-4878-8d36-d92dde9091fa-4.jpg?height=575&width=716&top_left_y=519&top_left_x=1147)
Fig. 2. BER vs SNR of three algorithms with $M=128$ and $M=512$ in block faded Rayleigh channels.

where $T_{\text {slot }}$ is the slot duration, $\omega_{A}$ is the bit-width of $\mathbf{A}$ entries and $\omega_{x}$ is the bit-width of $\mathbf{x}$ entries.

The GD algorithm only needs to deliver the $K$ dimensional estimate and thus the data exchange rate is

$$
\begin{equation*}
R_{G D}=\frac{2 \omega_{x} K N_{u} N_{U L}}{T_{\text {slot }}} . \tag{21}
\end{equation*}
$$

The data exchange rate of the c-MMSE equalizer (by viewing it as a big cluser) is

$$
R_{c-M M S E}=\frac{2 \omega_{y} M N_{u} N_{U L}}{T_{\text {slot }}}
$$

where $\omega_{y}$ is the bit-width of $\mathbf{y}$ entries. The data exchange rate of each cluster of three equalizers are listed in table II with the parameters $T_{\text {slot }}=500 u s, N_{u}=480, N_{U L}=6, \mathbf{x}=16$, $\omega_{x}=8$ and $\omega_{y}=\omega_{A}=12$.

## C. BER Performance

The simulated BER performance of the three equalizers is presented in Fig. 2 with the block Rayleigh fading channels and Fig. 3 with the line-of-sight (LOS) channels. We set $K=8, L=16$, and $M=128$ or 512, and the number of clusters is given by $C=\frac{M}{L}$. From Figs. 2 and 3, it is observed that the r-MMSE equalizer achieves the same BER performance as the c-MMSE equalizer, which verifies the mathematical equivalence between the c-MMSE and r-MMSE equalizers, whereas the r-MMSE equalizer is implemented in a decentralized way. On the other hand, though the GD algorithm enjoys low complexity and data exchange, its BER performance is considerably inferior to the r-MMSE equalizer.

![](https://cdn.mathpix.com/cropped/b8932a0a-651c-4878-8d36-d92dde9091fa-5.jpg?height=579&width=721&top_left_y=201&top_left_x=227)
Fig. 3. BER vs SNR of three algorithms with $M=128$ and $M=512$ in LOS channels.

![](https://cdn.mathpix.com/cropped/b8932a0a-651c-4878-8d36-d92dde9091fa-5.jpg?height=592&width=708&top_left_y=932&top_left_x=240)
Fig. 4. The number of complex multiplications in the recursive procedure at different SNR.

The performance gap between the r-MMSE and GD equalizers becomes even larger when it comes to the LOS channels as shown in Fig. 3.

We also make a comparison between two early termination strategies in Fig. 4. We set the conditions to terminate the recursion in strategy 1 and strategy 2 to $\left\|\epsilon^{(c)}\right\|_{2}^{2}<0.05$ and $\operatorname{Tr}\left(\mathbf{I}-\mathbf{S}_{c}\right)<0.05$, respectively. It can be seen that the complexity of complex multiplications is reduced dramatically by early termination strategy 2 when the SNR exceeds a certain threshold, while the effect of strategy 1 is slight. This is because strategy 1 cuts down the computational complexity only in the filtering phase, whereas strategy 2 does it in both the preprocessing phase and the filtering phase.

## VI. Conclusions

In this paper, we have considered designing a decentralized equalizer with the chain architecture for massive MIMO systems. A decentralized recursive MMSE equalizer has been developed by exploiting the Gaussian elimination.

We also proposed the early termination strategies for the designed recursive MMSE equalizer to reduce computational complexity and data exchange. Simulations showed that the proposed recursive MMSE equalizer achieves the same BER performance as the centralized MMSE equalizer with low data exchange rate and per-cluster complexity, and outperforms the existing decentralized GD equalizer.

## Acknowledgment

This work was supported by the National Key R\&D Program of China under Grant 2018YFB1801103, the National Natural Science Foundation of China under Grants 61971130 and 61720106003, the Natural Science Foundation on Frontier Leading Technology Basic Research Project of Jiangsu under Grant BK20212001, the Key Technologies R\&D Program of Jiangsu (Prospective and Key Technologies for Industry) under Grants BE2022067 and BE2022067-5, and the Southeast University-China Mobile Research Institute Joint Innovation Center.

## References

[1] T. L. Marzetta, "Massive MIMO: An introduction," Bell Labs Technical Journal, vol. 20, pp. 11-22, 2015.
[2] S. Malkowsky, J. Vieira, L. Liu, P. Harris, K. Nieman, N. Kundargi, I. C. Wong, F. Tufvesson, V. Owall, and O. Edfors, "The world's first real-time testbed for massive MIMO: Design, implementation, and validation," IEEE Access, vol. 5, pp. 9073-9088, 2017.
[3] C. Shepard, H. Yu, N. Anand, E. Li, T. Marzetta, R. Yang, and L. Zhong, "Argos: Practical many-antenna base stations," in Proceedings of the 18th annual international conference on Mobile computing and networking, 2012, pp. 53-64.
[4] E. Bertilsson, O. Gustafsson, and E. G. Larsson, "A scalable architecture for massive MIMO base stations using distributed processing," in 2016 50th Asilomar Conference on Signals, Systems and Computers, 2016, pp. 864-868.
[5] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE Journal on Emerging and Selected Topics in Circuits and Systems, vol. 7, no. 4, pp. 491-507, 2017.
[6] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Transactions on Signal Processing, vol. 67, no. 17, pp. 4418-4432, 2019.
[7] Z. Zhang, H. Li, Y. Dong, X. Wang, and X. Dai, "Decentralized signal detection via expectation propagation algorithm for uplink massive MIMO systems," IEEE Transactions on Vehicular Technology, vol. 69, no. 10, pp. 11233-11240, 2020.
[8] Z. Zhang, Y. Dong, K. Long, X. Wang, and X. Dai, "Decentralized baseband processing with gaussian message passing detection for uplink massive MU-MIMO systems," IEEE Transactions on Vehicular Technology, vol. 71, no. 2, pp. 2152-2157, 2022.
[9] K. Li, C. Jeon, J. R. Cavallaro, and C. Studer, "Decentralized equalization for massive MU-MIMO on FPGA," in 2017 51st Asilomar Conference on Signals, Systems, and Computers, 2017, pp. 1532-1536.
[10] A. Kulkarni, M. A. Ouameur, and D. Massicotte, "Hardware topologies for decentralized large-scale MIMO detection using newton method," IEEE Transactions on Circuits and Systems I: Regular Papers, vol. 68, no. 9, pp. 3732-3745, 2021.
[11] X. Zhao, X. Guan, M. Li, and Q. Shi, "Decentralized linear MMSE equalizer under colored noise for massive MIMO systems," in 2021 IEEE Global Communications Conference (GLOBECOM), 2021, pp. 01-06.
[12] Q. Liu, H. Liu, Y. Yan, and P. Wu, "A distributed detection algorithm for uplink massive MIMO systems," in 2019 IEEE International Workshop on Signal Processing Systems (SiPS), 2019, pp. 213-217.
[13] J. Rodríguez Sánchez, F. Rusek, O. Edfors, M. Sarajlić, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms," IEEE Transactions on Signal Processing, vol. 68, pp. 687-700, 2020.

