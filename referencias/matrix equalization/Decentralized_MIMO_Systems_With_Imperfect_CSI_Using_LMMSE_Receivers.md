# Decentralized MIMO Systems With Imperfect CSI Using LMMSE Receivers 

Zeyan Zhuang $\left.{ }^{( }\right)$, Graduate Student Member, IEEE, Xin Zhang $\left.{ }^{( }\right)$, Member, IEEE, Dongfang Xu $\left.{ }^{( }\right)$, Member, IEEE, Shenghui Song ${ }^{(1)}$, Senior Member, IEEE, and Yonina C. Eldar ${ }^{(1)}$, Fellow, IEEE


#### Abstract

Centralized baseband processing (CBP) is required to achieve the full potential of massive multiple-input multiple-output (MIMO) systems. However, due to the large number of antennas, CBP suffers from two major issues: 1) Extensive data interconnection between radio frequency (RF) circuitry and the central processing unit; and 2) high-dimensional computation. To this end, decentralized baseband processing (DBP) has been proposed, where the antennas at the base station are partitioned into clusters connected to separate RF circuits and equipped with separate computing units. However, the optimal fusion scheme that maximizes signal-to-interference-and-noise ratio (SINR) and the related performance analysis for DBP with general spatial correlation and imperfect channel state information (CSI) have not been studied. In this paper, we consider a decentralized MIMO system where all clusters adopt linear minimum mean-square error (LMMSE) receivers. We first establish an optimal linear fusion scheme that has high computational and data input/output costs. To reduce the cost, we then propose two suboptimal fusion schemes with reduced complexity. For all three schemes, we study the SINR performance by leveraging random matrix theory and demonstrate conditions under which the suboptimal schemes are optimal. Furthermore, we determine the optimal regularization parameter for the LMMSE receiver, identify the best antenna partitioning strategy, and prove that the SINR will decrease as the number of clusters increases. Numerical simulations validate the accuracy of the theoretical results.


Index Terms-Decentralized baseband processing (DBP), linear minimum mean-square error (LMMSE), massive multiple-input-multiple-output (MIMO), random matrix theory (RMT).

## I. Introduction

MASSIVE multi-input-multi-output (MIMO) technology has been shown very effective in achieving high spectral

Received 15 August 2024; revised 6 December 2024; accepted 20 January 2025. Date of publication 10 February 2025; date of current version 5 May 2025. This work was supported in part by the NSFC/RGC Joint Research Scheme through the Research Grants Council of the Hong Kong Special Administrative Region, China and National Natural Science Foundation of China under Project N_HKUST656/22 and in part by General Research Fund through Hong Kong Research Grants Council under Project 16209524. The guest editor coordinating the review of this article and approving it for publication was Prof. Xiao Li . (Corresponding author: Shenghui Song.)

Zeyan Zhuang, Xin Zhang, and Shenghui Song are with the Department of Electronic and Computer Engineering, The Hong Kong University of Science and Technology, Hong Kong, Hong Kong (e-mail: zzhuangac @ connect.ust.hk; eezhangxin@ust.hk; eeshsong@ust.hk).

Dongfang Xu is with the Division of Integrative Systems and Design, The Hong Kong University of Science and Technology, Hong Kong, Hong Kong (e-mail: eedxu@ust.hk).

Yonina C. Eldar is with the Department of Mathematics and Computer Science, The Weizmann Institute of Science, Rehovot 7610001, Israel (e-mail: yonina.eldar@weizmann.ac.il).

Digital Object Identifier 10.1109/JSTSP.2025.3539098
efficiency, energy efficiency, and link reliability [1]. However, conventional implementations require centralized baseband processing (CBP) where all baseband data are collected and processed by a centralized baseband processing unit (BBU) [2], [3]. Such centralized processing causes significant challenges when the size of the antenna arrays becomes extremely large. On the one hand, transmitting baseband data from a large number of base station (BS) antennas to the BBU results in very high throughput demands. On the other hand, traditional estimation or beamforming algorithms require the inversion of high-dimensional matrices, which causes heightened computational complexity. These challenges make CBP very difficult to implement in practice [4], [5].

To address the bandwidth and computation bottlenecks of CBP, a more efficient architecture called decentralized baseband processing (DBP) was recently proposed [2], [4], [6], [7], [8], [9], [10]. With DBP, BS antennas are divided into several clusters, each equipped with its own processing unit that performs signal processing tasks in a parallel and decentralized manner. Li et al. [4], [6] developed iterative decentralized algorithms to minimize the mean-squared error (MSE) of the received symbols. A gradient descent based decentralized algorithm was proposed in [7] to obtain zero-forcing (ZF) equalization for a daisy chain architecture. In [2], [11], the feedforward DBP architecture was proposed to reduce latency by avoiding the information exchange between clusters required by previous works [12].

With the feedforward structure, the estimates from all clusters and some middle-stage information are transferred to and fused at the central unit (CU). As a result, the fusion algorithm at the CU is crucial for successful estimation. In [2], Jeon et al. provided an optimal linear fusion that maximizes the signal-to-interference-and-noise ratio (SINR) in uncorrelated Rayleigh channels with perfect channel state information (CSI). Closedform deterministic approximations of the SINR for maximum ratio combining (MRC), ZF, and linear minimum mean-square error (LMMSE) receivers were also derived. The design of the fusion coefficients for decentralized MIMO systems resembles that of the collaboration among access points (APs) in cell-free massive MIMO (CF-mMIMO) systems, where distributed APs are deployed and linked to a central processing unit (CPU) [13]. The difference between DBP and CF-mMIMO lies in the spatial correlation among different clusters, which makes the DBP architecture more general. In [14], four levels of cooperation with minimum mean-square error (MMSE) receiver were
proposed for CF-mMIMO systems, considering imperfect CSI and spatially correlated fading. However, the fusion scheme and performance analysis for DBP with imperfect CSI and general spatial correlation have not been studied.

In this paper, we consider feedforward decentralized massive MIMO systems with LMMSE receivers due to their near-optimal performance and ease of implementation [12]. We also consider the case with imperfect CSI, where the channel estimation (CE) errors are assumed to follow Gaussian distributions [14], [15], due to the difficulty in obtaining perfect CSI in massive MIMO systems [16], [17]. Specifically, we first determine the optimal linear fusion that maximizes the SINR, which requires global CSI and has high complexity. To reduce the cost, we propose two linear fusion schemes with reduced computation and communication workloads. In particular, the first approach utilizes a moderate amount of intermediate results computed by the clusters, while the second method can be implemented by a fully decentralized (FD) architecture [2], where the CU only needs to calculate the weighted sum of the local estimates, without requiring any other intermediate results.

Unfortunately, the presence of CE errors and the decentralized structure make it very challenging to evaluate the receive SINR. To this end, we adopt large random matrix theory (RMT) to tackle the random vector channels, which has been proven effective in analyzing the fundamental limits of centralized LMMSE receivers [18], [19]. The SINR analysis for the DBP architecture has been considered in [2] utilizing RMT. However, they assumed perfect CSI and uncorrelated Rayleigh channel, while here we consider the more general case of imperfect CSI and general spatial correlation. Based on the analysis results, we further investigate the impacts of several key system parameters, including the regularization parameter, the antenna partitioning strategy, and the number of clusters.

The main contributions can be summarized as follows:

1) For decentralized massive MIMO systems, we first derive the optimal linear fusion scheme to maximize the SINR with imperfect CSI and demonstrate that the optimal coefficients for the fusion scheme also minimize the MSE for estimating the transmit signal. We then propose two suboptimal fusion schemes assuming local CSI, which have reduced levels of complexity.
2) We derive the deterministic approximations of the SINR for all three fusion schemes using RMT. The analysis results reveal that, without spatial correlation between clusters or CE errors, the first suboptimal fusion scheme achieves the optimal SINR. The second suboptimal fusion scheme, which has lower complexity, can achieve the optimal SINR when there is no spatial correlation between clusters.
3) Based on the theoretical analysis, we investigate the scenario with heterogeneous CSI inaccuracy among clusters. The results show that when the CSI error is high for certain clusters, the system's performance is asymptotically equal to that without considering those clusters.
4) To obtain more physical insights, we derive closed-form expressions for the SINR over independent and identically distributed (i.i.d.) channels. Based on the results, we
further determine the optimal regularization parameters and optimal antenna partition strategies that maximize SINR, and evaluate the impact of the number of clusters.
5) From the RMT perspective, we derive the deterministic approximations for linear functions of the resolvent where the covariance matrices have generally correlated columns, and demonstrate the convergence rates of the means are $\mathcal{O}\left(N^{-\frac{1}{2}}\right)$. These findings can be applied to the analysis of regularized zero-forcing (RZF) precoding in downlink MIMO systems [20].
The rest of the paper is organized as follows. In Section II, we introduce the system model and the DBP architecture. In Section III, we derive the optimal linear fusion scheme that maximizes the SINR and propose two linear fusion schemes for decentralized implementation. In Section IV, we derive deterministic approximations for the SINR of proposed fusion schemes and investigate the results with i.i.d. channels. Numerical results are given in Sections V and VI concludes the paper.

Notations: Throughout the paper, lowercase and uppercase boldface letters represent vectors and matrices, respectively. We use $\mathbb{C}^{N}$ and $\mathbb{C}^{N \times M}$ to denote the space of $N$-dimensional complex vectors and the space of $N$-by- $M$ complex matrices, respectively. The conjugate transpose and transpose operator are denoted by $(\cdot)^{H}$ and $(\cdot)^{T}$, respectively, $[\mathbf{A}]_{i, j}$ and $[\mathbf{a}]_{i}$ represent the $(i, j)$-th entry of matrix $\mathbf{A}$ and $i$-th element of $\mathbf{a}$, respectively. For integer vectors $\boldsymbol{\tau}=\left[\tau_{1}, \ldots, \tau_{N_{1}}\right]^{T}$ and $\boldsymbol{\beta}=\left[\beta_{1}, \ldots, \beta_{N_{2}}\right]^{T}$, we use notations $\mathbf{A}[\boldsymbol{\tau}, \boldsymbol{\beta}]$ and $\mathbf{A}[\boldsymbol{\tau},:]$ to denote the submatrices of $\mathbf{A}$ with $[\mathbf{A}[\boldsymbol{\tau}, \boldsymbol{\beta}]]_{i, j}=[\mathbf{A}]_{\tau_{i}, \beta_{j}}$ and $[\mathbf{A}[\boldsymbol{\tau},:]]_{i, j}=[\mathbf{A}]_{\tau_{i}, j}$, respectively. We write $\|\cdot\|$ for the spectral norm of a matrix or the Euclidean norm of a vector, $\operatorname{Tr} \mathbf{A}$ refers to the trace of $\mathbf{A}, \mathbf{I}_{N}$ represents the identity matrix of size $N$, and $\mathbf{1}_{N}$ denotes the vector with all 1 entries of size $N$. The probability measure and the expectation operator are denoted by $\mathbb{P}[\cdot]$ and $\mathbb{E}[\cdot]$, respectively, $\underline{x}=x-\mathbb{E} x$ denotes the centered form of random variable $x$, and $\xrightarrow{\text { a.s. }}$ indicates almost sure convergence. We use $\frac{\partial(\cdot)}{\partial x}$ to represent the partial derivative. The notations $[N]$ and $[N]_{0}$ represent the set $\{1,2, \ldots, N\}$ and $\{0\} \cup[N]$, respectively. The indicator function is represented by $\mathbb{I}_{\{\cdot\}}$, and $\mathcal{O}(\cdot)$ is the standard Big-O notation. Specifically, we have $f(N)=\mathcal{O}(g(N))$ if and only if there exists a positive real number $C$ and positive integer $N_{0}$ such that $|f(N)| \leq C g(N)$ for all $N \geq N_{0}$.

## II. System Model

## A. Signal Model

Consider an uplink MIMO system where $M+1$ singleantenna users transmit signals to one BS with $N$ antennas. We denote the transmit signal of all users as $\mathbf{x}=\left[x_{0}, \ldots, x_{M}\right]^{T} \sim \mathcal{C} \mathcal{N}\left(0, \mathbf{I}_{M+1}\right)$, where $x_{j}$ represents the signal of user $j$. The channel between user $j$ and the BS is denoted by $\mathbf{h}_{j} \in \mathbb{C}^{N}$. Thus, the received signal at the BS is given by

$$
\begin{equation*}
\mathbf{y}=\boldsymbol{\Sigma} \mathbf{x}+\mathbf{n}, \tag{1}
\end{equation*}
$$

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-03.jpg?height=630&width=800&top_left_y=223&top_left_x=165)
Fig. 1. The feedforward DBP architecture for massive MIMO uplink.

where $\mathbf{y} \in \mathbb{C}^{N}, \boldsymbol{\Sigma}=\left[\mathbf{h}_{0}, \ldots, \mathbf{h}_{M}\right] \in \mathbb{C}^{N \times(M+1)}$, and $\mathbf{n} \sim \mathcal{C} \mathcal{N}\left(0, \sigma^{2} \mathbf{I}_{N}\right)$ denotes the additive Gaussian white noise (AWGN) at the BS.

Decentralized Architecture: In this paper, we consider the decentralized architecture [2], [4] as shown in Fig. 1, where the $N$ antennas of the BS are divided into $K$ clusters, connected to one CU. The $k$-th cluster consists of $N_{k}$ antennas, and each cluster contains its own RF components and computing unit. For simplicity, we partition the received signal $\mathbf{y}=\left[\mathbf{y}_{1}^{T}, \ldots, \mathbf{y}_{K}^{T}\right]^{T}$, the channel matrix $\boldsymbol{\Sigma}=\left[\boldsymbol{\Sigma}_{1}^{T}, \ldots, \boldsymbol{\Sigma}_{K}^{T}\right]^{T}$, the channel vector $\mathbf{h}_{j}=\left[\mathbf{h}_{j 1}^{T}, \ldots, \mathbf{h}_{j K}^{T}\right]^{T}, j \in[M]_{0}$, and the noise vector $\mathbf{n}=\left[\mathbf{n}_{1}^{T}, \ldots, \mathbf{n}_{K}^{T}\right]^{T}$, such that the received signal at the $k$-th cluster is given by

$$
\begin{equation*}
\mathbf{y}_{k}=\boldsymbol{\Sigma}_{k} \mathbf{x}+\mathbf{n}_{k}, k \in[K], \tag{2}
\end{equation*}
$$

with $\mathbf{y}_{k} \in \mathbb{C}^{N_{k}}, \boldsymbol{\Sigma}_{k} \in \mathbb{C}^{N_{k} \times(M+1)}$, and $\mathbf{n}_{k} \in \mathbb{C}^{N_{k}}$. To estimate the signal from user $j$, the $k$-th cluster independently processes the baseband signal to compute the estimate $\widehat{x}_{j k}$. The local estimate $\widehat{x}_{j k}$ and a moderate amount of intermediate results are then transferred to the CU. These intermediate results are designed based on the estimation scheme and typically include the Gram matrices of the channels [21], [22] or variances of the estimation errors [2]. The CU will obtain the final estimate $\widehat{x}_{j}$ through linear fusion as

$$
\begin{equation*}
\widehat{x}_{j}=\sum_{k=1}^{K} \alpha_{k} \widehat{x}_{j k}, \tag{3}
\end{equation*}
$$

where $\alpha_{k}$ represents the fusion coefficient that can be chosen as constant or determined based on the information from clusters. To estimate $x_{j}$, LMMSE estimation is widely used in conventional CBP due to its simplicity in implementation and near-optimal performance [12]. Therefore, we consider the case where all clusters adopt LMMSE estimator and the detailed design for the fusion coefficients $\alpha_{k}, k \in[K]$ will be discussed in Section III.

## B. Channel Model

Due to limited angular spread and insufficient antenna spacing, spatial correlation between BS antennas is inevitable. In this paper, we consider the Rayleigh channel model [15], [23]

$$
\begin{equation*}
\mathbf{h}_{j}=\mathbf{R}_{j}^{\frac{1}{2}} \mathbf{z}_{j}, j \in[M]_{0}, \tag{4}
\end{equation*}
$$

where $\mathbf{R}_{j} \in \mathbb{C}^{N \times N}$ is a nonnegative definite matrix that models the spatial correlation of the BS antennas with respect to (w.r.t.) user $j$ and $\mathbf{z}_{j} \sim \mathcal{C} \mathcal{N}\left(0, \mathbf{I}_{N}\right)$. Note that this model takes the variance profile model [18], [24] as a special case. With DBP, each cluster can only know its local spatial correlation matrix, which is a principal sub matrix of $\mathbf{R}_{j}$. To this end, we denote the index vector

$$
\begin{equation*}
\varsigma_{k}=\left[\sum_{i=1}^{k-1} N_{i}+1, \sum_{i=1}^{k-1} N_{i}+2, \ldots, \sum_{i=1}^{k} N_{i}\right]^{T}, k \in[K], \tag{5}
\end{equation*}
$$

and for a $N$-by- $N$ matrix $\mathbf{R}$, we define

$$
\begin{equation*}
[\mathbf{R}]_{[k, l]}=\mathbf{R}\left[\varsigma_{k}, \varsigma_{l}\right] . \tag{6}
\end{equation*}
$$

As a result, the spatial correlation matrix $\mathbf{R}_{j}$ can be expressed in the following block matrix form

$$
\mathbf{R}_{j}=\left[\begin{array}{cccc}
{\left[\mathbf{R}_{j}\right]_{[1,1]}} & {\left[\mathbf{R}_{j}\right]_{[1,2]}} & \cdots & {\left[\mathbf{R}_{j}\right]_{[1, K]}}  \tag{7}\\
{\left[\mathbf{R}_{j}\right]_{[2,1]}} & {\left[\mathbf{R}_{j}\right]_{[2,2]}} & \cdots & {\left[\mathbf{R}_{j}\right]_{[2, K]}} \\
\vdots & \vdots & \ddots & \vdots \\
{\left[\mathbf{R}_{j}\right]_{[K, 1]}} & {\left[\mathbf{R}_{j}\right]_{[K, 2]}} & \cdots & {\left[\mathbf{R}_{j}\right]_{[K, K]}}
\end{array}\right],
$$

where the off-diagonal block $\left[\mathbf{R}_{j}\right]_{[k, l]}$ denotes the spatial correlation between the $k$-th and the $l$-th clusters for $k \neq l$, and the main-diagonal block $\left[\mathbf{R}_{j}\right]_{[k, k]}$ represents the spatial correlation within the $k$-th cluster.

Decentralized Channel Estimation: For simplicity, we assume $M+1$ mutually orthogonal pilot signals $\phi_{j} \in \mathbb{C}^{\tau}, j \in[M]_{0}$ with $\left\|\boldsymbol{\phi}_{j}\right\|^{2}=\tau(\tau \geq M+1)$. During the training phase, the received signal $\widetilde{\mathbf{Y}}_{k} \in \mathbb{C}^{N_{k} \times \tau}$ at the $k$-th cluster is given by

$$
\begin{equation*}
\tilde{\mathbf{Y}}_{k}=\sum_{i=0}^{M} \mathbf{h}_{i k} \boldsymbol{\phi}_{i}^{T}+\tilde{\mathbf{N}}_{k}, \tag{8}
\end{equation*}
$$

where $\widetilde{\mathbf{N}}_{k} \in \mathbb{C}^{N_{k} \times \tau}$ represents the noise matrix with i.i.d. entries, each following $\mathcal{C} \mathcal{N}\left(0, \sigma_{\mathrm{tr}, k}^{2}\right)$. To estimate $\mathbf{h}_{j k}$, the $k$-th cluster will first correlate the training signal with the scaled pilot $\widetilde{\mathbf{y}}_{j k}=\widetilde{\mathbf{Y}}_{k} \frac{\phi_{j}^{*}}{\tau}$, which yields

$$
\begin{equation*}
\tilde{\mathbf{y}}_{j k}=\left(\sum_{i=0}^{M} \mathbf{h}_{i k} \phi_{i}^{T}+\tilde{\mathbf{N}}_{k}\right) \frac{\phi_{j}^{*}}{\tau}=\mathbf{h}_{j k}+\tilde{\mathbf{n}}_{j k}, \tag{9}
\end{equation*}
$$

where $\widetilde{\mathbf{n}}_{j k} \sim \mathcal{C} \mathcal{N}\left(0, \frac{\sigma_{\mathrm{tr}, \mathrm{k}}^{2}}{\tau}\right)$. Denote the power of the resulting noise as $\widetilde{\sigma}_{k}^{2}=\frac{\sigma_{\mathrm{tr}, \mathrm{k}}^{2}}{\tau}$. Thus, the training signal-to-noise ratio (SNR) is $\frac{1}{\widetilde{\sigma}_{k}^{2}}$, which is assumed to be known at each cluster. Under such circumstances, the MMSE estimate $\widehat{\mathbf{h}}_{j k}$ of $\mathbf{h}_{j k}$ is given by [25, Theorem 3.1]

$$
\begin{equation*}
\widehat{\mathbf{h}}_{j k}=\left[\mathbf{R}_{j}\right]_{[k, k]}\left(\left[\mathbf{R}_{j}\right]_{[k, k]}+\widetilde{\sigma}_{k}^{2} \mathbf{I}_{N_{k}}\right)^{-1} \widetilde{\mathbf{y}}_{j k} . \tag{10}
\end{equation*}
$$

Stacking the channel estimate of all clusters as $\widehat{\mathbf{h}}_{j}= \left[\widehat{\mathbf{h}}_{j 1}^{T}, \ldots, \widehat{\mathbf{h}}_{j K}^{T}\right]^{T}$, the distribution of the channel vector can be expressed as

$$
\begin{align*}
\widehat{\mathbf{h}}_{j} & \sim \mathcal{C N}\left(\mathbf{0}, \Phi_{j}\right) \\
\mathbf{h}_{j} \mid \widehat{\mathbf{h}}_{j} & \sim \mathcal{C N}\left(\widetilde{\mathbf{h}}_{j}, \mathbf{W}_{j}\right) \tag{11}
\end{align*}
$$

where the distribution of $\widehat{\mathbf{h}}_{j}$ is derived from the zero mean channel (4) and zero mean training noise (8), using the properties of the linear transformations of Gaussian distributions [26, Section III]. Here, $\mathbf{W}_{j}$ represents the covariance matrix of the CE error and the posterior mean is given by $\widetilde{\mathbf{h}}_{j}=\mathbf{V}_{j} \widehat{\mathbf{h}}_{j}$, by the properties of conditional Gaussian distributions [26, Section IV]. Matrices $\boldsymbol{\Phi}_{j}, \mathbf{V}_{j}$, and $\mathbf{W}_{j}$ are defined as

$$
\begin{align*}
\mathbf{\Phi}_{j} & =\mathbf{D}_{T, j}\left(\mathbf{D}_{\widetilde{\sigma}}+\mathbf{R}_{j}\right) \mathbf{D}_{T, j} \\
\mathbf{V}_{j} & =\mathbf{T}_{j} \mathbf{D}_{T, j}^{-1}, \mathbf{W}_{j}=\mathbf{T}_{j} \mathbf{D}_{\widetilde{\sigma}} \tag{12}
\end{align*}
$$

where $\mathbf{D}_{\widetilde{\sigma}}=\operatorname{diag}\left(\widetilde{\sigma}_{k}^{2} \mathbf{I}_{N_{k}} ; k \in[K]\right), \mathbf{T}_{j}=\mathbf{R}_{j}\left(\mathbf{D}_{\widetilde{\sigma}}+\mathbf{R}_{j}\right)^{-1}$, $\mathbf{D}_{R, j}=\operatorname{diag}\left(\left[\mathbf{R}_{j}\right]_{[k, k]} ; k \in[K]\right), \quad$ and $\quad \mathbf{D}_{T, j}=\mathbf{D}_{R, j}\left(\mathbf{D}_{\widetilde{\sigma}}+\right. \left.\mathbf{D}_{R, j}\right)^{-1}$. When the spatial correlation between antennas of different clusters is negligible, i.e., the off-diagonal block $\left[\mathbf{R}_{j}\right]_{[k, l]}=\mathbf{0}_{N_{k} \times N_{l}}$ for $k \neq l$, it can be verified that $\mathbf{R}_{j}=\mathbf{D}_{R, j}, \mathbf{V}_{j}=\mathbf{I}_{N}$, and $\widehat{\mathbf{h}}_{j}$ is the same as that estimated by the centralized MMSE estimator. Therefore, $\mathbf{V}_{j}$ indicates the effect of decentralized CE . For ease of notation, we define the channel matrices $\widehat{\boldsymbol{\Sigma}}=\left[\widehat{\mathbf{h}}_{0}, \ldots, \widehat{\mathbf{h}}_{M}\right]$, $\widehat{\boldsymbol{\Sigma}}_{k}=\left[\widehat{\mathbf{h}}_{0 k}, \ldots, \widehat{\mathbf{h}}_{M k}\right], \widetilde{\boldsymbol{\Sigma}}=\left[\widetilde{\mathbf{h}}_{0}, \ldots, \widetilde{\mathbf{h}}_{M}\right]$, and the sum of the covariance $\mathbf{W}=\sum_{j \in[M]_{0}} \mathbf{W}_{j}$.

## C. SINR

Without loss of generality, we consider the estiomation of $x_{0}$ using linear reveiver at each cluster. Specifically, the $k$-th cluster will estimate $\widehat{x}_{0 k}=\mathbf{r}_{k}^{H} \mathbf{y}_{k}$, where $\mathbf{r}_{k}= \mathbf{r}_{k}\left(\widehat{\boldsymbol{\Sigma}}_{k},\left\{\left[\mathbf{R}_{j}\right]_{[k, k]}\right\}_{j=0}^{M}, \widetilde{\sigma}_{k}^{2}\right)$ depends on the local CSI of the $k$-th cluster. With the linear fusion in (3), the achievable rate of user 0 can be bounded by a standard lower bound $R_{0}=\log \left(1+\gamma_{0}\right)$ based on the worst-case uncorrelated additive noise [27]. Here, $\gamma_{0}$ is the associated SINR given by

$$
\begin{equation*}
\gamma_{0}=\frac{\left|\mathbb{E}_{\mathbf{h}_{0} \mid \widehat{\mathbf{h}}_{0}}\left[\mathbf{r}_{\alpha}^{H} \mathbf{h}_{0}\right]\right|^{2}}{\mathbb{E}_{\boldsymbol{\Sigma} \mid \widehat{\boldsymbol{\Sigma}, \mathbf{x}, \mathbf{n}}}\left|\mathbf{r}_{\alpha}^{H}\left[\boldsymbol{\Sigma} \mathbf{x}-\widetilde{\mathbf{h}}_{0} x_{0}+\mathbf{n}\right]\right|^{2}}, \tag{13}
\end{equation*}
$$

with $\mathbf{r}_{\alpha}=\left[\alpha_{1}^{*} \cdot\left(\mathbf{r}_{1}\right)^{T}, \ldots, \alpha_{K}^{*} \cdot\left(\mathbf{r}_{K}\right)^{T}\right]^{T} \in \mathbb{C}^{N}$. In this paper, we will determine the optimal fusion coefficients $\alpha_{1}, \ldots, \alpha_{K}$ that can maximize the SINR $\gamma_{0}$ in (13) [2] and investigate the asymptotic characterization of $\gamma_{0}$.

## III. Decentralized LMMSE Receiver and Linear Fusion

In this section, we first introduce the decentralized LMMSE receiver, and derive the optimal linear fusion scheme which requires global CSI and has high complexity. Then, we propose two linear fusion schemes, which only require local CSI and have reduced complexity.

## A. Decentralized LMMSE Receiver

With perfect CSI, the local MSE of the estimate $\widehat{x}_{0 k}=\mathbf{r}_{k}^{H} \mathbf{y}_{k}$ is given by

$$
\begin{equation*}
\operatorname{MSE}_{k}=\mathbb{E}_{\mathbf{x}, \mathbf{n}}\left|\widehat{x}_{0 k}-x_{0}\right|^{2}, \tag{14}
\end{equation*}
$$

where the expectation is w.r.t. the transmit signal and the AWGN. However, to obtain the linear receiver that minimizes the local MSE with imperfect CSI, the expectation should be performed over $\boldsymbol{\Sigma}_{k} \mid \widehat{\boldsymbol{\Sigma}}_{k}{ }^{1}$ [28, Eq. (6)], which yields

$$
\begin{equation*}
\left.\operatorname{MSE}_{k}\right|_{\widehat{\boldsymbol{\Sigma}}_{k}}=\mathbb{E}_{\boldsymbol{\Sigma}_{k} \mid \widehat{\boldsymbol{\Sigma}}_{k}, \mathbf{x}, \mathbf{n}}\left|\widehat{x}_{0 k}-x_{0}\right|^{2} \tag{15}
\end{equation*}
$$

Hence, the optimal $\mathbf{r}_{k}$ that minimizes $\left.\operatorname{MSE}_{k}\right|_{\widehat{\boldsymbol{\Sigma}}_{k}}$ is given by [28, Proposition 1]

$$
\begin{equation*}
\mathbf{r}_{k}^{\mathrm{mmse}}=\left(\widehat{\boldsymbol{\Sigma}}_{k} \widehat{\boldsymbol{\Sigma}}_{k}^{H}+N_{k} \mathbf{Z}_{k}+N_{k} \rho_{k} \mathbf{I}_{N_{k}}\right)^{-1} \widehat{\mathbf{h}}_{0 k}, \tag{16}
\end{equation*}
$$

where $\rho_{k}=\frac{\sigma^{2}}{N_{k}}$ and

$$
\begin{equation*}
\mathbf{Z}_{k}=\frac{\widetilde{\sigma}_{k}^{2}}{N_{k}} \sum_{j=0}^{M}\left[\mathbf{R}_{j}\right]_{[k, k]}\left(\left[\mathbf{R}_{j}\right]_{[k, k]}+\widetilde{\sigma}_{k}^{2} \mathbf{I}_{N_{k}}\right)^{-1} \tag{17}
\end{equation*}
$$

Note that the above $\rho_{k}$ and $\mathbf{Z}_{k}$ minimize the local MSE, but may not be optimal after fusion. As a result, we treat $\rho_{k}$ and $\mathbf{Z}_{k}$ as design parameters that can be optimized and refer to $\rho_{k}$ as the regularization parameter in the subsequent.

## B. Linear Fusion With Optimal Coefficients

The following proposition provides the optimal linear fusion scheme that maximizes the SINR and demonstrates that it also minimizes the MSE for estimating the transmit signal.

Proposition 1: The optimal coefficients $\boldsymbol{\alpha}=\left[\alpha_{1}, \ldots, \alpha_{K}\right]$ for maximizing (13) are given by

$$
\begin{equation*}
\boldsymbol{\alpha}^{\mathrm{opt}}=c \widetilde{\mathbf{h}}_{0}^{H} \mathbf{D}_{r}\left(\mathbf{D}_{r}^{H}\left(\widetilde{\Sigma} \widetilde{\Sigma}^{H}+\mathbf{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{D}_{r}\right)^{-1} \tag{18}
\end{equation*}
$$

where $c \in \mathbb{C} \backslash\{0\}$ and $\mathbf{D}_{r}=\operatorname{diag}\left(\mathbf{r}_{k}^{\mathrm{mmse}} ; k \in[K]\right)$. When $c= 1, \boldsymbol{\alpha}^{\text {opt }}$ is also the optimal solution for the following MMSE problem

$$
\begin{equation*}
\underset{\boldsymbol{\alpha}}{\operatorname{minimize}} \operatorname{MSE}_{\widehat{\boldsymbol{\Sigma}}}=\mathbb{E}_{\boldsymbol{\Sigma} \mid \widehat{\boldsymbol{\Sigma}, \mathbf{x}, \mathbf{n}}}\left|\sum_{k=1}^{K} \alpha_{k} \widehat{x}_{0 k}-x_{0}\right|^{2} . \tag{19}
\end{equation*}
$$

Proof: The proof of Proposition 1 is given in Appendix B.
Remark 1: The optimality of $\boldsymbol{\alpha}^{\text {opt }}$ in Proposition 1 holds for any linear receivers, e.g., MRC, and LMMSE is a special case.

Remark 2: It can be verified that when $\boldsymbol{\alpha}=\boldsymbol{\alpha}^{\text {opt }}$ and $c=1$, we have $\left.\operatorname{MSE}\right|_{\widehat{\boldsymbol{\Sigma}}}=\left(1+\gamma_{0}\right)^{-1}=\frac{\partial \log \left(1+\gamma_{0}\right)}{\partial \gamma_{0}}$, which reveals the connection between mutual information and MSE. This relation can be generalized to the case with non-Gaussian signals [29].

Remark 3: Proposition 1 shows that the fusion coefficients that maximize the SINR are actually a scaled version of the parameters that minimize MSE.

[^0]TABLE I
Comparison for the Complexity of Different Estimation Schemes
| Scheme | I/O Throughput of Cluster $k$ | Computational Complexity of Cluster $k$ | Computational Complexity of the CU |
| :--- | :--- | :--- | :--- |
| Centralized LMMSE Local LMMSE \& LFOC Local LMMSE \& LFSC Local LMMSE \& LFCC | $\begin{gathered} N_{k} M+2 N_{k}+1 \\ M+4 \\ 1 \end{gathered}$ | $\begin{gathered} C_{\mathrm{L}}\left(N_{k}, M\right) \\ C_{\mathrm{L}}\left(N_{k}, M\right)+N_{k} M+2 N_{k}^{2}+2 N_{k} \\ C_{\mathrm{L}}\left(N_{k}, M\right) \end{gathered}$ | $\begin{gathered} C_{\mathrm{L}}(N, M) \\ N^{2} M+2 N^{2}+N M+2 N+K^{2} M+C_{\mathrm{F}}(K) \\ K^{2} M+C_{\mathrm{F}}(K) \\ K \end{gathered}$ |


We will refer to the fusion scheme in Proposition 1 as linear fusion with optimal coefficients (LFOC) in the following. Note that, due to the presence of spatial correlation between different clusters, one cluster cannot determine the off-diagonal elements of $\mathbf{R}_{j}-\mathbf{D}_{R, j}$ and the channel $\widetilde{\boldsymbol{\Sigma}}$ in the feedforward architecture. As a result, to obtain $\boldsymbol{\alpha}^{\text {opt }}$, the CU needs to know the global CSI, which leads to high input/output (I/O) and computational cost. To reduce the complexity, we proposed two suboptimal linear fusion schemes in the following.

## C. Linear Fusion With Suboptimal Coefficients

Based on (18), we can design the suboptimal fusion parameter as

$$
\begin{equation*}
\boldsymbol{\alpha}^{\text {s-opt }}=\widehat{\mathbf{h}}_{0}^{H} \mathbf{D}_{r}\left(\mathbf{D}_{r}^{H}\left(\widehat{\boldsymbol{\Sigma}} \widehat{\boldsymbol{\Sigma}}^{H}+\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{D}_{r}\right)^{-1} \tag{20}
\end{equation*}
$$

where $\mathbf{D}_{W}=\sum_{j \in[M]_{0}} \mathbf{D}_{T, j} \mathbf{D}_{\widetilde{\sigma}}$. In particular, the suboptimal solution first replaces $\widetilde{\Sigma}$ in (18) with the estimated channel $\widehat{\Sigma}$, and then adopts a block diagonal version of $\mathbf{W}$. These terms are all computed based on the local CSI and spatial correlations. In fact, we can write

$$
\begin{align*}
{[\widehat{\mathbf{M}}]_{k, l}=} & \left(\mathbf{r}_{k}^{\mathrm{mmse}}\right)^{H} \widehat{\boldsymbol{\Sigma}}_{k} \widehat{\boldsymbol{\Sigma}}_{l}^{H} \mathbf{r}_{l}^{\mathrm{mmse}} \\
& +\mathbb{I}_{\{k=l\}}\left(\mathbf{r}_{k}^{\mathrm{mmse}}\right)^{H}\left[\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right]_{[k, k]} \mathbf{r}_{k}^{\mathrm{mmse}}  \tag{21}\\
{[\widehat{\mathbf{m}}]_{k}=} & \left(\mathbf{r}_{k}^{\mathrm{mmse}}\right)^{H} \widehat{\mathbf{h}}_{0 k} \tag{22}
\end{align*}
$$

where $\widehat{\mathbf{M}}=\mathbf{D}_{r}^{H}\left(\widehat{\boldsymbol{\Sigma}} \widehat{\boldsymbol{\Sigma}}^{H}+\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{D}_{r}$ and $\widehat{\mathbf{m}}=\mathbf{D}_{r}^{H} \widehat{\mathbf{h}}_{0}$. Therefore, to obtain $\boldsymbol{\alpha}^{\text {s-opt }}$, the $k$-th cluster needs to compute and transfer the intermediate parameter set

$$
\begin{align*}
\mathcal{P}_{k}=\{ & \left(\mathbf{r}_{k}^{\mathrm{mmse}}\right)^{H} \widehat{\mathbf{h}}_{0 k},\left(\mathbf{r}_{k}^{\mathrm{mmse}}\right)^{H} \widehat{\boldsymbol{\Sigma}}_{k} \\
& \left.\left(\mathbf{r}_{k}^{\mathrm{mmse}}\right)^{H}\left[\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right]_{[k, k]} \mathbf{r}_{k}^{\mathrm{mmse}}\right\} \tag{23}
\end{align*}
$$

to the CU. Then the CU will use $\mathcal{P}_{1}, \ldots \mathcal{P}_{K}$ to determine $\widehat{\mathbf{M}}$ and $\widehat{\mathbf{m}}$ by (21) and (22), respectively, and compute $\boldsymbol{\alpha}^{\text {s-opt }}= \widehat{\mathbf{m}}^{H} \widehat{\mathbf{M}}^{-1}$. Finally, based on (3), $\widehat{x}_{0}$ could be obtained. We will refer to this scheme as linear fusion with suboptimal coefficients (LFSC) in the following. Note that the computation and I/O complexity of LFSC is manageable since each parameter in $\mathcal{P}_{k}$ is a vector or a scalar, and the detailed computational complexity is given in Table I. It can be observed that the overall complexity of LFSC is significantly reduced compared to CBP and LFOC.

## D. Linear Fusion With Constant Coefficients

Although LFSC has reduced complexity, it still requires to compute and transmit additional information to the CU. When
the number of clusters is very large, the computational complexity, memory requirements, and I/O cost may be very high. To further reduce the complexity, we provide a simple linear fusion scheme with constant coefficients $\alpha_{k}$. For example, we can take

$$
\begin{equation*}
\alpha_{k}=\frac{1}{K}, k \in[K], \tag{24}
\end{equation*}
$$

or more heuristically

$$
\begin{equation*}
\alpha_{k}=\frac{N_{k}}{N}, k \in[K] . \tag{25}
\end{equation*}
$$

We will refer to this scheme as linear fusion with constant coefficients (LFCC) in the following. The complexity of LFCC is also given in Table I which is much lower than that of LFSC. Note that LFCC can be implemented by the FD feedforward architecture [2], where each cluster only needs to take the weighted sum of local estimates and does not require any additional intermediate results or processing.

## E. Complexity Analysis

The complexities for the proposed schemes and centralized LMMSE, including I/O and computations are summarized in Table I. We assume that under LFOC, the CU has access to global statistical CSI.

1) Computational Complexity: The computational complexity primarily arises from multiplication operations. For decentralized estimation, the $k$-th cluster calculates the channel covariance $\widehat{\boldsymbol{\Sigma}}_{k} \widehat{\boldsymbol{\Sigma}}_{k}^{H}$, which requires $N_{k}^{2}(M+1)$ multiplications. The matrix inversion and the equalization vector $\mathrm{r}_{k}^{\mathrm{mmse}}$ require $N_{k}^{3}$ and $N_{k}^{2}$ multiplications, respectively. Thus, the total computation complexity for the LMMSE estimate $\widehat{x}_{0 k}$ is

$$
\begin{equation*}
C_{\mathrm{L}}\left(N_{k}, M\right)=N_{k}^{2} M+N_{k}^{3}+2 N_{k}^{2}+N_{k} . \tag{26}
\end{equation*}
$$

For LFOC and LFCC, the $k$-th cluster only needs to compute the local estimate which requires $C_{\mathrm{L}}\left(N_{k}, M\right)$ multiplications. The computation of the parameter set $\mathcal{P}_{k}$ introduces extra $N_{k} M+2 N_{k}^{2}+2 N_{k}$ multiplications for LFSC. With LFOC, the CU computes the channel's posterior mean $\widetilde{\boldsymbol{\Sigma}}$ with $N^{2}(M+$ 1) multiplications and the fusion coefficients in (18) with $N^{2}+N M+2 N+K^{2} M+K^{3}+2 K^{2}$ multiplications. The fusion introduces $K$ multiplications, so the final computational complexity of the CU is given by $N^{2} M+2 N^{2}+N M+ 2 N+K^{2} M+C_{\mathrm{F}}(K)$ where $C_{\mathrm{F}}(K)=K^{3}+2 K^{2}+K$. For LFSC, the CU needs $K^{2} M+K^{3}+2 K^{2}$ multiplications to obtain $\boldsymbol{\alpha}^{\text {s-opt }}$ based on $\left\{\mathcal{P}_{k}\right\}_{k=1}^{K}$. Therefore, the overall complexity of obtaining the final estimate for the CU is $K^{2} M+C_{\mathrm{F}}(K)$. For LFCC, $K$ multiplications are used to fuse the local estimates.
2) I/O Throughput: For LFOC, the $k$-th cluster needs to transmit the $N_{k}$-by- $(M+1)$ matrix $\widehat{\boldsymbol{\Sigma}}_{k}$, the length- $N_{k}$ vector
$\mathbf{r}_{k}^{\mathrm{mmse}}$, and the local estimate $\widehat{x}_{0 k}$. LFSC requires $M+3$ complex scalars in $\mathcal{P}_{k}$, while LFCC only transmits the local estimate.

We note that in practice, $K$ is much smaller than $N$ and $M$, such that the complexity $C_{\mathrm{F}}(K)$ can be neglected. It can be observed that LFOC has high complexity at the CU. Furthermore, the CU requires global statistical CSI $\left\{\mathbf{R}_{j}\right\}_{j=0}^{M}$ for LFOC, resulting in a significant memory overhead. In contrast, LFSC reduces computational complexity at the CU. Overall, the complexity of LFCC is much lower than that of both LFSC and LFOC.

## IV. Asymptotic SINR Analysis

The expression for the SINR $\gamma_{0}$ in (59) contains the correlated terms between the channels $\widehat{\boldsymbol{\Sigma}}$ and $\widetilde{\boldsymbol{\Sigma}}$, making it very difficult to analyze. In this section, we will investigate the asymptotic behaviors of $\gamma_{0}$. Specifically, we will show that as the number of antennas and users tend to infinity at the same pace, $\gamma_{0}$ will converge almost surely. Then, we will derive the deterministic approximations for the SINR of the fusion schemes proposed in Section III. To achieve this, we require the following large-scale system assumptions.

Assumption A.1: For a given number of clusters $K$, we assume $0<\liminf _{N} \frac{N_{k}}{M} \leq \limsup _{N} \frac{N_{k}}{M}<+\infty$ for each $k \in[K]$.

Assumption A.2: Assume

$$
\begin{align*}
& \limsup _{N} \sup _{j \in[M]_{0}} \lambda_{\mathrm{M}}\left(\mathbf{R}_{j}\right)<+\infty,  \tag{27a}\\
& \liminf _{N} \inf _{j \in[M]_{0}} \lambda_{\mathrm{m}}\left(\mathbf{R}_{j}\right)>0, \tag{27b}
\end{align*}
$$

where $\lambda_{\mathrm{M}}\left(\mathbf{R}_{j}\right)$ and $\lambda_{\mathrm{m}}\left(\mathbf{R}_{j}\right)$ denote the largest and smallest eigenvalue of $\mathbf{R}_{j}$, respectively.

Assumption A.3: Assume $\rho_{k}>0$ and $\mathbf{Z}_{k}$ is Hermitian nonnegative such that $\limsup _{N} \sup _{k \in[K]}\left\|\mathbf{Z}_{k}\right\|<+\infty$ for each $k \in[K]$.
A. 1 implies that the number of antennas of the $k$-th cluster $N_{k}$ and the number of users $M$ approach infinity at the same pace [2]. For simplicity, we define $c_{k}=\frac{N_{k}}{M}$ and use $N \xrightarrow{c_{1}, \ldots, c_{K}} +\infty$ to indicate this asymptotic regime. According to interlacing inequalities [30], A. 2 ensures the eigenvalues of the local spatial correlation matrices $\left[\mathbf{R}_{j}\right]_{[k, k]}$ are bounded away from 0 , which makes $\mathbf{V}_{j}$ legal. A. 3 implies that the spectral norm of $\mathbf{Z}_{k}$ does not diverge to infinity. If A. 1 and A. 2 hold, (17) satisfies this assumption.

Let $\gamma^{\text {lfoc }}, \gamma^{\text {lfsc }}$, and $\gamma^{\text {lfcc }}$ denote the SINR with LFOC, LFSC, and LFCC, respectively. The following theorem provides the deterministic approximations for $\gamma^{\text {lfoc }}, \gamma^{\text {lfsc }}$, and $\gamma^{\text {lfcc }}$, respectively.

Theorem 1: When Assumptions A.1-A. 3 hold, the deterministic approximations for $\gamma^{\text {lfoc }}, \gamma^{\text {lfsc }}$, and $\gamma^{\text {lfcc }}$ are given by

$$
\begin{align*}
& \gamma^{\text {lfoc }} \xrightarrow[{N \xrightarrow{\text { a.s. }}}]{c_{1}, \ldots, c_{K}}+\infty  \tag{28a}\\
& \gamma^{\text {lfoc }}=\mathbf{v}^{H} \boldsymbol{\Delta}^{-1} \mathbf{v},  \tag{28b}\\
& \xrightarrow[{N \xrightarrow{c_{1}, \ldots, c_{K}}+} \infty]{\text { a.s. }} \bar{\gamma}^{\text {lfsc }}=\frac{\left(\mathbf{v}^{H} \boldsymbol{\Delta}_{I}{ }^{-1} \mathbf{v}\right)^{2}}{\mathbf{v}^{H} \boldsymbol{\Delta}_{I}{ }^{-1} \boldsymbol{\Delta} \boldsymbol{\Delta}_{I}{ }^{-1} \mathbf{v}},  \tag{28c}\\
& \gamma^{\text {lfcc }} \xrightarrow[{N \xrightarrow{\text { a.s. }}{ }^{\text {a }, \ldots, c_{K}}+} \infty]{ } \bar{\gamma}^{\text {lfcc }}=\frac{|\boldsymbol{\alpha} \mathbf{J} \mathbf{v}|^{2}}{\boldsymbol{\alpha} \mathbf{J} \boldsymbol{\Delta} \mathbf{J} \boldsymbol{\alpha}^{H}},
\end{align*}
$$

with

$$
\begin{align*}
{[\mathbf{v}]_{k}=} & \frac{\bar{\digamma}_{k}\left(\left[\mathbf{\Phi}_{0}\right]_{[k, k]}\right)}{N_{k}},  \tag{29a}\\
\mathbf{J}= & {\left[\mathbf{I}_{K}+\operatorname{diag}(\mathbf{v})\right]^{-1}, }  \tag{29b}\\
{[\boldsymbol{\Delta}]_{k, l}=} & \frac{\bar{\Upsilon}_{k l}\left(\left[\mathbf{\Phi}_{0}\right]_{[l, k]},\left[\mathbf{W}+\sigma^{2} \mathbf{I}_{N}\right]_{[k, l]}\right)}{N_{k} N_{l}} \\
& +\frac{\bar{\Pi}_{B, k l}\left(\left[\mathbf{\Phi}_{0}\right]_{[l, k]}\right)}{\sqrt{N_{k} N_{l}}},  \tag{29c}\\
{\left[\mathbf{\Delta}_{I}\right]_{k, l}=} & \frac{\bar{\Upsilon}_{k l}\left(\left[\mathbf{\Phi}_{0}\right]_{[l, k]},\left[\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right]_{[k, l]}\right)}{N_{k} N_{l}} \\
& +\frac{\bar{\Pi}_{k l}\left(\left[\mathbf{\Phi}_{0}\right]_{[l, k]}\right)}{\sqrt{N_{k} N_{l}}}, \tag{29d}
\end{align*}
$$

where functions $\bar{\digamma}_{k}, \bar{\Upsilon}_{k l}, \bar{\Pi}_{B, k l}$, and $\bar{\Pi}_{k l}$ can be obtained from Lemma 3 in Appendix A by setting $z_{i}=-\rho_{i}, \mathbf{S}_{i}=\mathbf{Z}_{i}, \mathbf{A}_{j}= \boldsymbol{\Phi}_{j}^{\frac{1}{2}}$, and $\mathbf{B}_{j}=\mathbf{V}_{j} \boldsymbol{\Phi}_{j}^{\frac{1}{2}}$ for each $i \in[K]$ and $j \in[M]$. Moreover, the following approximation for the mean holds

$$
\begin{equation*}
\mathbb{E}\left[\gamma^{\mathrm{fs}}\right]=\bar{\gamma}^{\mathrm{fs}}+\mathcal{O}\left(N^{-1}\right), \tag{30}
\end{equation*}
$$

where fs $\in\{$ lfoc, lfsc, lfcc $\}$.
Proof: The proof of Theorem 1 is given in Appendix C.
Remark 4: When $K=1$, which means there is only one cluster, $\bar{\gamma}^{\text {lfo }}, \bar{\gamma}^{\text {lfs }}$, and $\bar{\gamma}^{\text {lfc }}$ degenerate to the results with centralized LMMSE [18], [19].

Remark 5: Under certain conditions, the performance of LFSC approaches that of LFOC. In particular, when $\boldsymbol{\Delta}_{I}=\boldsymbol{\Delta}$, we have $\bar{\gamma}^{\text {lfoc }}=\bar{\gamma}^{\text {lfsc }}$. The above condition can be achieved when $\mathbf{V}_{j}=\mathbf{I}_{N}$, for each $j \in[M]_{0}$, which is equivalent to

$$
\begin{equation*}
\mathbf{D}_{\widetilde{\sigma}} \mathbf{D}_{R, j}=\mathbf{D}_{\widetilde{\sigma}} \mathbf{R}_{j} \tag{31}
\end{equation*}
$$

Denote the index set of the clusters with perfect CSI as $\mathcal{K}_{1} \subset[K]$ such that $\widetilde{\sigma}_{k_{1}}^{2}=0$, for $k_{1} \in \mathcal{K}_{1}$. The above condition (31) can be achieved if $\left[\mathbf{R}_{j}\right]_{[k, l]}=\mathbf{0}_{N_{k} \times N_{l}}$ when the indexes $k$ and $l (k \neq l)$ do not belong to the set $\mathcal{K}_{1}$ simultaneously. Furthermore, when the spatial correlations among all clusters are negligible, i.e., $\mathbf{R}_{j}=\mathbf{D}_{R, j}$ for each $j \in[M]_{0}$ or the CSI is perfect for all of the clusters, i.e., $\widetilde{\sigma}_{k}^{2}=0$ for each $k \in[K]$, (31) is satisfied automatically.

Remark 6: When there is no spatial correlation between clusters, the matrix $\boldsymbol{\Delta}$ becomes diagonal. Under such circumstances, it can be verified that when $\boldsymbol{\alpha}= C\left[\frac{\left(1+[\mathbf{v}]_{1}\right)[\mathbf{v}]_{1}}{[\boldsymbol{\Delta}]_{1,1}}, \ldots, \frac{\left(1+[\mathbf{v}]_{K}\right)[\mathbf{v}]_{K}}{[\boldsymbol{\Delta}]_{K, K}}\right]$ with $C \neq 0$ being an arbitrary constant in (28c), we have

$$
\begin{equation*}
\bar{\gamma}^{\mathrm{lfoc}}=\bar{\gamma}^{\mathrm{lfsc}}=\bar{\gamma}^{\mathrm{lfcc}}=\sum_{k=1}^{K} \frac{[\mathbf{v}]_{k}^{2}}{[\boldsymbol{\Delta}]_{k, k}}, \tag{32}
\end{equation*}
$$

which is equal to the sum of the SINRs from all clusters. This is consistent with the conclusion of [2, Theorem 6], which assumes uncorrelated Rayleigh channels and perfect CSI. In addition, $[\mathbf{v}]_{k}$ and $[\boldsymbol{\Delta}]_{k, k}$ are only related to the local spatial correlation, which varies slowly in time. As a result, the fusion
coefficients for LFCC can be set as $\alpha_{k}=\frac{\left(1+[\mathbf{v}]_{k}\right)[\mathbf{v}]_{k}}{[\boldsymbol{\Delta}]_{k, k}}$ to achieve the asymptotically optimal performance.

Remark 7: By applying Taylor expansion, it can be verified that the achievable rate can be calculated as $\mathbb{E}\left[\log \left(1+\gamma^{\text {fs }}\right)\right]= \log \left(1+\bar{\gamma}^{\mathrm{fs}}\right)+\mathcal{O}\left(N^{-1}\right)$, where fs $\in\{$ lfoc, lfsc, lfcc $\}$. These results can be utilized to evaluate the ergodic rate.

Remark 8: The result in (28) can be significantly simplified and given in a closed form with i.i.d. channels, providing useful insights for system design. More details are available in Section IV-A. It will be shown that there is a trade-off between complexity and performance. It is recommended to adopt LMMSE estimator locally, minimize the number of clusters, and avoid uniform partitioning.

Next, we investigate the case with heterogeneous CSI inaccuracy levels among the clusters. Specifically, the following corollary illustrates the behavior of the SINR when certain clusters have severe CSI errors.

Corollary 1: Let $\mathcal{K}_{e}$ be the index set of clusters with severe CSI errors, i.e., $\widetilde{\sigma}_{k}^{2} \rightarrow+\infty$ for $k \in \mathcal{K}_{e}$, while $\widetilde{\sigma}_{l}^{2}$ is fixed for $l \in \mathcal{K}_{g}=[K]-\mathcal{K}_{e}=\left\{k_{1}, k_{2}, \ldots, k_{G}\right\}$, where $G=K- \left|\mathcal{K}_{e}\right|$. Then the deterministic approximation of the SINR satisfies

$$
\begin{equation*}
\bar{\gamma}^{\mathrm{fs}} \rightarrow \bar{\gamma}_{\mathcal{K}_{g}}^{\mathrm{fs}}, \tag{33}
\end{equation*}
$$

where fs $\in\{$ lfoc, lfsc, lfcc $\}$ and $\bar{\gamma}_{\mathcal{K}_{g}}^{\mathrm{fs}}$ is obtained by replacing the channel $\mathbf{h}_{j}$ by $\mathbf{h}_{j}^{\mathcal{K}_{g}}=\left[\mathbf{h}_{j k_{1}}^{T}, \ldots, \mathbf{h}_{j k_{G}}^{T}\right]^{T}$ for each $j \in[M]_{0}$ and $\boldsymbol{\alpha}$ by $\boldsymbol{\alpha}^{\mathcal{K}_{g}}=\left[\alpha_{k_{1}}, \ldots, \alpha_{k_{G}}\right]$ in Theorem 1.

Proof: The proof of Corollary 1 is given in Appendix D.
Remark 9: Corollary 1 indicates that for decentralized estimation, when several clusters have severe CSI errors, the performance will be equal to that of a system where these clusters are ignored.

## A. Special Case Study: I.I.D. Channels

In this section, we will consider the simplified channel model with $\mathbf{R}_{j}=\mathbf{I}_{N}$ to get some physical insights. The parameter $\mathbf{Z}_{k}$ is set as (17), i.e., $\mathbf{Z}_{k}=\frac{(M+1) \widetilde{\sigma}_{k}^{2}}{N_{k}\left(\widetilde{\sigma}_{k}^{2}+1\right)} \mathbf{I}_{N_{k}}$.

1) SINR Approximation: With i.i.d. channels, the SINR in Theorem 1 can be given in a closed-form.

Corollary 2: Given assumptions A.1-A. 3 and the i.i.d. channels, $\bar{\gamma}^{\text {lfoc }}, \bar{\gamma}^{\text {lfsc }}$ and $\bar{\gamma}^{\text {lfcc }}$ can be given by

$$
\begin{align*}
& \bar{\gamma}^{\mathrm{lfcc}}=\bar{\gamma}^{\mathrm{lfc}}=\sum_{k=1}^{K} \frac{\delta_{k}}{\varpi_{k}},  \tag{34a}\\
& \bar{\gamma}^{\mathrm{lfcc}}=\frac{\left|\sum_{k=1}^{K} \alpha_{k} \frac{\delta_{k}}{1+\delta_{k}}\right|^{2}}{\sum_{k=1}^{K} \frac{\left|\alpha_{k}\right|^{2} \delta_{k}}{\left(1+\delta_{k}\right)^{2}} \varpi_{k}}, \tag{34b}
\end{align*}
$$

where

$$
\begin{equation*}
\varpi_{k}=1+\left(\frac{\sigma^{2}}{M c_{k}}-\rho_{k}\right) \frac{\left(\widetilde{\sigma}_{k}^{2}+1\right) \delta_{k}}{1-\frac{\delta_{k}^{2}}{c_{k}\left(1+\delta_{k}\right)^{2}}} \tag{35}
\end{equation*}
$$

and $\delta_{k}$ is given by

$$
\begin{equation*}
\delta_{k}=\frac{1-\frac{1}{c_{k}}-A_{k}+\sqrt{\left(A_{k}+\frac{1}{c_{k}}-1\right)^{2}+4 A_{k}}}{2 A_{k}} \tag{36}
\end{equation*}
$$

with $A_{k}=\rho_{k}\left(\widetilde{\sigma}_{k}^{2}+1\right)+\frac{M+1}{M c_{k}} \widetilde{\sigma}_{k}^{2}$.
Proof: The proof can be obtained by setting $\mathbf{R}_{j}=\mathbf{I}_{N}$ and $\mathbf{Z}_{k}=\frac{(M+1) \widetilde{\sigma}_{k}^{2}}{N_{k}\left(\widetilde{\sigma}_{k}^{2}+1\right)}$ in Theorem 1 and is omitted here.

Remark 10: According to the definition, it can be verified $\delta_{k}=[\mathbf{v}]_{k}$ and $\varpi_{k}=\frac{[\boldsymbol{\Delta}]_{k, k}}{[\mathbf{v}]_{k}}$ in Theorem 1.

Denote $\boldsymbol{\rho}_{K}=\left[\rho_{1}, \ldots, \rho_{K}\right]^{T}$ and $\mathbf{c}_{K}=\left[c_{1}, \ldots, c_{K}\right]^{T}$. We next investigate the impact of parameters $\boldsymbol{\rho}_{K}, \mathbf{c}_{K}$, and the number of clusters $K$ on the SINR $\bar{\gamma}^{\text {lfoc }}=\bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K}\right)$ where we keep $N$ and $M$ fixed. We also assume the CSI inaccuracy level is identical among clusters, i.e., $\widetilde{\sigma}_{k}^{2}=\widetilde{\sigma}^{2}$ for each $k \in[K]$ in the following.
2) Regularization Parameter: The following corollary gives the optimal parameter $\rho_{K}$.

Corollary 3: Assume the same conditions as Corollary 2. For any $\boldsymbol{\rho}_{K}>0, \mathbf{c}_{K} \geq 0$, we have

$$
\begin{equation*}
\bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K}\right) \leq \bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}^{\text {opt }}, \mathbf{c}_{K}\right), \tag{37}
\end{equation*}
$$

where $\boldsymbol{\rho}_{K}^{\mathrm{opt}}=\left[\frac{\sigma^{2}}{M c_{1}}, \ldots, \frac{\sigma^{2}}{M c_{K}}\right]^{T}$.
Proof: The proof of Corollary 3 is omitted due to limited space, and can be found in the extended version [31].

Remark 11: We can observe that the optimal parameter $\rho_{K}^{\text {opt }}$ that maximizes the SINR is identical to that achieving the minimal local MSE as derived in Section III-A. This can be intuitively obtained from (34a) where the SINR $\bar{\gamma}^{\text {lfoc }}$ is the sum of the SINRs of all clusters.
3) Antenna Partitioning Strategy: The following corollary shows the impact of the parameter $\mathbf{c}_{K}$.

Corollary 4: Assume the same conditions as Corollary 2 and denote $\boldsymbol{\rho}_{K}=\left[\frac{a}{c_{1}}, \ldots, \frac{a}{c_{K}}\right]^{T}$. For any $\mathbf{c}_{K} \geq 0$ and $\frac{\sigma^{2}}{M} \leq a$, we have

$$
\begin{equation*}
\bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K}\right) \leq \bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K, \mathrm{M}}\right), \tag{38}
\end{equation*}
$$

and for any $\mathbf{c}_{K} \geq 0$ and $\frac{\sigma^{2}}{M} \leq a \leq \frac{2 \sigma^{2}}{M}+\frac{(M+1) \widetilde{\sigma}^{2}}{M\left(\widetilde{\sigma}^{2}+1\right)}$, we have

$$
\begin{equation*}
\bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K, \mathrm{~m}}\right) \leq \bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K}\right), \tag{39}
\end{equation*}
$$

where $\mathbf{c}_{K, \mathrm{~m}}=[\bar{c}, \ldots, \bar{c}]^{T}, \mathbf{c}_{K, \mathrm{M}}=[K \bar{c}, 0, \ldots, 0]^{T}$, and $\bar{c}= \frac{1}{K} \sum_{k=1}^{K} c_{k}$.

Proof: The proof of Corollary 4 is omitted due to limited space, and can be found in the extended version [31].

Remark 12: Inequalities (38) and (39) imply that when the regularization parameter $\rho_{K}$ is within a certain range, i.e., $\frac{\sigma^{2}}{M} \leq a$, the system achieves the maximum SINR when the receive antennas are concentrated in one cluster, i.e., the centralized scheme. On the other side, when the antennas are equally partitioned, the system achieves the lowest SINR. This finding aligns with the conclusions in [2, Lemma 7, Lemma 8]. Note that [2] considers a given parameter $\rho_{K}$ with perfect CSI, but Corollary 4 provides the range for $\boldsymbol{\rho}_{K}$ with imperfect CSI.

Remark 13: It can be observed that the optimal regularization parameter $\rho_{K}^{\text {opt }}$ in Corollary 3 is within the range such that (38) and (39) hold.
4) Number of Clusters: Corollary 4 compares different antenna partitioning strategies with a fixed number of clusters $K$. Another interesting question to investigate is how the number
of clusters $K$ affects the SINR. The following corollary demonstrates this impact.

Corollary 5: Assume the same conditions as Corollary 2 and denote $\boldsymbol{\rho}_{K}=\left[\frac{a}{c_{1}}, \ldots, \frac{a}{c_{K}}\right]^{T}$. For any $\frac{\sigma^{2}}{M} \leq a$, we have

$$
\begin{equation*}
\bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K, \mathrm{~m}}\right) \geq \bar{\gamma}_{K+1}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K+1}, \mathbf{c}_{K+1, \mathrm{~m}}\right) . \tag{40}
\end{equation*}
$$

Proof: The proof of Corollary 5 is omitted due to limited space, and can be found in the extended version [31]. $\square$

Remark 14: Since the total number of receive antennas $N$ is fixed, Corollary 5 indicates that as the number of clusters increases, the SINR will monotonically decrease.

Remark 15: It can be verified from the proof of Corollary 5 that

$$
\begin{equation*}
\bar{\gamma}_{K}^{\text {lfoc }}\left(\boldsymbol{\rho}_{K}, \mathbf{c}_{K, \mathrm{~m}}\right) \geq \frac{N}{\left(\sigma^{2}+M\right)\left(\widetilde{\sigma}^{2}+1\right)+\widetilde{\sigma}^{2}}, \tag{41}
\end{equation*}
$$

and the equality holds when $K \rightarrow+\infty$, which is not achievable since $K \leq N$. From Corollary 4, we know that the equal antenna partitioning strategy has the worst performance. Therefore, for decentralized LMMSE receivers, the SINR is strictly lower bounded by the right hand side (RHS) of (41). When the numbers of antennas and users are large, this lower bound is approximately $\frac{N}{M}$.

## V. Numerical Results

In this section, we will verify the accuracy of the theoretical results in Section IV. We will also demonstrate the impact of several key system parameters over i.i.d. channels, including the regularization parameter, antenna partitioning strategy, and the number of clusters. For simplicity, we use the notation $\mathcal{N}_{K}= \left(N_{1}, \ldots, N_{K}\right)$ to denote the antenna partitioning strategy. The Monte Carlo (MC) simulation results were obtained from 5000 realizations and are illustrated by markers in all figures.

## A. Correlated Channels

We consider a uniform linear array of antennas at the BS. The ( $m, n$ )-th entry of the spatial correlation matrix at BS is modeled as [32], [33]

$$
\begin{align*}
& {\left[\mathbf{C}\left(\eta, \delta, d_{s}\right)\right]_{m, n} } \\
= & \int_{-180^{\circ}}^{180^{\circ}} \frac{1}{\sqrt{2 \pi \delta^{2}}} e^{2 \pi J d_{s}(m-n) \sin \left(\frac{\pi \phi}{180}\right)-\frac{(\phi-\eta)^{2}}{2 \delta^{2}}} \mathrm{~d} \phi \tag{42}
\end{align*}
$$

Here, $d_{s}$ and $\phi$ denote the receive antenna spacing and angular spread, respectively, $\eta$ represents the mean angle, and $\delta$ denotes the root-mean-square angle spread. In the simulation, we set $\mathbf{R}_{j}=\mathbf{C}\left(\eta_{j}, \delta_{j}, 1\right)$ with $\eta_{j}=\left(\frac{j}{180 M}\right)^{\circ}$ and $\delta_{j}=10^{\circ}+\left(\frac{j}{M 10}\right)^{\circ}$. The parameter $\rho_{k}$ is set as $\rho_{k}=\frac{\sigma^{2}}{N_{k}}$ and $\mathbf{Z}_{k}$ is set according to (17) for each $k \in[K]$.

Approximation of SINR: Fig. 2 illustrates the SINR with different linear fusion schemes. The system dimensions are set as $N=32, M=12, K=2$, and $\mathcal{N}_{2}=(10,22)$. The red line and the two dotted lines represent the results of centralized LMMSE and LFCC, respectively. The fusion parameter is set as (24) for LFCC-1 and (25) for LFCC-2, respectively. It is shown that centralized LMMSE performs better than the three decentralized

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-08.jpg?height=1396&width=860&top_left_y=214&top_left_x=1063)
Fig. 2. SINR with different linear fusion schemes.

schemes. By comparing the results with MC simulations, we can observe that the approximation results in Theorem 1 are accurate. By comparing the results of LFSC and LFOC, it can be observed that LFSC is highly efficient. Furthermore, Fig. 2 shows that when the antenna partition is unbalanced, using LFCC will lead to performance degradation.

BER Performance: Fig. 3 shows the bit error rate (BER) with 16-QAM modulation for different fusion schemes. The system parameters are set as $N=108, M=52, K=2$, and $\mathcal{N}_{2}= (20,88)$. The fusion parameter for LFCC is set as $\boldsymbol{\alpha}=[0.5,0.5]$ and the signal SNR and training SNR of two clusters are set to be equal, with $\frac{1}{\sigma^{2}}=\frac{1}{\widetilde{\sigma}_{1}^{2}}=\frac{1}{\widetilde{\sigma}_{2}^{2}}$, represented by the horizontal axis in Fig. 3. It can be observed that the BER for centralized architecture is much lower than that with the decentralized scheme.

Heterogeneous CSI Inaccuracy: Fig. 4 illustrates the performance of SINR with different levels of CSI inaccuracy among clusters. The system parameters are set as $N=40, M=16$, $K=2, \mathcal{N}_{2}=(22,18)$, and $\frac{1}{\sigma^{2}}=\frac{1}{\widetilde{\sigma}_{2}^{2}}=30 \mathrm{~dB}$. The fusion parameter for LFCC is set as $\boldsymbol{\alpha}=[0.5,0.5]$. The red line represents the performance of centralized estimation considering only the

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-09.jpg?height=532&width=704&top_left_y=227&top_left_x=214)
Fig. 3. BER versus SNR.

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-09.jpg?height=527&width=684&top_left_y=855&top_left_x=223)
Fig. 4. SINR versus training SNR $\frac{1}{\sigma_{1}^{2}}$.

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-09.jpg?height=532&width=700&top_left_y=1512&top_left_x=214)
Fig. 5. SINR versus mean angle $\eta$.

second cluster. It can be observed that when the training SNR of the first cluster is very low, the performance approaches that without considering the first cluster, which validates Corollary 1.

Impact of Spatial Correlations: Fig. 5 illustrates the impact of the mean angle of the spatial correlation matrices on SINR for different fusion schemes. The spatial correlations are set to be $\mathbf{R}_{j}=\mathbf{C}(\eta, 20,1)$. The parameters are set as $N=40, M=18$, $\mathcal{N}_{2}=(28,12)$, and $\frac{1}{\sigma^{2}}=\frac{1}{\widetilde{\sigma}_{1}^{2}}=\frac{1}{\widetilde{\sigma}_{2}^{2}}=30 \mathrm{~dB}$. For LFCC, $\boldsymbol{\alpha}$ is set as $[0.5,0.5]$. It can be observed that when $\eta=90^{\circ}$, the SINR is

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-09.jpg?height=523&width=680&top_left_y=227&top_left_x=1138)
Fig. 6. SINR versus the ratio of fusion coefficients $\frac{\alpha_{2}}{\alpha_{1}}$.

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-09.jpg?height=519&width=678&top_left_y=867&top_left_x=1140)
Fig. 7. SINR versus the regularization parameter $\rho$.

the lowest. This is because when $\eta=90^{\circ}$, the spatial correlation is strong, leading to many eigenvalues of $\mathbf{R}_{j}$ being close to zero.

Impact of Fusion Coefficients: Fig. 6 shows the impact of the fusion coefficients with different antenna partitioning strategies. The system dimensions are set as $N=40, M=15$, and $K=2$. The signal and training SNR are both set as 30 dB . It can be observed that when antennas are uniformly allocated to different clusters, i.e., $\mathcal{N}_{2}=(20,20)$, SINR is not sensitive to the value of $\boldsymbol{\alpha}$, but the maximum SINR is lower than that with unbalanced antenna partitioning. This observation for correlated channels is consistent with the conclusion for i.i.d. channels in Corollary 4. Moreover, as the number of antennas in a cluster increases, the corresponding linear fusion weights should also increase.

## B. I.I.D. Channels

In the experiment, the training and signal SNR are both 30 dB , and the parameter $\mathbf{Z}_{k}$ is set according to (17) for each $k \in[K]$.

Optimal Regularization Parameter: Fig. 7 depicts the impact of $\boldsymbol{\rho}_{K}$ on the SINR with i.i.d. channels. The system dimensions are set as $N=72$ and $M=40$. The parameter $\boldsymbol{\rho}_{K}$ is of the form $\boldsymbol{\rho}_{K}=\left[\frac{\rho}{N_{1}}, \ldots, \frac{\rho}{N_{K}}\right]^{T}$. It can be observed that SINR is not sensitive to $\rho$. Significant performance loss is only observed when $\rho$ is very large. Furthermore, according to Corollary 3, the theoretical optimal parameter $\boldsymbol{\rho}_{K}^{\mathrm{opt}}$ should be $\boldsymbol{\rho}_{K}^{\mathrm{opt}}=(-30 \mathrm{~dB}) \cdot \left[\frac{1}{N_{1}}, \ldots, \frac{1}{N_{1}}\right]^{T}$. The optimal value $\rho^{\text {opt }}=-30 \mathrm{~dB}$ shown in the

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-10.jpg?height=517&width=692&top_left_y=225&top_left_x=232)
Fig. 8. SINR versus the number of antennas allocated to the first cluster $N_{1}$.

![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-10.jpg?height=514&width=688&top_left_y=842&top_left_x=236)
Fig. 9. SINR versus $K$.

figure obtained by the exhausted search validates the accuracy of Corollary 3.

Impact of Antenna Partitioning Strategy: In Fig. 8, we plot the SINR for different antenna partitioning strategies with different numbers of users. The parameters are set as $N=120, K=2$, and $\rho_{k}=\frac{\sigma^{2}}{N_{k}}$. It is observed that when clusters are of equal size, the SINR is the lowest, which agrees with Corollary 4. Furthermore, as the number of users increases, the performance degradation with uniform antenna partitioning becomes more obvious.

Impact of Number of Clusters: In Fig. 9, we plot the SINR for different numbers of clusters $K$ where antennas are almost equally allocated with $\mathcal{N}_{K}=\left(\left\lfloor\frac{N}{K}\right\rfloor,\left\lfloor\frac{N}{K}\right\rfloor, \ldots, N-(K-\right.$ 1) $\left\lfloor\frac{N}{K}\right\rfloor$ ). The parameters are set as $M=40$ and $\rho_{k}=\frac{\sigma^{2}}{N_{k}}$. It can be observed that as the number of clusters increases, the SINR decreases monotonically and is lower bounded by (41), which is shown by the dashed lines. This validates Corollary 5.

## VI. Conclusion

In this paper, we considered the decentralized MIMO systems and imperfect CSI using LMMSE receivers. It was shown that with DBP, the linear fusion coefficients that maximize the receive SINR also minimize the MSE for estimating the transmit signal. To reduce the complexity, we further proposed two linear fusion schemes and derived the deterministic approximations of the SINR with imperfect CSI and general spatial correlations.

Based on the results, we investigated the optimal LMMSE regularization parameters, optimal antenna partitioning strategies, and the impact of the number of clusters. It was shown that with i.i.d. channels, the SINR is minimized when the clusters are of equal size. Conversely, the optimal performance is achieved when antennas are mostly unbalanced distributed, i.e., all antennas are allocated to a single cluster. We also proved that as the number of clusters increases, the SINR monotonically decreases.

From the perspective of RMT, we investigated the asymptotic convergence properties of the resolvent for the covariance matrix with generally correlated columns and its related functions. These results can be utilized for the second-order SINR analysis, e.g., the outage probability, and be applied to downlink scenarios, e.g., the analysis of RZF.

## Appendix A Useful Results

In this section, we will give the main mathematical results, which will be frequently used throughout the proofs in this paper.

## A. Matrix Inversion Lemma

Lemma 1: [23, Lemma 1]: Let $\mathbf{M} \in \mathbb{C}^{N \times N}$ be an invertible matrix, $\mathbf{m} \in \mathbb{C}^{N}$, and $a \in \mathbb{C}$. If $1+a \mathbf{m}^{H} \mathbf{M}^{-1} \mathbf{m} \neq 0$, we have

$$
\begin{equation*}
\mathbf{m}^{H}\left(\mathbf{M}+a \mathbf{m m}^{H}\right)^{-1}=\frac{\mathbf{m}^{H} \mathbf{M}^{-1}}{1+a \mathbf{m}^{H} \mathbf{M}^{-1} \mathbf{m}} . \tag{43}
\end{equation*}
$$

## B. Convergence of Random Vectors

Lemma 2: [23, Lemma 4]: Let $\mathbf{A}_{N} \in \mathbb{C}^{N \times N}$ be a random matrix and $\mathbf{x}_{N} \in \mathbb{C}^{N}$ be a random vector with i.i.d. entries with normalized Gaussian distribution $\mathcal{C N}(0,1)$. Assume that for each $j,[\mathbf{x}]_{j}$ is independent with sequence $\left(\mathbf{A}_{N}\right)_{N \geq 1}$ and $\mathbb{P}\left(\sup _{N \geq 1}\left\|\mathbf{A}_{N}\right\|<+\infty\right)=1$. Then, we have

$$
\begin{equation*}
\frac{\operatorname{Tr}\left(\mathbf{x}_{N}^{H} \mathbf{A}_{N} \mathbf{x}_{N}\right)}{N}-\frac{\operatorname{Tr} \mathbf{A}_{N}}{N} \xrightarrow[N \rightarrow+\infty]{\text { a.s. }} 0 . \tag{44}
\end{equation*}
$$

Proof: Here we provide a proof different from [23] which relies on Tonelli's theorem. To describe independence, [23] assumes the underlying probability space is the product probability space of $\left(\mathbf{x}_{N}\right)_{N \geq 1}$ and $\left(\mathbf{A}_{N}\right)_{N \geq 1}$, whereas here we discuss within the same probability space.

Denoting the underline probability space $(\Omega, \mathcal{F}, \mathbb{P})$. Define the set $A_{n, K}=\left\{\omega \in \Omega: \sup _{j \geq n}\left\|\mathbf{A}_{j}(\omega)\right\| \leq K\right\}$ and $B_{N, \epsilon}= \left\{\omega \in \Omega: d_{N}(\omega) \leq \epsilon\right\}$, where

$$
\begin{equation*}
d_{N}(\omega)=\left|\frac{\operatorname{Tr}\left[\mathbf{x}_{N}^{H}(\omega) \mathbf{A}_{N}(\omega) \mathbf{x}_{N}(\omega)\right]}{N}-\frac{\operatorname{Tr} \mathbf{A}_{N}(\omega)}{N}\right| . \tag{45}
\end{equation*}
$$

To prove $d_{N} \xrightarrow[N \rightarrow+\infty]{\text { a.s. }} 0$, we only need to show that for any positive integer $n$ and $\epsilon>0, \mathbb{P}\left(\bigcup_{n=1}^{+\infty} \bigcap_{N=n}^{+\infty} B_{N, \epsilon}\right)=1$ holds. In the following, we will prove this by a stronger result $\mathbb{P}\left(\bigcup_{n=1}^{+\infty} \bigcap_{N=n}^{+\infty} B_{N, \epsilon}\right) \geq 1$. To this end, we write

$$
\mathbb{P}\left(\bigcup_{n=1}^{+\infty} \bigcap_{N=n}^{+\infty} B_{N, \epsilon}\right) \geq \mathbb{P}\left(\bigcup_{n=1}^{+\infty} \bigcap_{N=n}^{+\infty} B_{N, \epsilon} \bigcap \bigcup_{K=0}^{+\infty} A_{n, K}\right)
$$

$$
\begin{align*}
& =\mathbb{P}\left(\bigcup_{K=0}^{+\infty} \bigcup_{n=1}^{+\infty} \bigcap_{N=n}^{+\infty} B_{N, \epsilon} \bigcap A_{n, K}\right) \\
& \stackrel{(a)}{=} \lim _{K \rightarrow+\infty} \lim _{n \rightarrow+\infty} \mathbb{P}\left(\bigcap_{N=n}^{+\infty} B_{N, \epsilon} \bigcap A_{n, K}\right) \tag{46}
\end{align*}
$$

where step (a) follows from $A_{n, K} \subset A_{n, K+1}, A_{n, K} \subset A_{n+1, K}$, and continuity of probability measure. On the other side, we have

$$
\begin{align*}
& \mathbb{P}\left(\bigcap_{N=n}^{+\infty} B_{N, \epsilon} \bigcap A_{n, K}\right)=1-\mathbb{P}\left(\bigcup_{N=n}^{+\infty} B_{N, \epsilon}^{c} \bigcup A_{n, K}^{c}\right) \\
& =1-\mathbb{P}\left(A_{n, K}^{c}\right)-\mathbb{P}\left(\bigcup_{N=n}^{+\infty} B_{N, \epsilon}^{c} \bigcap A_{n, K}\right) \\
& \geq \mathbb{P}\left(A_{n, K}\right)-\sum_{N \geq n} \mathbb{P}\left(B_{N, \epsilon}^{c} \bigcap A_{n, K}\right) \tag{47}
\end{align*}
$$

By using Markov's inequality, we can get

$$
\begin{align*}
& \mathbb{P}\left(B_{N, \epsilon}^{c} \bigcap A_{n, K}\right) \leq \mathbb{E}_{\left\{d_{N} \geq \epsilon\right\}} \mathbb{I}_{\left\{\left\|\mathbf{A}_{N}\right\| \leq K\right\}} \\
& \leq \mathbb{E}\left[\mathbb{I}_{\left\{\left\|\mathbf{A}_{N}\right\| \leq K\right\}} \mathbb{E}\left(\epsilon^{-p} d_{N}^{p} \mid \mathbf{A}_{N}\right)\right] \\
& \stackrel{(a)}{\leq} C_{p} N^{-\frac{p}{2}} \mathbb{E}\left[\mathbb{I}_{\left\{\left\|\mathbf{A}_{N}\right\| \leq K\right\}}\left\|\mathbf{A}_{N}\right\|^{p}\right]=\mathcal{O}\left(N^{-\frac{p}{2}} K^{p}\right), \tag{48}
\end{align*}
$$

where $p>2, C_{p}$ is a constant, and step (a) follows from the trace lemma [23, Lemma 3]. Hence, $\sum_{N=n}^{+\infty} \mathbb{P}\left(B_{N, \epsilon}^{c} \bigcap A_{n, K}\right) \rightarrow 0$ as $n \rightarrow+\infty$ and it holds true that

$$
\begin{equation*}
\lim _{n \rightarrow+\infty} \mathbb{P}\left(\bigcap_{N=n}^{+\infty} B_{N, \epsilon} \bigcap A_{n, K}\right) \geq \lim _{n \rightarrow+\infty} \mathbb{P}\left(A_{n, K}\right) \tag{49}
\end{equation*}
$$

By combining (49) and (46), we can obtain

$$
\begin{align*}
& \mathbb{P}\left(\bigcup_{n=1}^{+\infty} \bigcap_{N=n}^{+\infty} B_{N, \epsilon}\right) \geq \lim _{K \rightarrow+\infty} \lim _{n \rightarrow+\infty} \mathbb{P}\left(A_{n, K}\right) \\
& \stackrel{(a)}{=} \mathbb{P}\left(\bigcup_{k=0}^{+\infty} \bigcup_{n=1}^{+\infty} A_{n, K}\right)=\mathbb{P}\left(\bigcup_{n=1}^{+\infty} \bigcup_{K=0}^{+\infty} A_{n, K}\right) \stackrel{(b)}{=} 1 \tag{50}
\end{align*}
$$

where step ( $a$ ) follows from continuity of probability measure and step ( $b$ ) follows from the identity $\mathbb{P}\left(\bigcup_{K=0}^{+\infty} A_{n, k}\right)=1$. This completes the proof of Lemma 2.

## C. Convergence of Random Matrices

The SINR involves terms associated with random matrices $\widehat{\boldsymbol{\Sigma}}$ and $\widetilde{\boldsymbol{\Sigma}}$ whose columns are generally correlated. This makes the evaluation of the SINR very challenging. In the following, we introduce a more general setting and provide the relevant results, which can be utilized to prove Theorem 1.

Let $\quad \widetilde{\mathbf{X}}=\left[\mathbf{A}_{1} \mathbf{x}_{1}, \ldots, \mathbf{A}_{M} \mathbf{x}_{M}\right] \in \mathbb{C}^{N \times M} \quad$ and $\quad \widetilde{\mathbf{Y}}= \left[\mathbf{B}_{1} \mathbf{x}_{1}, \ldots, \mathbf{B}_{M} \mathbf{x}_{M}\right] \in \mathbb{C}^{N \times M}, \quad$ where $\quad \mathbf{A}_{j}, \mathbf{B}_{j} \in \mathbb{C}^{N \times N_{i}^{x}}$, and $\mathbf{x}_{j} \sim \mathcal{C} \mathcal{N}\left(0, \mathbf{I}_{N_{j}^{x}}\right)$ for each $j \in[M]$. Define two correlation matrices sets $A=\left\{\mathbf{A}_{j}: j \in[M]\right\}$ and $B=\left\{\mathbf{B}_{j}: j \in[M]\right\}$. Denote $\boldsymbol{\Omega}_{j}=\mathbf{A}_{j} \mathbf{A}_{j}^{H}, \mathbf{A}_{j k}=\mathbf{A}_{j}\left[\boldsymbol{\varsigma}_{k},:\right]$, and $\mathbf{B}_{j k}=\mathbf{B}_{j}\left[\boldsymbol{\varsigma}_{k},:\right]$. Let $\mathbf{X}_{k}=\frac{1}{\sqrt{N_{k}}} \widetilde{\mathbf{X}}\left[\boldsymbol{\varsigma}_{k},:\right]$ and $\mathbf{Y}_{k}=\frac{1}{\sqrt{N_{k}}} \widetilde{\mathbf{Y}}\left[\boldsymbol{\varsigma}_{k},:\right]$. The resolvent

TABLE II
Table of Notations
| Notation | Expression |
| :---: | :---: |
| $\digamma_{k}(\mathcal{A})$ | $\operatorname{Tr} \mathcal{A} \mathbf{Q}_{k}$ |
| $\Phi_{B, k l}(\mathcal{A}, \mathbf{b})$ | $\operatorname{Tr} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k} \operatorname{diag}(\mathbf{b}) \mathbf{Y}_{l}^{H}$ |
| $\Phi_{k l}(\mathcal{A}, \mathbf{b})$ | $\operatorname{Tr} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k} \operatorname{diag}(\mathbf{b}) \mathbf{X}_{l}^{H}$ |
| $\Upsilon_{k l}(\mathcal{A}, \mathcal{B})$ | $\operatorname{Tr} \mathcal{A} \mathbf{Q}_{k} \mathcal{B} \mathbf{Q}_{l}$ |
| $\Pi_{B, k l}(\mathcal{A})$ | $\operatorname{Tr} \mathcal{A} \mathbf{Q}_{k} \mathbf{Y}_{k} \mathbf{Y}_{l}^{H} \mathbf{Q}_{l}$ |
| $\Pi_{k l}(\mathcal{A})$ | $\operatorname{Tr} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k} \mathbf{X}_{l}^{H} \mathbf{Q}_{l}$ |


matrix of $\mathbf{X}_{k} \mathbf{X}_{k}^{H}+\mathbf{S}_{k}$ is given by

$$
\begin{equation*}
\mathbf{Q}_{k}(z)=\left(\mathbf{X}_{k} \mathbf{X}_{k}^{H}+\mathbf{S}_{k}-z \mathbf{I}_{N_{k}}\right)^{-1} \tag{51}
\end{equation*}
$$

with $\mathbf{S}_{k}$ being deterministic and Hermitian nonnegative. We further define some functions of the resolvents in Table II, where we set $\mathbf{Q}_{k}=\mathbf{Q}_{k}\left(z_{k}\right)$, for each $k \in[K]$ and omit the variable $z_{k}$ for the sake of notation simplicity. Furthermore, $\mathcal{A}$ and $\mathcal{B}$ are appropriately sized matrices, and $\mathbf{b}$ is a properly dimensioned vector. We next introduce the stochastic equivalent notation.

Definition 1: (Stochastic Equivalent) For random sequence $\left(X_{N}\right)_{N \geq 1}$ and deterministic sequence $\left(\bar{X}_{N}\right)_{N \geq 1}$, we use $X_{N} \asymp_{l} \bar{X}_{N}$ to denote

$$
\begin{equation*}
\left|\mathbb{E} X_{N}-\bar{X}_{N}\right|=\mathcal{O}\left(N^{-l}\right), \frac{\left|X_{N}-\bar{X}_{N}\right|}{N} \xrightarrow[N \rightarrow+\infty]{\text { a.s. }} 0 . \tag{52}
\end{equation*}
$$

The following lemma gives the stochastic equivalents for the functions in Table II.

Lemma 3: Assume Assumption A. 1 holds, the maximal spectral norm of the correlation matrices is bounded, i.e., $\limsup \sup _{j \in[M]}\left\{\left\|\mathbf{A}_{j}\right\|,\left\|\mathbf{B}_{j}\right\|\right\}<+\infty$, and the spectral norms of matrices $\mathcal{A}, \mathcal{B}$ and $\operatorname{diag}(\mathbf{b})$ are uniformly bounded. For any $z_{1}, \ldots, z_{K}<0$, we have $\digamma_{k} \asymp_{\frac{1}{2}} \bar{\digamma}_{k}, \Phi_{B, k l} \asymp_{\frac{1}{2}} \bar{\Phi}_{B, k l}$, $\Phi_{k l} \asymp_{\frac{1}{2}} \bar{\Phi}_{k l}, \Upsilon_{k l} \asymp_{\frac{1}{2}} \bar{\Upsilon}_{k l}, \Pi_{B, k l} \asymp_{\frac{1}{2}} \bar{\Pi}_{B, k l}$, and $\Pi_{k l} \asymp_{\frac{1}{2}} \bar{\Pi}_{k l}$, where

$$
\begin{align*}
\bar{\digamma}_{k}(\mathcal{A})= & \operatorname{Tr} \mathcal{A} \Theta_{k}  \tag{53}\\
\bar{\Phi}_{B, k l}(\mathcal{A}, \mathbf{b})= & \frac{\sum_{j=1}^{M}\left[\widetilde{\mathbf{F}}_{k} \mathbf{b}\right]_{j} \operatorname{Tr} \mathcal{A} \Theta_{k} \mathbf{A}_{j k} \mathbf{B}_{j l}^{H}}{\sqrt{N_{k} N_{l}}}  \tag{54}\\
\bar{\Upsilon}_{k l}(\mathcal{A}, \mathcal{B})= & \operatorname{Tr} \mathcal{A} \Theta_{k} \mathcal{B} \Theta_{l} \\
& +\widetilde{\lambda}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \Xi_{k l} \boldsymbol{\lambda}_{k l}(\mathcal{B}) \tag{55}
\end{align*}
$$

and $\bar{\Pi}_{k l, B}$ is given in (56) shown at the bottom of the next page. Functions $\bar{\Phi}_{k l}$ and $\bar{\Pi}_{k l}$ can be obtained by setting $\mathbf{B}_{j}=\mathbf{A}_{j}$ for each $j \in[M]$ in $\bar{\Phi}_{k l, B}$ and $\bar{\Pi}_{k l, B}$, respectively and we omit them here. The deterministic variables are defined in Table III where $P$ and $O$ can be any symbol from the set $\{A, B\}$. The matrix $\Theta_{k}$ is defined by the positive solutions of the following system of equations w.r.t. $\delta_{j k}$

$$
\begin{equation*}
\delta_{j k}=\frac{1}{N_{k}} \operatorname{Tr}\left[\boldsymbol{\Omega}_{j}\right]_{[k, k]} \boldsymbol{\Theta}_{k}, j \in[M] \tag{57}
\end{equation*}
$$

TABLE III
Table of Deterministic Quantities
| Notation | Expression | Notation | Expression |
| :--- | :--- | :--- | :--- |
| $\widetilde{\mathbf{F}}_{k}$ $\Xi_{k l}$ <br> $\widetilde{\boldsymbol{\lambda}}_{P, O, k l}(\mathcal{A})$ <br> $\left[\boldsymbol{\Lambda}_{P, O, k l}\right]_{i, j}$ | $\operatorname{diag}\left(\left(1+\delta_{j k}\right)^{-1} ; j \in[M]\right)$ $\left(\mathbf{I}_{M}-\mathbf{\Gamma}_{k l} \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l}\right)^{-1}$ $\frac{\mathbf{1}_{M}^{T}}{\sqrt{N_{k} N_{l}}} \operatorname{diag}\left(\operatorname{Tr} \mathcal{A} \Theta_{k} \mathbf{P}_{j k} \mathbf{O}_{j l}^{H} \Theta_{l} ; j \in[M]\right)$ $\frac{1}{N_{k} N_{l}} \operatorname{Tr}\left[\boldsymbol{\Omega}_{i}\right]_{[l, k]} \boldsymbol{\Theta}_{k} \mathbf{P}_{j k} \mathbf{O}_{j l}^{H} \boldsymbol{\Theta}_{l}$ | $\left[\boldsymbol{\Gamma}_{k l}\right]_{i, j}$ $\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A})$ <br> $\boldsymbol{\lambda}_{k l}(\boldsymbol{\mathcal { B }})$ <br> $\mathbf{D}_{P, O, k}$ | $\frac{1}{N_{k} N_{l}} \operatorname{Tr}\left[\boldsymbol{\Omega}_{i}\right]_{[l, k]} \boldsymbol{\Theta}_{k}\left[\boldsymbol{\Omega}_{j}\right]_{[k, l]} \boldsymbol{\Theta}_{l}$ $\frac{\mathbf{1}_{M}^{T}}{\sqrt{N_{k} N_{l}}} \operatorname{diag}\left(\operatorname{Tr} \mathcal{A} \Theta_{k}\left[\boldsymbol{\Omega}_{j}\right]_{[k, l]} \Theta_{l} ; j \in[M]\right)$ <br> $\frac{1}{N_{k}} \operatorname{diag}\left(\operatorname{Tr} \mathbf{P}_{j k} \mathbf{O}_{j k}^{H} \boldsymbol{\Theta}_{k} ; j \in[M]\right)$ |


$$
\begin{equation*}
\mathbf{\Theta}_{k}=\left(-z_{k} \mathbf{I}_{N_{k}}+\mathbf{S}_{k}+\frac{1}{N_{k}} \sum_{j=1}^{M} \frac{\left[\boldsymbol{\Omega}_{j}\right]_{[k, k]}}{1+\delta_{j k}}\right)^{-1} . \tag{58}
\end{equation*}
$$

Proof: The proof of Lemma 3 is given in Appendix E.

## Appendix B

## Proof of Proposition 1

Denote $\widetilde{\mathbf{H}}=\left[\widetilde{\mathbf{h}}_{1}, \ldots, \widetilde{\mathbf{h}}_{M}\right]$ and $\widehat{\mathbf{H}}_{k}=\left[\widehat{\mathbf{h}}_{1 k}, \ldots, \widehat{\mathbf{h}}_{M k}\right]$. By taking $\mathbf{r}_{k}=\mathbf{r}_{k}^{\mathrm{mmse}}$ in (13), straight-forward computations yield

$$
\begin{equation*}
\gamma_{0}=\frac{\boldsymbol{\alpha} \mathbf{m m}^{H} \boldsymbol{\alpha}^{H}}{\boldsymbol{\alpha} \mathbf{M} \boldsymbol{\alpha}^{H}}, \tag{59}
\end{equation*}
$$

where $\mathbf{M}=\mathbf{D}_{r}^{H}\left(\widetilde{\mathbf{H}} \widetilde{\mathbf{H}}^{H}+\mathbf{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{D}_{r}$ and $\mathbf{m}=\mathbf{D}_{r}^{H} \widetilde{\mathbf{h}}_{0}$. One can validate that $\mathbf{M}$ is almost surely invertible. By letting $\widetilde{\boldsymbol{\alpha}}=\boldsymbol{\alpha} \mathbf{M}^{\frac{1}{2}}$ and $\widetilde{\mathbf{m}}=\mathbf{M}^{-\frac{1}{2}} \mathbf{m}$, we have

$$
\begin{equation*}
\gamma_{0}=\frac{\tilde{\boldsymbol{\alpha}} \tilde{\mathbf{m}} \tilde{\mathbf{m}}^{H} \tilde{\boldsymbol{\alpha}}^{H}}{\tilde{\boldsymbol{\alpha}} \tilde{\boldsymbol{\alpha}}^{H}}, \tag{60}
\end{equation*}
$$

where $\gamma_{0}$ is maximized when $\widetilde{\boldsymbol{\alpha}}=\widetilde{c} \widetilde{\mathbf{m}}^{H}$ for $\widetilde{c} \neq 0$ according to Cauchy-Schwartz inequality. The optimal $\boldsymbol{\alpha}$ is given by

$$
\begin{align*}
\boldsymbol{\alpha}^{\mathrm{opt}}= & \widetilde{c} \mathbf{m}^{H} \mathbf{M}^{-1}=\frac{c \mathbf{m}^{H} \mathbf{M}^{-1}}{1+\mathbf{m}^{H} \mathbf{M}^{-1} \mathbf{m}} \\
& \stackrel{(a)}{=} c \mathbf{m}^{H}\left(\mathbf{M}+\mathbf{m} \mathbf{m}^{H}\right)^{-1} \tag{61}
\end{align*}
$$

where $c=\widetilde{c}\left(1+\mathbf{m}^{H} \mathbf{M}^{-1} \mathbf{m}\right)$ and step (a) follows from Lemma 1. Thus we proved (18). Since (19) is convex, by setting the derivative of the optimization objective w.r.t. $\boldsymbol{\alpha}$ to be to 0 , we can obtain that $\boldsymbol{\alpha}^{\text {opt }}$ is the optimal solution when $c=1$. Therefore, we complete the proof of Proposition 1.

## Appendix C Proof of Theorem 1

## A. Proof of the Almost Sure Convergence

According to Lemma 1, we can write

$$
\begin{equation*}
\mathbf{D}_{r}=\mathbf{Q D}_{h, 0} \mathbf{L F}, \tag{62}
\end{equation*}
$$

where
$\mathbf{Q}=\operatorname{diag}\left(\mathbf{Q}_{k} ; k \in[K]\right), \mathbf{Q}_{k}=\left(\frac{\widehat{\mathbf{H}}_{k} \widehat{\mathbf{H}}_{k}^{H}}{N_{k}}+\mathbf{Z}_{k}+\rho_{k} \mathbf{I}_{N_{k}}\right)^{-1}$,
$\mathbf{L}=\operatorname{diag}\left(N_{k}^{-1} ; k \in[K]\right), \mathbf{D}_{h, 0}=\operatorname{diag}\left(\widehat{\mathbf{h}}_{0 k} ; k \in[K]\right)$
$\mathbf{F}=\operatorname{diag}\left(\left(1+\frac{1}{N_{k}} \widehat{\mathbf{h}}_{0 k}^{H} \mathbf{Q}_{k} \widehat{\mathbf{h}}_{0 k}\right)^{-1} ; k \in[K]\right)$.

We first analyze the LFSC case. By setting $a=1, \mathbf{m}=\mathbf{D}_{r}^{H} \widehat{\mathbf{h}}_{0}$, and $\mathbf{M}=\mathbf{D}_{r}^{H}\left(\widehat{\mathbf{H}} \widehat{\mathbf{H}}^{H}+\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{D}_{r}$ in Lemma 1 and using (62), we can obtain

$$
\begin{equation*}
\gamma^{\mathrm{lfsc}}=\frac{\left|\mathbf{g}^{H} \mathbf{G}_{\Delta_{I}}^{-1} \widetilde{\mathbf{g}}\right|^{2}}{\mathbf{g}^{H} \mathbf{G}_{\Delta_{I}}^{-1} \mathbf{G}_{\Delta} \mathbf{G}_{\Delta_{I}}^{-1} \mathbf{g}}, \tag{64}
\end{equation*}
$$

where

$$
\begin{align*}
\mathbf{g}^{H} & =\widehat{\mathbf{h}}_{0}^{H} \mathbf{Q} \mathbf{D}_{h, 0} \mathbf{L}, \widetilde{\mathbf{g}}^{H}=\widetilde{\mathbf{h}}_{0}^{H} \mathbf{Q} \mathbf{D}_{h, 0} \mathbf{L} \\
\mathbf{G}_{\Delta_{I}} & =\mathbf{L D}_{h, 0}^{H} \mathbf{Q}\left(\widehat{\mathbf{H}} \widehat{\mathbf{H}}^{H}+\mathbf{D}_{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{Q} \mathbf{D}_{h, 0} \mathbf{L} \\
\mathbf{G}_{\Delta} & =\mathbf{L} \mathbf{D}_{h, 0}^{H} \mathbf{Q}\left(\widetilde{\mathbf{H}} \widetilde{\mathbf{H}}^{H}+\mathbf{W}+\sigma^{2} \mathbf{I}_{N}\right) \mathbf{Q} \mathbf{D}_{h, 0} \mathbf{L} \tag{65}
\end{align*}
$$

It can be proved that $\|\mathbf{Q}\|=\sup _{k}\left\|\mathbf{Q}_{k}\right\| \leq \frac{1}{\min _{k} \rho_{k}}$ for $\rho_{k}>0$. According to Lemmas 2 and 3, we have

$$
\begin{aligned}
& {[\mathbf{g}]_{k}-\frac{\operatorname{Tr}\left[\boldsymbol{\Phi}_{0}\right]_{[k, k]} \boldsymbol{\Theta}_{k}}{N_{k}}=\frac{\widehat{\mathbf{h}}_{0 k}^{H} \mathbf{Q}_{k} \widehat{\mathbf{h}}_{0 k}}{N_{k}}-\frac{\operatorname{Tr}\left[\boldsymbol{\Phi}_{0}\right]_{[k, k]} \boldsymbol{\Theta}_{k}}{N_{k}}} \\
& =\frac{\mathbf{q}_{0}^{H}\left(\boldsymbol{\Phi}_{0 k}^{\frac{1}{2}}\right)^{H} \mathbf{Q}_{k} \boldsymbol{\Phi}_{0 k}^{\frac{1}{2}} \mathbf{q}_{0}}{N_{k}}-\frac{\operatorname{Tr}\left(\boldsymbol{\Phi}_{0 k}^{\frac{1}{2}}\right)^{H} \mathbf{Q}_{k} \boldsymbol{\Phi}_{0 k}^{\frac{1}{2}}}{N_{k}}
\end{aligned}
$$

$$
\begin{align*}
\bar{\Pi}_{k l, B}(\mathcal{A})= & {\left[\widetilde{\boldsymbol{\lambda}}_{B, B, k l}(\mathcal{A})-\widetilde{\boldsymbol{\lambda}}_{B, A, k l}(\mathcal{A}) \mathbf{D}_{A, B, l} \widetilde{\mathbf{F}}_{l}-\widetilde{\boldsymbol{\lambda}}_{A, B, k l}(\mathcal{A}) \mathbf{D}_{B, A, k} \widetilde{\mathbf{F}}_{k}\right] \mathbf{1}_{M} } \\
& +\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l}\left[\boldsymbol{\Lambda}_{B, B, k l}-\boldsymbol{\Lambda}_{B, A, k l} \mathbf{D}_{A, B, l} \widetilde{\mathbf{F}}_{l}-\boldsymbol{\Lambda}_{A, B, k l} \mathbf{D}_{B, A, k} \widetilde{\mathbf{F}}_{k}+\mathbf{D}_{B, A, k} \mathbf{D}_{A, B, l}\right] \mathbf{1}_{M} \tag{56}
\end{align*}
$$

$$
\begin{equation*}
+\frac{\operatorname{Tr}\left[\mathbf{\Phi}_{0}\right]_{[k, k]} \mathbf{Q}_{k}}{N_{k}}-\frac{\operatorname{Tr}\left[\mathbf{\Phi}_{0}\right]_{[k, k]} \mathbf{\Theta}_{k}}{N_{k}} \xrightarrow[{N \xrightarrow{c_{1}, \ldots, c_{K}}+} \infty]{\text { a.s. }} 0 \tag{66}
\end{equation*}
$$

where $\mathbf{q}_{0} \sim \mathcal{C} \mathcal{N}\left(0, \mathbf{I}_{N}\right)$ and $\boldsymbol{\Phi}_{0 k}^{\frac{1}{2}}=\boldsymbol{\Phi}_{0}^{\frac{1}{2}}\left[\boldsymbol{\varsigma}_{k},:\right] \in \mathbb{C}^{N_{k} \times N}$. Since $K$ is a given number, it holds true that $[\mathbf{g}]_{k}-[\mathbf{v}]_{k}$ converges to 0 almost surely for each $k \in[K]$. Similarly, we write

$$
\begin{align*}
{\left[\mathbf{G}_{\Delta}\right]_{k, l}=} & \frac{\widehat{\mathbf{h}}_{0 k}^{H} \mathbf{Q}_{k}\left([\mathbf{W}]_{[k, l]}+\sigma^{2} \mathbb{I}_{\{k=l\}} \mathbf{I}_{N_{k}}\right) \mathbf{Q}_{l} \widehat{\mathbf{h}}_{0 l}}{N_{k} N_{l}} \\
& +\frac{\widehat{\mathbf{h}}_{0 k}^{H} \mathbf{Q}_{k} \widetilde{\mathbf{H}}_{k} \widetilde{\mathbf{H}}_{l}^{H} \mathbf{Q}_{l} \widehat{\mathbf{h}}_{0 l}}{N_{k} N_{l}}=G_{k l, 1}+G_{k l, 2} \tag{67}
\end{align*}
$$

According to [34, Theorem 2], we can conclude that the spectral norm of matrix $\frac{1}{\sqrt{N_{k}}} \widetilde{\mathbf{H}}_{k}$ is bounded with probability 1 for each $k \in[K]$ such that the following holds almost surely

$$
\begin{equation*}
\sup _{N \geq 1}\left\|\frac{\mathbf{Q}_{k} \widetilde{\mathbf{H}}_{k} \widetilde{\mathbf{H}}_{l}^{H} \mathbf{Q}_{l}}{\sqrt{N_{k} N_{l}}}\right\| \leq \sup _{N \geq 1} \frac{\left\|\frac{\widetilde{\mathbf{H}}_{k}}{\sqrt{N_{k}}}\right\|\left\|\frac{\widetilde{\mathbf{H}}_{l}}{\sqrt{N_{l}}}\right\|}{\min _{k} \rho_{k}^{2}}<+\infty, \tag{68}
\end{equation*}
$$

for each $k, l \in[K]$. By Lemmas 2 and 3, the difference $\mathcal{D}_{G_{k l, 2}}= G_{k l, 2}-\frac{1}{\sqrt{N_{k} N_{l}}} \bar{\Pi}_{B, k l}\left(\left[\Phi_{0}\right]_{[l, k]}\right)$ can be written as

$$
\begin{align*}
\mathcal{D}_{G_{k l, 2}}= & G_{k l, 2}-\frac{\operatorname{Tr} \mathbf{Q}_{k} \widetilde{\mathbf{H}}_{k} \widetilde{\mathbf{H}}_{l}^{H} \mathbf{Q}_{l}\left[\boldsymbol{\Phi}_{0}\right]_{[l, k]}}{N_{k} N_{l}} \\
& +\frac{\operatorname{Tr} \mathbf{Q}_{k} \widetilde{\mathbf{H}}_{k} \widetilde{\mathbf{H}}_{l}^{H} \mathbf{Q}_{l}\left[\boldsymbol{\Phi}_{0}\right]_{[l, k]}}{N_{k} N_{l}}-\frac{\bar{\Pi}_{B, k l}\left(\left[\boldsymbol{\Phi}_{0}\right]_{[l, k]}\right)}{\sqrt{N_{k} N_{l}}}, \tag{69}
\end{align*}
$$

which converges to 0 almost surely. Following a similar derivation, we can prove $G_{k l, 1}$ converges almost surely to $\frac{1}{N_{k} N_{l}} \bar{\Upsilon}_{k l}\left(\left[\mathbf{\Phi}_{0}\right]_{[l, k]},\left[\mathbf{W}+\sigma^{2} \mathbf{I}_{N}\right]_{[k, l]}\right)$. Moreover, it can be shown that,

$$
\begin{array}{r}
{[\widetilde{\mathbf{g}}]_{k}-[\mathbf{v}]_{k} \xrightarrow[{N \xrightarrow{c_{1}, \ldots, c_{K}}+} \infty]{\text { a.s. }} 0,} \\
{\left[\mathbf{G}_{\Delta_{I}}\right]_{k, l}-\left[\boldsymbol{\Delta}_{I}\right]_{k, l} \xrightarrow[{N \xrightarrow{\text { a.s. }}}]{c_{1, \ldots, c_{K}}}+\infty}  \tag{71}\\
\hline
\end{array}
$$

for each $k, l \in[K]$. According to the continuous mapping theorem [35], we have

$$
\begin{equation*}
\gamma^{\text {lfsc }} \xrightarrow[{N \xrightarrow{c_{1}, \ldots, c_{K}}+} \infty]{\text { a.s. }} \bar{\gamma}^{\text {lfsc }}, \tag{72}
\end{equation*}
$$

which concludes (28b). The proof for (28a) an (28c) can be obtained similarly and is omitted here.

## B. Proof of the Approximation for the Mean

We analyze the LFOC case here and the other two cases are similar. By using the resolvent identity $\mathbf{A}-\mathbf{B}=\mathbf{A}\left(\mathbf{B}^{-1}-\right.$
$\left.\mathbf{A}^{-1}\right) \mathbf{B}$, we have

$$
\begin{align*}
\mathbf{G}_{\Delta}^{-1}= & \Delta^{-1}+\Delta^{-1}\left(\Delta-\mathbf{G}_{\Delta}\right) \Delta^{-1} \\
& +\mathbf{G}_{\Delta}^{-1}\left(\Delta-\mathbf{G}_{\Delta}\right) \Delta^{-1}\left(\Delta-\mathbf{G}_{\Delta}\right) \Delta^{-1} \tag{73}
\end{align*}
$$

According to the definition, $\gamma^{\text {lfoc }}$ can be rewritten as (74) shown at the bottom of this page. It can be proved that $\left|\mathbb{E} X_{j}\right|, j= 2,3, \ldots 9$ is of order $\mathcal{O}\left(N^{-1}\right)$ and we will evaluate $\left|\mathbb{E} X_{6}\right|$ in the following, as the remaining terms can be addressed using a similar method. To this end, we first prove the following bounds

$$
\begin{align*}
& \mathbb{E}\left|[\widetilde{\mathbf{g}}-\mathbf{v}]_{k}\right|^{2}=\mathcal{O}\left(\frac{1}{N}\right), \forall k \in[K]  \tag{75}\\
& \mathbb{E}\left|\left[\mathbf{G}_{\Delta}-\Delta\right]_{k, l}\right|^{2}=\mathcal{O}\left(\frac{1}{N}\right), \forall k, l \in[K] . \tag{76}
\end{align*}
$$

Denote $\mathscr{F}_{M}$ as the $\sigma$-algebra generated by $\mathbf{h}_{1}, \ldots, \mathbf{h}_{M}$ and

$$
\begin{equation*}
\underline{\mathbf{g}}_{k}=\mathbb{E}\left([\widetilde{\mathbf{g}}]_{k} \mid \mathscr{F}_{M}\right)=\frac{1}{N_{k}} \operatorname{Tr}\left[\boldsymbol{\Phi}_{0}\right]_{[k, k]} \mathbf{Q}_{k} . \tag{77}
\end{equation*}
$$

According to the triangle inequality, we have

$$
\begin{align*}
\mathbb{E}\left|[\widetilde{\mathbf{g}}-\mathbf{v}]_{k}\right|^{2} \leq & C\left(\mathbb{E}\left|[\widetilde{\mathbf{g}}]_{k}-\underline{\mathbf{g}}_{k}\right|^{2}+\mathbb{E}\left|\underline{\mathbf{g}}_{k}-\mathbb{E}[\underline{\mathbf{g}}]_{k}\right|^{2}\right. \\
& \left.+\left|\mathbb{E}[\underline{\mathbf{g}}]_{k}-[\mathbf{v}]_{k}\right|^{2}\right):=C\left(W_{1}+W_{2}+W_{3}\right), \tag{78}
\end{align*}
$$

where $C$ is a constant independent of $N$. By applying the trace lemma [36, Lemma 2.7], we have

$$
\begin{align*}
W_{1}= & \frac{\mathbb{E}\left[\mathbb{E}\left(\left|\widehat{\mathbf{h}}_{0 k}^{H} \mathbf{Q}_{k} \widetilde{\mathbf{h}}_{0 k}-\operatorname{Tr} \mathbf{Q}_{k}\left[\Phi_{0}\right]_{[k, k]}\right|^{2} \mid \mathscr{F}_{M}\right)\right]}{N_{k}^{2}} \\
& \leq \frac{C_{1}}{N_{k}} \mathbb{E}\left\|\mathbf{Q}_{k}\right\|^{2}=\mathcal{O}\left(\frac{1}{N}\right) \tag{79}
\end{align*}
$$

where $C_{1}$ is a constant. By using Poincaré-Nash inequality [37, Eq. (18)], we can get

$$
\begin{equation*}
W_{2}=\operatorname{Var}\left(\underline{\mathbf{g}}_{k}\right) \leq \mathcal{O}\left(\frac{1}{N^{2}}\right) \tag{80}
\end{equation*}
$$

Finally, by Lemma 3, we have $W_{3} \leq \mathcal{O}\left(\frac{1}{N^{3}}\right)$. Therefore, the dominant term on the RHS of (78) is $\mathcal{O}\left(N^{-1}\right)$ which proves (75). The bound (76) can be proved in a similar manner. Next, we evaluate the term $\left|\mathbb{E} X_{6}\right|$. By applying (75) and (76), bound (81) shown at the bottom of the next page can be derived, where step (a) follows from Cauchy-Schwartz inequality $\mathbb{E}|X Y| \leq \mathbb{E}^{\frac{1}{2}}|X|^{2} \mathbb{E}^{\frac{1}{2}}|Y|^{2}$. Therefore, Theorem 1 is proved.

$$
\begin{align*}
\gamma^{\text {lfoc }}= & \mathbf{v}^{H} \boldsymbol{\Delta}^{-1} \mathbf{v}+\mathbf{v}^{H} \boldsymbol{\Delta}^{-1}(\widetilde{\mathbf{g}}-\mathbf{v})+(\widetilde{\mathbf{g}}-\mathbf{v})^{H} \boldsymbol{\Delta}^{-1} \mathbf{v}+(\widetilde{\mathbf{g}}-\mathbf{v})^{H} \boldsymbol{\Delta}^{-1}(\widetilde{\mathbf{g}}-\mathbf{v})+\mathbf{v}^{H} \boldsymbol{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1} \mathbf{v} \\
& +\mathbf{v}^{H} \boldsymbol{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1}(\widetilde{\mathbf{g}}-\mathbf{v})+(\widetilde{\mathbf{g}}-\mathbf{v})^{H} \boldsymbol{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1} \mathbf{v}+(\widetilde{\mathbf{g}}-\mathbf{v})^{H} \boldsymbol{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1}(\widetilde{\mathbf{g}}-\mathbf{v}) \\
& +\widetilde{\mathbf{g}}^{H} \mathbf{G}_{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1} \widetilde{\mathbf{g}}:=\sum_{j=1}^{9} X_{j} \tag{74}
\end{align*}
$$

## Appendix D Proof of Corollary 1

Define $\mathbf{R}_{j}^{\mathcal{K}_{g}}, \mathbf{D}_{\tilde{\sigma}}^{\mathcal{K}_{g}}, \mathbf{D}_{R, j}^{\mathcal{K}_{g}}, \mathbf{T}_{j}^{\mathcal{K}_{g}}, \mathbf{D}_{T, j}^{\mathcal{K}_{g}}, \boldsymbol{\Phi}_{j}^{\mathcal{K}_{g}}, \mathbf{V}_{j}^{\mathcal{K}_{g}}, \mathbf{W}_{j}^{\mathcal{K}_{g}}$, and $\mathbf{W}^{\mathcal{K}_{g}}$ as the matrices obtained by considering the channel $\mathbf{h}_{j}{ }^{\mathcal{K}_{g}}$ in (11) and (12) for each $j \in[M]_{0}$. Denote the asymptotic regime $\widetilde{\sigma}_{e}^{2} \rightarrow+\infty$ as $\widetilde{\sigma}_{k}^{2} \rightarrow+\infty$ for each $k \in \mathcal{K}_{e}$ with equal value $\widetilde{\sigma}_{k}^{2}= \widetilde{\sigma}_{e}^{2}$. To prove Corollary 1, it is sufficient to show

1) $\left[\mathbf{R}^{\mathcal{K}_{g}}\right]_{[a, b]} \rightarrow[\mathbf{R}]_{\left[k_{a}, k_{b}\right]}$, for $a, b \in[G]$ as $\widetilde{\sigma}_{e}^{2} \rightarrow+\infty$. Here, $\mathbf{R}$ is one of

$$
\begin{equation*}
\left\{\boldsymbol{\Phi}_{j}, \mathbf{V}_{j} \boldsymbol{\Phi}_{j}, \mathbf{V}_{j} \boldsymbol{\Phi}_{j} \mathbf{V}_{j}^{H}\right\}_{j=0}^{M} \cup\left\{\mathbf{W}, \mathbf{D}_{W}\right\} \tag{82}
\end{equation*}
$$

2) $\left[\boldsymbol{\Phi}_{j}\right]_{[x, y]} \rightarrow 0$ as $\widetilde{\sigma}_{e}^{2} \rightarrow+\infty$, for one of $x$ or $y$ that belongs to $\mathcal{K}_{e}$.
Here, $\left[\mathbf{R}_{j}^{\mathcal{K}_{g}}\right]_{[a, b]}$ is the submatrix obtained by partitioning the rows and columns based on $\mathbf{h}_{j}^{\mathcal{K}_{g}}$, with a size of $k_{a} \times k_{b}$. Thus, we have $\left[\mathbf{R}_{j}^{\mathcal{K}_{g}}\right]_{[a, b]}=\left[\mathbf{R}_{j}\right]_{\left[k_{a}, k_{b}\right]}$ and $\left[\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}\right]_{[a, a]}=\widetilde{\sigma}_{k_{a}}^{2} \mathbf{I}_{N_{k_{a}}}$ for each $a, b \in[G]$.

We prove item 1) first. We only prove the case with $\mathbf{R}=\mathbf{W}$ as the proofs for the other terms are similar. For $a, b \in[G]$, we have

$$
\begin{align*}
{\left[\mathbf{W}_{j}\right]_{\left[k_{a}, k_{b}\right]} } & =\left[\mathbf{R}_{j}\left(\mathbf{D}_{\widetilde{\sigma}}+\mathbf{R}_{j}\right)^{-1} \mathbf{D}_{\widetilde{\sigma}}\right]_{\left[k_{a}, k_{b}\right]} \\
& =\widetilde{\sigma}_{k_{b}}^{2}\left[\mathbf{R}_{j}\left(\mathbf{D}_{\widetilde{\sigma}}+\mathbf{R}_{j}\right)^{-1}\right]_{\left[k_{a}, k_{b}\right]} \tag{83}
\end{align*}
$$

Without loss of generality, assume $k_{a}=a$ for $a \in[G]$ and write

$$
\mathbf{R}_{j}=\left[\begin{array}{ll}
\mathbf{R}_{j}^{\mathcal{K}_{g}} & \mathbf{R}_{j, 1}  \tag{84}\\
\mathbf{R}_{j, 2} & \mathbf{R}_{j, 3}
\end{array}\right], \mathbf{D}_{\widetilde{\sigma}}=\left[\begin{array}{cc}
\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}} & \mathbf{0} \\
\mathbf{0} & \mathbf{D}_{\widetilde{\sigma}, 1}
\end{array}\right] .
$$

According to the block matrix inversion formula [38], we can get

$$
\left(\mathbf{D}_{\widetilde{\sigma}}+\mathbf{R}_{j}\right)^{-1}=\left[\begin{array}{ll}
\mathbf{P}_{1} & \mathbf{P}_{2}  \tag{85}\\
\mathbf{P}_{3} & \mathbf{P}_{4}
\end{array}\right],
$$

where terms $\mathbf{P}_{t}, t=2,3,4$ approach $\mathbf{0}$ as $\widetilde{\sigma}_{e}^{2} \rightarrow+\infty$, and the term

$$
\begin{align*}
\mathbf{P}_{1}= & \left(\mathbf{R}_{j}^{\mathcal{K}_{g}}+\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}-\mathbf{R}_{j, 2}\left(\mathbf{R}_{j, 3}+\mathbf{D}_{\widetilde{\sigma}, 1}\right)^{-1} \mathbf{R}_{j, 1}\right)^{-1} \\
& \rightarrow\left(\mathbf{R}_{j}^{\mathcal{K}_{g}}+\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}\right)^{-1}, \text { as } \widetilde{\sigma}_{e}^{2} \rightarrow+\infty \tag{86}
\end{align*}
$$

Hence, by (83), the following holds
$\lim _{\widetilde{\sigma}_{e}^{2} \rightarrow+\infty}\left[\mathbf{W}_{j}\right]_{\left[k_{a}, k_{b}\right]}=\widetilde{\sigma}_{k_{b}}^{2}\left[\left[\begin{array}{ll}\mathbf{R}_{j}^{\mathcal{K}_{g}}\left(\mathbf{R}_{j}^{\mathcal{K}_{g}}+\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}\right)^{-1} & \mathbf{0} \\ \mathbf{R}_{j, 2}\left(\mathbf{R}_{j}^{\mathcal{K}_{g}}+\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}\right)^{-1} & \mathbf{0}\end{array}\right]\right]_{\left[k_{a}, k_{b}\right]}$

$$
\begin{equation*}
=\left[\mathbf{R}_{j}^{\mathcal{K}_{g}}\left(\mathbf{R}_{j}^{\mathcal{K}_{g}}+\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}\right)^{-1}\right]_{[a, b]}\left[\mathbf{D}_{\widetilde{\sigma}}^{\mathcal{K}_{g}}\right]_{[b, b]}=\left[\mathbf{W}_{j}^{\mathcal{K}_{g}}\right]_{[a, b]} . \tag{87}
\end{equation*}
$$

By summing over the index $j$ in above equation, we get $\lim _{\widetilde{\sigma}_{e}^{2} \rightarrow+\infty}[\mathbf{W}]_{\left[k_{a}, k_{b}\right]}=\left[\mathbf{W}^{\mathcal{K}_{g}}\right]_{[a, b]}$. Therefore, item 1) is proved.

Next, we prove item 2). Without loss of generality, we assume $x \in \mathcal{K}_{e}$. As a result,

$$
\begin{equation*}
\left[\mathbf{D}_{T, j}\right]_{[x, x]}=\left[\mathbf{R}_{j}\right]_{[x, x]}\left(\widetilde{\sigma}_{x}^{2} \mathbf{I}_{N_{x}}+\left[\mathbf{R}_{j}\right]_{[x, x]}\right)^{-1} \rightarrow \mathbf{0} \tag{88}
\end{equation*}
$$

as $\widetilde{\sigma}_{e}^{2} \rightarrow+\infty$. Hence, we have

$$
\begin{equation*}
\left[\boldsymbol{\Phi}_{j}\right]_{[x, y]}=\left[\mathbf{D}_{T, j}\right]_{[x, x]}\left[\left(\mathbf{D}_{\widetilde{\sigma}}+\mathbf{R}_{j}\right) \mathbf{D}_{T, j}\right]_{[x, y]} \rightarrow \mathbf{0} \tag{89}
\end{equation*}
$$

Therefore, we complete the proof of Corollary 1.

## Appendix E <br> Proof of Lemma 3

The proof relies on Gaussian tools [19], [37], [39], [40], [41], which consist of the integration by parts formula [37, Eq. (17)] and the Poincaré-Nash inequality [37, Eq. (18)]. According to the Poincaré-Nash inequality, the variance of functions defined in Table II can be proved of order $\mathcal{O}(1)$ (See [34, Lemma 9] for the case of $\digamma_{k}$ and the proof of other functions are similar). As a result, for given $\epsilon>0$, we have

$$
\begin{equation*}
\sum_{N=1}^{+\infty} \mathbb{P}\left(\frac{|\mathcal{X}-\mathbb{E} \mathcal{X}|}{N} \geq \epsilon\right) \leq \sum_{N=1}^{+\infty} \frac{\operatorname{Var}(\mathcal{X})}{\epsilon^{2} N^{2}}<+\infty \tag{90}
\end{equation*}
$$

where $\mathcal{X}$ can be any function in Table II. Thus, according to Borel-Cantelli lemma, we have

$$
\begin{equation*}
\frac{\mathcal{X}-\mathbb{E} \mathcal{X}}{N} \xrightarrow[{N \xrightarrow{c_{1}, \ldots, c_{K}}+} \infty]{\text { a.s. }} 0 \tag{91}
\end{equation*}
$$

Therefore, to show the stochastic equivalence, we only need to evaluate the means of functions in Table II.

## A. Evaluation of $\mathbb{E} \digamma_{k}$

Before delving into the details of the proof, we first define the following quantities

$$
\begin{align*}
& \alpha_{j k}=\frac{1}{N_{k}} \operatorname{Tr}\left[\boldsymbol{\Omega}_{j}\right]_{[k, k]} \mathbf{Q}_{k}, \mathbf{D}_{\alpha, k}=\operatorname{diag}\left(\alpha_{j k} ; j \in[M]\right) \\
& \widetilde{\mathbf{F}}_{\alpha, k}=\left(\mathbf{I}+\mathbb{E} \mathbf{D}_{\alpha, k}\right)^{-1} \\
& \boldsymbol{\Theta}_{\alpha, k}=\left(-z_{k} \mathbf{I}_{N_{k}}+\mathbf{S}_{k}+\frac{1}{N_{k}} \sum_{j=1}^{M} \frac{\left[\boldsymbol{\Omega}_{j}\right]_{[k, k]}}{1+\underline{\alpha}_{j k}}\right)^{-1} \tag{92}
\end{align*}
$$

$$
\begin{align*}
\left|\mathbb{E} X_{6}\right| & =\left|\mathbb{E} \mathbf{v}^{H} \boldsymbol{\Delta}^{-1}\left(\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right) \boldsymbol{\Delta}^{-1}(\widetilde{\mathbf{g}}-\mathbf{v})\right|=\left|\mathbb{E} \sum_{i_{1}, i_{2}, i_{3}, i_{4} \in[K]}\left[\mathbf{v}^{H} \boldsymbol{\Delta}^{-1}\right]_{i_{1}}\left[\boldsymbol{\Delta}^{-1}\right]_{i_{1}, i_{2}}\left[\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right]_{i_{2}, i_{3}}\left[\boldsymbol{\Delta}^{-1}\right]_{i_{3}, i_{4}}[\widetilde{\mathbf{g}}-\mathbf{v}]_{i_{4}}\right| \\
& \stackrel{(a)}{\leq} \sum_{i_{1}, i_{2}, i_{3}, i_{4} \in[K]}\left|\left[\mathbf{v}^{H} \boldsymbol{\Delta}^{-1}\right]_{i_{1}}\left[\boldsymbol{\Delta}^{-1}\right]_{i_{1}, i_{2}}\left[\boldsymbol{\Delta}^{-1}\right]_{i_{3}, i_{4}}\right| \mathbb{E}^{\frac{1}{2}}\left|\left[\boldsymbol{\Delta}-\mathbf{G}_{\Delta}\right]_{i_{2}, i_{3}}\right|^{2} \mathbb{E}^{\frac{1}{2}}\left|[\widetilde{\mathbf{g}}-\mathbf{v}]_{i_{4}}\right|^{2}=\mathcal{O}\left(\frac{1}{N}\right) \tag{81}
\end{align*}
$$

These quantities will serve as intermediate variables in the proof, i.e., we will show $\mathbf{Q}_{k} \approx \Theta_{\alpha, k} \approx \Theta_{k}$.

Applying integration by parts formula to $\mathbb{E}\left[\mathbf{Q}_{k}\right]_{i, p}\left[\mathbf{x}_{s}\right]_{a}\left[\mathbf{Y}_{l}\right]_{j, s}^{*}$ and taking $\left[\mathbf{x}_{s}\right]_{a}$ as the variable, we have

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Q}_{k}\right]_{i, p}\left[\mathbf{x}_{s}\right]_{a}\left[\mathbf{Y}_{l}\right]_{j, s}^{*}=\mathbb{E} \frac{\partial\left[\mathbf{Q}_{k}\right]_{i, p}\left[\mathbf{Y}_{l}\right]_{j, s}^{*}}{\partial\left[\mathbf{x}_{s}\right]_{a}^{*}} \\
= & \mathbb{E}-\frac{1}{\sqrt{N_{k}}}\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{A}_{s k}^{H} \mathbf{Q}_{k}\right]_{a, p}\left[\mathbf{Y}_{l}\right]_{j, s}^{*} \\
& +\mathbb{E} \frac{1}{\sqrt{N_{l}}}\left[\mathbf{Q}_{k}\right]_{i, p}\left[\mathbf{B}_{s l}^{H}\right]_{a, j} \tag{93}
\end{align*}
$$

Multiplying $\frac{1}{\sqrt{N_{k}}}\left[\mathbf{A}_{s k}\right]_{p, a}$ at both sides of (93) and summing over the subscripts $p$ and $a$, the following holds

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{Y}_{l}\right]_{j, s}^{*}=\mathbb{E} \frac{\left[\mathbf{Q}_{k} \mathbf{A}_{s k} \mathbf{B}_{s l}^{H}\right]_{i, j}}{\sqrt{N_{k} N_{l}}} \\
& -\mathbb{E} \alpha_{s k}\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{Y}_{l}\right]_{j, s}^{*} \tag{94}
\end{align*}
$$

By writing the random variable $\alpha_{s k}$ as the sum of its mean and its centered version, i.e., $\alpha_{s k}=\underline{\alpha}_{s k}+\stackrel{\circ}{\alpha}_{s k}$ and solving (94) w.r.t. $\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{Y}_{l}\right]_{j, s}^{*}$, we get

$$
\begin{align*}
\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{Y}_{l}\right]_{j, s}^{*}= & \mathbb{E} \frac{\left[\mathbf{Q}_{k} \mathbf{A}_{s k} \mathbf{B}_{s l}^{H}\right]_{i, j}}{\sqrt{N_{k} N_{l}}\left(1+\underline{\alpha}_{s k}\right)} \\
& -\mathbb{E} \frac{\stackrel{\circ}{\alpha}_{s k}}{1+\underline{\alpha}_{s k}}\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{Y}_{l}\right]_{j, s}^{*} \tag{95}
\end{align*}
$$

Equation (95) will also be used for the evaluation of $\mathbb{E} \Phi_{B, k l}$ later. To obtain the approximation of the trace of the resolvent, we set $l=k$ and $\mathbf{Y}_{k}=\mathbf{X}_{k}$, i.e., $\mathbf{B}_{s}=\mathbf{A}_{s}, \forall s \in[M]$. By summing over the subscript $s$, we can obtain

$$
\begin{align*}
\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k} \mathbf{X}_{k}^{H}\right]_{i, j}= & \mathbb{E}\left[\mathbf{Q}_{k} \sum_{s=1}^{M} \frac{\left[\boldsymbol{\Omega}_{s}\right]_{[k, k]}}{N_{k}\left(1+\underline{\alpha}_{s k}\right)}\right]_{i, j} \\
& -\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k} \stackrel{\circ}{\mathbf{D}}_{\alpha, k} \widetilde{\mathbf{F}}_{\alpha, k} \mathbf{X}_{k}^{H}\right]_{i, j} . \tag{96}
\end{align*}
$$

By using the resolvent identity $\mathbf{Q}_{k} \mathbf{X}_{k} \mathbf{X}_{k}^{H}=z_{k} \mathbf{Q}_{k}-\mathbf{Q}_{k} \mathbf{S}_{k}+ \mathbf{I}_{N_{k}}$ on $\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k} \mathbf{X}_{k}^{H}\right]_{i, j}$, multiplying both sides $\left[\boldsymbol{\Theta}_{\alpha, k} \mathcal{A}\right]_{j, i}$, and summing over the subscripts $i$ and $j$, we can get

$$
\begin{align*}
& \mathbb{E} \operatorname{Tr} \mathcal{A} \mathbf{Q}_{k}-\operatorname{Tr} \mathcal{A} \boldsymbol{\Theta}_{\alpha, k} \\
& =\mathbb{E} \operatorname{Tr} \mathbf{Q}_{k} \mathbf{X}_{k} \stackrel{\circ}{\mathbf{D}}{ }_{\alpha, k} \widetilde{\mathbf{F}}_{\alpha, k} \mathbf{X}_{k}^{H} \boldsymbol{\Theta}_{\alpha, k} \mathcal{A}:=\varepsilon_{k}(\mathcal{A}) \tag{97}
\end{align*}
$$

We can write the residual term $\varepsilon_{k}(\mathcal{A})$ as

$$
\begin{align*}
\varepsilon_{k}(\mathcal{A}) & =\sum_{j=1}^{M} \mathbb{E} \stackrel{\circ}{\alpha}_{j k} \underbrace{\left[\widetilde{\mathbf{F}}_{\alpha, k} \mathbf{X}_{k}^{H} \boldsymbol{\Theta}_{\alpha, k} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k}\right]_{j, j}}_{:=\chi_{j k}} \\
& \stackrel{(a)}{\leq} \sum_{j=1}^{M} \operatorname{Var}^{\frac{1}{2}}\left(\alpha_{j k}\right) \operatorname{Var}^{\frac{1}{2}}\left(\chi_{j k}\right) \stackrel{(b)}{=} \mathcal{O}\left(\frac{1}{N^{\frac{1}{2}}}\right) \tag{98}
\end{align*}
$$

where step (a) follows from Cauchy-Schwartz inequality. Step (b) follows from the fact $\operatorname{Var}\left(\alpha_{j k}\right)=\mathcal{O}\left(\frac{1}{N^{2}}\right)$ and $\operatorname{Var}\left(\chi_{j k}\right)= \mathcal{O}\left(\frac{1}{N}\right)$, which can be proved by Poincaré-Nash inequality. Hence, we build the relation between $\mathbf{Q}_{k}$ and $\boldsymbol{\Theta}_{\alpha, k}$.

To establish the relationship between $\boldsymbol{\Theta}_{\alpha, k}$ and $\boldsymbol{\Theta}_{k}$, we take the difference between $\frac{1}{N_{k}} \operatorname{Tr}\left[\boldsymbol{\Omega}_{j}\right]_{[k, k]} \boldsymbol{\Theta}_{\alpha, k}$ and $\delta_{j k}$ for each $j \in [M]$. Following the same procedure as in the proof of [34, Proposition 3], we can show that $\left|\operatorname{Tr} \mathcal{A} \Theta_{k}-\operatorname{Tr} \mathcal{A} \Theta_{\alpha, k}\right|=\mathcal{O}\left(N^{-\frac{1}{2}}\right)$, which concludes (53).

## B. Evaluation of $\mathbb{E} \Phi_{B, k l}$

Multiplying $[\mathbf{b}]_{s}$ and $[\boldsymbol{\mathcal { A }}]_{j, i}$ at both sides of (95) and summing over the subscripts $s, i$, and $j$, we can obtain

$$
\begin{align*}
& \mathbb{E} \Phi_{B, k l}(\mathcal{A}, \mathbf{b})=-\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k} \operatorname{diag}(\mathbf{b}) \stackrel{\circ}{\mathbf{D}}_{\alpha, k} \widetilde{\mathbf{F}}_{\alpha, k} \mathbf{Y}_{l}^{H}\right] \\
& +\sum_{s} \frac{[\mathbf{b}]_{s} \operatorname{Tr} \mathcal{A}\left(\mathbb{E} \mathbf{Q}_{k}\right) \mathbf{A}_{s k} \mathbf{B}_{s l}^{H}}{\sqrt{N_{k} N_{l}}\left(1+\underline{\alpha}_{s k}\right)} \\
& \stackrel{(a)}{=} \sum_{s} \frac{[\mathbf{b}]_{s} \operatorname{Tr} \mathcal{A} \Theta_{k} \mathbf{A}_{s k} \mathbf{B}_{s l}^{H}}{\sqrt{N_{k} N_{l}}\left(1+\delta_{s k}\right)}+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \tag{99}
\end{align*}
$$

where step (a) follows from (53) and the variance control.

## C. Evaluation of $\mathbb{E} \Upsilon_{k l}$

According to integration by parts formula, we get

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Q}_{k} \mathcal{B} \mathbf{Q}_{l} \mathbf{X}_{l}\right]_{i, s}\left[\mathbf{X}_{l}\right]_{j, s}^{*}=\mathbb{E} \frac{\left[\mathbf{Q}_{k} \mathcal{B} \mathbf{Q}_{l}\left[\boldsymbol{\Omega}_{s}\right]_{[l, l]}\right]_{i, j}}{N_{l}\left(1+\underline{\alpha}_{s l}\right)} \\
& -\mathbb{E} \frac{\stackrel{\circ}{\alpha}_{s l}}{1+\underline{\alpha}_{s l}}\left[\mathbf{Q}_{k} \mathcal{B} \mathbf{Q}_{l} \mathbf{X}_{l}\right]_{i, s}\left[\mathbf{X}_{l}\right]_{j, s}^{*} \\
& -\frac{\mathbb{E} \Upsilon_{k l}\left(\left[\boldsymbol{\Omega}_{s}\right]_{[l, k]}, \mathcal{B}\right)\left[\mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, s}\left[\mathbf{X}_{l}\right]_{j, s}^{*}}{\sqrt{N_{l} N_{k}}\left(1+\underline{\alpha}_{s l}\right)} \tag{100}
\end{align*}
$$

Summing over the subscript $s$ and using the resolvent identity $\mathbf{Q}_{l} \mathbf{X}_{l} \mathbf{X}_{l}^{H}=z_{l} \mathbf{Q}_{l}-\mathbf{Q}_{l} \mathbf{S}_{l}+\mathbf{I}_{N_{l}}$, the following holds

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Q}_{k} \mathcal{B} \mathbf{Q}_{l} \boldsymbol{\Theta}_{\alpha, l}^{-1}\right]_{i, j}=\mathbb{E}\left[\mathbf{Q}_{k} \mathcal{B}\right]_{i, j} \\
& +\mathbb{E}\left[\mathbf{Q}_{k} \mathbf{X}_{k} \mathbf{D}_{\Upsilon, k l}(\mathcal{B}) \widetilde{\mathbf{F}}_{\alpha, l} \mathbf{X}_{l}^{H}\right]_{i, j}+\left[\varepsilon_{k l}\right]_{i, j} \tag{101}
\end{align*}
$$

where $\quad \mathbf{D}_{\Upsilon, k l}(\boldsymbol{\mathcal { B }})=\frac{1}{\sqrt{N_{k} N_{l}}} \operatorname{diag}\left(\Upsilon_{k l}\left(\left[\boldsymbol{\Omega}_{s}\right]_{[l, k]}, \mathcal{B}\right) ; s \in[M]\right)$ and $\varepsilon_{k l}$ is the residual matrix. It can be proved by Poincaré-Nash inequality that $\operatorname{Tr} \varepsilon \mathcal{C}=\mathcal{O}\left(N^{-\frac{1}{2}}\right)$ for any $\mathcal{C}$ with bounded spectral norm. Thus, we have

$$
\begin{align*}
& \mathbb{E} \Upsilon_{k l}(\mathcal{A}, \mathcal{B})=\operatorname{Tr} \mathcal{A}\left(\mathbb{E} \mathbf{Q}_{k}\right) \mathcal{B} \Theta_{\alpha, l} \\
& +\mathbb{E} \operatorname{Tr} \mathbf{Q}_{k} \mathbf{X}_{k} \mathbf{D}_{\Upsilon, k l}(\mathcal{B}) \widetilde{\mathbf{F}}_{\alpha, l} \mathbf{X}_{l}^{H} \Theta_{\alpha, l} \mathcal{A}+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \tag{102}
\end{align*}
$$

By replacing $\boldsymbol{\Theta}_{\alpha, l}$ and $\widetilde{\mathbf{F}}_{\alpha, l}$ with $\boldsymbol{\Theta}_{l}$ and $\widetilde{\mathbf{F}}_{l}$, respectively, setting $\mathcal{A}=\left[\boldsymbol{\Omega}_{u}\right]_{[l, k]}$ and $\mathcal{B}=\left[\boldsymbol{\Omega}_{v}\right]_{[k, l]}$, and using the approximation rules of $\Phi_{B, k l}$ in (54), we have

$$
\begin{align*}
& {\left[\boldsymbol{\Upsilon}_{\Omega, k l}\right]_{u, v}=N_{k} N_{l}\left[\boldsymbol{\Gamma}_{k l}\right]_{u, v}} \\
& +\sum_{j=1}^{M}\left[\boldsymbol{\Upsilon}_{\Omega, k l}\right]_{j, v}\left[\widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l}\right]_{j, j}\left[\boldsymbol{\Gamma}_{k l}\right]_{u, j}+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \tag{103}
\end{align*}
$$

where $\left[\boldsymbol{\Upsilon}_{\Omega, k l}\right]_{u, v}=\mathbb{E} \operatorname{Tr}\left[\boldsymbol{\Omega}_{u}\right]_{[l, k]} \mathbf{Q}_{k}\left[\boldsymbol{\Omega}_{v}\right]_{[k, l]} \mathbf{Q}_{l}$. Solving (103) w.r.t. $\Upsilon_{\Omega, k l}$, we get

$$
\begin{equation*}
\mathbf{\Upsilon}_{\Omega, k l}=N_{k} N_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Gamma}_{k l}+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \mathbf{1}_{M} \mathbf{1}_{M}^{T} \tag{104}
\end{equation*}
$$

$$
\begin{align*}
& \mathbb{E} \Pi_{B, k l}(\mathcal{A})=\sum_{i=1}^{M}\left\{\left[\widetilde{\boldsymbol{\lambda}}_{B, B, k l}(\mathcal{A})+\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Lambda}_{B, B, k l}-\left[\mathbf{D}_{A, B, l} \widetilde{\mathbf{F}}_{l}\right]_{i, i}\left(\widetilde{\boldsymbol{\lambda}}_{B, A, k l}(\mathcal{A})+\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Lambda}_{B, A, k l}\right)\right.\right. \\
& \left.\left.-\left[\mathbf{D}_{B, A, k} \widetilde{\mathbf{F}}_{k}\right]_{i, i}\left(\widetilde{\boldsymbol{\lambda}}_{A, B, k l}(\mathcal{A})+\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Lambda}_{A, B, k l}\right)\right] \mathbf{e}_{i}+\left[\mathbf{D}_{B, A, k} \mathbf{D}_{A, B, l} \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l}\right]_{i, i}\left[\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\boldsymbol{\Xi}}_{k l}\right]_{i}\right\}+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \\
& \stackrel{(a)}{=}\left(\widetilde{\boldsymbol{\lambda}}_{B, B, k l}(\mathcal{A})+\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Lambda}_{B, B, k l}-\widetilde{\boldsymbol{\lambda}}_{B, A, k l}(\mathcal{A}) \mathbf{D}_{A, B, l} \widetilde{\mathbf{F}}_{l}-\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Lambda}_{B, A, k l} \mathbf{D}_{A, B, l} \widetilde{\mathbf{F}}_{l}\right. \\
& \left.-\widetilde{\boldsymbol{\lambda}}_{A, B, k l}(\mathcal{A}) \mathbf{D}_{B, A, k} \widetilde{\mathbf{F}}_{k}-\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Lambda}_{A, B, k l} \mathbf{D}_{B, A, k} \widetilde{\mathbf{F}}_{k}+\widetilde{\boldsymbol{\lambda}}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \mathbf{D}_{B, A, k} \mathbf{D}_{A, B, l}\right) \mathbf{1}_{M}+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \tag{109}
\end{align*}
$$

By following the similar method as in [34], we can show that $\mathbf{I}_{M}-\boldsymbol{\Gamma}_{k l} \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l}$ is invertible and $\max _{i \in[M]} \sum_{j=1}^{M}\left|\left[\boldsymbol{\Xi}_{k l}\right]_{i, j}\right|= \mathcal{O}(1)$. Due to the space limitation, we omit the details. Similar to the evaluation of $\Upsilon_{\Omega, k l}$, we can derive the approximation rules for $\mathbb{E} \Upsilon_{k l}\left(\mathcal{A},\left[\boldsymbol{\Omega}_{v}\right]_{[k, l]}\right)$ and $\mathbb{E} \Upsilon_{k l}\left(\left[\boldsymbol{\Omega}_{u}\right]_{[l, k]}, \mathcal{B}\right)$. Plugging these results in (102) yields

$$
\begin{align*}
& \mathbb{E} \operatorname{Tr} \mathcal{A} \mathbf{Q}_{k} \mathcal{B} \mathbf{Q}_{l}=\operatorname{Tr} \mathcal{A} \Theta_{k} \mathcal{B} \Theta_{l} \\
& +\widetilde{\lambda}_{k l}(\mathcal{A}) \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \Xi_{k l} \lambda_{k l}(\mathcal{B})+\mathcal{O}\left(N^{-\frac{1}{2}}\right) \tag{105}
\end{align*}
$$

which proves (55).

## D. Evaluation of $\mathbb{E} \Pi_{B, k l}$

By applying integration by parts formula, we can obtain

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k}\right]_{i, p}\left[\mathbf{Y}_{k}\right]_{p, i}=\mathbb{E}\left\{\frac{\left[\mathbf{B}_{i k} \mathbf{B}_{i l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k}\right]_{p, p}}{\sqrt{N_{k} N_{l}}}\right. \\
& -\frac{1}{\sqrt{N_{k} N_{l}}}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathbf{X}_{l}\right]_{i, i}\left[\mathbf{B}_{i k} \mathbf{A}_{i l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k}\right]_{p, p} \\
& \left.-\frac{1}{N_{k}}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, i}\left[\mathbf{B}_{i k} \mathbf{A}_{i k}^{H} \mathbf{Q}_{k}\right]_{p, p}\right\} \tag{106}
\end{align*}
$$

Summing over the subscript $p$, and using the variance control and the approximation rules for $\Upsilon_{k l}$, we get

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k} \mathbf{Y}_{k}\right]_{i, i}=\frac{\bar{\Upsilon}_{k l}\left(\mathcal{A}, \mathbf{B}_{i k} \mathbf{B}_{i l}^{H}\right)}{\sqrt{N_{k} N_{l}}} \\
& -\frac{\bar{\Upsilon}_{k l}\left(\mathcal{A}, \mathbf{B}_{i k} \mathbf{A}_{i l}^{H}\right)}{\sqrt{N_{k} N_{l}}} \mathbb{E}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathbf{X}_{l}\right]_{i, i} \\
& -\mathbb{E}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, i} \frac{\operatorname{TrB}_{i k} \mathbf{A}_{i k}^{H} \boldsymbol{\Theta}_{k}}{N_{k}}+\mathcal{O}\left(N^{-\frac{3}{2}}\right) \tag{107}
\end{align*}
$$

Similarly, we can obtain

$$
\begin{align*}
& \mathbb{E}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathcal{A} \mathbf{Q}_{k} \mathbf{X}_{k}\right]_{i, i}=\frac{\bar{\Upsilon}_{k l}\left(\mathcal{A}, \mathbf{A}_{i k} \mathbf{B}_{i l}^{H}\right)}{\sqrt{N_{k} N_{l}}\left(1+\delta_{i k}\right)} \\
& -\frac{\bar{\Upsilon}_{k l}\left(\mathcal{A},\left[\boldsymbol{\Omega}_{i}\right]_{[k, l]}\right)}{\sqrt{N_{k} N_{l}}\left(1+\delta_{i k}\right)} \mathbb{E}\left[\mathbf{Y}_{l}^{H} \mathbf{Q}_{l} \mathbf{X}_{l}\right]_{i, i}+\mathcal{O}\left(N^{-\frac{3}{2}}\right) \tag{108}
\end{align*}
$$

Then, plugging (108) into (107), summing over the subscript $i$ and using the approximation rules for $\Phi_{B, k l}$ in (54), we get (109) at the top of this page, where $\widetilde{\Xi}_{k l}=\mathbf{I}_{M}+ \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l} \boldsymbol{\Gamma}_{k l}$, and step (a) in (109) follows by the identity
$\widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l} \boldsymbol{\Xi}_{k l}=\widetilde{\boldsymbol{\Xi}}_{k l} \widetilde{\mathbf{F}}_{k} \widetilde{\mathbf{F}}_{l}$. Therefore, we complete the proof of Lemma 3.

## References

[1] L. Lu, G. Y. Li, A. L. Swindlehurst, A. Ashikhmin, and R. Zhang, "An overview of massive MIMO: Benefits and challenges," IEEE J. Sel. Topics Signal Process., vol. 8, no. 5, pp. 742-758, Oct. 2014.
[2] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
[3] L. Van der Perre, L. Liu, and E. G. Larsson, "Efficient DSP and circuit architectures for massive MIMO: State of the art and future directions," IEEE Trans. Signal Process., vol. 66, no. 18, pp. 4717-4736, Sep. 2018.
[4] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE Trans. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[5] Y. Xu, E. G. Larsson, E. A. Jorswieck, X. Li, S. Jin, and T.-H. Chang, "Distributed signal processing for extremely large-scale antenna array systems: State-of-the-art and future directions," IEEE J. Sel. Topics Signal Process. (Early Access), pp. 1-526, 2025.
[6] K. Li, Y. Chen, R. Sharan, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized data detection for massive MU-MIMO on a Xeon Phi cluster," in Proc. Conf. Rec. 50th Asilomar Conf. Signals, Syst. Comput., 2016, pp. 468-472.
[7] J. Rodríguez Sánchez, F. Rusek, O. Edfors, M. Sarajlić, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms," IEEE Trans. Signal Process., vol. 68, pp. 687-700, 2020.
[8] K. Li et al., "Design trade-offs for decentralized baseband processing in massive MU-MIMO systems," in Proc. Conf. Rec. 53rd Asilomar Conf. Signals, Syst. Comput., 2019, pp. 906-912.
[9] Y. Dong, H. Li, C. Gong, X. Wang, and X. Dai, "An enhanced fully decentralized detector for the uplink M-MIMO system," IEEE Trans. Veh. Technol., vol. 71, no. 12, pp. 13030-13042, Dec. 2022.
[10] X. Zhou, L. Liang, J. Zhang, C.-K. Wen, and S. Jin, "Mini-batch gradientbased MCMC for decentralized massive MIMO detection," IEEE Trans. Commun., vol. 73, no. 1, pp. 677-692, Jan. 2025.
[11] K. Li, C. Jeon, J. R. Cavallaro, and C. Studer, "Decentralized equalization for massive MU-MIMO on FPGA," in Proc. Conf. Rec. 51st Asilomar Conf. Signals, Syst. Comput., 2017, pp. 1532-1536.
[12] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays," IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40-60, Jan. 2013.
[13] H. Q. Ngo, A. Ashikhmin, H. Yang, E. G. Larsson, and T. L. Marzetta, "Cell-free massive MIMO versus small cells," IEEE Trans. Wireless Commun., vol. 16, no. 3, pp. 1834-1850, Mar. 2017.
[14] E. Björnson and L. Sanguinetti, "Making cell-free massive MIMO competitive with MMSE processing and centralized implementation," IEEE Trans. Wireless Commun., vol. 19, no. 1, pp. 77-90, Jan. 2020.
[15] J. Hoydis, S. ten Brink, and M. Debbah, "Massive MIMO in the UL/DL of cellular networks: How many antennas do we need?," IEEE J. Select. Areas Commun., vol. 31, no. 2, pp. 160-171, Feb. 2013.
[16] J. Zhang, C. -K. Wen, S. Jin, X. Gao, and K.-K. Wong, "Large system analysis of cooperative multi-cell downlink transmission via regularized channel inversion with imperfect CSIT," IEEE Trans. Wireless Commun., vol. 12, no. 10, pp. 4801-4813, Oct. 2013.
[17] Z. Wei, D. Xu, S. Li, S. Song, D. W. K. Ng, and G. Caire, "Resource allocation design for next-generation multiple access: A tutorial overview," in Proc. IEEE, vol. 112, no. 9, pp. 1230-1263, Sep. 2024.
[18] A. Kammoun, M. Kharouf, W. Hachem, and J. Najim, "A central limit theorem for the SINR at the LMMSE estimator output for large-dimensional signals," IEEE Trans. Inf. Theory, vol. 55, no. 11, pp. 5048-5063, Nov. 2009.
[19] A. Kammoun et al., "BER and outage probability approximations for LMMSE detectors on correlated MIMO channels," IEEE Trans. Inf. Theory, vol. 55, no. 10, pp. 4386-4397, Oct. 2009.
[20] X. Zhang, S. Song, and Y. C. Eldar, "Secrecy analysis for MISO broadcast systems with regularized zero-forcing precoding," 2023, arXiv:2301.11515.
[21] X. Zhao, M. Li, Y. Liu, T. -H. Chang, and Q. Shi, "Communication-efficient decentralized linear precoding for massive MU-MIMO systems," IEEE Trans. Signal Process., vol. 71, pp. 4045-4059, 2023.
[22] X. Zhao, M. Li, B. Wang, E. Song, T.-H. Chang, and Q. Shi, "Efficient LMMSE equalization for massive MIMO systems under decentralized baseband processing architecture," IEEE J. Select. Areas Commun, vol. 43, no. 3, pp. 736-751, Mar. 2025.
[23] S. Wagner, R. Couillet, M. Debbah, and D. T. M. Slock, "Large system analysis of linear precoding in correlated MISO broadcast channels under limited feedback," IEEE Trans. Inf. Theory, vol. 58, no. 7, pp. 4509-4537, Jul. 2012.
[24] J. Hoydis, M. Kobayashi, and M. Debbah, "Asymptotic performance of linear receivers in network MIMO," in Proc. Conf. Rec. 44th Asilomar Conf. Signals, Syst. Comput., 2010, pp. 942-948.
[25] E. Björnson, J. Hoydis, and L. Sanguinetti, Massive MIMO Networks: Spectral, Energy, and Hardware Efficiency. London, U.K.: Now Found. Trends, 2017.
[26] B. Picinbono, "Second-order complex random vectors and normal distributions," IEEE Trans. Signal Process., vol. 44, no. 10, pp. 2637-2640, Oct. 1996.
[27] B. Hassibi and B. Hochwald, "How much training is needed in multipleantenna wireless links?," IEEE Trans. Inf. Theory, vol. 49, no. 4, pp. 951-963, Apr. 2003.
[28] A. Abrardo, G. Fodor, M. Moretti, and M. Telek, "MMSE receiver design and SINR calculation in MU-MIMO systems with imperfect CSI," IEEE Wireless Commun. Lett., vol. 8, no. 1, pp. 269-272, Feb. 2019.
[29] D. Guo, S. Shamai, and S. Verdu, "Mutual information and minimum mean-square error in Gaussian channels," IEEE Trans. Inf. Theory, vol. 51, no. 4, pp. 1261-1282, Apr. 2005.
[30] A. W. Marshall, I. Olkin, and B. C. Arnold, Inequalities: Theory of Majorization and its Applications. New York, NY, USA: Academic Press, 1979.
[31] Z. Zhuang, X. Zhang, D. Xu, S. Song, and Y. C. Eldar, "Decentralized MIMO systems with imperfect CSI using LMMSE receivers," 2025, arXiv:2408.12811.
[32] J. Zhang, C.-K. Wen, S. Jin, X. Gao, and K.-K. Wong, "On capacity of large-scale MIMO multiple access channels with distributed sets of correlated antennas," IEEE J. Select. Areas Commun., vol. 31, no. 2, pp. 133-148, Feb. 2013.
[33] X. Zhang and S. Song, "Secrecy analysis for IRS-aided wiretap MIMO communications: Fundamental limits and system design," IEEE Trans. Inf. Theory, vol. 70, no. 6, pp. 4140-4159, Jun. 2024.
[34] A. Kammoun and M.-S. Alouini, "No eigenvalues outside the limiting support of generally correlated gaussian matrices," IEEE Trans. Inf. Theory, vol. 62, no. 7, pp. 4312-4326, Jul. 2016.
[35] A. W. Van der Vaart, Asymptotic Statistics. Cambridge, U.K.: Cambridge Univ. Press, 1998.
[36] Z.-D. Bai and J. W. Silverstein, "No eigenvalues outside the support of the limiting spectral distribution of large-dimensional sample covariance matrices," Ann. Probab., vol. 26, no. 1, pp. 316-345, Jan. 1998.
[37] W. Hachem, O. Khorunzhiy, P. Loubaton, J. Najim, and L. Pastur, "A new approach for mutual information analysis of large dimensional multiantenna channels," IEEE Trans. Inf. Theory, vol. 54, no. 9, pp. 3987-4004, Sep. 2008.
[38] R. A. Horn and C. R. Johnson, Matrix Analysis. Cambridge, U.K.: Cambridge Univ. Press, 2012.
[39] L. A. Pastur and M. Shcherbina, Eigenvalue Distribution of Large Random Matrices. Providence, RI, USA: Amer. Math. Soc., 2011.
[40] X. Zhang and S. Song, "Asymptotic mutual information analysis for double-scattering MIMO channels: A new approach by Gaussian tools," IEEE Trans. Inf. Theory, vol. 69, no. 9, pp. 5497-5527, Sep. 2023.
[41] Z. Zhuang, X. Zhang, D. Xu, and S. Song, "Fundamental limits of two-hop MIMO channels: An asymptotic approach," 2024, arXiv:2402.03772.
![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-17.jpg?height=323&width=261&top_left_y=597&top_left_x=1039)

Zeyan Zhuang (Graduate Student Member, IEEE) received the B.Eng. degree from Nankai University, Tianjin, China, in 2022. He is currently working toward the Ph.D. degree with the Department of Electronic and Computer Engineering, The Hong Kong University of Science and Technology, Hong Kong. His research interests include random matrix theory and its corresponding applications.
![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-17.jpg?height=321&width=261&top_left_y=1237&top_left_x=1039)

Xin Zhang (Member, IEEE) received the B.Eng. degree in information engineering from the Beijing University of Posts and Telecommunications (BUPT) in 2015, the master's degree in electronic engineering from Tsinghua University, Beijing, China, in 2018, and the Ph.D. degree in electronic and computer engineering (ECE) from the Hong Kong University of Science and Technology (HKUST), Hong Kong, in 2024. He is currently a Postdoctoral Research Fellow with HKUST. His research interests include random matrix theory, information theory, and their applications in signal processing, communications, and learning. He was recognized as an Exemplary Reviewer of the IEEE Communications Letters in 2024.
![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-17.jpg?height=323&width=261&top_left_y=1961&top_left_x=1039)

Dongfang Xu (Member, IEEE) received the B.Eng. degree in communication engineering from Shandong University, Jinan, China in July 2014, and the M.Sc. degree (with Distinction) in communications and multimedia engineering and the Ph.D. degree (with Distinction) in electrical engineering from Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU), Erlangen, Germany, in September 2017 and December 2022, respectively. He is currently a Research Assistant Professor with the Hong Kong University of Science and Technology (HKUST), Hong Kong. He was the co-recipient of the IEEE Communications Society Leonard G. Abraham Prize 2023, IEEE Communications Society Stephen O. Rice Prize 2022, and IEEE Global Communications Conference (GLOBECOM) 2019 Best Paper Award. He was also recognized as an Exemplary Reviewer of IEEE Transactions on Communications in 2020, 2021, and 2022, and an Exemplary Reviewer of the IEEE Communications Letters in 2023. He is also the Editor of IEEE Transactions on Mobile Computing and IEEE Communications Letters.
![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-18.jpg?height=316&width=261&top_left_y=232&top_left_x=141)

Shenghui Song (Senior Member, IEEE) is currently an Assistant Professor jointly appointed by the Division of Integrative Systems and Design (ISD) and the Department of Electronic and Computer Engineering (ECE) with the Hong Kong University of Science and Technology (HKUST), Hong Kong. His research interests include the areas of wireless communications and machine learning with current focus on distributed intelligence, semantic communications, machine learning for communications, integrated sensing and communication, and information theory. He is also interested in the research on Engineering Education. He was named the Exemplary Reviewer for IEEE Communications Letter. He was the Tutorial Program Co-Chairs of the 2022 IEEE International Mediterranean Conference on Communications and Networking, and the Technical Program Chairs of the International Conference on 6G Communications Networking and Signal Processing, in 2023 and 2024. He is also an Associate Editor for IEEE Transactions on Education. He was the recipient of the several teaching awards at HKUST, including the Michael G. Gale Medal for Distinguished Teaching in 2018, Best Ten Lecturers in 2013, 2015, and 2017, School of Engineering Distinguished Teaching Award in 2012, Teachers I Like Award in 2013, 2015, 2016, and 2017, M.Sc. (Telecom) Teaching Excellent Appreciation Award for 2020-21 and 2022-23, and the honorees of the Third Faculty Recognition at HKUST in 2021.
![](https://cdn.mathpix.com/cropped/536eaeca-0e98-40cf-96c3-e0d131cfa318-18.jpg?height=326&width=259&top_left_y=227&top_left_x=1054)

Yonina C. Eldar (Fellow, IEEE) received the B.Sc. degree in physics and the B.Sc. degree in electrical engineering from Tel-Aviv University (TAU), TelAviv, Israel, in 1995 and 1996, respectively, and the Ph.D. degree in electrical engineering and computer science from the Massachusetts Institute of Technology (MIT), Cambridge, MA, USA, in 2002. She is currently a Professor with the Department of Mathematics and Computer Science, Weizmann Institute of Science, Rehovot, Israel, where she holds the Dorothy and Patrick Gorman Professorial Chair and also Heads the Center for Biomedical Engineering. She was a Professor with the Department of Electrical Engineering, Technion, where she held the Edwards Chair in Engineering. She is also a Visiting Professor with MIT, Visiting Scientist with Broad Institute, Visiting Research Collaborator with Princeton, an Adjunct Professor with Duke University, Durham, NC, USA, Advisory Professor with Fudan University, Shanghai, China, Distinguished Visiting Professor with Tsinghua University, Beijing, China, and was Visiting Professor with Stanford. She was a Horev Fellow of the Leaders in Science and Technology Program with Technion and an Alon Fellow. She is author of the book Sampling Theory: Beyond Bandlimited Systems and co-author of ten other books and also a highly cited Researcher. Her research interests include the broad areas of statistical signal processing, sampling theory, and compressed sensing, learning and optimization methods, and their applications to biology, medical imaging, and optics. Dr. Eldar was the recipient of the many awards for excellence in research and teaching, including the IEEE Signal Processing Society Technical Achievement Award (2013), IEEE/AESS Fred Nathanson Memorial Radar Award (2014), IEEE Kiyo Tomiyasu Award (2016), Michael Bruno Memorial Award from the Rothschild Foundation, Weizmann Prize for Exact Sciences, Wolf Foundation Krill Prize for Excellence in Scientific Research, Henry Taub Prize for Excellence in Research (twice), Hershel Rich Innovation Award (three times), Award for Women with Distinguished Contributions, Andre and Bella Meyer Lectureship, Career Development Chair at the Technion, Muriel David Jacknow Award for Excellence in Teaching, Technion's Award for Excellence in Teaching (two times), several Best Paper awards and Best Demo awards together with her research students and colleagues including the SIAM outstanding Paper Prize, UFFC Outstanding Paper Award, Signal Processing Society Best Paper Award and the IET Circuits, Devices and Systems Premium Award, was selected as one of the 50 most influential women in Israel and in Asia. She is the Editor in Chief of Foundations and Trends in Signal Processing. She was a Signal Processing Society Distinguished Lecturer, member of the IEEE Signal Processing Theory and Methods and Bio Imaging Signal Processing Technical Committees. She was an Associate Editor for the IEEE Transactions On Signal Processing, EURASIP Journal of Signal Processing, SIAM Journal on Matrix Analysis and Applications, and SIAM Journal on Imaging Sciences. She was Co-Chair and Technical Co-Chair of several international conferences and workshops. She was a member of the Young Israel Academy of Science and Humanities and the Israel Committee for Higher Education. She is a member with the Israel Academy of Sciences and Humanities (elected 2017) and with the Academia Europaea (elected 2023), EURASIP Fellow, Fellow of the Asia-Pacific Artificial Intelligence Association, and Fellow of the 8400 Health Network. She is also a member of the IEEE Sensor Array and Multichannel Technical Committee and serves on several other IEEE committees.


[^0]:    ${ }^{1}$ According to the properties of conditional Gaussian distributions [26, Section IV], the distribution of the channel vector is given by $\mathbf{h}_{j k} \mid \widehat{\mathbf{h}}_{j k} \sim \mathcal{C N}\left(\widehat{\mathbf{h}}_{j k}, \widetilde{\sigma}_{k}^{2}\left[\mathbf{R}_{j}\right]_{[k, k]}\left(\left[\mathbf{R}_{j}\right]_{[k, k]}+\widetilde{\sigma}_{k}^{2} \mathbf{I}_{N_{k}}\right)^{-1}\right)$.

