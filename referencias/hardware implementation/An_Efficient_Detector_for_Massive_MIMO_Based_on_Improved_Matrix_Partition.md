# An Efficient Detector for Massive MIMO Based on Improved Matrix Partition 

Huizheng Wang ${ }^{(1)}$, Yahui Ji, Yifei Shen, Student Member, IEEE, Wenqing Song ${ }^{(1)}$, Student Member, IEEE, Muhao Li, Student Member, IEEE, Xiaohu You ${ }^{(1)}$, Fellow, IEEE, and Chuan Zhang ${ }^{(1)}$, Senior Member, IEEE


#### Abstract

Massive multiple-input multiple-output (M-MIMO) brings better robustness and spectral efficiency but higher computational challenges compared to small-scale MIMO. One of the key challenges is the large-scale matrix inversion, as widely employed in channel estimation and detection. Traditionally, to address the issue, several low-complexity matrix inversion methods have been proposed, including the tri-diagonal matrix approximation (TMA) and the Neumann-series approximation (NSA). Although the previous methods effectively alleviate the computational cost, they all fail to exploit the typical properties of channel matrices, leading to unsatisfactory error-rate performance in some non-ideal scenarios. To solve the issue, in this paper, a two-level and block diagonal based improved Neumann series approximation (TL-BD-INSA) algorithm is proposed, which is suitable for both ideal uncorrelated channels and the correlated channels with multiple-antenna user equipment (MAUE) system. First, a two-level block diagonal iteration based on matrix partition is employed, which exhibits performance comparable to the exact method while having a lower computational load. An improved normalization factor is then introduced to accelerate convergence. Numerical results show that, for $128 \times 32$ MIMO with MAUE non-ideal channel, the proposed algorithm performs only 0.25 dB away from the exact matrix inversion when bit error rate (BER) $=10^{-3}$. The implementation on Xilinx Virtex-7 FPGA and ASIC with TSMC 45 nm shows that the proposed detector can achieve $1731 \mathrm{bps} /$ slices and $0.463 \mathrm{Gbps} / \mathrm{mm}^{2}$ hardware efficiency, respectively, demonstrating that the proposed system can achieve a well trade-off between error performance and implementation efficiency.


Index Terms-Massive MIMO, matrix inversion, block diagonal matrix, Neumann series, FPGA, VLSI.

Manuscript received September 22, 2020; revised January 30, 2021; accepted February 22, 2021. Date of publication March 10, 2021; date of current version June 1, 2021. The associate editor coordinating the review of this manuscript and approving it for publication was Tokunbo Ogunfunmi. This work was supported in part by the National Key R\&D Program of China under Grant 2020YFB2205503, in part by NSFC under Grant 61871115, in part by the Jiangsu Provincial NSF for Excellent Young Scholars under Grant BK20180059, in part by the Six Talent Peak Program of Jiangsu Province under Grant 2018-DZXX-001, in part by the Distinguished Perfection Professorship of Southeast University, and in part by the Fundamental Research Funds for the Central Universities. (Corresponding author: Chuan Zhang.)

Huizheng Wang, Yifei Shen, Muhao Li, Xiaohu You, and Chuan Zhang are with the LEADS of Southeast University, the National Mobile Communications Research Laboratory of Southeast University, and the Purple Mountain Laboratories, Nanjing 211189, China (e-mail: 15651771920@163.com; 597592813@qq.com; limuhao_2006@126.com; xhyu@seu.edu.cn; chzhang @ seu.edu.cn).

Yahui Ji is with the Institute of Microelectronics, Tsinghua University, Beijing 100084, China (e-mail: jyh@seu.edu.cn).

Wenqing Song is with the School of Electronic Science and Engineering, Nanjing University, Nanjing 210023, China (e-mail: asrswq@126.com).

Digital Object Identifier 10.1109/TSP.2021.3064781

## I. Introduction

MASSIVE multiple-input multiple-output (M-MIMO), as an emerging technology to meet the higher data rate demand, is a key technology for the fifth generation wireless communication system [1], [2]. By adding multiple antennas in an M-MIMO system, degrees of freedom in wireless channel can be obtained to accommodate more information data simultaneously, offering better reliability, spectral efficiency and energy efficiency compared with the traditional small-scale MIMO [3]-[5].

Unfortunately, the benefits of M-MIMO come at the expense of significantly increased computational complexity in base stations (BSs). One of the most critical issues is the low-complexity detection algorithm in uplink and downlink directions, since the presence of numerous antennas requires detection algorithms that scale favorably to high dimension [1].

The optimal detector is a nonlinear maximum-likelihood (ML) detector. However, its complexity increases exponentially with the increase of transmitting antennas, which hinders its implementation in practical MIMO system [6]. The sphere decoding (SD) detector [7] and $K$-best detector [8] are two variants of ML detector, which can balance computational complexity and performance by controlling the number of nodes in each search phase. Unfortunately, the QR decomposition in these nonlinear detectors results in high computational complexity and low parallelism due to the inclusion of unfavorable matrix operations such as element elimination.

In contrast, sub-optimal linear detectors, such as minimum mean square error (MMSE) [9] and zero-forcing (ZF) [10], are able to better trade off the performance with computational complexity. Compared to the aforementioned nonlinear methods or other more complex methods, such as belief propagation (BP) [11], [12] and iterative solvers [13], [14], the linear detection methods are especially applicable to practical systems not only for their low-complexity and convenient implementation but also for their near-optimal performance [1]. Furthermore, on condition that the number of BS antennas ( $N$ ) is much larger than that of user antennas ( $M$ ), i.e., $N \gg M$, the linear detections are one of the best choices to balance the performance and complexity [1].

Therefore, recent works [15]-[20] studied the linear precoding and linear detection on the premise of optimistic assumption about the propagation environment and the number of antennas. However, a challenging issue is the computational load of matrix inversion required in linear detections is generally an operation of complexity $\mathcal{O}\left(K^{3}\right)$ ( $K$ is the size of the matrix) [21], which is not practical for many real-time solutions. To reduce the complexity of matrix inversion, the Neumann series based
approximate (NSA) algorithm which utilizes the property of channel hardening [22], has been proposed for M-MIMO uplink signal detection [19]. Furthermore, several low-complexity inverse algorithms based on NSA are developed, such as matrix partition (MP) [23] and tridiagonal matrix inversion approximate (TMA) [17], [24]. Moreover, some works [25]-[28] introduce a normalization factor or polynomial coefficient to guarantee and accelerate the convergence of NSA iteration. Additionally, some linear iteration methods, including GaussSeidel (GS) [29] and conjugate gradient (CG) [30], are employed to avoid large matrix inversion.

However, most of the works mentioned above aim at singleantenna user equipment (SAUE) system and assume that the entries of channel matrix are independent and identically distributed (i.i.d.) and follow the Gaussian distribution. Unfortunately, in practice, a user usually equips with several antennas and the transmitted vectors from the same user are correlated generally because the antennas from the same user equipment (UE) are insufficiently separated [31]. The spatial correlation between antennas is a critical factor that influences the performance of M-MIMO systems, for the number of antennas soars to an unprecedented magnitude [1]. However, to the best of the authors' knowledge, for the scenarios of less favorable propagation environment where channel is of high correlation and each UE is equipped with multiple-antennas, the study in low-complexity matrix inversion and its efficient hardware implementation have not been investigated.

In this paper, an efficient low-complexity M-MIMO detection algorithm based on matrix partition is proposed. The main contributions of this work include:

- Targeting correlated channels with multiple-antenna user equipment (MAUE) system, a low-complexity linear MMIMO detector is proposed, which is named two-level and block diagonal (TL-BD) based improved Neumann series approximation (TL-BD-INSA). Specifically, a twolevel and block diagonal based iteration leveraging matrix partition is firstly carried out to extract the block diagonal features and reduce the multiplications between large matrices. Next, an optimized normalization factor based on mathematical expectation deduction, which can be calculated offline, is introduced to guarantee and accelerate the convergence.
- The residual error induced by the TL-BD-INSA and the computational complexity of the proposed method are analyzed in details.
- Numerical results are presented to show the advanced performance of the proposed algorithm by comparison with the state-of-the-art (SOA) methods in SAUE system and MAUE system with different propagation environments.
- We present an efficient pipelined VLSI architecture of the proposed detector and show the reference FPGA and ASIC results, which enables us to exhibit the hardware efficiency compared to the SOA detectors.
The remainder of this paper is organized as follows. Section II introduces the system model and Neumann series theorem. The proposed TL-BD-INSA is presented in Section III. Section IV exhibits the numerical results and complexity analysis. The VLSI architecture and implementation results are discussed in Section V. Section VI concludes this paper.

Notation: Bold uppercase, bold lowercase and lowercase letters denote matrices, vectors and scalars, respectively. The superscripts $(\cdot)^{\mathrm{H}},(\cdot)^{\mathrm{T}}$ and $(\cdot)^{-1}$ stand for conjugate transpose,

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-02.jpg?height=435&width=658&top_left_y=227&top_left_x=1162)
Fig. 1. An uplink M-MIMO system. (Enc. = Encoder, Mod. = Modulator).

transpose and matrix inversion, respectively. $\Re(\cdot), \mathfrak{J}(\cdot)$ and $\overline{(\cdot)}$ denote the real part, imaginary part and conjugate version of a complex number, respectively. $\mathbf{I}_{M}$ indicates an $M \times M$ identity matrix. The $i$-th element in vector $\boldsymbol{x}$ is denoted by $x_{i}$, while the ( $i, j$ )-th element in matrix $\mathbf{X}$ is $X_{i j} . x \sim \mathcal{C} \mathcal{N}(\mu, \xi)$ means that $x$ is a random variable that follows a complex Gaussian distribution with mean $\mu$ and variance $\xi$. The notation $\operatorname{diag}(\mathbf{x})$ creates a matrix with $\mathbf{x}$ in the diagonal and $\operatorname{diag}(\mathbf{X})$ is the vector of the diagonal elements of $\mathbf{X}$.

## II. Preliminaries

## A. System Model

Consider an uplink M-MIMO with MAUE system that a single BS with $N$ antennas communicates with $m$ UEs and each UE is equipped with $m_{\text {UE }}$ antennas, as depicted in Fig. 1. The total number of antennas at the user side is $M=m \times m_{\mathrm{UE}}$. The transmitted vector is represented as $\mathbf{s}=\left[\mathbf{s}_{1} \cdots \mathbf{s}_{i} \cdots \mathbf{s}_{m}\right]^{\mathrm{T}}$, where $\mathbf{s}_{i}=\left[s_{i 1} \cdots s_{i j} \cdots s_{i m_{\mathrm{UE}}}\right]$, with a normalized expected transmitted power $\mathbb{E}\left\{\left|s_{i j}\right|^{2}\right\}=1$. The received vector $\mathbf{y} \in \mathbb{C}^{N \times 1}$ at the BS side is obtained by:

$$
\begin{equation*}
\mathbf{y}=\mathbf{H} \mathbf{s}+\mathbf{n}, \tag{1}
\end{equation*}
$$

where the uplink channel matrix $\mathbf{H}=\left[\mathbf{H}_{1} \cdots \mathbf{H}_{i} \cdots \mathbf{H}_{m}\right] \in \mathbb{C}^{N \times M}$ with $\mathbf{H}_{i}=\left[\mathbf{H}_{i 1} \cdots \mathbf{H}_{i m_{\mathrm{UE}}}\right]$. Specifically, $\mathbf{H}_{i j}$ is an $N$-column vector and represents the uplink from the $j$-th antenna of the $i$-th UE to the BS, and $\mathbf{n} \in \mathbb{C}^{N \times 1}$ is the additive white Gaussian noise (AWGN) vector with mean zero and variance $N_{0}$. In this paper, H is assumed to be known at the BS.

Most of the previous researches on uplink M-MIMO system only considered geometric attenuation [17], [19], but neglected antenna correlation. However, for practical M-MIMO systems, the detection performance is affected by the spatial correlation of signals to a large extent. Therefore, in this paper, the Kronecker channel model [32] is applied as:

$$
\begin{equation*}
\mathbf{H}=\mathbf{R}^{1 / 2} \mathbf{H}_{0} \mathbf{T}^{1 / 2}, \tag{2}
\end{equation*}
$$

where $\mathbf{H}_{0} \in \mathbb{C}^{N \times M}$ denotes the fast fading coefficients with i.i.d. Gaussian elements. Additionally, $\mathbf{R} \in \mathbb{C}^{N \times N}$ and $\mathbf{T} \in \mathbb{C}^{M \times M}$ stand for the spatial correlation matrices. The elements of $\mathbf{R}$ and $\mathbf{T}$ can be determined by Eq. (3),

$$
R_{p q}=\left\{\begin{array}{l}
\left(\zeta_{r} e^{j \theta}\right)^{q-p}, p \leq q,  \tag{3}\\
R_{q p}^{*}, \quad p>q,
\end{array} T_{p q}=\left\{\begin{array}{l}
\left(\zeta_{t} e^{j \theta}\right)^{q-p}, p \leq q, \\
T_{q p}^{*}, \quad p>q,
\end{array}\right.\right.
$$

where $\zeta_{r}$ and $\zeta_{t}$ are correlated coefficients that reflect the correlation between the $p$-th antenna and the $q$-th antenna at the BS and the UE, respectively. As revealed by [33], the transmitting antennas from the same UE are usually of high correlation due
to insufficient spacing. However, in most published works [34], [35], the correlation between antennas from the same UE is not taken into consideration, which is impractical and inaccurate. Therefore, based on the propagation fact, $\zeta_{r}$ and $\zeta_{t}$ are redefined as the correlated factor of receiving antennas and transmitting antennas from the same UE, respectively. Note that the correlation between antennas from different UEs is neglected.

## B. MMSE Detection and Neumann Series Approximation

Minimum mean-square error (MMSE) detection, one of the most attractive low-complexity MIMO detection method, estimates the transmitted signal $\hat{\mathbf{s}}$ by:

$$
\begin{equation*}
\hat{\mathbf{s}}=\mathbf{A}^{-1} \cdot \hat{\mathbf{y}}^{\mathrm{MF}}=\left(\mathbf{H}^{\mathrm{H}} \mathbf{H}+N_{0} \mathbf{I}_{M}\right)^{-1} \cdot \mathbf{H}^{\mathrm{H}} \mathbf{y} \tag{4}
\end{equation*}
$$

where $\mathbf{A}=\mathbf{H}^{\mathrm{H}} \mathbf{H}+N_{0} \mathbf{I}_{M}$ is a conjugate-symmetric positive definite matrix in M-MIMO systems and $\hat{\mathbf{y}}^{\mathrm{MF}}=\mathbf{H}^{\mathrm{H}} \mathbf{y}$ is regarded as the output of the matched filter (MF).

As shown in Eq. (4), it is inevitable to compute an explicit complex matrix inversion in MMSE detection. However, since the computation complexity of the matrix inversion based on Cholesky decomposition or Gauss-Jordan elimination is $\mathcal{O}\left(K^{3}\right)$, it will result in unaffordable complexity and tough implementation when the number of terminal antennas increases exponentially [36]. To this end, a matrix inversion approach based on $k$-term Neumann series approximation (NSA) with complexity of $\mathcal{O}\left(K^{2}\right)$ when $k$ is less than 2 , is proposed [19]. Specifically, if matrix $\mathbf{A}$ is close to an invertible matrix $\mathbf{X}$ :

$$
\begin{equation*}
\lim _{n \rightarrow \infty}\left(\mathbf{I}-\mathbf{X}^{-1} \mathbf{A}\right)^{n}=0 \text { or } \lim _{n \rightarrow \infty}\left(\mathbf{I}-\mathbf{A} \mathbf{X}^{-1}\right)^{n}=0 \tag{5}
\end{equation*}
$$

Then the inverse of $\mathbf{A}$ can be expressed by Neumann series:

$$
\begin{equation*}
\mathbf{A}^{-1}=\sum_{n=0}^{\infty}\left(\mathbf{I}-\mathbf{X}^{-1} \mathbf{A}\right)^{n} \mathbf{X}^{-1} \tag{6}
\end{equation*}
$$

With $\mathbf{D}=\mathbf{X}$ and $\mathbf{E}=\mathbf{A}-\mathbf{X}$, we can take the first $k$ terms of Neumann series as the $k$-term approximation of $\mathbf{A}^{-1}$ :

$$
\begin{equation*}
\mathbf{A}^{-1} \approx \hat{\mathbf{A}}_{k}^{-1}=\sum_{n=0}^{k-1}\left(-\mathbf{D}^{-1} \mathbf{E}\right)^{n} \mathbf{D}^{-1} \tag{7}
\end{equation*}
$$

## III. Proposed TL-BD-INSA Algorithm

In this section, the correlated M-MIMO channels in MAUE systems is characterized at first. Next, based on the channel property, the TL-BD-INSA algorithm is proposed.

## A. Characteristic of Correlated M-MIMO Channels

Since the selection of $\mathbf{D}$ is vital for the convergence speed and approximation accuracy of Eq. (7) [17], we first analyze the property of Gram matrix in M-MIMO under different propagation environments. The characteristic of $\mathbf{A}$ is depicted in Fig. 2. It can be observed that $\mathbf{A}$ appears diversely dominant in different systems with different propagation conditions. Specifically, in MAUE system, Gram matrix $\mathbf{A}$ is near block diagonally dominant, and the block property becomes more evident with the increase of correlation. Therefore, the block diagonal constructing is more suitable for MAUE system with high correlation. It is worth mentioning that the block diagonally dominant characteristic is similar to the channel model obtained after block diagonalization (BD) precoding in the practical distributed MIMO (D-MIMO) system [31].

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-03.jpg?height=619&width=854&top_left_y=219&top_left_x=1052)
Fig. 2. The Gram matrix $\mathbf{A}$ in SAUE and MAUE systems with ideal propagation environment (IPE), non-ideal propagation environment (NPE) and bad propagation environment (BPE) [37] (From left to right, from top to bottom, they are called as channel $1,2,3,4,5,6$, respectively).

For the inversion problem of block diagonal matrix, based on MP [23], our previous work [37] has proposed a low-complexity inversion scheme called block diagonal multiple-level iteration (BD-MLI). However, the scheme is only available to the inversion of those matrices with order $2^{z}(z=1,2, \cdots)$. Moreover, to achieve satisfying accuracy, much more level iterations are required, which will result in severe latency.

## B. TL-BD Based Neumann Series Iteration

To alleviate the aforementioned problem, in this subsection, a TL-BD based Neumann series iteration is proposed.

Since the Gram matrices in MAUE systems exhibit block diagonal dominant, MP is employed to extract the dominant block diagonal elements. Specifically, the pre-conditioner matrix D remains the block diagonal entries of $\mathbf{A}$, i.e., $\mathbf{D}$ is composed of several block sub-matrices. For convenience, assume the order of each block matrix is identical, denoted by $K$. Then the number of submatrices is $L=M / K$, where $1 \leq K \leq M, K \in \mathcal{Z}$ and $L \in \mathcal{Z}$.

Since our previous work [37] has proved when $L=2$, as shown in Eq. (8), the number of complex-valued multiplications of Eq. (7) reaches minimum compared to other blocked modes, the blocked mode is adopted to calculate $\mathbf{A}^{-1}$ as Eq. (9) shows. Supposing $\mathbf{D}_{(1,1)}^{-1}$ and $\mathbf{D}_{(1,2)}^{-1}$ are known, the calculation of $\mathbf{A}^{-1}$ is denoted as the first-level iteration (FLI).

$$
\begin{align*}
\mathbf{D}_{1}= & {\left[\begin{array}{cc}
\mathbf{D}_{(1,1)} & \mathbf{0} \\
\mathbf{0} & \mathbf{D}_{(1,2)}
\end{array}\right], \quad \mathbf{E}_{1}=\left[\begin{array}{cc}
\mathbf{0} & \mathbf{E}_{(1,1)} \\
\mathbf{E}_{(1,2)} & \mathbf{0}
\end{array}\right] }  \tag{8}\\
\mathbf{A}^{-1} \approx & \sum_{n=0}^{k_{\mathrm{F}}-1}\left(-\left[\begin{array}{cc}
\mathbf{0} & \mathbf{D}_{(1,1)}^{-1} \mathbf{E}_{(1,1)} \\
\mathbf{D}_{(1,2)}^{-1} \mathbf{E}_{(1,2)} & \mathbf{0}
\end{array}\right]\right)^{n} \\
& \times\left[\begin{array}{cc}
\mathbf{D}_{(1,1)}^{-1} & \mathbf{0} \\
\mathbf{0} & \mathbf{D}_{(1,2)}^{-1}
\end{array}\right] . \tag{9}
\end{align*}
$$

As $\mathbf{D}_{(1,1)}$ and $\mathbf{D}_{(1,2)}$ are both block diagonal and symmetric positive definite matrix, the second-level iteration (SLI) is executed to obtain $\mathbf{D}_{(1,1)}^{-1}$ and $\mathbf{D}_{(1,2)}^{-1}$ by the same method as $\mathbf{A}^{-1}$, whereas $L=m_{\mathrm{UE}}$ is employed in SLI. Taking $\mathbf{D}_{(1,1)}^{-1}$

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-04.jpg?height=293&width=841&top_left_y=227&top_left_x=163)
Fig. 3. The schematic diagram of TL-BD scheme.

as an example, we further decompose $\mathbf{D}_{(1,1)}$ into its main block diagonal $\mathbf{D}_{2}^{1}$ and off block diagonal $\mathbf{E}_{2}^{1}$. Specifically, $\mathbf{D}_{2}^{1}$ is constructed by Eq. (10), where $\mathbf{D}_{(2, t)}\left(t=1,2, \ldots, \frac{T}{2}\right)$ are composed of the diagonal entries in $\mathbf{A}$ with size $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$. Utilizing the $k_{\mathrm{N}}$-term series, the approximate inversion of matrix $\mathbf{D}_{(1,1)}$ can be computed by Eq. (11). The calculation of $\mathbf{D}_{(1,2)}^{-1}$ follows the same way. The full process of obtaining $\mathbf{A}^{-1}$ by the TL-BD scheme is illustrated in Fig. 3, where $M=8, m_{\mathrm{UE}}=2$ is exemplified.

$$
\begin{align*}
\mathbf{D}_{2}^{1} & =\operatorname{diag}\left[\mathbf{D}_{(2,1)}, \mathbf{D}_{(2,2)}, \ldots, \mathbf{D}_{\left(2, \frac{T}{2}\right)}\right],\left(T=\frac{M}{m_{\mathrm{UE}}}\right)  \tag{10}\\
\mathbf{D}_{(1,1)}^{-1} & \approx \sum_{n=0}^{k_{\mathrm{N}}-1}\left(-\left(\mathbf{D}_{2}^{1}\right)^{-1} \mathbf{E}_{2}^{1}\right)^{n}\left(\mathbf{D}_{2}^{1}\right)^{-1} \tag{11}
\end{align*}
$$

## C. Improved Normalization Factor

To guarantee the convergence of Eq. (7), we must ensure the spectral radius of $-\mathbf{D}^{-1} \mathbf{E}$ is smaller than 1, i.e., $\rho\left(-\mathbf{D}^{-1} \mathbf{E}\right)<$ 1 [21]. Therefore, in [27], a normalization factor $\alpha$ is introduced to ensure the convergence and accelerate the speed. The work [27] suggests the optimal normalization factor $\alpha_{\text {opt }}$ multiplied before $\mathbf{D}$ is determined by Eq. (12):

$$
\begin{equation*}
\alpha_{\mathrm{opt}}=\frac{\lambda_{\min }(\mathbf{R})+\lambda_{\max }(\mathbf{R})}{2}, \tag{12}
\end{equation*}
$$

where $\mathbf{R}$ is equivalent to $\mathbf{D}^{-1} \mathbf{A}$ in NSA. However, calculating the matrix eigenvalues directly will introduce huge computation complexity, therefore, according to the Gershgorin circle theorem [21], an estimation for $\lambda_{\text {min }}(\mathbf{R})$ and $\lambda_{\text {max }}(\mathbf{R})$ is proposed in [27] via Eqs. (13) and (14). However, the approach is only suitable for diagonal-dominant matrices whose off-diagonal elements are relatively small so that the corresponding radius of Gershgorin circle is small. Even worse, the approach has to recalculate the eigenvalues of the new Gram matrix before each detection, which will result in unaffordable computation complexity.

$$
\begin{align*}
\hat{\lambda}_{\min }(\mathbf{R}) & =\max \left\{\min _{n \in(1, M)}\left\{R_{n, n}-\sum_{m=1, m \neq n}^{M}\left|R_{n, m}\right|\right\}, \epsilon\right\} \\
& \leq \lambda_{\min }(\mathbf{R})  \tag{13}\\
\hat{\lambda}_{\max }(\mathbf{R}) & =\max _{n \in(1, M)}\left\{\sum_{m=1}^{M}\left|R_{n, m}\right|\right\} \geq \lambda_{\max }(\mathbf{R}) \tag{14}
\end{align*}
$$

To tackle the issue, the work [25] proposes a channelhardening based estimation approach, which is expressed as:

$$
\begin{equation*}
\alpha_{\mathrm{opt}}^{*}=\frac{a+b}{2}, \tag{15}
\end{equation*}
$$

TABLE I
Numerical Results of Solving $\alpha_{\text {opt }}^{+}$by Image Method
| $M$ | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $\mathbb{E}\left\{\lambda_{\max }\right\}$ | 1.654 | 1.712 | 1.767 | 1.821 | 1.873 | 1.923 | 1.972 | 2.020 | 2.066 |
| $\mathbb{E}\left\{\lambda_{\min }\right\}$ | 0.4907 | 0.4590 | 0.4300 | 0.4033 | 0.3788 | 0.3559 | 0.3348 | 0.3148 | 0.2963 |
| $\alpha_{\text {opt }}^{+}$ | 1.0723 | 1.0855 | 1.0985 | 1.1122 | 1.1259 | 1.1395 | 1.1534 | 1.1674 | 1.1811 |


![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-04.jpg?height=579&width=704&top_left_y=528&top_left_x=1142)
Fig. 4. The comparison of $\alpha_{\mathrm{opt}}$ calculated by different methods.

where $a=(1-\sqrt{\eta})^{2}, b=(1+\sqrt{\eta})^{2}$ and $\eta=M / N$. However, it can be observed that the scheme does not account for the influence of matrix entries fluctuation.

To estimate $\alpha_{\text {opt }}$ more accurately, we propose a mathematical expectation based estimation in this paper. Our optimal normalization factor $\alpha_{\mathrm{opt}}^{+}$is determined by Eq. (16). Further, the $\mathbb{E}\left\{\lambda_{\max }\right\}$ and $\mathbb{E}\left\{\lambda_{\min }\right\}$ can be obtained by solving Eq. (17) utilizing image method offline. The detailed deduction and mathematical expression of $F_{\beta}(x)$ are provided in Appendix A. With the help of the function image of $F_{\beta}(\lambda)$, the numerical results of $\alpha_{\text {opt }}^{+}(N=128)$ are concluded in Table I.

$$
\begin{align*}
& \alpha_{\mathrm{opt}}^{+}=\frac{\mathbb{E}\left\{\lambda_{\max }\left(\mathbf{D}^{-1} \mathbf{A}\right)\right\}+\mathbb{E}\left\{\lambda_{\min }\left(\mathbf{D}^{-1} \mathbf{A}\right)\right\}}{2} .  \tag{16}\\
& \left\{\begin{array}{l}
F_{\beta}\left(\mathbb{E}\left\{\lambda_{\max }\right\}\right)=(1 / 2)^{\frac{1}{M}} \\
F_{\beta}\left(\mathbb{E}\left\{\lambda_{\min }\right\}\right)=1-(1 / 2)^{\frac{1}{M}}
\end{array}\right. \tag{17}
\end{align*}
$$

Fig. 4 compares the normalization factors obtained by different methods versus different values $M$ with $N=128$. The $\alpha_{\text {opt }}$ of Eq. (12) is obtained by Monte Carlo experiment and is regarded as the baseline. The number of Monte Carlo experiments is 1000 and the results are averaged. It can be observed that the $\alpha_{\text {opt }}$ calculated by the proposed method is almost identical to that of Monte Carlo experiment, but the method proposed in [25] is obviously larger. Further, the calculated $\alpha_{\text {opt }}$ is also available in MAUE system with correlation, which can be referred in Appendix A.

To sum up, the proposed TL-BD-INSA algorithm includes two-level iterations, namely FLI and SLI. The FLI consists of two block matrices of size $M / 2$, while the size of block matrices in SLI is determined by $m_{\mathrm{UE}}$. Furthermore, the elements of block matrices in SLI are multiplied with the improved normalization factor. The details of the proposed TL-BD-INSA is summarized in Alg. 1 , where $k_{\mathrm{F}}$ and $k_{\mathrm{N}}$ denote the iteration counts of FLI and SLI, respectively.

```
Algorithm 1: Proposed TL-BD-INSA Algorithm.
    Input: $\mathbf{A}, k_{\mathrm{F}}, k_{\mathrm{N}}, m_{\mathrm{UE}}, M, \alpha_{\mathrm{opt}}^{+}$;
    $T \leftarrow \frac{M}{m_{U E}} ;$
    Obtain $\mathbf{D}_{(1,1)}, \mathbf{D}_{(1,2)}, \mathbf{D}_{(2, t)},(t \in[1: T])$;
    for $t=1: T$ do
        $\mathbf{D}_{(2, t)} \leftarrow \alpha_{\text {opt }}^{+} \cdot \mathbf{D}_{(2, t)} ;$
    end
    Compute $\mathbf{D}_{(2, t)}^{-1}(t \in[1: T])$ by Cholesky inversion;
    for $i=1: 2$ do
        if $i==1$ then
            $K \leftarrow 0 ;$
        else
            $K \leftarrow 1 ;$
        end
        $\mathbf{N} \leftarrow \operatorname{diag}\left[\mathbf{D}_{2,1+\frac{K T}{2}}^{-1}, \mathbf{D}_{2,2+\frac{K T}{2}}^{-1}, \cdots, \mathbf{D}_{2, \frac{T}{2}+\frac{K T}{2}}^{-1}\right] ;$
        $\widetilde{\mathbf{D}}_{1, i} \leftarrow \operatorname{diag}\left[\mathbf{D}_{2,1+\frac{K T}{2}}, \mathbf{D}_{2,2+\frac{K T}{2}}, \cdots, \mathbf{D}_{2, \frac{T}{2}+\frac{K T}{2}}\right] ;$
        $\mathbf{E} \leftarrow \widetilde{\mathbf{D}}_{1, i}-\mathbf{D}_{(1, i)}$;
        $\mathbf{D}_{1, i}^{-1} \leftarrow \mathbf{N}$;
        for $n=1: k_{\mathrm{N}}-1$ do
            $\mathbf{D}_{(1, i)}^{-1} \leftarrow \mathbf{N E D}_{(1, i)}^{-1}+\mathbf{N} ;$
        end
    end
    $\mathbf{D}^{-1} \leftarrow \operatorname{diag}\left[\mathbf{D}_{(1,1)}^{-1}, \mathbf{D}_{(1,2)}^{-1}\right] ;$
    $\mathbf{E} \leftarrow \mathbf{D}^{-1}-\mathbf{A} ;$
    $\widetilde{\mathbf{A}}^{-1} \leftarrow \mathbf{D}^{-1} ;$
    for $n=1: k_{\mathrm{F}}-1$ do
        $\widetilde{\mathbf{A}}^{-1} \leftarrow \mathbf{D}^{-1} \mathbf{E} \widetilde{\mathbf{A}}^{-1}+\mathbf{D}^{-1} ;$
    end
    Output: $\widetilde{\mathbf{A}}^{-1}$.
```


## D. Complexity Analysis

For the proposed TL-BD-INSA algorithm, the calculation complexity of $\mathbf{A}^{-1}$ mainly comes from two parts: FLI and SLI. Consequently, the overall computational complexity is the summation of that of FLI and SLI. Please note here the computational complexity is given in the number of complex-valued multiplications (NCMs). ${ }^{1}$

Firstly, the complexity of block diagonalization matrix inversion relying on improved Neumann series algorithm (BD-INSA) is analyzed. Considering a $K \times K$ block diagonal matrix $\mathbf{W}$ whose block diagonal sub-matrices size is $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$, its approximate inversion can be obtained as shown in Eq. (18):

$$
\begin{equation*}
\mathbf{W}_{k}^{-1}=\sum_{n=0}^{k-1}\left(-\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}\right)^{-1} \mathbf{E}\right)^{n}\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}\right)^{-1}, \tag{18}
\end{equation*}
$$

where $\mathbf{W}_{k}^{-1}$ stands for the summation of the first $k$ terms of the series and $\mathbf{D}$ is a block diagonal matrix consists of $K / m_{\text {UE }}$ submatrices with size $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$. The number of NCMs required by BD-INSA is given by Eq. (19): ${ }^{2}$

$$
\begin{equation*}
N=(k-2) K^{3}-(k-3) K^{2} m_{\mathrm{UE}}+2 K m_{\mathrm{UE}}^{2} . \tag{19}
\end{equation*}
$$

Since for TL-ND-INSA, there are two $\frac{M}{2} \times \frac{M}{2}$ BD-INSAs in SLI, the complexity of SLI with $k_{\mathrm{N}}$ iteration counts can be calculated by:

$$
\begin{equation*}
N_{\mathrm{SLI}}=\frac{k_{\mathrm{N}}-2}{4} M^{3}+\frac{k_{\mathrm{N}}-3}{2} m_{\mathrm{UE}} M^{2}+2 M m_{\mathrm{UE}}^{2} \tag{20}
\end{equation*}
$$

[^0]![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-05.jpg?height=646&width=774&top_left_y=227&top_left_x=1093)
Fig. 5. Inaccuracy resulted from the SLI truncation ( $\mathrm{SNR}=4 \mathrm{~dB}$ ).

Next, the FLI complexity with $k_{\mathrm{F}}$ iteration counts is:

$$
\begin{equation*}
N_{\mathrm{FLI}}=\frac{M^{3}}{4}+\frac{M^{3}}{4}+\frac{k_{\mathrm{F}}-2}{4} M^{3}=\frac{k_{\mathrm{F}}}{4} M^{3}, \tag{21}
\end{equation*}
$$

where the first $M^{3} / 4$ stands for the NCMs between $\mathbf{D}^{-1}$ and $\mathbf{E}$. The second $M^{3} / 4$ represents the NCMs between ( $-\mathbf{D}^{-1} \mathbf{E}$ ) and $\mathbf{D}^{-1}$. The third term $\left(k_{\mathrm{F}}-2\right) M^{3} / 4$ denotes the NCMs among $\left(k_{\mathrm{F}}-2\right)\left(-\mathbf{D}^{-1} \mathbf{E}\right)$ and $\left(-\mathbf{D}^{-\mathbf{1}} \mathbf{E D}^{-\mathbf{1}}\right)$.

Therefore, the overall complexity of calculating $\mathbf{A}^{-1}$ is represented as follows,

$$
\begin{equation*}
N_{\text {total }}=\frac{k_{\mathrm{F}}+k_{\mathrm{N}}-2}{4} M^{3}+\frac{k_{\mathrm{N}}-3}{2} M^{2} m_{\mathrm{UE}}+2 M m_{\mathrm{UE}}^{2} . \tag{22}
\end{equation*}
$$

## E. Error Analysis

In practical MIMO systems, the number of iteration cannot be very large due to the considerations on complexity and latency. To this end, we next analyze the error resulted from the truncated polynomial in the proposed TL-BD-INSA for MMSE detection. The approximation error in TL-BD-INSA comes from two-level truncations: FLI and SLI. The overall truncated error in TL-BD-INSA is represented by Eq. (23). To explore the error resulted from the SLI truncation, we compare the average elements inaccuracy between different $k_{\mathrm{N}}$ with $k_{\mathrm{N}}=3$ under three different correlated channels and keeping $k_{\mathrm{F}}=3$. Simulation results in Fig. 5 reveal that compared with $k_{\mathrm{N}}=3$, the average difference introduced by the increasing iteration $k_{\mathrm{N}}$ is less than $2 \times 10^{-6}$, which can be neglected reasonably. Therefore, the whole truncated error of TL-BD-INSA is simplified as Eq. (24). For simplicity, we denote the first term in Eq. (24) as $\widetilde{\mathbf{A}}^{-1}$ and the second term as $\widetilde{\mathbf{A}}_{K_{\mathrm{F}}}^{-1}$. Additionally, $\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{1} \mathbf{E}_{2}^{1}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{1}$ and $\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2}$ are denoted as $\widetilde{\mathbf{D}}_{(1,1)}^{-1}$ and $\widetilde{\mathbf{D}}_{(1,2)}^{-1}$, respectively. Then, Eq. (24) can be rewritten as Eq. (25).

$$
\begin{align*}
\widetilde{\boldsymbol{\Delta}}_{k_{\mathrm{F}}} & =\widetilde{\mathbf{A}}^{-1}-\widetilde{\mathbf{A}}_{k_{\mathrm{F}}}^{-1} \\
& =\sum_{n 1=k_{\mathrm{F}}}^{\infty}\left[\begin{array}{cc}
\mathbf{0} & -\widetilde{\mathbf{D}}_{(1,1)}^{-1} \mathbf{E}_{(1,2)} \\
-\widetilde{\mathbf{D}}_{(1,2)}^{-1} \mathbf{E}_{(1,2)} & \mathbf{0}
\end{array}\right]^{n_{1}} \widetilde{\mathbf{D}}^{-1}, \tag{25}
\end{align*}
$$

where $\widetilde{\mathbf{D}}^{-1}$ represents $\left[\begin{array}{cc}\widetilde{\mathbf{D}}_{(1,1)}^{-1} & \mathbf{0} \\ \mathbf{0} & \widetilde{\mathbf{D}}_{(1,2)}^{-1}\end{array}\right]$. For simplicity, further, we denote $\left[\begin{array}{cc}\mathbf{0} & -\widetilde{\mathbf{D}}_{(1,1)}^{-1} \mathbf{E}_{(1,2)} \\ -\widetilde{\mathbf{D}}_{(1,2)}^{-1} \mathbf{E}_{(1,2)} & \mathbf{0}\end{array}\right]$ as $\boldsymbol{\Xi}$, then Eq. (25) can be further rewritten as:

$$
\begin{equation*}
\widetilde{\boldsymbol{\Delta}}_{k_{\mathrm{F}}}=\boldsymbol{\Xi}^{k_{\mathrm{F}}} \sum_{n_{1}=0}^{\infty} \boldsymbol{\Xi}^{n_{1}} \widetilde{\mathbf{D}}^{-1}=\boldsymbol{\Xi}^{k_{\mathrm{F}}} \mathbf{A}^{-1} . \tag{26}
\end{equation*}
$$

Furthermore, utilizing Eq. (4) to estimate the transmitted signal, the expression of transmitted signal $\hat{\mathbf{s}}_{\mathbf{A} \mid k_{\mathrm{F}}}$ related to truncated error $\widetilde{\boldsymbol{\Delta}}_{k_{\mathrm{F}}}$ can be obtained as Eq. (27),

$$
\begin{align*}
\hat{\mathbf{s}}_{\mathbf{A} \mid k_{\mathrm{F}}} & =\widetilde{\mathbf{A}}_{k_{\mathrm{F}}}^{-1}\left(\mathbf{R}^{1 / 2} \mathbf{H}_{0} \mathbf{T}^{1 / 2}\right)^{\mathrm{H}} \mathbf{y} \\
& =\mathbf{A}^{-1} \mathbf{y}^{\mathrm{MF}}-\widetilde{\boldsymbol{\Delta}}_{k_{\mathrm{F}}}\left(\mathbf{R}^{1 / 2} \mathbf{H}_{0} \mathbf{T}^{1 / 2}\right)^{\mathrm{H}} \mathbf{y}, \tag{27}
\end{align*}
$$

where $\widetilde{\boldsymbol{\Delta}}_{k_{\mathrm{F}}}\left(\mathbf{R}^{1 / 2} \mathbf{H}_{0} \mathbf{T}^{1 / 2}\right)^{\mathrm{H}} \mathbf{y}$ is the residual estimation error. Taking the L2-norm of residual estimation error and denote it as $\Psi$, we have:

$$
\begin{align*}
\Psi=\left\|\widetilde{\boldsymbol{\Delta}}_{k_{\mathrm{F}}}\left(\mathbf{R}^{1 / 2} \mathbf{H}_{0} \mathbf{T}^{1 / 2}\right)^{\mathrm{H}} \mathbf{y}\right\|_{2} & =\left\|\boldsymbol{\Xi}^{k_{\mathrm{F}}} \mathbf{A}^{-1} \mathbf{y}^{\mathrm{MF}}\right\|_{2} \\
& \leq\left\|\boldsymbol{\Xi}^{k_{\mathrm{F}}}\right\| \mathrm{F}\left\|\mathbf{y}^{\mathrm{MF}}\right\|_{2} \\
& \leq\|\boldsymbol{\Xi}\|_{\mathrm{F}}^{k_{\mathrm{F}}}\left\|\mathbf{y}^{\mathrm{MF}}\right\|_{2} . \tag{28}
\end{align*}
$$

As shown in Eq. (28), the $\Psi$ is determined by $\|\boldsymbol{\Xi}\|_{\mathrm{F}}^{k_{\mathrm{F}}}$. Considering the convergence condition in Section III-C, i.e., $\|\boldsymbol{\Xi}\|_{\mathrm{F}}<1$, the approximated error of detection signal can be reduced by large $k_{\mathrm{F}}$-term truncation. Specifically, under a limit condition $k_{\mathrm{F}} \rightarrow \infty$, the $\Psi$ tends to zero exponentially.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-06.jpg?height=656&width=789&top_left_y=223&top_left_x=1100)
Fig. 6. BER performance of different algorithms in SAUE system with IPE.

## IV. Performance Analysis

In this section, numerical results of the proposed algorithm TL-BD-INSA are presented to demonstrate its accuracy and efficiency in different scenarios.

## A. Numerical Results

To verify the effectiveness of the improved normalization factor proposed in Section III-C, Fig. 7 compares the performance of TL-BD-INSA with different normalization factors $\alpha$ under three antennas configurations assuming $\zeta_{t}=0.5$ and $\zeta_{r}=0.6$. As shown in Fig. 7(a), it can be observed that under MAUE system with size $128 \times(5 \times 4)$, the performance of $\alpha=1.0985$ outperforms that of other values, which is corresponding to the theoretical results in Table I. Moreover, both Fig. (7(b)) with size $128 \times(6 \times 4)$ and Fig. (7(c)) with size $128 \times(8 \times 4)$ further

$$
\begin{align*}
& \Delta_{k}= \\
& \underbrace{\sum_{n 1=0}^{\infty}\left[\begin{array}{cc}
\mathbf{0} & -\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{1} \mathbf{E}_{2}^{1}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{1} \\
-\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2} & \mathbf{0}
\end{array}\right]^{n_{1}}-\sum_{n 1=0}^{k_{\mathrm{F}}-1}\left[\begin{array}{cc}
\mathbf{0} & -\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{1} \mathbf{E}_{2}^{1}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{1} \\
\mathbf{0} & -\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2}
\end{array}\right)^{n_{1}} \hat{\mathbf{D}}_{2}^{1}}_{\text {FLI truncation }}]^{n_{1}}-\sum_{n 1=0}^{k_{\mathrm{F}-1}}\left[-\sum_{n_{2}=0}^{k_{\mathrm{N}}-1}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2}\right. \\
& \mathbf{0}
\end{align*} \underbrace{\sum_{n 1=0}^{k_{\mathrm{F}}-1}\left[\begin{array}{cc}
k_{\mathrm{N}}-1  \tag{23}\\
-\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2} & \left.\hat{\mathbf{D}}_{2}^{1} \mathbf{E}_{2}^{1}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{1}
\end{array}\right]^{n_{1}}}_{\text {SLI truncation }},
$$

$\widetilde{\Delta}_{k} \approx$

$$
\sum_{n 1=0}^{\infty}\left[\begin{array}{cc}
\mathbf{0} & -\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{1} \mathbf{E}_{2}^{1}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{1}  \tag{24}\\
-\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2} & \mathbf{0}
\end{array}\right]^{n_{1}}-\sum_{n 1=0}^{k_{\mathrm{F}}-1}\left[\begin{array}{cc}
\mathbf{0} & -\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{1} \mathbf{E}_{2}^{1}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{1} \\
-\sum_{n_{2}=0}^{\infty}\left(-\hat{\mathbf{D}}_{2}^{2} \mathbf{E}_{2}^{2}\right)^{n_{2}} \hat{\mathbf{D}}_{2}^{2} & \mathbf{0}
\end{array}\right]^{n_{1}} .
$$

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-07.jpg?height=517&width=1709&top_left_y=210&top_left_x=171)
Fig. 7. The comparison for different values of normalization factor $\alpha$ with 16-QAM modulation.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-07.jpg?height=518&width=1722&top_left_y=782&top_left_x=163)
Fig. 8. The BER performance of different algorithms in MAUE systems with different propagation environments with 16-QAM modulation.

verify the effectiveness of the proposed normalization factor in improving convergence.

Next, we compare the BER performance of different algorithms in SAUE system with IPE. As depicted in Fig. 6, under with large base-station to user antenna ratios and uncorrelated propagation environment, the Gauss-Seidel based on NSA initialization (GS-NSA) [30] can outperform the TL-BD-INSA 0.2 dB at BER $10^{-4}$ and CG [29] can outperform the TL-BDINSA slightly. Additionally, the TL-BD-INSA can outperform other Neumann-series based algorithms, including the improved Neumann series approximation (INSA) [27] and the TMA [24].

Further, the performance of different algorithms in MAUE system with different propagation environments is compared. As shown in Fig. 8, with the correlation increasing, the detection performance of almost all algorithms declines, which is resulted from the interference between the antennas of the same UE and BS. Some algorithms, such as NSA and TMA cannot converge in MAUE system with iteration $k=3$. Furthermore, with the same iteration $k=3$, the performance of CG and INSA is not satisfactory not only in low correlation environment, but also in high correlation environment. In addition, it can be observed that the proposed TL-BD-INSA algorithm can achieve near MMSE performance in all MAUE systems and outperform other algorithms apparently. It is worth mentioning that, although the GS-NSA scheme can achieve slightly better performance of TL-BD-INSA in MAUE system with IPE under the same iteration $k=3^{3}$, as shown in Fig. 8(b) and Fig. 8(c), its performance degrades significantly with the correlation increasing because

[^1]the NSA-based initialization is unsuitable for the correlation channels, while the performance of the proposed scheme still remains at a relatively near-MMSE level. Specifically, compared with MMSE at BER $=10^{-3}$, the SNR loss of TL-BD-INSA is around 0.1 dB in IPE and 0.25 dB in NPE, respectively. Further, compared with MMSE in BPE, the SNR loss of TL-BD-INSA becomes around 0.2 dB to achieve $\mathrm{BER}=10^{-2}$.

To make fairer comparisons and further investigate the convergence of the conventional detection algorithms, Fig. 9 compares the performance of different detectors in different channels versus different iterations, which regards the performance of TL-BD-INSA with $k=3$ and Cholesky-based MMSE as the baselines. As illustrated in Fig. 9(a), we can notice that TMA and NSA fail to converge in the medium correlation environment. Additionally, as shown in Fig. 9(b), when the channel is in high correlation, GS-INSA is also unable to converge, while TL-BD-INSA can maintain close-to-MMSE performance under the two channel conditions. Although GS-NSA and CG can achieve near-TL-BD-INSA performance by continuously increasing the iterations in medium correlation environments and high correlation environments, respectively, their corresponding computational costs would be higher than that of TL-BD-INSA, which will be further discussed in Section IV-B.

Furthermore, Fig. 10 depicts the performance variation of different algorithms in MAUE system with NPE versus different values of $\zeta_{t}$. Due to the correlation between antennas from the same UE, all algorithms, including MMSE, appear performance degradation with the $\zeta_{t}$ increasing. Performance of TMA and GS-NSA degrades steeply and a complete failure appears when $\zeta_{t}$ is greater than 0.3 . Additionally, the performance of both traditional NSA and INSA degrades comparatively severely and

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-08.jpg?height=856&width=850&top_left_y=223&top_left_x=158)
Fig. 9. BER performance of different algorithms versus iterations.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-08.jpg?height=586&width=746&top_left_y=1170&top_left_x=206)
Fig. 10. BER performance of different algorithm versus $\zeta_{t}$ with $\mathrm{SNR}=8 \mathrm{~dB}$.

deviates from the MMSE detection. Furthermore, with the increase of $\zeta_{t}$, the BER interval between CG and MMSE becomes more obvious, whereas the proposed TL-BD-INSA can achieve almost close-to-MMSE detection performance as $\zeta_{t}$ increases.

## B. Computational Complexity

In this section, computational complexity is analyzed in terms of the NCMs of different algorithms. The numerical expressions are summarized in Table II. Notice that the complexity for pre-processing (computing Gram matrix and matched filter results) is omitted since it is shared by all the methods. It can be observed although CG and GS-NSA have the low complexity, i.e., $\mathcal{O}\left(M^{2}\right)$, their error performance is inferior in NPE and BPE as analyzed in Section IV-A. Furthermore, if the number of user antenna becomes large, e.g. up to 30, as shown in Fig. 11, around $50 \%$ complexity reduction over Cholesky and around 36\% complexity reduction over the NSA can be achieved by the

TABLE II
Computational Complexity Comparison
| Algorithm | Number of Complex-valued multiplications |
| :--- | :--- |
| Cholesky [38] | $2 M^{3}+2 M$ |
| CG [29] | $k\left(M^{2}+6 M\right)$ |
| TMA [24] | $2\left(\log _{2}(k+1)-1\right) M^{3}+6\left(M^{2}+M\right)$ |
| GS-NSA [30] | $(k+3) M^{2}+3 M$ |
| NSA [19] ( $k=3$ ) | $\frac{3 M^{3}+9 M^{2}-12 M}{2}$ |
| TL-BD-INSA | $\frac{k_{\mathrm{F}}+k_{\mathrm{N}}-2}{4} M^{3}+\frac{k_{\mathrm{N}}-2}{2} m_{\mathrm{UE}} M^{2}+2 M m_{\mathrm{UE}}^{2}$ |


![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-08.jpg?height=627&width=744&top_left_y=678&top_left_x=1121)
Fig. 11. Complexity comparison against number of users $\left(m_{\mathrm{UE}}=4\right)$.

proposed TL-BD-INSA algorithm with iteration $k=3$. The reduction of computation mainly comes from the matrix partition in FLI, which reduces nearly half of the computation in each iteration compared to NSA. Moreover, TMA performs poorly in MAUE system with few iterations as shown in Section IV. Increasing the iterations may be a feasible solution to improve its performance, but it will result in its complexity higher than that of Cholesky-MMSE.

The complexity-performance trade-off for the numerical tests under different correlation scenarios is illustrated in Fig. 12 for a further comparison of the algorithm efficiency. In the graphs, the performance of Cholesky-based MMSE is regarded as the benchmark, while the SNR loss of each algorithm compared to Cholesky-based MMSE is exhibited in the horizontal axis at the specific BER. The vertical axis represents the complexities of the algorithms, which are evaluated by the NCMs. From Fig. 12(a), we notice that in MAUE system with IPE, GS-NSA and CG can outperform TL-BD-INSA with lower computational cost. However, with the increase of correlation and $m_{\text {UE }}$, GS-NSA with 29 iterations not only leaves 0.2 dB gap compared with TL-BDINSA, but also consumes higher computational cost due to the large number of iterations, as shown in Fig. 12(b). With the correlation increasing further, as depicted in Figs. 12(c) and 12(d), the performance of CG degrades evidently. Specifically, under $256 \times 24$ configuration with $\zeta_{t}=0.9, \zeta_{r}=0.5, m_{\mathrm{UE}}=6, \mathrm{CG}$ achieves the near TL-BD-INSA performance at expense of $30 \%$ higher computation complexity. Therefore, the proposed TL-BD-INSA exhibits good stability for challenging channel conditions and is able to achieve a good balance between BER performance and complexity.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-09.jpg?height=833&width=888&top_left_y=212&top_left_x=120)
Fig. 12. Comparison of the complexity to BER performance trade-off for different detectors. Cholesky-based MMSE is set as the performance benchmark to evaluate the SNR loss of each algorithm. NSA and TMA are not compared in sub-figures (b), (c), (d) and GS-NSA is not compared in sub-figures (c), (d) due to their highly-degraded performances which fail to converge to the illustrated BER level.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-09.jpg?height=432&width=852&top_left_y=1289&top_left_x=141)
Fig. 13. Proposed TL-BD-INSA based pipeline detection architecture.

## V. Hardware Implementation

We next show that the TL-BD-INSA based detector can be implemented on hardware, verifying its practical applicability.

## A. Hardware Architecture of TL-BD-INSA Detector

Based on Alg. 1, the overall framework of the proposed TL-BD-INSA detector, as shown in Fig. 13, is composed of three main parts:

1) Preprocessing Unit (PU): In this unit, the channel matrix $\mathbf{H}$ and received vector $\mathbf{y}$ are processed to give the Gram matrix $\mathbf{A}$, which can be split as $\mathbf{A}=\mathbf{D}+\mathbf{E}$, and the matched vector $\hat{\mathbf{y}}^{\text {MF }}$. Notice that in TL-BD-INSA, the matrix $\mathbf{D}$ includes the all $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$ block diagonal elements in $\mathbf{A}$.

Considering $\mathbf{A}$ is Hermitian, in matrix multiplier module, an $M \times M$ lower triangular systolic array (LTSA) shown in Fig. 14 is adopted to calculate it. The LTSA reads the elements of one-row matrix $\mathbf{H}$ at a time, and outputs the solution of the Gram matrix after $N$ clock cycles. Each processing element (PE) performs the multiply-accumulate (MAC) with the

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-09.jpg?height=549&width=667&top_left_y=227&top_left_x=1145)
Fig. 14. Architecture of the LTSA used in TL-BD-INSA.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-09.jpg?height=261&width=701&top_left_y=865&top_left_x=1130)
Fig. 15. Hardware implementation block diagram of Cholesky algorithm (Decom. $=$ Decomposition, Conj. $=$ Conjugate).

same inputs. Please notice we employ the same PE in diagonal and off-diagonal lines, so that the systolic array can be reused in Iteration Unit.

The matched filter (MF) module consists of a linear array (LA) including $M$ PEs, in which each PE is related to a row of matrix $\mathbf{H}^{\mathrm{H}}$. The MF reads a new y in each clock cycle and multiplies it with the $\mathbf{H}^{\mathrm{H}}$ in each PE, then the multiplied result is added to previous result. The module can also be reused in Estimation Unit.
2) TL-BD-INSA Unit: This unit, consisting of scaling, BD inversion, BD multiplier modules and an iteration unit, utilizes TL-BD-INSA to calculate $\widetilde{\mathbf{A}}^{-1}$ with arbitrary $k_{\mathrm{N}}$ iterations of SLI and $k_{\mathrm{F}}$ iterations of FLI, respectively. The scaling module is composed of $M$ real-multipliers and $M\left(m_{\mathrm{UE}}-1\right) / 2$ complex-multipliers (CMs) (requiring three real multipliers) to introduce the normalization factor. Other modules will be discussed later.
3) Estimation Unit (EU): In this unit, the estimated signal $\hat{\mathbf{s}}$ is calculated by $\widetilde{\mathbf{A}}^{-1} \hat{\mathbf{y}}^{\mathrm{MF}}$. To reduce unnecessary overhead, the LA used in MF is reused in this unit. Specifically, this unit reads a column of $\hat{\mathbf{A}}^{-1}$ each clock cycle, multiplies it with an entry in $\hat{\mathbf{y}}^{\mathrm{MF}}$ and next adds it to the previous result.

## B. Block Diagonal Inversion Based on Cholesky

Considering the BD sub-matrices are all Hermitian, Cholesky algorithm is employed here to calculate the inversion. Based on the previous work [15], the high-level block diagram of Cholesky algorithm is depicted in Fig. 15. First, a systolic array is utilized to decompose the matrix $\mathbf{D}$, and obtains a lower triangular matrix L. Next, $\mathbf{L}^{-1}$ is calculated by the forward substitution module [15]. Finally, an $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$ matrix multiplication module is used to compute $\mathbf{D}^{-1}=\left(\mathbf{L}^{\mathrm{H}}\right)^{-1} \mathbf{L}^{-1}$ as output.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-10.jpg?height=386&width=600&top_left_y=227&top_left_x=279)
Fig. 16. Architecture of Cholesky decomposition (Recip. $=$ Reciprocal).

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-10.jpg?height=364&width=650&top_left_y=696&top_left_x=257)
Fig. 17. Pipeline architecture of the PE3.

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-10.jpg?height=475&width=619&top_left_y=1160&top_left_x=262)
Fig. 18. Pipeline architecture of the PE4.

Take decomposing a $3 \times 3$ Hermitian matrix $\mathbf{D}_{(2, t)}$ as an example. An efficient systolic array architecture is designed as shown in Fig. 16, which contains four types of PEs. The PE in the last row and the last column on the systolic array is denoted as PE2, which consists of a square-root unit. And the remained PEs on the diagonal are classified as PE1 that contains a square-root module and a reciprocal unit.

Fig. 17 shows the architecture of PE3, which is composed of one adder, one CM and one real-complex multiplier (RCM) that executes a real number multiplied to a complex number and requires two real multipliers. In PE3, the input $x$ is firstly multiplied to $y_{1}$ and the product is taken as output out $t_{1}$. Next, out $t_{1}$ is fed back to the input of another multiplier and the other input is the conjugate of out ${ }_{1}$. Finally, the output of the multiplier is inverted and added with input $y_{2}$.

The architecture of PE4, containing one CM, one RCM, one adder and three multiplexers (MUXes), is depicted in Fig. 18. First, similar to that in PE3, the input $x_{1}$ is multiplied to $y_{1}$ and the result is regarded as output out ${ }_{1}$. Next, out ${ }_{1}$ is fed back to the input of other MUXes. The MUXes send $\bar{x}_{2}$ and out ${ }_{1}$ to the CM . Then the result of the CM is added with $y_{2}$ after taking the inverse. Finally, the MUXes send out ${ }_{1}$ and its conjugated
version to the CM , then the product is added with $y_{3}$ after taking the inverse.

The forward substitution is implemented by an MAC module which contains several PEs and an PE contains one multiplier and one subtracter. The detailed implementation of forward substitution is given in [15].

## C. Iteration Unit

Consisting of a matrix multiplier and a matrix adder, the unit owns an IIR-like structure and implements the matrix iterations in both SLI and FLI. First, when the iteration is in SLI, the inputs of this unit are $\mathbf{D}_{2}^{1^{-1}}$ and $\mathbf{D}_{2}^{1^{-1}} \cdot\left(\mathbf{D}_{2}^{1}-\right. \left.\mathbf{D}_{(1,1)}\right), \mathbf{D}_{2}^{2^{-1}}$ and $\mathbf{D}_{2}^{2^{-1}} \cdot\left(\mathbf{D}_{2}^{2}-\mathbf{D}_{(1,2)}\right)$. Next, when iteration is in FLI, the inputs change to $\mathbf{D}_{1}^{-1}$ and $\mathbf{D}_{1}^{-1} \cdot\left(\mathbf{D}_{1}-\mathbf{A}\right)$. For conciseness, we uniformly denote the iteration matrix as $\mathbf{W}^{-1}(L)$ and $-\mathbf{D}^{-1} \mathbf{E}$ as $\boldsymbol{\Psi}$, hence the iteration can be formulated as Eq. (29). Since $\mathbf{W}^{-1}(L)$ is Hermitian ${ }^{4}$, matrix multiplier can be implemented by a LTSA and the upper-triangular part can be obtained by conjugating.

$$
\left\{\begin{array}{l}
\mathbf{W}^{-1}(1)=\mathbf{D}^{-1}  \tag{29}\\
\mathbf{W}^{-1}(L)=\Psi \mathbf{W}^{-1}(L-1)+\mathbf{D}^{-1}
\end{array}\right.
$$

Further, the size of the lower systolic array needs to be determined. Obviously, the sizes of the input matrices of SLI and FLI are different. If SLI and FLI are implemented with two separate iteration units, it will result in extra overhead. Moreover, if the two groups of input data in SLI are calculated serially, the significant latency will be introduced. However, unnecessary hardware area will be increased, if the direct parallel mode is adopted. To this end, through utilizing the computational properties of block matrices, i.e., the product of matrix is equivalent to the product of corresponding block matrix, we implement the matrix multipliers of iteration module uniformly by an $M \times M$ LTSA. Therefore, the matrix multiplier can be implemented by reusing the LTSA in PU. It should be noted that such design is able to implement the two iterations in SLI at the same time and perform the iteration in FLI.

## D. Block Diagonal Multiplier

This module calculates the corresponding $\boldsymbol{\Psi}$ in FLI and SLI. Considering in SLI, to calculate $\mathbf{D}_{2}^{1^{-1}} \cdot\left(\mathbf{D}_{2}^{1}-\mathbf{D}_{(\mathbf{1}, \mathbf{1})}\right)$, every block diagonal element of $\mathbf{D}_{2}^{1-1}$ is multiplied with corresponding row of $\left(\mathbf{D}_{2}^{1}-\mathbf{D}_{(\mathbf{1}, \mathbf{1})}\right)$. Moreover, in FLI, the elements in $\mathbf{D}_{1}^{-1}$ are also multiplied with corresponding row of $\left(\mathbf{D}_{1}-\mathbf{A}\right)$. To reuse this module in SLI and FLI, we employ two systolic arrays with size $\frac{M}{2} \times \frac{M}{2}$ for calculation.

## E. Time Analysis

Fig. 19 illustrates the overall time schedule of TL-BD-INSA with $m_{\mathrm{UE}}=2$. The MF requires ( $N+M-1$ ) clock cycles. The computation of Gram matrix and scaling needs ( $N+ 2 M$ ) clock cycles in total. The BD inversion modules begin to operate since the first block sub-matrix of the Gram matrix is output. To obtain the inversion of a block sub-matrix, such as $\mathbf{D}_{2}^{1}$, it will take 12 clock cycles. For each iteration in SLI, it requires $(3 M / 2-2)$ clock cycles. After that, $(3 M-2)$ clock cycles are

[^2]![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-11.jpg?height=405&width=1689&top_left_y=225&top_left_x=174)
Fig. 19. The processing schedule of TL-BD-INSA detector $\left(m_{\mathrm{UE}}=2\right)$.

TABLE III
Implementation Results and Comparison for $128 \times 8$ MIMO Detectors
| Detector | This work | M. Wu [15] [JSTSP'14] |  | Z. Wu [30] [ISCAS'16] | B. Yin [39] [ISCAS'15] | C. Zhang [24] [TVT' 19] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Algorithm | TL-BD-INSA | Cholesky | NSA | GS-NSA | CG | TMA |
| Modulation | 64-QAM | 64-QAM | 64-QAM | 64-QAM | 64-QAM | 64-QAM |
| Iteration count | 3 | - | 3 | 1 | 3 | 3 |
| Instance or subcarrier | 1 | 8 | 8 | 1 | 1 | 10 |
| $E_{b} / N_{0} @ \mathrm{BER}=10^{-3}$ (channel 4) | 8.3 | 8.2 | 16 | NA | 9.4 | 9.2 |
| $E_{b} / N_{0} @ \mathrm{BER}=10^{-3}$ (channel 5) | 10.5 | 10.2 | NA | NA | 13.5 | NA |
| LUT slices | 13,640 | 208, 161 | 168, 125 | 18,976 | 3,324 | 91,353 |
| FF slices | 19,460 | 213, 226 | 193,451 | 15,864 | 3,878 | 69,784 |
| DSP48 units | 277 | 1,447 | 1,059 | 232 | 33 | 2,000 |
| Block RAMs | 1 | 65 | 18 | 6 | 1 | 40 |
| Latency [clks] | 260 | 202 | 202 | 311 | 951 | 169 |
| Maximum frequency [MHz] | 310 | 317 | 317 | 309 | 412 | 225 |
| Throughput [Mbps] | 57.3 | 603 | 603 | 48 | 20 | 630 |
| Throughtput/slices [bps/slices] | 1,731 | 1,430 | 1,667 | 1,377 | 2,777 | 3,909 |


![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-11.jpg?height=639&width=800&top_left_y=1428&top_left_x=165)
Fig. 20. Fixed-point performance of TL-BD-INSA based detector.

needed for each iteration of FLI. Finally, the Estimation Unit outputs the equalization vector after $M$ clock cycles.

## F. FPGA Implementation Results

In order to demonstrate the efficiency of the proposed TL-BD-INSA based detector, we provide an implementation on a Xilinx Virtex-7 XC7VX980 T FPGA and compare it to the SOAs. Fixed-point arithmetic is utilized: the input and output signals contain 15 bits per complex dimension and output of multipliers is 30 bits. The ROM of reciprocal module has 1024

TABLE IV
ASIC Implementation Results of TL-BD-INSA Detector
| Comparison item | This work | M. Wu [15] (results from [40] ) |
| :--- | :--- | :--- |
| CMOS technology | TSMC 45 nm | TSMC 45 nm |
| Inverse method | TL-BD-INSA | NSA |
| Modulation | 64-QAM | 64-QAM |
| Instance or subcarrier | 1 | 8 |
| $E_{b} / N_{0} @ \mathrm{BER}=10^{-3}{ }^{(1)}$ | 8.3 | 16 |
| Gate count ${ }^{(2)}$ [kGE] | 572 | 6650 |
| Supply voltage [V] | 0.81 | 0.81 |
| Area [ $\mathrm{mm}^{2}$ ] | 0.400 | 4.65 |
| Clock Freq. [MHz] | 1000 | 1000 |
| Power [W] | 0.144 | 1.72 |
| Throughput [Gbps] | 0.185 | 2.00 |
| Energy Eff. ${ }^{(3)}$ [Gbps/W] | 1.28 | 1.16 |
| Area Eff. ${ }^{(3)}$ [ $\mathrm{Gbps} / \mathrm{mm}^{2}$ ] | 0.463 | 0.430 |


${ }^{(1)}$ Results reported from channel 4.
${ }^{(2)}$ Estimated by 2 -input NAND gate.
${ }^{(3)}$ Energy efficiency $=$ throughput/power, area efficiency $=$ throughput/area.
addresses and 14 b outputs. As shown in Fig. 20, the performance loss of the fixed-point TL-BD-INSA is within 0.1 dB compared to that of the floating-point design in MAUE system with IPE, NPE and BPE .

In order to make a fair comparison, the designs of Cholesky detector [15], NSA detector [15], GS-NSA detector [30], CG detector [39] and TMA detector [24] are all mapped to the same FPGA using 64-QAM with a $128 \times 8$ antenna configuration. Here we assume that $m=4$ and $m_{\mathrm{UE}}=2$. The implementation results are summarized in Table III. It is noted that in terms
of Throughput/slices, the TL-BD-INSA detector achieves 21\%, $25.7 \%$ higher hardware efficiency compared with the Cholesky and GS-NSA based detectors, respectively. Furthermore, it can outperform the NSA detector $3.8 \%$ in hardware efficiency while showing better convergence as exhibited in Section IV-A. The hardware advantages mainly come from the reuse of the $8 \times 8$ LTSA in PU and Iteration unit, the reuse of the LA in MF and Estimation Unit and the pipelined structure to improve maximum frequency. It is worth mentioning that although CG and TMA detectors are more efficient in terms of Throughput/slices than the proposed detector, as aforementioned, they cannot provide satisfactory results under some challenging correlated MAUE channels, e.g., $256 \times 24$ antenna configuration with $\zeta_{t}=0.9$, $\zeta_{r}=0.5, m_{\mathrm{UE}}=6$, as shown in Fig. 9. Therefore, the implemented results further show that the proposed detector can achieve an overall superior tradeoff between error performance and hardware efficiency.

## G. ASIC Implementation Results

In this subsection, the ASIC implementation results of the proposed TL-BD-INSA detector are presented. The detector is implemented on TSMC 45-nm CMOS process and synthesized by Synopsys Design Compiler. The implementation is compared with the NSA based detector [15]. It can be observed that the detector can achieve 185 Mbps throughput at 1 GHz frequency. Furthermore, the energy efficiency and area efficiency of the TL-BD-INSA are $1.1 \times$ and $1.07 \times$ that of NSA, respectively. The implementation on ASIC further proves the relevance of our detector in practice.

## VI. Conclusion

In this paper, we propose a universal detector, TL-BD-INSA detector, which can achieve near-MMSE performance in both the ideal uncorrelated M-MIMO channels and the challenging correlated M-MIMO channels with MAUE systems at the expense of moderate computational complexity. Theoretical and numerical results validate the practical advantages of the proposed algorithm. The implementation results on FPGA and ASIC demonstrate the proposed detector achieves a well tradeoff between error-rate performance and complexity.

There are many avenues for future work. The proposed design can be applied to improve the MMSE detectors serving for D-MIMO [31], in which the channel exhibits block diagonal property prominently after interference suppression. Also, it can be applied to the expectation propagation (EP) detector [41], which involves an inevitable and explicit inversion of Gram matrix in each iteration. However, a limitation of this work is only the scenarios based on single BS are considered, hence the extension of our proposed algorithm to decentralized architectures [42]-[44] is a direction worth to pursue in the future. Finally, the corresponding hardware-based investigation for reducing latency is part of ongoing work.

## Appendix A

## Proof for the Normalization Factor $\alpha_{\text {opt }}^{+}$

## A. Theoretical Solution of $\alpha_{\mathrm{opt}}^{+}$in Ideal M-MIMO With SAUE

The necessary and sufficient condition for the convergence of Eq. (6) is as follows [38]:

$$
\begin{equation*}
\rho_{r}=\rho\left(\mathbf{I}-\mathbf{D}^{-1} \mathbf{A}\right)<1 . \tag{30}
\end{equation*}
$$

Further, assume $\lambda_{\text {max }}$ and $\lambda_{\text {min }}$ represent the maximum and minimum eigenvalues of $\mathbf{D}^{-1} \mathbf{A}$, respectively:

$$
\begin{equation*}
\rho_{r}=\max \left\{\left|\lambda_{\max }-1\right|,\left|\lambda_{\min }-1\right|\right\} . \tag{31}
\end{equation*}
$$

The normalization factor method remains the diagonal entries of $\mathbf{A}$ to construct $\mathbf{D}$, but enlarges it with coefficient $\alpha$ :

$$
\begin{equation*}
\rho\left(\mathbf{I}-\frac{1}{\alpha} \mathbf{D}^{-1} \mathbf{A}\right)=\max \left\{\left|\frac{1}{\alpha} \lambda_{\max }-1\right|,\left|\frac{1}{\alpha} \lambda_{\min }-1\right|\right\} . \tag{32}
\end{equation*}
$$

Since $\mathbf{D}^{-1} \mathbf{A}$ is positive definite Hermitian matrix, its eigenvalues are all positive real numbers. Suppose $\lambda_{\text {max }}>1,0< \lambda_{\text {min }}<1$ (In the following, we will prove this assumption establishes), then $\alpha$ should satisfy:

$$
\begin{equation*}
\left|\frac{1}{\alpha} \lambda_{\max }-1\right|=\left|\frac{1}{\alpha} \lambda_{\min }-1\right| \rightarrow \frac{1}{\alpha} \lambda_{\max }-1=1-\frac{1}{\alpha} \lambda_{\min } . \tag{33}
\end{equation*}
$$

Therefore:

$$
\begin{align*}
\alpha & =\frac{\lambda_{\max }+\lambda_{\min }}{2} \\
\alpha_{\mathrm{opt}}^{+} & =\frac{\mathbb{E}\left\{\lambda_{\max }\right\}+\mathbb{E}\left\{\lambda_{\min }\right\}}{2} . \tag{34}
\end{align*}
$$

Hence, the problem is transformed into finding the expectation of the maximum and minimum eigenvalues of $\mathbf{D}^{-1} \mathbf{A}$.

Since $\mathbf{A}=\mathbf{G}+N_{0} \mathbf{I}, \mathbf{G}=\mathbf{H}^{\mathrm{H}} \mathbf{H}$ and the regularization term $N_{0} \mathbf{I}$ is relatively small, we can think $\mathbf{D}^{-1} \mathbf{A} \approx \mathbf{D}^{-1} \mathbf{G}$, then we can get:

$$
\begin{equation*}
\mathbf{D}^{-1} \mathbf{A}=\operatorname{diag}\left[\sum_{i=1}^{N}\left|h_{i 1}\right|^{2}, \ldots, \sum_{i=1}^{N}\left|h_{i M}\right|^{2}\right]^{-1} \cdot \mathbf{H}^{\mathrm{H}} \mathbf{H} . \tag{35}
\end{equation*}
$$

Under the ideal conditions of communication, the entries of $\mathbf{H}$ are i.i.d and follow the distribution $\mathcal{C} \mathcal{N}(0,1), N / M=\beta$ and $\beta>5$, then we have

$$
\begin{equation*}
\mathbf{D}^{-1} \mathbf{A} \approx \frac{\mathbf{H}^{\mathrm{H}} \mathbf{H}}{N \mathrm{E}\left\{\left|h_{i j}\right|^{2}\right\}}=\frac{1}{N} \mathbf{H}^{\mathrm{H}} \mathbf{H} . \tag{36}
\end{equation*}
$$

According to Marcenko-Pastur law, the probability density function of eigenvalue distribution of $\mathbf{D}^{-1} \mathbf{A}$ is:

$$
f_{\beta}(\lambda)= \begin{cases}\frac{\sqrt{(\lambda-a)(b-\lambda)}}{2 \pi \beta \lambda}, & a \leq \lambda \leq b  \tag{37}\\ 0, & \text { otherwise }\end{cases}
$$

where $a=(1-\sqrt{\beta})^{2}, b=(1+\sqrt{\beta})^{2}$.
Since $\mathbf{D}$ owns $M$ eigenvalues, the problem is further transformed into: $M$ samples $\lambda_{1}, \lambda_{2}, \ldots, \lambda_{M}$ of random variables $\lambda$ are obtained by one observation and each sample is i.i.d and follows the probability density function $f_{\beta}(\lambda)$, find the $\mathbb{E}\left\{\lambda_{\max }\right\}$ and $\mathbb{E}\left\{\lambda_{\text {min }}\right\}$.

The above problem can be solved by the method we proposed in [45]. First, we need to find the probability distribution function of random variable $\lambda$ :

$$
\begin{align*}
F_{\beta}(\lambda) & =\int_{-\infty}^{\lambda} f_{\beta}(x) \mathrm{d} x=\int_{a}^{\lambda} \frac{\sqrt{(x-a)(b-x)}}{2 \pi \beta x} \mathrm{~d} x \\
& =\int_{a}^{\lambda} \frac{\sqrt{\left(\frac{b-a}{2}\right)^{2}-\left(x-\frac{(a+b)}{2}\right)^{2}}}{2 \pi \beta x} \mathrm{~d} x \tag{38}
\end{align*}
$$

Denote $r=\frac{b-a}{2}$ and $\omega=x-\frac{a+b}{2}$, then Eq. (38) can be rewritten as:

$$
\begin{equation*}
F_{\beta}(\lambda)=\int_{-r}^{r-(b-\lambda)} \frac{\sqrt{r^{2}-\omega^{2}}}{2 \pi \beta\left(\omega+\frac{a+b}{2}\right)} \mathrm{d} \omega \tag{39}
\end{equation*}
$$

Further, let $\omega=r \sin \theta$, then the upper and lower integral bounds of Eq. (39) become

$$
\begin{equation*}
\theta_{1}=\arcsin (-1)=-\frac{\pi}{2}, \theta_{2}=\arcsin \left(1-\frac{b-\lambda}{r}\right) \tag{40}
\end{equation*}
$$

and Eq. (39) can be rewritten as:

$$
\begin{align*}
F_{\beta}(\lambda) & =\frac{1}{2 \pi \beta} \int_{-\frac{\pi}{2}}^{\theta_{2}} \frac{\sqrt{r^{2}-r^{2} \sin ^{2} \theta}}{r \sin \theta+\frac{a+b}{2}} \mathrm{~d} r \sin \theta  \tag{41}\\
& =\frac{r}{2 \pi \beta} \int_{-\frac{\pi}{2}}^{\theta_{2}} \frac{\cos ^{2} \theta}{\sin \theta+\frac{a+b}{2 r}} \mathrm{~d} \theta
\end{align*}
$$

Denote $k=\frac{r}{2 \pi \beta}, A=\frac{a+b}{2 r}=\frac{a+b}{b-a}$, apparently, $A>1 ; \Omega= \sin \theta+A$, then we can obtain:

$$
\begin{align*}
\sin ^{2} \theta & =(\Omega-A)^{2}=1-\cos ^{2} \theta \\
\cos ^{2} \theta & =1-(\Omega-A)^{2}=-\Omega^{2}+2 A \Omega-\left(A^{2}-1\right)  \tag{42}\\
F_{\beta}(\lambda) & =k \int_{-\frac{\pi}{2}}^{\theta_{2}} \frac{-\Omega^{2}+2 A \Omega-\left(A^{2}-1\right)}{\Omega} \mathrm{d} \theta \\
& =k \int_{-\frac{\pi}{2}}^{\theta_{2}}(-\Omega+2 A) \mathrm{d} \theta-k\left(A^{2}-1\right) \int_{-\frac{\pi}{2}}^{\theta_{2}} \frac{1}{\Omega} \mathrm{~d} \theta  \tag{43}\\
& =k I_{1}-k\left(A^{2}-1\right) I_{2}
\end{align*}
$$

where

$$
\begin{align*}
& I_{1}=\int_{-\frac{\pi}{2}}^{\theta_{2}}(-(\sin \theta+A)+2 A) \mathrm{d} \theta=A\left(\theta_{2}+\frac{\pi}{2}\right)+\cos \theta_{2}  \tag{44}\\
& I_{2}=\int_{-\frac{\pi}{2}}^{\theta_{2}} \frac{1}{\sin \theta+A} \mathrm{~d} \theta \tag{45}
\end{align*}
$$

Further, let $t=\tan \frac{\theta}{2}, \sin \theta=\frac{2 t}{1+t^{2}}, \mathrm{~d} \theta=\frac{2}{1+t^{2}} \mathrm{~d} t$, then Eq. (45) can be rewritten as:

$$
\begin{align*}
I_{2} & =\int_{t_{1}}^{t_{2}} \frac{1}{\frac{2 t}{1+t^{2}}+A} \cdot \frac{2}{1+t^{2}} \mathrm{~d} t \\
& =\frac{2}{A\left(1-\frac{1}{A^{2}}\right)} \int_{-1+\frac{1}{A}}^{t_{2}+\frac{1}{A}} \frac{1}{1+\frac{A^{2}}{A^{2}-1} t^{2}} \mathrm{~d} t \tag{46}
\end{align*}
$$

where $t_{1}=\tan \left(-\frac{\pi}{4}\right)=-1$ and $t_{2}=\tan \frac{\theta_{2}}{2}$.
Further, denote $B=\sqrt{A^{2}-1}$ and let $\mu=\frac{A}{B} t$, then the lower and upper integral bounds of Eq. (46) become:

$$
\begin{align*}
& \mu_{1}=\frac{A}{B}\left(-1+\frac{1}{A}\right)=\frac{-A+1}{B} \\
& \mu_{2}=\frac{A}{B}\left(t_{2}+\frac{1}{A}\right)=\frac{A t_{2}+1}{B}=\frac{A \tan \frac{\theta_{2}}{2}+1}{B} \tag{47}
\end{align*}
$$

Then we can obtain:

$$
\begin{align*}
I_{2} & =\frac{2}{B^{2} / A} \int_{\mu_{1}}^{\mu_{2}} \frac{1}{1+\mu^{2}} \mathrm{~d} \frac{B}{A} \mu=\left.\frac{2}{B} \arctan \mu\right|_{\mu_{1}} ^{\mu_{2}} \\
& =\frac{2}{B}\left(\arctan \left(\frac{A \tan \frac{\theta_{2}}{2}+1}{B}\right)-\arctan \left(\frac{-A+1}{B}\right)\right) \tag{48}
\end{align*}
$$

Substitute Eq. (48) and Eq. (44) into Eq. (43), we can obtain the expression of $F_{\beta}(\lambda)$ as Eq. (49), where,

$$
\begin{align*}
& \beta=\frac{M}{N}, \quad a=(1-\sqrt{\beta})^{2}, \quad b=(1+\sqrt{\beta})^{2} \\
& r=\frac{b-a}{2}, \quad k=\frac{r}{2 \pi \beta}, \quad A=\frac{a+b}{2 r} \\
& B=\sqrt{A^{2}-1}, \quad \theta_{2}=\arcsin \left(1-\frac{b-\lambda}{r}\right) . \tag{50}
\end{align*}
$$

According to the decision criterion in [45], $\mathbb{E}\left\{\lambda_{\max }\right\}$ and $\mathbb{E}\left\{\lambda_{\text {min }}\right\}$ should satisfy:

$$
\begin{equation*}
\left[F_{\beta}\left(\mathbb{E}\left\{\lambda_{\max }\right\}\right)\right]^{M}=\frac{1}{2}, \quad\left[1-F_{\beta}\left(\mathbb{E}\left\{\lambda_{\min }\right\}\right)\right]^{M}=\frac{1}{2} \tag{51}
\end{equation*}
$$

which is equal to:

$$
\begin{equation*}
F_{\beta}\left(\mathbb{E}\left\{\lambda_{\max }\right\}\right)=\left(\frac{1}{2}\right)^{\frac{1}{M}}, F_{\beta}\left(\mathbb{E}\left\{\lambda_{\min }\right\}\right)=1-\left(\frac{1}{2}\right)^{\frac{1}{M}} \tag{52}
\end{equation*}
$$

## B. Theoretical Solution and Monte Carlo Verification of $\alpha_{\mathrm{opt}}^{+}$ in M-MIMO With MAUE System

First, assume under MAUE system with ideal propagation conditions, the entries in channel matrix $\mathbf{H}$ are i.i.d and follow the distribution $\mathcal{C} \mathcal{N}(0,1), M, N \rightarrow \infty$ and $M / N=\beta$. When D is diagonal matrix, it can be deduced:

$$
\begin{align*}
\operatorname{det}\left(\mathbf{D}^{-1} \mathbf{A}\right) & =\left.\operatorname{diag}\left|\sum_{i=1}^{N}\right| h_{i 1}\right|^{2}, \ldots,\left.\sum_{i=1}^{N}\left|h_{i M}\right|^{2}\right|^{-1}\left|\mathbf{H}^{\mathrm{H}} \mathbf{H}\right|  \tag{53}\\
& \approx \frac{\prod_{j=1}^{M} \lambda_{j}}{\prod_{j=1}^{M}\left|h_{i j}\right|^{2}}
\end{align*}
$$

where

1) $\lambda_{j}(j=1 \cdots M)$ are the $M$ eigenvalues of $\frac{1}{N} \mathbf{H}^{\mathrm{H}} \mathbf{H}$;
2) $\left|h_{i, j}\right|^{2}$ is the modular square of entries in $\mathbf{H}$, and its probability density function is:

$$
f_{\beta_{0}}(\lambda)=\left\{\begin{array}{lr}
e^{-x}, & x \geq 0  \tag{54}\\
0, & \text { otherwise }
\end{array}\right.
$$

its mathematical expectation is Eq. (55):

$$
\begin{equation*}
\mathrm{E}\left\{\left|h_{i j}\right|^{2}\right\}=\int_{-\infty}^{+\infty} x f(x) \mathrm{d} x=\int_{0}^{+\infty} x e^{-x} \mathrm{~d} x=1 \tag{55}
\end{equation*}
$$

$$
F_{\beta}(\lambda)=k\left(A\left(\theta_{2}+\frac{\pi}{2}\right)+\cos \theta_{2}-2 B\left(\arctan \left(\frac{A \tan \frac{\theta_{2}}{2}+1}{B}\right)-\arctan \left(\frac{-A+1}{B}\right)\right)\right) .
$$

Next, when $\mathbf{D}$ is a block diagonal matrix, it is composed of $m$ size- $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$ sub-matrices, hence we can obtain:

$$
\begin{align*}
\operatorname{det}\left(\mathbf{D}^{-1} \mathbf{A}\right) & =\operatorname{diag}\left|\mathbf{D}_{1}^{-1}, \mathbf{D}_{2}^{-1}, \ldots, \mathbf{D}_{m}^{-1}\right|\left|\mathbf{H}^{H} \mathbf{H}\right| \\
& =\frac{\prod_{j=1}^{M} \lambda_{j}}{\prod_{p=1}^{m} \prod_{q=1}^{m_{U E}} \lambda_{p q}} \tag{57}
\end{align*}
$$

1) $\mathbf{D}_{p}=\mathbf{H}_{p}^{\mathrm{H}} \mathbf{H}_{p}(p=1,2, \ldots, m), \mathbf{H}_{p} \quad$ is an $N \times m_{\mathrm{UE}}$ block matrix in $\mathbf{H}$;
2) $\lambda_{p q}\left(q=1, \ldots, m_{\mathrm{UE}}\right)$ are $m_{\mathrm{UE}}$ eigenvalues of $\frac{1}{N} \mathbf{D}_{p}$, whose probability density function is

$$
f_{\beta_{0}}(\lambda)=\left\{\begin{array}{lc}
\frac{\sqrt{\left(\lambda-a_{0}\right)\left(b_{0}-\lambda\right)}}{2 \pi \beta_{0} \lambda}, & a_{0} \leq \lambda \leq b_{0}  \tag{58}\\
0, & \text { otherwise }
\end{array}\right.
$$

$$
\begin{equation*}
\beta_{0}=\frac{m_{\mathrm{UE}}}{N}, a_{0}=\left(1-\sqrt{\beta_{0}}\right)^{2}, b_{0}=\left(1+\sqrt{\beta_{0}}\right)^{2} . \tag{59}
\end{equation*}
$$

The mathematical expectation is:

$$
\begin{align*}
\mathbb{E}\left\{\lambda_{p q}\right\} & =\int_{-\infty}^{+\infty} \lambda f_{\beta_{0}}(\lambda) \mathrm{d} \lambda=\int_{a_{0}}^{b_{0}} \lambda \frac{\sqrt{\left(\lambda-a_{0}\right)\left(b_{0}-\lambda\right)}}{2 \pi \beta_{0} \lambda} \mathrm{~d} \lambda  \tag{60}\\
& =\int_{-r_{0}}^{r_{0}} \frac{\sqrt{r_{0}^{2}-\omega^{2}}}{2 \pi \beta_{0}} \mathrm{~d} \omega=\frac{\left(b_{0}-a_{0}\right)^{2}}{16 \beta_{0}}=1 .
\end{align*}
$$

As shown in Eqs. (55) and (60), it can be observed $\mathbb{E}\left\{\left|h_{j}\right|^{2}\right\}= \mathbb{E}\left\{\lambda_{p q}\right\}=1$, thus, Eqs. (53) and (57) can be regarded as equal approximately. In other words, whether $\mathbf{D}$ is a diagonal or block diagonal matrix, the product of all eigenvalues of $\mathbf{D}^{-1} \mathbf{A}$ remains unchanged, hence its maximum and minimum eigenvalues do not change significantly.

When the channel is correlated in MAUE system, we compares the change of $\alpha_{\text {opt }}$ through Monte Carlo simulation. As illustrated in Fig. 21, the value of $\alpha_{\text {opt }}^{+}$is the same in the ideal channel and related channel under the same configuration. Therefore, the $\alpha_{\text {opt }}^{+}$obtained in ideal M-MIMO with SAUE is also suitable to MAUE system with correlation. $\square$

## Appendix B <br> Deduction for the Complexity of BD-INSA

For Eq. (18), the NCMs need to compute $\alpha_{\text {opt }}^{+} \mathbf{D}$ are:

$$
\begin{equation*}
\frac{K}{m_{\mathrm{UE}}} \cdot m_{\mathrm{UE}} \cdot m_{\mathrm{UE}}=K m_{\mathrm{UE}} . \tag{61}
\end{equation*}
$$

The inversion of an $m_{\mathrm{UE}} \times m_{\mathrm{UE}}$ matrix needs $2 m_{\mathrm{UE}}^{3}+ 2 m_{\mathrm{UE}} \mathrm{CMs}$ by Cholesky algorithm. Since there are $\frac{K}{m_{\mathrm{UE}}}$ submatrices in $\alpha_{\text {opt }}^{+} \mathbf{D}$, the CMs required by $\left(\alpha_{\text {opt }}^{+} \mathbf{D}\right)^{-1}$ are:

$$
\begin{equation*}
\frac{K}{m_{\mathrm{UE}}} \cdot\left(2 m_{\mathrm{UE}}^{3}+2 m_{\mathrm{UE}}\right)=2 K m_{\mathrm{UE}}^{2}+2 K . \tag{62}
\end{equation*}
$$

![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-14.jpg?height=618&width=794&top_left_y=227&top_left_x=1095)
Fig. 21. Monte Carlo results of $\alpha_{\mathrm{opt}}^{+}$versus different $M, m_{\mathrm{UE}}$ and $\zeta_{t}$.

For convenience of further analysis, denote $\mathbf{Y}(k)=\mathbf{W}_{k}^{-1}$, $\mathbf{N}=-\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}\right)^{-1} \mathbf{E}, \mathbf{M}=\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}\right)^{-1}$, then Eq. (18) can be rewritten as:

$$
\left\{\begin{array}{l}
\mathbf{Y}(1)=\mathbf{M},  \tag{63}\\
\mathbf{Y}(2)=\mathbf{M}+\mathbf{N M}=\mathbf{Y}(1)+\mathbf{N M}, \\
\mathbf{Y}(3)=\mathbf{M}+\mathbf{N M}+\mathbf{N}^{2} \mathbf{M}=\mathbf{Y}(2)+\mathbf{N N M}, \\
\ldots
\end{array}\right.
$$

To obtain the $\mathbf{N}$, i.e., computing $\left(-\left(\alpha_{\mathrm{opt}}^{+} \mathbf{D}\right)^{-1}\right) \cdot \mathbf{E}$, the NCMs required are $K^{2} m_{\mathrm{UE}}-K m_{\mathrm{UE}}^{2}$, which is consistent with that of $\mathbf{N} \cdot \mathbf{M}$. It is worth mentioning that, for the third term, $\mathbf{N} \cdot \mathbf{N M}$ requires $K m_{\mathrm{UE}}\left(K-m_{\mathrm{UE}}\right)+K\left(K-2 m_{\mathrm{UE}}\right)(K- \left.m_{\mathrm{UE}}\right) \mathrm{CMs}$, whereas for the fourth and later terms, each term needs $K^{2}\left(K-m_{\mathrm{UE}}\right)$ CMs. Therefore, the total NCMs in BDINSA with $k$ iteration counts can be concluded as Eq (56). $\square$

## Appendix C <br> Proof for the Hermitian Property of $\mathbf{W}^{-1}(L)$

The iteration formula Eq. (29) can be rewritten as:

$$
\begin{align*}
\mathbf{W}^{-1}(L) & =\mathbf{D}^{-1}+(-1)^{1}\left(\mathbf{D}^{-1} \mathbf{E} \mathbf{D}^{-1}\right) \\
& +\cdots+(-1)^{L-1} \underbrace{\left(\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E D}^{-1}\right)}_{2 L-1} \tag{64}
\end{align*}
$$

Since both $\mathbf{D}^{-1}$ and $\mathbf{E}$ are Hermitian, we can have:

$$
\begin{equation*}
\left(\mathbf{D}^{-1} \mathbf{E D}^{-1}\right)^{\mathrm{H}}=\left(\mathbf{D}^{-1}\right)^{\mathrm{H}} \mathbf{E}^{\mathrm{H}}\left(\mathbf{D}^{-1}\right)^{\mathrm{H}}=\left(\mathbf{D}^{-1} \mathbf{E D}^{-1}\right)^{\mathrm{H}} . \tag{65}
\end{equation*}
$$

Assume for the arbitrary $l$-th term:

$$
\begin{equation*}
\underbrace{\left(\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E D}^{-1}\right)^{\mathrm{H}}}_{2 l-1}=\underbrace{\left(\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E D}^{-1}\right)}_{2 l-1} . \tag{66}
\end{equation*}
$$

$$
\begin{aligned}
N & =K m_{U E}+2 K m_{U E}^{2}+2 K+2 K^{2} m_{U E}-K m_{U E}^{2}+(k-2)\left(K^{3}-2 K^{2} m_{U E}+K m_{U E}^{2}\right)+(k-3)\left(K^{2} m_{U E}-K m_{U E}^{2}\right) \\
& =(k-2) K^{3}-(k-3) K^{2} m_{U E}+2 K m_{U E}^{2}+K m_{U E}+2 K \\
& \approx(k-2) K^{3}-(k-3) K^{2} m_{U E}+2 K m_{U E}^{2}
\end{aligned}
$$

Then, for the arbitrary $l+1$-th term:

$$
\begin{align*}
& \underbrace{\left(\mathbf{D}^{-1} \mathbf{E}\right.}_{2} \underbrace{\left.\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E D}^{-1}\right)^{\mathrm{H}}}_{2 l-1} \\
& =\underbrace{\left(\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E D}^{-1}\right)^{\mathrm{H}}}_{2 l-1} \underbrace{\left(\mathbf{D}^{-1} \mathbf{E}\right)^{\mathrm{H}}}_{2}  \tag{67}\\
& =\underbrace{\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E D}^{-1}}_{2 l-1} \underbrace{\mathbf{E}^{\mathrm{H}}\left(\mathbf{D}^{-1}\right)^{\mathrm{H}}}_{2} \\
& =\underbrace{\mathbf{D}^{-1} \mathbf{E} \cdots \mathbf{D}^{-1} \mathbf{E} \mathbf{D}^{-1} \mathbf{E D}^{-1}}_{2 l+1} .
\end{align*}
$$

Therefore, $\mathbf{W}^{-1}(L)$ is a Hermitian matrix.

## References

[1] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays," IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40-60, Jan. 2013.
[2] J. G. Andrews et al., "What will 5G be?" IEEE J. Sel. Areas Commun., vol. 32, no. 6, pp. 1065-1082, Jun. 2014.
[3] T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Trans. Wireless Commun., vol. 9, no. 11, pp. 3590-3600, Nov. 2010.
[4] H. Q. Ngo, E. G. Larsson, and T. L. Marzetta, "Energy and spectral efficiency of very large multiuser MIMO systems," IEEE Trans. Commun., vol. 61, no. 4, pp. 1436-1449, Apr. 2013.
[5] J. Hoydis, S. Ten Brink, and M. Debbah, "Massive MIMO in the UL/DL of cellular networks: How many antennas do we need?," IEEE J. Sel. Areas Commun., vol. 31, no. 2, pp. 160-171, Feb. 2013.
[6] X. Gao, L. Dai, Y. Hu, Y. Zhang, and Z. Wang, "Low-complexity signal detection for large-scale MIMO in optical wireless communications," IEEE J. Sel. Areas Commun., vol. 33, no. 9, pp. 1903-1912, Sep. 2015.
[7] X. Chu and J. McAllister, "Software-defined sphere decoding for FPGAbased MIMO detection," IEEE Trans. Signal Process., vol. 60, no. 11, pp. 6017-6026, Nov. 2012.
[8] Z.-Y. Huang and P.-Y. Tsai, "Efficient implementation of QR decomposition for gigabit MIMO-OFDM systems," IEEE Trans. Circuits Syst. I, vol. 58, no. 10, pp. 2531-2542, Oct. 2011.
[9] D. Shnidman, "A generalized nyquist criterion and an optimum linear receiver for a pulse modulation system," Bell Syst. Tech. J., vol. 46, no. 9, pp. 2163-277, 1967.
[10] W. van Etten, "An optimum linear receiver for multiple channel digital transmission systems," IEEE Trans. Commun., vol. 23, no. 8, pp. 828-834, Aug. 1975.
[11] J. Hu and T. M. Duman, "Graph-based detection algorithms for layered space-time architectures," IEEE J. Sel. Areas Commun., vol. 26, no. 2, pp. 269-280, Feb. 2008.
[12] P. Som, T. Datta, A. Chockalingam, and B. S. Rajan, "Improved largeMIMO detection based on damped belief propagation," in Proc. IEEE Inf. Theory Workshop Inf. Theory, 2010, pp. 1-5.
[13] M. Moher, "An iterative multiuser decoder for near-capacity communications," IEEE Trans. Commun., vol. 46, no. 7, pp. 870-880, Jul. 1998.
[14] S. Sugiura, S. Chen, and L. Hanzo, "MIMO-aided near-capacity turbo transceivers: Taxonomy and performance versus complexity," IEEE Commun. Surveys Tuts., vol. 14, no. 2, pp. 421-442, Apr.-Jun. 2011.
[15] M. Wu, B. Yin, G. Wang, C. Dick, J. R. Cavallaro, and C. Studer, "Large-scale MIMO detection for 3GPP LTE: Algorithms and FPGA implementations," IEEE J. Sel. Topics Signal Process., vol. 8, no. 5, pp. 916-929, Oct. 2014.
[16] H. Prabhu, J. Rodrigues, O. Edfors, and F. Rusek, "Approximative matrix inverse computations for very-large MIMO and applications to linear precoding systems," in Proc. IEEE Wireless Commun. Netw. Conf., 2013, pp. 2710-2715.
[17] H. Prabhu, O. Edfors, J. Rodrigues, L. Liu, and F. Rusek, "Hardware efficient approximative matrix inversion for linear pre-coding in massive MIMO," in Proc. IEEE Int. Symp. Circuits Syst., 2014, pp. 1700-1703.
[18] A. Kammoun, A. Müller, E. Björnson, and M. Debbah, "Linear precoding based on polynomial expansion: Large-scale multi-cell MIMO systems," IEEE J. Sel. Topics Signal Process., vol. 8, no. 5, pp. 861-875, Oct. 2014.
[19] M. Wu, B. Yin, A. Vosoughi, C. Studer, J. R. Cavallaro, and C. Dick, "Approximate matrix inversion for high-throughput data detection in the large-scale MIMO uplink," in Proc. IEEE Int. Symp. Circuits Syst., 2013, pp. 2155-2158.
[20] M. Wu, B. Yin, K. Li, C. Dick, J. R. Cavallaro, and C. Studer, "Implicit vs. explicit approximate matrix inversion for wideband massive MU-MIMO data detection," J. Signal Process. Syst., vol. 90, no. 10, pp. 1311-1328, 2018.
[21] D. S. Watkins, Fundamentals of Matrix Computations. Hoboken, NJ, USA: Wiley, 2004.
[22] M. Matthaiou, M. R. McKay, P. J. Smith, and J. A. Nossek, "On the condition number distribution of complex wishart matrices," IEEE Trans. Commun., vol. 58, no. 6, pp. 1705-1717, Jun. 2010.
[23] H. Wu, J. Lin, C. Zhang, and Z. Wang, "Low-complexity detection algorithms based on matrix partition for massive MIMO," in Proc. IEEE Int. Conf. Wireless Commun. Signal Process., 2017, pp. 1-6.
[24] C. Zhang et al., "On the low-complexity, hardware-friendly tridiagonal matrix inversion for correlated massive MIMO systems," IEEE Trans. Veh. Technol., vol. 68, no. 7, pp. 6272-6285, Jul. 2019.
[25] W. Zhang, R. C. de Lamare, C. Pan, M. Chen, J. Dai, and B. Wu, "Simplified matrix polynomial-aided block diagonalization precoding for massive MIMO systems," in Proc. IEEE Sensor Array Multichannel Signal Process. Workshop, 2016, pp. 1-5.
[26] G. Sessler and F. Jondral, "Rapidly converging polynomial expansion multiuser detector with low complexity for CDMA systems," Electron. Lett., vol. 38, no. 17, pp. 997-998, 2002.
[27] G. M. Sessler and F. K. Jondral, "Low complexity polynomial expansion multiuser detector for CDMA systems," IEEE Trans. Veh. Technol., vol. 54, no. 4, pp. 1379-1391, Jul. 2005.
[28] X. Liang, C. Zhang, S. Xu, and X. You, "Coefficient adjustment matrix inversion approach and architecture for massive MIMO systems," in Proc. IEEE Int. Conf. ASIC, 2015, pp. 1-4.
$[29]$ B. Yin, M. Wu, J. R. Cavallaro, and C. Studer, "Conjugate gradient-based soft-output detection and precoding in massive MIMO systems," in Proc. IEEE Global Commun. Conf., 2014, pp. 3696-3701.
[30] Z. Wu, C. Zhang, Y. Xue, S. Xu, and X. You, "Efficient architecture for soft-output massive MIMO detection with gauss-seidel method," in Proc. IEEE Int. Symp. Circuits Syst., 2016, pp. 1886-1889.
$[31]$ D. Wang, C. Zhang, Y. Du, J. Zhao, M. Jiang, and X. You, "Implementation of a cloud-based cell-free distributed massive MIMO system," IEEE Commun. Mag., vol. 58, no. 8, pp. 61-67, Aug. 2020.
[32] K. Werner and M. Jansson, "Estimating MIMO channel covariances from training data under the kronecker model," Signal Process., vol. 89, no. 1, pp. 1-13, 2009.
[33] Q. H. Spencer, A. L. Swindlehurst, and M. Haardt, "Zero-forcing methods for downlink spatial multiplexing in multiuser MIMO channels," IEEE Trans. Signal Process., vol. 52, no. 2, pp. 461-471, Feb. 2004.
[34] H. Wei, D. Wang, and X. You, "Downlink and uplink transmissions in distributed large-scale MIMO systems for BD precoding with partial calibration," in Proc. IEEE Veh. Technol. Conf., 2016, pp. 1-5.
[35] C.-A. Chen, Y. Zao-Fu, C.-E. Chen, and Y.-H. Huang, "A generalized eigenvalue decomposition processor for multi-user MIMO precoding," in Proc. IEEE Asia Pacific Conf. Circuits Syst., 2016, pp. 281-284.
[36] Z. Quan and J. Liu, "Efficient complex matrix inversion for MIMO OFDM systems," J. Commun. Netw., vol. 19, no. 6, pp. 637-647, 2017.
[37] Y. Ji et al., "A low-complexity massive MIMO detection algorithm based on matrix partition," in Proc. IEEE Int. Workshop Signal Process. Syst., 2018, pp. 158-163.
[38] C. F. Van Loan and G. H. Golub, Matrix Computations. Baltimore: Johns Hopkins Univ. Press, 1983.
$[39]$ B. Yin, M. Wu, J. R. Cavallaro, and C. Studer, "VLSI design of large-scale soft-output MIMO detection using conjugate gradients," in Proc. IEEE Int. Symp. Circuits Syst., 2015, pp. 1498-1501.
[40] B. Yin, "Low complexity detection and precoding for massive MIMO systems: Algorithm, architecture, and application," Ph.D. dissertation, ECE Dept., Rice Univ., Houston TX, USA, 2014.
[41] J. Cespedes, P. M. Olmos, M. Sánchez-Fernández, and F. Perez-Cruz, "Expectation propagation detection for high-order high-dimensional MIMO systems," IEEE Trans. Commun., vol. 62, no. 8, pp. 2840-2849, Aug. 2014.
[42] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[43] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
[44] J. R. Sánchez, F. Rusek, O. Edfors, M. Sarajlić, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms," IEEE Trans. Signal Process., vol. 68, pp. 687-700, 2020.
[45] Y. Ji et al., "Quantum version of MMSE-based massive MIMO uplink detection," Quantum Inform. Process., vol. 19, no. 2, pp. 1-28, 2020.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=323&width=261&top_left_y=567&top_left_x=141)

Huizheng Wang was born in 1996. He received the B.S. degree from the Chien-Shiung Wu College (Honors College), Southeast University, Nanjing, China, where he is currently working toward the M.E. degree with the School of Information Science and Engineering. His current research interests include efficient algorithms and VLSI architectures for massive MIMO detection, polar decoder, and stochastic computing. He was the recipient of the Outstanding Undergraduate Award from Southeast University.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=321&width=261&top_left_y=941&top_left_x=141)

Yahui Ji received the B.S. degree in information engineering from Southeast University, Nanjing, China, in 2020. She is currently working toward the Ph.D. degree with the Department of Micro-electronics and Nanoelectronics, Tsinghua University, Beijing, China. She undertakes research work on 5G massive MIMO detection and quantum-assisted signal processing from National Mobile Communications Research Laboratory, Southeast University. Her current research interests include magnetoelectric antennas, piezoelectric antennas, and their applications in largescale antenna arrays and wireless communication systems. She was the recipient of the Outstanding Undergraduate Award from Southeast University.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=326&width=263&top_left_y=1400&top_left_x=141)

Yifei Shen (Student Member, IEEE) was born in 1997. He received the B.S. degree in 2016 from Chien-Shiung Wu College (Honors College), Southeast University, Nanjing, China. He received the M.S. degree in 2018 from the School of Information Science and Engineering, Southeast University, where he is currently working toward the Ph.D. degree. His research interests include error-correction codes, VLSI design for digital signal processing, and synthetic biology.

He was the recipient of the Best Student Paper Award at the 2016 IEEE International Conference on Digital Signal Processing and the 2020 IEEE Circuits and Systems Society Pre-Doctoral Scholarship Award.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=321&width=261&top_left_y=1899&top_left_x=141)

Wenqing Song (Student Member, IEEE) was born in 2000. She received the B.S. degree from ChienShiung Wu College (Honors College), Southeast University, Nanjing, China, in 2017. She is currently working toward the Ph.D. degree with the School of Electronic Science and Engineering, Nanjing University, Nanjing, China. Her current research interests include error-correction codes, reconfigurable computing, and efficient VLSI design.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=321&width=261&top_left_y=2273&top_left_x=141)

Muhao Li (Student Member, IEEE) was born in 1997. He received the B.E. degree in 2019 from the School of Information Science and Engineering, Southeast University, Nanjing, China, where he is currently working toward the Ph.D degree in information and communication engineering with National Mobile Communications Research Laboratory. His research focuses on VLSI design for digital signal processing.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=316&width=256&top_left_y=232&top_left_x=1057)

Xiaohu You (Fellow, IEEE) received the B.S., M.S., and Ph.D. degrees in electrical engineering from the Nanjing Institute of Technology, Nanjing, China, in 1982, 1985, and 1989, respectively. From 1987 to 1989, he was a Lecturer with the Nanjing Institute of Technology. Since 1990, he has been with Southeast University, first as an Associate Professor and then as a Professor. He was the Premier Foundation Investigator of China National Science Foundation. From 1999 to 2002, he was the Principal Expert of the C3G Project, responsible for organizing China's 3G mobile communications research and development activities. From 2001 to 2006, he was the Principal Expert of the National 863 FuTURE Project. His research interests include mobile communications, adaptive signal processing, artificial neural networks with applications to communications, and biomedical engineering. He is currently the Chairman of the IEEE Nanjing Section. He was selected as IEEE Fellow in 2012 for his contributions to the development of mobile communications in China. He was the recipient of the Excellent Paper Award from the China Institute of Communications in 1987 and the Elite Outstanding Young Teacher Award from Southeast University in 1990, 1991, and 1993.
![](https://cdn.mathpix.com/cropped/c4c2437b-39bf-451f-95b4-2a539e1511e0-16.jpg?height=323&width=259&top_left_y=1100&top_left_x=1054)

Chuan Zhang (Senior Member, IEEE) received the B.E. degree in microelectronics and the M.E. degree in very-large scale integration design from Nanjing University, Nanjing, China, in 2006 and 2009, respectively, and the M.S.E.E. and Ph.D. degrees from the Department of Electrical and Computer Engineering, University of Minnesota Twin Cities (UMN), Minneapolis, MN, USA, in 2012.

He is currently an Excellence Professor and the Purple Mountain Professor with Southeast University, Nanjing, China. He is also with the LEADS, National Mobile Communications Research Laboratory, Quantum Information Center, Southeast University, and the Purple Mountain Laboratories, Nanjing, China. His current research interests include low-power high-speed VLSI design for digital signal processing and digital communication, biochemical computation and neuromorphic engineering, and quantum communication.

He is currently an Associate Editor for the IEEE Transactions on Signal Processing and IEEE Open Journal of Circuits and Systems, and the Corresponding Guest Editor of the IEEE Journal on Emerging and Selected Topics in Circuits and Systems twice. He is also a Member of the Seasonal School of Signal Processing and Design and Implementation of Signal Processing Systems TC of the IEEE Signal Processing Society, and Circuits and Systems for Communications TC, VLSI Systems and Applications TC, and Digital Signal Processing TC of the IEEE Circuits and Systems Society. He was the recipient of the Best Contribution Award of the IEEE Asia Pacific Conference on Circuits and Systems (APCCAS) in 2018, the Three Best Student Paper Awards of the IEEE International Conference on ASIC in 2015, 2017, and 2019, the Best Paper Award Nomination of the IEEE Workshop on Signal Processing Systems in 2015, the Three Excellent Paper Awards and two Excellent Poster Presentation Awards of the International Collaboration Symposium on Information Production and Systems from 2016 to 2018, the Outstanding Achievement Award of the Intel Collaborative Research Institute in 2018, the Merit Student Paper Award of the IEEE APCCAS in 2008, and the Three-Year University-Wide Graduate School Fellowship of UMN and the Doctoral Dissertation Fellowship of UMN.


[^0]:    ${ }^{1}$ The number of complex-valued addition is less than the number of complexvalued multiplication [23]
    ${ }^{2}$ The derivation process is shown in Appendix B

[^1]:    ${ }^{3}$ We regard $k_{\mathrm{F}}=k_{\mathrm{N}}=3$ as $k=3$, because the computational complexity of TL-BD-INSA with $k_{\mathrm{F}}=k_{\mathrm{N}}=3$ is $M^{3}+2 M m_{\mathrm{UE}}^{2}$ (See Table II).

[^2]:    ${ }^{4}$ Please refer to Appendix C for the proof that $\mathbf{W}^{-1}(L)$ is Hermitian.

