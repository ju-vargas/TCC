# Trade-Offs in Decentralized Multi-Antenna Architectures: The WAX Decomposition 

Juan Vidal Alegría ${ }^{(1)}$, Student Member, IEEE, Fredrik Rusek ${ }^{(1)}$, and Ove Edfors ${ }^{(1)}$, Senior Member, IEEE


#### Abstract

Current research on multi-antenna architectures is trending towards increasing the amount of antennas in the base stations (BSs) so as to increase the spectral efficiency. As a result, the interconnection bandwidth and computational complexity required to process the data using centralized architectures is becoming prohibitively high. Decentralized architectures can reduce these requirements by pre-processing the data before it arrives at a central processing unit (CPU). However, performing decentralized processing introduces also cost in complexity/interconnection bandwidth at the antenna end which is in general being ignored. This paper aims at studying the interplay between level of decentralization and the associated complexity/interconnection bandwidth requirement at the antenna end. To do so, we propose a general framework for centralized/decentralized architectures that can explore said interplay by adjusting some system parameters, namely the number of connections to the CPU (level of decentralization), and the number of multiplications/outputs per antenna (complexity/interconnection bandwidth). We define a novel matrix decomposition, the WAX decomposition, that allows informationlossless processing within our proposed framework, and we use it to obtain the operational limits of the interplay under study. We also look into some of the limitations of the WAX decomposition.


Index Terms-WAX decomposition, MIMO, Massive MIMO, LIS, WAX decomposition, decentralized processing, linear equalization, MF.

## I. Introduction

MULTI-ANTENNA architectures have been widely employed since they were first introduced in the 1990s and they still remain a popular research topic. The main reason is the enormous improvements in data rate and reliability coming from exploiting space-division multiplexing and diversity. Current research and development on multi-antenna architectures is trending towards scaling up the number of antennas so as to increase the spatial resolution, thus increasing the spectral efficiency by serving several users in the same time-frequency resource. Furthermore, the exploitation of millimeter-wave spectrum in modern communications [2] also justifies the increase in the number of antennas. The reason is that the huge path-loss

[^0]associated to these frequencies when the electrical size of the antennas is kept constant needs to be overcome by focusing the transmitted energy more effectively [3]. Massive multiple-input multiple-output (MIMO) [4], [5] and large intelligent surface (LIS) [6] are some examples of the trend towards increasing the number of antennas, where massive MIMO considers base stations (BSs) with hundreds of antennas while LIS extends this concept even further by considering whole walls of electromagnetically active material.

Massive MIMO is already a reality and several prototypes have been developed and tested, such as [7]-[9]. In the prototypes presented in [7], [9], the use of centralized processing leads to huge data-rates between the antennas and the central processing unit (CPU), which limits the scalability of the system as the number of antennas grows. This fact is also noticed in [8], which sacrifices performance by relying on simple decentralized beam-forming to favor scalability. The scalability issue is likely to be exacerbated if we consider LIS, where we can think of practical deployments consisting of walls equipped with an even larger number of antennas than massive MIMO (the continuous surfaces are approximately equivalent to the discrete surfaces when the sampling is dense enough, as observed in [6], [10]). Other technologies that are gaining popularity and are likely to face scalability issues include cell-free massive MIMO [11][13], or intelligent reflecting surfaces (IRS) [13]-[15]. We will base our study in a general multi-antenna architecture so that it can be easily extended to more specific applications, such as the ones previously mentioned.

There is a current trend towards more decentralized architectures [16]-[24] so as to reduce the information transmitted to the CPU. The idea is to carry out pre-processing of the data at the antenna end (or close to it), so that the CPU does not need to have access to all the information required to decode raw data. Available literature on decentralized massive MIMO proposes a wide range of solutions from fully-decentralized architectures [16], [20]-[22], where channel state information (CSI) does not have to be available at the CPU, to partially decentralized architectures, where some of the processing tasks are distributed, but either full [17], [24] or partial CSI [19] is available at the CPU.

In this paper we do not address the problem of decentralized CSI estimation; we assume that perfect CSI is available at the CPU. We rely on the fact that CSI estimation does not limit the overall level of decentralization within our framework since it needs to be carried out only once per coherence block. Thus, CSI estimation takes a minor fraction of the coherence time,
and the estimated CSI can be then used for the data phase throughout the rest of the coherence block without affecting the level of decentralization. However, the problem of estimating and sharing CSI in an efficient and scalable way within our framework remains as future work.

In [19] it is argued that an architecture is decentralized enough if it does not need extra hardware apart from the minimum required during the payload data phase. It also states that the volume of data transferred during the data phase has to be independent of the number of antennas at the base station. However, as happens in [19]-[22], in order to reduce this volume of data (related to the number of connections to the CPU) and make it independent of the number of antennas, each antenna has to provide a number of outputs that scales with the number of users. Note that in a centralized architecture we would have only one output per antenna corresponding to one input to the CPU per antenna. We notice the existence of an interesting trade-off between the number of connections to the CPU and the number of outputs from each antenna.

The main goal of this paper is to study the interplay between level of decentralization and the corresponding increase in decentralized processing complexity for multi-antenna architectures. We measure the level of decentralization as the number of connections to a CPU required during the data phase, and we measure the decentralized processing complexity as the number of multiplications/outputs per antenna (or antenna panel) ${ }^{1}$ required to achieve a given level of decentralization. So as to study this trade-off, we present a general framework for a multi-antenna architecture which allows us to change the level of decentralization and complexity by adjusting some system parameters. In this framework, the antennas are grouped into panels of a given number of antennas (this number can be 1 as in [1]). Distributed processing is carried out by applying a linear transformation to the inputs of each antenna panel, which generates a given number of outputs (complexity). The outputs are then combined using a combining module that is connected to the CPU using a fixed number of CPU inputs (level of decentralization).

To the best of our knowledge, the presented trade-off has not been explored in the available literature and the results we present are completely new. In [18] trade-offs between different decentralized architectures, algorithms, and data precision levels are studied. However, these trade-offs are mainly systematic while we are interested in fundamental trade-offs where information rates are maintained with respect to typical centralized systems. Thus, our framework focuses on complex baseband processing, and we assume that the detection is always performed in a CPU.

This paper extends the work presented in [1]. The list of contributions are summarized next:

- We present a novel general framework for multi-antenna systems that allows us to consider different levels of decentralization and complexity by adjusting the system parameters. This general framework accounts for typical centralized architectures, decentralized architectures such

[^1]as the one presented in [19], and hybrid architectures in between those two. In [1], a similar framework to the one studied in this paper is considered. However, the architecture presented in the current work is more general since it adds the possibility of arranging the antennas into panels.

- We define the WAX decomposition, a novel matrix decomposition that allows us to define and exploit the trade-offs within our general framework while achieving information-lossless processing. In [1] the WAX decomposition is already introduced, but in the current work we adapt it to use it in a more general framework. Furthermore, we present novel results on the validity and application of said decomposition, e.g., Theorem 2.
- We present the trade-off in terms of number of multiplications/outputs per antenna panel and number of connections to the CPU for achieving information-lossless processing within our general framework. This trade-off is first studied in [1], but considering only the less general version of the current framework.
- We study through simulations the cost of obtaining simple combining modules that accept WAX decomposition within our general framework.
- We study complexity limitations for the combining modules within our general framework that accept WAX decomposition.
- We study the information-loss associated to operating within our framework when WAX decomposition is not available.
- We present a simple non-optimal solution for determining the distributed processing to be applied whenever WAX decomposition is not available. A deeper research on more effective solutions remains as future work.
The rest of the paper is organized as follows. Section II presents the general framework under study, as well as the system model and problem formulation. In Section III we present the WAX decomposition, which allows the application of information-lossless processing within our general framework. In Section IV we study the problem of defining a simple, but valid, combining network for our general framework. Section V presents some discussion on the resulting trade-offs, and some examples of the usage of WAX decomposition. Section VI explores broadly the case where WAX decomposition is not available and other information-lossy processing has to be applied to maximize the data-rates within our framework. We conclude the paper in Section VII with a summary of the contributions and future work.

Notation: In this paper, lowercase, bold lowercase and bold uppercase letters stand for scalars, column vectors and matrices, respectively. When using the mutual information operator, $I(. ;$.$) , bold uppercase in the sub-scripts refers to random vectors$ instead of their realizations. The operations $(\cdot)^{T},(\cdot)^{*}$ and $(\cdot)^{H}$ denote transpose, conjugate, and conjugate transpose, respectively. The operation $\operatorname{diag}(\cdot)$ outputs a block diagonal matrix with the input matrices/vectors as the diagonal blocks. The operator vec( ⋅ ) transforms a matrix into a vector by concatenating its columns. $\mathbf{I}_{i}$ corresponds to the identity matrix of size $i$, $\mathbf{1}_{i \times j}$ denotes the $i \times j$ all-ones matrix, and $\mathbf{0}_{i \times j}$ denotes the

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-03.jpg?height=442&width=792&top_left_y=225&top_left_x=169)
Fig. 1. General framework considered in this paper.

$i \times j$ all-zeros matrix. In this paper, a randomly chosen matrix corresponds to a realization of a random matrix whose elements are driven from a continuous probability distribution function.

## II. System Model

Let us consider $K$ single-antenna users transmitting to an $M$ antenna BS through a narrow-band channel. The $M \times 1$ received complex vector, $\boldsymbol{y}$, can be expressed as

$$
\begin{equation*}
\boldsymbol{y}=\boldsymbol{H} \boldsymbol{s}+\boldsymbol{n}, \tag{1}
\end{equation*}
$$

where $\boldsymbol{H}$ is the channel matrix of dimension $M \times K, s$ is the $K \times 1$ vector of symbols transmitted by the users, and $\boldsymbol{n}$ is a zero-mean complex white Gaussian noise vector with sample variance $N_{0}$. The $M$ antennas are divided into panels of $N$ antennas; $M / N=P$ is thus restricted to integer values. Each panel, $p \in\{1, \ldots, P\}$, multiplies the received vector, $\boldsymbol{y}_{p}=\left[y_{(p-1) N+1} \cdots y_{p N}\right]$, by an $L \times N$ matrix, $\boldsymbol{W}_{p}^{H}$. The aggregated outputs are combined through a fixed $T \times L P$ matrix, $\boldsymbol{A}^{H}$. The resulting vector is forwarded to a CPU, which can apply further processing. For our analysis, we will assume that the CPU can multiply the incoming vector by a $K \times T$ matrix $\boldsymbol{X}^{H}$ to be able to express the equivalent matrix in the form of already known linear equalizers. However, our main interest is to maximize the information rate at which the users transmit to the CPU, so the last step is not required for the analysis since it will not increase this information rate (recall the data-processing inequality [25]). Also, we define the previous matrices using conjugate transpose so as to ease upcoming notation. Fig. 1 shows a block diagram of the general framework under study.

The post-processed vector can be expressed as

$$
\begin{equation*}
\boldsymbol{z}=\boldsymbol{X}^{H} \boldsymbol{A}^{H} \boldsymbol{W}^{H} \boldsymbol{y}, \tag{2}
\end{equation*}
$$

where $\boldsymbol{W}$ is an $M \times L P$ block diagonal matrix of the form

$$
\begin{equation*}
\boldsymbol{W}=\operatorname{diag}\left(\boldsymbol{W}_{1}, \boldsymbol{W}_{2}, \ldots, \boldsymbol{W}_{P}\right) . \tag{3}
\end{equation*}
$$

We assume that the matrices $\boldsymbol{W}_{p}$, and $\boldsymbol{X}$ can be tuned for every channel realization, while the matrix $\boldsymbol{A}$ is fixed. We can interpret $\boldsymbol{A}$ as the matrix associated to a hardware combining network that can be predesigned, but it cannot be changed once deployed. Table I shows a classification of the different system parameters considered within our framework.

For tractability we assume that the channel matrix, $\boldsymbol{H}$, is perfectly available at the BS . Thus, we can obtain $\boldsymbol{W}_{p}$, and

TABLE I
System Parameters
| Given parameters | Trade-off parameters |
| :---: | :---: |
| $M, K$ | $L, T, N, P$ |
| Tunable parameters | Parameters fixed by design |
| $\boldsymbol{W}, \boldsymbol{X}$ | $\boldsymbol{A}$ |


$\boldsymbol{X}$ as a function of said matrix. However, the consequences of having an error in the estimation of $\boldsymbol{H}$ due to imperfect CSI would not be enhanced by the framework under study. In fact, the information-loss associated to having imperfect CSI within our framework would not differ from the case of having imperfect CSI in a typical centralized architecture. The reason is that we could still apply an approximation of the spatially-matched filter (MF) within our framework using the imperfectly estimated channel matrix, as we will be able to understand from the upcoming analysis.

For a fixed $\boldsymbol{A}$, we are interested in maximizing the information rate at which the users can transmit, i.e., we would like to solve the maximization problem

$$
\begin{equation*}
\underset{\boldsymbol{X},\left\{\boldsymbol{W}_{p}\right\}_{p=1}^{P}}{\operatorname{maximize}} I_{\boldsymbol{Z}, \boldsymbol{S}}(\boldsymbol{z} ; \boldsymbol{s}) . \tag{4}
\end{equation*}
$$

More specifically, we will explore the cases where the maximization results in $I_{\boldsymbol{Z}, \boldsymbol{S}}(\boldsymbol{z}, \boldsymbol{s})=I_{\boldsymbol{Y}, \boldsymbol{S}}(\boldsymbol{y}, \boldsymbol{s})$. From the dataprocessing inequality [25] we have

$$
\begin{align*}
I_{\boldsymbol{Z}, \boldsymbol{S}}(\boldsymbol{z} ; \boldsymbol{s}) & \leq I_{\boldsymbol{Y}, \boldsymbol{S}}\left(\boldsymbol{A}^{H} \boldsymbol{W}^{H} \boldsymbol{y} ; \boldsymbol{s}\right) \\
& \leq I_{\boldsymbol{Y}, \boldsymbol{S}}(\boldsymbol{y} ; \boldsymbol{s}) \tag{5}
\end{align*}
$$

This means that the application of $\boldsymbol{X}^{H}$ at the CPU cannot possibly increase the information rate and, as we mentioned before, it is just a manipulation to adapt the dimensions. Furthermore, assuming $s \sim \mathcal{C} \mathcal{N}\left(\mathbf{0}_{K \times 1}, P_{s} \mathbf{I}_{K}\right)$ so that the mutual information is maximized (and thus coincides with the capacity), we have [26]

$$
\begin{equation*}
I_{\boldsymbol{Y}, \boldsymbol{S}}(\boldsymbol{y} ; \boldsymbol{s})=\log \operatorname{det}\left(\mathbf{I}_{M}+\frac{P_{s}}{N_{0}} \boldsymbol{H} \boldsymbol{H}^{H}\right) . \tag{6}
\end{equation*}
$$

Therefore, we can state that, if we are able to achieve

$$
\begin{equation*}
I_{\boldsymbol{Z}, \boldsymbol{S}}(\boldsymbol{z} ; \boldsymbol{s})=I_{\boldsymbol{Y}, \boldsymbol{S}}(\boldsymbol{y} ; \boldsymbol{s}), \tag{7}
\end{equation*}
$$

the information rate is maximized and the equivalent processing is information-lossless.

One of the main scopes of this paper is to study the conditions, in terms of constraints on the system parameters, for our framework to be able to perform information-lossless processing. The following lemma will be helpful.

Lemma 1: Considering the presented framework, the equality

$$
\begin{equation*}
I_{\boldsymbol{Z}, \boldsymbol{S}}(\boldsymbol{z} ; \boldsymbol{s})=\log \operatorname{det}\left(\mathbf{I}_{M}+\frac{P_{s}}{N_{0}} \boldsymbol{H} \boldsymbol{H}^{H}\right), \tag{8}
\end{equation*}
$$

is fulfilled if and only if we can find $\boldsymbol{W}$ and $\boldsymbol{X}$ such that

$$
\begin{equation*}
W A X=H . \tag{9}
\end{equation*}
$$

Proof: Let $R(\boldsymbol{y})$ be any sufficient statistic for $\boldsymbol{s}$ (which means that it is information-lossless [25]). Then, for any $S \geq K$ there
exists a full-rank $S \times K$ matrix $\widetilde{\boldsymbol{X}}$ such that

$$
\begin{equation*}
R(\boldsymbol{y})=\widetilde{\boldsymbol{X}} \boldsymbol{H}^{H} \boldsymbol{y} \tag{10}
\end{equation*}
$$

Therefore, for $S=K$, we have that $\boldsymbol{X}^{H} \boldsymbol{A}^{H} \boldsymbol{W}^{H} \boldsymbol{y}$ is a sufficient statistic if and only if

$$
\begin{equation*}
\boldsymbol{X}^{H} \boldsymbol{A}^{H} \boldsymbol{W}^{H} \boldsymbol{y}=\widetilde{\boldsymbol{X}} \boldsymbol{H}^{H} \boldsymbol{y}, \tag{11}
\end{equation*}
$$

which leads to

$$
\begin{equation*}
\widetilde{\boldsymbol{X}}^{-1} \boldsymbol{X}^{H} \boldsymbol{A}^{H} \boldsymbol{W}^{H}=\boldsymbol{H}^{H}, \tag{12}
\end{equation*}
$$

but since $\widetilde{\boldsymbol{X}}^{-1}$ can be absorbed by $\boldsymbol{X}$, we have

$$
\begin{equation*}
\boldsymbol{X}^{H} \boldsymbol{A}^{H} \boldsymbol{W}^{H}=\boldsymbol{H}^{H}, \tag{13}
\end{equation*}
$$

which proves the lemma by taking the conjugate transpose. $\square$

Lemma 1 gives an important result to understand when the maximization in (4) achieves information-lossless processing. This lemma will be the basis in Section III for solving the maximization problem (4) whenever information-lossless processing is available within our framework. Note that (13) would correspond to applying MF within our framework, which is well known to be an information-lossless transformation if optimum processing is applied thereafter.

## A. Notes on the Downlink Scenario

Throughout this paper we focus on the uplink scenario for improved clarity. However, this work can straightforwardly be extended to a downlink scenario. We next provide a few details.

Let us assume channel reciprocity, which eases notation and remarks the equivalence with the uplink scenario. ${ }^{2}$ This means that, given the uplink equation (1), the corresponding downlink equation for the vector received by the users is as follows

$$
\begin{equation*}
\boldsymbol{y}_{\mathrm{d}}=\boldsymbol{H}^{T} \boldsymbol{z}_{\mathrm{d}}+\boldsymbol{n}_{\mathrm{d}}, \tag{14}
\end{equation*}
$$

where $\boldsymbol{y}_{\mathrm{d}}$ is now a $K \times 1$ vector with entries associated to the complex baseband signal seen by each user, $\boldsymbol{z}_{\mathrm{d}}$ is the $M \times 1$ precoded vector sent by the antennas, and $\boldsymbol{n}_{\mathrm{d}}$ is the corresponding noise vector. We assume that the same framework as in Fig. 1 applies for the downlink, but changing the arrows from left to right. This implies that the linear operators (including the combining module) are assumed to be able to use inputs as outputs, and vice versa. The precoded vector would then be defined as

$$
\begin{equation*}
\boldsymbol{z}_{\mathrm{d}}=\boldsymbol{W}^{*} \boldsymbol{A}^{*} \boldsymbol{X}^{*} \boldsymbol{s}_{\mathrm{d}} \tag{15}
\end{equation*}
$$

where $\boldsymbol{s}_{\mathrm{d}}$ is now a $K \times 1$ vector with complex entries associated to the signals intended for each user. In this case, Lemma 1 does not apply unless we assume that the users can collaborate with each other. However, we can achieve lossless precoding with respect to standard centralized linear precoding schemes, since we can still apply typical precoding schemes within our framework such as MF, zero-forcing (ZF) or minimum mean squared error (MMSE). Furthermore, with the assumption of channel reciprocity in place, the $\boldsymbol{W}$ matrices could be kept fixed

[^2]from the uplink processing ( $\boldsymbol{A}$ is still fixed by design) and $\boldsymbol{X}$ can be adapted to apply the desired precoding scheme. In the case of non-reciprocity of the channel, both $\boldsymbol{X}$ and $\boldsymbol{W}$ have to be recomputed for applying the desired precoding based on the downlink channel.

## B. Previously Studied Architectures Within Our Framework

There are several multi-antenna architectures that could be represented within our framework, which further motivates our study. In this case, what we mean with "represent an architecture within our framework" is that there is a combination of design variables within our framework that gives the same processing. The most obvious architecture that fulfills this is a typical centralized $M$-antenna architecture, e.g., centralized massive MIMO systems. In this case all the antennas are directly connected to a CPU, which corresponds to having one antenna per panel, and all antennas connected directly to the CPU, i.e., $N=1, L=1, \boldsymbol{W}_{p}=1$ (scalar), $T=M, \boldsymbol{A}=\mathbf{I}_{M}$. This architecture is depicted in Fig. 2 (left).

Another architecture that can be represented within our framework is the decentralized massive MIMO architecture from [19]. In this case, there is also one antenna per panel, but antenna $m$ multiplies its input by the $K \times 1$ local channel vector, $\boldsymbol{h}_{m}$, and the result is summed over all the antennas so that the size of the vector transmitted to the CPU coincides with the number of users, $K$. Thus, this architecture can be represented within our framework by setting $N=1, L=K, \boldsymbol{W}_{p}=\boldsymbol{h}_{p}$ (vector), $T=K, \boldsymbol{A}=\left[\begin{array}{lll}\mathbf{I}_{K} & \mathbf{I}_{K} & \ldots \\ \mathbf{I}_{K}\end{array}\right]^{T}$, which corresponds to MF if no $\boldsymbol{X}$ is applied at the CPU. This architecture is depicted in Fig. 2 (right). In [19] it is claimed that, for a system to be decentralized, the volume of data transmitted to the CPU during the data phase should not scale with $M$. However, the proposed solution reduces this scaling to $K$ by increasing the number of multiplications/outputs per antenna to $K$, which increases the decentralized processing complexity. Our framework allows us to freely adjust these parameters.

Comparing the two architectures from Fig. 2, where in both cases information-lossless processing can be applied, we immediately identify a trade-off between the number of connections to the CPU and the number of outputs per antenna panel as depicted in Fig. 3 (left). Note that, in this case, we have a single antenna per panel, i.e., $N=1$. In our framework, these two quantities, which are traded-off against each other, correspond to $T$ and $L$, respectively. We can also see the trade-off in terms of multiplications per antenna as in Fig. 3 (right), which can lead to a fairer comparison if we consider panels with more than 1 antenna. The main reason is that, for $N>1$, the number of outputs can be maintained [27], but the complexity still increases due to a higher number of multiplications.

If we look into other decentralized architectures, such as the ones presented in [18], [20]-[22], [27], we can also represent them within our framework and identify the trade-off between inputs to the CPU and multiplications/outputs per panel (in these cases the trade-off may not lead to information-lossless processing). For example, the architectures from [20]-[22] would all lead to the decentralized point in the plots from Fig. 3 since they

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-05.jpg?height=450&width=1148&top_left_y=227&top_left_x=449)
Fig. 2. Architecture of centralized massive MIMO (left), and decentralized massive MIMO from [19] (right).

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-05.jpg?height=424&width=858&top_left_y=799&top_left_x=137)
Fig. 3. Number of inputs to the CPU (related to $T$ ) v.s. number of outputs (left)/number of multiplications (right) per antenna (related to $L$ ) for the architectures depicted in Fig. 2. Available literature does not address the behavior in between 1 and $K$ outputs per antenna.

all apply $K \times 1$ filters in each antenna during the data phase and generate $K$ outputs per panel during the data phase ( $N=1$ in these architectures). The same is true in [27] if we consider outputs per panel, although if we look at multiplications per panel we should scale the number of outputs by the number of antennas per panel, $N>1$. Note that, even though [27] presents two different architectures with different level of decentralization, within our framework they lead to the same value of the trade-off; the only difference is that in the fully-decentralized architecture $\boldsymbol{X}$ would not be applied. In [18], however, we would not be able to represent the fully-decentralized architecture within our framework since detection is performed before reaching the CPU, while our framework only considers complex baseband processing.

## III. WAX Decomposition

Given an arbitrary $M \times K$ matrix, $\boldsymbol{H}$, and a fixed $L P \times T$ matrix, $\boldsymbol{A}$, we define the WAX decomposition of $\boldsymbol{H}$, whenever it exists, as

$$
\begin{equation*}
H=W A X . \tag{16}
\end{equation*}
$$

This decomposition relates directly to Lemma 1, i.e., $\boldsymbol{W}$ has the structure defined in (3) and $\boldsymbol{X}$ is a $T \times K$ matrix. Furthermore, the existence of this matrix decomposition for any channel realization would assure that our framework can apply information-lossless processing.

The next lemma will allow us to restrict our study to the case where $N=L$ since this case can span a major part of the general problem through some manipulation.

Lemma 2: Assume $M / L$ and $L / N$ are integer valued. Consider some fixed $T \times K$ matrix $\boldsymbol{X}$, an $M \times K$ matrix $\boldsymbol{H}$, an $M \times T$ matrix $\widetilde{\boldsymbol{A}}$, and an $L P \times T$ matrix $\boldsymbol{A}=\boldsymbol{T}_{L, N} \widetilde{\boldsymbol{A}}$, with

$$
\begin{equation*}
\boldsymbol{T}_{L, N}=\mathbf{I}_{\frac{M}{L}} \otimes\left(\mathbf{1}_{\frac{L}{N} \times 1} \otimes \mathbf{I}_{L}\right) . \tag{17}
\end{equation*}
$$

Then, the statement

$$
\begin{equation*}
\exists \boldsymbol{W}: \boldsymbol{H}=\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}, \tag{18}
\end{equation*}
$$

where $\boldsymbol{W}$ is defined as in (3), is true if and only if

$$
\begin{equation*}
\exists \widetilde{\boldsymbol{W}}: \boldsymbol{H}=\widetilde{\boldsymbol{W}} \widetilde{\boldsymbol{A}} \boldsymbol{X}, \tag{19}
\end{equation*}
$$

where $\widetilde{\boldsymbol{W}}=\operatorname{diag}\left(\widetilde{\boldsymbol{W}}_{1}, \ldots, \widetilde{\boldsymbol{W}}_{M / L}\right)$, and $\widetilde{\boldsymbol{W}}_{p}$ are $L \times L$ matrices $\forall p \in\{1, \ldots, M / L\}$, i.e., $\widetilde{\boldsymbol{W}}$ has the same structure as (3) for $N=L$.

Proof: The right implication can be immediately seen by choosing $\widetilde{\boldsymbol{W}}=\boldsymbol{W} \boldsymbol{T}_{L, N}$ and noticing that this matrix already has the required structure.

For the left implication it is enough to check that, for any $\widetilde{\boldsymbol{W}}$, there exists some $\boldsymbol{W}$ that fulfills $\boldsymbol{W} \boldsymbol{T}_{L, N}=\widetilde{\boldsymbol{W}}$, both $\boldsymbol{W}$ and $\widetilde{\boldsymbol{W}}$ with their corresponding structure. In this case, there is no linear transformation that gets $\boldsymbol{W}$ from $\widetilde{\boldsymbol{W}}$, but we can construct it as follows. Let us take $\widehat{\boldsymbol{W}}=\widetilde{\boldsymbol{W}} \boldsymbol{T}_{L, M}$, with $\boldsymbol{T}_{L, M}=\left[\mathbf{I}_{L}, \ldots, \mathbf{I}_{L}\right]^{T}$. We can then select the diagonal blocks of $\boldsymbol{W}$ to be $\boldsymbol{W}_{p}=\left[\widehat{\boldsymbol{w}}_{(p-1) N+1}^{T}, \ldots, \widehat{\boldsymbol{w}}_{(p-1) N}^{T}\right]^{T}$, where $\widehat{\boldsymbol{w}}_{m}, m=\{1, \ldots, M\}$, are the rows of $\widehat{\boldsymbol{W}}$. Thus, there is a one-to-one mapping between all possible $\widetilde{\boldsymbol{W}}$ and $\boldsymbol{W}$ that fulfills $\boldsymbol{W} \boldsymbol{T}_{L, N}=\widetilde{\boldsymbol{W}}$. $\square$

Lemma 2 also implies that, whenever the assumptions apply, the trade-off between the number of outputs per panel and the number of inputs to the CPU required ( $L$ and $T$, respectively) does not depend on the number of antennas per panel ( $N$ ). However, the number of multiplications per panel would scale with $N$. An important constraint of Lemma 2 is that we need to have $L \geq N$, which can be easily checked to be a requirement for having information-lossless processing within our framework unless $L=K$ (leading to the trivial solution of setting $\boldsymbol{W}_{p}$ as the local MFs).

The rest of this paper assumes $N=L$, unless otherwise stated, due to the intrinsic generality of this case. This means that $\boldsymbol{W}$ in (16) is a square $M \times M$ block diagonal matrix given by (3), with $P=M / L$, and containing square $L \times L$ blocks. The physical implication of this restriction is that all the panels in Fig. 1 have the same number of antennas and outputs. However, as seen in the proof of Lemma 2, we can construct almost any other case from the square case by applying some transformations, with the only limitation that $M / L$ and $L / N$ must evaluate to integer values, as well as that $\boldsymbol{A}$ must be constructed using a specific structure. For simplicity, we will use the same notation as in the general case (16), but considering the new restriction on the dimensions.

## A. Solving WAX

Let us assume for now that there exists the WAX decomposition of $\boldsymbol{H}$, we later investigate when this is the case. We provide next a step-by-step solution for practical computation of (16), i.e., for obtaining the matrices $\boldsymbol{W}$ and $\boldsymbol{X}$ in (16) based on the current channel realization, $\boldsymbol{H}$, and the fixed combining network, $\boldsymbol{A}$. This step-by-step solution will also be useful to set the ground for our main result on the applicability of WAX decomposition.

Let us express $\boldsymbol{H}=\left[\boldsymbol{H}_{1}^{T} \boldsymbol{H}_{2}^{T} \ldots \boldsymbol{H}_{P}^{T}\right]^{T} \quad$ and $\quad \boldsymbol{A}= \left[\boldsymbol{A}_{1}^{T} \boldsymbol{A}_{2}^{T} \ldots \boldsymbol{A}_{P}^{T}\right]^{T}$, where $\boldsymbol{H}_{p}$ and $\boldsymbol{A}_{p} \quad \forall p \in\{1, \ldots, P\}$ are $L \times K$ and $L \times T$ blocks, respectively. The following lemma will be useful.

Lemma 3: For all matrices $\boldsymbol{H}$ satisfying $\operatorname{rank}\left(\boldsymbol{H}_{n}\right)=L$ there exists a block diagonal matrix $\boldsymbol{W}$ and a matrix $\boldsymbol{X}$ such that $\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}=\boldsymbol{H}$ if and only if there exists a block diagonal invertible matrix $\hat{\boldsymbol{W}}$ with the same form as $\boldsymbol{W}$ that fulfills $\boldsymbol{A} \boldsymbol{X}-\hat{\boldsymbol{W}} \boldsymbol{H}=\mathbf{0}_{M \times K}$.

Proof: Assume existence of a block diagonal matrix $\boldsymbol{W}$ and a matrix $\boldsymbol{X}$ such that $\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}=\boldsymbol{H}$. This is equivalent to

$$
\boldsymbol{W}_{p} \boldsymbol{A}_{p} \boldsymbol{X}=\boldsymbol{H}_{p}, 1 \leq p \leq P .
$$

Since, by assumption, $\operatorname{rank}\left(\boldsymbol{H}_{p}\right)=L$, it follows that $\operatorname{rank}\left(\boldsymbol{W}_{p}\right)=L \quad \forall p$, making the matrix $\boldsymbol{W}$ invertible.

The reverse statement is trivial; if an invertible $\hat{\boldsymbol{W}}$ exists, then we can set $\boldsymbol{W}=\hat{\boldsymbol{W}}^{-1}$.

For a randomly chosen $\boldsymbol{H}$, the condition $\operatorname{rank}\left(\boldsymbol{H}_{p}\right)=L$ holds with probability 1 . We can then compute the WAX decomposition by invoking Lemma 3, which yields the linear system

$$
\begin{equation*}
\boldsymbol{A} \boldsymbol{X}-\boldsymbol{W}^{-1} \boldsymbol{H}=\mathbf{0}_{M \times K} \tag{20}
\end{equation*}
$$

Using the vectorization operator we get an equivalent linear system of equations

$$
\begin{equation*}
\boldsymbol{B} \boldsymbol{u}=\mathbf{0}_{M K \times 1}, \tag{21}
\end{equation*}
$$

where $\boldsymbol{u}$ corresponds to the $(T K+M L) \times 1$ vector of unknowns,

$$
\boldsymbol{u}=\left[\begin{array}{c}
\operatorname{vec}(\boldsymbol{X})  \tag{22}\\
\operatorname{vec}\left(\boldsymbol{W}_{1}\right) \\
\vdots \\
\operatorname{vec}\left(\boldsymbol{W}_{P}\right)
\end{array}\right],
$$

and $\boldsymbol{B}$ is an $M K \times(T K+M L)$ block matrix of the form $\boldsymbol{B}= \left[\begin{array}{ll}\boldsymbol{B}_{1} & \boldsymbol{B}_{2}\end{array}\right]$ resulting from the vectorization operation, with

$$
\begin{equation*}
\boldsymbol{B}_{1}=\mathbf{I}_{K} \otimes \boldsymbol{A}, \quad \boldsymbol{B}_{2}=-\left(\boldsymbol{H}^{\mathrm{T}} \otimes \mathbf{I}_{M}\right) \mathbf{P} . \tag{23}
\end{equation*}
$$

$\mathbf{P}$ is an $M^{2} \times M L$ block matrix composed of identity matrices, $\boldsymbol{I}_{L}$, separated by rows of zeros so as to disregard the zeros in $\operatorname{vec}(\boldsymbol{W})$. The solution to (21) can be found by setting $\boldsymbol{u}$ to be any vector in the null-space of $\boldsymbol{B}$, which will always be non-zero if condition (24) is met (as will be seen shortly). Then, we can obtain the corresponding $\boldsymbol{W}^{-1}$ and $\boldsymbol{X}$ from $\boldsymbol{u}$ through inverse vectorization, and we should check that the resulting $\boldsymbol{W}^{-1}$ is full rank so that we can obtain $\boldsymbol{W}$ by taking the matrix inverse. Thus, the complexity of performing the WAX decomposition using the provided method is equivalent to that of finding the null-space of an $M K \times(T K+M L)$ matrix, and inverting $P$ matrices of dimension $L \times L$.

We have now set the ground for presenting our main result on the applicability of WAX decomposition, which is established in the following theorem.

Theorem 1: Assuming $N=L$, which implies that $P=M / L$ must evaluate to an integer value, fulfilling the inequality

$$
\begin{equation*}
T>\max \left(M \frac{K-L}{K}, K-1\right) \tag{24}
\end{equation*}
$$

assures that, given a fixed randomly chosen $\boldsymbol{A} \in \mathbb{C}^{M \times T}$, a randomly chosen $\boldsymbol{H} \in \mathbb{C}^{M \times K}$ will admit a decomposition of the form (16) with probability 1.

Proof: See Appendix A.
An immediate result of Theorem 1 is that, since we are only interested in having $L \leq K$ due to its practical implications (otherwise there is no dimensionality reduction compared to local MF from Fig. 2 right side), then we have $T \geq L$ since $T \geq K$. The case where Theorem 1 is not fulfilled is considered in Section VI.

For a randomly chosen $\boldsymbol{A}, \boldsymbol{W}^{-1}$ is full rank with probability 1 , but note that some specific $\boldsymbol{A}$ matrices may lead to rank deficient $\boldsymbol{W}^{-1}$ even if (24) is met. That is, for a poorly chosen matrix $\boldsymbol{A}$, the WAX decomposition of a matrix $\boldsymbol{H}$ cannot be performed. In what follows next we study conditions on $\boldsymbol{A}$ in order for the WAX decomposition to be feasible.

## B. Studying Validity of Matrix $\boldsymbol{A}$

While Theorem 1 states that any randomly chosen $\boldsymbol{A}$ works for WAX decomposition, we are, from a practical perspective, interested in $\boldsymbol{A}$ matrices having simple forms (providing low computational complexity); for example, sparse matrices with elements in the set $\{0,1\}$. This would significantly simplify the combining network. However, for such a matrix, Theorem 1 no longer applies. Therefore, it is of importance to investigate the exceptions to Theorem 1. ${ }^{3}$

Definition 1: We consider $\boldsymbol{A}$ to be valid for WAX decomposition (16) if the set of matrices $\boldsymbol{H}$ that does not admit such

[^3]a decomposition has measure 0 . This is equivalent as saying that the probability of a randomly chosen $\boldsymbol{H}$ admitting WAX decomposition for a valid $\boldsymbol{A}$ is 1 .

The following theorem will be useful to check if an $\boldsymbol{A}$ matrix is valid or not.

Theorem 2: Consider a fixed $M \times T$ matrix $\boldsymbol{A}$, where $T$ fulfills (24), and a randomly chosen $\boldsymbol{H} \in \mathbb{C}^{M \times K}$, such that $\boldsymbol{B}=\left[\boldsymbol{B}_{1} \boldsymbol{B}_{2}\right]$ from (23) is full-rank. If the specific $\boldsymbol{H}$ admits WAX decomposition ((16) with $N=L$ ) for the given $\boldsymbol{A}$, then $\boldsymbol{A}$ will be valid for WAX decomposition with probability 1 , i.e., any other randomly chosen $\boldsymbol{H}$ will admit WAX decomposition for the same $\boldsymbol{A}$ with probability 1 .

Proof: The proof is a side-result from the proof of Theorem 1 in Appendix A. We just have to notice that the determinant of $\widetilde{\boldsymbol{W}}_{p}$ still fulfills (37) if $\boldsymbol{A}$ is fixed, so it is enough if we can find an $\boldsymbol{H}$ that gives $\operatorname{det}\left(\widetilde{\boldsymbol{W}}_{p}\right) \neq 0$ so that the determinant is 0 only for a countable set of $\boldsymbol{H}$ matrices.

The main contribution of Theorem 2 is that we can know if an $\boldsymbol{A}$ matrix is valid or not simply by trying to perform WAX decomposition of a single randomly chosen $\boldsymbol{H}$ using that $\boldsymbol{A}$. Theorem 2 will be widely used for our simulation results since it is our main result on the validity of $\boldsymbol{A}$. An essentially equivalent statement to that of Theorem 2 is to say that, for a given matrix $\boldsymbol{A}$, WAX decomposition of a randomly chosen matrix $\boldsymbol{H}$ is possible with probability either 1 or 0 .

The following lemma states a necessary condition for $\boldsymbol{A}$ to be valid.

Lemma 4: Let $\widehat{\boldsymbol{A}}$ be an $F L \times T$ submatrix of $\boldsymbol{A}$ formed by selecting $F$ out of the $P$ blocks of size $L \times T$ that conform $\boldsymbol{A}$, $\left\{\boldsymbol{A}_{1}, \ldots, \boldsymbol{A}_{P}\right\}$. If $\boldsymbol{A}$ is valid, then

$$
\begin{equation*}
\operatorname{rank}(\widehat{\boldsymbol{A}})=\min (F L, K) \tag{25}
\end{equation*}
$$

Proof: Let $\widehat{\boldsymbol{H}}$ be an $F L \times K$ submatrix of $\boldsymbol{H}$ formed by the $F$ respective $L \times K$ blocks of $\boldsymbol{H}$, and $\widehat{\boldsymbol{W}}$ an $F L \times F L$ block diagonal matrix with the $F$ respective $L \times L$ blocks from $\boldsymbol{W}$ as diagonal elements. If $\boldsymbol{A}$ is valid we can obtain $\widehat{\boldsymbol{W}}$ and $\boldsymbol{X}$ such that $\widehat{\boldsymbol{W}} \widehat{\boldsymbol{A}} \boldsymbol{X}=\widehat{\boldsymbol{H}}$ holds for any $\widehat{\boldsymbol{H}}$ except those in a set of measure 0 . For a randomly chosen $\boldsymbol{H}, \operatorname{rank}(\widehat{\boldsymbol{H}})=\min (F L, K)$ with probability 1 . Since

$$
\operatorname{rank}(\widehat{\boldsymbol{W}} \widehat{\boldsymbol{A}} \boldsymbol{X}) \leq \min (\operatorname{rank}(\widehat{\boldsymbol{W}}), \operatorname{rank}(\widehat{\boldsymbol{A}}), \operatorname{rank}(\boldsymbol{X})),
$$

condition (25) must be fulfilled.
A further necessary condition for $\boldsymbol{A}$ to be valid is given in Lemma 5.

Lemma 5: Let $\boldsymbol{A}_{0}$ be a submatrix of $\boldsymbol{A}$ formed by selecting $R$ rows from $\boldsymbol{A}$, where all rows are in different blocks $\boldsymbol{A}_{p}$. If $\boldsymbol{A}$ is valid, then

$$
\operatorname{rank}\left(\boldsymbol{A}_{0}\right)>R \frac{K-L}{K}
$$

Proof: See Appendix B.
We point out that, since $\boldsymbol{A}$ is an $M \times T$ matrix, $\operatorname{rank}\left(\boldsymbol{A}_{0}\right)$ cannot exceed $T$. However, with $T>M(K-L) / K$, it is guaranteed that $R \frac{K-L}{K}<T$.

An immediate consequence of Lemma 5 is that a block $\boldsymbol{A}_{p}$ cannot be repeated arbitrarily often in $\boldsymbol{A}$. In addition, any block
$\boldsymbol{A}_{p}$ must have rank $L$ (see Lemma 4). Repeating the block $\boldsymbol{A}_{p} r$ times in $\boldsymbol{A}$, and selecting $\boldsymbol{A}_{0}$ as the same row within each of these $r$ blocks yields,

$$
1>r \frac{K-L}{K},
$$

which implies $r<\frac{K}{K-L}$. Whenever $L \leq K / 2, r=1$ so that each block $\boldsymbol{A}_{p}$ can only occur once in $\boldsymbol{A}$.

Appendix C includes another, less intuitive, necessary condition for $\boldsymbol{A}$ to be valid. Despite extensive efforts, we have not been able to establish sufficient conditions for having a valid $\boldsymbol{A}$. The provided necessary conditions might not be helpful in generating valid $\boldsymbol{A}$ matrices, but they constitute initial progress on the matter. Thus, the problem of establishing sufficient conditions for valid $\boldsymbol{A}$ matrices remains open.

## IV. Finding Sparse $\boldsymbol{A}$ Matrices

Let us keep restricting ourselves to the case where $N=L$ due to the generality of this case. Recall, however, that the transformation (17), which allows considering other $N$ values, maintains the overall sparsity properties of $\boldsymbol{A}$ (although the percentage of 1 s can decrease since 0 s are being padded). As we have mentioned previously, from an implementation point of view, it is desirable to have $\boldsymbol{A}$ as a sparse matrix of 1 s and 0 s with as few 1 s as possible. The main reason is the direct relation between the number of $1 \sin \boldsymbol{A}$ and the number of sum operations required to implement such a combining matrix. Recall that we can view $\boldsymbol{A}$ as the matrix associated to a predesigned hardware combining module, which could be intuitively implemented through a network of sum modules.

In the previous section, we provided some necessary conditions on matrix $\boldsymbol{A}$ for the WAX decomposition to be applicable. However, after extensive research on the matter, we have not been able to find sufficient conditions for having a valid $\boldsymbol{A}$. This motivates the need of simulation results to further understand the limits on the sparsity of $\boldsymbol{A}$. Nevertheless, we will support these simulations with a simple theoretical bound that allows us to gain better understanding of how sparse $\boldsymbol{A}$ may be.

From Lemma 4, we can say that each $L \times T$ block $\boldsymbol{A}_{p} p \in\{1, \ldots, P\}$, has to be of rank $L$. If we put it together with Lemma 5 we can say that a valid $\boldsymbol{A}$ has a maximum of

$$
\begin{equation*}
r_{\max }=\left\lceil\frac{K}{K-L}-1\right\rceil \tag{26}
\end{equation*}
$$

equal $\boldsymbol{A}_{p}$ blocks. Therefore, if we aim at $\boldsymbol{A}$ matrices of 1 s and 0 s with the minimum number of 1 s , we can lower bound the number of 1 s through the following lemma.

Lemma 6: Given a valid $\boldsymbol{A} \in\{1,0\}^{M \times T}$, the number of 1 s in $\boldsymbol{A}$, which incidentally coincides with its squared Frobenius norm, can be lower bounded by

$$
\begin{equation*}
\|\boldsymbol{A}\|_{\mathrm{F}}^{2} \geq \sum_{k=1}^{Q-1} r_{\max }(k-Q)\binom{T}{k}+Q M, \tag{27}
\end{equation*}
$$

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-08.jpg?height=571&width=706&top_left_y=227&top_left_x=227)
Fig. 4. Minimum percentage of 1 s required for a valid $\boldsymbol{A} \in\{0,1\}^{M \times T}$ with respect to $100 / T_{\text {opt }}$ for $M=60, K=7, L=\{2,3,4,5,6\}(N=L)$.

where $Q$ is obtained by

$$
\begin{equation*}
Q=\arg \min _{q} \sum_{k=1}^{q} r_{\max }\binom{T}{k} \geq M . \tag{28}
\end{equation*}
$$

Proof: Let us impose the restriction that every row in $\boldsymbol{A}$ can be repeated a maximum of $r_{\text {max }}$ times, as suggested by Lemma 5, where the restriction of selecting the rows from different blocks can be relaxed since we are interested in a lower bound. Each row of $\boldsymbol{A}$ must have at least a 1 at some location, otherwise, considering $L \leq T$, a row of only 0 s would result in an $\boldsymbol{A}_{p}$ block with rank lower than $L$ (contradicting Lemma 4). Therefore, we can bound the number of 1 s in $\boldsymbol{A}$ by considering all possible combinations of rows having a single 1 , each of which could be repeated a maximum of $r_{\text {max }}$ times. Then, we can do the same for rows having 21 s , and go on until we have enough rows to fill the $M$ rows of $\boldsymbol{A}$. Straightforward combinatorics result in the statements in the lemma. $\square$

Even though the lower bound presented in Lemma 6 might look a bit hard to compute at first sight, for reasonable values of the design variables ( $M \leq 3 r_{\max } T$ ), it is enough to consider only rows with up to two 1 s to have enough rows for filling $\boldsymbol{A}$, i.e., $Q \leq 2$.

Figs. 4 and 5 show the minimum percentage of 1 s required to have a valid $\boldsymbol{A}$ through numerical optimization, as well as the theoretical lower bound from Lemma 6, with respect to $100 / T_{\text {opt }}$. The optimum $T, T_{\text {opt }}$, is computed as

$$
\begin{equation*}
T_{\mathrm{opt}}=\max \left(\left\lfloor M \frac{K-L}{K}+1\right\rfloor, K\right), \tag{29}
\end{equation*}
$$

which corresponds to the minimum integer $T$ that fulfills Theorem 1. The reason for having $100 / T_{\text {opt }}$ is that it corresponds to a trivial lower bound in the percentage of 1 s , i.e., if we have a single 1 per row. We can see that the relation between the minimum percentage of 1 s and $100 / T_{\text {opt }}$ is close to linear. In Fig. 4, $K$ is fixed and $L$ is changed, while in Fig. 5 it is the other way around. Although our initial intention was not to provide a tight bound to the numerical simulation, we can note that the obtained percentage of 1 s for valid $\boldsymbol{A}$ matrices is in general

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-08.jpg?height=568&width=706&top_left_y=227&top_left_x=1140)
Fig. 5. Minimum percentage of 1 s required for a valid $\boldsymbol{A} \in\{0,1\}^{M \times T}$ with respect to $100 / T_{\text {opt }}$ for $M=24, K=\{6,5,4\}, L=3$ ( $N=L$ ).

TABLE II
Minimum Number of 1 s Required to Have a Valid $\boldsymbol{A}$ for $M=60$, $T=T_{\mathrm{opt}}$
| $\mathrm{L} / \mathrm{K}$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 60 | 89 | 98 | 102 | 104 | 105 | 108 |
| 2 | - | 60 | 78 | 89 | 94 | 98 | 102 |
| 3 | - | - | 60 | 72 | 80 | 89 | 91 |
| 4 | - | - | - | 60 | 68 | 78 | 84 |
| 5 | - | - | - | - | 60 | 65 | 72 |
| 6 | - | - | - | - | - | 60 | 66 |


close to the lower bound computed given by Lemma 6 (within $\pm 3 \%$ error in the plots).

The algorithm for computing the minimum percentage of 1 s consists of selecting $\boldsymbol{A}$ by adding 1 s at random positions, with some constraints related to Lemma 4, until a valid $\boldsymbol{A}$ has been found. Then, we reduce through exhaustive search the number of 1 s in $\boldsymbol{A}$ as much as possible while maintaining its validity. The validity of $\boldsymbol{A}$ is evaluated by considering Theorem 2 .

Table II shows the minimum number of 1 s for having a valid $\boldsymbol{A}$ considering different values of $K$ and $L$ (recall $L \leq K$ for information-lossless processing). The same algorithm as for Figs. 4 and 5 is employed, and $T$ is also selected to be $T_{\text {opt }}$ from (29). We can see that, even though from Figs. 4 and 5 the percentage of 1 s increases with $L$ and decreases with $K$, for the total number of 1 s it is the other way around, i.e., it increases with $K$ and decreases with $L$. This is because the size of $\boldsymbol{A}$ increases at a higher rate when $T$ is increased. However, if we implement $\boldsymbol{A}$ using sum modules with only two inputs, we would need to subtract $T$ to the number of 1 s in $\boldsymbol{A}$, since a single 1 in a column of $\boldsymbol{A}$ would not require any sum module. Table III shows the minimum number of 2 -input sum modules required to have a valid $\boldsymbol{A}$, i.e., the values of this table correspond to the values of Table II subtracting the respective $T$ value to each entry. As we can see, the number of sum modules required does not vary considerably with $K$ and $L$, and it remains in the order of $M$.

TABLE III
Minimum Number of 2-Input Sum Modules Required to Implement a Valid $\boldsymbol{A}$ for $M=60, T=T_{\mathrm{opt}}$
| L/K | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 59 | 58 | 57 | 56 | 55 | 54 | 56 |
| 2 | - | 58 | 57 | 58 | 57 | 57 | 59 |
| 3 | - | - | 57 | 56 | 55 | 58 | 56 |
| 4 | - | - | - | 56 | 55 | 57 | 58 |
| 5 | - | - | - | - | 55 | 54 | 54 |
| 6 | - | - | - | - | - | 54 | 57 |


![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-09.jpg?height=564&width=720&top_left_y=717&top_left_x=206)
Fig. 6. Percentage of valid $\boldsymbol{A} \in\{0,1\}^{M \times T}$ with 1 s at random positions with respect to the percentage of 1 s for $M=24, L=3(\mathrm{~N}=\mathrm{L})$.

Fig. 6 shows the percentage of valid $\boldsymbol{A}$ matrices for different percentage of 1 s , where the 1 s are placed at random positions with the only restriction that they have at least a 1 per row and per column. The algorithm employed consists of generating a big number of random $\boldsymbol{A}$ matrices with the corresponding percentage of 1 s (while fulfilling a simple restriction related to Lemma 4 with $F=1$ ), and checking what percentage of them are valid (Theorem 2 comes in handy here too). The different curves correspond to the same parameter combinations as Fig. 5, where we can find the minimum percentage of 1 s that apply to the different values of $K$. As we can see, finding an $\boldsymbol{A}$ attaining a percentage of 1 s slightly higher than the optimum one ( $+10 \%$ ) is not that difficult since we can just put 1 s at random positions and, with high probability (around $80 \%$ in the case of $K=4$ ), this $\boldsymbol{A}$ will be valid.

## V. Discussion and Examples

As mentioned previously, one of the goals of this paper is to find the trade-off between the different system parameters required for the equivalent processing to be information-lossless. An interesting case is when $N=1$, since it relates directly to the trade-off between the centralized and decentralized architectures shown in Fig. 2. Assuming that our framework is equipped with a valid matrix $\boldsymbol{A}$, the trade-off between $L$ and $T$ comes directly from condition (24). We can select $T$ as $T_{\text {opt }}$ from (29), as can be seen in Fig. 7.

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-09.jpg?height=430&width=850&top_left_y=219&top_left_x=1052)
Fig. 7. Number of inputs to the CPU (related to $T$ ) v.s. number of outputs (left)/number of multiplications (right) per antenna (related to $L$ ).

It is interesting to observe that we reach a reduction compared with the centralized architecture also for $L=1$. To elaborate a bit further, we observe that with $L=1$, the number of CPU inputs becomes $T=T_{\text {max }} \triangleq\left\lfloor M-\frac{M}{K}+1\right\rfloor$. This reduction comes about since we have allowed the antennas to perform multiplications, which leads to a reduction in the number of CPU inputs from $M$ to, at most, $T_{\max }$. The centralized architecture, illustrated in the left part of Fig. 2, has the same number of outputs per antenna, namely 1 , but does not perform any multiplications. Therefore, the CPU must operate with $T=M$. If we let $L_{\text {mult }}$ denote the number of multiplications per antenna, the centralized architecture corresponds to $L_{\text {mult }}=0$, and we can select $T$ as

$$
T= \begin{cases}M & L_{\mathrm{mult}}=0 \\ \max \left(\left\lfloor M \frac{K-L_{\mathrm{mult}}}{K}+1\right\rfloor, K\right) & L_{\mathrm{mult}}>0\end{cases}
$$

This is conceptually illustrated in the right part of Fig. 7.
We conclude this section with a few examples.
Example 1: Assume a design with a CPU limited to $T^{\sim} \leq \sim 50$ inputs, and antenna panels with $L=2$ outputs. We now consider how many antennas and users ( $M$ and $K$, respectively) can be handled by the system. From (24), we have $50>M \frac{K-2}{K}$ implying that

$$
50 \frac{K}{K-2}>M .
$$

To maximize the left hand side, excluding the special case $K= L=2$ (which allows for an unlimited number of antennas), we set $K=3$ and obtain $M<150$ so that we can at most use 149 antennas. Differently put, if we choose to equip the base station with 149 antennas, we can at most serve $K=3$ users. With 150+ antennas, only 2 users can be served. Setting $K=4$, yields that at most 99 antennas can be used.

We next provide two numerical examples of the WAX decomposition. The first one is meant to illustrate that it is indeed possible to obtain valid sparse matrices $\boldsymbol{A}$ comprising only elements in the set $\{0,1\}$.

Example 2: Let $M=100, N=4, P=25, K=10$, and $L=4$. From Theorem 1, we have that $T>100 \times 0.6=60$, so
we take $T=61$. It can be numerically verified that the matrix

$$
\begin{equation*}
\boldsymbol{A}=\left[\right] \tag{30}
\end{equation*}
$$

is valid. We designed this $\boldsymbol{A}$ by aiming at a minimum number of non-zero elements, while satisfying both Lemma 4 and Lemma 5. It can be verified that $\boldsymbol{A}$ has 158 ones and 5942 zeros. Thus, merely $2.6 \%$ of $\boldsymbol{A}$ is non-zero.

Our next example is providing the reader with a graphical illustration of the WAX decomposition.

Example 3: Let $M=8, N=2, P=4, K=5$, and $L=2$. Thus, $T>4.8$, so we select $T=5$. In this case, the number of variables and the number of equations associated to the linear system (20) is $T K+M L=41$ and $M K=40$, respectively; thus, we have precisely one more variable than equations. A particular example of the WAX decomposition for the given parameters is shown in (31) at the bottom of this page. The strength of the WAX decomposition is that, for any $\boldsymbol{H}$, except for those in a set of measure 0 , the matrix $\boldsymbol{A}$ can be kept as it is while only $\boldsymbol{W}$ and $\boldsymbol{X}$ need to change.

## VI. Information-Loss Without WAX Decomposition

Throughout the previous sections of the paper we have focused on performing information-lossless processing within our framework, i.e., we have focused on the cases where the maximization (4) leads to $I_{\boldsymbol{Z}, \boldsymbol{S}}(\boldsymbol{z} ; \boldsymbol{s})=I_{\boldsymbol{Y}, \boldsymbol{S}}(\boldsymbol{y} ; \boldsymbol{s})$. We have defined the WAX decomposition, which allows performing informationlossless processing within our framework. Theorem 1 sets the main constraints on the system dimensions for WAX decomposition, and equivalently information-lossless processing, to be possible within our framework. However, it is of great interest to know the information-loss produced when WAX decomposition is not possible, i.e., we would like to solve ( 4 ) when Theorem 1 is not satisfied.

Solving (4) is a research challenge in itself which might lead to future work on the topic. In this section we will present initial ideas, as well as numerical results using standard optimization methods, to get an overall understanding of the informationlosses that are induced when having lower $T$ than the minimum
required from Theorem 1. We will again focus on the general case where $N=L$, and we will only consider randomly chosen $\boldsymbol{A}$ and $\boldsymbol{H}$ matrices.

## A. Approximate $M F$

A simple first approach, intuitively related to how we compute WAX decomposition, is to work on the minimization problem

$$
\begin{align*}
\underset{\boldsymbol{X},\left\{\hat{\boldsymbol{W}}_{p}\right\}_{p=1}^{P}}{\operatorname{minimize}} & \|\boldsymbol{A} \boldsymbol{X}-\hat{\boldsymbol{W}} \boldsymbol{H}\|_{\mathrm{F}}^{2}, \\
\text { s.t. } & \operatorname{rank}\left(\hat{\boldsymbol{W}}_{p}\right)=L, \forall p  \tag{32}\\
& \|\boldsymbol{X}\|+\|\hat{\boldsymbol{W}}\|=c,
\end{align*}
$$

where $\hat{\boldsymbol{W}}$ has the same structure as (3) for $N=L$ and $P= M / L$, and the actual matrix $\boldsymbol{W}$ to be used in our framework would be obtained as $\boldsymbol{W}=\hat{\boldsymbol{W}}^{-1}$. The last constraint in (32) ensures a non-zero solution, where the scalar $c$ can be any non-zero real value. ${ }^{4}$ The minimization (32) leads to the WAX decomposition when Theorem 1 applies. This means that we could solve both problems using the same approach, and thus, without altering the overall complexity. In case (24) is fulfilled, (32) would give 0 , and the solution would also solve the maximization (4), which is not true in general.

Solving (32) can be seen as applying approximate MF within our framework. This minimization can be found in closed-form when $L \leq \min (T, K)$ as we will now prove. Let us rewrite the norm as

$$
\begin{equation*}
\|\boldsymbol{A} \boldsymbol{X}-\hat{\boldsymbol{W}} \boldsymbol{H}\|_{\mathrm{F}}^{2}=\sum_{p=1}^{P}\left\|\boldsymbol{A}_{p} \boldsymbol{X}-\hat{\boldsymbol{W}}_{p} \boldsymbol{H}_{p}\right\|_{\mathrm{F}}^{2} . \tag{33}
\end{equation*}
$$

Assuming the optimum $\boldsymbol{X}$ has been fixed, we would have $\hat{\boldsymbol{W}}_{p}=\boldsymbol{A}_{p} \boldsymbol{X} \boldsymbol{H}_{p}^{\dagger}\left(\boldsymbol{H}_{p}^{\dagger}\right.$ being the right pseudo-inverse of $\left.\boldsymbol{H}_{p}\right)$, which is of rank $\min (T, K, L)$ when $\boldsymbol{A}$ and $\boldsymbol{H}$ are randomly chosen. We can restrict ourselves to $L \leq \min (T, K)$ due to its previously mentioned practical interest. In this case, (32) is solved by considering the equivalent linear system from (21)

$$
\begin{equation*}
\|\boldsymbol{A} \boldsymbol{X}-\hat{\boldsymbol{W}} \boldsymbol{H}\|_{\mathrm{F}}^{2}=\boldsymbol{u}^{H} \boldsymbol{B}^{H} \boldsymbol{B} \boldsymbol{u} . \tag{34}
\end{equation*}
$$

[^4]$$
\underbrace{\left[\begin{array}{cc|cccccc}
1 & -1 & 0 & 0 & 0 & 0 & 0 & 0  \tag{31}\\
2 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & -1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 2 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 2 & -1 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 2 & -1 \\
0 & 0 & 0 & 0 & 0 & 0 & 2 & 2
\end{array}\right]}_{\boldsymbol{W}} \underbrace{\left[\begin{array}{ccccc}
1 & 0 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 & 1 \\
1 & 0 & 0 & 1 & 1 \\
0 & 1 & 0 & 1 & 1 \\
0 & 0 & 1 & 1 & 1
\end{array}\right]}_{\boldsymbol{A}} \underbrace{\left[\begin{array}{ccccc}
-2 & -1 & -1 & 2 & 2 \\
1 & -2 & -1 & 1 & 2 \\
1 & -1 & -2 & -1 & -2 \\
0 & 2 & 0 & -1 & 0 \\
0 & -1 & 2 & 1 & -2
\end{array}\right]}_{\boldsymbol{X}} \underbrace{[ }_{\boldsymbol{H}}{ }_{\left.\left[\begin{array}{ccccc}
-3 & 1 & 0 & 1 & 0 \\
-2 & -4 & -3 & 5 & 6 \\
1 & 1 & -2 & -2 & -2 \\
0 & -2 & 0 & 1 & 0 \\
-2 & -2 & 5 & 4 & -4 \\
2 & -2 & 3 & 0 & -4 \\
1 & -2 & 2 & 3 & 4 \\
4 & -2 & 2 & 0 & -8
\end{array}\right]\right]}^{[ }
$$

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-11.jpg?height=566&width=712&top_left_y=227&top_left_x=210)
Fig. 8. Average relative rate (in percentage), $I_{\boldsymbol{Z}, \boldsymbol{S}}(z, s) / I_{\boldsymbol{Y}, \boldsymbol{S}}(y, z)$, with $\boldsymbol{A}$ and $\boldsymbol{H}$ having IID Gaussian entries, for $M=24, K=5, L=3, T_{\text {opt }}=10$.

The vector $\boldsymbol{u}$ corresponds to the entries of matrices $\boldsymbol{X}$ and $\hat{\boldsymbol{W}}$, so the constraint on the norms of $\hat{\boldsymbol{W}}$ and $\boldsymbol{X}$ corresponds to an arbitrary norm constraint on $\boldsymbol{u}$. With this in mind, the solution to the minimization problem is obtained by setting $\boldsymbol{u}$ to be the eigenvector associated to the lowest eigenvalue of $\boldsymbol{B}^{H} \boldsymbol{B}$. If the conditions for WAX were fulfilled, the lowest eigenvalue of $\boldsymbol{B}^{H} \boldsymbol{B}$ would be 0 , which would lead to the information-lossless solution.

## B. Antenna Selection

Another practical approach that would give a lower bound to the maximum $I_{\boldsymbol{Z}, \boldsymbol{S}}(z, s)$ from (4) is to consider antenna selection so as to reduce $M$ until Theorem 1 is satisfied. Note that this approach is valid only when $T \geq K$, which was not the case with the previous approach. Furthermore, for $N>1$, the antenna selection would correspond to panel selection since we need an integer number of panels, which means we can only reduce $N$ antennas at a time.

How to optimally make the panel selection is also a research problem in itself, but we limit our results to simple selection where the panels having the highest local channel matrix norms are the ones being used.

## C. Numerical Results

Definition 2: Let us define the relative rate for our framework as

$$
\begin{equation*}
\mathbb{E}_{\boldsymbol{A}, \boldsymbol{H}}\left(\frac{I_{\boldsymbol{Z}, \boldsymbol{S}}(z, s)}{I_{\boldsymbol{Y}, \boldsymbol{S}}(y, s)}\right), \tag{35}
\end{equation*}
$$

where $\boldsymbol{A}$ and $\boldsymbol{H}$ are standard IID Gaussian random matrices.
Figs. 8 and 9 show the average relative rates, which have been optimized using norm minimization (32) and panel selection. We have also included as a comparison the average relative rate obtained by standard brute force numerical optimization using the result from (32) as starting point. This numerical optimization can give us a hint of what average relative rates could be achieved if more clever optimization approaches were considered. In the plots, we have considered the range of $L$

![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-11.jpg?height=566&width=714&top_left_y=227&top_left_x=1121)
Fig. 9. Average relative rate (in percentage), $I_{\boldsymbol{Z}, \boldsymbol{S}}(z, s) / I_{\boldsymbol{Y}, \boldsymbol{S}}(y, z)$, with $\boldsymbol{A}$ and $\boldsymbol{H}$ having IID Gaussian entries, for $M=24, K=5, T=5, L_{\text {opt }}=4$.

and $T$ values not accepting a WAX decomposition according to Theorem 1. Fig. 8 shows that when we reduce $T$ below $T_{\text {opt }}$ the performance gets slowly degraded, so the system would still be able to work at acceptable rates even if we cannot perform WAX decomposition. In the case of Fig. 9, reducing $L$ below $L_{\text {opt }},{ }^{5}$ attains a steeper loss, but the degradation is still reasonable. We can also see that the norm minimization associated to (32) presents a considerable loss with respect to the numerical optimization, but it can still serve as a simple auxiliary method that allows our framework to keep serving users under conditions where WAX is not possible, e.g., if the number of users increase. In fact, (32) corresponds to the WAX decomposition when the parameters allow it, so that no further processing would be needed in such a system.

Panel selection, can perform better than the norm minimization in some cases, but the limitation of having to disregard full panels makes it perform slightly worse for most values of $T$ in Fig. 8. Furthermore, this method is slightly less versatile than norm minimization since it is not available for all possible values of $T$, as can be seen in Fig. 8. However, we can note that $T<K$ intuitively translates into having to discard the data from certain users, which could potentially be considered in more complex antenna selection schemes.

## VII. Conclusion

We have introduced a general framework that allows the exploitation of the trade-off between complexity (number of multiplications/outputs per panel) and level of decentralization (connections to CPU) in multi-antenna architectures. We have presented the WAX decomposition, a matrix decomposition that achieves information-lossless processing within our framework under some restrictions. Said restrictions also describe the trade-off between number of multiplications/outputs per panel and number of connections to the CPU if we consider only information-lossless processing. Furthermore, we have studied the problem of finding simple combining networks (A matrices)

[^5]that admit WAX decomposition within our framework. Finally, we have broadly studied the information-loss produced when the system parameters lead to non-availability of the WAX decomposition.

Future work could include a deeper study on the cases where WAX decomposition is not available and information-lossy processing has to be applied. This same line would include the design of efficient algorithms and analytical solutions to optimize the achievable information rates. Furthermore, finding sufficient conditions for the combining network (i.e., $\boldsymbol{A}$ ) to be valid for WAX decomposition still remains unresolved. Other lines of work could include narrowing the study to some of the exceptions that we have not covered such as when the parameters are not divisible, etc.

## Appendix A

## Proof of Theorem 1

We first make the observation that the rank of $\boldsymbol{A}$ cannot be lower than the rank of $\boldsymbol{H}$. The rank of a randomly chosen $\boldsymbol{A}$ is $\min (M, T)$ with probability 1 . Assuming that $M \geq K$, this implies $T \geq K$, expressed as $T>\max (\cdot, K-1)$ in the statement.

We next provide a lemma that will be useful.
Lemma 7: Let $\boldsymbol{W}$ and $\hat{\boldsymbol{W}}$ be two matrices of the same form as $\boldsymbol{W}$ in (3) with $N=L$ (i.e., they are block diagonal matrices where the blocks are $L \times L$ matrices). If $\boldsymbol{A} \boldsymbol{X}=\hat{\boldsymbol{W}} \boldsymbol{H}$ is solvable such that $\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right)>0,1 \leq p \leq P$, then $\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}=\boldsymbol{H}$ is solvable.

Proof: Suppose $\boldsymbol{A} \boldsymbol{X}=\hat{\boldsymbol{W}}^{H} \boldsymbol{H}$ is solvable such that $\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right)>0,1 \leq p \leq P$. This implies that $\hat{\boldsymbol{W}}^{-1}$ exists. Thus,

$$
\hat{\boldsymbol{W}}^{-1} \boldsymbol{A} \boldsymbol{X}=\boldsymbol{H} .
$$

The lemma follows by observing that $\hat{\boldsymbol{W}}^{-1}$ is of the same form as $\boldsymbol{W}$, so we can take $\boldsymbol{W}=\hat{\boldsymbol{W}}^{-1}$.

Let us now study $\boldsymbol{A} \boldsymbol{X}=\hat{\boldsymbol{W}} \boldsymbol{H}$. Said matrix equation specifies $M T$ line ar equations in $T K+M L$ variables, and hence, it is solvable if $T>M(K-L) / K$, as can be seen from the vectorized version in (21). It remains to show that for randomly chosen $\boldsymbol{A}$ and $\boldsymbol{H}$, the solution satisfies $\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right)>0,1 \leq p \leq P$. Let us define $\mathcal{V}$ as the set of admissible solutions, i.e.,

$$
\begin{align*}
\mathcal{V}=\{\boldsymbol{A}, \boldsymbol{H} \mid & \exists \hat{\boldsymbol{W}}, \boldsymbol{X}: \boldsymbol{A} \boldsymbol{X}=\hat{\boldsymbol{W}} \boldsymbol{H}, \\
& \left.\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right) \neq 0, \forall p, \operatorname{det}\left(\boldsymbol{B} \boldsymbol{B}^{H}\right) \neq 0\right\}, \tag{36}
\end{align*}
$$

where $\boldsymbol{B}=\left[\boldsymbol{B}_{1} \boldsymbol{B}_{2}\right]$ is again the matrix associated to the equivalent linear system (21), which is given by (23). Assuming that $\boldsymbol{B}$ is full-rank, the solution to $\boldsymbol{A} \boldsymbol{X}=\hat{\boldsymbol{W}} \boldsymbol{H}$ depends on $F=T K+M L-M K$ free variables, here denoted by $\left\{z_{f}\right\}$. The solution $\{\hat{\boldsymbol{W}}\}_{i, j}$ is a linear combination of the free variables $\left\{z_{f}\right\}$ where the weights depend on $\boldsymbol{A}$ and $\boldsymbol{H}$, i.e.,

$$
\left\{\hat{\boldsymbol{W}}_{p}\right\}_{i, j}=\sum_{f=1}^{F} c_{p, i, j, f}(\boldsymbol{A}, \boldsymbol{H}) z_{f}
$$

Note that the number of free variables, $F$, can be increased if $\boldsymbol{B}$ is not full-rank (leading to a different polynomial expression), that is why we are only interested in the solutions giving a full-rank $\boldsymbol{B}$, i.e., $\operatorname{det}\left(\boldsymbol{B}^{H}\right) \neq 0$. Thus, the following lemma will come in handy.

Lemma 8: Given randomly chosen matrices $\boldsymbol{H}$ and $\boldsymbol{A}$, the matrix $\boldsymbol{B}=\left[\boldsymbol{B}_{1} \boldsymbol{B}_{2}\right]$ ( $\boldsymbol{B}_{1}$ and $\boldsymbol{B}_{2}$ are defined as in (23)) fulfills $\operatorname{det}\left(\boldsymbol{B}^{H}\right) \neq 0$ with probability 1.

Proof: We can define the determinant $\operatorname{det}\left(\boldsymbol{B}^{H}\right)$ as a polynomial expression of the form

$$
\operatorname{det}\left(\boldsymbol{B B}^{H}\right)=\sum_{g} b_{g}(\boldsymbol{A}, \boldsymbol{H}) \prod_{i, j, l, k}\{\boldsymbol{H}\}_{i, j}^{h_{i, j, g}}\{\boldsymbol{A}\}_{l, k}^{a_{l, k, g}} .
$$

This polynomial expression will evaluate to 0 only for a countable set (which thus attains probability 0 ) of $\boldsymbol{A}$ and $\boldsymbol{H}$ matrices if we can find at least an $\boldsymbol{A}$ and an $\boldsymbol{H}$ such that $\operatorname{det}\left(\boldsymbol{B} \boldsymbol{B}^{H}\right) \neq 0$. One example of this is when $\boldsymbol{A}$ is chosen randomly and we have $\{\boldsymbol{H}\}_{i, j}=\{\boldsymbol{A}\}_{i, j}, i \in\{1, \ldots M\}, j \in\{1, \ldots, K\}$.

A similar reasoning to the one used in the proof of Lemma 8 can be applied to show that for randomly chosen $\boldsymbol{A}$ and $\boldsymbol{H}$ we have $\hat{\boldsymbol{W}} \neq 0$ with probability 1 . The determinant $\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right)$ can be written as a polynomial combination of the previous $\left\{\hat{\boldsymbol{W}}_{p}\right\}_{i, j}$. Thus we can express it as

$$
\begin{equation*}
\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right)=\sum_{g=1}^{G} \tilde{c}_{g}(\boldsymbol{A}, \boldsymbol{H}) \prod_{f=1}^{F} z_{f}^{q_{g, f}}, \tag{37}
\end{equation*}
$$

for some $G$, with $\sum_{f=1}^{F} q_{g, f}=P, \forall g$. Thus, the only possibility for having $\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right)=0$ is if the coefficients are zero, i.e., $\tilde{c}_{g}(\boldsymbol{A}, \boldsymbol{H})=0,1 \leq g \leq G$. However, the coefficients $\tilde{c}_{g}(\boldsymbol{A}, \boldsymbol{H})$ are rational expressions of the entries in $\boldsymbol{A}$ and $\boldsymbol{H}$. This means that, in order to have $\tilde{c}_{g}(\boldsymbol{A}, \boldsymbol{H})=0$, a polynomial multi-variate expression of the entries in $\boldsymbol{A}$ and $\boldsymbol{H}$ must be 0 . Again, this can only happen at most in a countable set of $\boldsymbol{A}$ and $\boldsymbol{H}$ as long as we find an $\boldsymbol{A}$ and an $\boldsymbol{H}$ such that $\operatorname{det}\left(\hat{\boldsymbol{W}}_{p}\right), \forall p$, while still assuring that $\boldsymbol{B}$ is full-rank so that $F$ remains fixed. The same example as in the proof of Lemma 8, i.e., randomly chosen $\boldsymbol{A}$ and $\{\boldsymbol{H}\}_{i, j}=\{\boldsymbol{A}\}_{i, j}, i \in \{1, \ldots M\}, j \in\{1, \ldots, K\}$, gives the trivial solution $\hat{\boldsymbol{W}}=\mathbf{I}_{M}$, and thus fulfills both conditions. Therefore, we have proved that a randomly chosen $\boldsymbol{A}$ and $\boldsymbol{H}$ will be in the set $\mathcal{V}$ with probability 1 .

## Appendix B <br> Proof of Lemma 5

From the structure of $\boldsymbol{B}_{1}$ in (23), we observe that a particular row of $\boldsymbol{A}$ appears exactly in $K$ rows of $\boldsymbol{B}$. Let us denote $\boldsymbol{B}_{0}$ as the submatrix of $\boldsymbol{B}$ formed by all rows in $\boldsymbol{B}$ where the rows of $\boldsymbol{A}_{0}$ appear. Clearly, to satisfy (21), we must in particular satisfy $\boldsymbol{B}_{0} \boldsymbol{u}=\mathbf{0}_{R K \times 1}$. Now, $\boldsymbol{B}_{0}$ reads

$$
\boldsymbol{B}_{0}=\left[\begin{array}{ll}
\boldsymbol{I}_{K} \otimes \boldsymbol{A}_{0} & \widehat{\boldsymbol{H}}_{0}
\end{array}\right]
$$

where $\widehat{\boldsymbol{H}}_{0}$ is formed from $\boldsymbol{H}$ as follows: Let $\iota(r)$ denote the block $\boldsymbol{H}_{\iota(r)}$ where the $r$ th row in $\boldsymbol{A}_{0}$ is taken from. Let
$\boldsymbol{H}_{0}=\left[\begin{array}{llll}\boldsymbol{H}_{\iota(1)}^{T} & \boldsymbol{H}_{\iota(2)^{T}} & \ldots & \boldsymbol{H}_{\iota(R)}^{T}\end{array}\right]^{T}$, and let $\mathbb{I} \mathbb{I}(\ell)$ be an $R \times L$ matrix with a single entry equal to 1 at row $\ell$ and column $(\iota(\ell) \bmod L)+1$, and all other equal to 0 . Then,

$$
\begin{array}{r}
\widehat{\boldsymbol{H}}_{0}=\left[\begin{array}{llll}
\mathbf{0}_{\mathcal{D}_{0}} & \boldsymbol{H}_{\iota(1)}^{H} \otimes \mathbb{I}(1) & \mathbf{0}_{\mathcal{D}_{1}} & \boldsymbol{H}_{\iota(2)}^{H} \otimes \mathbb{I}(2) \\
& \ldots & \mathbf{0}_{\mathcal{D}_{R-1}} & \boldsymbol{H}_{\iota(R)}^{H} \otimes \mathbb{I} \mathbb{I}(R) \\
\mathbf{0}_{\mathcal{D}_{R}}
\end{array}\right]
\end{array}
$$

where we have used the shorthand notation

$$
\begin{aligned}
& \mathcal{D}_{k}=R K \times(\iota(k+1)-\iota(k)) L^{2}, \\
& \iota(0) \triangleq 1, \quad \iota(R+1) \triangleq M / L .
\end{aligned}
$$

To study the null space of $\boldsymbol{B}_{0}$ we may just as well study the null space of $\left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \boldsymbol{B}_{0}$, where $\boldsymbol{Q}_{0} \boldsymbol{R}_{0}=\boldsymbol{A}_{0}$ is the QR decomposition of $\boldsymbol{A}_{0}$. We have,

$$
\left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \boldsymbol{B}_{0}=\left[\begin{array}{ll}
\boldsymbol{I}_{K} \otimes \boldsymbol{R}_{0} & \left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \widehat{\boldsymbol{H}}_{0} \tag{39}
\end{array}\right] .
$$

Let $\kappa=\operatorname{rank}\left(\boldsymbol{A}_{0}\right)$. The matrix $\boldsymbol{I}_{K} \otimes \boldsymbol{R}_{0}$ consequently has $K(R-\kappa)$ all-zero rows.

If we extract said all-zero rows, we obtain,

$$
\left[\mathbf{0}_{K(R-\kappa) \times T K} \boldsymbol{P}\left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \widehat{\boldsymbol{H}}_{0}\right]\left[\begin{array}{c}
\operatorname{vec}(\boldsymbol{X}) \\
\operatorname{vec}\left(\boldsymbol{W}_{1}\right) \\
\vdots \\
\operatorname{vec}\left(\boldsymbol{W}_{P}\right)
\end{array}\right]=\mathbf{0}_{K(R-\kappa) \times 1}
$$

where $\boldsymbol{P}$ is a $K(R-\kappa) \times K R$ matrix that extracts the rows where $\boldsymbol{I}_{K} \otimes \boldsymbol{R}_{0}$ is all-zero. This implies that we can discard $\boldsymbol{X}$ so that we equivalently obtain

$$
\boldsymbol{P}\left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \widehat{\boldsymbol{H}}_{0}\left[\begin{array}{c}
\operatorname{vec}\left(\boldsymbol{W}_{1}\right)  \tag{40}\\
\vdots \\
\operatorname{vec}\left(\boldsymbol{W}_{P}\right)
\end{array}\right]=\mathbf{0}_{K(R-\kappa) \times 1}
$$

We next note that, due to the many all-zero columns in $\widehat{\boldsymbol{H}}_{0}$ (represented by the terms $\mathbf{0}_{\mathcal{D}_{k}}$ in (38)), not all the $\boldsymbol{W}_{p}$ matrices matter. In fact, it can be straightforwardly verified that (40) is equivalent to

$$
\boldsymbol{P}\left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \overline{\boldsymbol{H}}_{0}\left[\begin{array}{c}
\boldsymbol{w}_{\iota(1)}  \tag{41}\\
\vdots \\
\boldsymbol{w}_{\iota(R)}
\end{array}\right]=\mathbf{0}_{K(R-\kappa) \times M L},
$$

where $\boldsymbol{w}_{m}$ is the $1 \times L$ vector formed from extracting the entries at the $m$ th row of $\boldsymbol{W}$ that are allowed to take non-zero values, and

$$
\overline{\boldsymbol{H}}_{0}=\left[\begin{array}{llll}
\boldsymbol{H}_{\iota(1)}^{H} \otimes \mathbb{I}(1) & \boldsymbol{H}_{\iota(2)}^{H} \otimes \mathbb{I}(2) & \ldots & \boldsymbol{H}_{\iota(R)}^{H} \otimes \mathbb{I}(R) \tag{42}
\end{array}\right]
$$

where $\mathbb{I}(\ell)$ is the non-zero column of $\mathbb{I} \mathbb{I}(\ell)$.
For randomly chosen $\boldsymbol{H}$, the matrix $\boldsymbol{P}\left(\boldsymbol{I}_{K} \otimes \boldsymbol{Q}_{0}^{H}\right) \overline{\boldsymbol{H}}_{0}$ is full rank with probability 1 . Therefore, (42) only has a non-trivial solution whenever the number of unknowns is larger than the
number of equations, i.e., whenever, $R L>K(R-\kappa)$. Consequently,

$$
\kappa>R \frac{K-L}{K} .
$$

## Appendix C Necessary condition for $\boldsymbol{A}$

As per previous results, a matrix $\boldsymbol{H}$ can, with probability 1 , be decomposed as $\boldsymbol{H}=\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}$ if and only if there exists a full rank matrix $\hat{\boldsymbol{W}}$ such that $\boldsymbol{A} \boldsymbol{X}=\hat{\boldsymbol{W}} \boldsymbol{H}$. We are now interested in establishing necessary conditions for the matrix $\boldsymbol{A}$ so that this is possible. Let $\boldsymbol{A}_{\mathcal{S}}$ denote a submatrix of $\boldsymbol{A}$ comprising an arbitrary selection of rows in $\boldsymbol{A}$ with $\operatorname{rank}\left(\boldsymbol{A}_{\mathcal{S}}\right)=r$. An immediate consequence is that $\operatorname{rank}\left(\boldsymbol{A}_{\mathcal{S}} \boldsymbol{X}\right) \leq r$. Assuming that $\boldsymbol{H}=\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}$ holds, $\operatorname{rank}\left(\hat{\boldsymbol{W}}_{\mathcal{S}} \boldsymbol{H}\right)=\operatorname{rank}\left(\boldsymbol{A}_{\mathcal{S}} \boldsymbol{X}\right)$, where $\hat{\boldsymbol{W}}_{\mathcal{S}}$ is a submatrix of $\hat{\boldsymbol{W}}$ comprising rows corresponding to those in $\boldsymbol{A}_{\mathcal{S}}$. On the other hand, if no $\hat{\boldsymbol{W}}_{\mathcal{S}}$ exists such that $\operatorname{rank}\left(\hat{\boldsymbol{W}}_{\mathcal{S}} \boldsymbol{H}\right) \leq r$, we can infer that $\boldsymbol{A}$ does not allow for a WAX decomposition, i.e., there are no matrices $\boldsymbol{W}$ and $\boldsymbol{X}$ such that $\boldsymbol{H}=\boldsymbol{W} \boldsymbol{A} \boldsymbol{X}$. Therefore, a necessary condition on $\boldsymbol{A}$ for the existence of a WAX decomposition is

$$
\begin{equation*}
\operatorname{rank}\left(\boldsymbol{A}_{\mathcal{S}}\right) \geq \min _{\hat{W}_{\mathcal{S}} \in \mathcal{W}} \operatorname{rank}\left(\hat{\boldsymbol{W}}_{\mathcal{S}} \boldsymbol{H}\right), \quad \forall \mathcal{S}, \tag{43}
\end{equation*}
$$

where we will define the set $\mathcal{W}$ after having introduced further notation. The matrix $\boldsymbol{A}$ contains $M$ rows, and since $L$ divides $M$, $\boldsymbol{A}$ contains $P=M / L$ blocks of $L$ rows. Let the $1 \times P$ vector $\boldsymbol{a}$ denote the number of rows in $\boldsymbol{A}_{\mathcal{S}}$ taken from the $p$ th block in $\boldsymbol{A}$, and let $\boldsymbol{A}_{\mathcal{S}, p}$ and $\hat{\boldsymbol{W}}_{\mathcal{S}, p}$ be the $a_{p} \times T$ and $a_{p} \times M$ submatrices of $\boldsymbol{A}_{\mathcal{S}}$ and $\hat{\boldsymbol{W}}_{\mathcal{S}}$, respectively, formed from these $a_{p}$ rows. With that, $\mathcal{W}$ is the set containing all block-diagonal matrices where the $p$ th block is of dimensions $a_{p} \times K$ and has rank $a_{p}$ (the latter is needed to ensure that the overall matrix $\hat{W}$ is invertible).

We are now ready to study (43). Suppose that the minimum of (43) is $r$. Since $\boldsymbol{W}_{\mathcal{S}} \boldsymbol{H}$ has dimensions $\left(\sum_{p} a_{p}\right) \times K$ this implies that the null-space of $\hat{\boldsymbol{W}}_{\mathcal{S}} \boldsymbol{H}$ has dimension $K-r$. Thus, if $\operatorname{rank}\left(\hat{\boldsymbol{W}}_{\mathcal{S}} \boldsymbol{H}\right)=r$, there must exist a $K \times(K-r)$ matrix $\boldsymbol{N}$ such that $\hat{\boldsymbol{W}}_{\mathcal{S}} \boldsymbol{H} \boldsymbol{N}=\mathbf{0}$. Recalling that $\hat{\boldsymbol{W}}_{\mathcal{S}}$ is block-diagonal with each block being of dimension $a_{p} \times L$ and having rank $a_{p}$, it follows that

$$
\begin{equation*}
\operatorname{rank}\left(\boldsymbol{H}_{p} \boldsymbol{N}\right) \leq L-a_{p} \tag{44}
\end{equation*}
$$

where $\boldsymbol{H}_{p}$ is of dimension $L \times K$ and $\boldsymbol{H}=\left[\begin{array}{lll}\boldsymbol{H}_{1}^{\mathrm{H}} & \cdots & \boldsymbol{H}_{P}^{\mathrm{H}}\end{array}\right]^{\mathrm{H}}$. Thus, if we want to solve the minimization in (43), we have the equivalent problem of finding the maximum possible number of columns in the matrix $\boldsymbol{N}$ so that it is full rank and $\operatorname{rank}\left(\boldsymbol{H}_{p} \boldsymbol{N}\right) \leq L-a_{p}, p=1 \ldots P$.

We next define the rank-profile $\boldsymbol{J}$ of a matrix $\boldsymbol{N}$ as $J_{b, p}=\operatorname{rank}\left(\boldsymbol{H}_{p} \boldsymbol{N}_{1: b}\right)-\operatorname{rank}\left(\boldsymbol{H}_{p} \boldsymbol{N}_{1: b-1}\right)$, where $\boldsymbol{N}_{1: b}$ denotes columns $1,2, \ldots, b$ of $\boldsymbol{N}$. We remark that $J_{b, p} \in\{0,1\}$, and that $\boldsymbol{J}$ depends on $\boldsymbol{H}$, although our notation does not indicate this dependency. In the following lemma, we characterize the admissible rank-profiles.

Lemma 9: There exists a full rank matrix $N$ with $B$ columns such that $\operatorname{rank}\left(\boldsymbol{H}_{p} \boldsymbol{N}\right) \leq L-a_{p}$ if and only if the rank-profile
matrix $\boldsymbol{J}$ satisfies

$$
\begin{gathered}
K-L d_{<L}(\overline{\boldsymbol{a}})+\sum_{b^{\prime}=1}^{b-1} \sum_{p=1}^{P} J_{b^{\prime}, p}+\sum_{p=1}^{P} J_{b, p}\left(L-\sum_{b^{\prime}=1}^{b-1} J_{b^{\prime}, p}\right) \geq b, \\
1 \leq b \leq B, \\
\sum_{b=1}^{B} J_{b, p} \leq \bar{a}_{p}, \quad 1 \leq p \leq P,
\end{gathered}
$$

where $d_{<L}(\cdot)$ denotes the number of elements of its argument that are less than $L$, and $\bar{a}_{p}=L-a_{p}$.

Proof: We first note that if $a_{p}=0$ for any $p$, then the condition in (44) is trivially satisfied for any $\boldsymbol{N}$ so we can without loss of generality assume that $a_{p}>0, \forall p$. From the definition of $J_{b, p}$ if follows that $\operatorname{rank}\left(\boldsymbol{H}_{p} \boldsymbol{N}\right)=\sum_{b=1}^{B} J_{b, p}$; thus, the second set of conditions in the lemma is trivial.

Consider now a specific value $b$. If $J_{b, p}=0$, it follows that column $b$ of $\boldsymbol{N}, \boldsymbol{n}_{b}$ is restricted to

$$
\boldsymbol{n}_{b} \in \mathcal{I}_{b, p}=\mathcal{N}\left(\boldsymbol{H}_{p}\right) \cup \operatorname{span}\left(\boldsymbol{H}_{p}^{+} \boldsymbol{H}_{p} \boldsymbol{N}_{1: b-1}\right),
$$

while $J_{b, p}=1$ does not restrict $\boldsymbol{n}_{b}$ so that $\boldsymbol{n}_{b} \in \mathcal{I}_{b, p}=\mathbb{C}^{K}$. By inspection, it can be seen that the dimensionality of $\mathcal{I}_{b, p}$ can be written as

$$
\operatorname{dim}\left(\mathcal{I}_{b, p}\right)=K\left(1-J_{b, p}\right)+J_{b, p}\left(K-L+\sum_{b^{\prime}=1}^{b-1} J_{b, p}\right) .
$$

Altogether, we have that

$$
\boldsymbol{n}_{b} \in \bigcap_{p=1}^{P} \mathcal{I}_{b, p} .
$$

The dimensionality of the intersection satisfies

$$
\operatorname{dim}\left(\bigcap_{p=1}^{P} \mathcal{I}_{b, p}\right)=\sum_{p=1}^{P} \operatorname{dim}\left(\mathcal{I}_{b, p}\right)-(P-1) K .
$$

This dimensionality must be at least b , since there are already $b-1$ vectors in $\boldsymbol{N}_{1: b-1}$ in the same space, and the rank of $\boldsymbol{N}_{1: b}$ must be full for all $b$. By manipulation, the statement of the lemma can be obtained.

Altogether, a necessary condition on $\boldsymbol{A}$ is that the rank of any submatrix $\boldsymbol{A}_{\mathcal{S}}$ satisfies $\operatorname{rank}\left(\boldsymbol{A}_{\mathcal{S}}\right) \geq K-B_{\mathcal{S}}$, where $B_{\mathcal{S}}$ is the largest integer $B$ that satisfies the conditions specified in Lemma 9; note that the vector $\boldsymbol{a}$ in the conditions depends on $\mathcal{S}$. It can be seen from Lemma 9 that finding the largest integer $B$ that satisfies the conditions is a non-linear (quadratic) integer problem and we have not been able to solve it in closed form.

## References

[1] J. V. Alegría, F. Rusek, J. R. Sánchez, and O. Edfors, "Trade-offs in quasi-decentralized massive MIMO," in Proc. IEEE Int. Conf. Commun. Workshops, 2020, pp. 1-6.
[2] J. G. Andrews et al., "What will 5G be?," IEEE J. Sel. Areas Commun., vol. 32, no. 6, pp. 1065-1082, Jun. 2014.
[3] Z. Pi and F. Khan, "An introduction to millimeter-wave mobile broadband systems," IEEE Commun. Mag., vol. 49, no. 6, pp. 101-107, Jun. 2011.
[4] T. L. Marzetta, "Noncooperative cellular wireless with unlimited numbers of base station antennas," IEEE Trans. Wireless Commun., vol. 9, no. 11, pp. 3590-3600, Nov. 2010.
[5] F. Rusek et al., "Scaling up MIMO: Opportunities and challenges with very large arrays," IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40-60, Jan. 2013.
[6] S. Hu, F. Rusek, and O. Edfors, "Beyond massive MIMO: The potential of data transmission with large intelligent surfaces," IEEE Trans. Signal Process., vol. 66, no. 10, pp. 2746-2758, May 2018.
[7] S. Malkowsky et al., "The world's first real-time testbed for massive MIMO: Design, implementation, and validation," IEEE Access, vol. 5, pp. 9073-9088, 2017.
[8] C. Shepard et al., "Argos: Practical many-antenna base stations," in Proc. 18th Annu. Int. Conf. Mobile Comput. Netw., New York, NY, USA, 2012, pp. 53-64.
[9] Q. Yang et al., "Bigstation: Enabling scalable real-time signal processing in large MU-MIMO systems," in Proc. ACM SIGCOMM, 2013, pp. 399-410. [Online]. Available: https://www.microsoft.com/en-us/research/publication/bigstation-enabling-scalable-real-time-signal-processing-in-large-mu-mimo-systems/
[10] J. V. Alegría and F. Rusek, "Achievable rate with correlated hardware impairments in large intelligent surfaces," in Proc. IEEE 8th Int. Workshop Comput. Adv. Multi-Sensor Adaptive Process., 2019, pp. 559-563.
[11] H. Q. Ngo, A. Ashikhmin, H. Yang, E. G. Larsson, and T. L. Marzetta, "Cell-free massive MIMO versus small cells," IEEE Trans. Wireless Commun., vol. 16, no. 3, pp. 1834-1850, Mar. 2017.
[12] E. Björnson and L. Sanguinetti, "Scalable cell-free massive MIMO systems," IEEE Trans. Commun., vol. 68, no. 7, pp. 4247-4261, Jul. 2020.
[13] J. Zhang, E. Björnson, M. Matthaiou, D. W. K. Ng, H. Yang, and D. J. Love, "Prospective multiple antenna technologies for beyond 5G," IEEE J. Sel. Areas Commun., vol. 38, no. 8, pp. 1637-1660, Aug. 2020.
[14] Q. Wu and R. Zhang, "Intelligent reflecting surface enhanced wireless network via joint active and passive beamforming," IEEE Trans. Wireless Соттип., vol. 18, no. 11, pp. 5394-5409, Nov. 2019.
[15] J. Chen, Y. C. Liang, Y. Pei, and H. Guo, "Intelligent reflecting surface: A programmable wireless environment for physical layer security," IEEE Access, vol. 7, pp. 82599-82612, 2019.
[16] K. Li, R. R. Sharan, Y. Chen, T. Goldstein, J. R. Cavallaro, and C. Studer, "Decentralized baseband processing for massive MU-MIMO systems," IEEE Trans. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491-507, Dec. 2017.
[17] E. Bertilsson, O. Gustafsson, and E. G. Larsson, "A scalable architecture for massive MIMO base stations using distributed processing," in Proc. 50th Asilomar Conf. Signals, Syst. Comput., 2016, pp. 864-868.
[18] K. Li et al., "Design trade-offs for decentralized baseband processing in massive MU-MIMO systems," in Proc. 53rd Asilomar Conf. Signals, Syst., Comput., 2019, pp. 906-912.
[19] J. R. Sánchez, J. Vidal Alegría, and F. Rusek, "Decentralized massive MIMO systems: Is there anything to be discussed?," in Proc. IEEE Int. Symp. Inf. Theory, 2019, pp. 787-791.
[20] M. Sarajlic, F. Rusek, J. R. Sanchez, L. Liu, and O. Edfors, "Fully decentralized approximate zero-forcing precoding for massive MIMO systems," IEEE Wireless Commun. Lett., vol. 8, no. 3, pp. 773-776, Jun. 2019.
[21] J. R. Sanchez, F. Rusek, M. Sarajlic, O. Edfors, and L. Liu, "Fully decentralized massive MIMO detection based on recursive methods," in Proc. IEEE Int. Workshop Signal Process. Syst., 2018, pp. 53-58.
[22] J. Vidal Alegría, J. R. Sánchez, F. Rusek, L. Liu, and O. Edfors, "Decentralized equalizer construction for large intelligent surfaces," in Proc. IEEE 90th Veh. Technol. Conf., 2019, pp. 1-6.
[23] Z. Zhang, H. Li, Y. Dong, X. Wang, and X. Dai, "Decentralized signal detection via expectation propagation algorithm for uplink massive MIMO systems," IEEE Trans. Veh. Technol., vol. 69, no. 10, pp. 11233-11240, 2020.
[24] A. Amiri, S. Rezaie, C. N. Manchon, and E. de Carvalho, "Distributed receivers for extra-large scale MIMO arrays: A message passing approach," 2020, arXiv:2007.06930.
[25] T. M. Cover and J. A. Thomas, Elements of Information Theory (Wiley Series in Telecommunications and Signal Processing). Hoboken, New Jersey: John Wiley \& Sons, Inc., 2006.
[26] A. Paulraj, R. Nabar, and D. Gore, Introduction to Space-Time Wireless Communications. 1st ed., New York, NY, USA: Cambridge Univ. Press, 2008.
[27] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, "Decentralized equalization with feedforward architectures for massive MU-MIMO," IEEE Trans. Signal Process., vol. 67, no. 17, pp. 4418-4432, Sep. 2019.
![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-15.jpg?height=316&width=257&top_left_y=232&top_left_x=128)

Juan Vidal Alegría (Student Member, IEEE) was born in Bilbao, Spain, in 1994. He received the B.Sc. and M.Sc. degrees in telecommunications engineering from the Technical University of Madrid, Madrid, Spain, in 2016 and 2018, respectively, and the M.Sc. degree in wireless communications from Lund University, Lund University, in 2018. He is currently working toward the Ph.D. degree with the Department of Electrical and Information Technology, Lund University. His main research interests include wireless communications, signal processing, applied information theory, and beyond massive MIMO.
![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-15.jpg?height=321&width=263&top_left_y=820&top_left_x=124)

Fredrik Rusek received the M.Sc. and Ph.D. degrees from Lund University, Lund, Sweden, in 2003 and 2007, respectively. Since 2007, he has been with the Department of Electrical and Information Technology with Lund University, where he is currently an Associate Professor. During 2011-2014, he held a part time position as an Algorithm Expert with Huawei, Lund, Sweden. Since 2018 and onwards, he holds a part time researcher position with Sony.
![](https://cdn.mathpix.com/cropped/000de3cf-47d1-4248-b974-bed670847363-15.jpg?height=326&width=261&top_left_y=227&top_left_x=1039)

Ove Edfors (Senior Member, IEEE) was born in Örnsköldsvik, Sweden, in 1966. He received the M.Sc. degree in computer science and electrical engineering and the Ph.D. degree in signal processing from the Luleå University of Technology, Luleå, Sweden, in 1990 and 1996, respectively. In the spring of 1997, he was a Researcher with the Division of Signal Processing at the same university and in July 1997, he joined the staff with the Department of Electrical and Information Technology, Lund University, Lund, Sweden, where he is currently a Professor of radio systems. His research interests include radio systems, statistical signal processing, and low-complexity algorithms with applications in telecommunication.


[^0]:    Manuscript received October 23, 2020; revised March 25, 2021 and May 28, 2021; accepted May 31, 2021. Date of publication June 15, 2021; date of current version June 30, 2021. The associate editor coordinating the review of this manuscript and approving it for publication was Prof. Luca Venturino. This paper is built upon previous results presented at the 2020 IEEE ICC conference [1]. This work has been funded by the Swedish Research Council. (Corresponding author: Juan Vidal Alegria.)

    The authors are with the Department of Electrical and Information Technology, Lund University, 22100 Lund, Sweden (e-mail: juan.vidal_alegria@eit.lth.se; fredrik.rusek @eit.lth.se; ove.edfors@eit.lth.se).

    Digital Object Identifier 10.1109/TSP.2021.3089442

[^1]:    ${ }^{1}$ Antenna panel refers to a group of co-located antennas.

[^2]:    ${ }^{2}$ In case of non-reciprocity, the presented framework would still be valid as long as the BS has access to the downlink channel matrix.

[^3]:    ${ }^{3}$ Note that, in the general case where $N \neq L$, selecting $\boldsymbol{A}$ as in Lemma 2 maintains the overall sparsity properties of $\widetilde{\boldsymbol{A}}$ since the transformation $\boldsymbol{T}_{L, N}$ just replicates the matrix $\widetilde{\boldsymbol{A}}$ in different positions, filling the rest with 0 s .

[^4]:    ${ }^{4}$ Note that, when applying $\boldsymbol{W}=\hat{\boldsymbol{W}}^{-1}$, the multiplication associated to (2) will cancel out any common scaling of $\hat{\boldsymbol{W}}$ and $\boldsymbol{X}$.

[^5]:    ${ }^{5} L_{\text {opt }}$ can be obtained from Theorem 1 as a converse of $T_{\text {opt }}$.

