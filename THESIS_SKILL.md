# SKILL — Thesis Writing Assistant
## Hardware Accelerator for Matrix Inversion in Decentralized Massive MU-MIMO LMMSE Equalization Under Colored Noise
**Author:** Juliana R. de Vargas — UFRGS, Instituto de Informática
**Template:** SBC (`sbc-template.sty`), 12 pt, `babel/american`, UTF-8

---

## 1. What this skill is for

Read this file before assisting with **any** writing, editing, or review task on this thesis. It encodes the research context, the complete notation system, the full citation inventory, the document structure, and the methodological constraints that must be respected at all times.

---

## 2. Research identity

### 2.1 One-sentence research statement
This work proposes and evaluates an **FPGA hardware accelerator** for the **local $M_c \times M_c$ Hermitian matrix inversion** required by each distributed unit (DU) once per coherence block in the **BCD-MMSE** algorithm (Zhao et al., IEEE JSAC 2025), which is the **first decentralized LMMSE equalizer for Massive MU-MIMO operating under colored noise**.

### 2.2 Research gap (triple conjunction — all three must be present to define the gap)
No prior work simultaneously addresses:
1. **Colored noise** (non-diagonal $\mathbf{R}_n$) in the receiver model;
2. **Decentralized baseband processing (DBP)** architecture;
3. **FPGA/ASIC hardware implementation** with measured resource metrics (LUT count, power).

### 2.3 Contributions
| Contribution | Metric |
|---|---|
| Signal quality | BER vs. SNR curves |
| Resource usage | LUT count, DSP48 blocks, BRAM |
| Power | On-chip power (W) |

### 2.4 Target algorithm — BCD-MMSE (Zhao et al. 2025, IEEE JSAC)
- **Architecture:** Daisy-chain DBP (equivalent to ring topology in Kulkarni et al.).
- **Key per-DU operation (Eq. 30 of Zhao et al. 2025):** inversion of
  $\left(E_s \mathbf{H}_c \mathbf{H}_c^H + \frac{1}{N}\sum_{i=1}^{N} \mathbf{n}_c^i (\mathbf{n}_c^i)^H\right)^{-1}$
  — a **Hermitian positive-definite** matrix of dimension $M_c \times M_c$.
- Uses only **local data** ($\mathbf{H}_c$, local noise samples $\{\mathbf{n}_c^i\}$); no cross-cluster communication at inversion time.
- Computed **once per coherence block**, reused for all $N_\text{coh}$ symbols (Zhao et al. 2025, Sec. V.B).
- Convergence in 4–5 BCD iterations to near-centralized LMMSE BER (guaranteed by Theorem 2).
- **Hardware gap:** Zhao et al. provide only SER curves and Table I fronthaul rates. No LUT count, power, or latency figures exist.

---

## 3. Notation — use exactly these symbols throughout

| Symbol | Meaning |
|---|---|
| $M$ | Total BS antennas |
| $K$ | Number of single-antenna users |
| $C$ | Number of antenna clusters / DUs |
| $M_c$ | Antennas in cluster $c$ ($M = \sum_c M_c$) |
| $\mathbf{y} \in \mathbb{C}^{M\times1}$ | Received uplink vector |
| $\mathbf{x}, \mathbf{s} \in \mathbb{C}^{K\times1}$ | Transmitted symbol vector |
| $\mathbf{H} \in \mathbb{C}^{M\times K}$ | Channel matrix |
| $\mathbf{n}$ | Noise vector |
| $\mathbf{R}, \mathbf{R}_n$ | Full noise covariance matrix ($M\times M$, non-diagonal under colored noise) |
| $\mathbf{R}_{cc}$ | Local diagonal block of $\mathbf{R}$ at cluster $c$ ($M_c \times M_c$) |
| $\hat{\mathbf{R}}_{cc}$ | Sample estimate of $\mathbf{R}_{cc}$ |
| $\rho = N_0/E_s$ | LMMSE regularization parameter |
| $E_s$ | Per-UE transmit power |
| $N_0$ | Noise power spectral density |
| $N_\text{coh}$ | Coherence block length (symbols) |
| $N$ | Number of pilot resource elements used for $\hat{\mathbf{R}}$ estimation (typically 96 or 192) |
| $\mathbf{W}_c$ | Local equalizer block at DU $c$ |
| $\mathbf{G}_c = \mathbf{H}_c^H\mathbf{H}_c$ | Local Gram matrix |
| $\mathbf{y}_c^{MRC} = \mathbf{H}_c^H\mathbf{y}_c$ | Local MRC vector |
| $\mathcal{O}(N^3)$ | Inversion complexity (cubic in matrix dimension) |
| DBP | Decentralized Baseband Processing |
| DU | Distributed Unit |
| CU | Central Unit |
| AWGN | Additive White Gaussian Noise |
| WGN | White Gaussian Noise (synonym) |
| CPRI | Common Public Radio Interface |

**Notation rules:**
- All matrices: bold uppercase ($\mathbf{H}$, $\mathbf{R}$).
- All vectors: bold lowercase ($\mathbf{y}$, $\mathbf{n}$).
- Hermitian transpose: superscript $^H$.
- Estimated quantities: hat ($\hat{\mathbf{R}}_{cc}$).
- Never use $\mathbf{R}_n$ and $\mathbf{R}$ interchangeably for the same object within a single section — pick one and stay consistent.

---

## 4. Document structure and section purposes

```
Abstract             (TODO — write last)
1. Introduction      Funnel: broad 5G context → centralized bottleneck
                     → colored noise gap → FPGA objective
2. Literature Review
   2.1 Massive MU-MIMO System Model   y = Hx + n; LMMSE AWGN + colored forms; O(N^3)
   2.2 Linear Equalization            MRC / ZF / LMMSE comparison
   2.3 Decentralized MIMO Arch.       DBP clusters; PD/FD; AWGN decomposes cleanly;
                                      colored noise does not; star vs. daisy-chain
   2.4 Colored Noise in Massive MIMO  Sources; R estimation; coherence-time trade-off;
                                      precision/BER trade-off; gap statement
   2.5 Decentralized LMMSE Under      BCD-MMSE algorithm (Zhao 2025)
       Colored Noise
       2.5.1 BCD-MMSE Algorithm
   2.6 Matrix Inversion Techniques    Cholesky; Neumann series; applicability;
                                      hardware cost comparison
3. Related Work
   3.1 FPGA Implementation of         Survey of FPGA/ASIC inversion papers;
       Matrix Inversion                comparison tables; gap synthesis
4. Methodology
5. Schedule
6. Conclusion
```

**Color convention in the .tex file** (for the author's reference during writing):
- `\color{red}` — author's seed text in Portuguese (to be expanded into final prose)
- `\color{olive}` — citations from the inversion-avoidance and algorithm papers
- `\color{magenta}` — citations from hardware implementation paper summaries
- `\color{blue}` — citations from the evolutionary timeline survey document
- All color markup **must be removed** before final submission.

---

## 5. Citation inventory

### 5.1 Algorithm / inversion-avoidance papers (olive citations)

| Key | Full reference | Noise model | Inversion handling |
|---|---|---|---|
| Li et al. 2017 | DBP with ADMM/CG, consensus | WGN | Iterative (implicit) |
| Jeon et al. 2019 | Feedforward PD/FD equalizer | WGN | $K\times K$ Gram (PD); local per cluster (FD) |
| Li et al. 2019 (Asilomar) | Explicit vs. implicit Cholesky trade-off analysis | WGN | Cholesky: $10/3\,U^3$ (explicit) vs. $2/3\,U^3$ (implicit) |
| Rodríguez Sánchez et al. 2020 | Daisy-chain CD / Kaczmarz | WGN | Inversion-free (gradient descent) |
| Croisfelt et al. 2021 | Bayesian Distributed Kaczmarz (BDK) | WGN | Inversion-free (closest to colored noise but still assumes $\sigma^2\mathbf{I}$) |
| Wang et al. 2023 (BD-NS-EPA) | Block-diagonal Neumann-series EP approx. | WGN (Kronecker channel model) | NSA approximation; ASIC Cholesky baseline |
| Li et al. 2023 (GW-EP, IoT-J) | Groupwise EP, star + daisy-chain | WGN | Inversion-free EP |
| Zheng et al. 2023 | Recursive MMSE chain | WGN | $L\times L$ per cluster (exact MMSE) |
| Chen et al. 2024 (GRLS) | Groupwise RLS, multiple antennas per DU | WGN | $B\times B$ at first $C_0$ DUs; diagonal elsewhere |
| Zhuang et al. 2025 | LMMSE, imperfect CSI, spatial correlation | WGN | $N_k\times N_k$ local; $K\times K$ at CU |
| **Zhao et al. 2021 (GLOBECOM)** | **BCD-MMSE, daisy-chain** | **Colored noise** | **$M_c\times M_c$ per DU per iteration** |
| **Zhao et al. 2025 (IEEE JSAC)** | **sDR-MMSE + cDR-MMSE (star) + BCD-MMSE (daisy-chain)** | **Colored noise** | **$M_c\times M_c$ per DU (preprocessing); $K\times K$ or $CK\times CK$ at CU** |

**Critical fact:** Zhao et al. 2025 is the **only** work in the DBP literature treating colored noise. Li et al. IoT-J 2023 explicitly confirms this: *"Zhao et al. [27] proposed a block CD (BCD)-based MMSE detection for the decentralized daisy chain architecture, which considers the practical colored noise scenario with a nondiagonal correlation matrix."*

### 5.2 Hardware implementation papers (magenta citations)

| Key | Platform | MIMO | Algorithm | Throughput | Power | Energy eff. |
|---|---|---|---|---|---|---|
| Wang et al. 2021 (TL-BD-INSA), FPGA | Virtex-7 XC7VX980T | 128×32 | TL-BD-INSA (Cholesky) | 57.3 Mbps | — | 1,731 bps/slice |
| Wang et al. 2021 (TL-BD-INSA), ASIC | TSMC 45 nm | 128×32 | TL-BD-INSA | 185 Mbps | 0.144 W | 1.28 Gbps/W |
| Wang et al. 2023 (BD-NS-EPA), ASIC | SMIC 65 nm | 128×32 | BD-NS-EPA | 715 Mbps | 571 mW | 1.252 Gbps/W |
| Jeon et al. / Li et al. (FD-LAMA) | Virtex-7 XC7VX690T | 128×8 | FD-LAMA (HLS) | 14 Mb/s ($C=1$) | — | 1,186 bps/LUT |
| Kulkarni et al. 2021 (ring) | Virtex-7 XC7VX690T | 128×8, $C=4$ | Decentralized Newton | 279 Mbps | 7.177 W | 38.92 Mb/J |
| Peng et al. 2020 (CGRA-CHD) | TSMC 28 nm ASIC | 128×8 | Cholesky (CHD) | 0.88 Gb/s | 0.537 W | 1.639 Gb/s/W |
| Dai et al. 2020 (Spine) | Xilinx VCU118 | 32 ant., 2 UE | MRC beamforming | 6.4 Gb/s | 5.4 W | — |

**Primary comparison targets:** Wang et al. 2021 (TL-BD-INSA) and Kulkarni et al. 2021 (Decentralized Newton ring).
**Efficiency ceiling:** Peng et al. 2020 ASIC CHD result.
**Critical difference from all of the above:** None considers colored noise. The BCD-MMSE inversion is *exact* and operates on the full non-diagonal $\hat{\mathbf{R}}_{cc}$.

### 5.3 Duplicate citation groups (flag before choosing one)

| Group | Topic | Options |
|---|---|---|
| A | Interconnect data-rate bottleneck (~1 Tbps) | Li 2019 CD (256 ant., 12-bit DAC); Li IoT-J 2023 (128 ant., 10-bit ADC); Rodríguez Sánchez 2020 (LuMaMi testbed, 384 Gbps) |
| B | System model $\mathbf{y} = \mathbf{H}\mathbf{x} + \mathbf{n}$ | Rodríguez Sánchez 2020; Li 2019 CD; Li IoT-J 2023; Wang 2023 BD-NS-EPA |
| C | LMMSE closed-form (AWGN) | Jeon 2019 (Gram form); Li 2019 Asilomar; Li 2017 |
| D | LMMSE closed-form (colored noise) | Zhao 2025 JSAC (Eq. 3); Zhao 2021 GLOBECOM (Eq. 4) |
| E | $\mathcal{O}(N^3)$ complexity statement | Zhao 2025; Zhao 2021 |
| F | Colored noise covariance definition | Zhao 2025 (Eq. 5, interference model); Zhao 2021 (sample estimate $\hat{\mathbf{R}}$) |

**Rule when writing:** For each duplicate group, choose **one** citation per occurrence. Do not cite both unless they make genuinely distinct points. When both make the same point, prefer the **most recent and most prominent venue** (generally the IEEE JSAC 2025 version over the GLOBECOM 2021 version for Zhao et al.).

---

## 6. Scientific writing rules for this thesis

### 6.1 Language and register
- **Target language:** Brazilian Portuguese (all final prose). Comments in the `.tex` file may remain in English.
- **Register:** Formal academic engineering Portuguese. No contractions, no colloquialisms.
- **Tense:** Present tense for established facts and general truths; past tense for describing specific experimental results; future tense for the proposed work's contributions (until results are available).

### 6.2 Equation and notation discipline
- Every symbol **must be defined** on first use in each section.
- Do **not** introduce new symbols that conflict with those in Section 3 of this skill.
- When citing an equation from a reference, include the equation number and paper explicitly, e.g., *"...conforme a Eq.~(30) de Zhao et al.~\cite{zhao2025jsac}."*
- The BCD-MMSE update equation (Eq. 10 / Eq. 30 of Zhao et al. 2025) should be reproduced verbatim with proper attribution, not paraphrased mathematically.

### 6.3 Argument structure for each section
Every section must answer, in order:
1. **What** is being introduced or surveyed?
2. **Why** does it matter for this specific work?
3. **What is missing** (the gap that motivates the next section or this work)?

The Introduction must follow the **funnel structure** exactly as outlined in the section comments of the `.tex` file: broad context → centralized bottleneck → colored noise gap → FPGA objective.

### 6.4 Citing hardware metrics
- Always state the **MIMO configuration** (e.g., 128×32), **modulation** (e.g., 64-QAM), and **platform** (e.g., Virtex-7 XC7VX980T or TSMC 45 nm) alongside any hardware number.
- Never cite throughput, power, or LUT counts without their context — an isolated number is meaningless without knowing whether it was measured at QPSK or 64-QAM, with or without CHEST overhead, etc.
- When comparing this work's results to prior work, always note that **BCD-MMSE operates under colored noise** whereas all prior hardware works operate under AWGN — this is a fundamental difference, not just a parameter difference.

### 6.5 What NOT to do
- Do **not** claim that inversion-avoidance methods can be applied to the colored-noise case without justification. The Neumann series convergence condition ($\rho(\boldsymbol{\Psi}) < 1$) requires the preconditioner to capture the dominant structure of the Gram matrix, which is only valid under white noise.
- Do **not** describe the Zhao 2021 GLOBECOM paper and the Zhao 2025 JSAC paper as the same work. The 2021 paper covers BCD-MMSE for the daisy-chain architecture; the 2025 paper additionally covers sDR-MMSE and cDR-MMSE for the star architecture.
- Do **not** omit the coherence-block reuse property when describing BCD-MMSE. The cost of the $M_c\times M_c$ inversion is **amortized across $N_\text{coh}$ symbols** — this is the key property that justifies building a dedicated hardware accelerator.
- Do **not** reproduce citation blocks from `\subsection{System Model}` inside `\subsection{Decentralized MIMO Architectures}`. The system model is defined once.

---

## 7. Section-by-section writing guidance

### Section 1 — Introduction
**Paragraph 1:** Establish the 5G/6G demand for high spectral efficiency. Introduce Massive MU-MIMO as the enabling technology. Cite the interconnect data-rate bottleneck (choose one citation from Duplicate Group A — Li 2019 CD or Li IoT-J 2023 are preferred over the testbed figure from Rodríguez Sánchez).

**Paragraph 2:** Explain why centralized processing is impractical at scale (cite Jeon 2019 or Li 2017 for the $\mathcal{O}(N^3)$ argument and Li 2017 for DBP motivation). State that decentralized architectures reduce the per-cluster matrix size but do not eliminate the inversion requirement.

**Paragraph 3:** Introduce the colored noise gap. All prior DBP works assume diagonal $\mathbf{R}_n$ (AWGN). Cite Wang 2023 for the failure of NSA under non-white noise, and Li IoT-J 2023 + Zhao 2025 for the explicit gap statement. State that Zhao et al. 2025 is the sole exception.

**Paragraph 4:** State the objective. The BCD-MMSE inversion (Eq. 30 of Zhao 2025) has no hardware implementation. This work provides the first FPGA analysis: BER, LUT count, and power consumption.

### Section 2.1 — Massive MU-MIMO System Model
Present the uplink model $\mathbf{y} = \mathbf{H}\mathbf{x} + \mathbf{n}$ with dimensions. Define each symbol. Present the LMMSE optimization form and both closed-form solutions (AWGN and colored-noise variants, selecting one citation each from Duplicate Groups C, D, E). Explain why $\mathcal{O}(N^3)$ is limiting at scale.

### Section 2.2 — Linear Equalization
Comparative presentation of MRC, ZF, and LMMSE. Use the SINR expressions from Jeon 2019 Corollary 2 to motivate LMMSE as the performance-optimal linear detector. A table with the three detectors, their complexity, and their SINR (from blue citation "Data Compilation Table") is strongly recommended.

### Section 2.3 — Decentralized MIMO Architectures
Structure: (a) define the cluster model (Jeon 2019 Eq. 3); (b) describe PD and FD feedforward architectures and where inversion occurs (Jeon 2019, Li 2019 Asilomar); (c) explain AWGN decomposition vs. colored noise impossibility (Zhao 2025 Sec. II.B); (d) describe star vs. daisy-chain; (e) survey the nine evolutionary stages, organized as two axes: WGN works (Stages 1–8) and colored-noise work (Stage 9).

### Section 2.4 — Colored Noise in Massive MIMO Systems
Structure: (a) define the colored noise model using Zhao 2025 Eq. 5 (interference) and Zhao 2021 (sample estimator $\hat{\mathbf{R}}$); (b) show that all eight inversion-avoidance papers assume $\sigma_n^2\mathbf{I}$ — cite all five noise declarations from the olive block as a group; (c) cite Wang 2023 BD-NS-EPA quantitative degradation evidence; (d) present the coherence-time amortization argument (Li 2019 Asilomar Eqs. 6–7) and the precision/BER trade-off (fp8 vs. fp32); (e) end with the gap statement from Zhao 2025.

### Section 2.5.1 — BCD-MMSE Algorithm
Present the algorithm fully. Reproduce Eq. 30 with attribution. Describe the local data locality property. State the amortization over $N_\text{coh}$ symbols (Zhao 2025 Sec. V.B). State the convergence guarantee (Theorem 2 / Remark 1). Explicitly state: no hardware implementation exists — this is the specific gap this work fills.

### Section 2.6 — Matrix Inversion Techniques
Structure: (a) Neumann series — definition, convergence condition, and why it fails for $\mathbf{H}^H\mathbf{R}_n^{-1}\mathbf{H} + \mathbf{R}_x^{-1}$ (cite Wang 2023 NSA formulation and convergence condition); (b) Cholesky decomposition — exact method for Hermitian PD matrices, implicit vs. explicit cost (Li 2019 Asilomar Eqs. 6–7), and ASIC architecture (Wang 2023 BD-NS-EPA Sec. VI.B).

### Section 3.1 — Related Work: FPGA Implementation of Matrix Inversion
Present the five hardware works in order of relevance to this work. For each: algorithm, MIMO configuration, platform, noise model, and key metrics. Use the comparison table (already present in the `.tex` file). Close with the **gap synthesis** paragraph: none of the reviewed works combines colored noise + decentralized LMMSE + FPGA hardware metrics.

---

## 8. LaTeX conventions

- Citation command: `\cite{key}` — citation keys follow the pattern `[firstauthor][year][venue]`, e.g., `\cite{zhao2025jsac}`.
- Equation labels follow the pattern `\label{eq:systemmodel}`, `\label{eq:lmmse_awgn}`, `\label{eq:lmmse_colored}`, `\label{eq:bcd_update}`.
- Table labels: `\label{tab:detector_comparison}`, `\label{tab:hw_summary}`.
- Section cross-references: `Section~\ref{sec:sysmodel}`, `Eq.~\eqref{eq:bcd_update}`.
- Use `\mathbf{}` for all vectors and matrices (never `\boldsymbol` for Latin letters).
- Use `\mathbb{C}^{M\times K}` for complex matrix spaces.
- Use `\mathcal{O}(N^3)` for complexity notation.
- Use `~` (non-breaking space) before `\cite`, `\ref`, `\eqref`.
- The template uses `\sloppy`; do not override line-break settings.

---

## 9. Quality checklist — run before submitting any drafted section

- [ ] Every symbol defined on first use in the section.
- [ ] No notation conflict with the inventory in Section 3.
- [ ] Every hardware metric accompanied by its MIMO config, modulation, and platform.
- [ ] No bare duplicate citations — one representative chosen per occurrence.
- [ ] The triple gap (colored noise + decentralized + FPGA) stated explicitly in Introduction and Related Work closings.
- [ ] The coherence-block amortization property mentioned whenever BCD-MMSE is described.
- [ ] All color blocks (`\color{red}`, `\color{olive}`, etc.) replaced by proper prose before any section is considered complete.
- [ ] The system model citation block does not appear a second time inside the Decentralized Architectures subsection.
- [ ] Language is Brazilian Portuguese, formal register, present tense for facts.
