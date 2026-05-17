# MATLAB Simulator — Zhao et al., IEEE JSAC 2025
## "Efficient LMMSE Equalization for Massive MIMO Under DBP Architecture"

---

## Requirements
- MATLAB R2020b or later
- No external toolboxes required  
  *(Signal Processing Toolbox optional; not used by core code)*
- QuaDRiGa channel model is used for physical channel generation.
  The implementation relies on QuaDRiGa v2.2.0 to reproduce 3GPP UMa fading.

---

## File Overview

| File | Description |
|------|-------------|
| `main_sim.m` | **Entry point.** Set `fig_select` and run. |
| `run_ser_sweep.m` | Monte-Carlo SER vs SNR loop over all algorithms |
| `run_table1.m` | Reproduces Table I (fronthaul data rates) |
| `lmmse_centralised.m` | Centralised LMMSE baseline (Eq. 3) |
| `zf_centralised.m` | Centralised ZF baseline |
| `bdac_mmse.m` | BDAC-MMSE (block-diagonal approx., Eq. 7) |
| `bcd_mmse_update.m` | One BCD-MMSE sweep — Algorithm 3, Eq. 30 |
| `lrd_algorithm.m` | Low-rank decomposition — Algorithm 4 |
| `bcd_mmse_lrd_update.m` | BCD-MMSE (LRD) update — Section IV-B |
| `dr_mmse.m` | sDR-MMSE (Alg. 1) and cDR-MMSE (Alg. 2) |
| `partition_clusters.m` | Split M-dim arrays into C clusters |
| `compute_local_cov.m` | Estimate local diagonal covariance blocks |
| `inv_stable.m` | Tikhonov-regularised matrix inversion |
| `get_constellation.m` | 16-QAM / QPSK constellations |
| `draw_symbols.m` | Random symbol draw |
| `detect.m` | Hard minimum-distance detection |
| `count_errors.m` | Symbol error counter |
| `apply_equalizer.m` | Apply block equalizer to received signal |
| `plot_results.m` | SER plots matching paper figures |
| `fronthaul_data_rate.m` | Table I fronthaul rate formulas |

---

## Quick Start

```matlab
% Reproduce Fig. 8(a): all equalizers, M=128, C=8, K=8
main_sim   % uses fig_select = 'fig8a' by default

% Change fig_select in main_sim.m to one of:
%   'fig6'  -> BCD-MMSE iterations  (Fig. 6)
%   'fig7'  -> BCD-MMSE(LRD) iters  (Fig. 7)
%   'fig8a' -> M=128, C=8,  K=8
%   'fig8b' -> M=256, C=8,  K=8
%   'fig8c' -> M=256, C=16, K=8
%   'fig8e' -> M=128, C=8,  K=12
%   'fig8f' -> M=128, C=8,  K=8,  IoT=20dB
%   'fig8g' -> M=128, C=8,  K=8,  QPSK

% Reproduce Table I
run_table1
```

---

## Key Parameters (Section VI-A)

| Parameter | Value |
|-----------|-------|
| BS antennas M | 128 or 256 |
| Clusters C | 8 or 16 |
| Target UEs K | 8 (or 12) |
| Noise samples N | 192 |
| Symbols per realisation | 480 |
| Monte Carlo realisations | 100 |
| Default IoT | 10 dB |
| Modulation | 16-QAM (or QPSK) |
| SNR range | −10 to +10 dB |
| LRD rank r | K |
| BCD iterations T | 4 |

---

## Algorithm–Equation Map

| MATLAB function | Paper reference |
|-----------------|-----------------|
| `lmmse_centralised` | Eq. (3) |
| `bdac_mmse` | Eq. (7) |
| `sdr_mmse` | Algorithm 1 / Eq. (15) |
| `cdr_mmse` | Algorithm 2 / Eq. (22) |
| `bcd_mmse_update` | Algorithm 3 / Eq. (30) |
| `lrd_algorithm` | Algorithm 4 / Eq. (33–34) |
| `bcd_mmse_lrd_update` | Section IV-B |

---

## Notes

1. **Coloured noise** is modelled as `R = beta*H_itf*H_itf' + sigma2*I`
   where `beta = (IoT-1)*sigma2` (Eq. 5, IoT definition in Section VI-A).

2. **BCD initialisation** uses BDAC-MMSE (Eq. 7) as stated in Algorithm 3.

3. The **daisy-chain ring** assumption means interaction variables are
   initialised from the sum over all clusters before the first sweep.

4. **LRD** approximates the full noise matrix with rank `r = K` factors,
   exploiting the fact that only K non-target UEs interfere.

5. For a faster test run, reduce `p.N_mc` to 20 and `p.N_sym` to 100
   in `main_sim.m`. Full accuracy requires the defaults (100 / 480).
