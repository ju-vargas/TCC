# Literature Review Guide
## Matrix Inversion in Decentralized Equalization for Massive MIMO — Final Year Project

---

## How to use this guide

This guide is organized as a sequential process across six phases, each with concrete tasks, search terms, and decision criteria. Work through phases 1–3 before writing anything. Phases 4–5 are where most of the reading and synthesis happens. Phase 6 is the writing itself. Expect the full process to take four to six weeks of part-time effort.

At the end of the guide you will find a paper logging template and a reference map of the complete narrative structure your review should produce.

---

## Phase 1 — Anchor and orient (Week 1)

### Goal
Build a precise mental model of what the two anchor papers claim, what assumptions they make, what operations they require, and where each one's argument stops. Everything in the review is measured against these two fixed points.

### Step 1.1 — Annotate Li et al. 2017 with an operational lens

Read the paper again, this time extracting only the information relevant to hardware implementation. For each algorithmic contribution, record:

- What matrix operations are required in the preprocessing stage (before iterations begin)?
- What matrix operations are required per iteration?
- What is communicated between clusters at each step, and what is its dimension?
- What is the assumed noise model (confirm: i.i.d. CN(0, N₀) — diagonal covariance)?
- Where does a matrix inversion appear, even implicitly?

For the ADMM detector (Algorithm 1): note that preprocessing requires computing A⁻¹_c = (H^H_c H_c + ρ⁻¹ I_S)⁻¹ or B⁻¹_c = (H_c H^H_c + ρ⁻¹ I_U)⁻¹ locally at each cluster. This is a K×K or S×S inversion — small and local. The key point is that this works *because* the noise covariance is diagonal and therefore does not couple clusters.

For the CG detector (Algorithm 2): note that no explicit inversion appears — the Gram matrix is assembled as a sum of local contributions. This is the canonical inversion-free design.

Write a one-paragraph summary of each algorithm from a hardware perspective. These paragraphs become the seed of your "baseline algorithms" subsection.

### Step 1.2 — Annotate Zhao et al. 2025 with a system-theoretic lens

For this paper, extract:

- The precise form of the LMMSE equalization matrix W_MMSE (Eq. 3): note the M×M inversion of R.
- The structure of R under AWGN (diagonal) vs. colored noise (non-diagonal, full M×M).
- Why the block-diagonal approximation R_B breaks equalization performance.
- What the paper proposes for the star architecture (dimensionality reduction, Eqs. 8–9) and for the daisy chain architecture (BCD iterations).
- What operations in their proposed methods *still require* a matrix inversion, and what its dimension is.
- What the paper does NOT address: hardware implementation, fixed-point arithmetic, FPGA mapping.

This last point is the gap your project fills.

### Step 1.3 — Define your project's mathematical kernel

Based on the above, write a precise statement of the operation your FPGA must implement. For example:

> "The target operation is the inversion of a K×K or (K+1)×(K+1) Hermitian positive semi-definite matrix arising from the compressed LMMSE formulation in the star architecture, or the per-iteration inversion step within the BCD algorithm in the daisy chain architecture. The matrix is complex-valued, and its condition number is determined by the interference-to-noise ratio and the rank of the interference channel H̄."

This statement governs which inversion families are in scope for your hardware analysis (Phase 5).

---

## Phase 2 — Map the citation tree (Week 1–2)

### Goal
Identify all papers that cite Li et al. 2017 and classify them into the three pillars. Produce a filtered, annotated reading list before reading a single paper in full.

### Step 2.1 — Pull the citation list

Use all three of the following sources and merge the results:

- **Google Scholar**: search the exact title "Decentralized Baseband Processing for Massive MU-MIMO Systems" and click "Cited by." Sort by date (oldest to newest) to understand the progression.
- **Semantic Scholar** (semanticscholar.org): the same search; use the "Highly Influential" filter to identify papers that built directly on the 2017 work rather than citing it tangentially.
- **IEEE Xplore**: search DOI 10.1109/JETCAS.2017.2775151 in the "Citing Articles" tab.

Export the full list (expect 80–150 entries). You do not need to read all of them.

### Step 2.2 — Triage by title and abstract (one sitting, no deep reading)

For each entry, assign a pillar:

| Pillar | Keyword signals in title/abstract |
|--------|----------------------------------|
| **A — Inversion avoidance** | CG, ADMM, conjugate gradient, coordinate descent, Newton, message passing, AMP, EP, GMP, iterative detection, approximate |
| **B — Equalization matrix design** | equalization matrix, ZF, LMMSE, feedforward, MRC, gradient descent, BCD, bidirectional |
| **C — Hardware implementation** | FPGA, ASIC, VLSI, chip, fixed-point, throughput, hardware, implementation, area, power |
| **Out of scope** | channel estimation only, downlink/precoding only, non-massive MIMO, unrelated topic |

Mark "out of scope" entries and set them aside. You will not return to them.

### Step 2.3 — Score remaining papers for relevance

For each pillar-A or pillar-B paper, assign a priority:

- **Priority 1**: directly extends or critiques an algorithm from Li et al. 2017, or proposes a competing DBP detection strategy.
- **Priority 2**: proposes a new inversion-avoidance method for Massive MIMO detection but not specifically for DBP.
- **Priority 3**: tangentially related (e.g., general Massive MIMO, not DBP-specific).

For pillar-C papers, all are priority 1 for your project regardless of their DBP focus.

Aim for approximately 15–20 priority-1 papers across pillars A and B, plus 10–15 pillar-C papers. This is your reading list.

### Step 2.4 — Add the independent hardware thread

The citation tree of Li et al. 2017 will underrepresent hardware implementations, because the hardware community cites different anchors (Yin et al. 2014, Wu et al. 2014, Prabhu et al. 2017). Run the following searches on IEEE Xplore independently:

```
Search 1: "matrix inversion" AND "FPGA" AND ("MIMO" OR "MMSE")
Search 2: "Cholesky decomposition" AND "FPGA" AND "MIMO"
Search 3: "LMMSE" AND "FPGA" AND ("massive MIMO" OR "large-scale MIMO")
Search 4: "Neumann series" AND "MIMO" AND ("approximation" OR "hardware")
Search 5: "matrix inversion" AND "VLSI" AND "MIMO"
```

Filter results to 2014–present. Add relevant results to your Pillar C reading list.

**Key anchors to include regardless of search results:**
- Wu et al. (2014), "Large-Scale MIMO Detection for 3GPP LTE," IEEE JSTSP — foundational FPGA MMSE detector
- Yin et al. (2014), "A 3.8 Gb/s Large-Scale MIMO Detector for 3GPP LTE-Advanced," ICASSP
- Prabhu et al. (2017), "A 60 pJ/b 300 Mb/s 128×8 Massive MIMO Precoder-Detector in 28nm FD-SOI," ISSCC — both cited by Li et al. 2017 itself

### Step 2.5 — Build the colored noise thread independently

This thread is not well-covered by the citation tree of Li et al. 2017. Run these searches:

```
Search 6: "colored noise" AND "MMSE" AND "massive MIMO"
Search 7: "MMSE-IRC" AND "massive MIMO" AND ("uplink" OR "detection")
Search 8: "interference rejection combining" AND "massive MIMO" AND "hardware"
Search 9: "interference covariance" AND "estimation" AND "massive MIMO"
Search 10: "pilot contamination" AND "colored noise" AND "LMMSE"
```

This thread justifies the premise of the 2025 paper and is the gap identified in our previous discussion. You need approximately 5–8 papers here.

---

## Phase 3 — Build the timeline skeleton (Week 2)

### Goal
Before reading in depth, place every priority-1 paper on a chronological map organized by pillar. This gives you the narrative arc before the details.

### Step 3.1 — Create a timeline table

For each priority-1 paper, fill one row:

| Year | Authors | Venue | Pillar | One-line claim | Assumption broken by 2025 |
|------|---------|-------|--------|----------------|--------------------------|
| 2017 | Li et al. | JETCAS | A+B | Proposes ADMM/CG DBP; avoids M×M inversion | AWGN, diagonal R |
| ... | | | | | |
| 2025 | Zhao et al. | JSAC | B | LMMSE equalization under colored noise in DBP | — (target paper) |

The rightmost column forces you to identify, for each prior paper, the exact assumption that the 2025 paper invalidates. Most entries will be "diagonal noise covariance / AWGN." Some may add further nuance (e.g., "also assumes perfect covariance knowledge").

### Step 3.2 — Identify the gap trajectory

Looking at your timeline, locate:

1. The last paper (before 2025) that made the AWGN assumption explicit rather than implicit.
2. Any paper that acknowledged the limitation of the AWGN assumption without solving it.
3. The first paper to use colored noise in a DBP context (likely the 2021 arXiv precursor to the 2025 paper, arXiv:2106.12416).

These are your "gap markers" and they structure the narrative of your review.

---

## Phase 4 — Deep reading by pillar (Weeks 2–4)

Work through pillars sequentially in this order: Colored Noise thread first (because it justifies the problem), then Pillar B (because it defines what you implement), then Pillar A (because it defines what others tried instead), then Pillar C (because it defines your hardware contribution space).

### Reading procedure for every paper

For each paper, fill in the four-element card:

**Setting**: System model, number of antennas, users, noise assumption, DBP architecture (if applicable), topology (star/daisy chain/other).

**Key technique**: The single mathematical operation or algorithmic idea that the paper contributes. Be precise — "avoids M×M inversion by decomposing the Gram matrix as a sum of local contributions" is better than "decentralized detection."

**Justification**: Why does the paper claim its approach is valid? What theorem, simulation result, or approximation bound does it cite?

**Limitation / open problem**: What does the paper leave unsolved, approximate, or assume away? At least one limitation per paper must connect to your project's contribution.

---

### Colored noise thread — what to look for

For each paper in this thread, the key question is: **does it establish, model, or quantify the performance impact of colored noise in a way that the 2025 paper's two references (Liu 2007, Tomasin 2023) do not?**

Specifically look for:
- Quantified BER or SINR degradation when AWGN is assumed but noise is actually colored.
- Analysis of interference structure (low-rank, spatially colored) from inter-cell UEs.
- Results showing that the interference-to-noise ratio (INR) matters for equalization design.
- The 3GPP/5G NR motivation for MMSE-IRC receivers — this is industry evidence for your justification.

For the MMSE-IRC papers (Ren 2017, related 5G NR literature): note that these exist in the *centralized* processing context. One of the contributions of your review is to bridge the centralized MMSE-IRC motivation to the decentralized DBP context — a bridge the 2025 paper does not explicitly build.

---

### Pillar B — equalization matrix design

The key distinction to track across papers is: **does the paper compute an equalization matrix (reusable across symbols) or estimate each symbol directly (must be rerun)?**

Map each paper to this classification. Papers in the equalization matrix camp are your direct upstream work. The evolution of this idea in DBP:

- Li et al. 2017 (ADMM/CG): symbol estimation — must rerun per symbol.
- Jeon et al. 2019 (feedforward DBP): introduces the equalization matrix directly for MRC/ZF/LMMSE in star architecture — identify this paper via Semantic Scholar from Li et al. 2017's citation network.
- Zhang et al. 2022: gradient descent for ZF equalization matrix in daisy chain.
- Cui et al. 2023: bidirectional-chain parallel iterative MMSE equalizer.
- Zhao et al. 2025: equalization matrix under colored noise, both architectures.

For each, extract the dimension of the matrix being inverted and the exact form of the inversion. This feeds directly into your hardware analysis in Phase 5.

---

### Pillar A — inversion avoidance

For each method, answer these questions:

1. What inversion does it avoid, and what does it replace it with?
2. Under what noise model is the avoidance valid?
3. Can the method be extended to colored noise without introducing an explicit inversion? If not, why?

This last question is the bridge from Pillar A to the problem that Pillar B (and your project) must solve.

The canonical answer for CG and ADMM: they avoid the M×M inversion because, under AWGN, the Gram matrix G = H^H H decomposes as a sum of local terms G_c = H^H_c H_c, and the noise contribution reduces to a scalar σ²I. Under colored noise, the matched filter becomes H^H R⁻¹ and the Gram matrix becomes H^H R⁻¹ H — neither decomposes without first computing R⁻¹, which is itself an M×M inversion. Write this argument out in your own words. It is the technical core of your justification section.

---

### Pillar C — hardware implementation

For each hardware paper, record:

**Matrix family**: Cholesky, LU, Gauss-Jordan elimination, Neumann series, QR, or other.

**Matrix dimension and structure**: What is the size of the matrix being inverted? Is it Hermitian positive definite (enables Cholesky)? Is it diagonally dominant (enables Neumann convergence)?

**Fixed-point word length**: What precision is used for inputs, intermediate products, and outputs? How is rounding handled?

**Throughput and latency**: What clock frequency, pipeline depth, and MIMO configuration does the paper target?

**Area and power**: In what technology node? How many LUTs, DSPs, BRAMs (for FPGA) or gate equivalents (for ASIC)?

**Condition number sensitivity**: Does the paper analyze how ill-conditioned matrices affect fixed-point accuracy? This is critical for colored noise scenarios, where R may be ill-conditioned at low INR.

Build a comparison table across all Pillar C papers. This table becomes the hardware survey section of your review and directly informs your FPGA design choices.

---

## Phase 5 — Synthesize the hardware design space (Week 4)

This phase is unique to your project — it does not appear in most literature reviews. Because your contribution is hardware, you must connect the algorithmic findings of phases 4A/4B to the implementation findings of 4C.

### Step 5.1 — Map algorithms to inversion families

For each equalization method that requires an inversion (from Pillar B and the 2025 paper), identify which matrix families can perform it:

| Algorithm | Matrix to invert | Structure | Compatible families |
|-----------|-----------------|-----------|-------------------|
| BDAC-MMSE baseline | R_cc (local, M_c × M_c) | Hermitian PSD | Cholesky, LU |
| DR star (superimposed) | L×L compressed system | Hermitian PSD | Cholesky, LU |
| DR star (concatenated) | CL×CL system at CU | Hermitian PSD | Cholesky, LU |
| BCD daisy chain per-iter | K×K (varies by formulation) | Hermitian PSD | Cholesky, Neumann |

For Neumann series: note that convergence requires the matrix to be close to a scaled identity — this holds under AWGN (diagonal dominance) but may fail under colored noise with high INR. This is a non-trivial limitation that your project can analyze.

### Step 5.2 — Identify the fixed-point analysis dimensions

Your project will analyze fixed-point accuracy. The literature suggests the following axes matter:

- **Quantization of R̂**: the sample covariance estimate is computed from a finite number of pilot REs (N in the 2025 paper's notation). Finite N introduces estimation error before any fixed-point effects.
- **Word length of intermediate Cholesky factors**: the triangular factorization amplifies dynamic range. The condition number of the matrix bounds the required dynamic range.
- **Accumulation precision**: inner products in matrix-matrix multiplications require guard bits.
- **Condition number under colored noise**: for R = βH̄H̄^H + σ²I, the condition number is approximately 1 + β·λ_max(H̄H̄^H)/σ², which grows with INR. At high INR, inversion becomes numerically sensitive.

Frame this as a research question: *how does the INR affect the minimum word length required to achieve a target BER for each inversion family?* This connects your fixed-point analysis to a system-level metric.

### Step 5.3 — Define your comparison framework

Your FPGA analysis will compare inversion families. Define now what metrics you will use, so the review can explain what prior work does and doesn't provide for each:

- Latency (clock cycles to compute one inversion, for a given K or L)
- Throughput (inversions per second at target clock frequency)
- Area (LUTs, DSPs, BRAMs on your target device)
- Power (dynamic + static, from Vivado/Quartus reports)
- Fixed-point accuracy (BER vs. floating-point baseline, at target SNR and INR)
- Scalability (how metrics scale with K)

For each prior hardware paper in Pillar C, annotate which of these metrics it reports and under what conditions (SNR, matrix size, FPGA family). Gaps in prior coverage become your original contributions.

---

## Phase 6 — Write the review (Week 5–6)

### Recommended section structure

**Section 1: Introduction to the problem**
One to two pages. Start from the raw data rate bottleneck (quote the 1 Tbps figure from the 2025 paper), establish that DBP is the architectural response, and state that LMMSE equalization under DBP requires a matrix inversion whose form depends critically on the noise model. End with a forward-looking paragraph: the review will show that the inversion-avoidance strategies valid under AWGN become inadequate under colored noise, and that no hardware implementation of the required inversion exists in the DBP context.

**Section 2: Background**
Two to three pages. System model (follow the 2025 paper's notation: M antennas, K users, H, s, n, R). LMMSE receiver derivation. DBP architectures (star and daisy chain). Definition of colored noise and its sources (inter-cell interference, pilot contamination, hardware impairments). Establish that R = βH̄H̄^H + σ²I is the relevant model.

**Section 3: The colored noise problem and its practical significance**
One to two pages. This is the section that fills the gap in the 2025 paper's motivation. Three subsections:

- *Sources of colored noise in 5G/6G deployments*: inter-cell interference from frequency reuse, pilot contamination as a structured noise component, hardware impairment distortion.
- *Performance impact of ignoring colored noise*: BER degradation when AWGN is assumed; reference the MMSE-IRC literature for quantitative evidence.
- *Why DBP specifically cannot handle colored noise with prior methods*: the decomposability argument (R non-diagonal → H^H R⁻¹ H does not split by cluster → inversion is unavoidable). This is your original synthesis.

**Section 4: Inversion avoidance under AWGN — strategies and limitations**
Three to four pages. Organize by strategy family, not chronologically:

- Iterative symbol estimators (CG, ADMM, coordinate descent, Newton): what inversion they avoid, what consensus overhead they require, why they fail under colored noise.
- Message passing detectors (AMP, EP, GMP): same structure.
- Equalization matrix methods under AWGN: feedforward DBP, gradient descent ZF, bidirectional MMSE.

End each subsection with an explicit statement of the assumption that breaks under colored noise.

**Section 5: Decentralized LMMSE equalization under colored noise**
Two pages. Present the 2025 paper's contributions in detail: DR techniques for star, BCD for daisy chain, low-rank approximation. Extract the precise form of the inversion required by each method. This section ends by establishing the exact mathematical operation your hardware must implement.

**Section 6: Hardware implementations of matrix inversion for MIMO**
Three to four pages. Organized by inversion family:

- Cholesky decomposition: principle, complexity, implementation results from literature, fixed-point considerations.
- LU decomposition: same structure.
- Neumann series approximation: convergence conditions, why it degrades under high INR (colored noise), implementation results.
- Other methods (Gauss-Jordan, QR): briefly if covered in literature.

End with a comparison table across families and a paragraph explaining why no existing implementation addresses the DBP colored noise context.

**Section 7: Open problems and your contribution**
One page. Enumerate precisely what is missing: (a) no hardware implementation of LMMSE equalization matrix computation under colored noise in DBP; (b) no fixed-point analysis of inversion families under condition numbers characteristic of colored noise scenarios; (c) no comparison of inversion families for the specific matrix dimensions arising from DBP (K×K or compressed L×L, not M×M). State how your project addresses each gap.

---

## Reference map

The review must cite works from all five threads. As a sanity check before submission, verify coverage:

| Thread | Minimum papers | Key gaps if missing |
|--------|---------------|-------------------|
| DBP architecture fundamentals (Li 2017 + immediate successors) | 3–5 | No baseline for your narrative |
| Inversion avoidance under AWGN | 6–10 | Cannot argue why inversion is necessary |
| Equalization matrix design in DBP | 4–6 | Cannot specify what your hardware implements |
| Colored noise motivation and modeling | 5–8 | Cannot justify the 2025 paper's premise |
| Hardware implementations | 8–12 | Cannot define your contribution space |

Total expected references: 30–45 is appropriate for a final year project literature review.

---

## Paper logging template

Copy this block once per paper:

```
PAPER LOG
─────────────────────────────────────────────
Title:
Authors:
Venue / Year:
DOI:
Pillar: [ A - inversion avoidance ] [ B - equalization matrix ] [ C - hardware ] [ colored noise ]
Priority: [ 1 ] [ 2 ] [ 3 ]

SETTING
  Antennas (M):
  Users (K or U):
  Noise model:
  DBP architecture:
  Topology:

KEY TECHNIQUE
  (one precise paragraph)

JUSTIFICATION
  (theorem / simulation / approximation bound)

LIMITATION / OPEN PROBLEM
  (what this paper leaves unsolved, specifically for your project)

HARDWARE METRICS (Pillar C only)
  Matrix family:
  Matrix dimension:
  Fixed-point word length:
  Technology node / FPGA family:
  Throughput:
  Area:
  Power:
  Condition number analysis: [ yes ] [ no ]

QUOTE (if needed — max 1 per paper, under 15 words)

CONNECTION TO YOUR WORK
  (one sentence on how this paper motivates, constrains, or is superseded by your project)
─────────────────────────────────────────────
```

---

*Guide prepared for Computer Engineering FYP: FPGA Implementation of Matrix Inversion for Decentralized LMMSE Equalization in Massive MIMO under Colored Noise.*
