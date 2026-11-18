# Efficient LMMSE Equalization for Massive MIMO Systems Under Decentralized Baseband Processing Architecture



# Page 1

736 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
Efficient LMMSE Equalization for Massive MIMO
Systems Under Decentralized Baseband
Processing Architecture
Xiaotong Zhao
 , Mian Li
 , Bo Wang
 , Enbin Song
 , Tsung-Hui Chang
 ,Fellow, IEEE ,
and Qingjiang Shi
 ,Member, IEEE
Abstract — Recently, the decentralized baseband processing
(DBP) paradigm and relevant uplink detection methods have been
proposed to enable extremely large-scale massive multiple-input
multiple-output technology. Under the DBP architecture, base
station antennas are divided into several independent clusters,
each connected to a local computing fabric. However, current
detection methods tailored to DBP only consider ideal white
Gaussian noise scenarios, while in practice, the noise is often col-
ored due to interference from neighboring cells. Moreover, in the
DBP architecture, linear minimum mean-square error (LMMSE)
detection methods require the knowledge of noise covariance
matrix which must be estimated using distributedly stored noise
samples. This presents a significant challenge for decentralized
LMMSE-based equalizer design. To address this issue, this paper
proposes decentralized LMMSE equalization methods under
colored noise scenarios for both star and daisy chain DBP
architectures. Specifically, we first propose two decentralized
equalizers for the star DBP architecture based on dimensionality
reduction techniques. Then, we derive an optimal decentralized
equalizer using the block coordinate descent method for the daisy
chain DBP architecture with a bandwidth reduction enhancement
scheme based on decentralized low-rank decomposition. Finally,
simulation results demonstrate that our proposed methods can
achieve excellent detection performance while requiring much
less communication bandwidth.
Received 3 March 2024; revised 13 August 2024; accepted 7 November
2024. Date of publication 4 February 2025; date of current version 27 February
2025. The work of Qingjiang Shi was supported by the NSFC under Grant
62231019 and Grant U23B2005. The work of Enbin Song was supported
by the NSFC under Grant U2066203. The work of Tsung-Hui Chang was
supported in part by Shenzhen Science and Technology Program under Grant
RCJC20210609104448114 and Grant ZDSYS20230626091302006, in part
by the NSFC under Grant 62071409, and in part by Guangdong Provincial
Key Laboratory of Big Data Computing. An earlier version of this paper
was presented in part at the IEEE Global Communications Conference
(GLOBECOM), Madrid, Spain, December 2021 [DOI: 10.1109/GLOBE-
COM46510.2021.9685271]. (Corresponding author: Qingjiang Shi.)
Xiaotong Zhao is with the School of Computer Science and Technol-
ogy, Tongji University, Shanghai 201804, China (e-mail: xiaotongzhao@
tongji.edu.cn).
Mian Li and Tsung-Hui Chang are with the School of Science and
Engineering, The Chinese University of Hong Kong Shenzhen (CUHK-SZ),
Shenzhen 518172, China, and also with Shenzhen Research Institute of
Big Data, Shenzhen 518172, China (e-mail: mianli1@link.cuhk.edu.cn;
tsunghui.chang@ieee.org).
Bo Wang is with the Wireless Network RAN Algorithm Department,
Xi’an Huawei Technologies Company Ltd., Xi’an 710000, China (e-mail:
wangbo169@huawei.com).
Enbin Song is with the College of Mathematics, Sichuan University,
Chengdu 610065, China (e-mail: e.b.song@163.com).
Qingjiang Shi is with the School of Computer Science and Technology,
Tongji University, Shanghai 201804, China, and also with Shenzhen Research
Institute of Big Data, Shenzhen 518172, China (e-mail: shiqj@tongji.edu.cn).
Digital Object Identifier 10.1109/JSAC.2025.3531524Index Terms— Massive MIMO, decentralized baseband pro-
cessing, data detection, LMMSE, colored noise.
I. I NTRODUCTION
MASSIVE
multiple-input multiple-output (MIMO) is a
critical technology for both fifth-generation (5G) and
sixth-generation systems due to its high spectral and power
efficiency [2], [3], [4]. With extremely large-scale antenna
arrays comprising hundreds or even thousands of antennas,
a base station (BS) is capable of simultaneously serving mul-
tiple user equipments (UEs) within the same time-frequency
resource. Data detection techniques are crucial in the uplink
of massive MIMO systems. While the optimal detector is
the nonlinear maximum-likelihood detector [5], its complexity
grows exponentially with the number of transmit antennas,
rendering it impractical for real-world systems. Consequently,
low-complexity linear equalization-based detection methods
such as maximum ratio combining (MRC), zero-forcing (ZF),
and linear minimum mean-square error (LMMSE) detectors
are preferred. Among these methods, the LMMSE detector
is widely adopted due to its near-optimal detection perfor-
mance [5].
Conventional LMMSE detection in practical massive MIMO
systems relies on centralized baseband processing (CBP)
in a single computing fabric, as shown in Fig. 1. How-
ever, extremely large antenna array in the next generation
wireless systems poses two major challenges: 1) Excessive
communication bandwidth: The rapid growth in the number
of BS antennas results in an exceedingly high amount of
raw baseband data, including channel state information (CSI),
received signal, and noise samples (for noise covariance esti-
mation), that must be transferred between the radio-frequency
(RF) chains and the centralized computing fabric shown in
Fig. 1with red arrow lines [6], [7]. This issue is evident
in a 256-antenna BS with an 80MHz bandwidth and 12-bit
digital-to-analog converters, where the raw baseband data
throughput reaches 1Tbps, greatly exceeding the existing
capacity of BS internal interface standards [8].2) High compu-
tational complexity: Traditional LMMSE equalization requires
a high-dimensional matrix inversion with a complexity cubic
in the number of BS antennas. This results in a formidable
requirement for computation capability, making the CBP archi-
tecture impractical for massive MIMO settings [6].
1558-0008 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 2

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 737
Fig. 1. Block diagram of a centralized baseband processing architecture for
the massive MU-MIMO uplink. “CHEST” is short for channel estimation.
To address the limitations of traditional CBP architectures,
recent studies have explored a promising next-generation
transceiver architecture called decentralized baseband process-
ing(DBP) [6], [7], [9],[10], [11], [12], [13], [14], [15], [16],
[17], [18], [19], [20]. As shown in Fig. 2, DBP replaces the
centralized computing fabric with multiple local computing
fabrics called distributed units (DUs). Additionally, the BS
antennas are divided into several independent clusters, each
connected to a DU. The DUs communicate with each other
through a topology such as a star or a daisy chain, as shown in
Fig.2(a)and(b), respectively. As a result, each DU stores local
information like CSI, received signals, and noise/interference
samples. This setup enables decentralized data detection with
moderate information exchange among DUs. Compared to
CBP, the DBP paradigm effectively mitigates bandwidth and
computation bottlenecks.
Numerous studies have investigated detection and equaliza-
tion designs in DBP architectures. To simplify the complicated
matrix inversion in centralized ZF and LMMSE equalizers,
decentralized iterative methods were proposed. These meth-
ods, such as conjugate gradient [6], alternating direction
method of multipliers [6], coordinate descent [10], and Newton
methods [17], combined the local matched filter, local Gram
matrix, and intermediate variables in a decentralized manner.
Maximum a posterior estimation-based decentralized detec-
tion algorithms, such as large-MIMO approximate message
passing [11], expectation propagation [12], [13], and Gaussian
message passing [16], were proposed to attain higher detec-
tion performance at the expense of increased computational
complexity. Notably, all the aforementioned methods aimed
to estimate symbols rather than obtain an equalization matrix
directly. However, equalization methods have a significant
advantage over symbol estimation methods: the equalization
matrix can be reused across multiple coherence blocks of
channels. In contrast, the symbol estimation algorithms men-
tioned above must be performed for each channel, resulting
in high computational complexity and communication band-
width. Given this consideration, the authors in [9]presented
a decentralized implementation that directly obtained MRC,
ZF, and LMMSE equalization matrices in a feedforward DBP
architecture. Meanwhile, a decentralized algorithm based on
gradient descent was proposed in [7]to obtain the ZF equal-
ization matrix for a daisy chain architecture. Recently, [18]
proposed a parallel iterative MMSE equalizer in a decentral-
ized bidirectional-chain equalizer architecture.
Prior works [6],[7],[9],[10], [11], [12], [13], [14], [15],
[16], [17], [18], and [19] all assumed that the BS receiver noisefollows an ideal additive white Gaussian noise (AWGN) model
with a diagonal covariance matrix. This naturally facilitates the
distributed implementation of LMMSE equalization in DBP
architectures using multiple diagonal submatrices. However,
in practical systems, interference from other non-target UEs
in neighboring cells must be modeled as part of the back-
ground noise [21], [22], i.e., results in colored noise with a
non-diagonal covariance matrix.1Moreover, the exact noise
covariance matrix at the BS is unknown and needs to be
estimated by averaging a finite number of noise samples.
In DBP architectures (see Fig. 2below), each DU has only
local noise samples for the corresponding antenna cluster.
Consequently, computing the non-diagonal covariance matrix
of colored noise requires collecting noise samples from all
clusters. However, this is hampered by prohibitively high com-
munication bandwidth and computational complexity, as the
sample dimension is related to the number of BS antennas
(which can be extremely large). Therefore, LMMSE equaliza-
tion in DBP architectures under the colored noise remains a
significant challenge, necessitating a completely new algorith-
mic design that considers limited communication bandwidth
and low computational complexity. This paper seeks to address
this challenge.
In summary, our main contributions are given as follows:
•Colored Noise and Covariance Estimation in DBP.
To the best of our knowledge, all the existing detection
methods designed for DBP focus solely on ideal white
Gaussian noise scenarios. We here for the first time con-
sider the more practical colored noise case. Particularly,
for the DBP architectures, we show how to efficiently
and implicitly implement decentralized estimation of the
noise covariance matrix during the LMMSE process
through averaging distributedly stored noise samples.
•Decentralized Equalization for the Star DBP Archi-
tecture. By investigating the closed-form expression for
the LMMSE equalization matrix, we propose two decen-
tralized equalizers that employ dimensionality reduction
(DR) techniques under the star DBP architecture. In both
methods, each DU embeds its local information into a
low-dimensional representation via linear transformation
and transmits it to the CU. The CU then either super-
imposes orconcatenates the compressed data to perform
LMMSE equalization. Both methods reduce data transfer
size from the number of BS antennas to the number of
UEs, alleviating the bandwidth and computation bottle-
necks, while achieving performance close to centralized
LMMSE equalization.
•Decentralized Equalization for the Daisy Chain DBP
Architecture. To obtain an optimal decentralized equal-
izer, we reshape the original optimization problem of
LMMSE and investigate the distributed storage structure
in the daisy chain DBP architecture. Then, we design an
efficient decentralized iterative algorithm using the block
coordinate descent (BCD) method [25] with guaranteed
convergence. During the BCD iteration, data transfer
1Practically, channel estimation errors can also be modeled as a specific
form of colored background noise [23], [24]. Note that our proposed decen-
tralized methods apply to all colored noise scenarios.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 3

738 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
size is significantly reduced, depending only on the
number of UEs rather than BS antennas. To further
reduce the data transfer size for the case when the
number of noise samples is very large, we present an
improved BCD-based decentralized LMMSE equalizer
by deliberately using a low-rank approximation of the
noise covariance matrix. While preserving near-optimal
performance, this approach requires the data transfer size
independent of the number of noise samples, significantly
reducing the bandwidth and computation burden.
The remainder of this paper is organized as follows.
Section II introduces the uplink system model and the DBP
architectures. Section III proposes two decentralized equaliza-
tion methods using DR techniques for the star architecture.
Section IV develops a BCD-based decentralized equalization
method for the daisy chain architecture and a low-rank decom-
position scheme for noise covariance matrix to further reduce
the communication bandwidth. Section Vpresents computa-
tional complexity and communication bandwidth analysis. The
simulation results are provided in Section VI. Finally, this
article is concluded in Section VII.
Notations: Throughout this paper, scalars are denoted by
both lower and upper case letters, while vectors and matrices
are denoted by boldface lower case and boldface upper case
letters, respectively. For a matrix A,AT,AH,A−1, Tr(A)
andR(A) denote its transpose, conjugate transpose, inverse,
trace, and range space, respectively. The Euclidean norm of
a vector xis defined as∥x∥2=√
xHx. In addition, E[·]
denotes the expectation operation. The notation Iis the identity
matrix, and blkdiag(A 1, . . . ,AC)denotes a block diagonal
matrix with A1, . . . ,ACbeing its diagonal blocks.
II. S YSTEMS MODEL AND DBP A RCHITECTURES
This section introduces the uplink massive MIMO system
model and the LMMSE equalization method. Two uplink DBP
architectures are then presented along with the challenges
posed by the decentralized LMMSE design.
A. Uplink System Model and LMMSE Equalization
1) Uplink System Model: Consider an uplink massive
MIMO system where Ktarget UEs, each with a single
antenna, transmit data to a BS equipped with Mantennas,
where M≫K. The received signal y∈CM×1at the BS is
expressed as:
y=Hs+n, (1)
where H∈CM×Krepresents the channel matrix between the
BS and UEs, s∈SK×1denotes the transmitted symbol vector
withSrepresenting the constellation set for some modulation
scheme (e.g., 16-QAM), and n∼ CN (0,R)denotes the
additional white Gaussian noise (AWGN) with R≜E
nnH
being the covariance matrix.
2) LMMSE Equalization: Typically, the CSI is considered
almost constant across several contiguous symbols [15], which
enables the reuse of the equalization matrix. Consequently,
it is more cost-effective to compute the equalization matrix
and reuse it, rather than estimating symbols directly for eachinstance. Therefore, we focus on obtaining an equalization
matrix instead of directly estimating symbols.
Assuming the channel matrix His perfectly known,2
LMMSE equalization aims to find a linear estimate by solving
the following problem:
min
WEh
∥Wy−s∥2
2i
, (2)
which leads to the well-known LMMSE receiver [28]:
WMMSE =
HHR−1H+1
EsI−1
HHR−1, (3)
where Esdenotes the average energy per symbol. The
LMMSE estimate ˆsMMSE is obtained by applying the equal-
ization matrix WMMSE to the received signal y, i.e., ˆsMMSE =
WMMSEy. Finally, the detector quantizes each entry of ˆsMMSE
to the nearest neighbor point in the constellation set S.
In conventional centralized LMMSE equalization, comput-
ing the equalization matrix in (3)requires complete knowledge
ofH∈CM×KandR∈CM×M, which must be collected
from the RF chains to a centralized computing fabric. Further-
more, the M-dimensional matrix inversion operation R−1in
(3)results in a computational complexity of O(M3). Conse-
quently, centralized processing imposes significant bandwidth
and computational demands that are unaffordable when M
is extremely large in massive MIMO settings. This motivates
the decentralized design of the LMMSE equalization under
certain decentralized baseband processing architecture, which
is introduced in the sequel.
B. Decentralized Baseband Processing: Architectures,
Challenges, and A Baseline Solution
1) DBP Architectures: To address the complexity and band-
width issues of traditional CBP architectures, recent studies
(e.g., [6],[7]) have explored the DBP architecture. As illus-
trated in Fig. 2, the uplink DBP architecture divides M
BS antenna elements into Cantenna clusters each with Mc
antennas (i.e.,PC
c=1Mc=M). In particular, each cluster has
its own local RF and computing fabric called DU.
In this paper, we consider two DBP architectures: the star
architecture in Fig. 2(a) and the daisy chain architecture in
Fig. 2(b). In the star architecture, all DUs are connected to a
central unit (CU), and each DU performs data compression and
subsequently transmits some message (i.e., intermediate results
as required) to the CU in parallel for the final equalization
operation. In contrast to the star architecture, there is no CU
in the daisy chain architecture. Instead, the DUs are connected
via unidirectional links, while an additional link connects the
last and first DUs to form a ring. Only one DU outputs the
symbol estimate and is directly linked to the decoder.
The star architecture requires a higher communication band-
width between the CU and DUs, resulting in complex chip
2Decentralized channel estimation is also a crucial problem for DBP imple-
mentation. Several papers have focused on this topic, such as [26]. However,
in our paper, we suppose that the decentralized channel estimation has
been already accomplished and focus on decentralized detection/equalization
design.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 4

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 739
Fig. 2. The DBP architectures in which the received signal yand each noise sample niare both distributed over multiple DUs.
input/output interfaces at the CU. Nevertheless, the star archi-
tecture has less latency than the daisy chain architecture since
the star architecture enables parallel processing. In contrast,
the interface design in the daisy chain architecture is simple,
low-cost, and easier to extend but often has higher latency.
Under the DBP architectures, the received vector, channel
matrix, and noise vector in Eq. (1)are accordingly partitioned
asy= [yT
1,yT
2, . . . ,yT
C]T,H= [HT
1,HT
2, . . . ,HT
C]T, and
n= [nT
1,nT
2, . . . ,nT
C]T, respectively. Therefore, the local
received signal yc∈CMc×1at cluster cis represented by
yc=Hcs+nc, c = 1,2, . . . , C, (4)
where Hc∈CMc×Kandnc∈CMc×1denote the local
channel matrix and the local noise vector with respect to
cluster c, respectively. Note that, Hcandycare only known
locally to the DU cand are not allowed to be directly
exchanged among DUs to save bandwidth overhead.
2) Challenges Imposed by DBP on Decentralized LMMSE:
Previous works on decentralized equalization under DBP
architectures all assumed AWGN noise with diagonal covari-
ance matrix [6],[7],[9],[10], [11], [12], [13], [14], [15], [16],
[17]. Under such an assumption, the noise covariance matrix
can be naturally decomposed into multiple block diagonal
submatrices that perfectly fit into the decentralized imple-
mentation of LMMSE equalization under DBP architectures.3
However, the noise at the BS is often colored due to the
existence of interference signals from non-target UEs in neigh-
boring cells [21], [22]. In interference scenarios, the baseband
model in (1)can be expressed in more detail as follows:
y=Hs+ n|{z}
colored noise=Hs+ ¯H¯s|{z}
interference+¯n|{z}
AWGN, (5)
3Note that the LMMSE receiver in Eq. (3)would degenerate into
HHH+σ2
0
EsI−1
HH, where σ2
0is the noise power of the AWGN.
In this case, HHHcan be computed asPC
c=1HH
cHcby aggregating
the low-dimensional local information from each DU. Subsequently, the
low-dimensional inversion result can be broadcast to each DU for local
equalizer computation.where ¯H∈CM×rand¯s∈ Sr×1respectively denote the
channel matrix and interference signals of rnon-target UEs,
and¯n∈CM×1is the background AWGN with distribution
CN 
0, σ2I
. Then, the colored noise covariance matrix R=
β¯H¯HH+σ2I, where βis the power of interference signals.
In this scenario, Rbecomes non-block-diagonal. Moreover,
the decentralized estimation of Ris not possible because
directly exchanging interference signals among DUs is for-
bidden due to bandwidth limitation. This imposes a huge
challenge for decentralized LMMSE equalization design.
To better understand the challenge mentioned above,
we write down the best estimation4ofRas[21], [22],
and[29]:
ˆR=1
NNX
i=1ni(ni)H, (6)
which is done by averaging the noise samples in Npilot
resource elements (REs). Here, N≫Kholds to ensure the
accuracy of estimation, and ni∈CM×1is the noise sample
in the i-th pilot RE.5
Corresponding to the antennas clustering in DBP archi-
tectures, the i-th noise sample nican be divided as ni=
[(ni
1)T,(ni
2)T, . . . , (ni
C)T]T,∀i, where{ni
c}N
i=1are stored in
cluster c(illustrated with orange color in Fig. 3). Similarly,
the noise covariance matrix Rcan be regarded as a block
matrix with C×Cblocks, where the (m, n)-th block submatrix
is denoted by Rmn=E
nmnH
n
. Accurate estimation of R
is crucial for effective LMMSE equalization. However, only
the diagonal blocks of R(denoted by ˆRccas illustrated in
yellow in Fig. 3) can be locally estimated by each clus-
tercusing ˆRcc=(1/N )PN
i=1ni
c(ni
c)H. The main challenge
lies in accurately obtaining the off-diagonal blocks of R
(i.e.,Rmn, m̸=n illustrated in blue in Fig. 3). Note that the
4The noise covariance has been shown to stay constant over a wide fre-
quency interval [29], and thus can be estimated via averaging over frequency
in practical wideband systems.
5Although ˆRis an approximate estimate of R, in practice, the estimation
error is small when Nis large. More importantly, we can only obtain the
estimation ˆRrather than statistical covariance R. Therefore, for simplicity of
notation, we make no distinction between ˆRandRin the rest of this paper.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 5

740 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
Fig. 3. An illustrative example of the colored noise assumption in a DBP
architecture with C= 4 . The computation of off-diagonal blocks of R
requires data transfer among DUs.
direct exchange of noise samples among DUs would result
in high-dimensional data transfer with size M×N, which is
prohibited for massive MIMO scenarios. Moreover, traditional
whitening noise methods cannot be applied because they
don’t allow distributed implementation in DBP. As a result,
decentralized computation of the LMMSE equalization matrix
in (3) under stringent bandwidth constraints poses a significant
challenge.
3) A Baseline Solution: We first propose a straightforward
solution to roughly tackle this challenge, i.e., approximat-
ingRwith a block diagonal matrix, denoted by RB≜
blkdiag (R11,R22, . . . ,RCC), where all off-diagonal blocks
are set to zero. Here, blkdiag(A 1, . . . ,AC)denotes a block
diagonal matrix with A1, . . . ,ACbeing its diagonal blocks.
This approach enables the approximation of the LMMSE
equalization matrix in (3)as

HHR−1
BH+1
EsI−1
HHR−1
B
= CX
c=1HH
cR−1
ccHc+1
EsI!−1
HH
1R−1
11, . . .,HH
CR−1
CC
.(7)
It is possible to implement (7) in a decentralized man-
ner. Specifically, each DU c= 1, 2, . . . , C first computes
HH
cR−1
ccHclocally, which is then collected together for sum-
mation and inversion operations. Finally, the matrix inverse
result is broadcasted to all DUs, allowing them to compute
their local equalization matrices. This decentralized imple-
mentation of obtaining the approximate equalization matrix
in (7) is called the block diagonal approximate covari-
ance MMSE (BDAC-MMSE) equalizer. The transfer of only
low-dimensional matrices with size K×Krequires minimal
communication bandwidth. Note that this simple approxima-
tion leads to a performance loss in colored noise scenarios.
Therefore, algorithms with better performance will be pro-
posed in the following sections. Nevertheless, BDAC-MMSE
can serve as a good initial point for our proposed decentralized
BCD-based equalizers in Section IV, as well as a baseline
algorithm.
Remark 1: : Recent works [23], [24] have investigated the
design of MMSE receivers for cell-free massive MIMO sys-
tems under colored noise conditions, where geographically
separated access points (APs) jointly receive signals from
all mobile users. In this scenario, the APs can be seen as
the DU in the DBP architecture. However, their problem
formulations differ significantly from ours. Specifically, theyconsidered colored noise caused by channel estimation error
and employed a Kalman filtering-based method to provide a
sequential implementation of centralized LMMSE using local
noise covariance matrices. However, they assumed that the
noise covariance matrix is a block diagonal matrix comprising
multiple local covariance matrices, with each decentralized
node having knowledge of its corresponding local covariance
matrix. Consequently, the algorithms proposed in [23] and[24]
for colored noise with block-diagonal covariance matrix are
not suitable for our decentralized LMMSE equalization prob-
lem with more general noise covariance matrix.
III. D IMENSIONALITY REDUCTION MMSE
EQUALIZATION FOR STAR
DBP A RCHITECTURE
This section introduces the DR technique for the star DBP
architecture and formulates the LMMSE problem under two
types of compression matrices. Then, two DR-based decen-
tralized equalization methods are designed.
A. Dimensionality Reduction in DBP
To reduce the bandwidth burden in DBP architectures,
a straightforward idea is to reduce the dimension of local
information while preserving equalization performance, which
matches the concept of the DR technique [30], [31]. Specif-
ically, in the star DBP architecture, through a fat local
compression matrix Qc∈CLc×Mc, where Lc< M c, each DU
parallelly transfers the compressed local received vector Qcyc,
channel matrix QcHc, and noise samples {Qcni
c}N
i=1to the
CU. Based on these compressed data, an LMMSE estimate of s
is formed through an equalization matrix W. Since Lc< M c,
the bandwidth can be significantly reduced. We assume local
compression dimension Lc=Lfor brevity.
The compression matrix can be an arbitrary fat matrix. For
the star DBP architecture, we focus on the following two
scenarios of compression matrices:
1)Superimposed Compression: The compressed received
signals from each DU are superimposed at the CU as
˜y(Q1, . . . ,QC) =CX
c=1Qcyc= [Q1, . . . ,QC]y.(8)
2)Concatenated Compression: The CU concatenates the
compressed data of individual DUs to form a vector
˜y(Q1, . . . ,QC) =blkdiag(Q 1, . . . ,QC)y.(9)
The dimension of ˜y(Q1, . . . ,QC)in the superimposed and
concatenated scenarios are L×1andCL×1, respectively.
[Q1, . . . ,QC]and blkdiag(Q 1, . . . ,QC)are global compres-
sion matrices. For both scenarios, we aim to design MSE
optimal equalization matrices ˜Wand local compression matri-
ces{Qc}C
c=1as follows:
min
˜W,{Qc}C
c=1Es−˜W˜y(Q1, . . . ,QC)2
2
, (10)
where ˜y(Q1, . . . ,QC)is given by either (8)or(9). In general,
concatenating has a better performance but with higher com-
plexity compared to superimposing. Although many articles
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 6

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 741
have investigated problem (10), they all assumed that the
statistical properties of the signal and noise are available at a
central node [30], [31]. However, the biggest challenge in this
paper is that the non-diagonal noise covariance matrix can only
be estimated by the noise samples, which are separately stored
at each DU. Thus, the global optimization methods in [31]
for problem (10) will inevitably lead to a heavy bandwidth
burden. Consequently, we need to reconsider the problem (10)
and find a reasonable approximate solution with the trade-off
between bandwidth and performance. Since the optimal ˜W
in problem (10) is obviously given by the LMMSE solution
after{Qc}C
c=1are obtained, we will focus on the design of
compression matrices {Qc}C
c=1.
A fundamental question is, under what conditions the
compression is lossless? Here, lossless means no MSE perfor-
mance gap exists between performing LMMSE equalization
with compressed and uncompressed information. The follow-
ing theorem answers this question:
Theorem 1: : Consider system model (1), i.e., y=Hs+n.
Denote Q∈CL×Mas the global compression matrix. The
minimal compression dimension without performance loss is
rank(H) = K, andQ=PHHR−1∈CK×Mfor an arbitrary
invertible matrix P∈CK×Kis a lossless compression matrix.
Proof: See Appendix A.
Following Theorem 1, setting P=Iresults in a lossless
compression matrix HHR−1∈CK×M. However, this cannot
be utilized directly for the DBP architectures because R−1is
unavailable without collecting {ni
c}N
i=1from each DU to the
CU, which is infeasible due to bandwidth limitations. There-
fore, we use a lossy compromise by using Qc=HH
cR−1
cc∈
CK×Mcas a local compression matrix at each DU c. The
following subsections show that it will be a lossless local com-
pression matrix when R=RB, and simulation results confirm
its effectiveness. The subsequent two subsections derive the
compression matrices and corresponding equalization methods
for different scenarios.
B. Superimposed DR-MMSE Equalization
We first consider the superimposed scenario. Adopting
Qc=HH
cR−1
ccas the local compression matrix at DU c,
the global superimposed compression matrix is given by
ˇQ= [Q1,Q2, . . . ,QC]
= [HH
1R−1
11,HH
2R−1
22, . . . ,HH
CR−1
CC]
=HHR−1
B, (11)
which is an approximation to the lossless compression matrix
HHR−1. Applying the compression to (1), we obtain the
effective compressed channel model at the CU as
ˇy=ˇHs+ˇn, (12)
where
ˇy=ˇQy=CX
c=1Qcyc,ˇH=ˇQH=CX
c=1QcHc, (13a)
ˇn=ˇQn=CX
c=1Qcnc. (13b)Algorithm 1 The Proposed sDR-MMSE Equalization
Input: yc,Hc,{ni
c}N
i=1, c= 1,2, . . . , C , and Es.
1:Decentralized preprocessing at each DU:
2:forc= 1 toCdo
3:Qc←HH
cR−1
cc;
4: Compute Qcyc,QcHc, and{Qcni
c}N
i=1; //Send to CU
5:end for
6:Central processing at the CU:
7:Compute ˇyandˇHvia (13);
8:Compute ˇRvia (14);
9:WsDR-MMSE is given by (15);
10:ˆssDR-MMSE is given by (16);
Output: WsDR-MMSE andˆssDR-MMSE .
The effective noise covariance matrix can be expressed by
ˇR=ˇQRˇQH=ˇQ 
1
NNX
i=1ni 
niH!
ˇQH
=CX
m=1CX
l=1 
Qm 
1
NNX
i=1ni
m 
ni
lH!
QH
l!
=1
NCX
m=1CX
l=1NX
i=1Qmni
m(Qlni
l)H. (14)
After the low-dimensional compressed information
Qcyc,QcHc, and{Qcni
c}N
i=1are collected from all the DUs,
the CU calculates the equalization matrix as follows:
WsDR-MMSE =
ˇHHˇR−1ˇH+1
EsI−1
ˇHHˇR−1, (15)
and the estimated symbol is given by
ˆssDR-MMSE =WsDR-MMSE ˇy. (16)
The proposed algorithm, named superimposed dimension-
ality reduction (sDR)-MMSE, is summarized in Algorithm 1.
In the preprocessing phase, Qcyc,QcHcand{Qcni
c}N
i=1are
calculated locally at each DU and then transmitted to the CU.
Later in the equalization phase, the compressed information
is superimposed to obtain the equalization matrix in (15).
Finally, multiplying the compressed received signal provides
the estimate of sin (16). Fig. 4illustrates the information
transfer in the proposed sDR-MMSE equalization. The data
transfer size is independent of the number of BS antennas.
Remark 2: Since HHR−1is a lossless compression matrix,
the sDR-MMSE equalization is equivalent to the centralized
LMMSE equalization when R=RB. Moreover, the perfor-
mance degradation caused by compression will be minor if the
off-diagonal elements of Rare relatively small compared to
the diagonal part. Fortunately, noise covariance matrix Roften
tends to block diagonally dominant in practical scenarios.
C. Concatenated DR-MMSE Equalization
The sDR-MMSE equalization results in information loss
due to the superimposition of information from each DU.
A potential approach to improve performance is to concatenate
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 7

742 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
Fig. 4. The communication and computation operations during the
sDR-MMSE equalization process.
compressed information instead of superimposing, although
this comes at the cost of increased complexity. Therefore,
we consider scenario 2) of the compression matrix in (9).
We still adopt the local compression matrix as Qc=
HH
cR−1
ccat the c-th DU. But different from (11), the global
concatenated compression matrix is given by
˜Q=blkdiag (Q1,Q2, . . . ,QC)
=blkdiag 
HH
1R−1
11,HH
2R−1
22, . . . ,HH
CR−1
CC
.(17)
Thus, the effective channel model at the CU is given by
˜y=˜Hs+˜n, (18)
where
˜y=
Q1y1
...
QCyC
,˜H=
Q1H1
...
QCHC
,˜n=
Q1n1
...
QCnC
.(19)
The effective noise covariance matrix can be expressed by
˜R=
Q1R11QH
1. . .Q1R1CQH
C.........
QCRC1QH
1. . .QCRCCQH
C
, (20)
where
QmRmlQH
l=Qm 
1
NNX
i=1ni
m 
ni
lH!
QH
l
=1
NNX
i=1Qmni
m 
Qlni
lH. (21)
Consequently, after collecting the compressed information
Qcyc,QcHc, and{Qcni
c}N
i=1 from all the DUs, the CU
calculates the equalization matrix as follows:
WcDR-MMSE =
˜HH˜R−1˜H+1
EsI−1
˜HH˜R−1, (22)
and the estimated symbol is given by
ˆscDR-MMSE =WcDR-MMSE ˜y. (23)
The resulting algorithm is called concatenated dimensional-
ity reduction (cDR)-MMSE equalization and is summarized
in Algorithm 2. The preprocessing stage of cDR-MMSE
equalization is the same as that of sDR-MMSE equalization,Algorithm 2 The Proposed cDR-MMSE Equalization
Input: yc,Hc,{ni
c}N
i=1, c= 1,2, . . . , C , and Es.
1:Decentralized preprocessing at each DU:
2:forc= 1 toCdo
3:Qc←HH
cR−1
cc;
4: Compute Qcyc,QcHc, and{Qcni
c}N
i=1; //Send to CU
5:end for
6:Central processing at the CU:
7:Compute ˜yand˜Hvia (19);
8:Compute ˜Rvia (20);
9:WcDR-MMSE is given by (22);
10:ˆscDR-MMSE is given by (23);
Output: WcDR-MMSE andˆscDR-MMSE .
i.e.,Qcyc,QcHcand{Qcni
c}N
i=1are calculated locally at
each DU and then sent to the CU. Whereas at the CU, the
compressed information is concatenated to obtain the LMMSE
equalization matrix in (22) instead of being superimposed.
The information transfer of the cDR-MMSE equalization is
identical to that of the sDR-MMSE equalization illustrated in
Fig. 4, except that the central processing at the CU should be
replaced by (22) and(23).
The cDR-MMSE equalizer outperforms the sDR-MMSE
equalizer due to the concatenation operation. Proposition 1
provides a rigorous analysis of this performance improvement.
However, the cDR-MMSE equalizer has a higher computa-
tional complexity due to the high-dimensional matrix inversion
˜R−1at the CU.
Proposition 1: : The MSE matrix EsDR⪰EcDR, where
EsDR≜E[(ˆssDR-MMSE−s) (ˆssDR-MMSE−s)H]andEcDR≜
E[(ˆscDR-MMSE−s) (ˆscDR-MMSE−s)H]. Moreover, we have
Eh
∥ˆssDR-MMSE−s∥2
2i
≥Eh
∥ˆscDR-MMSE−s∥2
2i
.
The proof is given in Appendix B. Here, A⪰0is a
generalized inequality meaning Ais a positive semidefinite
matrix. Proposition 1shows that the MSE of the cDR-MMSE
equalizer is no larger than that of the sDR-MMSE equalizer.
Remark 3 (Application in the Daisy Chain Architecture):
The sDR-MMSE equalizer still works in the daisy chain
architecture since the summation operation will not increase
bandwidth and computational complexity. However, the
sequential nature of the daisy chain architecture leads to
increased latency. In contrast, the cDR-MMSE equalizer
only works with the star architecture since the concatenation
operation increases the bandwidth sharply in the daisy
chain architecture due to the accumulation of information
dimensions.
IV. BCD-B ASED LMMSE E QUALIZATION FOR THE DAISY
CHAIN ARCHITECTURE
This section proposes an optimal BCD-based LMMSE
equalizer for the daisy chain architecture and improves it by
utilizing a decentralized low-rank decomposition method for
further bandwidth reduction.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 8

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 743
A. BCD-Based LMMSE Equalization
The DR-based LMMSE equalizers can be viewed as a
decentralized implementation of the closed-form expression
of the equalization matrix in (3). Although the sDR-MMSE
can be adapted for the daisy chain architecture, the DR-based
equalizers are only suboptimal solutions to the original
LMMSE problem (2). Therefore, we aim to design an optimal
decentralized equalizer for the daisy chain architecture by
reconsidering problem (2). Incorporating the baseband model
(1)and covariance estimation (6)into problem (2), and con-
sidering the independence of nands, we can reformulate
problem (2)equivalently as follows:
min
W1
NNX
i=1EhWHs +Wni−s2
2i
. (24)
The objective function of the above problem has only one
random variable s, and the other variables are deterministic.
It should be noted that niis stored separately at each DU. Thus
we deliberately partition the equalization matrix Winto block
matrix as W= [W 1,W2, . . . ,WC]withWc∈CK×Mc.
Then, problem (24) can be rewritten as
min
W1
NNX
i=1E"WcHcs+CX
j=1,j̸=cWjHjs
+Wcni
c+CX
j=1,j̸=cWjni
j−s2
2#
. (25)
We then use the BCD method [25] to optimize{Wc}C
c=1,
which is suitable for the decentralized daisy chain architecture.
Importantly, Wc∈CK×Mccan be seen as a dimensionality
reduction matrix that decreases the dimension of the interme-
diate variables. Specifically, the objective function in problem
(25) is minimized with respect to one block variable Wcwhile
fixing Wj, j̸=cforc= 1,2, . . . , C sequentially. The update
ofWcis given by the following proposition.
Proposition 2: : While fixing Wj, j̸=cin problem (25),
the optimal solution with respect to Wcin closed form is
given by as in (26), shown at the bottom of the page.
Proof: See Appendix C.
We observe thatP
j̸=cWjHjand{P
j̸=cWjni
j}N
i=1is
needed for computing W∗
c, and all the other terms in (26) can
be computed via local information at DU c. Therefore, based
on(26) and(27), we derive a BCD-based LMMSE equalizer
for the daisy chain architecture. Adopting the Gauss-Seidel
update rule [32], at the l-th iteration, the local equalization
matrix Wl
cis updated by solving the following subproblem:
Wl
c=arg min
Wcf 
Wl
1, . . . ,Wl
c−1,Wc,Wl−1
c+1, . . . ,Wl−1
C
,
(27)Algorithm 3 The Proposed BCD-MMSE Equalization
Input: yc,Hc,{ni
c}N
i=1, c= 1,2, . . . , C ,Es, and total itera-
tion number T.
1:Preprocessing:
2: Initialize W0using (7) in a decentralized manner;
3:A0
0←0;
4:b0
0,i←0, i= 1,2, . . . , N ;
5: forc= 1 toCdo
6: A0
0←A0
0+W0
cHc;
7: b0
0,i←b0
0,i+W0
cni
c, i= 1,2, . . . , N ;
8: end for
9:BCD iterations:
10: forl= 1 toTdo
11: forc= 1 toCdo
12: Update Wl
cvia (30);
13: Update Al
cvia (28);
14: Update bl
c,i, i= 1,2, . . . , N via (29);
15: end for
16: end for
17:Equalizer filter:
18: ˆsBCD-MMSE←0;
19: forc= 1 toCdo
20: ˆsBCD-MMSE←ˆsBCD-MMSE +Wcyc;
21: end for
Output: W= [W1,W2, . . . ,WC]andˆsBCD-MMSE .
where f(·)denotes the objective function of (25). Define Al
c∈
CK×Kand{bl
c,i∈CK×1}N
i=1as the interaction variables at
c-th DU and l-th iteration, which are updated recursively by
Al
c=Al
c−1−Wl−1
cHc+Wl
cHc, (28)
bl
c,i=bl−1
c,i−Wl−1
cni
c+Wl
cni
c, i= 1,2, . . . , N. (29)
These communication variables can be seen as the summa-
tion of the compressed local channel matrices and compressed
local noise samples, where the local equalization matrices
act as local compression matrices. The initialization of these
communication variables will be detailed in Algorithm 3.
Specifically, the c-th DU receives the communication variables
Al
c−1and{bl
c−1,i}N
i=1from the previous DU.6Then the local
equalization matrix Wl
cis updated by as in (30), shown at the
bottom of the next page. Except for the information received
from the previous DU, all other terms in (30) can be computed
locally. Finally, the c-th DU updates Al
candbl
c,iby(28) and
(29), respectively, and then transfers them to the next DU.
The BCD-based LMMSE equalization is summarized in
Algorithm 3, termed BCD-MMSE equalization. Theoretically,
the algorithm can be terminated if the objective function values
6Here, we assume the previous DU of the first DU is the C-th DU, i.e., Al
0
and{bl
0,i}N
i=1represent Al−1
Cand{bl−1
C,i}N
i=1, respectively.
W∗
c= 
Es
IK−CX
j=1,j̸=cWjHj
HH
c−1
NNX
i=1CX
j=1,j̸=cWjni
j(ni
c)H!
× 
EsHcHH
c+1
NNX
i=1ni
c(ni
c)H!−1
.(26)
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 9

744 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
Fig. 5. The communication and computation operations during the
BCD-MMSE equalization process.
at the two successive iterations are almost unchanged. In the
simulation part, only the first four iterations of the BCD
algorithms are considered due to bandwidth and computation
limitations in practice. Thus the number Tof iterations can
be chosen according to both the above two factors. Fig. 5(a)
shows the communication transfer in the iteration phase of
the proposed BCD-MMSE method, where the superscript
lis omitted for brevity. Fig. 5(b) shows the equalizer fil-
ter phase for estimating the transmitted symbol. Note that
Wl
c∈CK×Mccan be viewed as a dimensionality reduc-
tion matrix that reduces the dimension of Hc,ni
c, and yc
before transferring since K < M c. For example, to share the
covariance matrix information among DUs, the BCD-MMSE
equalization only requires exchanging bl
c,i∈CK×1among
DUs, which significantly reduces the bandwidth compared
to directly exchanging ni
c∈CMc×1. Therefore, the data
transfer size of the BCD-MMSE equalizer is independent of
the number of BS antennas.
Theorem 2 (Convergence Results of the BCD-MMSE
Algorithm) The proposed BCD-MMSE algorithm is guaran-
teed to converge to the global minimum of problem (2).
Proof: Since the objective function of (25) is a con-
tinuously differentiable and strongly convex function with
respect to Wc. According to [25], The BCD-MMSE algorithm
is guaranteed to converge to the global minimum of
problem (2).
Remark 4 (Extension to Other DBP Architectures):
Although the BCD-MMSE equalizer was originally proposed
for the unidirectional daisy chain architecture shown in
Fig. 2(b), it can be applied to other DBP architectures by
modifying the update rule in (27). For instance, the symmetric
Gauss-Seidel update rule [33] is suitable for the bidirectionaldaisy chain architecture without a ring, where DUs are
connected through bidirectional links, and there is no link
between the last DU and the first DU. Furthermore, this
update rule has a guaranteed convergence to global optima.
Regarding the star DBP architecture depicted in Fig. 2(a),
we could use the Jacobi update rule [34] for BCD iterations.
B. Low-Rank Decomposition Based BCD-MMSE
The proposed optimal BCD-MMSE equalizer effectively
mitigates the bandwidth and computation limitations inherent
in traditional centralized algorithm designs. However, the
communication bandwidth required for each iteration still
depends on the number of noise samples (N ), which may
be very large and even exceed the number of BS anten-
nas (M ) in certain scenarios. One straightforward way to
address this issue is to reduce the number of noise samples
used for covariance estimation. Unfortunately, this approach
results in significant performance degradation since it leads
to poor accuracy of covariance estimation. We below present
an improved BCD-MMSE equalization method with lower
bandwidth consumption for the case when Nis large.
Let us recall the interference scenario, where the noise
covariance matrix R=β ¯H¯HH+σ2Iwith ¯H∈CM×r. Note
that the number of non-target UEs in communication systems
is limited such that r≪min(M, N ). Moreover, the inter-
ference power is generally much greater than the background
AWGN power, i.e., β≫σ2. Consequently, the covariance
matrix Rcan be deemed to be approximately low-rank, i.e.,
a rank-r matrix, implying that, we may obtain its rank-
rapproximation instead of estimating R.7As seen below,
this way brings the benefit of low-interaction decentralized
algorithm design for BCD-MMSE with possibly minor per-
formance degradation.
Given a positive semidefinite matrix R∈CM×M, its rank-
rapproximation seeks a low-rank substitute G∈CM×rof its
square root such that GGHclosely approximates R, i.e.,
G= arg min
Rank(G )≤r∥R−GGH∥2
F, (31)
which can be efficiently solved. Firstly, define N≜1/√
N
[n1, . . . ,nN]and rewrite the estimation of Rin (6) as
ˆR=1
NNX
i=1ni(ni)H=NNH=
N1
...
NC
 
NH
1, . . . ,NH
C
,
(32)
where Nc∈CMc×Nis the local (scaled) noise samples stored
at the c-th DU. Then, denote the SVD of N∈CM×Nby
N=UΣVH, (33)
7Even if Ris not of low rank, to facilitate low-interaction decentralized
implementation, we can still approximate it with a rank-r matrix at the cost
of affordable performance degradation.
Wl
c= 
Es 
IK−Al
c−1+Wl−1
cHc
HH
c−1
NNX
i=1 
bl
c−1,i−Wl−1
cni
c 
ni
cH!
× 
EsHcHH
c+1
NNX
i=1ni
c(ni
c)H!−1
.(30)
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 10

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 745
Algorithm 4 The Proposed LRD Algorithm
Input: N= [NT
1,NT
2, . . . ,NT
C]T.
1:forc= 1 toC−1do
2: ifc= 1 then
3: ˜N0←∅;
4: else
5: ˜Nc−1←Dc−1VH
c−1;
6: end if
7: Compute rank-r decomposition ofh
˜NT
c−1,NT
ciT
as=
UcΣcVH
c;
8:Dc←UcΣc;
9: Transfer DcandVcto the next DU;
10:end for
11:At the C-th DU:
12:Compute rank-r decomposition ofh
˜NT
C−1,NT
CiT
as
UCΣCVH
C;
13:Broadcast and local computation:
14:Broadcast VCto each DU, and compute Gc←NcVC
at each DU;
Output: G= [GT
1,GT
2, . . . ,GT
C]T.
where Σ∈CM×Mis a diagonal matrix with positive singular
values sorted in descending order, U∈CM×MandV∈
CN×Mare matrices containing the left and right singular
vectors of Nas their columns, respectively. According to
Eckart-Young-Mirsky Theorem [35], the optimal solution to
the rank-r approximation problem (31) is given by
G=˜U˜Σ=N˜V, (34)
where ˜Σ∈Cr×ris a diagonal matrix consisting of the r
largest singular values of N,˜U∈CM×rand˜V∈CN×r
being associated left and right singular vectors corresponding
with singular values in ˜Σ. In addition, we call ˜U˜Σ˜Vthe
rank-r decomposition ofN.
We aim to replace NwithGin the proposed BCD-MMSE
algorithm, which can reduce the bandwidth burden at each
iteration since r≪N. Specifically, we focus on finding G=
N˜Vin a decentralized manner, i.e., computing Gc=Nc˜V
at DU cwith appropriate communication among DUs. The
crucial step is to determine ˜VsinceNcis known at DU c.
Traditionally, computing the SVD of matrix Nneeds to
collect all noise samples. Specifically, the c-th DU needs
to transmit
NT
1, . . . ,NT
cT∈CcMc×Nto the next DU.
However, this results in a significant bandwidth burden due
to the large data transfer size of M×Nat the last DU.
To address this issue, at the c-th DU, we transmit the rank-
rdecomposition (i.e.,UcΣcVH
c) of an approximation of
NT
1, . . . ,NT
cT, which significantly reduces the bandwidth
requirements with only minor performance degradation due
to the approximately low-rank property of R. We summarize
the proposed algorithm in Algorithm 4and term it low-rank
decomposition (LRD) algorithm. Note that the c-th DU trans-
mitsDc≜UcΣc∈CcMc×randVc∈CN×rto the next DU,
with a size proportional to (M+N)×r, which is far lessthanM×N. In practice, the value of ris unknown but can
be determined by the number of large singular values of N.
Based on the above discussions, we can represent the N
noise samples with the rcolumn vectors of Gwith little
loss. Specifically, we first perform the LRD algorithm and
then carry out the BCD-MMSE equalization by replacing N
withG. We refer to it as BCD-MMSE (LRD) equalization,
which has a small bandwidth cost at each iteration.
V. C OMPLEXITY AND BANDWIDTH ANALYSIS
A. Computational Complexity Analysis
Throughout the section, we consider the common sce-
nario where min{M, N }> M c> K . The computational
complexity of the centralized LMMSE equalizer in (3)is
O 
M3+NM2
. Since Mcan be extremely large, the cubic
complexity is impractical for massive MIMO systems.
The computational complexity of the proposed sDR-MMSE
and cDR-MMSE equalizers are O(MM2
c+NMM c)and
O(MM2
c+NMM c+K3C3), respectively. They have the
same preprocessing with a complexity of O(M3
c+NM2
c)
at each DU. The complexity of cDR-MMSE equalization is
much higher than that of sDR-MMSE equalization because the
concatenating and superimposing operation at the CU leads to
aCK×CK andK×Kmatrix inversion, respectively.
The complexity of initializing the proposed BCD-MMSE
and BCD-MMSE (LRD) equalization, known as the BDAC-
MMSE algorithm, is dominated by O(MM2
c+NMM c).
The proposed LRD algorithm only needs to be executed
once and has a complexity of O 
min 
M2N, N2M
. The
per-iteration complexity of the BCD-MMSE equalization is
O(NMK +MM cK). Benefiting from the LRD algorithm,
the per-iteration complexity of the BCD-MMSE (LRD) equal-
ization isO(rMK +MM cK), which is independent of N,
where r≪N. Therefore, increasing the number of iterations
of the BCD-MMSE (LRD) algorithm requires only a small
amount of computation.
The complexity of our proposed methods, except for
the BCD-MMSE (LRD) method, scales linearly with M
instead ofO 
M3
. The BCD-MMSE (LRD) method has low
per-iteration complexity that is independent of both MandN.
Therefore, all the proposed algorithms significantly alleviate
the computational bottleneck in massive MIMO systems.
B. Communication Bandwidth Analysis
The communication bandwidth is evaluated by the total
number of real-valued entries transferred among the DUs.
We assume that the channel and noise covariance remain
static across Ncohcontiguous symbols. This means that the
equalization matrix and covariance estimation can be reused
for different symbols, although they will change with every
coherence block. Thus the data required for computing the
equalization matrix is transferred only once for Ncohsymbols,
while the received signal ymust be transferred for each
symbol.
The average data transfer size of the centralized LMMSE
method is 2M(Ncoh+K+N)/N coh. The proposed
sDR-MMSE and cDR-MMSE methods have the same average
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 11

746 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
Fig. 6. SER performance versus SNR for the first four iterations of the proposed BCD-MMSE equalizer.
Fig. 7. SER performance versus SNR for the first four iterations of the proposed BCD-MMSE (LRD) equalizer.
data transfer size of 2CK (Ncoh+K+N)/Ncoh. The average
data transfer size of the proposed BCD-MMSE method is
C(4K2+2NK )/N coh+2TCK (N+K)/N coh+2CK , where
the three terms are induced by preprocessing, Titerations
for computing equalization matrix, and symbol estimation,
respectively. Notably, the average data transfer size of the
aforementioned methods is independent of M. Additionally,
the proposed BCD-MMSE (LRD) method only needs to
transfer ((C−1)Mr +4CNr )/N coh+C(4K2+2Kr )/N coh+
2TCK (r+K)/N coh+ 2CK entries. The first term is caused
by the LRD algorithm, the second term is due to the pre-
processing, the third term is induced by the iteration of the
BCD-MMSE (LRD) method, and the last term is due to
symbol estimation. Interestingly, the data transfer size at each
iteration of the BCD-MMSE (LRD) method is independent
of both MandN. Therefore, all the proposed methods can
achieve a decentralized baseband processing design with a
relatively small communication bandwidth among DUs.
VI. S IMULATION RESULTS
A. Simulation Setup
We investigate a single-cell massive MIMO system com-
prising of a BS equipped with M= 128 or 256 antennas,
divided into C= 8 or 16 clusters, where each cluster has
Mc=M/C antennas. The number of target and non-target
UEs is both set to K= 8, and there are N= 192 noise
samples. The channel matrix is generated from the QuaDRiGa
platform, which considers both large and small-scale fading.
UEs are uniformly distributed within a 120osector of radius50∼100m centered at BS. The signal-to-noise ratio (SNR)
is defined as SNR = 10 log10 
Es/σ2
, where σ2is the
power of background AWGN. The colored noise is mod-
eled as interference from rnon-target UEs plus background
AWGN, where the non-target UEs are molded similarly to
the target UEs. Specifically, the distribution of the colored
noise follows a complex Gaussian distribution, denoted as
CN 
0, β¯H¯HH+σ2I
, where ¯H∈CM×rdenotes the chan-
nel matrix of rnon-target UEs, and βsignifies the power of
non-target UEs. The interference over thermal (IoT) is used
to measure the intensity of interference relative to background
noise, i.e., IoT = 10 log10 
(β+N0)/σ2
. Large IoT leads to
significant interference, i.e., the off-diagonal elements of the
noise covariance matrix are more prominent. IoT = 10 dB is
a default setting in the simulation since it is a typical scenario
in practical systems. Under our settings, the noise covari-
ance is approximately low-rank. The simulation results are
averaged over 100 randomly generated channel realizations,
and 480 symbols are drawn independently from the 16-QAM
constellation for each channel.
B. SER Performance of the Proposed BCD-Based Equalizers
With Different Number of Iterations
This subsection evaluates the symbol error rate (SER)
performance of the proposed BCD-based equalizers. Due to
bandwidth and computation limitations, only the first four
iterations of the BCD algorithms are considered. Four base-
lines are evaluated: the centralized ZF method, the centralized
LMMSE method, the MMSE(AWGN), which denotes the
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 12

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 747
LMMSE equalizer considering only AWGN, and the proposed
intuitive BDAC-MMSE method that serves as the initial point
for the BCD-based algorithms.
Fig. 6 presents the SER performance of the first four
iterations of the proposed BCD-MMSE equalizer. It can be
observed that only 2 to 3 iterations are sufficient to approach
the performance of the centralized LMMSE method for all
cases.8Even a single BCD iteration enables excellent SER
performance. In addition, Fig. 6(a) and(b)illustrate that when
the BS employs more antennas, the performance gap between
the BCD-MMSE equalizer and LMMSE equalizer decreases,
and all the equalizers attain better performance. Thus, the
BCD-MMSE equalizer is suitable for extremely large antenna
arrays. As the number of clusters increases, the BDAC-MMSE
equalizer utilizes a smaller portion of the covariance matrix
for decentralized processing, which incurs larger performance
loss. Hence the performance of the BCD-MMSE equalizer
decreases slightly, as shown in Fig. 6(a) and(c). Moreover,
it can be seen that the performance of MMSE(AWGN) and
ZF equalizers is close, and both are far worse than other
algorithms. Therefore, the proposed methods are no longer
compared to MMSE(AWGN) in subsequent simulations.
Fig. 7illustrates the SER performance of the first four
iterations of the BCD-MMSE (LRD) equalizer. The value of r
is selected as the number of non-target UEs, i.e., K= 8. The
performance of the BCD-MMSE (LRD) algorithm is almost
the same as the BCD-MMSE algorithm in Fig. 6. According
to the complexity and bandwidth analysis in Section V, the
LRD algorithm significantly reduces the dimension of com-
munication variables. Thus, the complexity and bandwidth at
each iteration are considerably reduced.
C. SER Performance of All the Proposed Equalizers
Fig.8shows the SER performance of all the proposed meth-
ods, including sDR-MMSE, cDR-MMSE, BCD-MMSE, and
BCD-MMSE (LRD) equalizers. Considering the bandwidth
limitation in practical systems, we run the BCD-MMSE and
the BCD-MMSE (LRD) equalizers for one and four iterations,
respectively, resulting in similar levels of communication
bandwidth. Furthermore, we set r=Kfor the LRD algorithm.
As shown in Fig. 8, the proposed equalizers’ performance
ranking is BCD-MMSE (LRD), BCD-MMSE, cDR-MMSE,
and sDR-MMSE. Generally speaking, BCD-MMSE and
cDR-MMSE methods have comparable performance. Specif-
ically, Fig. 8(a) and(b)show that all methods achieve better
performance with increasing the number of BS antennas.
Fig.8(b) and(c)imply that more clusters lead to a lower SER
performance, as only a small portion of the covariance matrix
becomes locally available. Additionally, Fig. 8(a) and (e)
demonstrate that, with an increase in the number of UEs
from 8 to 12, the cDR-MMSE equalizer’s performance greatly
improves due to the rising local compression dimension
from 8 to 12. Finally, Fig. 8(f)shows SER performance under
IoT= 20 dB, where the performance of all equalizers is
8There is a small gap between the BCD-MMSE method and the centralized
LMMSE method because the number of iterations is not enough. Actually,
after sufficient iterations, they will overlap completely.TABLE I
TOTAL FRONTHAUL DATA RATECOMPARISON FORDIFFERENT
SYSTEM PARAMETERS [TBPS]
significantly degraded due to stronger interference in colored
noise. Moreover, Fig. 8(g) compares the proposed equalizers’
performance using QPSK modulation, which results in fewer
error symbols than 16-QAM modulation.
To summarize, for the daisy chain architecture, the
BCD-MMSE equalizer is an efficient algorithm with fast
convergence and near-optimal SER performance. The LRD
enhancement further improves the BCD-MMSE equalizer’s
performance with the same level of bandwidth. For the star
architecture, the cDR-MMSE equalizer has better performance
but higher complexity than the sDR-MMSE equalizer.
D. Fronthaul Data-Rate Comparison
To evaluate the required data rate of the proposed decen-
tralized equalization algorithms, we consider a frame structure
in orthogonal frequency-division multiplexing (OFDM) sys-
tems. Specifically, we leverage channel correlation based on
the physical resource block (PRB) concept outlined in the
third-generation partnership project (3GPP) technical stan-
dards. A PRB is defined as a frequency-time stripe over which
the wireless channel remains constant across all subcarriers.
Within an OFDM symbol, the number of subcarriers in each
PRB and the number of PRBs per symbol are specified as
Nsc,PRB andNPRB, respectively. Each symbol contains Nu≜
Nsc,PRB×NPRB subcarriers (a resource element in OFDM
system) to carry user data within a duration of TOFDM . Each
PRB corresponds to a different channel matrix in the baseband
model in (1).
1)Formulation phase: Define Aas the set of all matri-
ces transmitted during the equalization matrix formulation
phase for a decentralized scheme. For example, Aincludes
{QcHc,{Qcni
c}N
i=1}C
c=1for DR-MMSE.9The average fron-
thaul data rate during the formulation phase can be calculated
using the following equation:
Rform=wSANPRB
TOFDM,
where wis the bit-width of each element in A(including
both real and imaginary parts), SAis the total number of real
elements in A, and the numerator represents the total number
of bits required to transfer Awithin one OFDM symbol.
2) Filtering phase: The local processing results
(e.g.,{Qcyc}C
c=1for DR-MMSE.) are collected to obtain
9sDR-MMSE and cDR-MMSE are collectively referred to as DR-MMSE,
as they involve the same amount of information interaction
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 13

748 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
Fig. 8. SER versus SNR of the baselines and all the proposed equalizers.
the final estimate. The average fronthaul data rate during the
filtering phase can be calculated as
Rfil=wSsNu
TOFDM,
where Ssdenotes number of real elements in local processing
results. The total data rate is given by
Rtotal=Rform+Rfil.
For the numerical results, we set N= 192, r= 8, and
w= 12. The remaining system parameters are configured as
follows according to the worst case in 5G NR: Nu= 3300,
NPRB= 275 ,Nsc,PRB = 12 andTOFDM =1
120 KHz. Table I
presents a comparison of the total fronthaul data rate between
the centralized and our proposed decentralized algorithms
under the DBP architectures for different settings of M,K,
andC. The iteration number of the BCD-MMSE and BCD-
MMSE (LRD) algorithms are both set to 2. We observe
that for most of the test cases, the DR-MMSE and BCD-
MMSE, and BCD-MMSE (LRD) equalization schemes require
23%, 44%, and 37% of the data rate needed by centralized
MMSE (C-MMSE) algorithm. This portion can be further
decreased as the ratio M/K grows. Additionally, we find that
the fronthaul data rates of the DR-MMSE and BCD-MMSE
algorithms are independent of M, making them particularly
beneficial for massive MIMO settings. In contrast to the BCD-
MMSE algorithm, the fronthaul data-rate in BCD-MMSE
(LRD) increases slowly with the number of iterations.VII. C ONCLUSION
This paper has investigated the decentralized LMMSE
equalizer design under the DBP architectures. The existing
decentralized equalization algorithms only considered ideal
AWGN assumption, whereas colored noise exists in practice.
Therefore, we have proposed DR-based and BCD-based equal-
izers for the star and daisy chain architectures, respectively.
The data transfer size of these equalizers is independent of
the number of BS antennas, significantly mitigating the band-
width and computation bottlenecks encountered in centralized
counterparts. In addition, the communication bandwidth of the
BCD-MMSE equalizer can be reduced further by applying the
LRD algorithm. Extensive simulation results have shown the
excellent performance of the proposed algorithms. Future work
includes extending our decentralized equalization methods to
other decentralized architectures such as cell-free massive
MIMO systems. Additionally, deep learning techniques [36]
may help mitigate bandwidth and computation limitations in
our design.
APPENDIX A
PROOF OF THEOREM 1
Proof: The MSE matrix for the LMMSE estimate in (3)
is given by
EMMSE≜E[(ˆsMMSE−s) (ˆsMMSE−s)H]
=EsI−EsHH
HHH+1
EsR−1
H. (35)
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 14

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 749
Similarly, we obtain the MSE matrix for compression matrix
Q∈CL×Mas follows:
EC=EsI−EsHHQH
QHHHQH+1
EsR−1
QH. (36)
With these definitions, we first prove that the minimal com-
pression dimension without performance loss is rank(H) = K.
Specifically, we prove it via contradiction, Assume the con-
trary that Q∈CL×MwithL < K is a lossless compression
matrix, i.e., EC=EMMSE , which yields
HH
HHH+1
EsR−1
H
=HHQH
QHHHQH+1
EsR−1
QH. (37)
However, the rank of the left-hand side and right-hand side of
(37) is KandL, respectively. This leads to a contradiction.
Then we verify that PHHR−1for an arbitrary invertible
matrix P∈CK×Kis a lossless compression matrix by the
following derivation:
¯sMMSE =
HHQH 
QRQH−1QH+1
EsI−1
×HHQH 
QRQH−1Qy
=
HHR−1H+1
EsI−1
HHR−1y, (38)
where the first equality provides the LMMSE estimate (cf. (3))
ofsbased on the compressed received vector Qy, and the
second equality is obtained by taking Q=PHHR−1. The
equivalence between (3)and (38) immediately shows that
PHHR−1is a lossless compression matrix.
APPENDIX B
PROOF OF PROPOSITION 1
Proof: From the definition of EsDR, we have
EsDR=EsI−EsHHˇQH
×
ˇQHHHˇQH+1
EsˇQRˇQH−1
ˇQH. (39)
By leveraging the Woodbury identity [37], one has
E−1
sDR=1
EsI+HHˇQH ˇQRˇQH−1ˇQH. (40)
Similarly, we can obtain E−1
cDRby substituting the ˇQin(40)
with ˜Q. To prove EcDR⪯EsDR, it is equivalent to show
E−1
cDR⪰E−1
sDR. Further, it is sufficient to show
˜QH
˜QR˜QH−1˜Q⪰ˇQH ˇQRˇQH−1ˇQ, (41)
which is equivalent to
R1
2˜QH
˜QR˜QH−1˜QR1
2⪰R1
2ˇQH ˇQRˇQH−1ˇQR1
2.(42)
We observe that R1
2˜QH
˜QR˜QH−1˜QR1
2is an orthog-
onal projection matrix with range space R
R1
2˜QH
, andR
R1
2˜QH
⊇R
R1
2ˇQH
holds obviously (Notice that the
opposite is not necessarily true). Therefore, (42) must hold.
Thus we have EsDR⪰EcDR, which immediately implies
Tr(E sDR)≥Tr(E cDR). Further combining with Tr(E sDR) =
Eh
∥ˆssDR-MMSE−s∥2
2i
. The proof is concluded.
APPENDIX C
PROOF OF PROPOSITION 2
Proof: Since the objective function of problem (25) is
convex in Wc, we could obtain the optimal solution by setting
the gradient equal to 0. Note that the expectation in problem
(25) is taken with respect to s, it can be rewritten as
1
NNX
i=1E"WcHcs+CX
j=1,j̸=cWjHjs+Wcni
c
+CX
j=1,j̸=cWjni
j−s2
2#
=ℜe 
Tr 
EsWcHcHH
cWH
c+2E sCX
j=1,j̸=cWcHcHH
jWH
j
−2EsWcHc+Wc 
1
NNX
i=1ni
c(ni
c)H!
WH
c
+ 2CX
j=1,j̸=cWc 
1
NNX
i=1ni
j(ni
c)H!
WH
j!!
+const,
(43)
whereℜe(a) is the real part of a complex scalar a, “const”
denotes the terms independent of Wc, and the equality is due
to the independence of sandn. Denote f(·)as the function
in(43) and calculate its gradient w.r.t. Wc, yielding
∇Wcf(Wc) = 2 EsWcHcHH
c+ 2E sCX
j=1,j̸=cWjHjHH
c
−2EsHH
c+ 2W c 
1
NNX
i=1ni
c(ni
c)H!
+ 2CX
j=1,j̸=cWj 
1
NNX
i=1ni
j(ni
c)H!
.(44)
Letting∇Wcf(W∗
c) =0, we obtain the optimal solution W∗
c
in closed form as in (26).
REFERENCES
[1] X. Zhao, X. Guan, M. Li, and Q. Shi, “Decentralized linear MMSE
equalizer under colored noise for massive MIMO systems,” in Proc.
IEEE Global Commun. Conf. (GLOBECOM), Dec. 2021, pp. 1–6.
[2] J. Zhang, E. Björnson, M. Matthaiou, D. W. K. Ng, H. Yang, and
D. J. Love, “Prospective multiple antenna technologies for beyond 5G,”
IEEE J. Sel. Areas Commun., vol. 38, no. 8, pp. 1637–1660, Aug. 2020.
[3] T. L. Marzetta and H. Q. Ngo, Fundamentals of Massive MIMO.
Cambridge, U.K.: Cambridge Univ. Press, 2016.
[4] M. Wang, F. Gao, S. Jin, and H. Lin, “An overview of enhanced massive
MIMO with array signal processing techniques,” IEEE J. Sel. Topics
Signal Process., vol. 13, no. 5, pp. 886–901, Sep. 2019.
[5] F. Rusek et al., “Scaling up MIMO: Opportunities and challenges with
very large arrays,” IEEE Signal Process. Mag., vol. 30, no. 1, pp. 40–60,
Jan. 2013.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 15

750 IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS, VOL. 43, NO. 3, MARCH 2025
[6] K. Li, R. R. Sharan, Y . Chen, T. Goldstein, J. R. Cavallaro, and C. Studer,
“Decentralized baseband processing for massive MU-MIMO systems,”
IEEE J. Emerg. Sel. Topics Circuits Syst., vol. 7, no. 4, pp. 491–507,
Dec. 2017.
[7] J. Rodríguez Sánchez, F. Rusek, O. Edfors, M. Sarajlic, and L. Liu,
“Decentralized massive MIMO processing exploring daisy-chain archi-
tecture and recursive algorithms,” IEEE Trans. Signal Process., vol. 68,
pp. 687–700, 2020.
[8] (2019). Common Public Radio Interface . [Online]. Available:
http://www.cpri.info
[9] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, “Decentralized equal-
ization with feedforward architectures for massive MU-MIMO,” IEEE
Trans. Signal Process., vol. 67, no. 17, pp. 4418–4432, Sep. 2019.
[10] K. Li, O. Castañeda, C. Jeon, J. R. Cavallaro, and C. Studer,
“Decentralized coordinate-descent data detection and precoding for
massive MU-MIMO,” in Proc. IEEE Int. Symp. Circuits Syst. (ISCAS),
May 2019, pp. 1–5.
[11] C. Jeon, K. Li, J. R. Cavallaro, and C. Studer, “On the achievable rates
of decentralized equalization in massive MU-MIMO systems,” in Proc.
IEEE Int. Symp. Inf. Theory (ISIT), Jun. 2017, pp. 1102–1106.
[12] H. Wang, A. Kosasih, C.-K. Wen, S. Jin, and W. Hardjawana, “Expec-
tation propagation detector for extra-large scale massive MIMO,” IEEE
Trans. Wireless Commun., vol. 19, no. 3, pp. 2036–2051, Mar. 2020.
[13] Z. Zhang, H. Li, Y . Dong, X. Wang, and X. Dai, “Decentralized
signal detection via expectation propagation algorithm for uplink mas-
sive MIMO systems,” IEEE Trans. Veh. Technol., vol. 69, no. 10,
pp. 11233–11240, Oct. 2020.
[14] A. Amiri, C. N. Manchón, and E. De Carvalho, “Uncoordinated and
decentralized processing in extra-large MIMO arrays,” IEEE Wireless
Commun. Lett., vol. 11, no. 1, pp. 81–85, Jan. 2022.
[15] J. R. Sánchez, J. Vidal Alegría, and F. Rusek, “Decentralized massive
MIMO systems: Is there anything to be discussed?” in Proc. IEEE Int.
Symp. Inf. Theory (ISIT), Jul. 2019, pp. 787–791.
[16] Z. Zhang, Y . Dong, K. Long, X. Wang, and X. Dai, “Decentralized
baseband processing with Gaussian message passing detection for uplink
massive MU-MIMO systems,” IEEE Trans. Veh. Technol., vol. 71, no. 2,
pp. 2152–2157, Feb. 2022.
[17] A. Kulkarni, M. A. Ouameur, and D. Massicotte, “Hardware topologies
for decentralized large-scale MIMO detection using Newton method,”
IEEE Trans. Circuits Syst. I, Reg. Papers, vol. 68, no. 9, pp. 3732–3745,
Sep. 2021.
[18] S. Cui, J. Zhang, J. Wang, and X. Gao, “Decentralized bidirectional-
chain equalizer for massive MIMO,” in Proc. IEEE 97th Veh. Technol.
Conf. (VTC-Spring), Jun. 2023, pp. 1–7.
[19] J. V . Alegría and F. Rusek, “Trade-offs in decentralized multi-antenna
architectures: Sparse combining modules for WAX decomposition,”
IEEE Trans. Signal Process., vol. 71, pp. 2879–2894, 2023.
[20] X. Zhao, M. Li, Y . Liu, T.-H. Chang, and Q. Shi, “Communication-
efficient decentralized linear precoding for massive MU-MIMO sys-
tems,” IEEE Trans. Signal Process., vol. 71, pp. 4045–4059, 2023.
[21] Y . Liu, T. F. Wong, and W. W. Hager, “Training signal design for
estimation of correlated MIMO channels with colored interference,”
IEEE Trans. Signal Process., vol. 55, no. 4, pp. 1486–1497, Apr. 2007.
[22] S. Tomasin, R. Hasler, A. M. Tulino, and M. Sánchez-Fernández,
“Estimation of interference correlation in mmWave cellular systems,”
2023, arXiv:2304.14871.
[23] K. W. Helmersson, P. Frenger, and A. Helmersson, “Uplink D-MIMO
with decentralized subset combining,” in Proc. IEEE Int. Conf. Commun.
(ICC), May 2022, pp. 5134–5139.
[24] Z. H. Shaik, E. Björnson, and E. G. Larsson, “MMSE-optimal sequential
processing for cell-free massive MIMO with radio stripes,” IEEE Trans.
Commun., vol. 69, no. 11, pp. 7775–7789, Nov. 2021.
[25] D. P. Bertsekas, Nonlinear Programming. Cambridge, MA, USA: MIT
Press, 1999.
[26] Y . Xu, B. Wang, E. Song, Q. Shi, and T.-H. Chang, “Low-complexity
channel estimation for massive MIMO systems with decentralized
baseband processing,” 2022, arXiv:2210.15917.
[27] A. Rajoriya, R. Budhiraja, and L. Hanzo, “Centralized and decentralized
channel estimation in FDD multi-user massive MIMO systems,” IEEE
Trans. Veh. Technol., vol. 71, no. 7, pp. 7325–7342, Jul. 2022.
[28] S. M. Kay, Fundamentals of Statistical Signal Processing: Estimation
Theory. Upper Saddle River, NJ, USA: Prentice-Hall, 1993.
[29] G. Barriac and U. Madhow, “Space-time communication for OFDM with
implicit channel feedback,” IEEE Trans. Inf. Theory, vol. 50, no. 12,
pp. 3111–3129, Dec. 2004.[30] I.D. Schizas, G. B. Giannakis, and Z.-Q. Luo, “Distributed estimation
using reduced-dimensionality sensor observations,” IEEE Trans. Signal
Process., vol. 55, no. 8, pp. 4284–4299, Aug. 2007.
[31] E. Song, Y . Zhu, and J. Zhou, “Sensors’ optimal dimensionality com-
pression matrix in estimation fusion,” Automatica, vol. 41, no. 12,
pp. 2131–2139, Dec. 2005.
[32] M. Hong, X. Wang, M. Razaviyayn, and Z.-Q. Luo, “Iteration com-
plexity analysis of block coordinate descent methods,” Math. Program.,
vol. 163, no. 1, pp. 85–114, May 2017.
[33] D. Sun, K.-C. Toh, and L. Yang, “An efficient inexact ABCD method
for least squares semidefinite programming,” SIAM J. Optim., vol. 26,
no. 2, pp. 1072–1100, Jan. 2016.
[34] D. Bertsekas and J. Tsitsiklis, Parallel and Distributed Computation:
Numerical Methods. Englewood Cliffs, NJ, USA: Prentice-Hall, 1989.
[35] C. Eckart and G. Young, “The approximation of one matrix by another
of lower rank,” Psychometrika, vol. 1, no. 3, pp. 211–218, Sep. 1936.
[36] W. Xu, Z. Yang, D. W. K. Ng, M. Levorato, Y . C. Eldar, and M. Debbah,
“Edge learning for B5G networks with distributed signal processing:
Semantic communication, edge computing, and wireless sensing,” IEEE
J. Sel. Topics Signal Process., vol. 17, no. 1, pp. 9–39, Jan. 2023.
[37] K. B. Petersen and M. S. Pedersen, “The matrix cookbook,” Tech. Univ.
Denmark, Lyngby, Denmark, Tech. Rep., 2006.
Xiaotong Zhao received the B.S. and M.S. degrees
from the School of Mathematics, Sichuan University,
Chengdu, China, in 2015 and 2020, respectively.
He is currently pursuing the Ph.D. degree with
the School of Software Engineering, Tongji Uni-
versity, Shanghai, China. His research interests
include optimization theory and algorithms, and
their applications to signal processing for wireless
communications.
Mian Li received the B.S. degree from the
Huazhong University of Science and Technology,
Wuhan, China, in 2021. He is currently pursuing
the Ph.D. degree with the School of Science and
Engineering, The Chinese University of Hong Kong,
Shenzhen, China. His research interests include opti-
mization theory and algorithms, as well as machine
learning theory and applications.
Bo Wang received the B.S. and Ph.D. degrees in
information engineering from Xi’an Jiaotong Uni-
versity, Xi’an, China, in 2010 and 2017, respectively.
He is currently with the Wireless Network RAN
Algorithm Department, Xi’an Huawei Technologies
Company Ltd. His research interests include signal
processing techniques in wireless communication
systems.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 


# Page 16

ZHAO et al.: EFFICIENT LMMSE EQUALIZATION FOR MASSIVE MIMO SYSTEMS UNDER DBP ARCHITECTURE 751
Enbin Song received the B.S. degree from
Shandong Normal University, Jinan, China, in 2002,
and the Ph.D. degree from Sichuan University,
Chengdu, China, in 2007. From 2007 to 2009,
he was a Post-Doctoral Researcher with the Col-
lege of Computer Science. After that, he was
an Associate Professor moved to the College of
Mathematics, and since 2014, he has been a Full Pro-
fessor. From 2010 to 2011, he was a Post-Doctoral
Researcher with the Department of Electrical and
Computer Engineering, University of Minnesota,
Minneapolis, MN, USA. From 2013 to 2014, he was a Visiting Scholar with
the Department of Systems Engineering and Engineering Management, The
Chinese University of Hong Kong, Hong Kong, China. He is currently with
Sichuan University. His research interests include information processing and
nonlinear optimization with an emphasis on the design, analysis, and appli-
cations of optimization algorithms for multi-sensor estimation and decision
fusion, statistics, and multiuser wireless communication. He was a recipient
of the National Excellent Doctoral Dissertation Nomination Award in 2009.
Tsung-Hui Chang (Fellow, IEEE) received the B.S.
degree in electrical engineering and the Ph.D. degree
in communications engineering from National Tsing
Hua University (NTHU), Hsinchu, Taiwan, in
2003 and 2008, respectively.
He is currently a Professor and the Associate Dean
(Education) of the School of Science and Engineer-
ing (SSE), The Chinese University of Hong Kong,
Shenzhen (CUHK-SZ), China, and the Associate
Director of Guangdong Provincial Key Laboratory
of Big Data Computing. Before joining the CUHK-
SZ, he was with the NTHU, the University of California, Davis, and the
National Taiwan University of Science and Technology (NTUST), as a
Post-Doctoral Researcher and a Faculty Member, respectively. His research
interests include signal processing and optimization methods for data com-
munications and machine learning. He has been an Elected Member of the
IEEE Signal Processing Society (SPS) Signal Processing for Communications
and Networking Technical Committee (SPCOM TC) since January 2020.
He received the Young Scholar Research Award of NTUST in 2014, the
IEEE ComSoc Asian-Pacific Outstanding Young Researcher Award in 2015,
the IEEE SPS Best Paper Awards in 2018 and 2021, and the Outstanding
Faculty Research Award of SSE of CUHK-SZ in 2021. He is the Founding
Chair of the IEEE SPS Integrated Sensing and Communication Technical
Working Group (ISAC TWG). He has been the elected Regional Director-
at-Large of Board of Governors of IEEE SPS since 2022. He has served
on the editorial board for major SP journals, including an Associate Editor
for IEEE T RANSACTIONS ON SIGNAL PROCESSING from August 2014 to
December 2018, IEEE T RANSACTIONS ON SIGNAL AND INFORMATION
PROCESSING OVER NETWORKS from January 2015 to December 2018,
IEEE O PEN JOURNAL OF SIGNAL PROCESSING since January 2020, and a
Senior Area Editor for IEEE T RANSACTIONS ON SIGNAL PROCESSING since
February 2021.
Qingjiang Shi (Member, IEEE) received the Ph.D.
degree in electronic engineering from Shanghai Jiao
Tong University, Shanghai, China, in 2011.
From September 2009 to September 2010, he vis-
ited Prof. Z.-Q. (Tom) Luo’s Research Group,
University of Minnesota, Twin Cities, MN, USA.
In 2011, he was a Research Scientist with the Bell
Laboratories, China. Since 2012, he has been with
the School of Information and Science Technol-
ogy, Zhejiang Sci-Tech University. From February
2016 to March 2017, he was a Research Fellow with
Iowa State University, Ames, IA, USA. Since March 2018, he has been a
Full Professor with the School of Software Engineering, Tongji University,
Shanghai, China. He is also with Shenzhen Research Institute of Big Data.
He has published more than 80 IEEE journals and filed about 40 national
patents. His research interests include algorithm design and analysis with
applications in machine learning, signal processing, and wireless networks.
He was a recipient of the IEEE Signal Processing Society Best Paper Award in
2022, the Second Prize of Zhejiang Provincial Natural Science Award in 2023,
the Excellent Technical Cooperation Award From Huawei Wireless Network
Product Line in 2024, the Huawei Technical Cooperation Achievement
Transformation Award (2nd Prize) in 2022, the Huawei Outstanding Technical
Achievement Award in 2021, the Golden Medal at the 46th International
Exhibition of Inventions of Geneva in 2018, the First Prize of Science
and Technology Award from China Institute of Communications in 2017,
the National Excellent Doctoral Dissertation Nomination Award in 2013,
Shanghai Excellent Doctoral Dissertation Award in 2012, and the Best Paper
Award from the IEEE PIMRC’09 Conference. He has served on the editorial
board of IEEE T RANSACTIONS ON SIGNAL PROCESSING as an Associate
Editor.
Authorized licensed use limited to: UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Downloaded on May 16,2026 at 20:19:31 UTC from IEEE Xplore.  Restrictions apply. 