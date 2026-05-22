# Simulator Notes

This folder contains the documentation and verification material used to reproduce the results of the target paper.

## Files
- `simulation_parameters.md` — Extracted simulation parameter definitions from the paper (Section VI-A).
- `notes_about_versions.md` — Version-specific QuaDRiGa implementation notes and compatibility guidance for QuaDRiGa v2.2.0 and MATLAB R2014a.
- `matlab_scripts_analysis.md` — Comprehensive analysis of all MATLAB scripts, including bugs found and fixes applied, plus Python port documentation.
- `VERIFICATION_COMPLETE.md` — Summary verification status.
- `VERIFICATION_REPORT.md` — Detailed cross-validation report.
- `paper.md` — Full article transcript used as the source of truth.

## Bugs Found & Fixed

Three critical implementation bugs were identified and corrected (see `matlab_scripts_analysis.md` for details):
1. **β/r scaling** — interference was 8× too strong (actual IoT ≈ 18.6 dB instead of 10 dB)
2. **LMMSE used R_est** — should use R_true as a perfect-CSI benchmark
3. **Global channel normalization** — should be per-column (up to 4590× UE power imbalance)

## Purpose

These notes are the authoritative reference for:
- simulation parameters (M, C, K, r, N, N_sym, N_mc, IoT, modulation, SNR range)
- QuaDRiGa configuration and compatibility
- how the MATLAB implementation maps to paper equations and algorithm definitions

## How to use

1. Read `simulation_parameters.md` first to understand the paper's numerical setup.
2. Read `notes_about_versions.md` for the correct QuaDRiGa v2.2.0 usage patterns.
3. Read `matlab_scripts_analysis.md` for per-script analysis and bug fix documentation.
4. Use `VERIFICATION_REPORT.md` to confirm that the implementation matches the paper.

## Notes
- The implementation should be cross-checked against these markdown files before modifying the simulator code.
