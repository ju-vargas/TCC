## 1. System Model

**Uplink signal model (Eq. 1):**
```
y = H*s + n
y ∈ C^{M×1}  received signal at BS
H ∈ C^{M×K}  channel matrix (target UEs to BS)
s ∈ S^{K×1}  transmitted symbol vector
n ~ CN(0, R)  colored noise
R = E[n*n^H]  noise covariance matrix (M×M)
```

**Interference model (Eq. 5):**
```
n = H_bar * s_bar + n_bar
H_bar ∈ C^{M×r}   channel of r non-target (interfering) UEs
s_bar ∈ S^{r×1}   interfering symbols
n_bar ~ CN(0, σ²I) background AWGN
R = β*H_bar*H_bar^H + σ²*I
β = power of interference signals
```

---

## 2. Simulation Parameters (Section VI-A)

| Parameter | Value |
|---|---|
| BS antennas M | 128 or 256 |
| Clusters C | 8 or 16 |
| Antennas per cluster Mc | M/C |
| Target UEs K | 8 (or 12 in Fig. 8e) |
| Non-target UEs r | 8 (fixed — same as K, never changes) |
| Noise samples N | 192 |
| Modulation | 16-QAM (QPSK in Fig. 8g) |
| Symbols per realisation | 480 |
| Monte Carlo realisations | 100 |
| Symbol energy Es | 1 (normalised) |
| SNR definition | SNR = 10·log10(Es/σ²) |
| SNR range | −10 to +10 dB (step 2 dB) |
| Default IoT | 10 dB |
| High IoT (Fig. 8f) | 20 dB |
| IoT definition | IoT = 10·log10((β + N₀)/σ²) |

**Note on IoT:** N₀ in the IoT formula is the background noise power, which equals σ². So β = (10^(IoT/10) − 1)·σ².

---

## 3. Channel Model (Section VI-A)

- **Platform:** QuaDRiGa (not i.i.d. Rayleigh)
- **Scenario:** 3GPP UMa (Urban Macro), considers both large-scale and small-scale fading
- **UE placement:** Uniformly distributed in a 120° sector, radius 50–100 m, centred at BS
- **Both target and interfering UEs** are modelled similarly via QuaDRiGa
- **Noise covariance** estimated from samples: R̂ = (1/N)·∑ nⁱ(nⁱ)^H (Eq. 6)
- **Channel assumed perfectly known** at receiver (ideal CSI)

---

## 4. DBP Architecture Parameters

**Cluster partitioning:**
```
y = [y1^T, y2^T, ..., yC^T]^T
H = [H1^T, H2^T, ..., HC^T]^T
n = [n1^T, n2^T, ..., nC^T]^T
yc = Hc*s + nc,   c = 1,...,C
Hc ∈ C^{Mc×K},  nc ∈ C^{Mc×1}
```

**Noise covariance block structure:**
```
R is C×C block matrix
Rcc = (1/N)*∑ nc^i*(nc^i)^H   ← available locally at DU c
Rmn (m≠n)                      ← NOT available locally (requires data exchange)
```

---

## 5. Algorithms

### Algorithm 0: Centralised LMMSE (Eq. 3) — Baseline upper bound
```
W_MMSE = (H^H * R^{-1} * H + (1/Es)*I)^{-1} * H^H * R^{-1}
Complexity: O(M³ + N·M²)
Requires: full H (M×K) and R (M×M) at one location
```

### Algorithm 0b: Centralised ZF — Baseline
```
W_ZF = (H^H * H)^{-1} * H^H
Ignores noise structure entirely
```

### Algorithm 0c: MMSE(AWGN) — Baseline (Figs. 6–7 only)
```
W = (H^H*H + (σ²/Es)*I)^{-1} * H^H
Uses diagonal R = σ²*I, ignoring interference
```

### Algorithm 1: BDAC-MMSE — Baseline/Initialiser (Eq. 7)
```
Approximates R with block-diagonal RB = blkdiag(R11,...,RCC)

Step 1 (each DU c):
  Compute Hc^H * Rcc^{-1} * Hc   (K×K local Gram matrix)

Step 2 (CU):
  A_inv = (∑c Hc^H*Rcc^{-1}*Hc + (1/Es)*I)^{-1}   (K×K inversion)

Step 3 (broadcast A_inv to all DUs):
  Wc = A_inv * Hc^H * Rcc^{-1}   (K×Mc local equalizer block)

Data transfer: K×K matrices only
Performance: poor under colored noise (ignores off-diagonal R)
Use: initialiser for BCD methods; plotted in Figs. 6–7
```

### Algorithm 2: sDR-MMSE — Star architecture (Algorithm 1 in paper, Eqs. 11–16)
```
Local compression matrix at DU c: Qc = Hc^H * Rcc^{-1}   (K×Mc)

Step 1 (each DU c, in parallel):
  Compute Qc*yc        (K×1)
  Compute Qc*Hc        (K×K)
  Compute {Qc*nc^i}    (K×N)  ← N noise samples compressed
  Send all to CU

Step 2 (CU — superimpose):
  y_check = ∑c Qc*yc           (K×1, Eq. 13a)
  H_check = ∑c Qc*Hc           (K×K, Eq. 13a)
  R_check = (1/N)*∑m∑l∑i (Qm*nm^i)*(Ql*nl^i)^H   (K×K, Eq. 14)
  W = (H_check^H * R_check^{-1} * H_check + (1/Es)*I)^{-1}
      * H_check^H * R_check^{-1}                   (K×K, Eq. 15)
  s_hat = W * y_check                              (Eq. 16)

Data transfer: K×K and K×N per DU (independent of M)
Note: lossless when R = RB (block diagonal)
```

### Algorithm 3: cDR-MMSE — Star architecture (Algorithm 2 in paper, Eqs. 17–23)
```
Same local compression: Qc = Hc^H * Rcc^{-1}   (K×Mc)
Same DU preprocessing as sDR (send Qc*yc, Qc*Hc, {Qc*nc^i} to CU)

Step 2 (CU — concatenate):
  y_tilde = [Q1*y1; Q2*y2; ...; QC*yC]           (CK×1, Eq. 19)
  H_tilde = [Q1*H1; Q2*H2; ...; QC*HC]           (CK×K, Eq. 19)
  R_tilde block (m,l) = (1/N)*∑i (Qm*nm^i)*(Ql*nl^i)^H  (K×K, Eq. 21)
  R_tilde is CK×CK full block matrix              (Eq. 20)
  W = (H_tilde^H * R_tilde^{-1} * H_tilde + (1/Es)*I)^{-1}
      * H_tilde^H * R_tilde^{-1}                  (K×CK, Eq. 22)
  s_hat = W * y_tilde                             (Eq. 23)

Data transfer: same as sDR, but CK×CK inversion at CU
Performance: always ≥ sDR-MMSE (Proposition 1)
Note: does NOT scale to daisy chain (bandwidth grows with C)
```

### Algorithm 4: BCD-MMSE — Daisy chain architecture (Algorithm 3 in paper, Eqs. 24–30)
```
Initialisation:
  W^0 = BDAC-MMSE result (cell array of K×Mc blocks)
  A^0_0 = ∑c W^0_c * Hc        (K×K)
  b^0_{0,i} = ∑c W^0_c * nc^i  (K×1, for each i=1..N)

BCD iterations (l = 1 to T, T=4):
  Gauss-Seidel sweep: for c = 1 to C:

    Receive from previous DU: A^l_{c-1} (K×K) and {b^l_{c-1,i}} (K×1 each)

    Update W^l_c (Eq. 30):
      numerator = Es*(I - A^l_{c-1} + W^{l-1}_c*Hc)*Hc^H
                  - (1/N)*∑i (b^l_{c-1,i} - W^{l-1}_c*nc^i)*(nc^i)^H
      denominator = Es*Hc*Hc^H + (1/N)*∑i nc^i*(nc^i)^H
      W^l_c = numerator * denominator^{-1}

    Update interaction variables (Eqs. 28–29):
      A^l_c = A^l_{c-1} - W^{l-1}_c*Hc + W^l_c*Hc
      b^l_{c,i} = b^l_{c-1,i} - W^{l-1}_c*nc^i + W^l_c*nc^i  ∀i

    Send A^l_c and {b^l_{c,i}} to next DU

Symbol estimation:
  s_hat = ∑c W^T_c * yc

Key properties:
  - Guaranteed convergence to global minimum (Theorem 2)
  - Data transfer size independent of M
  - Data transfer at each iteration: K×K (A) + K×N (b, all samples)
  - Initialised with BDAC-MMSE
  - Ring topology: DU C sends to DU 1 to close the loop
```

### Algorithm 5: LRD — Low-rank decomposition (Algorithm 4 in paper, Eqs. 31–34)
```
Purpose: replace N noise samples with r << N column vectors
Rank used: r = K = 8

Define scaled noise matrix: N_tilde = (1/√N)*[n^1,...,n^N] ∈ C^{M×N}
Partitioned: Nc ∈ C^{Mc×N} at DU c (scaled)

Sequential daisy-chain SVD:
  For c = 1 to C-1:
    if c=1: N_approx = empty
    else:   N_approx = D_{c-1} * V_{c-1}^H   (reconstruct approx of [N1;...;N_{c-1}])
    
    N_stack = [N_approx^T; Nc^T]^T
    [Uc, Sc, Vc] = rank-r SVD of N_stack
    Dc = Uc * Sc   (cMc × r)
    
    Transfer Dc and Vc to next DU

  At last DU C:
    N_approx = D_{C-1} * V_{C-1}^H
    N_stack = [N_approx^T; NC^T]^T
    [UC, SC, VC] = rank-r SVD of N_stack
    Broadcast VC (N×r) to ALL DUs

  Each DU c computes locally:
    Gc = Nc * VC   (Mc×r)    ← Note: Nc here is the SCALED version

Result: G = [G1^T;...;GC^T]^T ∈ C^{M×r}
Property: G*G^H ≈ R_est = (1/N)*N_full*N_full^H
```

### Algorithm 6: BCD-MMSE (LRD) — Section IV-B
```
Replace noise samples Nc (Mc×N) with Gc (Mc×r) in inter-DU transfers ONLY.
Local denominator still uses Rcc = (1/N)*Nc*Nc^H (full, includes σ²I).

Interaction variables change:
  A_c = ∑j W_j * Hj          (K×K — unchanged)
  B_c = ∑j W_j * Gj          (K×r — replaces b of size K×N)

Update W^l_c:
  numerator = Es*(I - A_{c-1} + W^{l-1}_c*Hc)*Hc^H
              - B_{c-1} * Gc^H     ← low-rank cross-cluster term
  denominator = Es*Hc*Hc^H + Rcc  ← FULL local covariance (not Gc*Gc^H)
  W^l_c = numerator * denominator^{-1}

  Update:
    A_c = A_{c-1} - W^{l-1}_c*Hc + W^l_c*Hc
    B_c = B_{c-1} - W^{l-1}_c*Gc + W^l_c*Gc

Data transfer per iteration: K×K (A) + K×r (B) — independent of N
```

---

## 6. Figure-by-Figure Scenario Matrix

| Figure | M | C | K | IoT | Mod | Algorithms shown |
|---|---|---|---|---|---|---|
| 6(a) | 128 | 8 | 8 | 10 | 16QAM | LMMSE, ZF, MMSE(AWGN), BDAC, BCD iter 1–4 |
| 6(b) | 256 | 8 | 8 | 10 | 16QAM | same |
| 6(c) | 256 | 16 | 8 | 10 | 16QAM | same |
| 7(a) | 128 | 8 | 8 | 10 | 16QAM | LMMSE, ZF, BDAC, LRD iter 1–4 |
| 7(b) | 256 | 8 | 8 | 10 | 16QAM | same |
| 7(c) | 256 | 16 | 8 | 10 | 16QAM | same |
| 8(a) | 128 | 8 | 8 | 10 | 16QAM | LMMSE, ZF, BCD iter1, LRD iter4, sDR, cDR |
| 8(b) | 256 | 8 | 8 | 10 | 16QAM | same |
| 8(c) | 256 | 16 | 8 | 10 | 16QAM | same |
| 8(e) | 128 | 8 | **12** | 10 | 16QAM | same |
| 8(f) | 128 | 8 | 8 | **20** | 16QAM | same |
| 8(g) | 128 | 8 | 8 | 10 | **QPSK** | same |

**Note on Fig. 8:** BCD iter1 and LRD iter4 are specifically chosen to represent similar communication bandwidth budgets (Section VI-C).

---

## 7. Table I Parameters (Fronthaul Data Rate)

| Parameter | Value |
|---|---|
| Nsc,PRB | 12 |
| NPRB | 275 |
| Nu = Nsc,PRB × NPRB | 3300 |
| TOFDM | 1/120 kHz |
| Bit-width w | 12 bits |
| N (noise samples) | 192 |
| r (LRD rank) | 8 |
| T (BCD iterations for table) | 2 |
| Scenarios | Case 1: M=128,C=2,K=8 / Case 2: M=128,C=4,K=8 / Case 3: M=256,C=4,K=8 |

---

## 8. Critical Implementation Notes

**A. The non-target UEs are generated the same way as target UEs** (Section VI-A: *"non-target UEs are modelled similarly to the target UEs"*). Both use QuaDRiGa with the same scenario, placement distribution, and normalisation.

**B. r is always 8**, even for Fig. 8(e) where K=12. The number of non-target interferers does not change with the number of target UEs.

**C. The noise covariance R is never directly available.** It is always estimated from samples via Eq. (6). The algorithms work with R̂, not the true R.

**D. The BCD ring initialisation** (Algorithm 3 lines 3–8): A⁰₀ and b⁰_{0,i} are initialised to zero, then accumulated over all C clusters using W⁰ (BDAC result). This means at iteration l=1, the "previous DU's" variables passed to DU 1 are A⁰_C and b⁰_{C,i} — the full sum over all clusters from the BDAC initialisation.

**E. For BCD-MMSE (LRD)**, the LRD algorithm (Algorithm 5) must be run once before the BCD iterations begin. The resulting Gc matrices are then used in place of Nc throughout all BCD-LRD iterations.

**F. SNR is defined using background AWGN only** (σ²), not total noise power. The interference adds on top of this through R.