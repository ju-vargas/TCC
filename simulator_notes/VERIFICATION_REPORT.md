# Verification Report: Markdown Files vs Paper + Code

**Date:** May 17, 2026 (updated)
**Status:** ⚠️ **VERIFIED - Three critical implementation bugs found and fixed**

---

## Summary

Both markdown files (`simulation_parameters.md` and `notes_about_versions.md`) have been cross-checked against:
1. The paper.pdf  
2. The MATLAB implementation in `massive_mimo_dbp/` (main_sim.m, run_ser_sweep.m, etc.)
3. The QuaDRiGa integration code (generate_quadriga_channel.m)

**Conclusion:** The parameter descriptions were accurate, but three critical implementation bugs were found in the MATLAB code during SER curve validation. All have been fixed in both MATLAB and Python codebases.

---

## ✅ Verified Parameters (simulation_parameters.md)

| Parameter | Markdown | Code | Match | Notes |
|-----------|----------|------|-------|-------|
| SNR range | -10 to +10 dB, step 2 dB | `SNR_dB = -10:2:10` | ✓ | Exact match |
| Noise samples N | 192 | `N_samples = 192` | ✓ | Exact match |
| Symbols per realization | 480 | `N_sym = 480` | ✓ | Exact match |
| Monte Carlo trials | 100 | `N_mc = 100` | ✓ | Exact match |
| Modulation (default) | 16-QAM | `mod = '16QAM'` | ✓ | QPSK option also available |
| Symbol energy Es | 1 (normalized) | `Es = 1` | ✓ | Exact match |
| Non-target UEs r | 8 (fixed, all scenarios) | `r = 8` | ✓ | Fixed even for K=12 (Fig 8e) |
| Channel model | 3GPP UMa via QuaDRiGa | Confirmed in code | ✓ | LOS/NLOS mixed via 3GPP probability |
| UE placement | 120° sector, 50–100 m | Confirmed | ✓ | Exact match |
| BS antenna | Vertical ULA, λ/2 spacing | Confirmed | ✓ | M elements (128 or 256) |
| Default IoT | 10 dB | `IoT_dB = 10` | ✓ | Exact match |
| High IoT (Fig 8f) | 20 dB | `IoT_dB = 20` | ✓ | Exact match |
| LRD rank r | 8 | `p.r = 8` (Table I code) | ✓ | Rank-8 approximation |
| BCD iterations (main) | 4 | `T_bcd = 4` | ✓ | For SER curves (Figs 6–8) |
| BCD iterations (Table I) | 2 | `T_bcd = 2` (run_table1.m:14) | ✓ | For fronthaul budget analysis |

---

## ✅ Verified Algorithms (simulation_parameters.md)

All 6 algorithms are correctly described:

| Algorithm | Markdown Formula | Code Match | Status |
|-----------|------------------|-----------|--------|
| 0: Centralised LMMSE (Eq. 3) | W = (H^H R^{-1} H + Es^{-1} I)^{-1} H^H R^{-1} | lmmse_centralised.m | ✓ |
| 0b: ZF | W = (H^H H)^{-1} H^H | zf_centralised.m | ✓ |
| 0c: MMSE(AWGN) | R = σ²I (ignores interference) | run_ser_sweep.m:113 | ✓ |
| 1: BDAC-MMSE (Eq. 7) | Block-diagonal covariance approximation | bdac_mmse.m | ✓ |
| 2: sDR-MMSE (Alg 1) | Star topology with rank-independent transfer | sdr_mmse.m | ✓ |
| 3: cDR-MMSE (Alg 2) | Concatenate compressed signals at CU | cdr_mmse.m | ✓ |
| 4: BCD-MMSE (Alg 3) | Daisy-chain iterations (Eq. 30) | bcd_mmse_update.m | ✓ |
| 5: LRD (Alg 4) | Low-rank SVD decomposition | lrd_algorithm.m | ✓ |

---

## ✅ Verified QuaDRiGa Implementation (notes_about_versions.md)

| Claim | Status | Evidence |
|-------|--------|----------|
| Path setup with addpath (genpath) | ✓ | Confirmed in all simulation files |
| `qd_simulation_parameters` settings | ✓ | generate_quadriga_channel.m:75–78 |
| `set_scenario` accepts only single string in v2.2.0 | ✓ | generate_quadriga_channel.m:95 |
| Three-step builder flow (init → gen_parameters → get_channels) | ✓ | generate_quadriga_channel.m:102–104 |
| `gen_parameters` handles all LSF + SSF | ✓ | Documented in code comment |
| Calling gen_lsf/gen_ssf separately causes "deleted parameters" warnings | ✓ | Noted in generate_quadriga_channel.m:97–100 |
| coeff dimensions: [M_rx × M_tx × paths × snapshots] | ✓ | generate_quadriga_channel.m:107–110 |
| Correct extraction: `sum(chan(k).coeff(1,:,:,1), 3)` | ✓ | generate_quadriga_channel.m:120 |
| No `deg2rad` in R2014a; use `x * π/180` | ✓ | generate_quadriga_channel.m:50 |
| Handle copy: use `.copy` method not `=` | ✓ | Best practice, applied throughout |

---

## 📝 Minor Suggestions for Improvement

### 1. **simulation_parameters.md** — Note on Table I BCD Iterations
**Location:** Section 7, Table I Parameters  
**Current:** Lists `T (BCD iterations for table): 2`  
**Suggestion:** Add clarification:
```
T (BCD iterations for table):     2
  Note: Different from main simulation (T=4). Section VI-C justifies Iter1 and Iter4
  for equal bandwidth budget comparison.
```

**Rationale:** Users might be confused why main_sim.m uses T=4 but Table I uses T=2.

---

### 2. **notes_about_versions.md** — Clarity on Multiple Scenarios

**Location:** Step 6 — Scenario Assignment  
**Current Text:** "Solution for mixed LOS/NLOS in v2.2.0: Run two separate `qd_layout` objects..."  
**Suggestion:** Expand slightly:
```
In v2.2.0, per-UE scenario assignment is implemented by running two separate 
qd_layout objects: one for LOS UEs and one for NLOS UEs. The LOS probability 
is computed per UE using the 3GPP 38.901 formula (shown in generate_quadriga_channel.m:40–42).
```

**Rationale:** Readers may want to understand where the LOS/NLOS split logic is located.

---

### 3. **notes_about_versions.md** — Supported Scenarios Clarification

**Location:** Step 6 — "How to find available scenario names"  
**Current:** Shows how to find scenarios using `dir(fullfile(conf_dir, '*UMa*.conf'))`  
**Suggestion:** Add note:
```
% The qd_builder.supported_scenarios method exists in v2.2.0 but requires
% a builder object to be created first. The config-file listing above is 
% more direct for exploring options.
```

**Rationale:** Clarifies why the manual config-file search is recommended over method calls.

---

## 🔧 Cross-Validation Checklist

- [x] SNR definition matches paper (SNR = 10·log10(Es/σ²))
- [x] IoT definition corrected: IoT = 10·log10((β·r + σ²)/σ²)
- [x] β formula corrected: β = (IoT_lin − 1)·σ²/r  ⚠️ **was missing /r**
- [x] Non-target UEs always r=8 (even for K=12 scenarios)
- [x] Noise covariance estimated via Eq. 6: R̂ = (1/N)·Σ nⁱ(nⁱ)^H
- [x] LMMSE uses R_true (perfect CSI benchmark)  ⚠️ **was using R_est**
- [x] Channel power normalized per-column: ||h_k||²/M = 1  ⚠️ **was global normalization**
- [x] QuaDRiGa 3GPP UMa LOS/NLOS split implemented correctly
- [x] All 6 algorithms implemented per paper equations
- [x] BCD ring topology: iteration 1 receives results from iteration 0 (BDAC initialization)
- [x] LRD rank fixed at r=K=8 (even for K=12 in Fig 8e)
- [x] Table I fronthaul rates computed with T=2 (not T=4)

---

## Cross-Validation with Paper.md

✅ **All major parameters directly confirmed in paper.md (Section VI.A):**
- M ∈ {128, 256} antennas
- C ∈ {8, 16} clusters  
- K = 8 target UEs (paper explicitly states: "both set to K=8")
- r = 8 non-target UEs (paper: "The number of target and non-target UEs is both set to K=8")
- N = 192 noise samples
- IoT = 10 dB default
- 3GPP 38.901 UMa scenario

✅ **Algorithm equations all match paper text:**
- Eq. (3): LMMSE formula W_MMSE = (H^H R^{-1} H + (1/E_s) I)^{-1} H^H R^{-1}
- Eq. (6): Noise covariance R = (1/N) Σ n^i (n^i)^H  
- Eq. (7): BDAC-MMSE (block-diagonal approximation)
- Algorithms 1–4: sDR-MMSE, cDR-MMSE, BCD-MMSE, LRD all confirmed

⚠️ **Minor note:** Some specific test cases (K=12 Fig 8e, IoT=20dB Fig 8f, QPSK Fig 8g) are in the code but not explicitly discussed in the provided paper sections. These are reasonable extensions consistent with the paper's framework.

---

## Conclusion

⚠️ **Three critical implementation bugs were found during SER curve validation** (see `matlab_scripts_analysis.md` for full details):
1. β scaling missing `/r` — actual IoT was 18.6 dB instead of 10 dB
2. LMMSE used R_est instead of R_true — broke expected curve ordering
3. Global channel normalization instead of per-column — caused 4590× UE power imbalance

All bugs have been fixed in both MATLAB and Python. SER curves now match the paper's Figure 8(a) qualitatively.

**Recommendation:** Re-export QuaDRiGa channels with the corrected per-column normalization (`export_quadriga_channels.m`) before running final validation.

---

*Verified against:*
- **Paper source:** paper.md (IEEE JSAC 2025 full transcript)
- **MATLAB code:**
  - `main_sim.m`  
  - `run_ser_sweep.m`  
  - `run_table1.m`  
  - `generate_quadriga_channel.m`  
  - Algorithm files (bdac_mmse.m, bcd_mmse_update.m, lrd_algorithm.m, sdr_mmse.m, cdr_mmse.m)  
  - Supporting utilities (compute_local_cov.m, partition_clusters.m, etc.)
- **Verification date:** May 16, 2026
