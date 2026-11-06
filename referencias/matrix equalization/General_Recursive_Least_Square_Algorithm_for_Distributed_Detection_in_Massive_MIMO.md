# General Recursive Least Square Algorithm for Distributed Detection in Massive MIMO 

Qiqiang Chen ${ }^{(1)}$, Zheng Wang ${ }^{(1)}$, Senior Member, IEEE, Cong Ma ${ }^{(1)}$, Xiaoming Dai ${ }^{(1)}$, Member, IEEE, and Derrick Wing Kwan Ng ${ }^{(1)}$, Fellow, IEEE


#### Abstract

In this paper, a general recursive least square (GRLS) detection algorithm is proposed for the uplink of distributed massive multipleinput multiple-output (MIMO) to alleviate the bottlenecks in both computational complexity and data bandwidth for interconnection. Different from the existing recursive least square (RLS) detection algorithm which only supports a single antenna in each distributed unit (DU), the proposed GRLS allows for multiple antennas in each DU, rendering it adaptable to a variety of practical scenarios. Moreover, among the total $C$ DUs and with an integer parameter $C_{0}$, the computational complexity of $C-C_{0}$ DUs in GRLS can be significantly reduced by leveraging the channel hardening property. Through analysis, we demonstrate that the convergence of the GRLS algorithm is guaranteed if $C_{0} \geq\left\lfloor(\sqrt{B / 2}+\sqrt{K})^{2} / B\right\rfloor$ holds, where $K$ and $B$ denote the numbers of antennas at the user side and each DU, respectively. Furthermore, based on the daisy-chain architecture, the proposed GRLS algorithm also enjoys excellent scalability, which can be easily extended with extra DUs for further improvement. Finally, the detection complexity and data bandwidth analysis are also provided to unveil the superiority of GRLS compared to other distributed detection schemes for massive MIMO.


Index Terms-Daisy-chain, decentralized signal detection, distributed MIMO detection, Massive MIMO, RLS.

## I. Introduction

Due to its promising capacity, ultra-fast data rate, and high energy efficiency, massive MIMO has become a core technology for enabling beyond fifth-generation ( 5 G ) and sixth-generation ( 6 G ) wireless communications [1]. However, most of the existing detection schemes for massive MIMO are commonly implemented in a centralized manner. As the number of antennas at the base station (BS) increases to hundreds or thousands, there arises a pressing challenge in transferring the vast volumes of raw data for advanced signal processing, even with the state-of-the-art hardware capabilities [2]. Meanwhile, the rapid growths in both computational complexity and data storage requirement also render the single computing fabric difficult to satisfy practical demands. To this end, a number of distributed detection schemes for massive MIMO have been proposed [2], [3], [4], [5], [6], [7], [8], [9].

[^0]Specifically, the decentralized baseband processing (DBP) architecture was introduced in [2]. It partitions the BS antennas into $C$ individual DUs, where each DU contains $B$ antennas and is equipped with an independent computing fabric. Based on DBP, the alternating direction method of multipliers (ADMM), conjugate gradient (CG) methods [3], and expectation propagation algorithm (EPA) [4] can be applied for distributed massive MIMO detection but at a high data bandwidth cost. Besides, the minimum mean square error (FD-MMSE) [5] and the Gaussian message passing (GMP) [6] algorithms were employed on the fully decentralized architecture, which retains only an unidirectional link from DUs to the central processing unit (CPU), thereby further reducing the data bandwidth cost at the expense of practical performance degradation. Furthermore, with the aid of channel hardening, the decentralized Newton (DN) detection was designed for a lower complexity implementation [7]. However, all of these methods require a large number of antennas in DU, i.e., $B \gg 1$, and rely on the CPU to process the partial results. In contrast, the daisy-chain architecture, presented in [8], [9], directly outputs the detection results to the CPU, thus freeing the CPU from the detection process. Based on the daisy-chain architecture, the RLS detection algorithm operates as the traditional zero forcing (ZF) detection but in a distributed fashion. Nevertheless, this approach not only suffers from the high complexity and data bandwidth costs, but also confine to DUs equipped with only a single antenna, rendering it impractical in the most of cases of interest. Unfortunately, these issues persist in other detection methods, such as the stochastic gradient descent (SGD) and the averaged stochastic gradient descent (ASGD) detection schemes [8].

In this paper, we extend the distributed RLS detection to a more generalized one named as GRLS, which allows the deployment of multiple antennas in each DU. Then, by exploiting the channel hardening property in massive MIMO, those computationally expensive operations, such as matrix multiplication and inversion, in the last $C-C_{0}$ DUs in GRLS can be greatly simplified, resulting in remarkable reductions in both complexity and data bandwidth. Meanwhile, to ensure the convergence of GRLS, we also provide a convergence analysis concerning the choice of $C_{0}$. Furthermore, the complexity and data bandwidth of GRLS are given to validate its advantages over various existing distributed massive MIMO detection schemes. Finally, simulation results are provided to affirm its improved trade-off between performance and complexity, as well as its notable scalability to very large antenna arrays, i.e., XL-MIMO [10].

## II. RLS Detection Algorithm Based on Decentralized Daisy-Chain Architecture

Considering a massive MIMO scenario with $N$ antennas at the BS that serves $K$ single antenna users $(N \gg K)$, the input-output relation for the uplink is

$$
\begin{equation*}
\mathbf{y}=\mathbf{H} \mathbf{x}+\mathbf{n} \tag{1}
\end{equation*}
$$

Here, $\mathbf{y} \in \mathbb{C}^{N}$ is the received vector, $\mathbf{x} \in \mathcal{O}^{K}$ is the transmitted vector from the discrete QAM constellation $\mathcal{O}^{K}, \mathbf{H} \in \mathbb{C}^{N \times K}$ represents the Rayleigh fading channel matrix whose entries follow $\mathcal{C N}(0,1)$ and $\mathbf{n} \in \mathbb{C}^{N}$ denotes the addictive white Gaussian noise (AWGN) with mean $\mathbf{O}$ and covariance matrix $\sigma^{2} \mathbf{I}_{N}$. Given the system model in (1), the traditional linear detection methods, i.e., ZF and MMSE are presented as

$$
\begin{equation*}
\mathbf{x}_{\mathrm{ZF}}=\left(\mathbf{H}^{H} \mathbf{H}\right)^{-1} \mathbf{H}^{H} \mathbf{y} \tag{2}
\end{equation*}
$$

![](https://cdn.mathpix.com/cropped/f9a8916d-0c04-4741-87fe-835da85f3ff3-2.jpg?height=571&width=843&top_left_y=227&top_left_x=161)
Fig. 1. Illustration of a decentralized daisy-chain architecture with $C$ DUs. Each DU is equipped with $B=N / C$ antennas and an independent computing fabric for channel estimation (CHEST) and detection (DET), while quantization $(\mathcal{Q})$ is performed centrally.

$$
\begin{equation*}
\mathbf{x}_{\mathrm{MMSE}}=\left(\mathbf{H}^{H} \mathbf{H}+\sigma^{2} \mathbf{I}_{K}\right)^{-1} \mathbf{H}^{H} \mathbf{y}, \tag{3}
\end{equation*}
$$

where the final detection output $\widehat{\mathbf{x}}$ is acquired by quantizing $\widehat{\mathbf{x}}= \left\lceil\mathbf{x}_{\mathrm{ZF}}\right\rfloor_{\mathcal{Q}} \in \mathcal{O}^{K}$ or $\widehat{\mathbf{x}}=\left\lceil\mathbf{x}_{\text {MMSE }}\right\rfloor_{\mathcal{Q}} \in \mathcal{O}^{K}$. Theoretically, due to the favorable propagation in massive MIMO systems, the optimal maximum likelihood (ML) detection performance can be approximated by ZF or MMSE [1].

On the other hand, based on the daisy-chain architecture shown in Fig. 1, the RLS detection algorithm serves as a recursive version of ZF detection by [8]

$$
\begin{equation*}
\mathbf{x}_{c}=\mathbf{x}_{c-1}+\mathbf{P}_{c} \mathbf{h}_{c}^{H}\left(y_{c}-\mathbf{h}_{c} \mathbf{x}_{c-1}\right), \tag{4}
\end{equation*}
$$

where

$$
\begin{equation*}
\mathbf{P}_{c}=\mathbf{P}_{c-1}-\frac{\mathbf{P}_{c-1} \mathbf{h}_{c}^{H} \mathbf{h}_{c} \mathbf{P}_{c-1}^{H}}{1+\mathbf{h}_{c} \mathbf{P}_{c-1} \mathbf{h}_{c}^{H}} \in \mathbb{C}^{K \times K} \tag{5}
\end{equation*}
$$

is the weight matrix. Here, $\mathbf{h}_{c} \in \mathbb{C}^{1 \times K}, y_{c}$, and $\mathbf{x}_{c} \in \mathbb{C}^{K}$ refer to the local channel information, received signal, and estimated vector at the $c$-th DU, respectively.

However, the RLS detection method restricts each DU in daisy-chain to equip with only one single antenna, i.e., $B=1$, which severely limits its piratical applications. Moreover, the matrix multiplications in computing $\mathbf{P}_{c}$ in (5) also incur a high complexity cost. In addition, updating $\mathbf{x}_{c}$ on the $c$-th DU requires $\mathbf{P}_{c-1}$ and $\mathbf{x}_{c-1}$ from the previous DU, which accounts for the high data bandwidth consumption by conveying a $K \times K$ matrix and a $K \times 1$ vector, respectively.

## III. The Proposed GRLS Detection Algorithm

## A. Extension of the Traditional RLS Algorithm

We now extend the existing RLS detection algorithm to a more generalized one such that it allows for having multiple antennas at each DU over iterations as

$$
\begin{equation*}
\mathbf{x}_{c}=\mathbf{x}_{c-1}+\mathbf{P}_{c} \mathbf{H}_{c}^{H}\left(\mathbf{y}_{c}-\mathbf{H}_{c} \mathbf{x}_{c-1}\right), \tag{6}
\end{equation*}
$$

with

$$
\begin{equation*}
\mathbf{R}_{c}=\left(\mathbf{I}_{B}+\mathbf{H}_{c} \mathbf{P}_{c-1} \mathbf{H}_{c}^{H}\right)^{-1} \tag{7}
\end{equation*}
$$

and

$$
\begin{equation*}
\mathbf{P}_{c}=\mathbf{P}_{c-1}-\mathbf{P}_{c-1} \mathbf{H}_{c}^{H} \mathbf{R}_{c} \mathbf{H}_{c} \mathbf{P}_{c-1}^{H}, \tag{8}
\end{equation*}
$$

where $\mathbf{H}_{c} \in \mathbb{C}^{B \times K}$ and $\mathbf{y}_{c} \in \mathbb{C}^{B}$ with $B \geq 1$. Meanwhile, the weight matrix $\mathbf{P}_{c}$ is used to approximate $\left(\mathbf{H}_{\text {Acum }}^{H} \mathbf{H}_{\text {Acum }}\right)^{-1}$, while $\mathbf{H}_{\text {Acum }}= \left[\mathbf{H}_{1} ; \mathbf{H}_{2} ; \ldots ; \mathbf{H}_{c}\right] \in \mathbb{C}^{N_{c} \times K}$ denotes the accumulated channel information from the previous $N_{c}=c \times B$ received antennas. Note that matrix $\mathbf{H}_{\text {Acum }}$ is equivalent to $\mathbf{H}$ and $N_{c}$ is equal to $N$ when $c=C$. Furthermore, according to (6), (7), and (8), $\mathbf{x}_{c}$ can be reformulated as

$$
\begin{equation*}
\mathbf{x}_{c}=\left[\mathbf{P}_{0}^{-1}+\sum_{i=1}^{c} \mathbf{H}_{i}^{H} \mathbf{H}_{i}\right]^{-1}\left[\mathbf{P}_{0}^{-1} \mathbf{x}_{0}+\sum_{i=1}^{c} \mathbf{H}_{i}^{H} \mathbf{y}_{i}\right], \tag{9}
\end{equation*}
$$

which naturally leads to the following convergence result.
Theorem 1: Based on the iterations in (6), (7), and (8), $\mathbf{x}_{c}$ will gradually converge to the MMSE detection solution in (3) with the initial setup $\mathbf{x}_{0}=\mathbf{0}$ and $\mathbf{P}_{0}=\frac{1}{\sigma^{2}} \mathbf{I}_{K}$.

Concerning the least squares problem, the least absolute shrinkage and selection operator (LASSO) [11] and box-relaxation optimization (BRO) [12] methods can be applied for further improvement. However, as shown in (6), (7), and (8), each iteration of such an extension of RLS involves the complicated operations such as matrix multiplication and matrix inversion. In order to effectively reduce the computational complexity burden, we aim to incorporate the property of channel hardening into the iterations.

## B. Complexity Reduction by Adopting Channel Hardening

With $N \gg K$, the Gram matrix $\mathbf{H}^{H} \mathbf{H}$ is diagonally dominant due to channel hardening, which is one of the key properties in massive MIMO systems [1]. Here, since the weight matrix $\mathbf{P}_{c}$ is an approximation of the inverse of $\mathbf{H}_{\text {Acum }}^{H} \mathbf{H}_{\text {Acum }}$, it is supposed to be diagonally dominant as well when $c$ is sufficiently large, which inspires us to construct the matrix $\mathbf{P}_{c}$ only by its diagonal elements, i.e.,

$$
\begin{equation*}
\overline{\mathbf{P}}_{c}=\operatorname{diag}\left(\operatorname{diag}\left(\overline{\mathbf{P}}_{c-1}-\overline{\mathbf{P}}_{c-1} \mathbf{H}_{c}^{H} \overline{\mathbf{R}}_{c} \mathbf{H}_{c} \overline{\mathbf{P}}_{c-1}^{H}\right)\right) . \tag{10}
\end{equation*}
$$

Similarly, the matrix $\mathbf{R}_{c}$ in (7) can also be approximated as

$$
\begin{equation*}
\overline{\mathbf{R}}_{c}=\operatorname{diag}\left(\operatorname{diag}\left(\left(\mathbf{I}_{B}+\mathbf{H}_{c} \overline{\mathbf{P}}_{c-1} \mathbf{H}_{c}^{H}\right)^{-1}\right)\right) . \tag{11}
\end{equation*}
$$

Thanks to the diagonal structure of matrices $\overline{\mathbf{P}}_{c}$ and $\overline{\mathbf{R}}_{c}$, significant reductions in both computational complexity and data bandwidth can be achieved. On one hand, the computation of the matrix inversion is simplified as computing only the reciprocal of the diagonal elements, while the matrix multiplication is also simplified as only the diagonal elements need to be preserved. On the other hand, the $K \times K$ diagonal matrix $\overline{\mathbf{P}}_{c}$, which needs to convey by each DU, can be refined as a $K \times 1$ diagonal vector, thus greatly reducing the required data bandwidth.

## C. Accumulation of Channel Information

However, due to the daisy-chain architecture, the matrix $\mathbf{P}_{c}$ at the $c$-th DU only contains the information from the previous $N_{c}$ received antennas. As a result, the diagonal elements of $\mathbf{P}_{c}$ become dominant gradually with the increment of $c$, thus rendering the complexity reduction driven by channel hardening ineffective during the early stages in daisy-chain.

To address this issue, we divide the iterations of the proposed GRLS into two stages:

- The first $C_{0}$ DUs: Due to the lack of channel information for exploiting the channel hardening, perform the iteration in (6) based on $\mathbf{R}_{c}$ in (7) and $\mathbf{P}_{c}$ in (8).
- The rest of $C-C_{0}$ DUs: Based on the accumulated channel information for channel hardening, perform the iteration in (6) based on $\overline{\mathbf{R}}_{c}$ in (11) and $\overline{\mathbf{P}}_{c}$ in (10).

```
Algorithm 1: The Proposed GRLS Detection Algorithm.
Input: $\mathbf{y}_{c}, \mathbf{H}_{c}, c=1,2, \cdots C, \sigma^{2}, \beta$ and $C_{0}$
Output: estimated transmit signal $\widehat{\mathbf{x}}$
    Initialize: $\mathbf{x}_{0}=\mathbf{0}, \mathbf{P}_{0}=\frac{1}{\sigma^{2}} \mathbf{I}_{K}$
    for $c=1,2, \ldots, C_{0}$ do
        $\mathbf{R}_{c}=\left(\mathbf{I}_{B}+\mathbf{H}_{c} \mathbf{P}_{c-1} \mathbf{H}_{c}^{H}\right)^{-1}$
        $\mathbf{P}_{c}=\mathbf{P}_{c-1}-\mathbf{P}_{c-1} \mathbf{H}_{c}^{H} \mathbf{R}_{c} \mathbf{H}_{c} \mathbf{P}_{c-1}^{H}$
        $\mathbf{x}_{c}=\mathbf{x}_{c-1}+\mathbf{P}_{c} \mathbf{H}_{c}^{H}\left(\mathbf{y}_{c}-\mathbf{H}_{c} \mathbf{x}_{c-1}\right)$
        if $c=C_{0}$ then
            $\overline{\mathbf{R}}_{c}=\operatorname{diag}\left(\operatorname{diag}\left(\mathbf{R}_{c}\right)\right)$
            $\overline{\mathbf{P}}_{c}=\operatorname{diag}\left(\operatorname{diag}\left(\mathbf{P}_{c}\right)\right)$
        end if
    end for
    for $c=C_{0}+1, C_{0}+2 \cdots, C$ do
        $\overline{\mathbf{R}}_{c}=\operatorname{diag}\left(\operatorname{diag}\left(\left(\mathbf{I}_{B}+\mathbf{H}_{c} \overline{\mathbf{P}}_{c-1} \mathbf{H}_{c}^{H}\right)^{-1}\right)\right)$
        $\overline{\mathbf{P}}_{c}=\operatorname{diag}\left(\operatorname{diag}\left(\overline{\mathbf{P}}_{c-1}-\overline{\mathbf{P}}_{c-1} \mathbf{H}_{c}^{H} \overline{\mathbf{R}}_{c} \mathbf{H}_{c} \overline{\mathbf{P}}_{c-1}^{H}\right)\right)$
        $\mathbf{x}_{c}=\mathbf{x}_{c-1}+(1-\beta)\left(\overline{\mathbf{P}}_{c} \mathbf{H}_{c}^{H}\left(\mathbf{y}_{c}-\mathbf{H}_{c} \mathbf{x}_{c-1}\right)\right)$
    end for
    output $\widehat{\mathbf{x}}=\left\lceil\mathbf{x}_{C}\right\rfloor_{\mathcal{Q}} \in \mathcal{O}^{K}$
```

In addition, for better detection performance, the technique of damping factor $\beta \in(0,1)$ (i.e., here we use $\beta=0.1$ ) is also introduced to the second stage by

$$
\begin{equation*}
\mathbf{x}_{c}=\beta \mathbf{x}_{c-1}+(1-\beta) \mathbf{x}_{c} . \tag{12}
\end{equation*}
$$

Finally, at the CPU, the detected signal

$$
\begin{equation*}
\widehat{\mathbf{x}}=\left\lceil\mathbf{x}_{C}\right\rfloor_{\mathcal{Q}} \in \mathcal{O}^{K} \tag{13}
\end{equation*}
$$

is outputted as the detection solution of GRLS.
Based on the daisy-chain architecture, the GRLS algorithm employs local processing of data where it is generated to avoid the additional overhead for transmission and storage. Furthermore, leveraging its sequential, regular, and modular structure, extending GRLS to larger antenna arrays can be easily achieved by increasing the number of DUs, which demonstrates its excellent scalability.

To summarize, the proposed general recursive least square (GRLS) detection algorithm for distributed uplink massive MIMO systems is outlined in Algorithm 1.

## IV. Convergence Analysis

Undoubtedly, how to reasonably set the parameter $C_{0}$ is the key to GRLS. In what follows, we provide the convergence analysis with respect to the choice of $C_{0}$.

Lemma 1: For the flat Rayleigh fading matrix $\mathbf{H}_{c} \in \mathbb{C}^{B \times K}$ whose entries follow $\mathcal{C} \mathcal{N}(0,1)$, it follows that

$$
\begin{equation*}
\mathbf{A}_{c}=\mathrm{E}\left[\mathbf{H}_{c}^{H} \mathbf{H}_{c}\right]=B \mathbf{I}_{K} . \tag{14}
\end{equation*}
$$

Proof: To start with, let $h_{m n}$ denote the element in the $m$-th row and $n$-th column of matrix $\mathbf{H}_{c}$. Meanwhile, define $\mathbf{D}_{c}=\mathbf{H}_{c}^{H} \mathbf{H}_{c}$ with its elements $d_{m n}=\sum_{l=1}^{B} h_{l m}^{*} h_{l n}$. Then, in the case of $m=n$, we can find that $h_{l m}^{*} h_{l m}=\Re\left(h_{l m}\right)^{2}+\Im\left(h_{l m}\right)^{2}$, while $\Re\left(h_{l m}\right)^{2}$ and $\Im\left(h_{l m}\right)^{2}$ both follow the Gamma distribution with the shape parameter $\alpha=0.5$ and the scale parameter $\gamma=1[13]$ (i.e., $\Re(\cdot)$ and $\Im(\cdot)$ denote the real and imaginary parts, respectively), namely,

$$
\begin{equation*}
h_{l m}^{*} h_{l m} \sim \Gamma(0.5,1)+\Gamma(0.5,1)=\Gamma(1,1) . \tag{15}
\end{equation*}
$$

Building upon it, $d_{m m}$, as the summation of $h_{l m}^{*} h_{l m}$, obeys the following distribution

$$
\begin{equation*}
d_{m m}=\sum_{l=1}^{B} h_{l m}^{*} h_{l m} \sim \Gamma(B, 1) . \tag{16}
\end{equation*}
$$

Subsequently, in the case of $m \neq n, h_{l m}$ and $h_{l n}$ are independent entries with mean zero, and this leads to

$$
\mathrm{E}\left[d_{m n}\right]= \begin{cases}B & \text { if } m=n,  \tag{17}\\ 0 & \text { if } m \neq n,\end{cases}
$$

which completes the proof. $\square$

Theorem 2: The proposed GRLS detection algorithm for the distributed massive MIMO systems converges when

$$
\begin{equation*}
C_{0} \geq\left\lfloor\left(\sqrt{\frac{B}{2}}+\sqrt{K}\right)^{2} / B\right\rfloor, \tag{18}
\end{equation*}
$$

where $\lfloor x\rfloor$ rounds to the closest integer smaller than or equal to $x$.
Proof: According to Theorem 1, the convergence of the first stage about the first $C_{0}$ DUs in GRLS is guaranteed unconditionally. Therefore, we pay our attentions on the convergence of the second stage for the rest of $C-C_{0}$ DUs.

In particular, we can express the error in the second stage (i.e., $c> C_{0}$ ) as

$$
\begin{align*}
\mathbf{e}_{C} & =\mathbf{x}_{C}-\mathbf{x}_{\mathrm{MMSE}} \\
& =\mathbf{x}_{C-1}+\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H}\left(\mathbf{y}_{C}-\mathbf{H}_{C} \mathbf{x}_{C-1}\right)-\mathbf{x}_{\mathrm{MMSE}} \\
& =\left(\mathbf{I}_{K}-\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H} \mathbf{H}_{C}\right)\left(\mathbf{x}_{C-1}-\mathbf{x}_{\mathrm{MMSE}}\right)+\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H}\left(\mathbf{y}_{C}-\mathbf{H}_{C} \mathbf{x}_{\mathrm{MMSE}}\right) \\
& =\left(\mathbf{I}_{K}-\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H} \mathbf{H}_{C}\right) \mathbf{e}_{C-1}+\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H} \mathbf{n}_{C} \tag{19}
\end{align*}
$$

Moreover, given the fact that $\mathbf{H}_{c}$ is statistically independent of $\overline{\mathbf{P}}_{c}$ and $\mathbf{e}_{c}$, then based on (14) in Lemma 1, by taking expectation on (19), we have

$$
\begin{align*}
\mathrm{E}\left[\mathbf{e}_{C}\right] & =\mathrm{E}\left[\left(\mathbf{I}_{K}-\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H} \mathbf{H}_{C}\right) \mathbf{e}_{C-1}\right]+\mathrm{E}\left[\overline{\mathbf{P}}_{C} \mathbf{H}_{C}^{H} \mathbf{n}_{C}\right] \\
& =\left(\mathbf{I}_{K}-\overline{\mathbf{P}}_{C} \mathbf{A}_{C}\right) \mathrm{E}\left[\mathbf{e}_{C-1}\right] \\
& \triangleq \prod_{c=C_{0}+1}^{C} \mathbf{F}_{c} \mathrm{E}\left[\mathbf{e}_{C_{0}}\right] \tag{20}
\end{align*}
$$

where $\mathbf{F}_{c} \triangleq \mathbf{I}_{K}-B \overline{\mathbf{P}}_{c} \in \mathbb{C}^{K \times K}$ is the iteration matrix. Then, to guarantee the convergence of (20) for diminishing the error over the iterations, the spectral radius of $\mathbf{F}_{c}$ should be smaller than 1 [14], namely,

$$
\begin{equation*}
\rho\left(\mathbf{F}_{c}\right)=\max _{1 \leq k \leq K}\left|\lambda_{k}\left(\mathbf{F}_{c}\right)\right|=\max _{1 \leq k \leq K}\left|1-B \lambda_{k}\left(\overline{\mathbf{P}}_{c}\right)\right|<1, \tag{21}
\end{equation*}
$$

where $\lambda_{k}(\cdot)$ denotes the $k$-th eigenvalue. Since the matrix $\overline{\mathbf{P}}_{c}$ is approximated to the inverse of a positive-definite matrix $\mathbf{H}_{\text {Acum }}^{H} \mathbf{H}_{\text {Acum }}$, its eigenvalues are all larger than $0[1]$, which implies that the condition in (21) can be further expressed by

$$
\begin{equation*}
\lambda_{\max }\left(\overline{\mathbf{P}}_{c}\right)<\frac{2}{B} . \tag{22}
\end{equation*}
$$

On the other hand, at the $c$-th DU, $\lambda_{\text {min }}\left(\left(\mathbf{H}_{\text {Acum }}^{H} \mathbf{H}_{\text {Acum }}\right)^{-1}\right)$ approaches $N_{c}\left(1-\sqrt{K / N_{c}}\right)^{2}$ with $N_{c} \gg K$ [14] such that the following approximation holds

$$
\begin{equation*}
\lambda_{\max }\left(\overline{\mathbf{P}}_{c}\right) \approx \frac{1}{\lambda_{\min }\left(\left(\mathbf{H}_{\text {Acum }}^{H} \mathbf{H}_{\text {Acum }}\right)^{-1}\right)} \approx \frac{1}{N_{c}\left(1-\sqrt{\frac{K}{N_{c}}}\right)^{2}} . \tag{23}
\end{equation*}
$$

TABLE I
Computation Complexity Comparison of Decentralized Algorithms
| Algorithm | Number of complex multiplications | Averaged complex values transferred on each link |  | $256 \times 16$ Complexity | system Bandwidth | $256 \times 32$ system |  |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ADMM [3] | $\left(2 K^{2} B+K B+K+0.5 K^{3}\right) C+\left(\left(K^{2}+2 K\right) C+K\right) T$ | $(2 T-1) K$ |  | 158640 | 80 | 690016 | 160 |
| CG [3] | $\left(K^{2} B+K B\right) C+\left(K^{2}+7 K\right) C T-4 K C$ | $(2 T+2) K$ |  | 77952 | 128 | 299264 | 256 |
| EPA [4] | $((8 \mathcal{O}+2 K+1) N K I+5 \mathcal{O} K) T+N K+\mathcal{O}$ | $(2 T-1) K$ |  | 5943056 | 80 | 14245392 | 160 |
| FD-MMSE [5] | $\left(K^{2} B+K B+3.5 K^{3}+K^{2}+4 K\right) C$ | 2K |  | 186880 | 32 | 1197056 | 64 |
| GMP [6] | $(8 \mathcal{O}+2 K+1) N K I+N K+6 \mathcal{O} K$ | $2 K$ |  | 1984000 | 32 | 4754432 | 64 |
| DN [7] | $\left(K^{2} B+K B+K\right) C+\left(K^{2} C+K\right) T$ | Ring: $2 K T+4 K T / C$ |  | 75952 | 160 | 295264 | 320 |
| RLS [8] | $\left(3 K^{2}+4 K+1\right) N$ | $K^{2}+K$ |  | 213248 | 272 | 819456 | 1056 |
| SGD [8] | $(2 K+1) N$ | $K$ |  | 8448 | 16 | 16640 | 32 |
| ASGD [8] | $(2 K+1) k_{0}+(3 K+1)\left(N-k_{0}\right)$ | $2 K$ |  | 10496 | 32 | 20736 | 64 |
|  |  |  | $C_{\text {min }}$ : | 51972 | 58 | 210000 | 250 |
| Proposed GRLS | $\left(3 K^{2} B+2 K B^{2}+2 K B+0.5 B^{3}\right) C_{0}+(7 K B+B)\left(C-C_{0}\right)$ | $\left(\left(K^{2}+K\right) C_{0}+2 K\left(C-C_{0}\right)\right) / C$ | $2 \times C_{\text {min }}$ : | 75016 | 84 | 362404 | 436 |
|  |  |  | $3 \times C_{\text {min }}$ : | 98060 | 110 | 514800 | 622 |


Therefore, by substituting (23) into (22), we arrive at the following convergence requirement

$$
\begin{equation*}
N_{c}>\left(\sqrt{\frac{B}{2}}+\sqrt{K}\right)^{2} . \tag{24}
\end{equation*}
$$

To satisfy (24) with $N_{c}=c \times B$ for $c=C_{0}+1, C_{0}+2, \ldots, C$, we get the following condition

$$
\begin{equation*}
C_{0} \geq\left\lceil\frac{N_{c}}{B}-1\right\rceil=\left\lfloor\left(\sqrt{\frac{B}{2}}+\sqrt{K}\right)^{2} / B\right\rfloor, \tag{25}
\end{equation*}
$$

completing the proof. $\square$

According to Theorems 1 and 2, it is evident that the proposed GRLS offers a flexible trade-off between the detection performance and complexity reduction, where a better detection performance can be obtained with the increment of $C_{0}$ at the expense of computational complexity. When $C_{0}=C$, GRLS will exactly output the performance of MMSE detection.

## V. Complexity and Data Bandwidth Analysis

We now study the complexity and data bandwidth of the proposed GRLS algorithm for distributed detection in massive MIMO, where the computational complexity is evaluated in terms of the required number of complex multiplications [4]. For example, computing the inversion of a $K \times K$ complex-valued matrix demands complexity $0.5 K^{3}[15]$.

In particular, the computational complexity of GRLS consists of two parts. As for the first stage (i.e., $c \leq C_{0}$ ), computing $\mathbf{R}_{c}$ involves matrix multiplications between $\mathbf{P}_{c-1} \in \mathbb{C}^{K \times K}$ and $\mathbf{H}_{c}^{H} \in \mathbb{C}^{K \times B}$, between $\mathbf{H}_{c} \in \mathbb{C}^{B \times K}$ and $\mathbf{P}_{c-1} \mathbf{H}_{c}^{H} \in \mathbb{C}^{K \times B}$, and a $B \times B$ matrix inversion, which corresponds to complexity $K^{2} B+K B^{2}+0.5 B^{3}$. Similarly, the complexities of computing $\mathbf{P}_{c}$ and $\mathbf{x}_{c}$ are $K^{2} B+K B^{2}$ and $K^{2} B+ 2 K B$, respectively.

On the other hand, as for the second stage (i.e., $c>C_{0}$ ), the matrix multiplications between $\overline{\mathbf{P}}_{c-1}$ and $\mathbf{H}_{c}^{H}$, and between $\mathbf{H}_{c}$ and $\overline{\mathbf{P}}_{c-1} \mathbf{H}_{c}^{H}$ in (11) only need to take the diagonal elements into account, resulting in complexity $2 K B$. Subsequently, the inversion operation requires the complexity $B$ since it only involves calculating the reciprocals of the diagonal elements. The complexities of (11), (10), and (6) are reduced to $2 K B+B, 2 K B$, and $3 K B$, respectively.

To summarize, the total computational complexity of GRLS is $\left(3 K^{2} B+2 K B^{2}+2 K B+0.5 B^{3}\right) C_{0}+(7 K B+B)\left(C-C_{0}\right)$. For ease of illustration, the complexity comparison is shown in Table I. Throughout the context, the numbers of DUs of RLS, SGD, and ASGD algorithms in [8] are set to $C=N$ due to the restriction $B=1$, and the ADMM, CG, EPA, FD-MMSE, GMP, and DN algorithms in [3], [4], [5], [6], [7] with $C=8$ are applied as the comparison, which corresponds to $B=N / 8$ in each DU. As recommended in [8], the step-size of SGD is configured at 0.03 and the onset of the averaging procedure in ASGD is set to $k_{0}=N / 2$. Meanwhile, the numbers of inner iterations for EPA and GMP algorithms and the numbers of outer iterations for ADMM, CG, EPA, and DN algorithms are set to $I=3$ and $T=3$, respectively. From Table I, the proposed GRLS algorithm exhibits a much lower computational complexity than other schemes except the simple SGD and ASGD algorithms. More precisely, compared to the traditional RLS algorithm, more than $75 \%$ complexity is reduced for the case of $256 \times 16$, where $B=4, C=64$, and $C_{0}=7$, the minimum value in (18), are employed in GRLS, making it highly suitable for practical hardware implementation.

As summarized in Table I, the data bandwidth for interconnection of these distributed massive MIMO detection schemes is determined by the averaged complex values transferred on each link (e.g., $K$ for SGD algorithm), which means the actual overhead in interface and may restricts its applications in practice [8]. Intuitively, GRLS achieves the comparable data bandwidth to the simple SGD and ASGD algorithms, along with a $78 \%$ reduction compared to the traditional RLS algorithm in the case of $256 \times 16$. Moreover, for the $256 \times 32$ scenario, while GRLS requires more data bandwidth, it still brings a reduction of $76 \%$ over RLS, making it more easily accommodated by existing hardware interfaces.

## VI. Simulation

In this section, for a better illustration of the iteration convergence of the proposed GRLS algorithm, we first verify the effectiveness of the setting of parameter $C_{0}$ in Theorem 2. Then we compare GRLS with other distributed detection methods in bit error rate (BER) performance. Finally, we assess the performance of the GRLS across varying system sizes to evaluate its scalability. In all simulations, we consider the 16QAM modulation scheme and uncoded systems.

Fig. 2 illustrates the convergence performance of the proposed GRLS detection algorithm under different antenna configurations at each DU

![](https://cdn.mathpix.com/cropped/f9a8916d-0c04-4741-87fe-835da85f3ff3-5.jpg?height=504&width=1793&top_left_y=212&top_left_x=126)
Fig. 2. GRLS detection algorithm convergence with SNR $=2 \mathrm{~dB}$ for the uncoded $256 \times 16$ massive MIMO. (a) $B=1, C=256$. (b) $B=2, C=128$. (c) $B=4, C=64$.

![](https://cdn.mathpix.com/cropped/f9a8916d-0c04-4741-87fe-835da85f3ff3-5.jpg?height=635&width=850&top_left_y=910&top_left_x=141)
Fig. 3. BER performance comparison of different methods for the uncoded $256 \times 16$ massive MIMO.

for $256 \times 16$ massive MIMO systems at signal-to-noise ratio (SNR) $=2 \mathrm{~dB}$. As can be seen clearly, when $C_{0}$ exceeds the minimum value in Theorem $2\left(C_{\text {min }}\right)$, the GRLS detection algorithm converges rapidly and achieves the near MMSE performance. It is worth noting that as $C_{0}$ increases to $C$, GRLS works as the MMSE detection solution, which is in line with the result derived in Theorem 1.

The BER performance comparison between GRLS and other distributed detection schemes, employed the same parameters as Section V, is presented in Fig. 3 with respect to a $256 \times 16$ massive MIMO system. Despite their extremely high computational complexity and data bandwidth, the EPA and RLS algorithms achieve the MMSE performance. Also, the ADMM and CG detection schemes incur a slight performance loss over the centralized MMSE detection but at a substantial data bandwidth cost. Due to the high scattering of BS antennas, the local estimation results obtained by FD-MMSE, GMP, and DN algorithms are inaccurate, resulting in significant performance degradation. Besides, the SGD and ASGD algorithms require quite low computational complexity and data bandwidth, making it easy to apply, but their performance decreases at about 7.0 dB and 3.5 dB over the centralized MMSE detection, respectively. Note that the proposed GRLS detection algorithm with $C_{\text {min }}$ outperforms CG, DN, FD-MMSE,

![](https://cdn.mathpix.com/cropped/f9a8916d-0c04-4741-87fe-835da85f3ff3-5.jpg?height=635&width=848&top_left_y=910&top_left_x=1054)
Fig. 4. BER performance comparison of different methods for the uncoded $256 \times 32$ massive MIMO.

and GMP detection schemes at a lower cost while achieving near MMSE performance with the increment of $C_{0}$.

In Fig. 4, we extend the BER performance comparison to a $256 \times 32$ massive MIMO system. Intuitively, all the convergence performance of FD-MMSE, GMP, and DN algorithms degrades further, leading to unsatisfactory detection performance in uplink massive MIMO systems. This is attributed to the fact that the limited number of antenna resources in each DU fails to satisfy the condition $B \gg K$. In contrast, the convergence of GRLS works well as expected, because its convergence always hold if (18) is satisfied. Clearly, with the increment of $C_{0}$, the BER performance of GRLS improves gradually. For example, the proposed GRLS detection algorithm with two and three times $C_{\text {min }}$ achieves gains of nearly 1.5 dB and 2.0 dB over that with $C_{\text {min }}$ at the BER of $10^{-5}$, respectively. However, it also leads to a rise in computational complexity and data bandwidth costs by $72 \%$ and $74 \%$ for $2 \times C_{\text {min }}$, and $145 \%$ and $148 \%$ for $3 \times C_{\text {min }}$, as indicated in Table I, respectively. In summary, a larger $C_{0}$ brings considerable performance gains but with higher complexity and bandwidth cost such that it should be selected according to the practical implementation requirement.

In Fig. 5, to illustrate the scalability of our proposed GRLS algorithm, we scale the total number of BS antennas $N=C \times B$ by increasing the number of DU from $C=128, C=192$, to $C=256$ with fixed

![](https://cdn.mathpix.com/cropped/f9a8916d-0c04-4741-87fe-835da85f3ff3-6.jpg?height=637&width=848&top_left_y=227&top_left_x=156)
Fig. 5. BER performance of the GRLS algorithm with a fixed number of users $K=64$.

$B=4$. As can be seen clearly, GRLS consistently exhibits near-MMSE performance, suggesting its effectiveness and scalability in distributed massive MIMO systems.

## VII. Conclusion

In this paper, by exploiting the potential of the RLS detection algorithm, we proposed a novel near-MMSE algorithm, termed GRLS, for distributed massive MIMO detection with low computational complexity and data bandwidth. The convergence, complexity, and bandwidth analysis for the proposed GRLS detection algorithm are also provided. When the derived convergence condition about $C_{0}$ is satisfied, the proposed GRLS achieves rapid convergence and is capable of attaining the near MMSE performance. Additionally, the simulation results not only confirm its desirable trade-off between complexity and performance but also validate its excellent scalability, making it well-suited for practical implementations.

## References

[1] M. A. Albreem, M. Juntti, and S. Shahabuddin, "Massive MIMO detection techniques: A survey," IEEE Commun. Surveys Tuts., vol. 21, no. 4, pp. 3109-3132, Fourth Quarter 2019.
[2] K. Li, Y. Chen, R. Sharan, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized data detection for massive MU-MIMO on a Xeon Phi cluster," in Proc. IEEE 50th Conf. Rec. Asilomar Conf. Signals Syst. Comput., 2016, pp. 468-472.
[3] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[4] Z. Zhang, H. Li, Y. Dong, X. Wang, and X. Dai, "Decentralized signal detection via expectation propagation algorithm for uplink massive MIMO systems," IEEE Trans. Veh. Technol., vol. 69, no. 10, pp. 11233-11240, Oct. 2020.
[5] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
[6] Z. Zhang, Y. Dong, K. Long, X. Wang, and X. Dai, "Decentralized baseband processing with Gaussian message passing detection for uplink massive MU-MIMO systems," IEEE Trans. Veh. Technol., vol. 71, no. 2, pp. 2152-2157, Feb. 2022.
[7] A. Kulkarni, M. A. Ouameur, and D. Massicotte, "Hardware topologies for decentralized large-scale MIMO detection using newton method," IEEE Trans. Circuits Syst., vol. 68, no. 9, pp. 3732-3745, Sep. 2021.
[8] J. R. Sanchez, F. Rusek, M. Sarajlic, O. Edfors, and L. Liu, "Fully decentralized massive MIMO detection based on recursive methods," in Proc. IEEE Workshop Signal. Process. Syst. Des. Implement., 2018, pp. 53-58.
[9] J. R. Snchez, F. Rusek, O. Edfors, M. Sarajlic, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms," IEEE Trans. Signal Process., vol. 68, pp. 687-700, 2020.
[10] Z. Wang, J. Zhang, and H. Du, "Extremely large-scale MIMO: Fundamentals, challenges, solutions, and future directions," IEEE Wireless Commun., early access, Apr. 10, 2023, doi: 10.1109/MWC.132.2200443.
[11] A. Bereyhi, S. Asaad, B. Gade, R. R. Muller, and H. V. Poor, "Detection of spatially modulated signals via RLS: Theoretical bounds and applications," IEEE Trans. Wireless Commun., vol. 21, no. 4, pp. 2291-2304, Apr. 2022.
[12] C. Thrampoulidis, W. Xu, and B. Hassibi, "Symbol error rate performance of box-relaxation decoders in massive MIMO," IEEE Trans. Signal Process., vol. 66, no. 13, pp. 3377-3392, Jul. 2018.
[13] A. Papoulis, Probability, Random Variables, and Stochastic Processes, 4th ed. New York, NY, USA: McGraw-Hill, Dec. 2002.
[14] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays," IEEE Signal Process Mag., vol. 30, no. 1, pp. 40-60, Jan. 2013.
[15] A. Krishnamoorthy and D. Menon, "Matrix inversion using Cholesky decomposition," in Proc. IEEE Signal Process. Algorithms, Architectures, Arrangements, Appl. Conf., 2013, pp. 70-72.


[^0]:    Manuscript received 10 August 2023; revised 15 December 2023; accepted 22 February 2024. Date of publication 18 March 2024; date of current version 15 August 2024. This work was supported in part by the National Natural Science Foundation of China under Grant 62371124 and Grant 62371037, and in part by ZTE Industry-University-Institute Cooperation Funds under Grant HC-CN20200628010. The review of this article was coordinated by Prof. Gabriella Olmo. (Corresponding author: Zheng Wang.)

    Qiqiang Chen and Zheng Wang are with the School of Information Science and Engineering, Southeast University, Nanjing 210096, China (e-mail: wznuaa@gmail.com).

    Cong Ma is with the ZTE Corporation, Shenzhen 518057, China (e-mail: 1192403915@qq.com).

    Xiaoming Dai is with the University of Science and Technology Beijing, Beijing 100083, China (e-mail: daixiaoming@ustb.edu.cn).

    Derrick Wing Kwan Ng is with the School of Electrical Engineering and Telecommunications, University of New South Wales, Sydney, NSW 2052, Australia (e-mail: w.k.ng @ unsw.edu.au).

    Digital Object Identifier 10.1109/TVT.2024.3370611

