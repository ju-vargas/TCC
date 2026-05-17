# Simulator Notes

This folder contains the documentation and verification material used to reproduce the results of the target paper.

## Files
- `simulation_parameters.md` — Extracted simulation parameter definitions from the paper (Section VI-A).
- `notes_about_versions.md` — Version-specific QuaDRiGa implementation notes and compatibility guidance for QuaDRiGa v2.2.0 and MATLAB R2014a.
- `VERIFICATION_COMPLETE.md` — Summary verification status showing that the simulator parameters and implementation were checked against the paper.
- `VERIFICATION_REPORT.md` — Detailed cross-validation report.
- `paper.md` — Full article transcript used as the source of truth.

## Purpose

These notes are the authoritative reference for:
- simulation parameters (M, C, K, r, N, N_sym, N_mc, IoT, modulation, SNR range)
- QueDRiGa configuration and compatibility
- how the MATLAB implementation maps to paper equations and algorithm definitions

## How to use

1. Read `simulation_parameters.md` first to understand the paper's numerical setup.
2. Read `notes_about_versions.md` for the correct QuaDRiGa v2.2.0 usage patterns.
3. Use `VERIFICATION_REPORT.md` to confirm that the implementation matches the paper.

## Notes
- The implementation should be cross-checked against these markdown files before modifying the simulator code.
