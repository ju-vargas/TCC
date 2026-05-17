# Massive MIMO DBP Simulator: Comprehensive Analysis

This document provides a complete analysis of the MATLAB scripts in the `massive_mimo_dbp` repository. It integrates the theoretical system models, algorithmic structures, simulation parameters, and version-specific implementation details into the descriptions of the individual scripts.

---

## Bugs Found & Fixes Applied

Three critical bugs were identified that caused SER curves to diverge from the paper's results. All have been fixed in both the MATLAB and Python codebases.

### Bug 1: β scaling missing `/r` (Critical)

**File:** `run_ser_sweep.m` line 78

The interference scaling parameter β in `R = β·H̄·H̄ᴴ + σ²I` was computed as:

```matlab
% WRONG (original):
beta = max((IoT - 1) * sigma2, 0);

% CORRECT (fixed):
beta = (IoT_lin - 1) * sigma2 / p.r;
```

**Root cause:** With per-column normalization, `trace(H̄·H̄ᴴ)/M ≈ r`. The per-antenna interference power is `β·r`, not `β`. So the IoT formula `(β·r + σ²)/σ² = IoT_lin` gives `β = (IoT_lin - 1)·σ²/r`. The original code produced an actual IoT of **18.6 dB** instead of 10 dB (with r=8), making interference 8× too strong.

### Bug 2: LMMSE must use R_true, not R_est (Critical)

**File:** `run_ser_sweep.m` line 107

```matlab
% WRONG (original):
W = lmmse_centralised(H_tgt, R_est, p.Es);

% CORRECT (fixed):
W = lmmse_centralised(H_tgt, R_true, p.Es);
```

**Root cause:** The paper's centralized LMMSE is a gold-standard benchmark with **perfect knowledge of R**. With only N=192 samples and M=128 dimensions (ratio N/M = 1.5), the sample covariance R_est is poorly conditioned. Using R_est caused the centralized LMMSE to perform *worse* than decentralized methods, violating the expected ordering.

### Bug 3: Channel normalization must be per-column (Critical)

**File:** `generate_quadriga_channel.m` lines 63–70

```matlab
% WRONG (original): Global normalization (same scale for all UEs)
avg_power = mean(sum(abs(H_full).^2, 1)) / p.M;
H_full = H_full / sqrt(avg_power);

% CORRECT (fixed): Per-column normalization (each UE individually)
for k = 1:n_UE_total
    col_pow = sum(abs(H_full(:,k)).^2) / p.M;
    if col_pow > 0
        H_full(:,k) = H_full(:,k) / sqrt(col_pow);
    end
end
```

**Root cause:** QuaDRiGa's 3GPP UMa model produces realistic path loss, creating **up to 4590× power imbalance** between near-LOS and far-NLOS UEs. Global normalization preserves these differences, making weak UEs effectively undetectable. Per-column normalization ensures every UE has `||h_k||²/M = 1`, equivalent to perfect uplink power control. This is the standard assumption in massive MIMO simulation literature and is required for the paper's SNR definition `SNR = Es/σ²` to be meaningful for every UE.

---

## Core Simulation Scripts

### 1. `main_sim.m`
- **Description:** Main simulation script that reproduces Figures 6, 7, and 8 of the paper.
- **System Model & Parameters:** 
  - Simulates the uplink signal model $y = Hs + n$ with colored noise $R = \beta H_{bar}H_{bar}^H + \sigma^2 I$.
  - Configures global parameters: BS antennas $M$ (128 or 256), Clusters $C$ (8 or 16), Target UEs $K$ (8 or 12), Non-target UEs $r$ (always 8), noise samples $N=192$, symbols $480$, 100 Monte Carlo realisations, and modulation (16QAM or QPSK).
  - Sweeps SNR from -10 to +10 dB. SNR is defined using background AWGN only ($\sigma^2$), not total noise power.
  - Interference-over-thermal (IoT) is typically 10 dB (20 dB for Fig. 8f).
- **Implementation Note:** Controls which figure to run and sets the `p` struct accordingly.

### 2. `run_ser_sweep.m`
- **Description:** Runs the Monte-Carlo simulation loop to compute SER vs SNR for selected equalizers.
- **Details:** 
  - Replicates specific algorithm sets per figure (e.g., Fig 8a: LMMSE, ZF, BCD iter1, LRD iter4, sDR, cDR). BCD iter1 and LRD iter4 are chosen to represent similar communication bandwidth budgets.
  - The centralized LMMSE benchmark uses the **true** covariance R_true (perfect CSI), while all decentralized methods estimate R from N=192 noise samples.
  - Interference scaling: `beta = (IoT_lin - 1) * sigma2 / r`, ensuring the actual per-antenna IoT matches the target.
  - Noise samples are drawn from `CN(0, R_true)` via Cholesky factorization, consistent with the paper's Gaussian noise model `n ~ CN(0, R)`.

### 3. `generate_quadriga_channel.m`
- **Description:** Generates one QuaDRiGa channel realization using v2.2.0 (large- and small-scale fading).
- **Channel Model:** 3GPP UMa (Urban Macro) scenario. UEs are placed uniformly in a 120° sector, radius 50–100 m, centred at the BS. Both target and interfering UEs are modelled similarly.
- **QuaDRiGa v2.2.0 Implementation Notes:**
  - Uses `qd_simulation_parameters` with `use_3GPP_baseline = 1` and `center_frequency = 2e9`.
  - BS uses a Vertical ULA created with `qd_arrayant('omni')`.
  - **Critical Version Differences:** In v2.2.0, `set_scenario` strictly requires a single string. To mix LOS/NLOS per UE, the script runs two separate `qd_layout` objects. `gen_parameters` is called alone to handle ALL parameters (calling `gen_lsf_parameters` separately causes warnings).
  - Channel coefficients extraction: `chan(k).coeff` dimensions are `[M_rx x M_tx x n_paths x n_snapshots]` (1 x M x paths x snap).
  - **Normalisation (FIXED):** Each UE column is independently normalized so `||h_k||²/M = 1`. This is equivalent to perfect uplink power control and ensures the SNR definition `Es/σ²` applies equally to all UEs. **The original global normalization caused up to 4590× power imbalance between UEs.**

### 4. `export_quadriga_channels.m`
- **Description:** Exports QuaDRiGa channel realisations to `.mat` files for use in the Python simulator.
- **Output:** `channels_{fig}_{M}_{C}_{K}.mat` containing `H_tgt_all` (M×K×N_mc) and `H_itf_all` (M×r×N_mc), saved with `-v7` for `scipy.io.loadmat` compatibility.

### 5. `partition_clusters.m`
- **Description:** Splits $M$-dimensional arrays (channel $H$, received signal $y$, noise $n$) into $C$ antenna clusters.
- **Architecture:** Fits the DBP (Decentralized Baseband Processing) architecture where vectors are partitioned into $C$ blocks of size $M_c \times 1$.

### 6. `compute_local_cov.m`
- **Description:** Computes local diagonal blocks of the noise covariance estimated at each Distributed Unit (DU).
- **Architecture:** $R$ is a $C \times C$ block matrix. Each DU $c$ computes its local block $R_{cc} = \frac{1}{N} \sum n_c^i (n_c^i)^H$. Off-diagonal blocks $R_{mn}$ are NOT available locally.

## Baseline Centralised Equalizers

### 7. `lmmse_centralised.m`
- **Description:** Centralised LMMSE equalizer (Algorithm 0). Serves as the **gold-standard upper bound** using the true covariance R.
- **Algorithm:** $W_{MMSE} = (H^H R^{-1} H + \frac{1}{E_s}I)^{-1} H^H R^{-1}$
- **Complexity:** Requires full $H$ ($M \times K$) and full $R$ ($M \times M$) at one location. $O(M^3 + N M^2)$.
- **Note:** In the simulation, LMMSE uses R_true (not the estimated R_est), as it represents a centralized benchmark with perfect CSI.

### 8. `zf_centralised.m`
- **Description:** Centralised Zero-Forcing (ZF) equalizer.
- **Algorithm:** $W_{ZF} = (H^H H)^{-1} H^H$. Ignores noise structure entirely.

## Decentralized Equalizer Algorithms

### 9. `bdac_mmse.m`
- **Description:** Block-Diagonal Approximate Covariance (BDAC) MMSE equalizer (Algorithm 1).
- **Algorithm:** Approximates $R$ with block-diagonal $R_B$. Each DU computes $H_c^H R_{cc}^{-1} H_c$. CU performs a $K \times K$ inversion and broadcasts it.
- **Role:** Yields poor performance under colored noise but is used as the initialiser for BCD methods.

### 10. `sdr_mmse.m`
- **Description:** Superimposed Dimensionality Reduction (sDR) MMSE (Algorithm 2). Uses a Star architecture.
- **Algorithm:** 
  - **DU Preprocessing:** Each DU computes a compression matrix $Q_c = H_c^H R_{cc}^{-1}$ and sends $Q_c y_c$, $Q_c H_c$, and compressed noise samples $\{Q_c n_c^i\}$ to the CU.
  - **CU Processing:** Superimposes the compressed data to form $y_{check}$, $H_{check}$, and $R_{check}$ (all of dimension $K$), then runs LMMSE.
  - **Data Transfer:** $K \times K$ and $K \times N$ per DU (independent of $M$).

### 11. `cdr_mmse.m`
- **Description:** Concatenated Dimensionality Reduction (cDR) MMSE (Algorithm 3). Uses a Star architecture.
- **Algorithm:** Same local compression $Q_c$ and DU preprocessing as sDR-MMSE. However, the CU concatenates the data into $CK \times 1$ and $CK \times K$ structures instead of superimposing them.
- **Performance:** Always $\geq$ sDR-MMSE, but requires a $CK \times CK$ inversion at the CU and does not scale well to daisy chain topologies.

### 12. `bcd_mmse_update.m`
- **Description:** One Gauss-Seidel BCD sweep over all $C$ clusters for the BCD-MMSE daisy chain architecture (Algorithm 4).
- **Algorithm:**
  - **Initialisation:** Uses BDAC-MMSE. Interaction variables $A_0^0$ and $b_{0,i}^0$ are the full sum over all clusters.
  - **Iterations:** A ring topology passes running sums $A_c^l$ ($K \times K$) and $b_{c,i}^l$ ($K \times N$) between DUs.
  - **Data Transfer:** $K \times K$ plus $K \times N$ per iteration. Size is independent of $M$. Guaranteed convergence to global minimum.

### 13. `lrd_algorithm.m`
- **Description:** Decentralised low-rank decomposition (LRD) algorithm (Algorithm 5).
- **Algorithm:** Replaces $N$ noise samples with $r \ll N$ column vectors (rank $r = K = 8$). It performs a sequential daisy-chain SVD on the scaled noise matrices, avoiding the transfer of all $N$ samples. The resulting low-rank factors $G$ satisfy $GG^H \approx R_{est}$.

### 14. `bcd_mmse_lrd_update.m`
- **Description:** One Gauss-Seidel BCD sweep using LRD (Algorithm 6).
- **Algorithm:** Replaces noise samples $N_c$ with the LRD factors $G_c$ ($M_c \times r$) in inter-DU transfers. The interaction variable $b$ ($K \times N$) is replaced by $B$ ($K \times r$).
- **Critical Detail:** The local denominator in the update still uses the FULL local covariance $R_{cc} = \frac{1}{N} N_c N_c^H$ to properly include the $\sigma^2 I$ AWGN floor that a rank-$r$ approximation would miss.

## Fronthaul Data Rate Scripts

### 15. `run_table1.m`
- **Description:** Reproduces Table I of the paper for fronthaul data rate comparison.
- **Parameters:** 5G NR worst-case parameters: $N_{sc,PRB} = 12$, $N_{PRB} = 275$, $N_u = 3300$, $T_{OFDM} = 1/120 \text{ kHz}$, bit-width $w=12$, $N=192$, $r=8$, $T_{bcd}=2$.
- **Scenarios:** Tests $M=128, C=2$; $M=128, C=4$; and $M=256, C=4$.

### 16. `fronthaul_data_rate.m`
- **Description:** Computes the total fronthaul data rates (Tbps) for the scenarios provided by `run_table1.m`, calculating the formulation and filtering payload sizes for Centralised, sDR/cDR, BCD, and BCD-LRD methods.

## Utility Scripts

### 17. `apply_equalizer.m`
- **Description:** Applies a block equalizer $W_{cell}$ to a partitioned received signal $Y_c$.

### 18. `count_errors.m`
- **Description:** Counts the number of symbol errors by comparing detected symbols $S_{det}$ with transmitted symbols $S_{tx}$.

### 19. `detect.m`
- **Description:** Performs hard minimum-distance symbol detection against the given constellation.

### 20. `draw_symbols.m`
- **Description:** Draws $K \times N_s$ i.i.d. symbols uniformly from a given constellation.

### 21. `get_constellation.m`
- **Description:** Returns the normalised constellation and bits-per-symbol (bpS) for '16QAM' or 'QPSK'.

### 22. `inv_stable.m`
- **Description:** Performs regularised (Tikhonov) matrix inversion (`(A + reg*I) \ I`) to avoid numerical singularity.

### 23. `plot_results.m`
- **Description:** Generates SER vs SNR plots matching the paper's figures. Saves output as `.png` files.

---

## Python Simulator Port

A complete Python port of the simulator is available in `massive_mimo_dbp/python/`. It uses NumPy/SciPy and includes all bug fixes listed above. It supports two channel modes:

| File | Purpose |
|---|---|
| `config.py` | `SimConfig` dataclass + `make_config()` factory for each figure |
| `constellation.py` | 16QAM/QPSK constellation + `draw_symbols()` |
| `utils.py` | `partition_clusters`, `compute_local_cov`, `detect`, `count_errors`, `inv_stable` |
| `channel.py` | i.i.d. Rayleigh channel + `.mat` file loader with per-column normalization |
| `equalizers.py` | All 8 algorithms: LMMSE, ZF, BDAC, sDR, cDR, BCD, LRD, BCD-LRD |
| `run_sim.py` | Monte Carlo SER sweep with corrected β/r fix and R_true for LMMSE |
| `plot_results.py` | SER vs SNR plots matching paper style |
| `main.py` | CLI entry point with `--quick`, `--N_mc`, `--seed`, `--channel` options |

### Usage

```bash
# Quick test (5 MC, coarse SNR grid, ~20s)
.venv/bin/python3 python/main.py fig8a --quick

# Full run with i.i.d. Rayleigh channels (100 MC)
.venv/bin/python3 python/main.py fig8a

# Run with exported QuaDRiGa channels
.venv/bin/python3 python/main.py fig8a --channel mat_file \
    --mat_file channels_fig8a_M128_C8_K8.mat
```

### Virtual Environment

The Python simulator uses a virtual environment at `massive_mimo_dbp/.venv/` with the following packages:
- `numpy`, `scipy`, `matplotlib` — core numerical/plotting libraries
- `quadriga-lib` — C++/Python QuaDRiGa utilities (v0.11.5, low-level only)

---

## Expected Algorithm Performance Ordering

Based on validated simulations matching the paper's Figure 8(a):

```
LMMSE (best) > BCD-MMSE > cDR-MMSE > LRD4 ≈ sDR-MMSE > ZF (worst)
```

Key observations:
- LMMSE is the centralized benchmark with perfect R — always the best.
- BCD-MMSE (1 iteration) approaches LMMSE closely; 2-3 iterations are sufficient to converge.
- cDR-MMSE outperforms sDR-MMSE because it preserves cross-cluster noise correlations.
- BCD-MMSE(LRD) trades noise sample fidelity for bandwidth reduction; performance is between BCD and cDR.
- ZF is always the worst because it ignores noise structure entirely.