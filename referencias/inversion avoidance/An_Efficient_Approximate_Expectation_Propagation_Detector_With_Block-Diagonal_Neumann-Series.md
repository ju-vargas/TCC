# An Efficient Approximate Expectation Propagation Detector With Block-Diagonal Neumann-Series 

Huizheng Wang ${ }^{(1)}$, Bingyang Cheng ${ }^{(1)}$, Student Member, IEEE, Xiaosi Tan ${ }^{(1)}$, Member, IEEE Xiaohu You ${ }^{(D)}$, Fellow, IEEE, and Chuan Zhang ${ }^{(D)}$, Senior Member, IEEE


#### Abstract

Expectation propagation (EP) achieves near-optimal performance for large-scale multiple-input multiple-output (L-MIMO) detection, however, at the expense of unaffordable matrix inversions. To tackle the issue, several low-complexity EP detectors have been proposed. However, they all fail to exploit the properties of channel matrices, thus resulting in unsatisfactory performance in non-ideal scenarios. To this end, in this paper, a block-diagonal Neumann-series-based expectation propagation approximation (BD-NS-EPA) algorithm is proposed, which is applicable for both ideal uncorrelated channels and the correlated channels with multiple-antenna user equipment system. First, a block-diagonal-based Neumann iteration is employed, which skillfully exerts the main information of the channels while reducing computational cost. An adjustable sorting message updating scheme then is introduced to reduce the update of redundant nodes during iterations. Numerical results show that, for $128 \times 32$ MIMO with the non-ideal channel, the proposed algorithm exhibits 0.3 dB away from the original EP when bit error-rate $(\mathrm{BER})=10^{-3}$, at the cost of mere $3 \%$ normalized complexity. The implementation results on SMIC $65-\mathrm{nm}$ CMOS technology suggest that the proposed detector can achieve $1.252 \mathrm{Gbps} / \mathrm{W}$ and $0.275 \mathrm{Mbps} / \mathrm{kGE}$ hardware efficiency, further demonstrating that the proposed detectors can achieve a good trade-off between error-rate performance and hardware efficiency.


Index Terms-Large-scale MIMO, expectation propagation, block-diagonal matrix, Neumann-series approximation, VLSI.

## I. Introduction

LARGE-SCALE multiple-input multiple-output (L-MIMO), as an emerging technology to meet the higher data rate demand, is one of the key technologies for the fifth generation wireless communication system [1]. This technique is proposed to equip a base station (BS) with a massive antenna array (in the order of hundreds or thousands) and simultaneously serve a relatively small

Manuscript received 27 February 2022; revised 19 May 2022, 7 July 2022, and 29 August 2022; accepted 7 October 2022. Date of publication 25 January 2023; date of current version 27 February 2023. This work was supported in part by the National Key Research and Development Program of China under Grant 2020YFB2205503, in part by the NSFC under Grant 62122020 and Grant 61871115, in part by the Jiangsu Provincial NSF under Grant BK20211512, in part by the Major Key Project of Pengcheng Laboratory under Grant PCL2021A01-2, and in part by the Fundamental Research Funds for the Central Universities. This article was recommended by Associate Editor J. Lota. (Corresponding author: Chuan Zhang.)

The authors are with the LEADS, the National Mobile Communications Research Laboratory, and the Frontiers Science Center for Mobile Information Communication and Security, Southeast University, Nanjing 211189, China, and also with Purple Mountain Laboratories, Nanjing 211189, China (e-mail: chzhang @ seu.edu.cn).

Color versions of one or more figures in this article are available at https://doi.org/10.1109/TCSI.2022.3229690.

Digital Object Identifier 10.1109/TCSI.2022.3229690
number of user equipments (UEs) in the same time-frequency resource [2]. Many advantages, including better reliability, spectral efficiency and energy efficiency, can be obtained by increasing the antenna array dimension [3]. Unfortunately, the benefits of L-MIMO come at the expense of significantly increase computational complexity in BS side [1]. One of the most vital issues is the low complexity detection algorithm in both uplink and downlink directions, since the presence of numerous antennas requires detection algorithms that can scale favorably to high dimension [3].

In the L-MIMO system, conventional optimal detectors, such as maximum-likelihood (ML) detector, suffer prohibitive computational cost due to the increasing system size [4]. In contrast, some sub-optimal linear detectors such as minimum mean square error (MMSE) [5], [6] and zero-forcing (ZF) [7] successfully alleviate the computational burden and are relatively simpler to implement, but exhibit performance far from satisfying. For an MIMO system with $M$ transmitting antennas and $N$ receiving antennas, the linear detectors deliver near-optimal performance when loading factor $\alpha \ll 1\left(\alpha=\frac{M}{N}\right)$. However, in practice, systems with loading factor $\alpha$ close to 1 can contribute higher spectral efficiency, while the performance of linear detectors degrades evidently under these configurations. Therefore, to further improve the spectral efficiency, a detection algorithm that can tackle flexible antenna configurations effectively is still entailed.

Recently, based on Bayesian inference theory, graph-based message passing detectors (MPDs) such as channel-hardening exploiting message passing (CHEMP) [8], large-MIMO approximate message passing (LAMA) [9] and belief propagation (BP) [10] are proposed, which can exhibit superior performance compared to the linear detectors with strong robustness. However, the factor graph (FG) of MIMO is fully connected, which means there are lots of short loops especially for large loading factors. As a result, the MIMO BP detectors exhibit severe performance degradation as $\alpha$ goes to 1 .

Expectation propagation (EP) is firstly considered for MIMO detection in [11] named EP-based detector (EPD) and exhibits superior with near optimal performance for all kinds of antenna configurations, among various MIMO detection algorithms. As introduced in [11], EPD outstrips the aforementioned detectors such as BP with lower complexity and acquires stronger robustness regarding antenna and modulation configurations. Profiting from these advantages, recently, various extensions and modifications of EPD are proposed [12], [13]. Furthermore, the moment matching methodology in EPD is also utilized to derive and enhance the approximate message passing (AMP) for MIMO detections [14].

However, one critical drawback still lying in EPD blames the explicit matrix inversion in each iteration, thus leading
to $\mathcal{O}\left(L M^{3}\right)$ complexity, where $L$ denotes the number of iterations. This will result in an unaffordable computational burden as the system size grows and thus hinder its efficient implementation in practice. More unfortunately, some foremost linear iterative solvers for MMSE detection, including Gauss-Seidel [15] and conjugate gradient [16], are impotent to relieve the computational burden, as they cannot provide an estimation of the needed covariance matrix.

To address the complexity issue, several low-complexity versions of EPD have been proposed. By substituting the matrix inversion in each iteration with an approximation with Neumann-series, an EP detector with Neumann-series approximation (EP-NSA) is proposed in [17], which can exhibit satisfying performance with $\alpha \ll 1$ while maintaining reduced complexity. Further, based on the EP-NSA, an improved version named EP-INSA is proposed in [18], which introduces an approximation to avoid exponentiations, making the algorithm more hardware-friendly. Additionally, in [19], an EP-successive updating (EP-SU) detector is proposed to eliminate the matrix inversion by Sherman-Morrison formula. Further, to improve the efficiency of EP-SU, authors in [20] proposes a sorting updating method to distinguishably update different posterior distributions of the transmitted symbols and a sphere search aided scheme to reduce the calculation space, when calculating the probability density of approximated Gaussian distribution for every transmitted symbol in constellation space. Unfortunately, computational savings gained by these methods are limited since the complexity of $\mathcal{O}\left(L M^{3}\right)$ is still required to achieve satisfying performance. Instead of straightforward substitution of inverse matrices, an EP with approximation (EPA) detector is proposed in [21], which reformulates the EP moment matching equations and successfully simplifies the sequential updating process, hence avoiding iterative matrix inversions. Further, based on EPA, [22] employs a weighted NSA (EP-wNSA) to enhance the convergence and approximation accuracy for the iterations of solving matrix inversion.

It is worth mentioning that most of the works mentioned above aim at single-antenna user equipment (SAUE) system and assume that the entries of channel matrix are independent and identically distributed (i.i.d.) and follow the standard Gaussian distribution. Unfortunately, in practical system-scenarios, an UE usually equips several antennas and the transmitting vectors from one UE are correlated generally since the antennas of the same UE are insufficiently separated due to the space limitation [23]. The spatial correlation between antennas plays a vital role in influencing the performance of L-MIMO systems, for the number of antennas soars to an unprecedented magnitude [1]. However, to the best of the authors' knowledge, for the scenarios in less favorable propagation environment where channels are of high correlation and each UE is equipped with multiple antennas, the studies in low-complexity EP detectors and its efficient hardware implementation still have not been investigated.

## A. Contributions

In this paper, a novel low-complexity EP detector is proposed based on EPA. The main contributions include:

- Targeting correlated channels with multiple-antenna user equipment (MAUE) systems, a low-complexity EP detector based on EPA is proposed, which is named block-diagonal Neumann-series (BD-NS) based

EP approximation (BD-NS-EPA). Specifically, a block diagonalization based iteration leveraging matrix partition is carried out to extract the block-diagonal features and decrease the operations between large matrices among iterations. Such strategy can not only skillfully extract the main information of the channel, but also minimize the computational complexity effectively.

- An adjustable sorting message updating (ASMU) scheme is proposed to further reduce the redundant and inefficient operations in each iteration. The resulted algorithm is easy to parallelize and hardware-friendly.
- We design an efficient pipelined VLSI architecture for the proposed detector and present the reference ASIC implementation results, which enables us to exhibit its hardware efficiency compared to the state-of-the-art (SOA) detectors.


## B. Paper Outline

The remainder of this paper is organized as follows. The system model, NSA, EPD and EPA detection for MIMO systems are introduced in Section II. The proposed BD-NS-EPA algorithm is presented in Section III. Section IV provides the numerical results and complexity analysis is presented in Section V. The VLSI architecture and corresponding hardware implementation results are discussed in Section VI. Section VII concludes this paper.

## C. Notations

Throughout the paper, we utilize the following notations. Bold uppercase, bold lowercase and lowercase letters denote matrices, vectors and scalars, respectively. The superscripts $(\cdot)^{H},(\cdot)^{T}$ and $(\cdot)^{-1}$ stand for conjugate transpose, transpose and matrix inversion, respectively. $\Re(\cdot), \mathfrak{J}(\cdot)$ and $\overline{(\cdot)}$ denote the real part, imaginary part and conjugate version of a complex number, respectively. The symbol $\mathbf{I}_{M}$ indicates an $M \times M$ identity matrix and $\log (\cdot)$ denotes the natural logarithm. The $i$-th element in vector $\mathbf{x}$ is denoted by $x_{i}$, while the $(i, j)$-th element in matrix $\mathbf{X}$ is $X_{i j}$. The notation $\operatorname{diag}(\mathbf{x})$ creates a matrix with $\mathbf{x}$ in the diagonal and $\operatorname{diag}(\mathbf{X})$ is the vector of the diagonal elements of $\mathbf{X} . \mathcal{C} \mathcal{N}\left(\mathbf{x}, \boldsymbol{\sigma}^{2}\right)$ denotes the complex Gaussian distribution. The multi-variate complex normal distribution of a random vector $\mathbf{y}$ is represented by $\mathcal{C} \mathcal{N}(\mathbf{y}, \boldsymbol{\mu}, \boldsymbol{\Sigma})$, where the $\boldsymbol{\mu}$ is the mean vector and $\boldsymbol{\Sigma}$ denotes the covariance matrix. Also, $\mathbb{E}_{f}[x]$ represents the expectation of the distribution $f(x)$, and $\rho(\mathbf{X})$ stands for for the spectral radius of matrix $\mathbf{X}$.

## II. Preliminary

## A. System Model

Consider an uplink MIMO system, in which a single BS with $N$ antennas communicates with $m$ UEs and each UE is equipped with $m_{\text {UE }}$ antennas, as depicted in Fig. 1. The total number of antennas in user side is $M=m \times m_{\mathrm{UE}}$. Supposing the transmitted symbols are from the $\mathcal{Q}$-QAM constellation, the set of constellation symbols is represented by $\Theta$ and $\mathcal{Q}$ denotes the constellation size. The transmitted symbol vector is denoted by an $M \times 1$ complex vector $\mathbf{x}=\left[\mathbf{x}_{1}^{T} \cdots \mathbf{x}_{i}^{T} \cdots \mathbf{x}_{m}^{T}\right]^{T}$, where $\mathbf{x}_{i}=\left[x_{i 1} \cdots x_{i j} \cdots x_{i m_{\mathrm{UE}}}\right]^{T}$ with each component $x_{i j} \in \Theta$ and follows a normalized expected transmitted power $\mathbb{E}\left\{\left|x_{i j}\right|^{2}\right\}=1$. The received vector $\mathbf{y} \in \mathbb{C}^{N \times 1}$ at the BS side

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-03.jpg?height=399&width=618&top_left_y=197&top_left_x=296)
Fig. 1. An uplink L-MIMO system. (Enc. $=$ Encoder, Mod. $=$ Modulator) [24].

is obtained by:

$$
\begin{equation*}
\mathbf{y}=\mathbf{H} \mathbf{x}+\mathbf{n}, \tag{1}
\end{equation*}
$$

where $\mathbf{n} \in \mathbb{C}^{N \times 1}$ represents the additive white Gaussian noise (AWGN) vector with distribution $\mathbf{n} \sim \mathcal{C} \mathcal{N}\left(0, \sigma_{n}^{2} \mathbf{I}_{N}\right)$. In this paper, we assume that perfect channel state information (CSI) is known at the receiver side and the relevant experiments are based on the quasi-static channel.

Most of the previous researches on low-complexity EPD only considered geometric attenuation, but neglected antenna correlation [18], [20], [21], [22]. However, for practical L-MIMO systems, the detection performance is affected by the spatial correlation of signals to a large extent. Therefore, in this paper, the Kronecker channel model [25] is considered as:

$$
\begin{equation*}
\mathbf{H}=\mathbf{R}^{1 / 2} \mathbf{G} \mathbf{T}^{1 / 2}, \tag{2}
\end{equation*}
$$

where $\mathbf{G} \in \mathbb{C}^{N \times M}$ denotes the complex standard Gaussian distribution channel with i.i.d. elements, i.e., $\mathbf{G}_{i, j} \sim \mathcal{C} \mathcal{N}(0,1)$. Furthermore, $\mathbf{R} \in \mathbb{C}^{N \times N}$ and $\mathbf{T} \in \mathbb{C}^{M \times M}$ stand for the spatial correlation matrices. The elements of $\mathbf{R}$ and $\mathbf{T}$ can be determined by Eq. (3),

$$
\begin{align*}
& R_{p q}=\left\{\begin{array}{l}
\left(\zeta_{r} e^{j \theta}\right)^{q-p}, \quad p \leq q, \\
R_{q p}^{*}, \quad p>q,
\end{array}\right. \\
& T_{p q}=\left\{\begin{array}{l}
\left(\zeta_{t} e^{j \theta}\right)^{q-p}, \quad p \leq q, \\
T_{q p}^{*}, \quad p>q,
\end{array}\right. \tag{3}
\end{align*}
$$

where $\zeta_{r}$ and $\zeta_{t}$ are correlated coefficients that reflect the correlation between the $p$-th antenna and the $q$-th antenna at the BS and the user sides, respectively. In addition, $\theta$ is the phase factor [26], which is randomly generated from $[-\pi / 2, \pi / 2]$ in our simulations. Eq. (2) is derived under the assumption that the correlation between BS and UEs are statistically independent, since the BS and UEs are usually far from each other. As revealed by [23], the transmitting antennas from the same UE are usually in high correlation due to insufficient spacing. However, in most of the existing low-complexity EPD works [17], [18], [22], the correlation between antennas from the same UE are totally neglected, which is impractical and inaccurate. Therefore, based on the propagation fact, the $\zeta_{r}$ and $\zeta_{t}$ are redefined as the correlation factor of the receiving antennas and the transmitting antennas from the same UE, respectively. Please notice that the correlation between antennas from different UEs is neglected and the pseudo-codes for the generation of $\mathbf{T}$ are provided in Alg. 1.

```
Algorithm 1 Key steps for generating T
    Input: $M, m_{\mathrm{UE}}, \zeta_{\mathrm{t}}$;
    Initialization: $\mathbf{T}=\mathbf{I}_{M}$;
    for $\operatorname{bln}=1$ to $M / m_{\mathrm{UE}}$ do
        for $p=m_{\mathrm{UE}} \times(\mathrm{bln}-1)$ to $m_{\mathrm{UE}} *$ bln do
            for $q=(p+1)$ to $m_{\mathrm{UE}} \times \operatorname{bln}$ do
                $T(p, q)=\left(\exp (j * \operatorname{rand} * \pi / 2) * \zeta_{t}\right)^{(q-p)}$;
    $\mathbf{T}=\mathbf{T}+\mathbf{T}^{H}-\mathbf{I}_{M} ;$
    Output: T.
```


## B. Neumann Seires Approximation (NSA)

As a promising approach for large-scale matrix inversion, the Neumann series expansion [27] takes the advantages of iterative architecture to improve its accuracy, which efficiently alleviates the prohibitive computation and power cost for traditional exact decomposition methods [28]. Specifically, if the matrix $\mathbf{A}$ is close to an invertible matrix $\mathbf{X}$ :

$$
\begin{equation*}
\lim _{n \rightarrow \infty}\left(\mathbf{I}-\mathbf{X}^{-1} \mathbf{A}\right)^{n}=0 \text { or } \lim _{n \rightarrow \infty}\left(\mathbf{I}-\mathbf{A} \mathbf{X}^{-1}\right)^{n}=0, \tag{4}
\end{equation*}
$$

then the inversion of $\mathbf{A}$ can be expressed by Neumann series:

$$
\begin{equation*}
\mathbf{A}^{-1}=\sum_{n=0}^{\infty}\left(\mathbf{I}-\mathbf{X}^{-1} \mathbf{A}\right)^{n} \mathbf{X}^{-1} \tag{5}
\end{equation*}
$$

With $\mathbf{D}=\mathbf{X}$ and $\mathbf{E}=\mathbf{A}-\mathbf{X}$, we can take the first $k$ terms of Neumann series as the $k$-term approximation of $\mathbf{A}^{-1}$ :

$$
\begin{equation*}
\mathbf{A}^{-1} \approx \hat{\mathbf{A}}_{k}^{-1}=\sum_{n=0}^{k-1}\left(-\mathbf{D}^{-1} \mathbf{E}\right)^{n} \mathbf{D}^{-1} \tag{6}
\end{equation*}
$$

## C. Expectation Propagation Detector (EPD)

In MIMO detection, it is difficult to perform inference over the posterior distribution $p(\mathbf{x} \mid \mathbf{y})$ in Eq. (7), where $\mathbb{I}_{x_{i} \in \Theta}$ is the indicator function that constrains the value of $x_{i} \in \Theta$.

$$
\begin{equation*}
p(\mathbf{x} \mid \mathbf{y})=\frac{p(\mathbf{y} \mid \mathbf{x}) p(\mathbf{x})}{p(\mathbf{y})} \propto \mathcal{C} \mathcal{N}\left(\mathbf{y}: \mathbf{H x}, \sigma_{n}^{2} \mathbf{I}_{N}\right) \prod_{i=1}^{M} \mathbb{I}_{x_{i} \in \Theta} . \tag{7}
\end{equation*}
$$

To this end, by substituting the non-Gaussian parts in Eq. (7) with exponential family distribution, the EPD proposed in [11] utilizes an approximated joint posterior distribution (AJPoD) $q(\mathbf{x})$ that belongs to exponential family to approximates the intractable posterior:

$$
\begin{align*}
q(\mathbf{x}) & =\mathcal{C} \mathcal{N}\left(\mathbf{y}: \mathbf{H x}, \sigma_{n}^{2} \mathbf{I}_{N}\right) \prod_{i=1}^{M} \exp \left(-\frac{1}{2} \Lambda_{i} x_{i}^{2}+\gamma_{i} x_{i}\right) \\
& =\mathcal{C} \mathcal{N}\left(\mathbf{y}: \mathbf{H} \mathbf{x}, \sigma_{n}^{2} \mathbf{I}_{N}\right) \exp \left(-\frac{1}{2} \mathbf{x}^{H} \Lambda \mathbf{x}+\boldsymbol{\gamma}^{H} \mathbf{x}\right) \tag{8}
\end{align*}
$$

where $\exp \left(-\frac{1}{2} \Lambda_{i} x_{i}^{2}+y_{i} x_{i}\right)$ represents unnormalized Gaussian function, and $\Lambda_{i}$ is the parameter related to its variance, while $y_{i}$ is the parameter related to its both variance and mean. Further, $\boldsymbol{\gamma}=\left[\gamma_{1}, \gamma_{2}, \cdots, \gamma_{M}\right]^{H}$ and $\Lambda$ is a diagonal matrix such that $\Lambda=\operatorname{diag}\left(\left[\Lambda_{1}, \Lambda_{2}, \cdots, \Lambda_{M}\right]\right)$.

According to [11], Eq. (8) follows the joint Gaussian distribution, which is:

$$
\begin{equation*}
q(\mathbf{x}) \sim \mathcal{C} \mathcal{N}(\mathbf{x}: \boldsymbol{\mu}, \Sigma) \propto \exp \left(-\frac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^{H} \Sigma^{-1}(\mathbf{x}-\boldsymbol{\mu})\right) \tag{9}
\end{equation*}
$$

where $\boldsymbol{\mu}$ and $\Sigma$ are the corresponding mean vector and covariance matrix, respectively. Compare Eq. (8) with Eq. (9), we can obtain:

$$
\begin{align*}
\Sigma & =\left(\sigma_{n}^{-2} \mathbf{H}^{H} \mathbf{H}+\boldsymbol{\Lambda}\right)^{-1}  \tag{10}\\
\boldsymbol{\mu} & =\Sigma\left(\sigma_{n}^{-2} \mathbf{H}^{H} \mathbf{y}+\boldsymbol{\gamma}\right) \tag{11}
\end{align*}
$$

However, acquiring $\Lambda$ and $\boldsymbol{\gamma}$ is not viable due to the intractability of $p(\mathbf{x})$. To tackle this issue, the sequential EP proposed in [29] considers a titled PDF $\hat{p}(\mathbf{x})$, whose $i$-th marginal distribution $\hat{p}\left(x_{i}\right)$ is calculated by replacing the $i$-th unnormalized Gaussian factor $\exp \left(-\frac{1}{2} \Lambda_{i} x_{i}^{2}+y_{i} x_{i}\right)$ in the $i$-th marginal of Eq. (8) with a non-Gaussian function $\mathbb{I}_{x_{i} \in \Theta}$ in Eq. (7), as follows:

$$
\begin{equation*}
\hat{p}\left(x_{i}\right)=\frac{q\left(x_{i}\right)}{\exp \left(-\frac{1}{2} \Lambda_{i} x_{i}^{2}+\gamma_{i} x_{i}\right)} \mathbb{I}_{x_{i} \in \Theta,} \tag{12}
\end{equation*}
$$

where $q\left(x_{i}\right)$ represents the $i$-th marginal of the distribution $q(\mathbf{x})$ and $\hat{p}(\mathbf{x})$ is named replacement distribution (RD). Further, Eq. (13) is defined as the $i$-th cavity marginal distribution (CMD) of $q(\mathbf{x})$.

$$
\begin{equation*}
q^{\backslash i}\left(x_{i}\right)=\frac{q\left(x_{i}\right)}{\exp \left(-\frac{1}{2} \Lambda_{i} x_{i}^{2}+\gamma_{i} x_{i}\right)} . \tag{13}
\end{equation*}
$$

Therefore, it is possible to execute inference relying on Eq. (12), as it consists of only one non-Gaussian factor.

## D. EP Detection With Approximation (EPA)

To alleviate the matrix inversion burden in original EPD, the EPA is proposed in [21] by simplifying the sequential updating relations. The generalized procedure of EPA is summarized in Alg. 2. Through reformulating the moment-matching process, an approximation of $\boldsymbol{\Sigma}$ is applied to eliminate the iterative matrix inversions. Since the iteration of EPA is matrix inversion-free, its performance would not be deteriorated by the inversion approximation methods.

However, several bottlenecks of EPA still need to be tackled: i) An inevitable exact matrix inversion with complexity $\mathcal{O}\left(M^{3}\right)$ is still required to guarantee its performance (Line 3 in Alg. 2); ii) Each iteration in EPA suffers from $\mathcal{O}(M N)$ multiplications and $\mathcal{O}(M \mathcal{Q})$ exponentiations (Line 8 in Alg. 2); iii) Each iteration of EPA updates all node messages, while in fact, some nodes tend to be stable after each iteration and only partial unstable nodes need to be further updated. It is noteworthy that the $\boldsymbol{\gamma}$ is set as zero in the EPA algorithm.

## III. Proposed Efficient MIMO Detector

Although some works [17], [18], [21] have proposed to approximate the matrix inversion in Eq. (10) by NSA, they all assume under ideal channels. In this section, the correlated L-MIMO channels in MAUE systems are characterized firstly. Then, based on the channel property, the BD-NS-EPA algorithm is proposed.

```
Algorithm 2 EPA algorithm [21].
    Input: $\mathbf{y}, \mathbf{H}, \sigma_{n}^{2}, L, \beta$;
    Initialization: $\Lambda_{i}=E_{s}^{-1}, \gamma_{i}=0, i=1, \ldots, M$;
    $\Sigma=\left(\sigma_{n}^{-2} \mathbf{H}^{H} \mathbf{H}+\operatorname{diag}(\Lambda)\right)^{-1}, \mathbf{b}=\sigma_{n}^{-2} \mathbf{H}^{H} \mathbf{y}+\boldsymbol{\gamma}$;
    $\Sigma_{d} \leftarrow \operatorname{diag}(\Sigma), \mathbf{V} \leftarrow \operatorname{diag}\left(\sigma_{n}^{-2} \mathbf{H}^{H} \mathbf{H}\right) ;$
    $\mathbf{h}=\Sigma_{d} \cdot /\left(1-\Sigma_{d} \cdot \times \Lambda\right), \boldsymbol{\xi}^{(0)}=\mathbf{h} \cdot \times\left(\boldsymbol{\mu} \cdot / \Sigma_{d}-\boldsymbol{\gamma}\right) ;$
    for $l=1$ to $L$ do
        for $i=1,2, \ldots, M$ do
            $\left\lfloor\eta_{i}^{(l)}=\mathbb{E}_{\hat{p}^{(l)}\left(x_{i}\right)}\left[x_{i}\right] ;\right.$
        $\boldsymbol{\eta}^{(l)}=\left\{\eta_{1}^{(l)}, \eta_{2}^{(l)}, \ldots, \eta_{M}^{(l)}\right\}^{T} ;$
        $\mathbf{m}^{(l)}=\mathbf{y}-\mathbf{H} \boldsymbol{\eta}^{(l)}$;
        $\boldsymbol{\rho}^{(l)}=\sigma_{n}^{-2} \mathbf{H}^{H} \mathbf{m}^{(l)}+\mathbf{V} . \times \boldsymbol{\eta}^{(l)} ;$
        $\boldsymbol{\xi}^{(l)}=\boldsymbol{\rho}^{(l)} . / \mathbf{V}$;
        $\boldsymbol{\xi}^{(l)}=\beta \boldsymbol{\xi}^{(l)}+(1-\beta) \boldsymbol{\xi}^{(l-1)} ;$
    Output: $\eta$.
```

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-04.jpg?height=603&width=901&top_left_y=968&top_left_x=1072)
Fig. 2. The Gram matrix $\mathbf{A}$ in SAUE and MAUE systems with ideal propagation environment (IPE), non-ideal propagation environment (NPE) and bad propagation environment (BPE) [24] (From left to right, and top to bottom, they are called as channel $1,2,3,4,5,6$, respectively).

## A. Characteristic of Correlated L-MIMO Channels

Considering the selection of $\mathbf{D}$ poses a vital impact on the approximate accuracy and convergence speed of Eq. (6) [30], we firstly analyze the characteristic of Gram matrix in L-MIMO system with different propagation environments. The property of Gram matrix $\mathbf{A}$, i.e., $\mathbf{H}^{H} \mathbf{H}$ is illustrated in Fig. 2. It can be noticed that $\mathbf{A}$ exhibits diversely dominant in different systems under various propagation conditions. Specifically, in MAUE systems, Gram matrix appears near block diagonally dominant and the block property becomes more evident with the correlation increasing. Therefore, intuitively, the block-diagonal construction is more suitable for the MAUE systems in high correlation.

## B. BD-Based Neumann Series (BD-NS) Iteration

To break the implementation bottleneck of the explicit matrix inversion in EPD and EPA, previous works [17], [18], [22] have tried to apply NSA to approximate the inversion results. Though these methods effectively alleviate the computational cost, they all assume ideal propagation conditions and fail to exploit the emblematic properties of channel

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-05.jpg?height=357&width=875&top_left_y=189&top_left_x=163)
Fig. 3. The schematic diagram of BD-based MP scheme.

matrices, thus leading to unsatisfactory performance in nonideal scenarios. To this end, in this subsection, a BD-NS and the corresponding iterations for the mean vector $\boldsymbol{\mu}$ are proposed.

As revealed in Fig. 2, since the Gram matrices in MAUE systems features block-diagonal dominant, matrix partition (MP) [31] is firstly employed to extract the dominant block-diagonal entries. Specifically, the pre-conditioner matrix $\tilde{\mathbf{D}}_{1}$ maintains the block diagonal elements of $\mathbf{A}$, i.e., $\tilde{\mathbf{D}}_{1}$ is composed of several block sub-matrices. For convenience, the size of each block sub-matrix is assumed to be identical, denoted by $m_{\mathrm{UE}}$. Hence the number of sub-matrices is $M / m_{\mathrm{UE}}$, that is, the number of UEs $m$. The mathematic expression of $\tilde{\mathbf{D}}_{1}$ is denoted as Eq. (14) where $\tilde{\mathbf{D}}_{(1, t)}(t=1, \cdots, m)$ are composed of the block-diagonal elements in $\mathbf{A}$ with size $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$.

$$
\begin{equation*}
\tilde{\mathbf{D}}_{1}=\operatorname{diag}\left[\tilde{\mathbf{D}}_{(1,1)}, \tilde{\mathbf{D}}_{(1,2)}, \cdots, \tilde{\mathbf{D}}_{(1, m)}\right] . \tag{14}
\end{equation*}
$$

Since the $\tilde{\mathbf{D}}_{(1,1)}, \cdots, \tilde{\mathbf{D}}_{(1, m)}$ are all symmetric positive definite matrices and their size $m_{\text {UE }}$ is usually small, Cholesky decomposition [32] is employed here to compute their inversions. Therefore, the $\tilde{\mathbf{D}}_{1}^{-1}$ can be obtained by Eq. (15) and the approximate inversion of Gram matrix $\mathbf{A}$ can be further calculated by Eq. (16), where $\tilde{\mathbf{E}}_{1}=\mathbf{A}-\tilde{\mathbf{D}}_{1}$.

$$
\begin{align*}
& \tilde{\mathbf{D}}_{1}^{-1}=\operatorname{diag}\left[\tilde{\mathbf{D}}_{(1,1)}^{-1}, \tilde{\mathbf{D}}_{(1,2)}^{-1}, \cdots, \tilde{\mathbf{D}}_{(1, m)}^{-1}\right]  \tag{15}\\
& \mathbf{A}_{k}^{-1} \approx \sum_{n=0}^{k-1}\left(-\tilde{\mathbf{D}}_{1}^{-1} \tilde{\mathbf{E}}_{1}\right)^{n} \tilde{\mathbf{D}}_{1}^{-1} \tag{16}
\end{align*}
$$

The illustration of MP process for $\mathbf{A}$ is depicted in Fig. 3, where $M=8$ with $m_{\mathrm{UE}}=4$ and $m_{\mathrm{UE}}=2$ are exemplified, respectively. It is worth mentioning that such accurate Cholesky inversion for the sub-matrices can skillfully exert the main information of channels at the expense of slight complexity, as $m_{\mathrm{UE}}$ is usually small.

To simplify the matrix inversion of EPA with the BD-NS, firstly, we modify its initialization mode as $\Sigma=\mathbf{W}^{-1}$, where $\mathbf{W}=\mathbf{H}^{\mathrm{H}} \mathbf{H}+\sigma_{n}^{2} \operatorname{diag}(\boldsymbol{\Lambda})$. ${ }^{1}$ It is worth mentioning that such conversion profits the hardware implementation, as it avoids the multiplications for the $M \times M$ components in Gram matrix, and only needs to execute multiplications on the $M$ elements in $\operatorname{diag}(\boldsymbol{\Lambda})$. Denoting $\mathbf{D}_{1}$ as its block-diagonal matrix, the $k$-term approximate inversion of $\mathbf{W}$ is obtained by:

$$
\begin{equation*}
\Sigma \approx \mathbf{W}_{k}^{-1}=\sum_{n=0}^{k-1} \Psi^{n} \mathbf{D}_{1}^{-1}=\Psi \mathbf{W}_{k-1}^{-1}+\mathbf{D}_{1}^{-1} \tag{17}
\end{equation*}
$$

[^0]![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-05.jpg?height=298&width=652&top_left_y=197&top_left_x=1192)
Fig. 4. Statistics on error probability versus the variances of CMD.

where $\Psi=\mathbf{I}-\mathbf{D}_{1}^{-1} \mathbf{W}=-\mathbf{D}_{1}^{-1} \mathbf{E}$. Further, observing the Eqs. (10) and (11), we can notice that the ultimate purpose for calculating covariance matrix $\boldsymbol{\Sigma}$ is to obtain the mean vector $\boldsymbol{\mu}$. Therefore, at each iteration of Eq. (17), we can directly update the $\boldsymbol{\mu}$ instead of $\boldsymbol{\Sigma}$. Specifically, denoting $\mathbf{b}=\mathbf{H}^{H} \mathbf{y}$ and multiplying Eq. (17) with $\mathbf{b}$, we can attain a recursive formulation for $\boldsymbol{\mu}$ as follows:

$$
\begin{equation*}
\tilde{\boldsymbol{\mu}}^{(k)}=\Psi \tilde{\boldsymbol{\mu}}^{(k-1)}+\mathbf{D}_{1}^{-1} \mathbf{b}=\Psi \tilde{\boldsymbol{\mu}}^{(k-1)}+\tilde{\boldsymbol{\mu}}^{(1)}, \tag{18}
\end{equation*}
$$

where $\tilde{\boldsymbol{\mu}}^{(k)}=\mathbf{W}_{k}^{-1} \mathbf{b}$ and $\tilde{\boldsymbol{\mu}}^{(1)}=\mathbf{D}_{1}^{-1} \mathbf{b}$. Therefore, the matrix inversion in EPA is simplified as the block-diagonal Neumann iteration in the proposed algorithm.

## C. Adjustable Sorting Message Updating (ASMU)

As presented in [21], in the update process of EPA, the parameters $\rho$ and $\xi$ of the CMD for each transmitted symbol are batch updated and have no difference to each other, which means the parameters of the CMD are all calculated consistently during iterations. However, as revealed in [20], the reliability of the CMD for each symbol node is different due to the channel response coefficients and practical noise power. Therefore, we calculate the error probability of the detection symbols corresponding to different variances of the CMD under different antenna configurations for 10000 samples, with $\mathrm{SNR}=2$ and 16 -QAM modulation. The statistical results in Fig. 4 reveal those symbols with large variances are more likely to be incorrectly detected, indicating the symbols with large variances require more iterations to improve accuracy, while those symbols with small variances need less.

Therefore, leveraging the variance information, an efficient partial updating scheme named adjustable sorting message updating is proposed, which can noticeably decrease the computational cost at the expense of slight performance degradation. The details of it is described in follows.

After each iteration, a certain number of symbol nodes with small variances would converge, hence it is unnecessary to update the information of all nodes. According to [11], the variance $h_{i}$ of CMD is obtained by calculating the Eq. (19), and thus a straightforward but also very coarse scheme is to directly utilize the variance as an index to evaluate the reliability of each symbol. Admittedly, such scheme is indeed able to acquire favorable reliability estimation, but also introduces redundant computation such as division and multiplication, both of which are hardware-unfriendly.

$$
\begin{equation*}
h_{i}=\frac{\boldsymbol{\Sigma}_{i i}}{1-\boldsymbol{\Sigma}_{i i} \cdot \Lambda_{i}} . \tag{19}
\end{equation*}
$$

To this end, based on the monotonicity of Eq. (19), a simple but useful simplification is proposed. Specifically, as the $\Lambda_{i}$ is initialized by the reciprocal of mean transmitted power, i.e., $E_{S}$, which is normalized to 1 as mentioned in Section II, and $0 \leq \boldsymbol{\Sigma}_{i i}<1$, Eq. (19) exhibits the property of monotone
increasing. Therefore, sorting $\boldsymbol{\Sigma}_{d}$ is equivalent to sort $\mathbf{h}$. More importantly, combined with the simplification algorithm presented in the next subsection, the calculation of Eq. (19) can be completely omitted.

Accordingly, the steps of ASMU are summarized as follows. Firstly, sort the variances of all approximate marginal posterior distributions (AMPoDs), i.e., $\Sigma_{d}$ in descending order. Next, based on the sorting results, those symbols with larger variances are updated preferentially. Specifically, in the first iteration, all symbols are refreshed and only partial symbols are updated in subsequent iterations. Accordingly, a pruning degree $\kappa$ is defined and the number of nodes needs to be updated in each iteration is $(1-(l-1) \kappa) M$, where $l$ denotes the iteration number.

## D. The Proposed BD-NS-EPA Algorithm

As revealed by [32], to assure the convergence, the $\rho(\boldsymbol{\Psi})$ should be smaller than 1 . To this end, an improved normalization factor (INF) proposed by our previous work [24] is introduced here to ensure and speed up the Neumann-series convergence in the proposed detector.

According to [24], the normalization factor $\alpha_{\text {opt }}^{+}$multiplied before $\mathbf{D}_{1}$ can be determined by the below:

$$
\begin{equation*}
\alpha_{\mathrm{opt}}^{+}=\frac{\mathbb{E}\left\{\lambda_{\max }\left(\mathbf{D}_{1}^{-1} \mathbf{W}\right)\right\}+\mathbb{E}\left\{\lambda_{\min }\left(\mathbf{D}_{1}^{-1} \mathbf{W}\right)\right\}}{2}, \tag{20}
\end{equation*}
$$

where the $\mathbb{E}\left\{\lambda_{\text {max }}\right\}$ and $\mathbb{E}\left\{\lambda_{\text {min }}\right\}$ can be acquired by image method offline. It is noteworthy that all related calculations only utilize the information about antenna configuration, which can be pre-known. Therefore, the $\alpha_{\text {opt }}^{+}$can be pre-computed offline and directly employed as the input in the proposed detector. Based on the INF, Eq. (18) is further rewritten as:

$$
\begin{equation*}
\boldsymbol{\mu}^{(k)}=\boldsymbol{\Psi} \boldsymbol{\mu}^{(k-1)}+\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}_{1}\right)^{-1} \mathbf{b}=\boldsymbol{\Psi} \boldsymbol{\mu}^{(k-1)}+\boldsymbol{\mu}^{(1)}, \tag{21}
\end{equation*}
$$

where $\boldsymbol{\Psi}=-\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}_{1}\right)^{-1} \mathbf{E}$ and $\boldsymbol{\mu}^{(1)}=\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}_{1}\right)^{-1} \mathbf{b}$.
Additionally, as discussed in Section II, to obtain the mean $\hat{\eta}_{i}^{(l)}$ and variance $\hat{\chi}_{i}^{(l)}$ of RD, both the original EPD and EPA have to compute the probability of approximated Gaussian distribution for each constellation point of every transmitted symbol as follows:

$$
\begin{equation*}
p\left(x_{i}=\theta_{k}\right)=\frac{1}{\sqrt{2 \pi h_{i}^{2(l)}}} \exp \left(-\frac{1}{2} \frac{\left(\theta_{k}-\xi_{i}^{(l)}\right)^{2}}{h_{i}^{2(l)}}\right), \tag{22}
\end{equation*}
$$

where $\theta_{k} \in \Theta, k=1,2, \cdots, \mathcal{Q}$ are the sampled constellation points. Next the probability $p\left(x_{i}=\theta_{k}\right)$ is utilized to calculate $\hat{\eta}_{i}^{(l)}$ and $\hat{\chi}_{i}^{(l)}$ as:

$$
\left\{\begin{array}{l}
\hat{\eta}_{i}^{(l)}=\sum_{k=1}^{\mathcal{Q}} p\left(x_{i}=\theta_{k}\right) \cdot \theta_{k},  \tag{23}\\
\hat{\chi}_{i}^{(l)}=\sum_{k=1}^{\mathcal{Q}} p\left(x_{i}=\theta_{k}\right) \cdot\left(\theta_{k}-\hat{\eta}_{i}^{(l)}\right)^{2} .
\end{array}\right.
$$

Obviously, the process from Eq. (22) to Eq. (23) contains subtraction, multiplication and hardware-unfriendly exponential operations with complexity $\mathcal{O}(L \mathcal{Q} M)$. To this end, a hard decision approximation (HDA) [33] is employed here to alleviate the complexity burden. Operating on the constellation, the HDA is shown as Eq. (24), where $l$ and $i$ denote the iteration and symbol node respectively.

$$
\begin{equation*}
\hat{\eta}_{i}^{(l)}=\arg \min _{v_{i} \in \Theta}\left|v_{i}-\xi_{i}^{(l-1)}\right| . \tag{24}
\end{equation*}
$$

```
Algorithm 3 Proposed BD-NS-EPA algorithm
    Input : $\mathbf{y}, \mathbf{H}, \sigma_{n}^{2}, k, L, \beta, \alpha_{\text {opt }}^{+}, \kappa$.
    $\Lambda_{i}=E_{s}^{-1}, i=1, \cdots, M ; T \leftarrow M / m_{\mathrm{UE}} ;$
    $\mathbf{A}=\mathbf{H}^{H} \mathbf{H}, \mathbf{V}=\sigma_{n}^{-2} \operatorname{diag}(\mathbf{A}) ;$
    $\mathbf{W}=\mathbf{A}+\sigma_{n}^{2} \operatorname{diag}(\Lambda), \mathbf{b}=\mathbf{H}^{H} \mathbf{y} ;$
    Obtain $\mathbf{D}_{(1,1)}, \mathbf{D}_{(1,2)}, \cdots, \mathbf{D}_{(1, T)}$;
    for $t=1: T$ do
        $\mathbf{D}_{(1, t)} \leftarrow \alpha_{\text {opt }}^{+} \cdot \mathbf{D}_{(1, t)} ; \quad$ // INF optimization
    Compute $\mathbf{D}_{(1, t)}^{-1}(t \in[1: T])$ by Cholesky inversion;
    $\mathbf{D}^{-1}=\operatorname{diag}\left[\mathbf{D}_{(1,1)}^{-1}, \cdots, \mathbf{D}_{(1, T)}^{-1}\right] ;$
    $\boldsymbol{\mu}^{(1)}=\sigma_{n}^{-2} \mathbf{D}^{-1} \mathbf{b}, \boldsymbol{\Sigma}_{d}=\operatorname{diag}\left(\mathbf{D}^{-1}\right), \boldsymbol{\Psi}=\mathbf{I}-\sigma_{n}^{-2} \mathbf{D}^{-1} \mathbf{W} ;$
    for $i=2: k$ do
        // Block Diagonal Neumann iteration
        $\boldsymbol{\mu}^{(i)}=\boldsymbol{\Psi} \boldsymbol{\mu}^{(i-1)}+\boldsymbol{\mu}^{(1)} ;$
    $\boldsymbol{\xi}^{(0)}=\boldsymbol{\mu}^{(k)} \cdot /\left(1-\boldsymbol{\Sigma}_{d} \cdot \times \boldsymbol{\Lambda}\right) ;$
    $[\sim, \Pi]=\operatorname{sort}\left(\boldsymbol{\Sigma}_{d}\right.$, descend $) / /$ Sorting
    for $l=1$ to $L$ do
        // Adjustable sorting message
                updating
        for $i=1, \cdots,(1-(l-1) \kappa) M$ do
            $j=\Pi(i) ;$
            $\eta_{j}=\arg \min _{v_{j} \in \Theta}\left|v_{j}-\xi_{j}^{(l-1)}\right| ;$
            $m_{j}=b_{j}-\sum_{k=1}^{M} A_{j k} \eta_{k}$;
            $\xi_{j}^{(l)}=m_{j} / V_{j}+\eta_{j} ;$
            $\xi_{j}^{(l)}=\beta \xi_{j}^{(l)}+(1-\beta) \xi_{j}^{(l-1)} ;$
    Output: $\quad \hat{x}_{i}=\underset{v \in \Theta}{\arg \min }\left|v-\eta_{i}\right|, i \in[1: M]$;
```

Benefiting from HDA scheme, to obtain the mean vector $\boldsymbol{\eta}$ of RD, it is unnecessary to calculate the variance $\mathbf{h}$ of the cavity distribution. Moreover, as discussed in Section III-C, since we utilize the variances of AMPoDs as the reliability evaluation instead of that of the CMDs, the calculation for $\mathbf{h}$ can be removed completely in the proposed algorithm.

Therefore, the details of the proposed BD-NS-EPA is summarized in Alg. 3, where $k$ and $L$ represents the counts of Neumann iterations and EP iterations, respectively. Additionally, the updating and moment matching processes of EP, EPA and BD-NS-EPA are concluded in Fig. 5. It can be noticed that EP follows a rigorous updating process from CMD $q^{\backslash i}(x)$ to RD $\hat{p}(x)$ and then to AJPoD $\tilde{q}(x)$, to approach the real joint posterior distribution $q(x)$. Although the EPA successfully avoids the updating of AJPoD, where the dominant computational burden of matrix inversions come from, it still needs to continuously update the variances of CMD and RD. By contrast, the BD-NS-EPA not only omits the calculation of variances, but also simplifies the calculation of initialization, thus successfully achieving reduced complexity.

## IV. Numerical Results

In this section, numerical simulation results are presented to demonstrate the enhancements achieved by the proposed BD-NS-EPA detector. Performance of several SOA message passing based detectors are also provided to compare with the BD-BS-EPA detector, including the EPA [21], EP-wNSA [22],

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-07.jpg?height=510&width=609&top_left_y=206&top_left_x=300)
Fig. 5. Diagrams of the message updating process for different algorithms.

BP [34], EP-NSA [17], LAMA [9] and CHEMP [8] detectors. Further, original EP detector [11], typical Cholesky-based MMSE detector and TL-BD-INSA detector [24] are provided as the benchmarks.

To verify the effectiveness of the BD-NS initialization, INF and ASMU schemes proposed in Section III, Fig. 6 compares the bit error ratio (BER) performance of EPA algorithm with different optimization schemes under three propagation environments. The $E_{b} / N_{0}[\mathrm{~dB}]$ used in our performance simulations is defined as Eq. (25) [35], where $E_{\mathrm{s}}$ denotes energy per transmitted symbol, $N$ is the number of receive antennas, $Q$ denotes the number of bits per constellation symbol, $R$ represents the channel code rate and $N_{0}$ denotes the noise power spectral density.

$$
\begin{equation*}
E_{\mathrm{b}} / N_{0}[\mathrm{~dB}]=10 \log _{10} \frac{E_{\mathrm{b}}}{N_{0}}=10 \log _{10} \frac{E_{\mathrm{s}} \times N}{Q \times R \times N_{0}} . \tag{25}
\end{equation*}
$$

As shown in Figs. 6(a) and 6(b), it can be noticed that under SAUE system with IPE, all EPA algorithms with different optimization schemes can achieve near-EP performance. However, most of them suffer from severe performance degradation as the propagation environment deteriorates. Specifically, although the EPA with traditional Neumannseries initialization (NS-EPA) can achieve near-EP performance and outperforms MMSE around 0.7 dB at $\mathrm{BER}=10^{-4}$ with iteration $L=3, k=8$, while with the correlation increasing, its performance declines evidently and becomes far worse than that of MMSE, because the NS initialization is unsuitable for correlated channels, as revealed by Fig. 6(c) and Fig. 6(d). By contrast, the EPA with BD-NS initialization but no INF (BD-NS-EPA-w/o-INF) performs obviously better than NS-EPA, delivering about 1 dB advantage at $\mathrm{BER}=10^{-2}$ in MAUE system with NPE, as depicted in Fig. 6(c). Further, it can be observed that the EPA with both BD-NS initialization and INF (BD-NS-EPA-INF) can further improve the BER performance significantly. Specifically, compare to the BD-NS-EPA-w/o-INF, it can realize around 2.5 dB enhancement at $\mathrm{BER}=10^{-3}$ in MAUE with NPE and 2.7 dB enhancement at $\mathrm{BER}=10^{-2}$ in MAUE with BPE, respectively.

Based on the BD-NS-EPA-INF and $\kappa=0.1$, we further compare the performance of the ASMU with diverse sorting orders, which are ascending (BD-NS-EPA-a), descending (BD-NS-EPA-d) and without sorting (BD-NS-EPA-w/o-s), respectively. As depicted in both Fig. 6(c) and Fig. 6(d), under the same $\kappa$, BD-NS-EPA-d outperforms that without sorting while the BD-NS-EPA-a delivers the worst BER performance. This is because, in each iteration, BD-NS-EPA-a discards the
updated calculations of the nodes with the largest variances, while these nodes are more likely to be detected mistakenly. In contrast, BD-NS-EPA-d only discards the updates of the nodes with the smallest variances, and the error probability of these nodes is relatively small. Therefore, BD-NS-EPA-d can achieve better detection performance than EP-NS-EPA-a. In addition, since BD-NS-EPA-w/o-s prunes without sorting, its discarded nodes include nodes with large and small variances. Therefore, its performance outstrips BD-NS-EPA-a but is worse than BD-NS-EPA-d. Further, it is noteworthy that as shown in both Fig. 6(c) and Fig. 6(d), compared to the BD-NS-EPA-INF at BER $=10^{-3}$, the SNR loss of the BD-NS-EPA-INF-d is around 0.1 dB , which almost can be neglected, while the reduction in computational complexity is considerable (see Section V).

## A. SAUE Systems

Next, we compare the BER performance of SOA algorithms in SAUE system with IPE. As shown in Fig. 7(a), under large BS to user antenna ratios and uncorrelated propagation environment, both EPA and BP can obtain the comparable performance as EP detector, with iteration $L=3$. Additionally, it can be noticed that $k=4$ is sufficient for EP-NSA, EP-wNSA and BD-NS-EPA to obtain similar performance as EP with the same iteration $L$, which outperforms MMSE. Moreover, LAMA and CHEMP can also achieve comparable performance, but require 8 and 6 iterations, respectively. However, as revealed by Fig. 7(b), when loading factor and correlation increase slightly, the performance of BP and EP-wNSA degrades evidently.

## B. MAUE Systems

Further, the performance among diverse detectors in MAUE systems with different propagation environments is compared. For the IPE scenario in Fig. 8(a), all non-linear detectors can outperform the MMSE evidently and the gaps among EP, EPA, BP, LAMA, CHEMP and BD-NS-EPA are relatively small. Specifically, compared to EP, CHEMP shows around 0.1 dB loss at the BER of $10^{-4}$ while the discrepancy of EPA is only about 0.05 dB . Additionally, by exerting $k=6$, the BD-NS-EPA with $\kappa=0$ can achieve near-EPA performance. Further, the gap between BD-NS-EPA with $\kappa=0.1$ and that with $\kappa=0$ is slight, with only around 0.1 dB at BER of $10^{-4}$. However, EP-NSA and EP-wNSA both show unsatisfying performance, with around 1 dB gap at the BER of $10^{-4}$ compared to EP. Due to the property of linear iteration, the performance of TL-BD-INSA detector is slightly worse than MMSE with 0.6 dB at $\mathrm{BER}=10^{-3}$. When correlation increases as illustrated in Fig. 8(b), BP, CHEMP and EP-NSA all exhibit evident performance deterioration, resulting in even worse performance than MMSE. Meanwhile, BD-NS-EPA can still achieve close-to-EPA performance and the SNR gap compared with EP is only 0.4 dB at the BER of $10^{-4}$. Moreover, a certain degree of pruning, i.e., $\kappa=0.1$, only brings about 0.1 dB degradation at $\mathrm{BER}=10^{-4}$. When we reach the BPE scenario as $\zeta_{r}$ and $\zeta_{t}$ raise to 0.5 and 0.6 respectively, BP , EPA, EP-NSA and EP-wNSA suffer convergence difficulty, while MMSE and TL-BD-INSA are also far from satisfying as exhibited in Fig. 8(c). By contrast, the exact EP still exhibits promising results. Compared to EP, the performance of EPA degrades to some extent, with 0.2 dB loss at the BER of $10^{-3}$. Although the BD-NS-EPA also presents certain

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-08.jpg?height=553&width=1737&top_left_y=184&top_left_x=186)
Fig. 6. BER performance of different EPA algorithms in different propagation environments with 16-QAM modulation ( $L=3, k=8$ for all BD-NS-EPA).

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-08.jpg?height=691&width=893&top_left_y=820&top_left_x=154)
Fig. 7. BER performance of different algorithms in SAUE system.

degraded performance due to the increase of correlation, it can still maintain the performance close to EPA, with 0.5 dB gap at $\mathrm{BER}=10^{-3}$, which outperforms the other methods evidently.

## V. Computational Complexity

In this section, we first analyze the complexity of each iteration in the proposed BD-NS-EPA detector in terms of multiplications (MULTs), additions (ADDs), comparisons (CMPs), divisions (DIVs) and exponentiations (EXPs), and then compare them with those of SOA detectors. Real value decomposition is employed first to map the complex operations into the real domain. After such preprocessing, W becomes a $2 M \times 2 M$ matrix while $\mathbf{b}$ and $\boldsymbol{\mu}$ are both $2 M \times$ 1 vectors.

## A. Complexity of BD-NS-EPA Detector

1) INF Optimization: As shown in the line 6 of Alg. 3, since the number of MULTs needed to compute the $\alpha_{\text {opt }}^{+} \cdot \mathbf{D}_{(1, i)}$ is $4 m_{\mathrm{UE}}^{2}$, this unit requires $\mathcal{O}\left(M m_{\mathrm{UE}}\right)$ MULTs totally.
2) Cholesky Inversion: As presented in the line 7 of Alg. 3, for a sub-matrix with size $2 m_{\text {UE }} \times 2 m_{\text {UE }}$, Cholesky inversion requires $16 m_{\mathrm{UE}}^{3}+4 m_{\mathrm{UE}}^{2}$ MULTs, $16 m_{\mathrm{UE}}^{3}$ ADDs and $2 m_{\mathrm{UE}}$ DIVs. Therefore, the total number of MULTs, ADDs and DIVs is $\mathcal{O}\left(M m_{\mathrm{UE}}^{2}\right), \mathcal{O}\left(M m_{\mathrm{UE}}^{2}\right)$ and $\mathcal{O}(M)$, respectively.
3) Block Diagonal Neumann Iteration: As depicted in the line 9-11 of Alg. 3, first, to obtain $\Psi, \mathcal{O}\left(M^{2} m_{\text {UE }}\right)$ MULTs and ADDs are needed. Moreover, computing $\boldsymbol{\mu}^{(1)}$ brings about $\mathcal{O}\left(M m_{\text {ue }}\right)$ MULTs and $\mathcal{O}\left(M m_{\text {ue }}\right)$ ADDs. Next, in each iteration, the inner product between matrix $\Psi$ and column vector $\boldsymbol{\mu}$ brings $\mathcal{O}\left(M^{2}\right)$ MULTs and ADDs.
4) Compute $\boldsymbol{\xi}^{(0)}$ and Sorting: According to the line $12-13$ of Alg. 3, to calculate $\boldsymbol{\xi}^{(0)}, \mathcal{O}(M)$ MULTs, ADDs and DIVs are required. Further, the sorting needs $\mathcal{O}\left(M^{2}\right)$ CMPs. In addition, computing $1 / \mathrm{V}$ requires $\mathcal{O}(M)$ DIVs.
5) ASMU: The calculation corresponds to the line $14-20$ of Alg. 3 and for brevity, we first denote $1-(l-1) \kappa$ as $\delta_{l}$. Hence, in one iteration, the hard decision for $\boldsymbol{\eta}^{(l)}$ contributes $\mathcal{O}\left(\delta_{l} M \sqrt{\mathcal{Q}}\right)$ ADDs and CMPs. Moreover, computing $\boldsymbol{m}$ requires $\mathcal{O}\left(\delta_{l} M^{2}\right)$ MULTs and ADDs. Finally, calculating $\boldsymbol{\xi}^{(l)}$ needs $\mathcal{O}\left(\delta_{l} M\right)$ ADDs and MULTs.

Therefore, the overall number of MULTs and ADDs for the proposed BD-NS-EPA detector is concluded in Eq. (26) and Eq. (27), as shown at the bottom of the next page, respectively. Additionally, the BD-NS-EPA detector requires $\mathcal{O}(M)$ DIVs and $\mathcal{O}\left(\sum_{l} \delta_{l} M \sqrt{\mathcal{Q}}\right)$ CMPs.

## B. Complexity Comparisons

The computational complexity of different message-passing detectors is concluded in Table I. In the following, $Q$ denotes the $\sqrt{\mathcal{Q}}$. Further, $k$ denotes the number of Neumann iterations and $L$ denotes the number of iterations for the specific algorithm. Since all the discussed message passing algorithms requires to compute $\mathbf{H}^{H} \mathbf{H}$ and $\mathbf{H}^{H} \mathbf{y}$, the complexity is regarded as a common preprocessing thus being neglected.

The statistical results in Table I suggest the characteristics of different message-passing detectors. For the original EP, explicit matrix inversion takes part in initialization and each iteration, which brings $\mathcal{O}\left((L+1) M^{3}\right)$ MULTs. Further, EP-NSA initializes by exact matrix inversion and employ Neumann series to calculate the explicit inverse matrix in each iteration, hence it requires the MULTs of order $\mathcal{O}\left(M^{3}+L(k-\right.$ 2) $M^{3}$ ). As for EPA, it reformulates the EP moment matching process thus successfully eliminating the explicit matrix inversion during iterations, hence it consumes around $\mathcal{O}\left(M^{3}+\right. L M^{2}$ ) MULTs. Based on EPA, the EP-wNSA further exerts weighted Neumann series to simplify the matrix inversion in initialization. As a result, EP-wNSA requires the MULT operations of order $\mathcal{O}\left(k M^{2}+L M^{2}\right)$. Since the factor graph of BP detector is fully-connected, that is, there is message

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-09.jpg?height=562&width=1724&top_left_y=180&top_left_x=197)
Fig. 8. The BER performance of different detectors in MAUE systems with different propagation environments with 16-QAM modulation.

TABLE I
Complexity Comparison of the SOA Detectors
| Algorithm | Multiplications | Additions | Divisions | CMPs | EXPs |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EP [11] | $\mathcal{O}\left(M^{3}+M^{2}+L\left(M^{3}+M^{2}+M Q\right)\right)$ | $\mathcal{O}\left(M^{3}+M^{2}+L\left(M^{3}+M^{2}+M Q\right)\right)$ | $\mathcal{O}(L(M+M Q))$ | $\mathcal{O}(L M)$ | $\mathcal{O}(L M Q)$ |
| EP-NSA [17] | $\mathcal{O}\left(M^{3}+M^{2}+L\left((k-2) M^{3}+M^{2}+M Q\right)\right.$ | $\mathcal{O}\left(M^{3}+M^{2}+L\left((k-2) M^{3}+M Q\right)\right)$ | $\mathcal{O}(L(M+M Q))$ | 0 | $\mathcal{O}(L M Q)$ |
| EPA [21] | $\mathcal{O}\left(M^{3}+M^{2}+L\left(M^{2}+M Q\right)\right)$ | $\mathcal{O}\left(M^{3}+M^{2}+L\left(M^{2}+M Q\right)\right)$ | $\mathcal{O}(L M Q)$ | 0 | $\mathcal{O}(L M Q)$ |
| EP-wNSA [22] | $\mathcal{O}\left(k M^{2}+L M^{2}\right)$ | $\mathcal{O}\left((k-1) M^{2}+L\left(M^{2}+L M Q\right)\right)$ | $\mathcal{O}(M)$ | $\mathcal{O}(L M Q)$ | 0 |
| BP [34] | $\mathcal{O}(L(N M Q+N M))$ | $\mathcal{O}(L(N M Q+N M))$ | $\mathcal{O}(L M N Q)$ | $\mathcal{O}(N M Q)$ | $\mathcal{O}(L N M Q)$ |
| LAMA [9] | $\mathcal{O}(L(N M+M Q))$ | $\mathcal{O}(L(N M+M Q))$ | $\mathcal{O}(L M Q)$ | 0 | $\mathcal{O}(L M Q)$ |
| CHEMP [8] | $\mathcal{O}\left(L\left(M^{2}+M Q\right)\right)$ | $\mathcal{O}\left(L\left(M^{2}+M Q\right)\right)$ | $\mathcal{O}(L M Q)$ | $\mathcal{O}(M Q)$ | $\mathcal{O}(L M Q)$ |
| BD-NS-EPA | $\mathcal{O}\left(M^{2} m_{\mathrm{UE}}+k M\left(M-m_{\mathrm{UE}}\right)+\sum_{l} \delta_{l} M^{2}\right)$ | $\mathcal{O}\left(M^{2} m_{\mathrm{UE}}+k M\left(M-m_{\mathrm{UE}}\right)+\sum_{l} \delta_{l} M^{2}\right)$ | $\mathcal{O}(M)$ | $\mathcal{O}\left(\sum_{l} \delta_{l} M Q\right)$ | 0 |


passing between any receiving and transmitting antennas, which brings $\mathcal{O}(L M N Q)$ complexity. Further, by exerting the Gaussian assumption for the marginal densities of the messages, LAMA simplifies the sum-product message-passing computations and requires MULTs of only $\mathcal{O}(L N M)$, but still consumes extensive EXPs, with order of $\mathcal{O}(L M Q)$. Moreover, through exploiting the channel hardening property [36], CHEMP further simplifies the computations for the mean and variance of the interference-plus-noise term, thus requiring $\mathcal{O}\left(L M^{2}\right)$ complexity.

Compared with other algorithms, the proposed BD-NS-EPA requires no exponential operation and only $\mathcal{O}(M)$ divisions. Moreover, compared to EP, EP-NSA and EPA, the BD-NS-EPA takes only $\mathcal{O}\left(\left(m_{\mathrm{UE}}+\sum_{l} \delta_{l}\right) M^{2}\right)$ MULTs and $\mathcal{O}\left(\left(m_{\mathrm{UE}}+\sum_{l} \delta_{l}\right) M^{2}\right)$ ADDs.

The complexity-performance trade-off for the numerical tests under different correlation scenarios is provided in Fig. 9 for a further comparison of the algorithm efficiency. In the graphs, the performance of EP is regarded as the benchmark, while the SNR loss of each algorithm compared to the EP is exhibited in the horizontal axis at the specific BER. The vertical axis represents the normalized complxity of algorithms. Here we employ the arithmetic complexity model [37] to normalize the complexity for different kinds of operations. From Fig. 9(a), we notice that in MAUE system with IPE, CHEMP can outperform BD-NS-EPA slightly with comparable computational cost. However, with the correlation
increasing, CHEMP with 10 iterations is unable to converge, as revealed in Fig. 8(b). Further, it can be observed from Fig. 9(a) that EP-wNSA consumes similar complexity to the proposed algorithm but exhibits the performance far from satisfying. Additionally, the proposed algorithm can achieve evident advantages especially for the scenarios in high correlation, as depicted in Figs. 9(b), 9(c), 9(d), 9(e) and 9(f).

## VI. Hardware Implementation

We next show that the BD-NS-EPA detector can be implemented on hardware, verifying its relevance in practice. The architecture is designed for a case study of a 64-QAM $128 \times 32$ L-MIMO system, with $m=16$ and $m_{\mathrm{UE}}=2$. Additionally, to ensure acceptable results, the iteration numbers are set as $L=4, k=6$ and the pruning degree is $\kappa=0.05$.

## A. Hardware Architecture of BD-NS-EPA Detector

Based on the Alg. 3, the overall architecture of BD-NS-EPA is illustrated in Fig. 10, which consists of five main units:

1) Preprocessing Unit (PU): In this unit, the channel matrix $\mathbf{H}$ and received vector $\mathbf{y}$ are processed to provide the Gram matrix $\mathbf{W}$ that can be split as $\mathbf{W}=\mathbf{D}+\mathbf{E}$, and the matched vector $\mathbf{b}$. It is noteworthy that in the proposed BD-NS-EPA, the matrix $\mathbf{D}$ consists of all $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$ block diagonal elements of $\mathbf{W}$.

Considering $\mathbf{W}$ exhibits Hermitian property, in matrix multiplier module, a lower triangular systolic array

$$
\begin{align*}
C_{\mathrm{mul}} & \propto \mathcal{O}\left(M^{2} m_{\mathrm{UE}}+M m_{\mathrm{UE}}^{2}+M m_{\mathrm{UE}}+M+k M\left(M-m_{\mathrm{UE}}\right)+\sum_{l=1}^{L} \delta_{l}\left(M^{2}+M\right)\right)  \tag{26}\\
C_{\mathrm{addition}} & \propto\left(M^{2} m_{\mathrm{UE}}+M m_{\mathrm{UE}}^{2}+M m_{\mathrm{UE}}-M^{2}+k M\left(M-m_{\mathrm{UE}}\right)+\sum_{l=1}^{L} \delta_{l}\left(M^{2}+M \sqrt{\mathcal{Q}}+M\right)\right) \tag{27}
\end{align*}
$$

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-10.jpg?height=1004&width=811&top_left_y=197&top_left_x=199)
Fig. 9. Comparison of the complexity to BER performance trade-off for different detectors. Exact EP is set as the performance benchmark to evaluate the SNR loss of each algorithm. BP and CHEMP are not compared in sub-figures (b), (d), (e), (f) and EP-NSA, EP-wNSA are not compared in sub-figures (e), (f) due to their highly-degraded performance which fails to converge to the specific BER level.

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-10.jpg?height=463&width=669&top_left_y=1456&top_left_x=270)
Fig. 10. Overall diagram of the proposed BD-NS-EPA detector.

(LTSA) including $(M+1)\lceil M / 2\rceil$ processing elements (PEs), which is depicted in Fig. 11, is employed to calculate it. The LTSA reads the specific entries of the rows of matrix $\mathbf{H}$ at a time and delivers the elements of the Gram matrix after $N$ clock cycle. Further, to obtain the regularized Gram matrix $\mathbf{W}$, the regularization term $\sigma_{n}^{2} \operatorname{diag}(\boldsymbol{\Lambda})$ is added to the diagonal of $\mathbf{A}$ in the regularization module. After that, the scaling module that consists of $M$ real multipliers and $M\left(m_{\text {UE }}-1\right) / 2$ real-complex multipliers (RCMs) normalizes the $\mathbf{D}$ with the factor $\alpha_{\mathrm{opt}}^{+} \sigma_{n}^{2}$.

The matched filter (MF) module is composed of a linear array (LA) that includes $M$ PEs, each of which is related to a row of $\mathbf{H}^{H}$ and executes the multiple-accumulate operations. Specifically, in each clock cycle, the MF module reads a new y element and multiplies it with the input of

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-10.jpg?height=345&width=670&top_left_y=201&top_left_x=1185)
Fig. 11. Architecture of the LSTA in BD-NS-EPA detector.

$\mathbf{H}^{H}$ in each PE, then accumulates each product with the corresponding previous results.
2) BD-Iteration Unit: This unit is capable of performing various $k$ BD-based Neumann iterations to obtain the $\boldsymbol{\mu}^{(k)}$. First, the sub-matrices $\mathbf{D}$ after scaling are send to BD-matrix inversion to execute Cholesky-based inversion. Next, the matrix multiplier used in PU is reused here to calculate $\mathbf{D}^{-1} \mathbf{W}$. Please note since $\mathbf{D}^{-1} \mathbf{W}$ is not Hermitian, the matrix multiplier calculates the upper and lower triangular parts of $\mathbf{D}^{-1} \mathbf{W}$ separately. Then, the diagonal matrix subtracter computes the $\mathbf{I}-\mathbf{D}^{-1} \mathbf{W}$, i.e., $\boldsymbol{\Psi}$. Finally, with the aid of a vector adder, the matched filter utilized in PU is reused again to perform the block diagonal Neumann iteration. The BD-matrix inversion module will be discussed later.
3) Sorting Unit: This unit, consisting of $M / 2 \cdot \log _{2} M$ comparators, employs the bitonic sorting to adjust the diagonal elements of $\mathbf{D}^{-1}$ in descending order.
4) $\boldsymbol{\xi}$-Initialization Unit: This unit initializes $\boldsymbol{\xi}^{(0)}$ with the $\boldsymbol{\mu}^{(k)}$ from BD-Iteration unit and the $\boldsymbol{\Sigma}_{d}$ from sorting unit. Firstly, diagonal matrix subtracter module is reused to calculate $1-\boldsymbol{\Sigma}_{d}$. Next, $2 M$ dividers are introduced to compute the $\boldsymbol{\xi}^{(0)}$.
5) ASMU Unit: Consisting of index choose, hard decision, $m$ updating and cavity marginal updating, this unit targets at updating the mean $\boldsymbol{\eta}$ of replacement distribution by the mean $\boldsymbol{\xi}$ of cavity distribution. Specifically, as illustrated in Fig. 12, this unit employs fully parallel mode to reduce iteration latency. The $m$ updating is composed of one subtractor and one PE that contains a complex multiplier plus a complex adder. Additionally, the cavity marginal updating requires three real-complex multipliers, two complex adders and one D flip-flop. It is noteworthy that to execute partial updating, the control module firstly outputs $M$ enable signals each with $L$ bit-width, according to the set pruning degree $\kappa$ and the output results of sorting unit. Then, the ASMU unit executes iterations according to the enable signals. Specifically, if the $j$-th bit of the $i$-th enable signal is 1 , the corresponding $i$-th calculation modules are activated to perform computation on this variable, where $j$ means the enable signal for the $j$-th iteration. Otherwise, the iteration for the $i$-th variable is stopped and the result is output.

## B. BD-Matrix Inversion Based on Cholesky

Since the BD sub-matrices all exhibit Hermitian, Cholesky algorithm is employed to compute their inversions. Based on the work [38], the overall block diagram for the Cholesky implementation is depicted in Fig 13, which contains a decomposition unit and a forward/backward (Forw./Backw.) substitution unit (FBSU). First, an upper-triangular systolic array is

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-11.jpg?height=188&width=684&top_left_y=197&top_left_x=264)
Fig. 12. Architecture of the $m$ updating and cavity marginal updating.

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-11.jpg?height=375&width=566&top_left_y=504&top_left_x=322)
Fig. 13. The VLSI architecture of Cholesky algorithm (Conj.=Conjugate).

employed to decompose the sub-matrix $\mathbf{D}_{(1, t)}$ to obtain the lower-triangular matrix $\mathbf{L}_{t}$. The systolic array adopts the same design as our previous work [24], which consists of several distinct PEs on the diagonal and off-diagonal. Next, $\mathbf{D}_{(1, t)}^{-1}$ is computed by the FBSU. Specifically, the forward substitution unit (FSU) solves for $\mathbf{L}_{t} \mathbf{u}_{i}=\mathbf{e}_{i}$ and the backward substitution unit (BSU) solves for $\mathbf{L}_{t}^{H} \mathbf{v}_{i}=\mathbf{u}_{i}$, where $\mathbf{v}_{i}$ designates the $i$-th column vector in $\mathbf{D}_{(1, t)}^{-1}$. Considering the FSU of solving $\mathbf{L}_{t} \mathbf{u}_{i}=\mathbf{e}_{i}$ for each $\mathbf{e}_{i}\left(i=1, \cdots, m_{\mathrm{UE}}\right)$ is independent, we utilize $m_{\text {UE }}$ processor elements for substitution (S-PEs) to compute all $\mathbf{u}_{i}$ in parallel. Additionally, since the structure of equations to be solved by FSU and BSU is identical, the S-PEs for FSU are reused for BSU. For convenience, in Fig. 13, we uniformly describe the equation solved by the S-PEs as $\mathbf{L x}=\mathbf{b}$. Specifically, each S-PE, containing two complexvalued multipliers, one complex-valued adder and a complexvalued subtractor, computes either $\delta_{i}=b_{i}-\sum_{j} L_{i, j} x_{j}$ or $\delta_{i}=b_{1} / L_{i, i}$ according to the control signals.

## C. Data-Flow Graph (DFG) Analysis

The DFG shown in Fig. 14 reveals the dependence of nodes in Fig. 10, in which the number in parentheses indicates the clock cycles (CCs) required by the node for its calculation. It is noticed that there are three iteration loops in the DFG:
$l_{1}=$ Node $5 \rightarrow$ Node 5 ,
$l_{2}=$ Node $5 \rightarrow$ Node $6 \rightarrow$ Node 5 ,
$l_{3}=$ Node $8 \rightarrow$ Node $9 \rightarrow$ Node $10 \rightarrow$ Node $11 \rightarrow$ Node 8.
Since the iteration numbers of loops $l_{1}, l_{2}$ and $l_{3}$ are 1 , 6 and 4 respectively, the corresponding iteration latency is $T_{l_{1}}=M+1, T_{l_{2}}=6(M+2)$ and $T_{l_{3}}=4(M+4)$. It can be observed that the key that restricts the system throughput lies in the iteration loop $l_{2}$.

To this end, the architecture for iteration $l_{2}$ is unfolded, the 2 -unfolded version is depicted in Fig. 15. As a result, the latency of the 2 -unfolded architecture becomes $T_{l_{2}}^{*}=3(M+2)$, which is lower than the calculation latency of iteration loop $l_{3}$. It is noted that the hardware cost of unfolding $l_{3}$ is expensive due to more computation modules in the ASMU unit. Additionally, our pruning algorithm can effectively reduce the

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-11.jpg?height=375&width=502&top_left_y=195&top_left_x=1267)
Fig. 14. DFG of the proposed BD-NS-EPA detector.

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-11.jpg?height=185&width=796&top_left_y=653&top_left_x=1121)
Fig. 15. The BD-iteration module after 2-unfolding.

average latency of $l_{3}$, hence the architecture of iteration loop $l_{3}$ is not unfolded.

## D. Timing Analysis

The overall time schedule of the BD-NS-EPA detector with $m_{\mathrm{UE}}=2$ is illustrated in Fig. 16. In the PU, the computations for $\mathbf{b}$ and $\mathbf{W}$ requires $(N+1)$ and $(N+2 M)$ CCs respectively. After the $\mathbf{D}$ is obtained, the BD inversion modules start working and complete the calculation after 66 CCs. Next, the sorting module begins working to sort the diagonal elements of $\mathbf{D}^{-1}$ in descending order and MF is reused to calculate $\boldsymbol{\mu}^{(1)}$. Meanwhile, the LTSA is reused to compute $\Psi=\mathbf{D}^{-1} \mathbf{W}$, which requires ( $2 M+4 m_{\mathrm{UE}}-1$ ) CCs to obtain all results. Then, the MF is reused again to perform block-diagonal Neumann iteration that consumes ( $M+2$ ) CCs for each iteration. After that, $\boldsymbol{\xi}$-Initialization unit processes the $M$ components of $\boldsymbol{\mu}^{(k)}$ in parallel, which consumes 10 CCs. Finally, the ASMU unit performs iterations and outputs the estimated vector.

## E. Implementation Results

To demonstrate the efficiency of the BD-NS-EPA detector, it is implemented on SMIC 65 nm 1P9M CMOS process, synthesized by Synopsys Design Compiler, and placed/routed by IC Complier. The layout photo and implementation results are depicted in Fig. 17. It is noted that no power straps are built in the layout. Fixed-point simulation is performed: the real and imaginary parts of the complex data are each quantized to 11 bits averagely. As illustrated in Fig. 18, the performance loss from the floating-point version of the fixed design is acceptable in MAUE system with IPE, NPE and BPE. Further, the throughput of the detector is formulated as:

$$
\begin{equation*}
\text { Throughput [Gbps] }=\frac{\log _{2} \mathcal{Q} \times M}{\mathbb{E}\left[T_{\text {cycle }}\right]} \times f_{\text {clk }}, \tag{28}
\end{equation*}
$$

where $\mathcal{Q}$ denotes the constellation size, $M$ represents the number of users, $f_{\text {clk }}$ is the clock frequency, and $\mathbb{E}\left[T_{\text {cycle }}\right]$ denotes the average number of execution clock cycles required to detect a symbol vector. It is noteworthy that in this implementation, the execution clock cycles are determined by the iteration loop $l_{3}$, and independent of the value of $m_{\mathrm{UE}}$.

The comparisons of the proposed design with EP-wNSA detector [22], MMSE detector [39], CHEMP detector [40],

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-12.jpg?height=343&width=1569&top_left_y=201&top_left_x=277)
Fig. 16. The processing schedule of the proposed BD-NS-EPA detector.

TABLE II
Implementation Results and Comparison for Different MIMO Detectors
| Detector | This work |  | X. Tan [22] [TCAS-II'21] | H. Prabhu [39] [ISSCC'17] | W. Tang [40] [VLSI-Circuits'16] | W. Tang [33] [ISSCC'18] | H. Wang [24] [TSP'21] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Algorithm | BD-NS-EPA |  | EP-wNSA | MMSE | CHEMP | EPD | TL-BD-INSA |
| Antenna Configuration | $128 \times 32$ |  | $128 \times 32$ | $128 \times 8$ | $128 \times 32$ | $128 \times 16$ | $128 \times 8$ |
| Modulation | 64-QAM |  | QPSK to 256-QAM | 256-QAM | 256-QAM | QPSK to 256-QAM | 64-QAM |
| Preprocessing Unit | Included |  | Included | Included | Not Included | Not Included | Included |
| Technology [ nm ] \& Voltage [V] | 65 @ 1.0 |  | 65 @ 1.0 | 28 @ 0.9 | 40 @ 0.9 | 28 @ 1.0 | 45 @ 0.8 |
| Iterative number | $L=4, k=6$ |  | $L=10, k=10$ | NA | $L=10$ | $L=4$ | $k=4$ |
| Result type | Layout ${ }^{(1)}$ | Layout | Layout | Chip ${ }^{(2)}$ | Chip | Chip | Systhesis |
| Prunning | $\kappa=0$ | $\kappa=0.05$ | w/o | w/o | w/o | w/o | w/o |
| $E_{\mathrm{b}} / N_{0} @ \mathrm{BER}=10^{-3(3)}$ | 15.5 | 15.7 | 16.7 | 16.9 | NA ${ }^{(4)}$ | 15.3 | 18.2 |
| Gate Count [kGE] | 2,524 ${ }^{(5)}$ | 2,595 ${ }^{\text {(5) }}$ | 2,364 | 148 | 1, 167 | 3,607 | 572 |
| Area [ $\mathrm{mm}^{2}$ ] | 2.83 | 2.91 | 2.65 | 1.10 | 0.58 | 2.00 | 0.40 |
| Frequency [MHz] | 500 | 500 | 500 | 300 | 425 | 569 | 1,000 |
| Power [mW] | 549 | 571 | 955 | 18 | 221 | 127 | 144 |
| Throughput [Gbps] | 0.667 | 0.715 | 0.860 | 0.300 | 2.76 | 1.80 | 0.185 |
| Energy Eff. ${ }^{\text {(6) }}$ [Gbps/W] | 1.215 | 1.252 | 0.901 | 16.67 | 12.49 | 14.17 | 1.284 |
| Area Eff. ${ }^{(6)}$ [Mbps/kGE] | 0.264 | 0.275 | 0.363 | 2.027 | 2.365 | 0.499 | 0.323 |
| Scaled ${ }^{77}$ Energy Eff. [Gbps/W] | 1.215 | 1.252 | 0.901 | 2.505 | 3.831 | 2.630 | 0.394 |
| Scaled ${ }^{(6)}$ Area Eff. [Mbps/kGE] | 0.264 | 0.275 | 0.363 | 0.873 | 1.455 | 0.215 | 0.224 |


${ }^{(1)}$ Layout with post-layout simulation results. ${ }^{(2)}$ Chip with measurement results. ${ }^{(3)}$ Obtained under channel 5 with floating-point $\left(m_{\mathrm{UE}}=2\right)$. ${ }^{(4)}$ Fails to converge.
${ }^{(5)}$ Estimated by 2 -input NAND gates, and the area of a gate is $1.12 \mathrm{um}^{2}$. ${ }^{(6)}$ Energy efficiency=throughput/power, area efficiency=throughput/gate count.
${ }^{77}$ There are two kinds of normalizaed aspects: 1) Scaled to 65 nm and 1.0 V CMOS process with frequency $\propto s$, area $\propto 1 / s^{2}$ and power $\propto(1 / s)\left(1.0 / V_{d d}\right)^{2}$, where $s=$ Tech $/ 65 \mathrm{~nm}$. 2) Normalizaed to $128 \times 32$ configuration: throughput $\propto \frac{32}{M} \times \frac{\log _{2} M}{\log _{2} 32}$, and power and area $\propto \frac{128}{N} \times \frac{32}{M} \times \frac{\log _{2} M}{\log _{2} 32}$ [41, 42].

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-12.jpg?height=343&width=674&top_left_y=1602&top_left_x=268)
Fig. 17. Layout and implementation results of the BD-NS-EPA detector.

EPD [33] and TL-BD-INSA detector [24] are concluded in Table II. Their performance in channel 5 with $m_{\mathrm{UE}}=2$, 64-QAM is also shown in the Table II. Above all, it can be noticed that compared with the design without pruning ( $\kappa=0$ ), although the introduction of pruning ( $\kappa=0.05$ ) results in extra area overhead on the sorting unit, as revealed by the area breakdown results in Table III, it can effectively achieve $1.03 \times$ and $1.04 \times$ energy and area efficiency, owing to the reduced average latency. Further, the BD-NS-EPA detector can exhibit around 1 dB performance advantage, compared to the EP-wNSA detector. Additionally, the proposed detector achieves higher hardware efficiency and better performance than the TL-BD-NSA detector. The hardware advantages mainly come from three aspects: i) The reuse of the $32 \times 32$

![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-12.jpg?height=528&width=654&top_left_y=1602&top_left_x=1192)
Fig. 18. Fixed-point performance of the proposed BD-NS-EPA detector.

LTSA in PU and BD-Iteration unit; ii) The reuse of the MF in PU, BD-Iteration unit and ASMU unit; iii) The overall pipelined structure and the 2-unfolded BD-Iteration architecture to improve the system frequency. Although the EPD can yield the best performance, it requires the implementation for the inversion of an $M$-order matrix, and this inversion process must be performed in each iteration. Hence, even without implementing the preprocessing module, its area efficiency is merely $78 \%$ of ours. Furthermore, it is worth mentioning

TABLE III
Detailed Area Breakdown of the Different Functional Units
| BD-NS-EPA | No pruning |  | Pruning |  |
| :--- | :--- | :--- | :--- | :--- |
|  | [kGE] | [\%] | [kGE] | [\%] |
| Preprocessing unit | 1564 | 62.0 | 1564 | 60.3 |
| BD iteration unit | 424.2 | 16.8 | 424.2 | 16.3 |
| Sorting unit | NA | NA | 65.80 | 2.53 |
| $\xi$ Initialization unit | 50.80 | 2.0 | 50.80 | 1.96 |
| ASMU unit | 71.90 | 2.8 | 72.85 | 2.81 |
| Control logic \& Memory | 412.7 | 16.4 | 417.2 | 16.1 |
| Total | 2523.6 | 100 | 2594.8 | 100 |


${ }^{\dagger}$ The number of logic gate consumption of a Cholesky inversion is 12.04 kGE .
that although the MMSE detector and CHEMP detector are more efficient in energy and area efficiencies than the proposed design, as presented in Section IV and the line 10 of Table II, they are unable to provide satisfactory error-rate performance under the challenging correlated MAUE channels. Therefore, the implemented results further prove the BD-NS-EPA detector is able to achieve an overall superior tradeoff between error performance and hardware efficiency.

## VII. Conclusion

In this paper, a novel BD-NS-EPA detector is proposed, which achieves enhanced performance in both uncorrelated and challenging correlated L-MIMO channels at the cost of moderate computational complexity. Numerical results are presented to validate the practical advantages of the proposed method. The implementation results on ASIC further exhibit its practical applicability and ability to achieve a well trade-off between error-rate performance and complexity.

For future work, a rigorous error-rate performance analysis of the proposed algorithm is an open question. Second, the extension of the proposed algorithm to the decentralized processing architectures [43], [44] is also a direction worth pursuing. In this work, the pruning degree is empirical and determined by simulations. How to utilize neural networks to find the optimal value is left for future work.

## References

[1] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays," IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40-60, Jan. 2013.
[2] T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Trans. Wireless Commun., vol. 9, no. 11, pp. 3590-3600, Nov. 2010.
[3] J. Hoydis, S. T. Brink, and M. Debbah, "Massive MIMO in the UL/DL of cellular networks: How many antennas do we need?" IEEE J. Sel. Areas Commun., vol. 31, no. 2, pp. 160-171, Feb. 2013.
[4] X. Gao, L. Dai, Y. Hu, Y. Zhang, and Z. Wang, "Low-complexity signal detection for large-scale MIMO in optical wireless communications," IEEE J. Sel. Areas Commun., vol. 33, no. 9, pp. 1903-1912, Sep. 2015.
[5] D. Shnidman, "A generalized Nyquist criterion and an optimum linear receiver for a pulse modulation system," Bell Syst. Tech. J., vol. 46, no. 9, pp. 277-2163, 1967.
[6] G. Peng, L. Liu, S. Zhou, S. Yin, and S. Wei, "A $1.58 \mathrm{Gbps} / \mathrm{W} 0.40 \mathrm{Gbps} / \mathrm{mm}^{2}$ ASIC implementation of MMSE detection for $128 \times 8$ 64-QAM massive MIMO in 65 nm CMOS," IEEE Trans. Circuits Syst. I, Reg. Papers, vol. 65, no. 5, pp. 1717-1730, May 2018.
[7] W. van Etten, "An optimum linear receiver for multiple channel digital transmission systems," IEEE Trans. Commun., vol. COM-23, no. 8, pp. 828-834, Aug. 1975.
[8] T. L. Narasimhan and A. Chockalingam, "Channel hardening-exploiting message passing (CHEMP) receiver in large-scale MIMO systems," IEEE J. Sel. Topics Signal Process., vol. 8, no. 5, pp. 847-860, Oct. 2014.
[9] C. Jeon, R. Ghods, A. Maleki, and C. Studer, "Optimality of large MIMO detection via approximate message passing," in Proc. IEEE Int. Symp. Inf. Theory (ISIT), Jun. 2015, pp. 1227-1231.
[10] P. Som, T. Datta, A. Chockalingam, and B. S. Rajan, "Improved largeMIMO detection based on damped belief propagation," in Proc. IEEE Inf. Theory Workshop (ITW), Jan. 2010, pp. 1-5.
[11] J. Céspedes, P. M. Olmos, M. Sánchez-Fernández, and F. Perez-Cruz, "Expectation propagation detection for high-order high-dimensional MIMO systems," IEEE Trans. Commun., vol. 62, no. 8, pp. 2840-2849, Aug. 2014.
[12] D. J. Jakubisin, R. M. Buehrer, and C. R. C. M. da Silva, "BP, MF, and EP for joint channel estimation and detection of MIMO-OFDM signals," in Proc. IEEE Global Commun. Conf. (GLOBECOM), Dec. 2016, pp. 1-6.
[13] S. Sahin, C. Poulliat, A. M. Cipriano, and M.-L. Boucheret, "Spectrally efficient iterative MU-MIMO receiver for SC-FDMA based on EP," in Proc. IEEE 29th Annu. Int. Symp. Pers., Indoor Mobile Radio Commun. (PIMRC), Sep. 2018, pp. 1-7.
[14] X. Meng, S. Wu, L. Kuang, and J. Lu, "An expectation propagation perspective on approximate message passing," IEEE Signal Process. Lett., vol. 22, no. 8, pp. 1194-1197, Aug. 2015.
[15] C. Zhang, Z. Wu, C. Studer, Z. Zhang, and X. You, "Efficient soft-output Gauss-Seidel data detector for massive MIMO systems," IEEE Trans. Circuits Syst. I, Reg. Papers, vol. 68, no. 12, pp. 5049-5060, Dec. 2021.
[16] B. Yin, M. Wu, J. R. Cavallaro, and C. Studer, "Conjugate gradientbased soft-output detection and precoding in massive MIMO systems," in Proc. IEEE Global Commun. Conf., Dec. 2014, pp. 3696-3701.
[17] Y. Zhang, Z. Wu, C. Li, Z. Zhang, X. You, and C. Zhang, "Expectation propagation detection with Neumann-series approximation for massive MIMO," in Proc. IEEE Int. Workshop Signal Process. Syst. (SiPS), Oct. 2018, pp. 59-64.
[18] X. Tan, W. Xu, Y. Zhang, Z. Zhang, X. You, and C. Zhang, "Efficient expectation propagation massive MIMO detector with Neumann-series approximation," IEEE Trans. Circuits Syst. II, Exp. Briefs, vol. 67, no. 10, pp. 1924-1928, Oct. 2020.
[19] G. Yao, G. Yang, J. Hu, and C. Fei, "A low complexity expectation propagation detection for massive MIMO system," in Proc. IEEE Global Commun. Conf. (GLOBECOM), Dec. 2018, pp. 1-6.
[20] G. Yao, G. Yang, J. Hu, and C. Fei, "High-efficiency expectation propagation detector for high-order massive MIMO systems," IEEE Access, vol. 7, pp. 125225-125239, 2019.
[21] X. Tan, Y.-L. Ueng, Z. Zhang, X. You, and C. Zhang, "A lowcomplexity massive MIMO detection based on approximate expectation propagation," IEEE Trans. Veh. Technol., vol. 68, no. 8, pp. 7260-7272, Aug. 2019.
[22] X. Tan et al., "Approximate expectation propagation massive MIMO detector with weighted Neumann-series," IEEE Trans. Circuits Syst. II, Exp. Briefs, vol. 68, no. 2, pp. 662-666, Feb. 2021.
[23] Q. H. Spencer, A. L. Swindlehurst, and M. Haardt, "Zero-forcing methods for downlink spatial multiplexing in multiuser MIMO channels," IEEE Trans. Signal Process., vol. 52, no. 2, pp. 461-471, Feb. 2004.
[24] H. Wang et al., "An efficient detector for massive MIMO based on improved matrix partition," IEEE Trans. Signal Process., vol. 69, pp. 2971-2986, 2021.
[25] B. E. Godana and T. Ekman, "Parametrization based limited feedback design for correlated MIMO channels using new statistical models," IEEE Trans. Wireless Commun., vol. 12, no. 10, pp. 5172-5184, Oct. 2013.
[26] J. P. Kermoal, L. Schumacher, K. I. Pedersen, P. E. Mogensen, and F. Frederiksen, "A stochastic MIMO radio channel model with experimental validation," IEEE J. Sel. Areas Commun., vol. 20, no. 6, pp. 1211-1226, Aug. 2002.
[27] G. W. Stewart, Matrix Algorithms: Basic Decompositions, vol. 1. Philadelphia, PA, USA: SIAM, 1998.
[28] F. Wang, C. Zhang, J. Yang, X. Liang, X. You, and S. Xu, "Efficient matrix inversion architecture for linear detection in massive MIMO systems," in Proc. IEEE Int. Conf. Digit. Signal Process. (DSP), Jul. 2015, pp. 248-252.
[29] T. P. Minka, "Expectation propagation for approximate Bayesian inference," 2013, arXiv:1301.2294.
[30] H. Prabhu, O. Edfors, J. Rodrigues, L. Liu, and F. Rusek, "Hardware efficient approximative matrix inversion for linear pre-coding in massive MIMO," in Proc. IEEE Int. Symp. Circuits Syst. (ISCAS), Jun. 2014, pp. 1700-1703.
[31] H. Wu, J. Lin, C. Zhang, and Z. Wang, "Low-complexity detection algorithms based on matrix partition for massive MIMO," in Proc. 9th Int. Conf. Wireless Commun. Signal Process. (WCSP), Oct. 2017, pp. 1-6.
[32] D. S. Watkins, Fundamentals of Matrix Computations, vol. 64. Hoboken, NJ, USA: Wiley, 2004.
[33] W. Tang, H. Prabhu, L. Liu, V. Owall, and Z. Zhang, "A $1.8 \mathrm{~Gb} / \mathrm{s} 70.6 \mathrm{pJ} / \mathrm{b} 128 \times 16$ link-adaptive near-optimal massive MIMO detector in 28 nm UTBB-FDSOI," in IEEE Int. Solid-State Circuits Conf. (ISSCC) Dig. Tech. Papers, Feb. 2018, pp. 224-226.
[34] J. Yang, W. Song, S. Zhang, X. You, and C. Zhang, "Low-complexity belief propagation detection for correlated large-scale MIMO systems," J. Signal Process. Syst., vol. 90, no. 4, pp. 585-599, 2018.
[35] B. M. Hochwald and S. T. Brink, "Achieving near-capacity on a multiple-antenna channel," IEEE Trans. Commun., vol. 51, no. 3, pp. 389-399, Mar. 2003.
[36] B. M. Hochwald, T. L. Marzetta, and V. Tarokh, "Multiple-antenna channel hardening and its implications for rate feedback and scheduling," IEEE Trans. Inf. Theory, vol. 50, no. 9, pp. 1893-1909, Sep. 2004.
[37] R. P. Brent and P. Zimmermann, Modern Computer Arithmetic, vol. 18. Cambridge, U.K.: Cambridge Univ. Press, 2010.
[38] M. Wu, B. Yin, G. Wang, C. Dick, J. R. Cavallaro, and C. Studer, "Large-scale MIMO detection for 3GPP LTE: Algorithms and FPGA implementations," IEEE J. Sel. Topics Signal Process., vol. 8, no. 5, pp. 916-929, Oct. 2014.
[39] H. Prabhu, J. N. Rodrigues, L. Liu, and O. Edfors, "A $60 \mathrm{pJ} / \mathrm{b} 300 \mathrm{Mb} / \mathrm{s} 128 \times 8$ massive MIMO precoder-detector in 28 nm FD-SOI," in IEEE Int. Solid-State Circuits Conf. (ISSCC) Dig. Tech. Papers, Feb. 2017, pp. 60-61.
[40] W. Tang, C.-H. Chen, and Z. Zhang, "A $0.58 \mathrm{~mm}^{2} 2.76 \mathrm{~Gb} / \mathrm{s} 79.8 \mathrm{pJ} / \mathrm{b}$ 256-QAM massive MIMO message-passing detector," in Proc. IEEE Symp. VLSI Circuits (VLSI-Circuits), Jun. 2016, pp. 1-2.
[41] Y.-T. Chen, C.-C. Cheng, T.-L. Tsai, W.-C. Sun, Y.-L. Ueng, and C.-H. Yang, "A $501 \mathrm{~mW} 7.6 \mathrm{lGb} / \mathrm{s}$ integrated message-passing detector and decoder for polar-coded massive MIMO systems," in Proc. Symp. VLSI Circuits, Jun. 2017, pp. C330-C331.
[42] L. Liu et al., "Energy- and area-efficient recursive-conjugate-gradientbased MMSE detector for massive MIMO systems," IEEE Trans. Signal Process., vol. 68, pp. 573-588, 2020.
[43] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[44] J. Rodriguez Sanchez, F. Rusek, O. Edfors, M. Sarajlic, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms," IEEE Trans. Signal Process., vol. 68, pp. 687-700, 2020.
![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-14.jpg?height=332&width=263&top_left_y=1746&top_left_x=163)

Huizheng Wang received the B.S. and M.S. degrees in communication engineering from Southeast University (SEU), Nanjing, China, in 2019 and 2022, respectively. His research interests include efficient algorithms and VLSI architectures for massive MIMO detection, polar decoder, neural networks, and stochastic computing.
![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-14.jpg?height=324&width=257&top_left_y=2268&top_left_x=167)

Bingyang Cheng (Student Member, IEEE) received the B.S. degree in communication engineering from the Harbin Institute of Technology, Weihai, China, in 2019, and the M.S. degree in electronics and communication engineering from Southeast University, Nanjing, China, in 2022. His research interests include efficient MIMO detection algorithm, iterative MIMO detection, and channel decoding systems.
![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-14.jpg?height=319&width=255&top_left_y=216&top_left_x=1082)

Xiaosi Tan (Member, IEEE) received the Ph.D. degree from Texas A\&M University, College Station, TX, USA, in 2015. She was a Post-Doctoral Research Associate with Texas A\&M University from 2015 to 2017. She joined the National Mobile Communications Research Laboratory, School of Information Science and Engineering, Southeast University, Nanjing, China, as a Post-Doctoral Researcher, in 2017, where she is currently a Lecturer. Her current research interests include efficient algorithms and VLSI architectures for baseband signal processing, and machine learning for wireless communications.
![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-14.jpg?height=330&width=257&top_left_y=687&top_left_x=1080)

Xiaohu You (Fellow, IEEE) received the B.S., M.S., and Ph.D. degrees in electrical engineering from the Nanjing Institute of Technology, Nanjing, China, in 1982, 1985, and 1989, respectively. From 1987 to 1989, he was a Lecturer with the Nanjing Institute of Technology. Since 1990, he has been with Southeast University as an Associate Professor and then as a Professor. His research interests include mobile communications, adaptive signal processing, and artificial neural networks with applications to communications and biomedical engineering. He was the Premier Foundation Investigator of the China National Science Foundation. From 1999 to 2002, he was the Principal Expert of the C3G Project, responsible for organizing China's 3G mobile communications research and development activities. From 2001 to 2006, he was the Principal Expert of the National 863 FuTURE Project. He is currently the Chairperson of the IEEE Nanjing Section. He was selected as an IEEE Fellow in 2012 for his contributions to the development of mobile communications in China.
![](https://cdn.mathpix.com/cropped/66837fb7-9eaa-491e-9bb6-f144aeedabbc-14.jpg?height=323&width=255&top_left_y=1355&top_left_x=1082)

Chuan Zhang (Senior Member, IEEE) received the B.E. degree in microelectronics and the M.E. degree in very-large scale integration (VLSI) design from Nanjing University, Nanjing, China, in 2006 and 2009, respectively, and the M.S.E.E. and Ph.D. degrees from the Department of Electrical and Computer Engineering, University of Minnesota, Twin Cities (UMN), USA, in 2012.
He is currently the Young Chair Professor with Southeast University. He is also with the LEADS, National Mobile Communications Research Laboratory, Frontiers Science Center for Mobile Information Communications and Security of MoE, Quantum Information Center, Southeast University, and the Purple Mountain Laboratories, Nanjing. His current research interests are algorithms and implementations for signal processing and communication systems.

Dr. Zhang received the Best Contribution Award of the IEEE Asia Pacific Conference on Circuits and Systems (APCCAS) in 2018, the Best Paper Award in 2016, the Best (Student) Paper Award of the IEEE International Conference on DSP in 2016, three Best (Student) Paper Awards of the IEEE International Conference on ASIC in 2015, 2017, and 2019, the Best Paper Award Nomination of the IEEE Workshop on Signal Processing Systems in 2015, three Excellent Paper Awards and two Excellent Poster Presentation Awards of the International Collaboration Symposium on Information Production and Systems from 2016 to 2018, the Outstanding Achievement Award of the Intel Collaborative Research Institute in 2018, and the Merit (Student) Paper Award of the IEEE APCCAS in 2008. He also received the Three-Year University-Wide Graduate School Fellowship of UMN and the Doctoral Dissertation Fellowship of UMN. He serves as an Associate Editor for the IEEE Transactions on Circuits and Systems-II: Express Briefs. He served as an Associate Editor for the IEEE Transactions on Signal Processing and IEEE Open Journal of Circuits and Systems, and a Corresponding Guest Editor for the IEEE Journal on Emerging and Selected Topics in Circuits and Systems twice. He is also a Distinguished Lecturer and the Vice Chair of the Circuits and Systems for Communications TC of the IEEE Circuits and Systems Society. He is also a member of the Applied Signal Processing Systems TC of the IEEE Signal Processing Society, and Circuits and Systems for Communications TC, VLSI Systems and Applications TC, and Digital Signal Processing TC of the IEEE Circuits and Systems Society.


[^0]:    ${ }^{1}$ Since the regularization $\Lambda$ is relatively small, it would not change the BD property of matrix $\mathbf{W}$.

