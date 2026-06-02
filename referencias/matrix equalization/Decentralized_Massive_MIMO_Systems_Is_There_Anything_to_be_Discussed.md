# Decentralized Massive MIMO Systems: Is There Anything to be Discussed? 

Jesús Rodríguez Sánchez ${ }^{1}$, Juan Vidal Alegría ${ }^{1}$, Fredrik Rusek ${ }^{1,2}$<br>${ }^{1}$ Department of Electrical and Information Technology, Lund University, Sweden<br>${ }^{2}$ Sony Europe, Lund, Sweden<br>\{jesus.rodriguez, juan.vidal, fredrik.rusek\}@eit.lth.se


#### Abstract

Algorithms for Massive MIMO uplink detection are typically based on a centralized approach, by which baseband data from all antenna modules need to be routed to a central node for further processing. In the case of Massive MIMO, where hundreds or thousands of antennas are expected in the base-station, such architecture requires high interconnection bandwidth between antennas and the central node. Recently, decentralized architectures have been proposed to maintain low interconnection bandwidth, where channel-state-information (CSI) is obtained locally in each antenna node and not shared. Further, Massive MIMO performance is sensitive to CSI quality. However, in the literature, ideal CSI is typically assumed in decentralized systems, which is not only far from reality but also limits the generality of the analysis.

This paper proposes a decentralized (a term that will be defined in the main body of the paper) architecture with the following main features: (i) the channel matrix is not made available at any single node, (ii) there is no inter-communication among antennas, (iii) the architecture used during the payload data phase, is reused to provide a certain statistic to a processing node, (iv) A non-standard channel estimation problem based on said statistic arises, ( $v$ ) a matrix inversion is needed (in case of zero-forcing) at said processing node.


A hefty share of the paper is devoted to (iv).
Index Terms-Massive MIMO, decentralized, detection, zeroforcing, wishart, MMSE, ML, MAP.

## I. Introduction

Massive MIMO [1] is one of the most relevant technologies in contemporary wireless communications. High spectral efficiency and improved link reliability, achieved by using hundreds or thousands of antenna elements, are among the technology's key features, making it a key enabler to exploit spatial diversity far beyond traditional MIMO systems. Unprecedented spatial resolution is achieved, while simultaneously providing service to multiple users within the same timefrequency resource.

Despite all advantages of Massive MIMO, there are challenges from an implementation point of view. Uplink detection algorithms, like zero-forcing (ZF), typically rely on a centralized architecture, where baseband samples and channel state information (CSI) are collected in a central processing node for further matrix inversion and detection. Physical connections are needed between the antenna modules and the central node to carry the required data. This approach, that is perfectly valid for a relatively low number of antennas, becomes problematic when the number of antennas increases,
with the interconnection bandwidth as the main bottleneck in the system.

Initial Massive MIMO prototypes [2] [3] were the first to face this problem and pragmatic solutions were proposed. Later, efforts have been made to study the problem more rigorously, see for example [4] and [5]. In [5], a partial decentralized (PD) solution is put forth, which achieves exactly the same estimates (and therefore performance) as linear detectors, such as maximum ratio combing (MRC), ZF and L-MMSE. There are more recent activities in this area in [6] and [7], where antennas are connected by direct links forming a daisy-chain. It has been shown that such a structure is able to achieve approximate ZF performance under IID channel conditions and perfect CSI with very low inter-connection requirements and fully decentralized detection/precoding processing. In order to achieve this, obtaining CSI is required prior to detection. However, motivated by scalability reasons, decentralized architectures do not allow all baseband samples to be collected at a single point, which limits one's channel estimation capability.

It has been understood that the full benefits of massive MIMO, such as high spectrum efficiency, heavily rely on accurate CSI. Poor channel estimates cannot reach sufficiently good inter-user interference (IUI) cancellation, a problem that amplifies as the number of users grows. Unfortunately, channel estimation is not typically covered in the decentralized debate and ideal CSI is always assumed to be available.

In this work we argue that much of the centralized vs. noncentralized discussion is unnecessary and that non-perfect CSI has to be assumed for the problem not to be trivial. In short, our arguments are as follows: The non-centralized discussion seems to be revolving around the training phase, more specifically around avoiding the collection of full CSI at any given node. However, there is also a payload data phase, and during this phase it can be assumed that each antenna contributes, at the very minimum, with a scalar value to a central processing unit (responsible for, e.g., error control decoding, HARQ, etc.). In order to maintain low interconnection bandwidth, these antenna contributions are likely to be summed up before being formally presented to the central processing unit. That said, we observe that there is an easy way to transfer a statistic that is sufficient for demodulation purposes, using the same circuitry used during the payload data phase. Such a method
can, according to a separate discussion in the next section, be classified as non-centralized since it 1) does not store the full CSI at any given node, and 2) it does not expand the interconnections between antennas and processing unit beyond what is needed for payload data. At the central processing node, channel estimation and channel inversion remains, but we argue that these are fairly minor tasks compared to other baseband tasks needed at such a node. One of our main messages we try to convey is that, in our view, meeting 2) is sufficient for a scheme to be classified as non-centralized (roughly speaking, 1) is a natural consequence of 2)). Further, if perfect CSI is assumed, then the method to be presented is optimal, so not much discussion is needed.

The remainder of the paper is organized as follows. A system model and a review of linear detection methods in Massive MIMO is presented in section II. In III we discuss centralized and decentralized systems and motivate the scope of our article. Our method and a collection of practical channel estimators are presented in IV. Results are presented in V. Finally, section VI summarizes our conclusions.

Notation: In this paper, lowercase, bold lowercase and upper bold face letters stand for scalars, column vectors and matrices, respectively. The operations $(.)^{T}$, (.)* and $(.)^{H}$ denote transpose, conjugate and conjugate transpose, respectively. ${ }_{0} \tilde{F}_{1}$ is the hypergeometrical function of a matrix argument, defined as in [8], $\tilde{\Gamma}_{m}$ denotes the complex multivariate gamma function. $|\mathbf{A}|, \operatorname{tr}(\mathbf{A})$ and $\operatorname{eig}(\mathbf{A})$ represent the determinant, trace, and eigenvalues of a matrix A, respectively. $\mathcal{C} \mathcal{N}(\mathbf{0}, \mathbf{A})$ denotes circularly-symmetric multivariate complex-valued Gaussian probability density distribution with covariance $\mathbf{A}$.

## II. System model

For uplink detection, we consider a scenario with $K$ singleantenna users transmitting to a base-station (BS) with an antenna array with $M$ elements through a narrow-band channel with IID Rayleigh fading

$$
\begin{equation*}
\mathbf{y}=\mathbf{H} \mathbf{x}+\mathbf{n}, \tag{1}
\end{equation*}
$$

where $\mathbf{y}$ is the $M \times 1$ received vector, $\mathbf{x}$ is the transmitted user data vector ( $K \times 1$ ), with uniform unitary power distribution across users such that $\mathbb{E}\left\{\mathbf{x x}^{H}\right\}=\mathbf{I}, \mathbf{H}=\left[\mathbf{h}_{1} \mathbf{h}_{2} \cdots \mathbf{h}_{M}\right]^{T}$ is the channel matrix ( $M \times K$ ) whose rows follows $\mathcal{C} \mathcal{N}(\mathbf{0}, \mathbf{C})$, and $\mathbf{n}$ thermal noise ( $M \times 1$ ) at the BS with distribution $\mathcal{C} \mathcal{N}\left(\mathbf{0}, N_{0} \mathbf{I}\right)$.

## A. Linear Processing in massive MIMO

We consider only linear detectors, because they exhibit close to optimal performance in Massive MIMO while having low complexity. A linear equalizer provides an estimate of $\mathbf{x}, \hat{\mathbf{x}}$, by applying an equalizer filter matrix $\mathbf{W}$ to the vector observation, $\mathbf{y}$, as follows

$$
\begin{equation*}
\hat{\mathbf{x}}=\mathbf{W} \mathbf{y}, \tag{2}
\end{equation*}
$$

where $\mathbf{W}=\left[\begin{array}{llll}\mathbf{w}_{1} & \mathbf{w}_{2} & \cdots & \mathbf{w}_{K}\end{array}\right]^{T}$ is a $K \times M$ complex matrix.

We limit our exposition to maximum-ratio combining (MRC) and zero-forcing (ZF), with the remark that our analysis would remain essentially unaltered for other choices, whose equalizer matrices are defined as

$$
\mathbf{W}= \begin{cases}\mathbf{H}^{H} & \text { for MRC }  \tag{3}\\ \mathbf{G}^{-1} \mathbf{H}^{H} & \text { for ZF. }\end{cases}
$$

where $\mathbf{G}=\mathbf{H}^{H} \mathbf{H}$ is the Gramian matrix. It is important to note that matrix $\mathbf{W}$ is valid during a Coherence Block (CB) of the channel, representing a time-frequency region where the channel can be considered approximately constant.

MRC represents ideal decentralized processing, allowing each antenna node to obtain an equalization vector from local CSI. ZF, on the other hand, ostensibly requires the system to collect all CSI from all antennas in a central processing node, for further matrix inversion. It is well known that ZF provides superior performance over MRC due to perfect inter-user interference cancellation capabilities at the cost of increased interconnection bandwidth and processing requirements. However, as we will show, the interconnection bandwidth needs in fact not to increase, leaving the amplified processing as the only issue. If we take all other tasks that a central processing node needs to carry out into account, we argue that the need of a matrix inversion per CB is not the bottleneck of a centralized architecture. Thus, it is the interconnection bandwidth that needs consideration.

## III. Decentralized vs centralized: current debate

Linear processing in Massive MIMO was presented in the previous section together with two detection methods. These two schemes can be implemented in centralized or decentralized systems. In centralized architectures, the central node collects CSI from all antenna elements, represented by the matrix $\mathbf{H}$, which allows for optimal construction of the matrix W. Apart from that, the central unit's tasks also include, e.g., demodulation and decoding. Processing at the antenna side comprises RF, ADC and optionally OFDM processing (FFT). The amount of interconnection data-rate between antennas and the central node depends on $M$, which is an important limitation in Massive MIMO systems where a large number of antenna elements is expected.

There is nowadays a trend towards decentralized systems in order to allow scalability of the system. Decentralized systems perform antenna processing locally, including CSI acquisition and partial detection. One of the key characteristics of this type of systems is that full CSI is not available at any point. The central node carries out remaining parts, such as per-user processing (e.g., symbol de-mapping and decoding).

In both types of architectures, antenna elements need to be connected to the central node. We acknowledge that the definition of a decentralized system is not an easy one to make, but here we define the term as a system where the volume of the data provided during the training phase to the processing node is independent of $M$. Our definition allows for the Gramian to be transfered, since it is of dimension $K \times K$.

We now, briefly, interlude the discussion by considering what tasks are needed during the payload data phase. Since matched filtering is information lossless, we can, without any loss of generality, assume that such operation is performed. This implies that, for each channel observation, each antenna should multiply its observed signal with a $K \times 1$ vector, and that the $M$ resulting $K \times 1$ vectors should be summed and passed to the central node by specific hardware that has to be be in place.

Let us now return to a decentralized system. For $K$ singleantenna users, there are $K$ slots per CB where the payload data phase in inactive. This releases $K$ usages of the hardware mentioned just above. Earlier it was also mentioned that passage of the $K \times K$ Gramian to the central node is within the delineations of a decentralized architecture. Conveniently, such transfer can be done via $K$ transmissions of $K \times 1$ vectors. Since the Gramian can be written as a sum over the $M$ outer products of the antennas' channel vectors, we can conclude that the hardware used in the payload data phase is, 1) sufficient to transfer the Gramian, and 2) unoccupied for a duration sufficient for the transmission of the Gramian.

Under assumption that matched filtering is applied at each antenna, it remains for the central node during the payload data phase to invert the Gramian, and apply the inverse to its $K \times 1$ input vectors. We claim that this is of non-prohibitive complexity when taking its other tasks into account.

If we further, assume an absolute absence of noise, then the above described method would be optimal. In that case, we do not see much need for any further discussion on decentralized architecture design. Our sentiment is, thus, that non-ideal CSI must be assumed. Consequently, we must study the channel estimation problem that the central node faces, namely, that of the estimation of a Gramian matrix from a noisy version. We study this in some detail in the next section, with outcome that it poses no noteworthy challenges.

## IV. Channel Estimation

In this section we discuss channel estimation of Gramian matrices. However, we commence by first going through all steps prior to the central node facing said estimation problem. An initial channel estimation is performed per-antenna basis, based on pilots sent by users. With a received signal y given by (1), the goal for each antenna is to obtain an estimate of its corresponding part of $\mathbf{H}$. If users send orthogonal pilots, we can define the $K \times K$ matrix $\mathbf{P}=\left[\mathbf{p}_{1}, \mathbf{p}_{2}, \ldots, \mathbf{p}_{K}\right]$, where $\mathbf{p}_{k}$ is defined as a $K \times 1$ vector of the following form

$$
\mathbf{p}_{k}(i) \triangleq \begin{cases}p_{k} & \text { if } k=i \\ 0 & \text { if } k \neq i\end{cases}
$$

where $p_{k}$ is a complex number known by the BS which represents the pilot from the $k$-th user. Based on this definition, the $M \times K$ BS observation matrix $\mathbf{Z}$ can be described by

$$
\begin{equation*}
\mathbf{Z}=\mathbf{H P}+\mathbf{N} \tag{4}
\end{equation*}
$$

where $\mathbf{Z}=\left[\mathbf{z}_{1}, \mathbf{z}_{2}, \ldots, \mathbf{z}_{M}\right]^{T}, \mathbf{z}_{m}$ being the $K \times 1$ observation vector at antenna $m . \mathbf{N}=\left[\mathbf{n}_{1}, \mathbf{n}_{2}, \ldots, \mathbf{n}_{M}\right]^{T}$ represents the
noise term as a $M \times K$ matrix and $\mathbf{n}_{m}$ the $K \times 1$ noise vector related to the same antenna. For antenna $m$, (4) becomes

$$
\mathbf{z}_{m}=\mathbf{P} \mathbf{h}_{m}+\mathbf{n}_{m}
$$

and channel estimation is performed locally based on the observation vector $\mathbf{z}_{m}$. The Least Squares (LS) estimate of $\mathbf{H}$ is

$$
\begin{equation*}
\widehat{\mathbf{H}}_{\mathrm{LS}}=\mathbf{Z} \mathbf{P}^{-1}, \tag{5}
\end{equation*}
$$

and in the simple case $\mathbf{P}=\mathbf{I}$, then $\widehat{\mathbf{H}}_{\mathrm{LS}}=\mathbf{Z}$, or per antenna $\widehat{\mathbf{h}}_{m, \mathrm{LS}}=\mathbf{z}_{m}$.

The second step in channel estimation is to obtain $\mathbf{R}= \widehat{\mathbf{G}}_{\mathrm{LS}}$, where $\widehat{\mathbf{G}}_{\mathrm{LS}}=\widehat{\mathbf{H}}_{\mathrm{LS}}^{H} \widehat{\mathbf{H}}_{\mathrm{LS}}$. To do that, each antenna computes the partial term $\mathbf{R}_{m}=\widehat{\mathbf{h}}_{m}^{*} \widehat{\mathbf{h}}_{m}^{T}$, a $K \times K$ matrix, and therefore $\mathbf{R}=\sum_{m=1}^{M} \mathbf{R}_{m}$. This addition can be carried out by exploiting the existing antennas' connections needed for data detection.

In next subsections we obtain the PDF of $\mathbf{R}$ and $\mathbf{G}$, and the results will be used to formulate estimators of $\mathbf{G}$, which outperform the one-step channel estimation based solely on the decentralized LS channel estimate derived from (5).

## A. Derivation of conditional PDFs

If $\mathbf{Z}$ is an $M \times K$ complex matrix whose rows follow a multivariate normal distribution with covariance matrix $\boldsymbol{\Sigma}$ and mean $\mathbb{E}(\mathbf{Z})=\mathbf{H}$, then the conditional distribution of $\mathbf{R}= \mathbf{Z}^{\mathbf{H}} \mathbf{Z}$ is noncentral Wishart and is defined as [8]

$$
\begin{align*}
p(\mathbf{R} \mid \mathbf{G}) & =\mathrm{e}^{-\operatorname{tr}\left(\boldsymbol{\Sigma}^{-1} \mathbf{G}\right)}{ }_{0} \tilde{F}_{1}\left(M ; \boldsymbol{\Sigma}^{-1} \mathbf{G} \boldsymbol{\Sigma}^{-1} \mathbf{R}\right) \\
& \times \frac{1}{\tilde{\Gamma}_{K}(M)|\boldsymbol{\Sigma}|^{M}} e^{-\operatorname{tr}\left(\boldsymbol{\Sigma}^{-1} \mathbf{R}\right)}|\mathbf{R}|^{M-K}, \tag{6}
\end{align*}
$$

and noted as $\mathbf{R} \mid \mathbf{G} \sim \mathcal{W}_{K}\left(M, \boldsymbol{\Sigma}, \boldsymbol{\Sigma}^{-1} \mathbf{G}\right)$. The matrix $\boldsymbol{\Sigma}^{-1} \mathbf{G}$ is referred to as noncentrality matrix in most literature.

The marginal PDF for matrix $\mathbf{G}$ becomes a central Wishart and its expression is as follows

$$
\begin{equation*}
p(\mathbf{G})=\frac{1}{\tilde{\Gamma}_{K}(M)|\mathbf{C}|^{M}} e^{-\operatorname{tr}\left(\mathbf{C}^{-1} \mathbf{G}\right)}|\mathbf{G}|^{M-K} \tag{7}
\end{equation*}
$$

and noted as $\mathbf{G} \sim \mathcal{W}_{K}(M, \mathbf{C})$. The marginal PDF of $\mathbf{R}$ can be obtained as

$$
\begin{aligned}
p(\mathbf{R}) & =\frac{1}{\tilde{\Gamma}_{K}(M)|\boldsymbol{\Sigma}|^{M}} e^{-\operatorname{tr}\left(\boldsymbol{\Sigma}^{-1} \mathbf{R}\right)}|\mathbf{R}|^{M-K} \\
& \times \frac{1}{\tilde{\Gamma}_{K}(M)|\mathbf{C}|^{M}} \int e^{-\operatorname{tr}\left[\left(\boldsymbol{\Sigma}^{-1}+\mathbf{C}^{-1}\right) \mathbf{G}\right]}|\mathbf{G}|^{M-K} \\
& \times{ }_{0} \tilde{F}_{1}\left(M ; \boldsymbol{\Sigma}^{-1} \mathbf{G} \boldsymbol{\Sigma}^{-1} \mathbf{R}\right) \mathrm{d} G
\end{aligned}
$$

Introducing a matrix $\mathbf{A}$ such that $\mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1}=\boldsymbol{\Sigma}^{-1}+\mathbf{C}^{-1}$, which translates to $\mathbf{A}=\left(\mathbf{I}+\mathbf{C}^{-1} \boldsymbol{\Sigma}\right)^{-1}$, leads to

$$
\begin{align*}
p(\mathbf{R}) & =\frac{|\boldsymbol{\Sigma} \mathbf{A}|^{M}}{\tilde{\Gamma}_{K}(M)|\boldsymbol{\Sigma}|^{M}|\mathbf{C}|^{M}} e^{-\operatorname{tr}\left[\boldsymbol{\Sigma}^{-1} \mathbf{R}(\mathbf{I}-\mathbf{A})\right]}|\mathbf{R}|^{M-K} \\
& \times \int \frac{1}{\tilde{\Gamma}_{K}(M)|\Sigma \mathbf{A}|^{M}} e^{-\operatorname{tr}\left(\boldsymbol{\Sigma}^{-1} \mathbf{R} \mathbf{A}\right)} e^{-\operatorname{tr}\left(\mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1} \mathbf{G}\right)}  \tag{8}\\
& \times|\mathbf{G}|^{M-K_{0}} \tilde{F}_{1}\left(M ; \boldsymbol{\Sigma}^{-1} \mathbf{R} \boldsymbol{\Sigma}^{-1} \mathbf{G}\right) \mathrm{d} G,
\end{align*}
$$

where we used the fact that $\operatorname{eig}(\mathbf{P X P Y})=\operatorname{eig}(\mathbf{P Y P X})$ given any complex matrix $\mathbf{P}$, being $\mathbf{X}$ and $\mathbf{Y}$ two Hermitian complex matrices, and therefore ${ }_{0} \tilde{F}_{1}(M ; \mathbf{P X P Y})= { }_{0} \tilde{F}_{1}(M ; \mathbf{P} \mathbf{Y P X})$. In our case $\mathbf{P}=\boldsymbol{\Sigma}^{-1}, \mathbf{X}=\mathbf{G}$ and $\mathbf{Y}=\mathbf{R}$.

We can manipulate $\frac{|\boldsymbol{\Sigma} \mathbf{A}|^{M}}{|\boldsymbol{\Sigma}|^{M}|\mathbf{C}|^{M}}$ as follows

$$
\begin{align*}
\frac{|\boldsymbol{\Sigma} \mathbf{A}|^{M}}{|\boldsymbol{\Sigma}|^{M}|\mathbf{C}|^{M}} & =|\mathbf{A}|^{M}\left|\mathbf{C}^{-1}\right|^{M} \\
& =\left|\mathbf{A}\left(\mathbf{A}^{-1}-\mathbf{I}\right) \boldsymbol{\Sigma}^{-1}\right|^{M}  \tag{9}\\
& =\left|(\mathbf{I}-\mathbf{A}) \boldsymbol{\Sigma}^{-1}\right|^{M},
\end{align*}
$$

where the equality $\mathbf{C}^{-1}=\left(\mathbf{A}^{-1}-\mathbf{I}\right) \boldsymbol{\Sigma}^{-1}$ has been used.
By comparing (6) and (8) it is possible to observe that the second part of (8) is actually the integral of a noncentral Wishart PDF and therefore its value must be 1 . The final expression for $p(\mathbf{R})$ is a central Wishart as shown below

$$
\begin{equation*}
p(\mathbf{R})=\frac{1}{\tilde{\Gamma}_{K}(M)\left|\boldsymbol{\Sigma}(\mathbf{I}-\mathbf{A})^{-1}\right|^{M}} e^{-\operatorname{tr}\left[(\mathbf{I}-\mathbf{A}) \boldsymbol{\Sigma}^{-1} \mathbf{R}\right]}|\mathbf{R}|^{M-K}, \tag{10}
\end{equation*}
$$

which we denote as $\mathbf{R} \sim \mathcal{W}_{K}\left(M, \boldsymbol{\Sigma}(\mathbf{I}-\mathbf{A})^{-1}\right)$. Additionally, using $\boldsymbol{\Sigma}(\mathbf{I}-\mathbf{A})^{-1}=\mathbf{C}+\boldsymbol{\Sigma}$ then $\mathbf{R} \sim \mathcal{W}_{K}(M, \mathbf{C}+\boldsymbol{\Sigma})$.

Finally, the posterior PDF can be obtained by using Bayes' theorem and the results from (6), (7), (9) and (10) as follows

$$
\begin{align*}
p(\mathbf{G} \mid \mathbf{R}) & =\frac{p(\mathbf{R} \mid \mathbf{G}) p(\mathbf{G})}{p(\mathbf{R})} \\
& =e^{-\operatorname{tr}\left(\boldsymbol{\Sigma}^{-1} \mathbf{R} \mathbf{A}\right)}{ }_{0} \tilde{F}_{1}\left(M ; \boldsymbol{\Sigma}^{-1} \mathbf{R} \boldsymbol{\Sigma}^{-1} \mathbf{G}\right)  \tag{11}\\
& \times \frac{1}{\tilde{\Gamma}_{K}(M)|\boldsymbol{\Sigma} \mathbf{A}|^{M}} e^{-\operatorname{tr}\left(\mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1} \mathbf{G}\right)}|\mathbf{G}|^{M-K}
\end{align*}
$$

PDF in equation (11), assuming IID noise samples, is a noncentral Wishart, $\mathbf{G} \mid \mathbf{R} \sim \mathcal{W}_{K}\left(M, \boldsymbol{\Sigma} \mathbf{A}, \mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1} \mathbf{A R A}\right)$.

Once we have presented the PDFs involved in this study we can introduce the estimators.

## B. Maximum Likelihood (ML)

Maximum Likelihood (ML) estimate of $\mathbf{G}$ is defined as the matrix $\widehat{\mathbf{G}}_{\text {ML }}$, which maximizes the likelihood as follows

$$
\begin{align*}
\widehat{\mathbf{G}}_{\mathrm{ML}} & =\arg \max _{\mathrm{G}}\{p(\mathbf{R} \mid \mathbf{G})\} \\
& =\arg \max _{\underset{\mathrm{G}}{\max }}\left\{-\operatorname{tr}\left(\boldsymbol{\Sigma}^{-1} \mathbf{G}\right)\right.  \tag{12}\\
& \left.+\log \left[{ }_{0} \tilde{F}_{1}\left(M ; \boldsymbol{\Sigma}^{-1} \mathbf{G} \boldsymbol{\Sigma}^{-1} \mathbf{R}\right)\right]\right\} .
\end{align*}
$$

If $\mathbf{R}$ has an eigenvalue decomposition $\mathbf{R}=\mathbf{U} \boldsymbol{\Lambda} \mathbf{U}^{H}$, then we look for solutions whose form is $\mathbf{G}=\mathbf{U} \boldsymbol{\Omega} \mathbf{U}^{H}$, where $\boldsymbol{\Omega}$ and $\boldsymbol{\Lambda}$ are diagonal matrices containing the eigenvalues of $\mathbf{G}$ and $\mathbf{R}$ respectively. In the particular case that all pilots have equal power, i.e., $\left|p_{k}\right|=|p|, \forall k$, then without loosing generality we can set $|p|=1$, leading to $\boldsymbol{\Sigma}=N_{0} \mathbf{I}$, and (12) can be expressed as

$$
\widehat{\mathbf{G}}_{\mathrm{ML}}=\arg \max _{\boldsymbol{\Omega}}\left\{-\frac{1}{N_{0}} \operatorname{tr}(\boldsymbol{\Omega})+\log \left[{ }_{0} \tilde{F}_{1}\left(M ; \frac{1}{N_{0}^{2}} \boldsymbol{\Omega} \boldsymbol{\Lambda}\right)\right]\right\} .
$$

After derivation of the argument of the previous expression, the optimality condition can be expressed as

$$
\frac{1}{N_{0}}{ }_{0} \tilde{F}_{1}\left(M ; \frac{1}{N_{0}^{2}} \boldsymbol{\Omega}^{*} \boldsymbol{\Lambda}\right) \mathbf{I}=\left.\frac{\partial_{0} \tilde{F}_{1}\left(M ; \frac{1}{N_{0}^{2}} \boldsymbol{\Omega} \boldsymbol{\Lambda}\right)}{\partial \boldsymbol{\Omega}}\right|_{\boldsymbol{\Omega}=\boldsymbol{\Omega}^{*}},
$$

where $\widehat{\mathbf{G}}_{\mathrm{ML}}=\mathbf{U} \boldsymbol{\Omega}^{*} \mathbf{U}^{H}$, and from where we do not continue in an analytical form.

## C. Maximum A Posteriori (MAP)

The Maximum A Posteriori (MAP) estimate is defined as

$$
\begin{aligned}
\widehat{\mathbf{G}}_{\mathrm{MAP}} & =\arg \max _{\mathrm{G}}\{p(\mathbf{G} \mid \mathbf{R})\} \\
& =\arg \max _{\mathrm{G}} \log \left[{ }_{0} \tilde{F}_{1}\left(M ; \boldsymbol{\Sigma}^{-1} \mathbf{R} \boldsymbol{\Sigma}^{-1} \mathbf{G}\right)\right] \\
& -\operatorname{tr}\left(\mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1} \mathbf{G}\right)+(M-K) \log |\mathbf{G}| .
\end{aligned}
$$

If $\boldsymbol{\Sigma}=N_{0} \mathbf{I}$ and $\mathbf{C}=h_{\text {pow }} \mathbf{I}$ then $\mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1}= \left(\frac{1}{N_{0}}+\frac{1}{h_{\text {pow }}}\right) \mathbf{I}$ and therefore the MAP estimate can be expressed as follows, where $\mu_{1}, . ., \mu_{K}$ are the eigenvalues of $\mathbf{G}$,

$$
\begin{aligned}
\widehat{\mathbf{G}}_{\mathrm{MAP}} & =\arg \max _{\mu_{1}, \mu_{2}, \ldots, \mu_{K}} \log \left[{ }_{0} \tilde{F}_{1}\left(M ; \frac{1}{N_{0}^{2}} \boldsymbol{\Omega} \boldsymbol{\Lambda}\right)\right] \\
& -\left(\frac{1}{N_{0}}+\frac{1}{h_{\mathrm{pow}}}\right) \sum_{i=1}^{K} \mu_{i}+(M-K) \sum_{i=1}^{K} \log \left(\mu_{i}\right) .
\end{aligned}
$$

## D. Minimum Mean Square Error (MMSE)

The Minimum Mean Square Error (MMSE) estimate is defined as the expectation over the posterior probability. Taking into account that $\mathbf{G} \mid \mathbf{R}$ is a noncentral Wishart, that is $\mathbf{G} \mid \mathbf{R} \sim \mathcal{W}_{K}\left(M, \boldsymbol{\Sigma} \mathbf{A}, \mathbf{A}^{-1} \boldsymbol{\Sigma}^{-1} \mathbf{A} \mathbf{R} \mathbf{A}\right)$, the expectation is

$$
\begin{equation*}
\widehat{\mathbf{G}}_{\mathrm{MMSE}}=\mathbb{E}(\mathbf{G} \mid \mathbf{R})=M \boldsymbol{\Sigma} \mathbf{A}+\mathbf{A} \mathbf{R} \mathbf{A} . \tag{13}
\end{equation*}
$$

If $\mathbf{C}=h_{\text {pow }} \mathbf{I}$ and $\boldsymbol{\Sigma}=N_{0} \mathbf{I}$ then (13) becomes

$$
\begin{equation*}
\widehat{\mathbf{G}}_{\mathrm{MMSE}}=\frac{h_{\mathrm{pow}} N_{0}}{h_{\mathrm{pow}}+N_{0}} M \mathbf{I}+\left(\frac{h_{\mathrm{pow}}}{h_{\mathrm{pow}}+N_{0}}\right)^{2} \mathbf{R} . \tag{14}
\end{equation*}
$$

When $h_{\text {pow }} \gg N_{0}$ then $\widehat{\mathbf{G}}_{\text {MMSE }} \approx \mathbf{R}$. On the other hand, when $N_{0} \gg h_{\text {pow }}$ then $\widehat{\mathbf{G}}_{\text {MMSE }} \approx h_{\text {pow }} M \mathbf{I}$, which does not depend on $\mathbf{R}$, due to $\mathbf{R}$ conveys almost no information about $\mathbf{G}$ in that case.

## V. Equalizer formulation and results

The ZF equalization matrix is made up of two parts (3). The first part (or MRC part), $\widehat{\mathbf{H}}^{H}$, that is implemented in a decentralized form by the antenna modules, and the second part, $\widehat{\mathbf{G}}^{-1}$, that is performed in a central processing unit. Let's define two equalizers and compare their performance. ZF based on MMSE channel estimation (14) and LS channel estimation (5), is defined as, respectively,

$$
\mathbf{W}_{\mathrm{MMSE}}=\widehat{\mathbf{G}}_{\mathrm{MMSE}}^{-1} \widehat{\mathbf{H}}_{\mathrm{LS}}^{H}, \quad \mathbf{W}_{\mathrm{LS}}=\widehat{\mathbf{G}}_{\mathrm{LS}}^{-1} \widehat{\mathbf{H}}_{\mathrm{LS}}^{H}
$$

## A. Channel Estimation

In this subsection we compare both channel estimation methods based on the relative error defined as follows

$$
\epsilon_{\mathrm{Q}} \triangleq \mathbb{E}\left\{\frac{\left\|\widehat{\mathbf{G}}_{\mathrm{Q}}-\mathbf{G}\right\|_{\mathrm{F}}^{2}}{\|\mathbf{G}\|_{\mathrm{F}}^{2}}\right\}
$$

where $Q \in\{$ MMSE, LS$\}$. In scenarios with high SNR, that is $h_{\mathrm{pow}} \gg N_{0}$, (14) simplifies to $\widehat{\mathbf{G}}_{\mathrm{MMSE}} \simeq \mathbf{R}$, so $\epsilon_{\mathrm{MMSE}} \simeq \epsilon_{\mathrm{LS}}$. At low SNR levels, that is $N_{0} \gg h_{\text {pow }}, \widehat{\mathbf{G}}_{\text {MMSE }} \approx h_{\text {pow }} M \mathbf{I}$ and $\epsilon_{\text {MMSE }}$ saturates unlike $\epsilon_{\mathrm{LS}}$, that grows with $N_{0}$. Figure 1 shows this behavior in simulation.

![](https://cdn.mathpix.com/cropped/bff329b6-6b33-417f-80f9-dcec9c5d9118-5.jpg?height=555&width=614&top_left_y=212&top_left_x=300)
Fig. 1. Channel estimation error vs. noise level for both methods, $\mathbf{W}_{\text {MMSE }}$ and $\mathbf{W}_{\mathrm{ZF}} . \mathrm{M}=100 . \mathrm{K}=16 . \epsilon(\mathrm{dB})=10 \log _{10}(\epsilon)$.

## B. Sum-rate

The instantaneous SINR for user $k$ is given by

$$
\mathrm{SINR}_{k}=\frac{\left|\mathbf{w}_{k}^{H} \mathbf{h}_{k}\right|^{2}}{\sum_{i=1, i \neq k}^{K}\left|\mathbf{w}_{k}^{H} \mathbf{h}_{i}\right|^{2}+N_{0}\left\|\mathbf{w}_{k}\right\|^{2}},
$$

and the ergodic sum-rate as follows

$$
\begin{equation*}
R=\mathbb{E}\left\{\sum_{k=1}^{K} \log _{2}\left(1+\mathrm{SINR}_{k}\right)\right\} . \tag{15}
\end{equation*}
$$

Figure 2 shows the simulation results in terms of ergodic sum-rate for ZF with MMSE and LS channel estimators versus $\frac{K}{M}$. It is observed same performance for relative low $K$. MMSE outperforms the LS counterpart as $K$ grows which shows

![](https://cdn.mathpix.com/cropped/bff329b6-6b33-417f-80f9-dcec9c5d9118-5.jpg?height=555&width=618&top_left_y=1536&top_left_x=296)
Fig. 2. Total sum-rate for ZF detector with both channel estimation methods, LS and MMSE, according to (15) versus $\frac{K}{M}$ for $\mathrm{M}=100$. SNR at base-station receiver antenna. $\mathrm{SNR}=h_{\text {pow }} / N_{0}$.

## VI. Conclusions

We claim that the Gramian can be collected in a processing node by re-using existing connections without increasing interconnection data-rate requirements, and that this is sufficiently
decentralized for practical purposes. In this paper we have discussed in detail the ensuing channel estimation in decentralized Massive MIMO systems, where channel information is distributed and not fully available in one single point. We proposed a channel estimation based on the Gramian matrix for further ZF detection which outperforms direct methods based uniquely on per antenna processing.

## References

[1] T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Transactions on Wireless Communications, vol. 9, no. 11, pp. 3590-3600, November 2010.
[2] C. Shepard et al., "Argos: Practical many-antenna base stations," in Proceedings of the 18th Annual International Conference on Mobile Computing and Networking (Mobicom), New York, NY, USA, 2012, pp. 53-64.
[3] S. Malkowsky et al., "The world's first real-time testbed for massive MIMO: Design, implementation, and validation," IEEE Access, vol. 5, pp. 9073-9088, 2017.
[4] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE Journal on Emerging and Selected Topics in Circuits and Systems, vol. 7, no. 4, pp. 491-507, Dec 2017.
[5] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized Equalization with Feedforward Architectures for Massive MU-MIMO," ArXiv e-prints, Aug. 2018.
[6] J. R. Sanchez, F. Rusek, M. Sarajlic, O. Edfors, and L. Liu, "Fully decentralized massive mimo detection based on recursive methods," in 2018 IEEE International Workshop on Signal Processing Systems (SiPS), Oct 2018, pp. 53-58.
[7] M. Sarajlic, F. Rusek, J. R. Sanchez, L. Liu, and O. Edfors, "Fully decentralized approximate zero-forcing precoding for massive mimo systems," IEEE Wireless Communications Letters, pp. 1-1, 2019.
[8] A. T. James, "Distributions of matrix variates and latent roots derived from normal samples," Ann. Math. Statist., vol. 35, no. 2, pp. 475-501, 061964.
[9] A. Zanella, M. Chiani, and M. Z. Win, "On the marginal distribution of the eigenvalues of wishart matrices," IEEE Transactions on Communications, vol. 57, no. 4, pp. 1050-1060, April 2009.
[10] M. Kang and M. Alouini, "Largest eigenvalue of complex wishart matrices and performance analysis of mimo mrc systems," IEEE Journal on Selected Areas in Communications, vol. 21, no. 3, pp. 418-426, April 2003.
[11] K. Gross and D. Richards, "Total positivity, spherical series, and hypergeometric functions of matrix argument," IEEE Journal of Approximation Theory, no. 59, pp. 229-246, 1989.
[12] A. Gupta, Y. Sheena, and Y. Fujikoshi, "Estimation of the eigenvalues of noncentrality parameter matrix in noncentral wishart distribution," Journal of Multivariate Analysis, vol. 93, no. 1, pp. 1-20, 2005.
[13] P. Koev and A. Edelman, "The efficient evaluation of the hypergeometric function of a matrix argument," Math. Comp, p. 2006.
[14] Y. Sheena, A. K. Gupta, and Y. Fujikoshi, "Estimation of the eigenvalues of noncentrality parameter in matrix variate noncentral beta distribution," Annals of the Institute of Statistical Mathematics, vol. 56, no. 1, pp. 101-125, Mar 2004.
[15] A. K. Gupta and D. K. Nagar, Matrix Variate Distributions. Monographs and Suerveys in Pure and Applied Mathematics. 104. Chapman \& Hall/CRC, 2000.

