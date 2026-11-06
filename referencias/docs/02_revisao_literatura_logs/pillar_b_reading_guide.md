# Pillar B — Equalization Matrix Design
## Annotated Reading Guide: Priorities, Questions Answered, and Narrative Placement

*For: FPGA Implementation of Matrix Inversion for Decentralized LMMSE Equalization in Massive MIMO under Colored Noise*

---

## How to use this guide

Each entry is structured as follows:

- **Priority** and **venue/year**
- **Narrative role** — where this paper lives in your review's story
- **The question it answers** — the specific gap in your understanding that this paper fills
- **What to extract** — the concrete items to note when reading
- **Points to keep in mind** — traps, nuances, and connections to watch for
- **What it adds to your analysis** — the sentence-level contribution to your argument

Papers are ordered chronologically within priority tiers, reflecting the reading order that builds the narrative most efficiently.

---

---

# PRIORITY 1 — Read in full, in this order

---

## 1. Jeon, Li, Cavallaro, Studer — TSP 2019
**"Decentralized Equalization With Feedforward Architectures for Massive MU-MIMO"**
IEEE Transactions on Signal Processing, vol. 67, no. 17, Sept. 2019

**Narrative role:** Section 2 (background, canonical feedforward architecture) + Section 4 (AWGN equalization methods) + Section 5 (direct predecessor to anchor paper)

### The question it answers
*What does the state-of-the-art decentralized equalization system look like before colored noise is considered, and what are its precise performance and complexity characteristics?*

This paper defines the baseline that your entire review measures everything else against. It is the paper your 2025 anchor paper extends, and every limitation you identify here becomes a motivation for your project.

### What to extract
- The exact form of the local equalization matrices at each cluster for ZF, L-MMSE, and MRC — specifically what each cluster computes locally and what is communicated to the fusion node.
- The fusion step for each algorithm — what operation is performed at the central unit, and does it involve any matrix inversion? What is its dimension?
- The post-equalization SINR expressions for each algorithm under each architecture — these are the performance benchmarks your hardware must match.
- The two feedforward architectures: what distinguishes them in terms of interconnect requirements, and which one corresponds to the star architecture in Zhao et al. 2025?
- GPU throughput figures — even as a Pillar B paper, these establish the computational regime you are targeting.
- The AWGN assumption — where exactly does it appear in the derivation? Is it in the noise model for the SINR expression, in the structure of the equalization matrix, or both?

### Points to keep in mind
- This paper has four co-authors who appear across multiple papers on your list (Li, Cavallaro, Studer). Understanding their architectural vocabulary here unlocks all the papers from that group.
- The AMP algorithm is included alongside ZF and L-MMSE. AMP is an inversion-avoidance method (Pillar A), but its appearance here in a Pillar B paper means the feedforward architecture is algorithm-agnostic. Note this: the architecture and the algorithm are separable design choices, and your hardware contribution addresses the inversion required by L-MMSE specifically within this architecture.
- The "no or only a small performance loss" claim relative to centralized solutions is made under AWGN. This qualification is implicit but critical — it is the gap your project exists to address.

### What it adds to your analysis
This paper provides the canonical definition of feedforward DBP equalization. In Section 4, you cite it to establish the AWGN baseline performance and the precise form of the equalization matrix your hardware must compute. In Section 5, you cite it as the work that Zhao et al. 2025 directly extends. In Section 2, it anchors the architectural description of the star topology.

---

## 2. Li et al. (K. Li group) — Asilomar 2019
**"Design Trade-offs for Decentralized Baseband Processing in Massive MU-MIMO Systems"**
53rd Asilomar Conference, 2019

**Narrative role:** Section 2 (practical design guidelines) + Section 5 (motivation for hardware analysis)

### The question it answers
*What are the practical engineering tradeoffs — error rate, complexity, latency, numerical precision — that a designer must navigate when choosing a DBP architecture and algorithm?*

This paper is the practical companion to the theoretical TSP 2019 paper. Where Jeon et al. proves things work under AWGN, this paper tells you how well and at what cost.

### What to extract
- The tradeoff framework: how do error-rate performance, computational complexity, and data transfer latency vary as you change the DBP architecture, the algorithm, and the system configuration?
- The numerical precision analysis — this is the most directly relevant section for your project. What word lengths are evaluated? What precision loss is acceptable at what SNR? Does the paper quantify the degradation from finite-precision arithmetic?
- The practical guidelines for selecting DBP architecture and algorithm — do these guidelines assume AWGN throughout? This is your colored noise gap in the practical design space.
- Any results on how performance degrades as the number of clusters increases — this connects to Zhuang et al. 2025's theorem that SINR decreases with cluster count.

### Points to keep in mind
- This is a conference paper from the same group as Jeon TSP 2019, likely based on the same codebase. Cross-reference the system parameters to confirm consistency.
- The numerical precision results, if present, are almost certainly under AWGN. The condition number under colored noise (which drives precision requirements) will be higher, meaning the word lengths this paper recommends may be insufficient for your setting — this is a direct contribution your project makes beyond this paper's scope.
- "Numerical precision" in this context likely means fixed-point simulation, not analytical condition number bounds. Your Phase 5 analysis adds the analytical dimension.

### What it adds to your analysis
In Section 2, this paper provides the engineering rationale for why hardware implementation choices matter — it is not enough to show an algorithm works; you must show it works at acceptable precision and latency. In Section 7, it defines the prior art on precision analysis that your project extends to the colored noise regime.

---

## 3. Sánchez, Alegría, Rusek — ISIT 2019
**"Decentralized Massive MIMO Systems: Is There Anything to be Discussed?"**
IEEE ISIT, Paris, 2019

**Narrative role:** Section 3 (why inversion is structurally unavoidable) + Section 4 (theoretical boundary of inversion-avoidance)

### The question it answers
*Is matrix inversion fundamentally unavoidable in decentralized ZF/MMSE detection, or can it always be distributed away?*

This paper provides the theoretical answer: for zero-forcing in a fully decentralized setting where no single node sees the full channel matrix, a matrix inversion is still required at a processing node. This is the strongest theoretical motivation for your hardware contribution.

### What to extract
- Feature (v) from the abstract: what is the exact form of the matrix inversion required at the processing node for ZF? What is its dimension?
- The noise model assumed — is R diagonal (AWGN) or general? If AWGN, note explicitly that the inversion structure may change under colored noise.
- The channel estimation problem (feature iv) — understand its structure enough to confirm it is out of scope for your project, but check whether the statistic passed to the processing node is a sample covariance. If so, it connects to your interference covariance estimation thread.
- Whether MMSE is also analyzed and whether its inversion has a different structure from ZF's.

### Points to keep in mind
- The paper's title is deliberately provocative — "is there anything to be discussed?" The answer it gives is yes, because ideal CSI assumptions hide real implementation problems. This rhetorical structure can be borrowed for your Section 3 opening.
- This is a theory paper (ISIT venue). It will not give you hardware metrics, and its proofs may be dense. You need the conclusion, not the full proof.
- The Sánchez/Rusek/Edfors group takes a different approach to decentralization than the Li/Studer group — no cluster aggregation, no central CPU for detection. Understanding this difference clarifies why your review covers multiple decentralization paradigms even though your project targets one specific architecture.

### What it adds to your analysis
In Section 3, this paper provides the theoretical anchor for your claim that matrix inversion is unavoidable. It lets you write: "Even in fully decentralized settings where no node holds the full channel matrix, a matrix inversion remains structurally required [Sánchez 2019] — and the form of that inversion changes under colored noise in ways no existing hardware implementation addresses."

---

## 4. Alegría, Rusek, Edfors — TSP 2021
**"Trade-Offs in Decentralized Multi-Antenna Architectures: The WAX Decomposition"**
IEEE Transactions on Signal Processing, vol. 69, 2021

**Narrative role:** Section 2 (unifying theoretical framework for DBP architectures)

### The question it answers
*Is there a single mathematical framework that captures all possible tradeoffs between level of decentralization and per-antenna complexity, and what are the fundamental limits of information-lossless decentralized processing?*

The WAX decomposition answers this by parameterizing the entire centralized-to-decentralized spectrum through two variables. Every specific architecture in your review (star, daisy-chain, ring, binary tree) is a point in the WAX design space.

### What to extract
- The WAX decomposition definition: what are W, A, and X, and what operation does each require? Does computing any factor require a matrix inversion, and of what dimension?
- The two design parameters (connections to CPU and multiplications/outputs per antenna) — these become your architectural comparison axes in Section 2.
- The information-lossless condition — under what mathematical assumptions on the channel and noise is lossless processing achievable? Is R required to be diagonal?
- The limitations section — what does the paper itself identify as unsolved? This is your colored noise gap stated from the perspective of the most general existing framework.

### Points to keep in mind
- This is a TSP journal paper — read it carefully but selectively. The framework section and the limitations section are essential; the detailed proofs of the achievability bounds are not.
- The fact that LIS appears in the keywords alongside massive MIMO means the WAX framework is intentionally general enough to cover both. This is useful for positioning your review's scope: you are targeting one specific region of the WAX design space (the DBP star/daisy-chain region), not the full space.
- If the information-lossless condition requires diagonal R, this is the most powerful single sentence for your Section 3: the most general existing framework for decentralized processing is lossless only under AWGN.

### What it adds to your analysis
In Section 2, WAX provides a unifying language for describing all DBP architectures without enumerating them separately. This lets you write a compact background section that positions the star and daisy-chain architectures as specific instances of a general framework, then zoom in on the colored noise problem that affects all instances in the same way.

---

## 5. Zhao, Guan, Li, Shi — GLOBECOM 2021
**"Decentralized Linear MMSE Equalizer Under Colored Noise for Massive MIMO Systems"**
IEEE GLOBECOM, Madrid, 2021

**Narrative role:** Section 5 (originating contribution, daisy-chain colored noise) — read alongside your anchor paper

### The question it answers
*Can the BCD-based L-MMSE equalization under colored noise be derived for the daisy-chain architecture, and what does the per-iteration inversion look like in that compressed form?*

This conference paper is the seed of your anchor paper. Reading it before the full JSAC 2025 paper gives you the core BCD derivation in its most compressed, transparent form — before the journal expansion added the star architecture, dimensionality reduction, and low-rank decomposition.

### What to extract
- The BCD derivation for the daisy-chain: what is the per-iteration update rule, and what matrix inversion does it require? What is the dimension of that inversion?
- The colored noise model used — is it R = βH̄H̄ᴴ + σ²I, or a more general form? Does the paper define R explicitly?
- Which equations appear identically in the JSAC 2025 paper and which are simplified here — this tells you what is original to the conference vs. what was added in the journal.
- The performance gap between the proposed method and centralized LMMSE — at what SNR and for what system size?

### Points to keep in mind
- Read this paper with the JSAC 2025 paper open beside it. Your goal is not to understand this paper independently but to understand what the journal added. The conference paper covers only the daisy-chain; the star architecture and DR techniques are journal contributions.
- The BCD derivation here is your project's mathematical kernel in its simplest form. If the derivation is unclear in the journal paper, this version may be easier to follow.
- The AWGN assumption in all prior work is stated explicitly here as a motivation — this is the clearest statement of the gap your thesis fills, in the paper most directly connected to your work.

### What it adds to your analysis
In Section 5, cite this alongside the JSAC 2025 paper to show the research has a development history. The conference version establishes that the colored noise problem was identified and partially solved in 2021; the journal version completed the solution. Your hardware contribution is the next step in this progression.

---

## 6. Zheng, Gao, Cui, Wang, Huang — ICCT 2022
**"Decentralized Recursive MMSE Equalizer for Massive MIMO Systems"**
IEEE ICCT, Nanjing, 2022

**Narrative role:** Section 4 (chain architecture equalization under AWGN, direct predecessor to BCD)

### The question it answers
*Before BCD, what was the state of the art for MMSE equalization on the chain architecture, and what was its fundamental limitation?*

This paper is the "before" in the before/after pair that your Section 4→5 transition needs. It shows recursive MMSE converging to the centralized MMSE solution on the chain under AWGN, which is exactly what Zhao et al. 2025 extends to colored noise.

### What to extract
- The recursive update rule at each chain node: what operation is performed, and what matrix inversion does it require? Is it a rank-one Woodbury update or a full local solve?
- The early termination condition based on channel quality — what channel property does it rely on? If it is channel hardening (which requires AWGN or near-diagonal noise), this becomes your limitation statement.
- The convergence proof structure — what assumptions on the system matrix does the proof require?
- The BER comparison against existing decentralized equalizers — which methods does it beat and by how much?

### Points to keep in mind
- This is a short conference paper (5 pages). Extract the key equations and the convergence condition; don't expect full proofs.
- The recursive update structure (rank-one or rank-k Woodbury) is a different inversion family from the full K×K solve in BCD. If confirmed, this gives your Section 6 an additional inversion variant for the chain architecture that you can compare against your target operation.
- The early termination strategy is practically important: it means the number of chain steps (and therefore the total latency) is adaptive. Under colored noise, when convergence is slower, early termination triggers later — increasing latency. This is a non-obvious consequence of the colored noise problem that your Section 3 can mention.

### What it adds to your analysis
In Section 4, this paper closes the chain architecture story under AWGN: recursive MMSE achieves centralized performance but requires channel hardening, which fails under colored noise. In Section 5, the contrast with BCD — which doesn't require channel hardening — is your sharpest statement of what the 2025 paper's contribution actually is.

---

## 7. Chen, Wang, Ma, Dai, Ng — TVT 2024
**"General Recursive Least Square Algorithm for Distributed Detection in Massive MIMO"**
IEEE Transactions on Vehicular Technology, vol. 73, no. 8, Aug. 2024

**Narrative role:** Section 4 (recursive detection family, chain architecture, explicit convergence condition)

### The question it answers
*What is the precise mathematical condition under which a recursive distributed detection algorithm on the chain converges, and what does that condition tell us about the colored noise regime?*

This paper is the most analytically explicit about convergence conditions among all the chain-architecture papers. The inequality C₀ ≥ ⌊(√(B/2)+√K)²/B⌋ is a directly quotable result that connects channel hardening to the minimum number of "full-complexity" nodes required for convergence — and channel hardening is exactly what breaks under colored noise.

### What to extract
- The GRLS update rule: is the rank-B update to the inverse matrix implemented via Woodbury, or a direct solve? What is the computational cost per step?
- The convergence condition in full: C₀ ≥ ⌊(√(B/2)+√K)²/B⌋. What does C₀ represent physically? What happens to this bound when channel hardening weakens (as under colored noise)?
- The distinction between the C₀ "full-complexity" nodes and the C−C₀ "reduced-complexity" nodes — what operation do the reduced nodes skip, and why can they skip it only under channel hardening?
- Complexity and bandwidth cost analysis figures — these go in your comparison notes even if not directly in your hardware table.

### Points to keep in mind
- The channel hardening property is a large-system approximation that becomes exact only as M→∞ with K fixed. Under colored noise (interference-limited regime), the effective channel hardening weakens even for large M, because the interference term βH̄H̄ᴴ introduces structured correlation that the hardening approximation cannot absorb. This is the analytical argument that the convergence guarantee of GRLS fails under your target noise model.
- The bound C₀ ≥ ⌊(√(B/2)+√K)²/B⌋ gives you a quantitative handle: under colored noise, more nodes need to be in the "full-complexity" set, increasing the total inversion burden rather than reducing it. This is a precise, citable argument for why colored noise makes the inversion problem harder, not just different.
- Compare this paper's RLS structure with the Zheng et al. recursive MMSE paper. Both are recursive on the chain; the difference is the algorithm (RLS vs. MMSE update) and the multi-antenna generalization. Together they show that the entire family of recursive chain algorithms shares the same channel hardening dependency.

### What it adds to your analysis
In Section 4, this paper provides the most precise statement of the AWGN dependency among all chain-architecture papers. The convergence condition becomes a direct setup for your Section 5 argument: Zhao et al. 2025's BCD approach is not just an extension to colored noise but a fundamentally different formulation that removes the channel hardening requirement entirely, at the cost of requiring an explicit matrix inversion — which your hardware implements.

---

## 8. Zhao et al. — JSAC 2025 (your anchor paper)
**"Efficient LMMSE Equalization for Massive MIMO Systems Under Decentralized Baseband Processing Architecture"**
IEEE Journal on Selected Areas in Communications, vol. 43, no. 3, March 2025

**Narrative role:** Section 5 (primary technical reference) — already annotated in Phase 1 of the guide

*(Listed here for completeness in the chronological sequence. Refer to your Phase 1 annotation for the full extraction plan.)*

### The single most important thing to keep in mind
Everything in Pillars A, B, and C of your review is either a predecessor that this paper supersedes (algorithmically) or a context within which your hardware contribution sits (implementationally). Read every other paper asking: "what does this paper not do that the 2025 paper does?" The answer is always the same: it does not handle colored noise with a hardware-implementable inversion. That gap is your project.

---

## 9. Zhuang, Zhang, Xu, Song, Eldar — JSTSP 2025
**"Decentralized MIMO Systems With Imperfect CSI Using LMMSE Receivers"**
IEEE Journal of Selected Topics in Signal Processing, vol. 19, no. 2, March 2025

**Narrative role:** Section 5 (theoretical envelope for LMMSE under correlation) + Section 7 (performance targets and architectural constraints)

### The question it answers
*What is the theoretical SINR achievable by decentralized LMMSE receivers under general spatial correlation and imperfect CSI, and what does random matrix theory tell us about the precision and architecture required to approach that bound?*

This paper provides the performance ceiling your hardware implementation must target. Without it, your Section 7 can only say "our hardware achieves X BER" — with it, you can say "our hardware operates within Y dB of the theoretical SINR bound under colored noise conditions."

### What to extract
- The optimal linear fusion scheme: its exact matrix form, what inversion it requires, and at what node (central unit or distributed clusters). The dimension of this inversion is the most important single number to extract from this paper.
- The two suboptimal fusion schemes and their complexity reductions — specifically, do they reduce the inversion dimension, and under what conditions are they optimal?
- The conditions under which the suboptimal schemes achieve the same SINR as the optimal — these conditions define the boundary of when your hardware's full inversion capability is necessary vs. when approximation suffices.
- The optimal regularization parameter result — this is the analytically derived value for your hardware evaluation scenarios. Using it in your fixed-point experiments connects your hardware analysis to established theory rather than ad-hoc parameter choices.
- The theorem that SINR decreases as the number of clusters increases — what is the rate of decrease, and how does it depend on the noise covariance structure?

### Points to keep in mind
- This paper uses random matrix theory extensively. You do not need to follow the RMT proofs, but you need the results: the SINR expressions, the optimal regularization parameter, and the suboptimality conditions. Read the theorem statements and their interpretations; skip the proofs.
- The "general spatial correlation" in this paper and the "colored noise" in your anchor paper are mathematically related but not identical. Spatial correlation enters through the channel matrix H; colored noise enters through R in the equalization matrix. Both produce non-diagonal covariance structure, and the inversion structure in both cases is a K×K or compressed-dimension Hermitian positive semi-definite matrix. Note this connection explicitly when you write Section 5.
- Eldar is a co-author — this signals a compressed sensing / random matrix theory perspective that complements the optimization-based approach of the Zhao/Shi group. The two 2025 papers together represent the current theoretical frontier for your problem.

### What it adds to your analysis
In Section 5, this paper defines what "optimal" means for decentralized LMMSE under colored noise — giving your hardware a target to aim at. In Section 7, the optimal regularization parameter and the SINR-clusters tradeoff provide the theoretical constraints within which your FPGA must operate. Without this paper, your contribution is "we implemented an inversion"; with it, your contribution is "we implemented the inversion required to approach the theoretical SINR bound under colored noise."

---

---

# PRIORITY 2 — Read selectively

---

## 10. Liu, Liu, Yan, Wu — SiPS 2019
**"A Distributed Detection Algorithm For Uplink Massive MIMO Systems"**
IEEE SiPS Workshop, Nanjing, 2019

**Narrative role:** Section 4 (early daisy-chain detection under channel hardening, one paragraph)

### The question it answers
*What was the earliest explicit use of channel hardening to enable distributed detection on the daisy-chain architecture?*

### What to extract
Only two things: (1) how channel hardening is used to simplify the distributed detection update, and (2) the performance-complexity tradeoff claim. Both can be extracted from the abstract and the results section in under 15 minutes.

### Points to keep in mind
This is a short workshop paper. Its value is historical placement in the chronological narrative — it establishes that the channel hardening approach to daisy-chain detection predates the recursive MMSE and GRLS papers. Do not spend more than 20 minutes on it.

### What it adds to your analysis
One sentence in Section 4: early daisy-chain detection exploited channel hardening to simplify distributed updates, an approach that later recursive methods (Zheng 2022, Chen 2024) generalized — all sharing the AWGN-regime dependency that Zhao 2025 removes.

---

## 11. Alegría, Rusek — ICC 2022
**"Enabling Decentralized Computation of the WAX Decomposition"**
IEEE ICC, Seoul, 2022

**Narrative role:** Section 2 (one sentence following the WAX TSP citation)

### The question it answers
*Can the WAX decomposition itself be computed in a decentralized fashion, or does it require a centralized computation step?*

### What to extract
Only the answer to the above question and the computational structure of the decentralized basis matrix construction. Read only after finishing the WAX TSP 2021 paper.

### Points to keep in mind
If the decentralized computation of W requires any local matrix inversion, note the dimension — this is an additional inversion instance for your landscape. But this is a secondary observation; the paper's primary value is confirming the WAX framework is practically realizable.

### What it adds to your analysis
One sentence in Section 2: the WAX decomposition can be computed decentrally, confirming that information-lossless decentralized processing is not just theoretically achievable but computationally realizable — within the AWGN regime.

---

## 12. Cui, Zhang, Wang, Gao — VTC 2023
**"Decentralized Bidirectional-Chain Equalizer for Massive MIMO"**
IEEE VTC Spring, Florence, 2023

**Narrative role:** Section 4 (chain architecture design space, parallel update variant)

### The question it answers
*Can the latency bottleneck of sequential chain processing be resolved through bidirectional parallel updates, and does the inversion structure change when processing is parallelized?*

### What to extract
- The per-cluster operation in the parallel update — what matrix operation is performed, and does the bidirectional structure change its dimension compared to the unidirectional case?
- The BER comparison against sequential chain methods — does parallel processing achieve the same BER at lower latency, or is there a performance tradeoff?
- The noise model — AWGN throughout, or is any generalization mentioned?

### Points to keep in mind
The parallel update structure may change the local inversion from a sequential rank-one update to a full local solve — check this. If so, the bidirectional chain requires a larger per-cluster inversion than the sequential chain, which has implications for your hardware design that are worth one sentence in Section 7.

### What it adds to your analysis
In Section 4, it completes the chain architecture design space: unidirectional sequential (Zheng 2022), recursive generalized (Chen 2024), and bidirectional parallel (Cui 2023) — all under AWGN, all superseded by Zhao 2025 for the colored noise case. The three papers together make the argument that the AWGN limitation is pervasive across all chain architecture variants, not an artifact of any single design.

---

## 13. Xu, Zhu, Shi, Chang — TSP 2024
**"Joint Compression and Multiuser Equalization for Multi-Carrier Massive MIMO Systems With Decentralized Baseband Processing"**
IEEE Transactions on Signal Processing, vol. 72, 2024

**Narrative role:** Section 5 (complementary compression approach) + Section 7 (multi-carrier as open direction)

### The question it answers
*Can the dimensionality reduction / compression approach to DBP equalization be extended to multi-carrier systems, and what inversion does the joint compressor-equalizer design require?*

### What to extract
- The compressor design: what matrix inversion does the joint MC-JCDE optimization require, and at what node (distributed BBU or central unit)?
- How BCD handles the cross-subcarrier coupling — does each BCD iteration require a per-subcarrier inversion, and if so what is its dimension relative to single-carrier K×K?
- The noise model — AWGN or colored? If AWGN, note explicitly as a gap.
- The fronthaul bandwidth reduction achieved by compression — compare against the DR techniques in Zhao et al. 2025.

### Points to keep in mind
- Read the SPAWC 2024 conference version abstract first to confirm the TSP journal version is strictly a superset; then read only the TSP version. The conference version can be cited as a reference but the journal version supersedes it.
- The cross-subcarrier coupling is the key technical challenge unique to this paper. If BCD decouples the subcarriers at each iteration, the per-subcarrier inversion dimension is the same as the single-carrier case — in which case your hardware is directly applicable to the multi-carrier setting. If not, the multi-carrier inversion is larger, and that is a contribution boundary to state in Section 7.
- This paper is from the same Chang group as your anchor paper. The two papers are complementary: Zhao et al. 2025 addresses colored noise in single-carrier; this paper addresses multi-carrier under AWGN. The intersection — multi-carrier + colored noise — is genuinely open.

### What it adds to your analysis
In Section 5, it shows that compression-based DBP equalization extends naturally to multi-carrier, using the same BCD framework as your anchor paper. In Section 7, it defines the multi-carrier colored noise inversion problem as an open direction your project does not address — a clean scope boundary that avoids overpromising.

---

---

# PRIORITY 3 — One-sentence citation, no dedicated reading time

---

## 14. Alegría, Sánchez, Rusek, Liu, Edfors — VTC 2019
**"Decentralized Equalizer Construction for Large Intelligent Surfaces"**

**One sentence:** Fully decentralized ZF equalization has been studied for LIS topologies through neighbor-only message passing [Alegría 2019], but the LIS system model and channel structure differ fundamentally from the DBP cluster model addressed here.

**Where:** Section 2, footnote or parenthetical acknowledging alternative decentralization topologies.

---

## 15. Seidel, Paul, Rust — Asilomar 2019
**"Decentralized Massive MIMO Uplink Signal Estimation by Binary Multistep Synthesis"**

**One sentence:** Binary tree fusion topologies have also been proposed for decentralized equalization [Seidel 2019], offering reduced latency through hierarchical aggregation but sharing the AWGN-assumption dependency of other non-colored-noise methods.

**Where:** Section 4, parenthetical in the architecture diversity paragraph.

---

## 16. Zhao, Gao, Liang, Shi — ICCC 2025
**"A Star-Chain Hybrid Decentralized Baseband Processing Architecture for XL-MIMO Systems"**

**One sentence:** Hybrid star-chain architectures have recently been proposed to combine the advantages of both topologies [Zhao 2025b], introducing additional inversion design choices beyond the scope of this project.

**Where:** Section 7, scope boundary paragraph.

---

## 17. Xu, Zhu, Shi, Chang — SPAWC 2024
**"Fronthaul-Efficient Multiuser Equalization for Multi-Carrier Massive MIMO Systems with Decentralized Baseband Processing"**

**Action:** Do not cite independently. This conference paper is fully superseded by the TSP 2024 journal version (entry 13 above). Cite only the TSP version.

---

---

# The Chronological Narrative Arc

The table below shows how the Priority 1 and 2 papers map onto your review sections, with the argument each paper carries forward.

| Year | Paper | Argument carried forward |
|------|-------|--------------------------|
| 2019 | Jeon et al. TSP | Feedforward DBP works under AWGN — baseline defined |
| 2019 | Li et al. Asilomar | Practical tradeoffs are understood, precision matters — hardware problem is real |
| 2019 | Sánchez et al. ISIT | Inversion is structurally unavoidable even in fully decentralized ZF |
| 2019 | Liu et al. SiPS | Earliest chain detection uses channel hardening — dependency established early |
| 2021 | Alegría et al. TSP | WAX gives theoretical limits of decentralized processing — lossless only under AWGN |
| 2021 | Zhao et al. GLOBECOM | Colored noise problem identified, BCD solution derived for daisy-chain |
| 2022 | Alegría, Rusek ICC | WAX computation is realizable — AWGN assumption persists |
| 2022 | Zheng et al. ICCT | Recursive MMSE on chain converges under AWGN — channel hardening dependency |
| 2023 | Cui et al. VTC | Bidirectional parallel chain reduces latency — AWGN assumption persists |
| 2024 | Chen et al. TVT | Convergence condition quantified — breaks under colored noise |
| 2024 | Xu et al. TSP | Multi-carrier compression works under AWGN — colored noise gap in multi-carrier |
| 2025 | Zhao et al. JSAC | Complete colored noise solution for both architectures — **hardware gap opened** |
| 2025 | Zhuang et al. JSTSP | Theoretical SINR bounds under correlation — **performance target defined** |

The narrative reads: the field spent 2019–2024 perfecting decentralized equalization under AWGN, with progressively more sophisticated algorithms and tighter convergence guarantees, all resting on an assumption the 2025 papers finally remove. The hardware gap is not an oversight — it was invisible until the algorithmic solution existed. Your project is the natural next step.

---

*Guide prepared for Computer Engineering FYP: FPGA Implementation of Matrix Inversion for Decentralized LMMSE Equalization in Massive MIMO under Colored Noise.*
