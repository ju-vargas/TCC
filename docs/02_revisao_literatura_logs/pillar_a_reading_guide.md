# Pillar A — Inversion Avoidance
## Annotated Reading Guide: Priorities, Questions Answered, and Narrative Placement

*For: FPGA Implementation of Matrix Inversion for Decentralized LMMSE Equalization in Massive MIMO under Colored Noise*

---

## How to use this guide

Pillar A serves a specific narrative function in your review: it demonstrates that the research community has invested heavily in avoiding matrix inversion, and that every inversion-avoidance strategy ultimately relies — explicitly or implicitly — on assumptions about the noise model that break under colored noise. Your goal when reading these papers is not to master each algorithm but to extract the assumption that limits it and the inversion structure it either avoids or defers.

Each entry is structured as:
- **Priority** and **venue/year**
- **Narrative role** — where this paper appears in your review
- **The question it answers** — what gap in your argument this paper fills
- **What to extract** — the concrete items to note when reading
- **Points to keep in mind** — traps, nuances, and cross-paper connections
- **What it adds to your analysis** — the sentence-level contribution to your argument

Papers are ordered chronologically within priority tiers.

---

---

# PRIORITY 1 — Read in full

---

## 1. Sanchez, Rusek, Sarajlic, Edfors, Liu — SiPS 2018
**"Fully Decentralized Massive MIMO Detection Based on Recursive Methods"**
IEEE SiPS Workshop, Cape Town, 2018

**Narrative role:** Section 4 — earliest anchor for the inversion-avoidance thread in fully decentralized settings

### The question it answers
*What was the first explicit demonstration that matrix inversion can be avoided in fully decentralized massive MIMO detection, and what recursive method achieves ZF performance without dedicated inversion hardware?*

This paper establishes the historical starting point of the inversion-avoidance-in-decentralized-MIMO thread. It predates the Li et al. 2017 anchor paper's decentralized extension by proposing a fully decentralized recursive approach (gradient descent and RLS variants) that converges asymptotically to ZF without any central node. Reading this first gives you the "year zero" of the story Section 4 tells.

### What to extract
- The recursive update rule: which of the three methods (gradient descent, RLS, stochastic approximation) is presented, and what operation does each cluster perform per step?
- The convergence target: ZF is the stated goal — is MMSE also discussed, or only ZF? If only ZF, note that colored noise affects ZF and MMSE differently.
- The noise model: AWGN assumed? Is it stated explicitly or implicit in the ZF formulation?
- The interconnect data rate claim: what is communicated between clusters and how does it compare to centralized processing?
- Any mention of what happens to convergence when the channel is poorly conditioned — this is the earliest proxy for the colored noise condition number problem.

### Points to keep in mind
- This is a SiPS workshop paper (6 pages). Extract the key equations and the convergence claim; don't expect full proofs. The journal expansion (Sánchez et al. TSP 2020) will contain the complete analysis.
- The same first author (Sánchez) appears in the ISIT 2019 Pillar B paper that proves inversion is unavoidable for ZF. Reading these two papers from the same author in sequence reveals a productive tension: first he shows inversion can be avoided recursively (this paper), then he shows it is unavoidable in general (ISIT 2019). Your review benefits from citing both and noting the resolution: recursive avoidance works under AWGN but the structural inversion reappears under colored noise.
- "Without the need of specific hardware for matrix inversion" is the claim your project refutes — not because the paper is wrong, but because it assumes AWGN. Under colored noise, that specific hardware is exactly what is needed.

### What it adds to your analysis
In Section 4, this paper opens the inversion-avoidance narrative: as early as 2018, researchers showed that ZF detection could be achieved without explicit inversion hardware, under AWGN. Every subsequent Pillar A paper refines this result — until the colored noise papers show the assumption breaks.

---

## 2. Sánchez, Rusek, Edfors, Sarajlić, Liu — TSP 2020
**"Decentralized Massive MIMO Processing Exploring Daisy-Chain Architecture and Recursive Algorithms"**
IEEE Transactions on Signal Processing, vol. 68, 2020

**Narrative role:** Section 4 — definitive journal treatment of recursive inversion avoidance on the daisy-chain; the canonical Pillar A reference for the Sánchez/Rusek group

### The question it answers
*What is the full theoretical characterization of coordinate descent and Kaczmarz-based recursive detection on the daisy-chain architecture, and under what conditions do these methods converge to ZF/MMSE performance without inversion?*

This is the journal expansion of the SiPS 2018 paper and the TSP companion to the Pillar B ISIT 2019 paper. It is the most complete treatment of inversion-avoidance on the daisy-chain from the Rusek group, and it establishes the performance-interconnect-latency tradeoff that all subsequent daisy-chain papers measure against.

### What to extract
- The coordinate descent (CD) update rule on the daisy-chain: what each node computes, what is communicated, and what the per-step computational cost is.
- The connection to the Kaczmarz algorithm: this is not just a footnote — it provides the convergence theory. Extract the convergence rate and the conditions on the system matrix under which convergence is guaranteed.
- The SINR or BER achieved as a function of the number of iterations — this becomes the benchmark your Section 4 uses to compare inversion-avoidance performance against exact inversion.
- The noise model: where exactly does AWGN appear? In the SINR derivation, in the convergence proof, or in both?
- Any discussion of what happens to convergence under ill-conditioned channels — this is the closest this paper comes to the colored noise problem.

### Points to keep in mind
- The CD and Kaczmarz connection is mathematically deep and important for your review: Kaczmarz is a randomized row-projection method for solving linear systems, and its convergence rate is bounded by the condition number of the system matrix. Under colored noise, the effective system matrix H^H R^{-1} H has a higher condition number than H^H H (under AWGN), which means CD/Kaczmarz converges more slowly — or fails to converge within a fixed iteration budget. This is your most analytically precise colored noise limitation argument for this family.
- This paper and the Wang et al. TSP 2025 Kaczmarz paper (entry 11 below) are the bookends of the Kaczmarz thread: Sánchez 2020 introduces Kaczmarz for decentralized detection, Wang 2025 proposes MCRBK with dynamic step size to handle convergence problems. The progression shows the field has been fighting the condition number problem for five years without addressing it in the colored noise regime directly.
- The downlink precoding results in this paper are out of scope — focus only on the uplink detection analysis.

### What it adds to your analysis
This paper is the primary reference for the coordinate descent / Kaczmarz family of inversion-avoidance methods in your Section 4. It provides the convergence conditions, the performance benchmarks, and the SINR analysis that your colored noise gap argument builds on. When you write "coordinate descent methods converge to ZF under AWGN but their convergence rate degrades with the condition number of the effective system matrix," this paper supplies the supporting citation and the quantitative bound.

---

## 3. Li, Castañeda, Jeon, Cavallaro, Studer — ISCAS 2019
**"Decentralized Coordinate-Descent Data Detection and Precoding for Massive MU-MIMO"**
IEEE ISCAS, Sapporo, 2019

**Narrative role:** Section 4 — coordinate descent in the Li/Studer DBP lineage; GPU implementation results

### The question it answers
*How does coordinate descent perform as a decentralized detection algorithm in the Li/Studer DBP architecture, and what does half-precision floating-point implementation tell us about the precision requirements for inversion-avoidance methods?*

This paper sits at the intersection of Pillars A and B: it uses coordinate descent (Pillar A) within the DBP architecture (Pillar B lineage of Li et al. 2017). It provides the most practically grounded evaluation of CD-based detection in the specific architectural context your review targets.

### What to extract
- The coordinate descent update rule in the decentralized setting: what each cluster computes, what is communicated to the fusion node, and whether any preprocessing inversion is required before iterations begin.
- Whether the preprocessing step (if any) involves a local K×K solve — this is the hidden inversion that CD-based methods often defer to initialization.
- The half-precision (FP16) implementation results: what precision loss is observed relative to FP32, and at what SNR? This is the only paper in your Pillar A list that directly addresses numerical precision in the decentralized detection context.
- The multi-Gbps throughput and sub-1ms latency figures — these become the performance targets for your FPGA implementation in Section 7.
- The noise model and whether correlated channels are tested.

### Points to keep in mind
- Half-precision floating point is a 16-bit format, similar in bit count to fixed-point implementations. The fact that the authors chose FP16 rather than INT16 (fixed-point) tells you something about the dynamic range requirements of CD: FP16's floating exponent handles a wider dynamic range than INT16 at the same bit width. Under colored noise, where the condition number is higher, this dynamic range advantage becomes even more important — fixed-point arithmetic may require more bits than FP16 suggests.
- This paper covers both uplink detection and downlink precoding. Focus only on the uplink (detection) results.
- Cross-reference with Jeon et al. TSP 2019 (Pillar B): both papers are from the same group and the same period. Jeon covers the architecture; this paper covers the CD algorithm within that architecture. Read them as a pair.

### What it adds to your analysis
In Section 4, this paper provides the GPU-implemented CD baseline that your FPGA must compare against. It also introduces the precision dimension to the Pillar A narrative: even inversion-avoidance methods require careful numerical treatment, and the half-precision results here are the baseline from which your colored noise fixed-point analysis departs.

---

## 4. Zhang, Li, Dong, Wang, Dai — TVT 2020
**"Decentralized Signal Detection via Expectation Propagation Algorithm for Uplink Massive MIMO Systems"**
IEEE Transactions on Vehicular Technology, vol. 69, no. 10, Oct. 2020

**Narrative role:** Section 4 — EP family baseline for decentralized DBP detection; introduces the message fusion rule

### The question it answers
*Can expectation propagation be adapted to the DBP cluster architecture with a local-means-and-variances message passing scheme, and what message fusion rule at the CPU recovers near-centralized performance?*

This is the foundational paper for EP-based decentralized detection in the DBP architecture. It establishes the message structure (local means and variances per cluster), the fusion rule at the CPU, and the performance benchmark that all subsequent EP papers (Li groupwise 2023, FFIC-EP 2025, FF-VEP 2025) build on.

### What to extract
- The message structure: what exactly each cluster computes and communicates — means and variances of the local posterior, or something else?
- The fusion rule at the CPU: what mathematical operation does it perform? Does it require any matrix inversion, and of what dimension?
- The EP cavity computation at each cluster: does it require inverting a K×K precision matrix per iteration? This is the hidden inversion that EP-based methods carry.
- The convergence behavior as the number of antenna clusters increases — this is where performance loss appears and where the colored noise problem will be most severe.
- The noise model: AWGN throughout? Is any correlation structure tested?

### Points to keep in mind
- Standard EP for MIMO detection requires inverting a K×K precision matrix (the cavity distribution's precision matrix) at each cluster per iteration. Whether this paper uses the exact EP inversion or an approximation is the single most important thing to determine when you read it. If exact, EP is not truly inversion-free — it defers the inversion to a smaller local matrix. If approximate (e.g., Neumann series for the cavity inversion), the approximation quality degrades under colored noise.
- The "marginal computational complexity overhead when the number of antenna clusters is small" claim is the key limitation: performance degrades as cluster count increases. Under colored noise, this degradation is amplified because each cluster's local posterior is less well-conditioned.
- This paper is the root of a tree of subsequent EP papers (Zhang GMP 2022, Li groupwise 2023, Dong enhanced 2022, FFIC-EP 2025, FF-VEP 2025). Understanding the message structure here makes all the subsequent papers faster to read.

### What it adds to your analysis
In Section 4, this paper establishes the EP detection baseline for the DBP architecture. Every subsequent EP paper either improves the message fusion rule, the cavity approximation, or the architecture. When you write the EP subsection, this paper is the "standard EP" reference that all improvements are measured against — including your implicit argument that none of them address the covariance inversion under colored noise.

---

## 5. Croisfelt, Abrão, Amiri, de Carvalho, Popovski — Asilomar 2021
**"Decentralized Design of Fast Iterative Receivers for Massive MIMO with Spatial Non-Stationarities"**
55th Asilomar Conference, 2021

**Narrative role:** Section 4 — Kaczmarz/GD family under non-stationary channels; bridges inversion-avoidance and colored noise threads

### The question it answers
*Can gradient descent and Kaczmarz-based decentralized receivers handle spatial non-stationarities — a form of structured channel variation analogous to colored noise — and what modifications are required for convergence in non-ideal channel conditions?*

This is the paper in Pillar A that comes closest to your colored noise problem. Spatial non-stationarities in XL-MIMO introduce structured channel variation across the array that, like colored noise, violates the uniform assumptions underlying standard convergence proofs. The three acceleration methods proposed here (Bayesian receiver, adaptive relaxation, tree extension) are responses to the same challenge your project addresses: inversion-avoidance methods that fail when standard assumptions break.

### What to extract
- The explicit connection between the decentralized GD receiver and the Kaczmarz algorithm — this unifies two families (GD and Kaczmarz) that appear separately in other papers on your list.
- The three acceleration methods and what each one costs computationally: does any of them implicitly introduce a matrix inversion (e.g., the Bayesian receiver that "estimates and eliminates noise")?
- The successive residual cancellation (SRC) principle — how does it differ from standard interference cancellation, and does it require any covariance knowledge?
- The non-stationarity results: how much performance is recovered relative to the stationary channel case? What remains unresolved (the paper explicitly states "non-stationary performance can still be improved")?
- Whether the relaxation parameter selection is related to the condition number of the system matrix — this directly connects to your Phase 5 analysis.

### Points to keep in mind
- Spatial non-stationarities and colored interference noise are mathematically distinct: non-stationarities affect the channel matrix H (different users are visible to different antenna subsets), while colored noise affects R (the noise covariance is non-diagonal). However, both break the assumptions that make standard inversion-avoidance methods well-behaved. This paper demonstrates that the field is aware of the general problem of structured deviation from ideal conditions, even if it addresses a different specific form.
- The connection to the Kaczmarz paper (Wang TSP 2025) is direct and worth making explicit in your review: Croisfelt 2021 identifies the non-stationary convergence problem and proposes heuristic fixes; Wang 2025 provides a rigorous dynamic step-size solution for the stationary colored noise case. Neither paper solves both problems simultaneously.
- The tree-based architecture extension connects to the Seidel binary tree paper (Pillar B) and the Rodríguez Sánchez LIS paper. If the same tree topology appears across multiple papers from different groups, it signals a genuine architectural trend worth one sentence in Section 2.

### What it adds to your analysis
In Section 4, this paper is your strongest bridge between the inversion-avoidance literature and the non-ideal channel thread. Cite it when arguing that structured channel/noise deviation from AWGN is a known problem across the inversion-avoidance family — not just under colored noise specifically — and that no existing solution handles both the decentralized architecture and the full non-ideal channel regime simultaneously.

---

## 6. Li, Dong, Gong, Wang, Dai — IoT Journal 2023
**"Decentralized Groupwise Expectation Propagation Detector for Uplink Massive MU-MIMO Systems"**
IEEE Internet of Things Journal, vol. 10, no. 6, March 2023

**Narrative role:** Section 4 — EP family under correlated channels; closest EP paper to the colored noise regime

### The question it answers
*Can user-grouping within the EP framework recover the performance lost by standard decentralized EP under spatially correlated channels and high overload ratios, and what does the Gaussian product fusion rule require at the CPU?*

This is the most important EP paper for your review because it explicitly addresses performance degradation under correlated channels — the regime closest to your colored noise setting. The groupwise paradigm and the CPU fusion rule are the key technical contributions, and the correlated channel results provide quantitative evidence of what "performance loss under structured interference" actually means in practice.

### What to extract
- The Gaussian product fusion rule at the CPU: the exact mathematical form. Does it require inverting a K×K matrix or a group-size×group-size matrix? The dimension reduction from K to group size is directly analogous to the dimensionality reduction in Zhao et al. 2025's star architecture.
- The EP cavity computation within each group: what precision matrix is inverted per iteration, and what is its dimension relative to the group size?
- The correlated channel results specifically: how much performance is recovered by the groupwise approach relative to standard decentralized EP, and how does it compare to centralized EP?
- The spatial correlation model used — is it a standard exponential correlation matrix, or something structurally similar to your R = βH̄H̄ᴴ + σ²I?
- The daisy-chain extension — the paper covers both star and daisy-chain. Extract the daisy-chain version's message structure and whether it differs from the star in its inversion requirements.

### Points to keep in mind
- The groupwise user division is structurally parallel to the dimensionality reduction in Zhao et al. 2025: both reduce the dimension of the key matrix operation from K to a smaller quantity (group size or compressed dimension L). This parallel is worth making explicit in your review — it shows that the field independently discovered the same dimensionality reduction strategy from two different starting points (EP algorithm design vs. LMMSE equalization matrix design).
- The spatial correlation model (correlated channels between users' antennas) is different from interference covariance (colored noise from inter-cell interference). When you cite this paper in Section 4, state the distinction clearly: the paper addresses antenna correlation, not interference noise; both produce structured non-diagonal matrices but enter the detection problem at different points.
- The AGW-EP approximation (selecting reliable constellation vectors) introduces a different source of performance loss from the inversion approximation. Don't conflate the two in your analysis.

### What it adds to your analysis
In Section 4, this paper is your primary evidence that EP-based decentralized detectors are aware of the correlated channel problem and have proposed partial solutions — but those solutions address antenna spatial correlation, not the interference covariance structure your project targets. In Section 3, it provides quantitative BER evidence for the performance loss that motivates colored noise handling, drawn from the closest related algorithmic family.

---

## 7. Wang, Cheng, Tan, You, Zhang — TCAS-I 2023
**"An Efficient Approximate Expectation Propagation Detector With Block-Diagonal Neumann-Series"**
IEEE Transactions on Circuits and Systems I, vol. 70, no. 3, March 2023

**Narrative role:** Section 4 (Neumann series approximation under correlation) + Section 6 (hardware comparison table, ASIC row)

### The question it answers
*Can a block-diagonal Neumann series approximation replace the exact EP cavity inversion while maintaining acceptable BER performance under both uncorrelated and correlated channels, and what are the silicon implementation costs?*

This is the only paper in Pillar A that simultaneously addresses: (a) EP inversion avoidance, (b) correlated channel performance, (c) Neumann series as the approximation method, and (d) fabricated silicon implementation. This four-way intersection makes it uniquely central to your narrative — it lives in Pillars A and C simultaneously.

### What to extract
- The block-diagonal structure of the Neumann iteration: what determines the block boundaries, and is it the channel spatial correlation structure or a deliberate approximation design choice? This is critical — if the blocks are defined by antenna correlation structure, they may not match the block structure of your interference covariance R.
- The convergence condition for the block-diagonal Neumann iteration: what spectral property of the matrix must hold? How does correlated channel performance degrade relative to uncorrelated, and at what SNR does the 0.3 dB gap appear?
- The 3% normalized complexity claim: what is the baseline (exact EP), and what operations remain in the 3%?
- The ASIC results: 1.252 Gbps/W energy efficiency and 0.275 Mbps/kGE area efficiency on SMIC 65nm. Extract these for your hardware comparison table.
- The 128×32 MIMO benchmark: this is the same system size as the TL-BD-INSA paper (Pillar C), enabling direct comparison.

### Points to keep in mind
- The Neumann series convergence condition requires the matrix to be close to a scaled identity — specifically, the spectral radius of (I - D^{-1}A) must be less than 1, where D is the diagonal or block-diagonal approximation and A is the full matrix. Under your colored noise model, R = βH̄H̄ᴴ + σ²I, the Gram matrix H^H R^{-1} H has a condition number that grows with the interference-to-noise ratio β/σ². This directly violates the Neumann convergence condition at high INR. Your Section 4 can make this argument precisely using the spectral radius criterion from this paper.
- The block structure here is defined by channel correlation (antenna groups with correlated channels), which is different from the block structure induced by your noise covariance. This means even an improved Neumann approximation designed for correlated channels does not automatically transfer to the colored noise setting.
- Compare directly with TL-BD-INSA (Pillar C): same MIMO scale (128×32), different technology (65nm SMIC vs 45nm TSMC ASIC and Virtex-7 FPGA), different algorithmic context (EP-driven vs. pure detection). The comparison table in Section 6 should include both.

### What it adds to your analysis
In Section 4, this paper closes the Neumann series argument: even improved block-diagonal Neumann approximations, implemented in silicon, fail to achieve acceptable BER under colored interference noise because the convergence condition requires near-diagonal-dominance that colored noise destroys. In Section 6, it provides an ASIC data point for the hardware comparison table. The combination — best available Neumann hardware, demonstrated limitation under correlation — is your strongest single argument that exact inversion hardware is necessary.

---

## 8. Wang, Pan, Huang, Jin, Caire — TSP 2025
**"Randomized Iterative Algorithms for Distributed Massive MIMO Detection"**
IEEE Transactions on Signal Processing, vol. 73, 2025

**Narrative role:** Section 4 — Kaczmarz family with strongest theoretical convergence guarantees; most recent rigorous inversion-avoidance result

### The question it answers
*What is the tightest achievable convergence guarantee for Kaczmarz-based distributed massive MIMO detection, and does dynamic step-size selection achieve global convergence regardless of the system matrix's spectral properties?*

This is the theoretically strongest Pillar A paper in your list. MCRBK with dynamic step-size achieves exponential convergence to the linear detection solution with a global convergence guarantee — the best result in the inversion-avoidance literature for distributed detection. Establishing this ceiling is essential for your argument: you must show not just that existing methods fail, but that even the best existing method has a limitation under colored noise.

### What to extract
- The convergence rate bound for MCRBK: does it depend on the spectral properties of H^H H, or of H^H R^{-1} H? If the former, the guarantee is implicitly for AWGN; if the latter, it already incorporates R and may be more general than expected.
- The dynamic step-size mechanism: how is the step size computed at each iteration? Does it require any knowledge of R, or only local channel information? If it requires R^{-1}, the algorithm implicitly contains the inversion it claims to avoid.
- The "global convergence" claim: what exactly does global mean here — convergence from any initialization, or convergence in the large-system limit? This distinction matters for hardware implementation where initialization is not arbitrary.
- The DBP architecture mapping: which topology (star, daisy-chain, ring) does MCRBK naturally fit, and how does the block structure in RBK correspond to antenna clusters?
- The complexity analysis: how many operations per cluster per iteration, and how does this scale with K and the number of clusters?

### Points to keep in mind
- The exponential convergence rate is bounded by the condition number of the system matrix. Even with dynamic step-size, the convergence *rate* (not just the limit) depends on spectral properties that worsen under colored noise. Global convergence means the algorithm eventually reaches the solution; it does not mean it does so within a practical iteration budget when the condition number is high. This is the precise statement of the limitation: MCRBK converges globally but too slowly under high-INR colored noise to meet latency constraints.
- Co-authorship with Caire (a major figure in distributed MIMO) and Jin (co-author on other papers in your list) makes this paper high-visibility. Citing it correctly — as the strongest available inversion-avoidance result, with a well-characterized condition number limitation — signals that you understand the state of the art.
- Compare directly with the BGD paper (Chen et al. ICCT 2025, entry 12): both use dynamic step-size for convergence, BGD on a ring architecture with block structure. The parallel shows that dynamic step-size is converging as a field-wide solution to the convergence problem — strengthening your argument that the field knows about the spectral sensitivity but has not addressed it via hardware inversion.

### What it adds to your analysis
In Section 4, this paper closes the inversion-avoidance narrative with its strongest result. After citing it, you write: "Even with global convergence guarantees and optimal step-size selection, the convergence rate of Kaczmarz-based methods degrades with the condition number of the effective system matrix — a condition number that grows proportionally to the interference-to-noise ratio under colored noise [Wang 2025]. This degradation is not a fixable implementation detail; it is a structural consequence of avoiding the inversion that our hardware directly performs."

---

---

# PRIORITY 2 — Read selectively

---

## 9. Ouameur, Massicotte — EUSIPCO 2019
**"Efficient Distributed Processing for Large Scale MIMO Detection"**
27th European Signal Processing Conference, 2019

**Narrative role:** Section 4 — ADMM-GS hybrid, one paragraph on ADMM family in non-perfect CSI conditions

### The question it answers
*Can embedding a single Gauss-Seidel iteration within each ADMM iteration produce a distributed detector that is both computationally efficient and robust to channel estimation error?*

### What to extract
- The ADMM-GS hybrid update: what each distributed unit computes per iteration, and whether the ADMM consensus step requires any matrix inversion.
- The non-perfect CSI results: how does performance degrade under channel estimation error? This is the closest proxy in the ADMM literature to the colored noise robustness question.
- The comparison against centralized GS: the paper claims ADMM-GS outperforms centralized GS at high SNR. Understand why — it likely exploits the averaging effect of distributed processing.

### Points to keep in mind
- ADMM's consensus step typically requires solving a local linear system, which may involve a K×K inversion. Determine whether this is the case here or whether the Gauss-Seidel embedding eliminates it. If ADMM-GS still contains a local inversion, the paper belongs at the Pillar A/C boundary.
- The non-perfect CSI results are valuable: they show the ADMM family has some robustness to model mismatch, which provides a comparison point for your colored noise analysis. However, channel estimation error (wrong H) and colored noise (wrong R) are different types of mismatch and affect the equalization matrix differently.
- Massicotte also co-authors the Kulkarni Newton method paper (Pillar C). Reading both gives you a consistent hardware perspective from the same group.

### What it adds to your analysis
One paragraph in Section 4's ADMM subsection: the ADMM family provides some robustness to imperfect CSI but the consensus step still requires solving a local linear system whose structure changes under colored noise. This paper provides the non-perfect CSI data point that the other ADMM papers (Chataut 2018) lack.

---

## 10. Chataut, Akl — UEMCON 2018
**"Huber Fitting based ADMM Detection for Uplink 5G Massive MIMO Systems"**
9th IEEE UEMCON, New York, 2018

**Narrative role:** Section 4 — ADMM family, one paragraph; Huber fitting variant for robustness

### The question it answers
*Does replacing the standard least-squares fit in ADMM with a Huber loss function improve BER performance and reduce computational complexity for uplink massive MIMO detection?*

### What to extract
- The ADMM update rule with Huber fitting: what the proximal step looks like and whether it requires a matrix inversion.
- The convergence acceleration method used — what is it, and does it change the inversion structure?
- The BER comparison against standard ADMM and LMMSE: at what SNR does Huber-ADMM outperform standard ADMM, and by how much?

### Points to keep in mind
- This is a conference paper from 2018, predating the decentralized DBP framing. It addresses centralized massive MIMO detection. Its value in your review is limited to showing that the ADMM family has been applied to MIMO detection and that the proximal step typically involves a matrix solve. Don't spend significant reading time on it.
- The Huber loss is designed to be robust to outliers, not to colored noise specifically. The robustness properties are different from what your project needs.

### What it adds to your analysis
One sentence in Section 4's ADMM subsection establishing that ADMM-based detection has been applied to uplink massive MIMO, followed by the note that the proximal step requires a matrix solve whose structure changes under colored noise.

---

## 11. Shafivulla, Patel, Khan — IEEE WCL 2020
**"Low Complexity Signal Detection for Massive-MIMO Systems"**
IEEE Wireless Communications Letters, vol. 9, no. 9, Sept. 2020

**Narrative role:** Section 4 — Cayley-Hamilton approximation; quadratic complexity inversion avoidance

### The question it answers
*Can the Cayley-Hamilton theorem provide an inversion approximation with quadratic (in K) complexity that achieves near-ZF/LMMSE BER performance?*

### What to extract
- The two detection schemes: what polynomial approximation of the inverse does Cayley-Hamilton produce, and what is its computational complexity in terms of K?
- The BER similarity claim relative to ideal ZF/LMMSE: at what SNR does the approximation hold, and where does it break down?
- Whether the Cayley-Hamilton polynomial coefficients depend on the eigenvalue distribution of the Gram matrix — if they do, the approximation quality degrades when the eigenvalue spread increases (which happens under colored noise).

### Points to keep in mind
- This is a short letter (4 pages) addressing centralized detection, not DBP. Its value is as a representative of the polynomial approximation family alongside Neumann series — both approximate the inverse as a polynomial in the Gram matrix, and both degrade when the spectral radius condition fails.
- The Cayley-Hamilton approach is less common in the literature than Neumann series; citing it in Section 4 alongside Neumann shows breadth without requiring deep engagement.

### What it adds to your analysis
One sentence in Section 4's polynomial approximation paragraph: alongside Neumann series, Cayley-Hamilton-based approximations achieve near-ideal BER at quadratic complexity, but the polynomial coefficients depend on the eigenvalue distribution of the Gram matrix, which becomes unfavorable under colored noise interference.

---

## 12. Alegría, Rusek, Sánchez, Edfors — ICC Workshops 2020
**"Trade-Offs in Quasi-Decentralized Massive MIMO"**
IEEE ICC Workshops, Dublin, 2020

**Narrative role:** Section 2 — conference precursor to the WAX TSP 2021 paper; one citation alongside WAX

### The question it answers
*What is the fundamental tradeoff between CPU connections and per-antenna outputs in quasi-decentralized architectures, and does an information-lossless matrix decomposition exist for arbitrary levels of decentralization?*

### What to extract
Only the core tradeoff result and the name of the matrix decomposition introduced. This is the conference seed of the WAX paper — cite only the TSP version in your review, and treat this paper as context.

### Points to keep in mind
This paper is a precursor to the WAX TSP 2021 paper already in your Pillar B Priority 1 list. Do not duplicate reading effort. Cite only the TSP version in your review.

### What it adds to your analysis
No independent citation needed — superseded by WAX TSP 2021.

---

## 13. Zhang, Dong, Long, Wang, Dai — TVT 2022
**"Decentralized Baseband Processing With Gaussian Message Passing Detection for Uplink Massive MU-MIMO Systems"**
IEEE Transactions on Vehicular Technology, vol. 71, no. 2, Feb. 2022

**Narrative role:** Section 4 — GMP detection, message passing family; state evolution framework

### The question it answers
*Can Gaussian message passing (GMP) achieve better decentralized detection performance than EP-based methods, and does a nonuniform cluster partition strategy improve convergence?*

### What to extract
- The GMP message structure: how it differs from EP (GMP uses Gaussian beliefs directly; EP uses moment matching). Does the difference change the per-iteration inversion requirement?
- The state evolution framework: under what assumptions (large-system limit, Gaussian sources) is it valid? Both assumptions are AWGN-compatible and may not extend to colored noise.
- The nonuniform partition result: what makes nonuniform partitions converge faster, and does this depend on the channel statistics?

### Points to keep in mind
- GMP and EP are from the same message passing family but with different approximation strategies. GMP's Gaussian belief assumption is more restrictive than EP's moment matching — it is less robust to non-Gaussian noise. Under colored interference noise, the effective noise seen at each cluster is non-Gaussian, which means GMP's state evolution framework (which assumes Gaussian noise) breaks down more severely than EP's.
- The Zhang group (Zhang, Dong, Li, Wang, Dai) produces multiple papers in your Pillar A list. Reading this paper alongside Zhang TVT 2020 (EP) and Dong TVT 2022 (enhanced EP) as a trio gives you the full progression of this group's work in one reading session.

### What it adds to your analysis
One paragraph in Section 4's message passing subsection: GMP achieves competitive performance through Gaussian belief propagation but its state evolution framework assumes Gaussian noise, making it structurally more sensitive to colored interference than EP-based alternatives.

---

## 14. Dong, Li, Gong, Wang, Dai — TVT 2022
**"An Enhanced Fully Decentralized Detector for the Uplink M-MIMO System"**
IEEE Transactions on Vehicular Technology, vol. 71, no. 12, Dec. 2022

**Narrative role:** Section 4 — enhanced EP with factor graph transformation; performance recovery under large cluster count

### The question it answers
*Can factor graph transformation and a compensation factor recover the performance loss that standard decentralized EP suffers when the number of antenna clusters is large or modulation order is high?*

### What to extract
- The factor graph transformation: how does transforming to a less-loopy graph reduce interference between clusters, and does the transformation require any matrix operation?
- The compensation factor: how is it computed, and does it depend on R or only on H? If it depends on R, note that colored noise changes the compensation value.
- The performance results under large cluster count: how close to centralized EP does the enhanced method get, and at what complexity cost?

### Points to keep in mind
- "Information-lossless factor graph transformation" is a strong claim — verify what lossless means here and whether it assumes AWGN in the factor graph construction.
- The Zhang/Dong/Li group (Zhang TVT 2020, Zhang TVT 2022, Dong TVT 2022, Li IoT 2023) forms a coherent progression. Reading the three TVT/IoT papers together in one session is more efficient than reading each in isolation.

### What it adds to your analysis
One paragraph in Section 4's EP subsection: enhanced factor graph transformation partially recovers performance under large cluster counts but introduces a compensation factor that depends on cluster statistics — a dependency that changes under colored noise interference and has not been analyzed in that regime.

---

## 15. Wang, Kosasih, Wen, Jin, Hardjawana — TWC 2020
**"Expectation Propagation Detector for Extra-Large Scale Massive MIMO"**
IEEE Transactions on Wireless Communications, vol. 19, no. 3, March 2020

**Narrative role:** Section 4 — EP for subarray architecture under spatial non-stationarity; bridge to XL-MIMO thread

### The question it answers
*Can EP be extended to a subarray-based decentralized architecture for extra-large-scale MIMO, and what modifications are needed for convergence under spatially non-stationary channels?*

### What to extract
- The subarray-based EP convergence proof: under what conditions is asymptotic Bayesian optimality achieved?
- The per-iteration inversion at each subarray: dimension and structure of the cavity precision matrix.
- The information exchange reduction strategies: what approximations are used to reduce overhead, and do they change the inversion structure?
- The spatial non-stationarity handling: what assumption about the channel is made, and how does it relate to your colored noise model?

### Points to keep in mind
- Spatial non-stationarity (different antennas see different users) and colored noise (non-diagonal R) are distinct phenomena but both produce structured deviation from the AWGN ideal. This paper is the closest Pillar A paper to bridging both, which makes it useful in Section 4 as a transition toward Section 3.
- The convergence conditions under non-stationarity are likely weaker than under stationary AWGN channels — quantifying this degradation connects to your colored noise argument.

### What it adds to your analysis
One paragraph in Section 4's EP subsection: extending EP to extra-large arrays introduces spatial non-stationarity handling, but the convergence conditions remain sensitive to the channel structure — a sensitivity that colored noise exacerbates through the noise covariance term in the LMMSE formulation.

---

## 16. Zhou, Liang, Zhang, Wen, Jin — TCOMM 2025
**"Mini-Batch Gradient-Based MCMC for Decentralized Massive MIMO Detection"**
IEEE Transactions on Communications, vol. 73, no. 1, Jan. 2025

**Narrative role:** Section 4 — MCMC detection, one paragraph; nonlinear detection family acknowledgment

### The question it answers
*Can gradient-based MCMC — a near-optimal nonlinear detector — be decentralized across antenna clusters with mini-batch SGD to achieve high efficiency?*

### What to extract
- The gradient computation per cluster: does it require H^H R^{-1} y or only H^H y? If R enters, the algorithm implicitly uses covariance information.
- The complexity and delay analysis figures for comparison against linear methods.
- The performance gains over linear decentralized detectors — this quantifies the potential upside of nonlinear detection.

### Points to keep in mind
MCMC is a nonlinear detector that does not compute an equalization matrix. Its value in your review is limited to acknowledging that the detection landscape includes nonlinear methods, and that even these methods benefit from accurate noise covariance information if R enters the gradient. Keep to one paragraph; don't let this paper expand into a detour.

### What it adds to your analysis
One paragraph in Section 4's nonlinear detection acknowledgment: gradient-based MCMC detectors have been decentralized and achieve near-ML performance, but even nonlinear methods require accurate noise modeling — if the gradient incorporates R^{-1}, colored noise still induces an inversion requirement.

---

---

# PRIORITY 3 — One-sentence citation only

---

## 17. Li, Liang, Zhang, Wen, Jin — Comm. Letters 2025
**"Decentralized Feedforward-Feedback Interference Cancellation-Based Detector for M-MIMO Systems"**

**One sentence:** Feedforward-feedback interference cancellation architectures for EP-based DBP detection have been proposed to recover performance at low antenna-to-user ratios [Li 2025a], but the EP cavity inversion requirements remain unaddressed under colored noise.

**Where:** Section 4, EP subsection, after the main EP papers. Introduce before citing the more detailed RIA follow-up paper.

---

## 18. Li et al. — WCL 2025
**"Residual-Impairments-Aware Feedforward-Feedback Detection for Massive MIMO Systems With Decentralized Baseband Processing"**

**Narrative role:** Section 3 (hardware impairments as a source of colored noise) + Section 4 (one paragraph, most recent EP paper)

**One sentence for Section 3:** Hardware impairments — phase noise, IQ imbalance, amplifier nonlinearity — produce residual transceiver noise with non-diagonal covariance structure, constituting a practical source of colored noise distinct from inter-cell interference [Li 2025b].

**One sentence for Section 4:** A residual-impairments-aware VEP detector has been proposed that empirically characterizes transceiver noise covariance [Li 2025b], but the associated covariance inversion required within VEP has not been implemented in hardware.

**Note:** This paper is worth a slightly longer treatment than other Priority 3 entries because it directly connects the colored noise thread (Section 3) to the EP detection thread (Section 4). If your Section 3 has a paragraph on hardware impairments as a source of colored noise, this paper earns two sentences rather than one.

---

## 19. Chen, Wang, Qi, Gao, Huang, Niyato — TWC 2025
**"Decentralized Likelihood Ascent Search-Aided Detection for Distributed Large-Scale MIMO Systems"**

**One sentence:** Nonlinear decentralized detection methods such as likelihood ascent search [Chen 2025] can improve BER beyond linear LMMSE bounds, but they require a linear MMSE initialization that itself depends on the noise covariance inversion your hardware implements.

**Where:** Section 4, final paragraph before the section conclusion, as evidence that even nonlinear improvements to decentralized detection are downstream of the linear inversion your project provides.

---

## 20. Chen, Chen, He, Wang — ICCT 2025
**"Block Gradient Descent Algorithm for Distributed Detection in Massive MIMO"**

**One sentence:** Block gradient descent with dynamic step size on a ring architecture [Chen 2025b] converges to the linear detection solution but shares the condition number sensitivity of the broader gradient descent family under colored noise.

**Where:** Section 4, gradient descent subsection, after the main Sánchez TSP 2020 and Croisfelt Asilomar 2021 citations. Pairs naturally with Wang TSP 2025 to show that dynamic step-size has independently emerged across multiple groups as the response to convergence problems — yet the condition number limitation remains.

---

## 21. Zheng, Gao, Cui, Wang, Huang — ICCT 2022
**"Decentralized Recursive MMSE Equalizer for Massive MIMO Systems"**

**Note:** This paper is already classified as Pillar B Priority 1 and appears in the Pillar B reading guide. Do not duplicate in Pillar A. If your Pillar A list includes it, treat the Pillar B annotation as authoritative and cite it in Section 4 only to connect the recursive detection and recursive equalization threads.

---

---

# The Chronological Narrative Arc for Section 4

Section 4 of your review ("Inversion Avoidance Under AWGN — Strategies and Limitations") should be organized by algorithm family rather than chronologically, but within each family the chronological order below shows how each family developed and where its AWGN dependency crystallized.

| Year | Paper | Family | Argument carried forward |
|------|-------|--------|--------------------------|
| 2018 | Sánchez SiPS | Recursive/GD | Inversion avoidance demonstrated; ZF achieved without inversion hardware |
| 2018 | Chataut UEMCON | ADMM | ADMM proximal step applied to MIMO detection; implicit local solve |
| 2019 | Li ISCAS | Coord. descent | CD decentralized with GPU; half-precision results; preprocessing inversion deferred |
| 2019 | Ouameur EUSIPCO | ADMM-GS | ADMM-GS robust to imperfect CSI; local solve remains |
| 2020 | Sánchez TSP | Coord. descent / Kaczmarz | Full theory; convergence bound tied to condition number |
| 2020 | Wang TWC | EP subarray | EP for XL-MIMO under non-stationarity; cavity inversion deferred |
| 2020 | Zhang TVT | EP | EP baseline for DBP; message fusion rule; cavity inversion present |
| 2020 | Shafivulla WCL | Polynomial approx. | Cayley-Hamilton; quadratic complexity; eigenvalue-dependent coefficients |
| 2020 | Alegría ICC | Quasi-decentralized | WAX precursor; lossless decomposition under AWGN |
| 2021 | Croisfelt Asilomar | GD / Kaczmarz | Non-stationarity handled partially; convergence still condition-number sensitive |
| 2022 | Zhang TVT | GMP | State evolution under Gaussian/AWGN; breaks under non-Gaussian noise |
| 2022 | Dong TVT | EP enhanced | Factor graph transformation recovers performance; compensation factor depends on statistics |
| 2023 | Li IoT | EP groupwise | Correlated channels handled; spatial correlation ≠ interference covariance |
| 2023 | Wang TCAS-I | Neumann-EP hybrid | Block-diagonal Neumann in silicon; convergence fails under high INR |
| 2025 | Zhou TCOMM | MCMC | Near-ML nonlinear detection decentralized; gradient may require R^{-1} |
| 2025 | Li Comm. Letters | FFIC-EP | Feedforward-feedback improves EP; cavity inversion unaddressed |
| 2025 | Li WCL | RIA-VEP | Hardware impairments as colored noise source; covariance inversion in VEP |
| 2025 | Wang TSP | MCRBK | Strongest convergence guarantee; rate still bounded by condition number |
| 2025 | Chen TWC | DLAS | Near-ML nonlinear aided by linear init; init requires R-dependent inversion |
| 2025 | Chen ICCT | BGD | Dynamic step-size on ring; condition number sensitivity persists |

**The section-closing argument** that these papers collectively support: across every inversion-avoidance family — recursive, ADMM, coordinate descent, EP, GMP, Kaczmarz, MCMC — the performance guarantee either explicitly assumes AWGN or implicitly depends on spectral properties of the system matrix that degrade under colored noise. The 2025 papers pushing the state of the art (Wang TSP, Li WCL, Chen TWC) are the strongest available results, and they confirm rather than resolve the limitation. The inversion your hardware implements is not an engineering choice that could be designed away; it is the structural consequence of removing the AWGN assumption.

---

*Guide prepared for Computer Engineering FYP: FPGA Implementation of Matrix Inversion for Decentralized LMMSE Equalization in Massive MIMO under Colored Noise.*
