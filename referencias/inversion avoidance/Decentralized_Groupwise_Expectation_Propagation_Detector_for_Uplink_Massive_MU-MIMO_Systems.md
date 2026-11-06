# Decentralized Groupwise Expectation Propagation Detector for Uplink Massive MU-MIMO Systems 

Hua $\mathrm{Li}^{(B)}$, Yuanyuan Dong ${ }^{(D)}$, Caihong Gong ${ }^{(D)}$, Xiyuan Wang, Member, IEEE, and Xiaoming Dai ${ }^{(1)}$, Member, IEEE


#### Abstract

With the proliferation of emerging Internet of Things (IoT) applications, massive multiuser multiple-input-multiple-output (MU-MIMO) is a promising technology to support the massive connectivity requirement with limited spectral resources. The existing detection algorithms are mainly designed based on a centralized baseband processing architecture, which requires extremely high raw baseband data rates transferred between base-station antennas and the central processing unit (CPU). Decentralized baseband processing (DBP) architecture has recently been proposed to alleviate high interconnect data rates and chip input/output bandwidth bottlenecks. Since the information is not fully shared among each antenna cluster, conventional decentralized detectors suffer from significant performance loss, especially for systems with high overload ratios and/or spatially correlated channels. In this work, we first propose a decentralized groupwise detection paradigm for the star architecture by dividing users into multiple user groups, which can be effectively exploited by factor graph-based message passing algorithms, such as the expectation propagation (EP) algorithm. Then, an efficient message fusion rule is devised based on the product principle of the multivariate Gaussian probability density function at the CPU. To reduce the computational complexity, an approximate groupwise EP (AGW-EP) method is proposed by judiciously selecting reliable constellation vectors during the symbol belief calculation phase. In addition, we extend the proposed methods to the daisy-chain architecture, which requires constant interconnect data rates. Simulation results demonstrate that the proposed groupwise paradigm greatly enhances the performance of the conventional EP detector. Moreover, the proposed decentralized groupwise EP and AGW-EP detection schemes outperform their counterparts, particularly in correlated MIMO channels.


Index Terms-Decentralized baseband processing (DBP), expectation propagation (EP), groupwise, multiuser multiple-input-multiple-output (MU-MIMO).

## I. Introduction

MASSIVE connectivity is a central requirement for next-generation wireless systems that aim to support

[^0]machine-type communications and the Internet of Things (IoT) [1], [2], [3]. According to Cisco, the number of IoT devices envisioned is expected to reach 500 billion by 2030 and will continue to increase exponentially, which imposes critical challenges for the load capacity of IoT networks [4], [5]. Massive multiuser multiple-input-multipleoutput (MU-MIMO) is considered to be one of the main enablers in the fifth-generation ( 5 G ) network and beyond, due to its superiority in increasing spectral efficiency and enhancing link reliability [6], [7], [8]. Equipped with large-scale antennas, the base station (BS) can simultaneously provide service to tens or hundreds of users in the same time-frequency resource [9], [10]. However, most existing uplink detection algorithms are designed based on a centralized baseband processing architecture, which entails prohibitive computational complexity and excessively high raw baseband data rates transferred between BS radio-frequency (RF) units and the central processor. For a 128 BS-antenna massive MU-MIMO system operating at $80-\mathrm{MHz}$ bandwidth with 10 -bit analog-to-digital converters (ADCs), the raw baseband data rates approach 400 $\mathrm{Gb} / \mathrm{s}[11]$. Such high interconnect data rates exceed the existing common public radio interface (CPRI) [12], which is the industry standard for interface between remote radio units and baseband units. Additionally, the data rates scale linearly with the number of antennas, which imposes severe bottlenecks in terms of hardware implementation, chip input/output (I/O) bandwidth, and array scalability [13], [14]. Similar challenges persist for other increasingly popular technologies, including large intelligent surfaces (LISs) [15], [16] and cell-free massive MIMO [17], [18].

To solve the interconnection bottleneck, several different decentralized architectures have been studied in [13], [14], [19], [20], [21], [22], [23], [24], [25], [26], [27], [28], [29], and [30]. In [13], a decentralized baseband processing (DBP) architecture has been proposed to reduce the front-haul data, in which the antenna array is partitioned into multiple independent clusters. Each cluster executes the baseband processing tasks (e.g., channel estimation and data detection) in an independent and parallel manner. Two distinct feedforward architectures, i.e., partially decentralized (PD) and fully decentralized (FD) architectures, have been investigated in [14] to overcome the achievable throughput limitation caused by the transfer latency of DBP. In [19] and [20], a decentralized daisy-chain architecture was designed, which allows data to be consumed close to where it is generated, thus saving energy and throughput. In addition, detailed analyses of
the interconnection data rate, complexity, and latency were presented. Kulkarni et al. [21] proposed two hardware topologies, namely the ring and the star topologies, to discuss the throughput, latency, and interconnect bandwidth tradeoffs. The ring topology offers higher throughput at constant interconnect bandwidth, while the star topology yields lower latency. A generalized framework for centralized/decentralized architectures with WAX decomposition was proposed to evaluate the tradeoff between the level of decentralization and the associated requirement of interconnection bandwidth at the BS [22], [23].

Although DBP architectures can effectively alleviate the interconnect bandwidth bottleneck, their performance deteriorates dramatically in scenarios with a large number of antenna clusters [14], [24]. High-performance detectors and efficient fusion rules are of great importance in the potential application of DBP architectures. The decentralized maximum ratio combining (MRC), zero-forcing (ZF), and minimum mean-square error (MMSE) detectors were considered in [14], followed by the design of the optimal fusion rule. Unfortunately, the decentralized MRC provides poor spectral efficiency for systems with low BS-to-user antenna ratio configurations. The decentralized ZF and MMSE detectors suffer costly computational overheads at each cluster due to matrix inversion operations. To reduce the computational complexity, some inversion-free decentralized detectors, such as coordinate descent (CD) [25], conjugate gradient (CG), and alternating direction method of multipliers (ADMMs) have been proposed to approximate the performance of the MMSE detector [13], [26]. Zhao et al. [27] proposed a block CD (BCD)-based MMSE detection for the decentralized daisy chain architecture, which considers the practical colored noise scenario with a nondiagonal correlation matrix. In [28], a novel multistep fusion algorithm based on Gram matrix splitting was designed for the FD architecture to reduce the performance degradation caused by the weakened diagonal dominance of the Gram matrix in the practical finite-dimensional system. In [14] and [29], a nonlinear decentralized equalizer based on the large-MIMO approximate message passing (LAMA) was proposed for FD and PD architectures, which achieves individually optimal performance in the large-system limit. A decentralized expectation propagation (EP) detector, which approximates the symbol belief by a Gaussian probability density function (PDF) and exchanges the messages (i.e., means and variances) on a factor graph was presented in [24]. Zhang et al. [30] proposed a decentralized Gaussian message passing (GMP) receiver for the DBP architecture. In addition, the partition scheme of the antenna clusters and the convergence of the GMP method are also characterized by fixed-point analysis under the assumption of a large-system limit. Traditional decentralized detectors have mostly focused on the DBP architectures with high BS-touser antenna ratios. However, considering the future need for massive connectivity in the cellular IoT network, a BS may be required to serve a large number of devices. The existing decentralized methods suffer from severe performance deterioration as the number of clusters increases. In addition, the vast majority of DBP-related literature assumes that the propagation channels are spatially uncorrelated. Although
this assumption leads to analytical tractability, practical channels are generally spatially correlated in IoT networks due to the nonuniform radiation patterns of antennas [31]. The performance of decentralized detectors is affected by the spatial correlation of the channel to a large extent.

In this article, we propose a decentralized groupwise detection paradigm for uplink massive MU-MIMO systems with DBP architectures. In contrast to the conventional DBPbased approaches that perform interference cancelation on a user-by-user basis at each cluster, the proposed scheme suppresses the residual interference from all nondesired user groups, while fully exploiting the groupwise information of the desired group. As an illustrative example, the EP algorithm is employed in this work, which is an effective Bayesian computational approach for inferring intractable posterior densities. In the proposed scheme, the users are first divided into multiple groups and the groupwise EP (GW-EP) detection is carried out at the decentralized processor of each antenna cluster. Then, the output local messages are fused at the central processing unit (CPU) based on the judiciously designed message fusion rule. To reduce the computational complexity of the GW-EP detector, we propose an approximate GW-EP (AGWEP) method, in which only a part of more reliable constellation vectors are selected to calculate the symbol beliefs at each iteration. The convergence of the proposed GW-EP algorithm is characterized by state evolution under the assumption of a large-system limit. In addition, we apply the proposed GW-EP/AGW-EP detectors, as well as the message fusion rule to the daisy-chain architecture. In this scheme, the a priori probability of the current cluster is calculated based on the local messages passed from the preceding cluster. The average interconnection data rate between nodes is independent of the number of antenna clusters for the daisy-chain architecture. Numerical results validate that the proposed GW-EP and AGW-EP detectors outperform their conventional counterparts in the star architecture, in particular for scenarios with a large number of clusters and spatially correlated channels. The proposed detectors in the daisy-chain architecture achieve comparable performance to the centralized architecture.

The remainder of this work is organized as follows. The uplink MU-MIMO system model and DBP architectures are described in Section II. In Section III, the detailed derivations of the proposed groupwise detectors are presented. Section IV provides the simulation results. Finally, we conclude this work in Section V.

Notation: Throughout this article, vectors and matrices are represented by lowercase boldface letters and uppercase boldface letters, respectively. The notations $(\cdot)^{\mathrm{T}},(\cdot)^{-1}$, and $(\cdot)^{\mathrm{H}}$ denote the matrix transpose, inversion, and complex conjugate transpose, respectively. $\propto$ stands for equality up to scale. $\mathbb{C}^{N \times K}$ represents the set of $N \times K$ complex matrices. $\operatorname{diag}(\mathbf{x})$ forms a diagonal matrix with the elements of $\mathbf{x}$. $\mathbf{x} \backslash x$ expresses all the enumerations of $\mathbf{x}$ except for $x . \mathbf{I}_{N}$ denotes an identity matrix of size $N \times N . \mathbf{0}$ represents a vector with all elements being $0 . \infty_{N}$ and $\mathbf{0}_{N}$ denote a matrix of size $N \times N$ with all elements being $\infty$ and 0 , respectively. $\mathcal{C} \mathcal{N}(\mathbf{x} ; \boldsymbol{\mu}, \boldsymbol{\Omega})=[1 / \operatorname{det}(\pi \boldsymbol{\Omega})] e^{-(\mathbf{x}-\boldsymbol{\mu})^{\mathrm{H}} \boldsymbol{\Omega}^{-1}(\mathbf{x}-\boldsymbol{\mu})}$ represents a multivariate complex Gaussian distribution with mean vector

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-03.jpg?height=554&width=1534&top_left_y=164&top_left_x=296)
Fig. 1. Block diagram of centralized and DBP architectures. (a) Centralized architecture. The received signal at each antenna is forwarded to the centralized processor through its respective independent front-haul link. (b) Star architecture. Each DBU transmits the local messages to the centralized processor. (c) Daisy-chain architecture. Each DBU transmits the local messages to the next cluster, and only the last cluster has a direct connection with the centralized processor.

TABLE I
List of Main Variables and Their Physical Meanings
| Variable | Description |
| :--- | :--- |
| K | Number of single-antenna users |
| $M$ | Number of antennas at the BS |
| $\mathcal{Q}$ | The power-normalized QAM constellation set |
| C | Number of antenna clusters |
| N | Number of antennas of each antenna cluster |
| $G$ | Number of user groups |
| $K_{g}$ | Number of user in each group |
| s $\in \mathbb{C}^{K}$ | The transmit symbols vector of $K$ users |
| $\mathbf{y}_{c} \in \mathbb{C}^{N}$ | The received signals at the $c$ th cluster |
| $\mathbf{H}_{c} \in \mathbb{C}^{N \times K}$ | The local channel matrix at the $c$ th cluster |
| $M_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}$ | The message propagated from $\mathbf{x}_{g}$ to $f_{c, n}$ |
| $\mathbf{u}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}, \mathbf{V}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}$ | The mean vector and covariance matrix of $M_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}$ |
| $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ | The message propagated from $f_{c, n}$ to $\mathbf{x}_{g}$ |
| $u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}, V_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ | The mean and variance of $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ |
| $\beta_{c}^{t}\left(\mathbf{x}_{g}\right)$ | The symbol belief of $\mathbf{x}_{g}$ at the $c$ th cluster |
| $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right)$ | The multiplication of messages from all FNs to $\mathbf{x}_{g}$ |
| $\mathbf{u}_{c, \mathbf{x}_{g}}^{t}, \mathbf{V}_{c, \mathbf{x}_{g}}^{t}$ | The mean vector and covariance matrix of $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right)$ |
| $\widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}, \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}$ | The posterior mean vector and covariance matrix |
| $\alpha\left(\mathbf{x}_{g}\right)$ | The fused messages at the SN |
| $\gamma_{c}\left(\mathbf{x}_{g}\right)$ | The messages passed from the $c$ th cluster |
| $\boldsymbol{\mu}_{c, \mathbf{x}_{g}}, \boldsymbol{\Omega}_{c, \mathbf{x}_{g}}$ | The mean vector and covariance matrix of $\gamma_{c}\left(\mathbf{x}_{g}\right)$ |


$\boldsymbol{\mu}$ and covariance matrix $\boldsymbol{\Omega}$. For ease of reference, the main variables throughout this article are summarized in Table I, shown at the top of the page.

## II. System Model

## A. Uplink MU-MIMO System Model

Consider an uplink massive MU-MIMO system with $K$ single-antenna users (IoT devices or sensors) and $M$ receiveantennas ( $M>K$ ) at the BS. The standard complex baseband relation between the transmitted and received signals is modeled as

$$
\begin{equation*}
\mathbf{y}=\mathbf{H s}+\mathbf{w} \tag{1}
\end{equation*}
$$

where $\mathbf{H}=\left[\mathbf{h}_{1}, \ldots, \mathbf{h}_{K}\right] \in \mathbb{C}^{M \times K}$ represents the complex channel matrix, $\mathbf{s}=\left[s_{1}, \ldots, s_{K}\right]^{\mathrm{T}} \in \mathcal{Q}^{K}$ denotes the transmit symbol vector of $K$ users, $\mathcal{Q}$ is the power-normalized
quadrature amplitude modulation (QAM) constellation set with cardinality $|\mathcal{Q}|=Q$, and $\mathbf{w} \in \mathbb{C}^{M}$ is the additive white Gaussian noise (AWGN) vector with zero mean and covariance matrix $\sigma_{n}^{2} \mathbf{I}_{M}$.

## B. Decentralized Baseband Processing Architectures

For the centralized architecture, the data/pilot signals received at all antennas are gathered at the centralized processor, which performs baseband processing tasks, e.g., synchronization, channel estimation, and data detection, as depicted in Fig. 1(a). In contrast, partial baseband processing tasks are moved from the CPU to the DBU in DBP architectures to overcome the interconnection bottleneck and reduce the computational complexity in the CPU. In this article, we consider two DBP architectures (i.e., star and daisy-chain architectures), which have been widely adopted in academia [19], [20], [21], [22], [23], [24], [25], [26], [27], [28], [29], [30]. For the star architecture in Fig. 1(b), all clusters are directly and unidirectionally connected to the centralized processor. Each cluster performs local baseband processing tasks in parallel. For the daisy-chain architecture in Fig. 1(c), all clusters are connected sequentially to each other by a dedicated connection and only the final cluster has a direct connection with the centralized processor. ${ }^{1}$ Each cluster utilizes its local information and partial results from the prior cluster in the data detection phase. The DBP architectures partition the $M$ BS antennas into $C$ antenna clusters, where the $c$ th cluster contains $N$ antennas. ${ }^{2}$ Each cluster is associated with an independent baseband processor. The channel matrix $\mathbf{H}$ is divided rowwise into $C$ blocks as $\mathbf{H}=\left[\mathbf{H}_{1}^{\mathrm{T}}, \ldots, \mathbf{H}_{C}^{\mathrm{T}}\right]^{\mathrm{T}}$ with the local channel matrix $\mathbf{H}_{c} \in \mathbb{C}^{N \times K}$. The received signals $\mathbf{y}_{c} \in \mathbb{C}^{N}$ at the $c$ th cluster can be rewritten as

$$
\begin{equation*}
\mathbf{y}_{c}=\mathbf{H}_{c} \mathbf{s}+\mathbf{w}_{c} \tag{2}
\end{equation*}
$$

where $\mathbf{w}_{c} \in \mathbb{C}^{N}$ represents the local AWGN vector.

[^1]![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-04.jpg?height=448&width=721&top_left_y=193&top_left_x=244)
Fig. 2. Factor graph of the decentralized GW-EP detector for the star architecture with $M=8, K=4, G=2$, and $C=2$.

## III. Proposed Decentralized Groupwise EP Detector

Since the information [e.g., the receive signals, noise samples, and channel state information (CSI)] is not fully shared among antenna clusters, conventional DBP-based detectors suffer from considerable performance loss, especially for DBP architectures with a large number of clusters [24]. We propose a groupwise scheme to improve the performance of the system with DBP architectures. The core idea of the groupwise scheme is to fully exploit the groupwise information and jointly suppress residual interferences for the users' signals in each user group. In the proposed groupwise detection scheme, we divide the users into $G$ user groups. ${ }^{3}$ The channel matrix at each cluster is partitioned columnwise into $G$ group, e.g., $\mathbf{H}_{c}=\left[\mathbf{H}_{c, 1}, \ldots, \mathbf{H}_{c, G}\right]$ with $\mathbf{H}_{c, g} \in \mathbb{C}^{N \times K_{g}}$. The corresponding input-output relation of the $c$ cluster is expressed as

$$
\begin{equation*}
\mathbf{y}_{c}=\sum_{g} \mathbf{H}_{c, g} \mathbf{x}_{g}+\mathbf{w}_{c} \tag{3}
\end{equation*}
$$

where $\mathbf{x}_{g}=\left[s_{(g-1) K_{g}+1}, \ldots, s_{g K_{g}}\right]^{\mathrm{T}} \in \mathbb{C}^{K_{g}}$ is the transmitted signal at the $g$ th user group. As an illustrative example, we apply the groupwise scheme to the EP algorithm.

## A. Decentralized GW-EP Detector for Star Architecture

1) GW-EP Detector: Without loss of generality, we take the $c$ th cluster as an illustrative example. According to (3), the decentralized GW-EP detection of the uplink MIMO system can be represented by a factor graph as illustrated in Fig. 2. In the factor graph, variable nodes (VNs), factor nodes (FNs), and sum nodes (SNs) represent the user groups, ${ }^{4}$ likelihood functions, and message fusions, respectively. The joint distribution $P\left(\mathbf{s}, \mathbf{y}_{c}\right)$ is factorized as [34]

$$
\begin{align*}
P\left(\mathbf{s}, \mathbf{y}_{c}\right) & =P(\mathbf{s}) P\left(\mathbf{y}_{c} \mid \mathbf{s}\right) \\
& =\prod_{g} P\left(\mathbf{x}_{g}\right) \prod_{n} P\left(y_{c, n} \mid \mathbf{x}_{g}\right) . \tag{4}
\end{align*}
$$

[^2]The likelihood function $P\left(y_{c, n} \mid \mathbf{x}_{g}\right)$ is given by

$$
\begin{equation*}
P\left(y_{c, n} \mid \mathbf{x}_{g}\right) \propto \exp \left(-\frac{1}{\sigma_{n}^{2}}\left|y_{c, n}-\mathbf{e}_{c, n}^{\mathrm{T}} \sum_{g} \mathbf{H}_{c, g} \mathbf{x}_{g}\right|^{2}\right) \tag{5}
\end{equation*}
$$

where $\mathbf{e}_{c, n}$ denotes the $n$th column vector of $\mathbf{I}_{N}$. Let $M_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}$ represent the message propagated from $\mathbf{x}_{g}$ to $f_{c, n}$ at the $t$ th iteration ( $t<T_{\max }$ ), and $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ denote the message from the opposite direction. The message passing rules between VNs and FNs are given by [32]

$$
\begin{align*}
M_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}\left(\mathbf{x}_{g}\right) & =P\left(\mathbf{x}_{g}\right) \prod_{n^{\prime} \neq n} M_{f_{c, n^{\prime}} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)  \tag{6}\\
M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\left(\mathbf{x}_{g}\right) & =\sum_{\mathbf{x} \backslash \mathbf{x}_{g}} P\left(y_{c, n} \mid \mathbf{x}_{g}\right) \prod_{g^{\prime} \neq g} M_{\mathbf{x}_{g^{\prime}} \rightarrow f_{c, n}}^{t}\left(\mathbf{x}_{g^{\prime}}\right) \tag{7}
\end{align*}
$$

where $P\left(\mathbf{x}_{g}\right)=1 / Q^{K_{g}}$ is the a priori probability of $\mathbf{x}_{g}$. Since the symbol vectors take on values in the discrete constellation set $\mathcal{Q}$, the computational complexity of $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\left(\mathbf{x}_{g}\right)$ grows exponentially. To simplify the implementation of the sum-product algorithm, the concept of symbol belief based on EP is utilized to calculate approximate messages $M_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}\left(\mathbf{x}_{g}\right)$ and $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\left(\mathbf{x}_{g}\right)$. EP is an algorithm for approximate statistical inference, which has extensive cutting-edge applications in multiuser detection, pattern recognition, and machine learning [24], [33], [34], [35], [36], [37]. The key idea of the EP algorithm is to approximate the intricate posterior distribution with a much simpler complex Gaussian distribution. Thus, the complicated symbol beliefs update can be replaced by mean vector and covariance matrix propagation [35]. The symbol belief (i.e., the approximate a posteriori probability) of $\mathbf{x}_{g}$ at the $c$ th cluster is represented as

$$
\begin{equation*}
\beta_{c}^{t}\left(\mathbf{x}_{g}\right)=\frac{P_{0}\left(\mathbf{x}_{g}\right) \prod_{n} M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)}{\sum_{\mathbf{x}_{g} \in \mathcal{Q}^{K_{g}}} P_{0}\left(\mathbf{x}_{g}\right) \prod_{n} M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)} \tag{8}
\end{equation*}
$$

where $P_{0}\left(\mathbf{x}_{g}\right)=1 / Q^{K_{g}}$ is the a priori probability of $\mathbf{x}_{g}$ at the $c$ th cluster. We consider $\mathbf{x}_{g}$ as a vector of continuous random variables. Therefore, the message $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\left(\mathbf{x}_{g}\right)$ is approximated as a complex Gaussian PDF $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\left(\mathbf{x}_{g}\right)= \mathcal{C N}\left(\mathbf{H}_{c, g} \mathbf{x}_{g} ; u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}, v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\right)$. The multiplicative message $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right)=\prod_{n} M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)$ is assumed to follow a continuous multivariate complex Gaussian PDF $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right) \propto \mathcal{C} \mathcal{N}\left(\mathbf{x}_{g} ; \mathbf{u}_{c, \mathbf{x}_{g}}^{t}, \mathbf{V}_{c, \mathbf{x}_{g}}^{t}\right)$, where the covariance matrix and mean vector are computed, respectively, as

$$
\begin{align*}
\left(\mathbf{V}_{c, \mathbf{x}_{g}}^{t}\right)^{-1} & =\sum_{n} \frac{1}{v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \\
& =\mathbf{H}_{c, g}^{\mathrm{H}} \Lambda_{c}^{t-1} \mathbf{H}_{c, g}  \tag{9}\\
\mathbf{u}_{c, \mathbf{x}_{g}}^{t} & =\mathbf{V}_{c, \mathbf{x}_{g}}^{t} \sum_{n} \frac{u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n} \\
& =\mathbf{V}_{c, \mathbf{x}_{g}}^{t} \mathbf{H}_{c, g}^{\mathrm{H}} \Delta_{c}^{t-1} \tag{10}
\end{align*}
$$

where $\Lambda^{t-1}=\operatorname{diag}\left(1 / v_{f_{c, 1} \rightarrow \mathbf{x}_{g}}^{t-1}, \ldots, 1 / v_{f_{c, N} \rightarrow \mathbf{x}_{g}}^{t-1}\right)$ and $\Delta^{t-1}= \left[u_{f_{c, 1} \rightarrow \mathbf{x}_{g}}^{t-1} / v_{f_{c, 1} \rightarrow \mathbf{x}_{g}}^{t-1}, \ldots, u_{f_{c, N} \rightarrow \mathbf{x}_{g}}^{t-1} / v_{f_{c, N} \rightarrow \mathbf{x}_{g}}^{t-1}\right]^{\mathrm{T}}$. The approximate
symbol belief is obtained by minimizing the KL divergence $\mathrm{KL}\left(\beta_{c}^{t}\left(\mathbf{x}_{g}\right) \| \widetilde{\beta}_{c}^{t}\left(\mathbf{x}_{g}\right)\right)$ [34], which obeys a continuous multivariate complex Gaussian PDF $\widetilde{\beta}_{c}^{t}\left(\mathbf{x}_{g}\right)=\mathcal{C} \mathcal{N}\left(\mathbf{x}_{g} ; \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}, \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}\right)$ with

$$
\begin{align*}
\widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t} & =\mathbb{E}_{\beta_{c}^{t}\left(\mathbf{x}_{g}\right)}\left[\mathbf{x}_{g}\right]  \tag{11}\\
\widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t} & =\mathbb{E}_{\beta_{c}^{t}\left(\mathbf{x}_{g}\right)}\left[\mathbf{x}_{g} \mathbf{x}_{g}^{\mathrm{H}}\right]-\widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}\left(\widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}\right)^{\mathrm{H}} . \tag{12}
\end{align*}
$$

Based on (6) and (8), the messages from VNs to FNs can be computed as

$$
\begin{align*}
M_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}\left(\mathbf{x}_{g}\right) & \propto \frac{\beta_{c}^{t}\left(\mathbf{x}_{g}\right)}{M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)} \\
& \approx \frac{\widetilde{\beta}_{c}^{t}\left(\mathbf{x}_{g}\right)}{M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)} \\
& =\mathcal{C} \mathcal{N}\left(\mathbf{x}_{g} ; \mathbf{u}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}, \mathbf{V}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}\right) \tag{13}
\end{align*}
$$

where

$$
\begin{align*}
& \mathbf{V}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}=\left(\left(\widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}\right)^{-1}-\frac{\mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}}\right)^{-1}  \tag{14}\\
& \mathbf{u}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}=\mathbf{V}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}\left(\left(\widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}\right)^{-1} \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}-\frac{u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n}\right) . \tag{15}
\end{align*}
$$

Utilizing (5) and (7), we compute the mean and variance of $M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}\left(\mathbf{x}_{g}\right)$ from FNs to VNs as

$$
\begin{align*}
& u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=y_{c, n}-\mathbf{e}_{c, n}^{\mathrm{T}} \sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}} \mathbf{u}_{\mathbf{x}_{g^{\prime}} \rightarrow f_{c, n}}^{t}  \tag{16}\\
& v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=\sigma_{n}^{2}+\mathbf{e}_{c, n}^{\mathrm{T}}\left(\sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}} \mathbf{V}_{\mathbf{x}_{g^{\prime}} \rightarrow f_{c, n}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}}\right) \mathbf{e}_{c, n} . \tag{17}
\end{align*}
$$

To avoid the matrix inversion in (14) and (15), by substituting (14) and (15) into (16) and (17), we rewrite the messages $u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ and $v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ as

$$
\begin{align*}
& u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=y_{c, n}-\sum_{g^{\prime}} \phi_{c, n, g^{\prime}}^{t} \varphi_{c, n, g^{\prime}}^{t}+\phi_{c, n, g}^{t} \varphi_{c, n, g}^{t}  \tag{18}\\
& v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=\sigma_{n}^{2}+\sum_{g^{\prime}} \psi_{c, n, g^{\prime}}^{t} \varphi_{c, n, g^{\prime}}^{t}-\psi_{c, n, g}^{t} \varphi_{c, n, g}^{t} \tag{19}
\end{align*}
$$

where $\phi_{c, n, g}^{t}=\underset{\sim}{\mathbf{e}_{c, n}^{\mathrm{T}}} \mathbf{H}_{c, g} \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}-\left(u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1} / v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\right) \psi_{c, n, g}^{t}$, $\psi_{c, n, g}^{t}=\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n}$, and $\varphi_{c, n, g}^{t}=\left(v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1} /\right. \left.\left[v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}-\psi_{c, n, g}^{t}\right]\right)$ are all scalar quantities. The detailed derivation can be found in the Appendix.
2) Fusion of the Local Messages: When the maximum number of iterations is reached, the local messages of each cluster are fused at the CPU. The fused message of $g$ th user group at SNs is computed based on the product principle of multivariate Gaussian PDF as

$$
\begin{align*}
\alpha\left(\mathbf{x}_{g}\right) & \propto \prod_{c} \alpha_{c}^{T_{\max }}\left(\mathbf{x}_{g}\right)=\prod_{c} \mathcal{C} \mathcal{N}\left(\mathbf{x}_{g} ; \mathbf{u}_{c, \mathbf{x}_{g}}^{T_{\max }}, \mathbf{V}_{c, \mathbf{x}_{g}}^{T_{\max }}\right) \\
& =\mathcal{C N}\left(\mathbf{x}_{g} ; \mathbf{u}_{\mathbf{x}_{g}}, \mathbf{V}_{\mathbf{x}_{g}}\right) \tag{20}
\end{align*}
$$

```
Algorithm 1 Decentralized GW-EP Detector for the Star
Architecture
    Input: $\mathbf{H , y}, \sigma_{n}^{2}, T_{\text {max }}$
    Initialization: $u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{0}=0, v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=+\infty, P_{0}\left(\mathbf{x}_{g}\right)=$
    $1 / Q^{K_{g}}$
    Each cluster carries out the GW-EP detection
    for $t=1, \ldots, T_{\text {max }}$ do
        Compute $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right)$ via (9) and (10).
        Compute $\beta_{c}^{t}\left(\mathbf{x}_{g}\right)$ via (8).
        Compute $\widetilde{\beta}_{c}^{t}\left(\mathbf{x}_{g}\right), \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}$, and $\widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}$ via (11) and (12).
        Compute $u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ and $v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ via (18) and (19).
    end for
    Fusion of the Decentralized Local Messages
    Compute $\alpha\left(\mathbf{x}_{g}\right)$ via (20), (21), (22).
    Compute the a posteriori probabilities $\beta\left(\mathbf{x}_{g}\right)$ via (20) and
    (23).
    Compute the estimated soft symbol vector $\hat{\mathbf{x}}_{g}$ via (24).
    Output: $\hat{\mathbf{x}}_{g}$
```

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-05.jpg?height=384&width=705&top_left_y=1007&top_left_x=1162)
Fig. 3. Factor graph of the decentralized GW-EP detector for the daisy-chain architecture with $M=8, K=4, G=2$, and $C=2$.

where the covariance matrix and mean vector are given, respectively, by

$$
\begin{align*}
& \mathbf{V}_{\mathbf{x}_{g}}=\left(\sum_{c}\left(\mathbf{V}_{c, \mathbf{x}_{g}}^{T_{\max }}\right)^{-1}\right)^{-1}  \tag{21}\\
& \mathbf{u}_{\mathbf{x}_{g}}=\mathbf{V}_{\mathbf{x}_{g}}\left(\sum_{c}\left(\mathbf{V}_{c, \mathbf{x}_{g}}^{T_{\max }}\right)^{-1} \mathbf{u}_{c, \mathbf{x}_{g}}^{T_{\max }}\right) . \tag{22}
\end{align*}
$$

The symbol belief at the CPU can be calculated as

$$
\begin{equation*}
\beta\left(\mathbf{x}_{g}=\boldsymbol{\xi}\right)=\frac{P_{0}\left(\mathbf{x}_{g}=\boldsymbol{\xi}\right) \alpha\left(\mathbf{x}_{g}=\boldsymbol{\xi}\right)}{\sum_{\boldsymbol{\xi}^{\prime} \in \mathcal{Q}^{K_{g}}} P_{0}\left(\mathbf{x}_{g}=\boldsymbol{\xi}^{\prime}\right) \alpha\left(\mathbf{x}_{g}=\boldsymbol{\xi}^{\prime}\right)} . \tag{23}
\end{equation*}
$$

Finally, the estimated soft symbol vector of the $g$ th group is computed as

$$
\begin{equation*}
\hat{\mathbf{x}}_{g}=\sum_{\boldsymbol{\xi} \in \mathcal{Q}^{K_{g}}} \boldsymbol{\xi} \beta\left(\mathbf{x}_{g}=\boldsymbol{\xi}\right) . \tag{24}
\end{equation*}
$$

The proposed decentralized GW-EP detector for the star architecture is summarized in Algorithm 1.

## B. Decentralized GW-EP Detector for the Daisy-Chain Architecture

1) GW-EP Detector: The factor graph of the proposed GW-EP method for the daisy-chain architecture is illustrated in Fig. 3. Each cluster computes partial information locally, fuses
it with received local messages from the preceding cluster, and then forwards the combined messages to the next cluster. Based on the mean vectors and covariance matrices of the multivariate Gaussian PDF passed from the preceding cluster, the a priori probability is first calculated at each cluster as

$$
\begin{equation*}
P_{c}\left(\mathbf{x}_{g}\right)=\frac{P_{0}\left(\mathbf{x}_{g}\right) \gamma_{c-1}\left(\mathbf{x}_{g}\right)}{\sum_{\mathbf{x}_{g} \in \mathcal{Q}^{K_{g}}} P_{0}\left(\mathbf{x}_{g}\right) \gamma_{c-1}\left(\mathbf{x}_{g}\right)} \tag{25}
\end{equation*}
$$

where $P_{0}\left(\mathbf{x}_{g}\right)=1 / Q^{K_{g}}$ is the initial a priori probability of all clusters, $\gamma_{0}=\mathcal{C} \mathcal{N}\left(\mathbf{x}_{g} ; \mu_{0, \mathbf{x}_{g}}, \Omega_{0, \mathbf{x}_{g}}\right)$ with $\boldsymbol{\mu}_{0, \mathbf{x}_{g}}=\mathbf{0}$ and $\boldsymbol{\Omega}_{0, \mathbf{x}_{g}}=+\infty{ }_{K_{g}}$. At each iteration of the GW-EP detector, the symbol belief of $\mathbf{x}_{g}$ is calculated as

$$
\begin{align*}
\beta_{c}^{t}\left(\mathbf{x}_{g}\right) & =\frac{P_{c}\left(\mathbf{x}_{g}\right) \prod_{n} M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)}{\sum_{\mathbf{x}_{g} \in \mathcal{Q}^{K_{g}}} P_{c}\left(\mathbf{x}_{g}\right) \prod_{n} M_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}\left(\mathbf{x}_{g}\right)} \\
& =\frac{P_{c}\left(\mathbf{x}_{g}\right) \alpha_{c}^{t}\left(\mathbf{x}_{g}\right)}{\sum_{\mathbf{x}_{g} \in \mathcal{Q}^{K_{g}}} P_{c}\left(\mathbf{x}_{g}\right) \alpha_{c}^{t}\left(\mathbf{x}_{g}\right)} \tag{26}
\end{align*}
$$

where the mean vector and covariance matrix of $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right)$ are computed based on (9) and (10), respectively.
2) Fusion of the Local Messages: When the maximum number of iterations is reached, the local messages $\alpha_{c}^{T_{\text {max }}}\left(\mathbf{x}_{g}\right)$ of the current cluster and the messages $\gamma_{c-1}\left(\mathbf{x}_{g}\right)$ passed from the preceding cluster are fused at the current DBU

$$
\begin{align*}
\gamma_{c}\left(\mathbf{x}_{g}\right) & =\alpha_{c}^{T_{\max }}\left(\mathbf{x}_{g}\right) \gamma_{c-1}\left(\mathbf{x}_{g}\right) \\
& =\mathcal{C N}\left(\mathbf{x}_{g} ; \boldsymbol{\mu}_{c, \mathbf{x}_{g}}, \boldsymbol{\Omega}_{c, \mathbf{x}_{g}}\right) \tag{27}
\end{align*}
$$

where the combined covariance matrix and mean vector are given, respectively, by

$$
\begin{align*}
\boldsymbol{\Omega}_{c, \mathbf{x}_{g}} & =\left(\left(\mathbf{V}_{c, \mathbf{x}_{g}}^{T_{\max }}\right)^{-1}+\left(\boldsymbol{\Omega}_{c-1, \mathbf{x}_{g}}\right)^{-1}\right)^{-1}  \tag{28}\\
\boldsymbol{\mu}_{c, \mathbf{x}_{g}} & =\boldsymbol{\Omega}_{c, \mathbf{x}_{g}}\left(\left(\mathbf{V}_{c, \mathbf{x}_{g}}^{T_{\max }}\right)^{-1} \mathbf{u}_{c, \mathbf{x}_{g}}^{T_{\max }}+\left(\boldsymbol{\Omega}_{c-1, \mathbf{x}_{g}}\right)^{-1} \boldsymbol{\mu}_{c-1, \mathbf{x}_{g}}\right) . \tag{29}
\end{align*}
$$

Finally, the last cluster transmits its messages to the CPU, and the symbol belief $\beta\left(\mathbf{x}_{g}\right)$ of the $g$ th group can be calculated based on (25) by replacing $\gamma_{c-1}\left(\mathbf{x}_{g}\right)$ with $\gamma_{C}\left(\mathbf{x}_{g}\right)$ as

$$
\begin{equation*}
\beta\left(\mathbf{x}_{g}\right)=\frac{P_{0}\left(\mathbf{x}_{g}\right) \gamma_{C}\left(\mathbf{x}_{g}\right)}{\sum_{\mathbf{x}_{g} \in \mathcal{Q}^{K_{g}}} P_{0}\left(\mathbf{x}_{g}\right) \gamma_{C}\left(\mathbf{x}_{g}\right)} . \tag{30}
\end{equation*}
$$

The soft symbol vector of the $g$ th group can be computed based on (24). The proposed decentralized GW-EP detector for the daisy-chain architecture is summarized in Algorithm 2.

## C. Approximate Groupwise EP Detector

With a closer observation of (8) and (26), we find that the main computational complexity of the GW-EP algorithm lies in the calculation of symbol beliefs, which depends on the modulation order $Q$ and the number of users $K_{g}$ per group. To reduce the computational complexity, we propose an AGW-EP method by judiciously selecting the most reliable constellation vectors (i.e., with larger symbol beliefs) according to symbol beliefs in the last iteration $\beta_{c}^{t-1}\left(\mathbf{x}_{g}\right)$. The number of reliable constellation vectors is set as $K_{g} Q$ for the AGW-EP method, thus exhibiting the same order of computational complexity as

```
Algorithm 2 Decentralized GW-EP Detector for the Daisy-
Chain Architecture
    Input: $\mathbf{H , y}, \sigma_{n}^{2}, T_{\text {max }}$
    Initialization: $u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{0}=0, v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=+\infty, P_{0}\left(\mathbf{x}_{g}\right)=$
    $1 / Q^{K_{g}}, \boldsymbol{\mu}_{0, \mathbf{x}_{g}}=\mathbf{0}, \boldsymbol{\Omega}_{0, \mathbf{x}_{g}}=+\infty_{K_{g}}$
    for $c=1, \ldots, C$ do
        Compute the a priori probability $P_{c}\left(\mathbf{x}_{g}\right)$ via (25).
        for $t=1, \cdots, T_{\text {max }}$ do
            Compute $\alpha_{c}^{t}\left(\mathbf{x}_{g}\right)$ via (9) and (10).
            Compute $\beta_{c}^{t}\left(\mathbf{x}_{g}\right)$ via (26).
            Compute $\tilde{\beta}_{c}^{t}\left(\mathbf{x}_{g}\right), \quad \tilde{\mathbf{u}}_{c, \mathbf{x}_{g}}^{t}$, and $\tilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}$ via (11)
    and (12).
            Compute $u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ and $v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$ via (18) and (19).
        end for
    Fusion of the Decentralized Local Messages
        Compute $\gamma_{c}\left(\mathbf{x}_{g}\right)$ via (27), (28), (29).
    end for
    Compute the estimated soft symbol vector $\hat{\mathbf{x}}_{g}$ via (24).
    Output: $\hat{\mathbf{x}}_{g}$
```

the conventional EP detector. In fact, the performance loss due to the choice of $K_{g} Q$ is marginal for both DBP architectures, as demonstrated later in Section IV.

Remark 1: For the daisy-chain architecture, the computational complexity of $\beta_{c}^{t}\left(\mathbf{x}_{g}\right)$ can be further reduced since the latter cluster can exploit the a priori information (i.e., a posteriori output) of the preceding cluster.

## D. Convergence Analysis

The convergence of the proposed decentralized GW-EP algorithm is characterized by the state evolution, which derives the distribution of messages at the ( $t+1$ ) th iteration according to that of the $t$ th iteration [36], [37]. Based on the large system limit (i.e., $K \rightarrow+\infty, N \rightarrow+\infty$, and $\lambda=N / K \geq 1$ being a fixed constant), we assume $\mathbf{V}_{\mathbf{x} \rightarrow f_{c}}=\lim _{t \rightarrow+\infty}{\underset{\sim}{V}}_{\mathbf{x}_{g} \rightarrow f_{c, n}}^{t}$, $v_{f_{c} \rightarrow \mathbf{x}}=\lim _{t \rightarrow+\infty} v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}$, and $\tilde{\mathbf{V}}_{c, \mathbf{x}}=\lim _{t \rightarrow+\infty} \tilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t}$ for $\forall n \in[1, \ldots, N]$ and $\forall g \in[1, \ldots, G]$.

Proposition 1: At the VNs, the output is given by

$$
\begin{equation*}
\mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \approx \tilde{\mathbf{V}}_{c, \mathbf{x}} \tag{31}
\end{equation*}
$$

Proof: By submitting (17) into (14), we have

$$
\begin{gather*}
\mathbf{V}_{\mathbf{x} \rightarrow f_{c}}=\left(\left(\widetilde{\mathbf{V}}_{c, \mathbf{x}}\right)^{-1}-\frac{\mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g}}{\sigma_{n}^{2}+\mathbf{e}_{c, n}^{\mathrm{T}}\left(\sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}} \mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}}\right) \mathbf{e}_{c, n}}\right)^{-1} \\
=\left(\left(\widetilde{\mathbf{V}}_{c, \mathbf{x}}\right)^{-1}-\frac{\mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g}}{\sigma_{n}^{2}+(G-1) \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right)^{-1} \stackrel{(a)}{\approx} \widetilde{\mathbf{V}}_{c, \mathbf{x}} \tag{32}
\end{gather*}
$$

where ( $a$ ) holds due to the fact that the second term approaches zero when $G=K / K_{g} \rightarrow+\infty$. $\square$

Proposition 2: At the FNs, we have

$$
\begin{equation*}
\mathbf{V}_{c, \mathbf{x}} \approx \frac{\sigma_{n}^{2}+G \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n}}{N} \mathbf{I}_{K_{g}} \tag{33}
\end{equation*}
$$

where $\mathbf{V}_{c, \mathbf{x}}=\lim _{t \rightarrow+\infty} \mathbf{V}_{c, \mathbf{x}_{g}}$ for $\forall g \in[1, \ldots, G]$.

TABLE II
Computational Complexity
| CG | $(T-1)(8 C N K+10 C K+2 K)+12 C N K+4 C K+4 K$ |
| :--- | :--- |
| MRC | $C\left(K^{3}+3 K^{2}+5 K\right)+N K^{2}+N K$ |
| MMSE | $C\left(\frac{10}{3} K^{3}+\frac{7}{2} K^{2}+2 K\right)+N K^{2}+N K$ |
| LAMA | $C T_{\text {max }}\left(6 K Q+(K+1)^{2}\right)+C\left(N K^{2}+N K+4 K+2\right)+N$ |
| GMP/EP | $C T_{\text {max }} K(6 N+5 Q+4)+4 Q K+2 C K+2 K$ |
| GW-EP | $\begin{gathered} \hline T_{\max } C G\left(Q^{K_{g}}\left(\frac{5}{2} K_{g}^{2}+\frac{1}{2} K_{g}\right)+3 K_{g}^{2} N+3 K_{g} N+4\right)+ \\ 2(C+1) G K_{g}^{2}+G Q^{K_{g}}\left(K_{g}+1\right)^{2} \\ \hline \end{gathered}$ |
| AGW-EP | $\begin{gathered} T_{\max } C G\left(Q K_{g}\left(\frac{5}{2} K_{g}^{2}+\frac{1}{2} K_{g}\right)+3 K_{g}^{2} N+3 K_{g} N+4\right)+ \\ C G Q^{K_{g}}\left(\frac{5}{2} K_{g}^{2}+\frac{1}{2} K_{g}\right)+2(C+1) G K_{g}^{2}+G Q^{K_{g}}\left(K_{g}+1\right)^{2} \\ \hline \end{gathered}$ |


Proof: By submitting (17) into (9), we have

$$
\begin{align*}
\mathbf{V}_{c, \mathbf{x}} & =\left(\frac{\mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{H}_{c, g}}{v_{f_{c} \rightarrow \mathbf{x}}}\right)^{-1}=v_{f_{c} \rightarrow \mathbf{x}}\left(\mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{H}_{c, g}\right)^{-1} \\
& =\left(\sigma_{n}^{2}+G \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n}\right)\left(\mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{H}_{c, g}\right)^{-1} \\
& \approx \frac{\sigma_{n}^{2}+G \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n}}{N} \mathbf{I}_{K_{g}} . \tag{34}
\end{align*}
$$ $\square$

Remark 2: When the symbol belief [cf. (8)] for a certain element converges to 1 , i.e., $\beta_{c}^{t}\left(\mathbf{x}_{g}=\boldsymbol{\xi}\right)=1$, we obtain $\mathbf{V}_{\mathbf{x} \rightarrow f_{c}} \approx \tilde{\mathbf{V}}_{c, \mathbf{x}} \rightarrow \mathbf{0}_{K_{g}}$ according to (11), (12), and (32). Therefore, $v_{f_{c} \rightarrow \mathbf{x}} \rightarrow \sigma_{n}^{2}$ is obtained based on (17). The gap between $v_{f_{c} \rightarrow \mathbf{x}}$ and $\sigma_{n}^{2}$ can be used to evaluate the performance of the proposed detectors. In Section IV, the state evolution of $v_{f_{c} \rightarrow \mathbf{x}}$ will be tracked to validate the convergence and the performance of the proposed detectors. The bit error rate (BER) performance is uniquely determined at the fixed-point as the iteration increases [38].

## E. Computational Complexity Analysis

The computational complexity is assessed in terms of the number of complex multiplications [39]. The computational complexity of the decentralized GW-EP detector can be divided into three parts, i.e., the calculation of messages between FNs and VNs: $T_{\text {max }} C G\left(Q^{K_{g}}\left([5 / 2] K_{g}^{2}+[1 / 2] K_{g}\right)+\right. \left.3 K_{g}^{2} N+3 K_{g} N+4\right)$, the calculation of fusion of the decentralized message: $2(C+1) G K_{g}^{2}$, and the computation of the a posteriori probabilities at VNs: $G Q^{K_{g}}\left(K_{g}+1\right)^{2}$. In addition, the computational complexity of the MRC, CG [26], MMSE [14], GMP [30], and LAMA [29] detectors is also provided in Table II.

## F. Interconnect Data Rates

The average interconnect data rates of the proposed detectors are measured in terms of the number of real symbols entered into the CPU. For the centralized architecture, each antenna forwards the received data signal $y_{m}$ to the CPU, which corresponds to two real symbols. This amounts to $2 M$ real symbols being transmitted from all antennas to the CPU, which is proportionate to the number of BS antennas. For the star architecture, each antenna cluster sends $\mathbf{u}_{c, \mathbf{x}_{g}}^{T_{\text {max }}}$ and $\mathbf{V}_{c, \mathbf{x}_{g}}^{T_{\text {max }}}$ to the CPU, where $g \in[1, \ldots, G]$. The total number of real symbols amounts to $C K\left(2+K_{g}\right)$. For the daisy-chain architecture, the messages $\boldsymbol{\mu}_{c, \mathbf{x}_{g}}$ and $\boldsymbol{\Omega}_{c, \mathbf{x}_{g}}$ are passed through the
nodes (DBU or CPU) sequentially. The number of real symbols entered into the CPU is $K\left(2+K_{g}\right)$, which is independent of the number of antenna clusters.

## IV. Simulation Results

In this section, simulation results are presented to verify the validity of the proposed decentralized GW-EP/AGW-EP detectors for the uplink massive MU-MIMO system.

## A. Simulations Parameters

We consider two different channel models, i.e., uncorrelated and correlated Rayleigh fading channels. For the uncorrelated Rayleigh fading channel, $\mathbf{h}_{k}$ is distributed as $\mathbf{h}_{k} \sim \mathcal{C} \mathcal{N}\left(0, \mathbf{I}_{M}\right)$, where each entry of $\mathbf{h}_{k}$ is assumed to be an i.i.d. Gaussian random variable with zero mean and unit variance. For the correlated Rayleigh fading channel, we consider a uniform linear array (ULA) at the BS modeled by the exponential correlation model. $\mathbf{h}_{k}$ is modeled as $\mathbf{h}_{k} \sim \mathcal{C} \mathcal{N}\left(\mathbf{0}, \mathbf{C}_{k}\right)$, where $\mathbf{C}_{k}$ is the spatial correlation matrix. The element at the $a$ th row and the $b$ th column of $\mathbf{C}_{k}$ is expressed as $\left[\mathbf{C}_{k}\right]_{a, b}=\rho^{-|b-a|} e^{i \delta_{k}(b-a)}$, where $0 \leq \rho \leq 1$ is the correlation coefficient between adjacent antennas and $-\pi \leq \delta_{k}<\pi$ is the angle-of-arrival from the $k$ th user to BS. In this work, perfect CSI is assumed to be available at the receiver. The QPSK and 16-QAM modulation are adopted. Unless otherwise stated, the number of users in each group is set to be $K_{g}=2$ for the proposed GW-EP/AGW-EP methods. The turbo code with code rate $1 / 2$ is considered. $T_{\text {max }}$ is set to be 6 for the iterative detectors. The MMSE, LAMA, MRC, CG, and GMP detectors are provided as baselines for comparison.

## B. Simulation Results

Fig. 4 illustrates the BER performance of different detectors as a function of antenna cluster number $C$ for the star architecture with $M=96, K=12$, and 16-QAM. For the spatially uncorrelated channel, Fig. 4(a) shows that all decentralized detectors (i.e., $C>1$ ) suffer BER performance loss compared with their centralized counterparts (i.e., $C=1$ ). This can be interpreted by the fact that the global information sharing is limited and each cluster only accesses local CSI and local received data. With the increase of $C$, the BER performance of decentralized linear methods deteriorates drastically compared with nonlinear algorithms. As expected, the proposed GW-EP detector achieves the best BER performance. The performance gap between the GW-EP and AGW-EP methods is almost indistinguishable. ${ }^{5}$ For the spatially correlated channel, similar trends are also observed in Fig. 4(b).

Figs. 5 and 6 illustrate the BER performance comparison of different decentralized detectors for the star architecture when $M=96$ and $K=12$. For the spatially uncorrelated channel, it can be seen from Fig. 5(a) that the GW-EP detector outperforms its counterparts, especially for the scenarios with large $C$ and high modulation order. For $C=4$ and 16-QAM, the proposed GW-WP detector obtains performance gains of

[^3]![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-08.jpg?height=1193&width=710&top_left_y=180&top_left_x=249)
Fig. 4. BER performance of different detectors as a function of clusters number $C$ with different SNR ( $M=96, K=12$, and 16-QAM). (a) Uncorrelated. (b) Correlated, $\rho=0.4$.

about $0.5,0.7,1,2$, and 2.4 dB , respectively, over the conventional EP, GMP, LAMA, MMSE, and CG counterparts at $\mathrm{BER}=10^{-3}$. The performance loss of the AGW-EP detector is almost negligible compared with the GW-EP method. The results in Fig. 5(b) show that the performance gains of the GW-EP method are more pronounced when $C=8$. Similar phenomena are also observed for the spatially correlated channel with $\rho=0.4$, and the GW-EP method achieves the best BER performance as illustrated in Fig. 6(a) and (b).

Fig. 7 depicts the BER performance of the GW-EP and AGW-EP detectors with different values of $K_{g}$ for the star architecture when $M=64$ and $K=8$. For the uncorrelated channel, Fig. 7 shows that the BER performance improves significantly with the increased $K_{g}$, especially for the star architecture with a large number of antenna clusters. For $C=8$, the proposed GW-EP method with $K_{g}=2$ and $K_{g}=4$ yield about 1.2 and $3-\mathrm{dB}$ gains at $\mathrm{BER}=10^{-4}$, respectively, over the conventional one (i.e., $K_{g}=1$ ). This can be explained as follows: the proposed GW-EP method can fully exploit the groupwise information in each local cluster, whereas the conventional one fails to share the information among clusters. In addition, the proposed AGW-EP detector only suffers marginal performance loss, i.e., about 0.2 dB for $K_{g}=2$ and 0.3 dB for $K_{g}=4$ at BER $=10^{-4}$, compared with the GW-EP detector.

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-08.jpg?height=1168&width=693&top_left_y=171&top_left_x=1170)
Fig. 5. BER performance comparison of the decentralized GW-EP detector with other recently proposed methods for uncorrelated channel ( $M=96$, $K=12$, and $\rho=0$ ). (a) $C=4$, Uncorrelated. (b) $C=8$, Uncorrelated.

Fig. 8 shows the BER performance of the GW-EP detector for the spatially correlated channel with different correlation coefficients $\rho$ when $M=64, K=8$, and $C=4$. It is shown that the proposed groupwise scheme exhibits great resilience to the channel correlation. For example, the performance loss of the GW-EP detector with $\rho=0.5$ and $\rho=0.6$ is about 0.4 and 0.7 dB compared to that with $\rho=0.4$ at $\mathrm{BER}=10^{-4}$. In addition, the proposed GW-EP detector achieves greater performance gains over the conventional EP method with the increase of $\rho$. The BER performance gaps between $K_{g}=4$ and $K_{g}=1$ are approximately $0.6,1.2,2.2$, and 5 dB at $\mathrm{BER}= 10^{-3}$, respectively, for $\rho=0, \rho=0.4, \rho=0.5$, and $\rho=0.6$.

Fig. 9 shows the convergence of the proposed GW-EP method for the star architecture by tracking the value of $v_{f_{c} \rightarrow \mathbf{x}}$ [cf. (17)] in the spatially correlated channel when SNR $=8 \mathrm{~dB}, M=64, K=8$, and $\rho=0.4$. It is observed that for both $C=4$ and $C=8$, the proposed GW-EP algorithm converges faster with the increase of $K_{g}$. For $K_{g}=4$, the GW-EP algorithm requires three iterations to converge, while $K_{g}=1$ and $K_{g}=2$ take about five iterations. The gap between $v_{f_{c} \rightarrow \mathbf{x}}$ and $\sigma_{n}^{2}$ decreases as $K_{g}$ increases, which demonstrates the effectiveness of the proposed algorithm. In addition, as the antenna cluster increases, the value of $v_{f_{c} \rightarrow \mathbf{x}}$ in the proposed algorithm is far away from $\sigma_{n}^{2}$ due to the limited sharing of global information, which corroborates the BER analysis results in Fig. 4.

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-09.jpg?height=1226&width=725&top_left_y=166&top_left_x=243)
Fig. 6. BER performance comparison of the decentralized GW-EP detector with other recently proposed methods for correlated channel ( $M=96$, $K=12$, and $\rho=0.4$ ). (a) $C=4$, Correlated, $\rho=0.4$. (b) $C=8$, Correlated, $\rho=0.4$.

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-09.jpg?height=547&width=689&top_left_y=1583&top_left_x=259)
Fig. 7. BER performance of the GW-EP and AGW-EP detectors with different $K_{g}$ for the star architecture ( $M=64, K=8, \rho=0$, and 16-QAM).

Fig. 10 illustrates the BER performance of the proposed GW-EP detector for both DBP architectures with $M=96$, $K=12, K_{g}=2$, and 16-QAM. The performance of the centralized architecture is plotted as a benchmark. For both spatially uncorrelated and correlated channels, it is shown that the performance of the star architecture is severely degraded with the increase of antenna clusters. In contrast, the daisychain structure suffers less performance degradation because

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-09.jpg?height=551&width=693&top_left_y=180&top_left_x=1170)
Fig. 8. BER performance of the GW-EP detector for the spatially correlated channel with different $\rho(M=64, K=8, C=4$, and 16-QAM).

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-09.jpg?height=555&width=676&top_left_y=870&top_left_x=1179)
Fig. 9. State evolution of $v_{f_{c} \rightarrow \mathbf{x}}$ as a function of the number of iterations $t$ for the star architecture ( $M=64, K=8, \rho=0.4$, and 16-QAM).

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-09.jpg?height=572&width=697&top_left_y=1564&top_left_x=1170)
Fig. 10. BER performance of the GW-EP detector for the daisy-chain and star architectures ( $M=96, K=12, K_{g}=2$, and 16-QAM).

part of the information is shared between adjacent clusters, and its performance is close to that of the centralized scheme.

Fig. 11 illustrates the BER performance of the proposed GW-EP and AGW-EP detectors for the daisy-chain architecture when $M=64, K=8$, and $\rho=0.4$. As expected, the proposed GW-EP detector obtains greater performance gains than the conventional EP method. The performance gap between the GW-EP and the AGW-EP detector is less than

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-10.jpg?height=540&width=682&top_left_y=180&top_left_x=262)
Fig. 11. BER performance of the GW-EP and AGW-EP detectors for the daisy-chain architecture ( $M=64, K=8, \rho=0.4$, and 16-QAM).

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-10.jpg?height=536&width=669&top_left_y=880&top_left_x=270)
Fig. 12. State evolution of $v_{f_{c} \rightarrow \mathbf{x}}$ as a function of the order of antenna clusters $c$ for the daisy-chain architecture $(M=64, K=8, C=8, \rho=0.4$, and 16-QAM).

0.2 dB at $\mathrm{BER}=10^{-4}$, which demonstrates the efficacy of the proposed AGW-EP method for the daisy-chain architecture.

Fig. 12 depicts the value of $v_{f_{c} \rightarrow \mathbf{x}}$ of the proposed GW-EP method for the daisy-chain architecture with the increasing order of antenna clusters $c$ when $\mathrm{SNR}=4 \mathrm{~dB}, M=64$, $K=8, C=8$, and $\rho=0.4$. It is shown that the gap between $v_{l, f \rightarrow \mathbf{x}}$ and $\sigma_{n}^{2}$ decreases as the order of antenna clusters $c$ increases. The number of required iterations of the proposed GW-EP method to achieve numerical stability decreases with the increase of $c$. This is attributed to the fact that the a priori information from the preceding antenna clusters can be adopted by the current cluster. Similar to the phenomenon in the star architecture, the gap between $v_{f_{c} \rightarrow \mathbf{x}}$ and $\sigma_{n}^{2}$ decreases as $K_{g}$ increases owing to the full use of groupwise information.

Fig. 13 shows the computational complexity comparison of different detectors against the number of users $K$ when $N=96, C=4$, and $K_{g}=2$. It is shown that the computational complexity of the proposed GW-EP detector scales linearly with the number of users, as opposed to the cubic order of the MMSE method. As expected, the approximate process (AGW-EP) can further reduce the computational complexity of the GW-EP detector, especially for the high-order modulation (16QAM).

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-10.jpg?height=607&width=714&top_left_y=180&top_left_x=1158)
Fig. 13. Complexity comparison of different receivers with different number of users $K\left(N=96, C=4\right.$, and $\left.K_{g}=2\right)$.

![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-10.jpg?height=574&width=716&top_left_y=941&top_left_x=1160)
Fig. 14. Percentage of interconnect data rates saved for the proposed GWEP algorithm over centralized implementation as a function of the number of antennas $M\left(K=8, C=4\right.$, and $\left.K_{g}=2\right)$.

Fig. 14 presents the percentage of interconnect data rates saved for the proposed GW-EP algorithm over centralized implementation as a function of the number of antennas $M$ when $K=8$, and $C=4$. It is observed that the reduced interconnect data rates of the proposed method for star and daisy-chain architectures increases with $M$, which enables the scalability required for MU-MIMO networks with a large number of BS antennas.

## V. Conclusion

In this article, we have focused on the massive MU-MIMO technology to support the requirement of massive connectivity in IoT networks. We proposed a novel decentralized groupwise detection paradigm and applied it to the EP-based DBP equalization of the uplink massive MU-MIMO system. A nonlinear message fusion rule was designed based on the product principle of multivariate Gaussian PDF for star and daisychain architectures, respectively. To reduce the computational complexity of the GW-EP method, we proposed an AGWEP algorithm based on the most reliable constellation vectors.

$$
\begin{align*}
& v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=\sigma_{n}^{2}+\mathbf{e}_{c, n}^{\mathrm{T}}\left(\sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}} \mathbf{V}_{\mathbf{x}_{g^{\prime}} \rightarrow f_{c, n}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}}\right) \mathbf{e}_{c, n} \\
& =\sigma_{n}^{2}+\mathbf{e}_{c, n}^{\mathrm{T}}\left(\sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}}\left(\left(\tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}\right)^{-1}-\frac{\mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}}\right)^{-1} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}}\right) \mathbf{e}_{c, n} \\
& \stackrel{(a)}{=} \sigma_{n}^{2}+\mathbf{e}_{c, n}^{\mathrm{T}}\left(\sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}}\left(\tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}+\frac{\tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right) \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}}\right) \mathbf{e}_{c, n} \\
& =\sigma_{n}^{2}+\left(\sum_{g^{\prime} \neq g} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}\right)+\left(\sum_{g^{\prime} \neq g} \frac{\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right) \\
& =\sigma_{n}^{2}+\sum_{g^{\prime} \neq g}\left(\frac{\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}\left(v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}\right)}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right. \\
& \left.+\frac{\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right) \\
& =\sigma_{n}^{2}+\left(\sum_{g^{\prime}} \frac{\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n} v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right)-\frac{\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n} v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g}}^{t} \mathbf{H}_{c, g}^{\mathrm{H}} \mathbf{e}_{c, n}} \\
& =\sigma_{n}^{2}+\sum_{g^{\prime}} \psi_{c, n, g^{\prime}}^{t} \varphi_{c, n, g^{\prime}}^{t}-\psi_{c, n, g}^{t} \varphi_{c, n, g}^{t}  \tag{36}\\
& u_{f_{c, n} \rightarrow \mathbf{x}_{g}}^{t}=y_{c, n}-\mathbf{e}_{c, n}^{\mathrm{T}} \sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}} \mathbf{u}_{\mathbf{x}_{g^{\prime}} \rightarrow f_{c, n}}^{t} \\
& =y_{c, n}-\mathbf{e}_{c, n}^{\mathrm{T}} \sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}}\left(\mathbf{V}_{\mathbf{x}_{g^{\prime}} \rightarrow f_{c, n}}^{t}\left(\left(\widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}\right)^{-1} \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g^{\prime}}}^{t}-\frac{u_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right)\right) \\
& =y_{c, n}-\mathbf{e}_{c, n}^{\mathrm{T}} \sum_{g^{\prime} \neq g} \mathbf{H}_{c, g^{\prime}}\left(\left(\tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}+\frac{\tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathrm{e}_{c, n} \mathrm{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathbf{H}} \mathbf{e}_{c, n}}\right)\left(\left(\widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}\right)^{-1} \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g^{\prime}}}^{t}-\frac{u_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right)\right) \\
& =y_{c, n}-\sum_{g^{\prime} \neq g}\left(\left(\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{u}}_{c, \mathbf{x}_{g^{\prime}}}^{t}-\frac{u_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}} \mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}\right) \frac{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}}{v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}-\mathbf{e}_{c, n}^{\mathrm{T}} \mathbf{H}_{c, g^{\prime}} \widetilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t} \mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}}\right) \\
& =y_{c, n}-\sum_{g^{\prime}} \phi_{c, n, g^{\prime}}^{t} \varphi_{c, n, g^{\prime}}^{t}+\phi_{c, n, g}^{t} \varphi_{c, n, g}^{t} \tag{37}
\end{align*}
$$

The state evolution illustrates that the proposed decentralized GW-EP achieves faster convergence than the conventional one. Simulation results demonstrate that the proposed GW-EP and AGW-EP detectors achieve significant performance gains over the conventional decentralized methods of the star architecture, especially for scenarios with lower BS-to-user ratios and/or spatially correlated channels. For the daisy-chain architecture, the proposed detectors achieve comparable performance to that of the centralized detector. The proposed scheme delivers a flexible tradeoff between the BER performance and interconnect bandwidth requirements, which renders it suitable for implementation in practical systems. A rigorous BER performance analysis of the proposed methods and decentralized channel estimation algorithm are left for a future work.

## Appendix

## Derivation of (18) and (19)

By substituting (14) and (15) into (16) and (17), we obtain (36) and (37), shown at the top of the page, where (a) holds based on the Sherman-Morrison formula [40]

$$
\begin{equation*}
\left(\mathbf{A}+\mathbf{x y} \mathbf{y}^{\mathrm{T}}\right)^{-1}=\mathbf{A}^{-1}-\frac{\mathbf{A}^{-1} \mathbf{x y} \mathbf{y}^{\mathrm{T}} \mathbf{A}^{-1}}{1+\mathbf{y}^{\mathrm{T}} \mathbf{A}^{-1} \mathbf{x}} \tag{35}
\end{equation*}
$$

where $\mathbf{A}=\left(\tilde{\mathbf{V}}_{c, \mathbf{x}_{g^{\prime}}}^{t}\right)^{-1}, \mathbf{x}=\left(\left[\mathbf{H}_{c, g^{\prime}}^{\mathrm{H}} \mathbf{e}_{c, n}\right] /\left[v_{f_{c, n} \rightarrow \mathbf{x}_{g^{\prime}}}^{t-1}\right]\right)$, and $\mathbf{y}= \mathbf{H}_{c, g^{\prime}}^{\mathrm{T}} \mathbf{e}_{c, n}$.

## References

[1] L. Chettri and R. Bera, "A comprehensive survey on Internet of Things (IoT) toward 5G wireless systems," IEEE Internet Things J., vol. 7, no. 1, pp. 16-32, Jan. 2020.
[2] K. Shafique, B. A. Khawaja, F. Sabir, S. Qazi, and M. Mustaqim, "Internet of Things (IoT) for next-generation smart systems: A review of current challenges, future trends and prospects for emerging 5G-IoT scenarios," IEEE Access, vol. 8, pp. 23022-23040, 2020.
[3] S. Verma, S. Kaur, M. A. Khan, and P. S. Sehdev, "Toward green communication in 6G-enabled massive Internet of Things," IEEE Internet Things J., vol. 8, no. 7, pp. 5408-5415, Apr. 2021.
[4] D. C. Nguyen et al., "6G Internet of Things: A comprehensive survey," IEEE Internet Things J., vol. 9, no. 1, pp. 359-383, Jan. 2022.
[5] "Internet of Things 2016." 2016. [Online]. Available: https://www.cisco. com/c/dam/en/us/products/collateral/se/internetof-things/at-a-glance-c45-731471.pdf
[6] M. Xiao P. Yang, Y. Xiao, and S. Li, "6G wireless communications: Vision and potential techniques," IEEE Netw., vol. 33, no. 4, pp. 70-75, Jul./Aug. 2019.
[7] E. Bjornson, L. Sanguinetti, H. Wymeersch, J. Hoydis, and T. L. Marzetta, "Massive MIMO is a reality-What is next? Five promising research directions for antenna arrays," Digit. Signal Process., vol. 94, pp. 3-20, Nov. 2019.
[8] F. Guo, F. R. Yu, H. Zhang, X. Li, H. Ji, and V. C. M. Leung, "Enabling massive IoT toward 6G: A comprehensive survey," IEEE Internet Things J., vol. 8, no. 15, pp. 11891-11915, Aug. 2021.
[9] H. Q. Ngo, E. G. Larsson, and T. L. Marzetta, "Energy and spectral efficiency of very large multiuser MIMO systems," IEEE Trans. Commun., vol. 61, no. 4, pp. 1436-1449, Apr. 2013.
[10] J. G. Andrews et al., "What will 5G be?" IEEE J. Sel. Areas Commun., vol. 32, no. 6, pp. 1065-1082, Jun. 2014.
[11] A. Puglielli et al., "Design of energy-and cost-efficient massive MIMO arrays," Proc. IEEE, vol. 104, no. 3, pp. 586-606, Mar. 2016.
[12] Common Public Radio Interface: eCPRI Interface Specification, eCPRI Specification V1.2, CPRI, Bangalore, India, Jun. 2018.
[13] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[14] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
[15] J. R. Sanchez, F. Rusek, O. Edfors, and L. Liu, "An iterative interference cancellation algorithm for large intelligent surfaces," Aug. 2019, arXiv:1911.10804.
[16] X. Cao, B. Yang, H. Zhang, C. Huang, C. Yuen, and Z. Han, "Reconfigurable-intelligent-surface-assisted MAC for wireless networks: Protocol design, analysis, and optimization," IEEE Internet Things J., vol. 8, no. 18, pp. 14171-14186, Sep. 2021.
[17] E. Bjornson and L. Sanguinetti, "Scalable cell-free massive MIMO systems," IEEE Trans. Commun., vol. 68, no. 7, pp. 4247-4261, Jul. 2020.
[18] H. Yan, A. Ashikhmin, and H. Yang, "A scalable and energy-efficient IoT system supported by cell-free massive MIMO," IEEE Internet Things J., vol. 8, no. 19, pp. 14705-14718, Oct. 2021.
[19] J. R. Sánchez, J. V. Alegría, and F. Rusek, "Decentralized massive MIMO systems: Is there anything to be discussed?" in Proc. IEEE Int. Symp. Inf. Theory (ISIT), 2019, pp. 787-791.
[20] J. R. Sánchez, F. Rusek, O. Edfors, M. Sarajlić, and L. Liu, "Decentralized massive MIMO processing exploring daisy-chain architecture and recursive algorithms," IEEE Trans. Signal Process., vol. 68, no. 1, pp. 687-700, Jan. 2020.
$[21]$ A. Kulkarni, M. A. Ouameur, and D. Massicotte, "Hardware topologies for decentralized large-scale MIMO detection using Newton method," IEEE Trans. Circuits Syst. I, Reg. Papers, vol. 68, no. 9, pp. 3732-3745, Sep. 2021.
[22] J. V. Alegría, F. Rusek, J. R. Sánchez, and O. Edfors, "Trade-offs in quasi-decentralized massive MIMO," in Proc. IEEE Int. Conf. Commun. Workshop (ICCW), 2020, pp. 1-6.
[23] J. V. Alegría, F. Rusek, and O. Edfors, "Trade-offs in decentralized multi-antenna architectures: The WAX decomposition," Dec. 2020, arXiv:2012.00572.
[24] Z. Zhang, H. Li, Y. Dong, X. Wang, and X. Dai, "Decentralized signal detection via expectation propagation algorithm for uplink massive MIMO systems," IEEE Trans. Veh. Technol., vol. 69, no. 10, pp. 11233-11240, Oct. 2020.
[25] K. Li, O. Castañeda, C. Jeon, J. R. Cavallaro, and C. Studer, "Decentralized coordinate-descent data detection and precoding for massive MU-MIMO," in Proc. IEEE Int. Symp. Circuits Syst., Sapporo, Japan, 2019, pp. 1-5.
[26] K. Li, Y. Chen, R. Sharan, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized data detection for massive MU-MIMO on a Xeon Phi cluster," in Proc. 50th Asilomar Conf. Signals Syst. Comput., Pacific Grove, CA, USA, 2016, pp. 468-472.
[27] X. Zhao, X. Guan, M. Li, and Q. Shi, "Decentralized linear MMSE equalizer under colored noise for massive MIMO systems," 2021, arXiv:2106.12416.
[28] P. Seidel, L. Karsthof, and S. Paul, "A novel approach for combining local estimates for fully decentralized feedforward massive MIMO equalization: The multistep fusion," in Proc. 54th Asilomar Conf. Signals Syst. Comput., 2020, pp. 1033-1036.
[29] K. Li, C. Jeon, J. R. Cavallaro, and C. Studer, "Decentralized equalization for massive MU-MIMO on FPGA," in Proc. Asilomar Conf. Signals Syst. Comput., Apr. 2017, pp. 1532-1536.
[30] Z. Zhang, Y. Dong, K. Long, X. Wang, and X. Dai, "Decentralized baseband processing with Gaussian message passing detection for uplink massive MU-MIMO systems," 2021, arXiv:2105.10636.
[31] X. Gao, O. Edfors, F. Rusek, and F. Tufvesson, "Massive MIMO performance evaluation based on measured propagation data," IEEE Trans. Wireless Commun., vol. 14, no. 7, pp. 3899-3911, Jul. 2015.
[32] F. R. Kschischang, B. J. Frey, and H.-A. Loeliger, "Factor graphs and the sum-product algorithm," IEEE Trans. Inf. Theory, vol. 47, no. 2, pp. 498-519, Feb. 2001.
[33] A. Vehtari et al., "Expectation propagation as a way of life: A framework for bayesian inference on partitioned data," J. Mach. Learn. Res., vol. 21, no. 1, pp. 577-629, 2020.
[34] S. Wu, L. Kuang, Z. Ni, J. Lu, D. D. Huang, and Q. Guo, "Expectation propagation based iterative group wise detection for Large-scale multiuser MIMO-OFDM systems," in Proc. IEEE Wireless Commun. Netw. Conf. (WCNC), Istanbul, Turkey, Apr. 2014, pp. 236-241.
[35] S. Wu, L. Kuang, Z. Ni, J. Lu, D. Huang, and Q. Guo, "Low-complexity iterative detection for large-scale multiuser MIMO-OFDM systems using approximate message passing," IEEE J. Sel. Areas Signal Process., vol. 8, no. 5, pp. 902-915, Oct. 2014.
[36] H. Li, Y. Dong, C. Gong, Z. Zhang, X. Wang, and X. Dai, "Low complexity receiver via expectation propagation for OTFS modulation," IEEE Commun. Lett., vol. 25, no. 10, pp. 3180-3184, Oct. 2021.
[37] P. Wang, L. Liu, S. Zhou, G. Peng, S. Yin, and S. Wei, "Near-optimal MIMO-SCMA uplink detection with low-complexity expectation propagation," IEEE Trans. Wireless Commun., vol. 19, no. 2, pp. 1025-1037, Feb. 2020.
[38] X. Yuan, J. Ma, and L. Ping, "Energy-spreading-transform based MIMO systems: Iterative equalization, evolution analysis, and precoder optimization," IEEE Trans. Wireless Commun., vol. 13, no. 9, pp. 5237-5250, Sep. 2014.
[39] X. Dai, S. Sun, and Y. Wang, "Reduced-complexity performancelossless (quasi-)maximum-likelihood detectors for S-QAM modulated MIMO systems," Electron. Lett., vol. 49, no. 11, pp. 724-725, May 2013.
[40] J. Sherman and W. J. Morrison, "Adjustment of an inverse matrix corresponding to a change in one element of a given matrix," Ann. Math. Stat., vol. 21, no. 1, pp. 124-127, 1950.
![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-12.jpg?height=328&width=267&top_left_y=2255&top_left_x=1078)

Hua $\mathbf{L i}$ received the B.S. degree from Henan University of Science and Technology, Luoyang, China, in 2016. He is currently pursuing the Ph.D. degree with the School of Computer and Communication Engineering, University of Science and Technology Beijing, Beijing, China.

His research interests include underwater acoustic communication, massive multiple-input-multipleoutput, nonorthogonal multiple access, orthogonal time-frequency space, and reconfigurable intelligent surface.
![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-13.jpg?height=319&width=257&top_left_y=206&top_left_x=167)

Yuanyuan Dong received the B.S. degree from the School of Computer and Communication Engineering, University of Science and Technology Beijing, Beijing, China, in 2017, where she is currently pursuing the Ph.D. degree with the School of Computer and Communication Engineering.

Her research interests inclue massive multiple-input-multiple-output, nonorthogonal multiple access, and reconfigurable intelligent surface.
![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-13.jpg?height=321&width=259&top_left_y=812&top_left_x=165)

Caihong Gong received the master's degree from Henan Normal University, Xinxiang, China, in 2015. She is currently pursuing the Ph.D. degree with the School of Computer and Communication Engineering, University of Science and Technology Beijing, Beijing, China.

Her research interests include nonorthogonal multiple access and reconfigurable intelligent surface.
![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-13.jpg?height=313&width=259&top_left_y=214&top_left_x=1078)

Xiyuan Wang (Member, IEEE) received the Ph.D. degree in control sciences and engineering from the Department of Automation, Tsinghua University, Beijing, China, in 2013.

He is currently an Associate Professor with the School of Information and Communication Engineering, Beijing Information Science and Technology University, Beijing. His research interests include information theory and signal processing for wireless communications.
![](https://cdn.mathpix.com/cropped/92ad3116-eb8e-444a-9a69-bcbeb1f74ff3-13.jpg?height=321&width=267&top_left_y=670&top_left_x=1078)

Xiaoming Dai (Member, IEEE) received the Ph.D. degree (with Hons.) in electrical engineering and automation from Shanghai Jiaotong University, Shanghai, China, in 2002.

His work on the sequence designs during the Doctoral study has been nominated for the Top 100 Ph.D. Thesis Contest sponsored by the Ministry of Education in China. He is currently a Professor with the Department of Telecommunications, University of Science and Technology Beijing, Beijing, China. His research activity has led to numerous publications in leading international journals and to fruitful industrial applications, most notably the pattern-division multiple access scheme. His research interests expand on modulation and coding, space-time coding, signal processing, and code designs.


[^0]:    Manuscript received 20 May 2022; revised 26 September 2022; accepted 10 November 2022. Date of publication 15 November 2022; date of current version 7 March 2023. This work was supported by the National Natural Science Foundation of China under Grant 61871029. (Corresponding author: Xiaoming Dai.)

    Hua Li, Yuanyuan Dong, Caihong Gong, and Xiaoming Dai are with the School of Computer and Communication Engineering, University of Science and Technology Beijing, Beijing 100083, China (e-mail: lihua2016_ustb@ 163.com; daixiaoming @ ustb.edu.cn).

    Xiyuan Wang is with the School of Information and Communication Engineering, Beijing Information Science and Technology University, Beijing 100101, China.

    Digital Object Identifier 10.1109/JIOT.2022.3222361

[^1]:    ${ }^{1}$ Without loss of generality, we assume that the order of antenna clusters is sequential, i.e., $c=1, \ldots, C$.
    ${ }^{2}$ In this work, the BS antennas are assumed to be uniformly partitioned (i.e, $M=C N$ ) to minimize the chip I/O bandwidth.

[^2]:    ${ }^{3}$ Without loss of generality, the users are assumed to be uniformly divided, i.e., $K_{1}=K_{2}=\cdots=K_{G}$.
    ${ }^{4}$ For the factor graph-based methods, in contrast to the traditional EP algorithm that treats each user as a VN node, the proposed GW-EP method treats each user group as a VN node to make full use of the user groupwise information.

[^3]:    ${ }^{5}$ For clarity, the performance of the AGW-EP detector with QPSK modulation scheme is not plotted in Figs. 5 and 6.

