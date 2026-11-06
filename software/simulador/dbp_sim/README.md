# `dbp_sim` — Figure 8 simulator

Python port of the uplink simulator behind **Figure 8** of Zhao, Li, Wang, Song, Chang,
Shi, *"Efficient LMMSE Equalization for Massive MIMO Systems Under Decentralized Baseband
Processing Architecture"*, IEEE JSAC, DOI `10.1109/JSAC.2025.3531524`.

Full provenance analysis: `../simulation_parameters.md`.

## Layout

| File | Module | Responsibility |
| :-- | :-- | :-- |
| `params.py` | — | **Every constant, with its provenance and tier.** Single source of truth |
| `provenance.py` | — | The `Param` record and status/tier vocabulary |
| `m1_driver.py` | M1 | Monte-Carlo loop, `SimConfig`, panel runner |
| `m2_channel.py` | M2 | `H`, `Hbar`; QuaDriGa-export and stand-in backends; normalization |
| `m3_clustering.py` | M3 | Antenna → cluster partition (contiguous / interleaved) |
| `m4_source.py` | M4 | Constellations and symbol draws |
| `m5_noise.py` | M5, M6 | Colored noise, `β` from IoT, `R̂`, conditioning (Ledoit–Wolf) |
| `m7_equalizers.py` | M7 | LMMSE, ZF, BDAC, sDR, cDR, BCD, LRD |
| `m8_metric.py` | M8 | Slicing and SER |

Entry point `../run_figure8.py`; correctness checks `../test_dbp_sim.py`.

## Running

```sh
python run_figure8.py --provenance      # parameter table + every non-stated decision
python run_figure8.py --quick --panels a
python run_figure8.py                   # all panels, article settings (slow)
python run_figure8.py --bcd-iterations 1,2,3,4   # LMMSE, ZF and BCD-MMSE per iteration count
python run_figure8.py --n-noise-samples 12,48,144,192   # one run per number of noise samples N
python run_figure8.py --conditions all  # 3GPP test conditions, one run per (N, carrier)
python test_dbp_sim.py                  # correctness checks
```

Useful overrides for sensitivity work — each maps to a documented open item:

```sh
--channel standin_ula                      # substitute channel, NOT QuaDriGa (tests only)
--normalization unit_mean_entry_power      # 2A.2: no uplink power control
--shrinkage none                           # no conditioning (pinv where singular)
--shrinkage fixed --epsilon 0.1            # fixed diagonal loading (not adopted), for sweeps
--mapping interleaved                      # 2B.1: 1.07-1.43x on real channels
```

## Reading the results honestly

Every run writes to its own timestamped folder under `results/`, so nothing is ever
overwritten. Three things bound what a run can claim.

**Channels come from QuaDriGa** — generate them once, then run against them:

```sh
matlab -nodisplay -nosplash -r "run('quadriga/export_quadriga_channels.m')"   # ~15 min
.venv/bin/python quadriga/convert_quadriga_export.py                          # dados/*.mat -> dados/*.npz
.venv/bin/python run_figure8.py                                      # default channel = quadriga_file
```

`quadriga/export_quadriga_channels.m` records every open choice at the top (scenario, carrier
frequency, array, heights) and carries them into the `.npz` so a figure can always be
traced back to the channel that produced it. `StandInULAChannel` is used by the tests,
which run without MATLAB; it reproduces only the article's *angular* geometry, not its
large-scale fading — figures made with it must say so.

**The conditioning rule is ours, not the article's.** Eq. (3) needs `R⁻¹`, footnote 5 says use
`R̂`, and `rank(R̂) ≤ N = 192 < 256 = M` — so *something* must condition it, but the article never
says what. The default is **Ledoit–Wolf shrinkage**, whose intensity is computed from the samples,
so it adds no free parameter: write "this work uses Ledoit–Wolf shrinkage", never "the paper
uses …". `params.M6_Covariance.shrinkage` carries the argument, including why fixed diagonal
loading is not adopted (its scale tracks the *largest* eigenvalues, so at IoT = 20 dB it swamps the
noise floor by 10× and centralized LMMSE loses its optimality).

**Panel (d) does not exist here.** It is absent from the extracted figure and never cited
in the article. Its configuration is unrecoverable and is deliberately not guessed.

## What the implementation guarantees

`test_dbp_sim.py` checks properties the article *proves*, rather than numbers it reports:

- **Theorem 2 (L463)** — the BCD objective (24) decreases monotonically.
- **The optimality gate** — centralized LMMSE must give the lowest SER in *every* panel, at
  IoT = 10 **and** 20 dB. This is the property a bad conditioning rule silently breaks.
- **Proposition 1 (L363)** — `MSE(sDR) ≥ MSE(cDR)`.
- Centralized LMMSE minimises (24) among all seven equalizers.
- `S Sᴴ == R̂` exactly (Eq. 32); constellations carry unit average energy; per-UE
  normalization gives `E[|h_mk|²] = 1` for every UE; the realised per-antenna IoT equals the nominal.
- **Decentralization is real**: no routine inverts anything larger than the article
  permits (`M_c × M_c`, or `CK × CK` for cDR).

## Status against the article

Colours match the article's own Figure 8 (LMMSE red, ZF magenta, BCD green, LRD orange,
sDR dark blue, cDR light blue) so the two can be compared side by side — see
`plotting.py` for why the hues are the nearest *validated* steps to the paper's rather
than its literal values.

The dominant open choice is **`--normalization`**. With real QuaDriGa channels the
article's own geometry (UEs over a 50–100 m annulus) yields a measured **13 dB median
per-UE power spread**, and whether uplink power control is applied changes panel (a)
ratios-vs-target from a scattered 0.8–7.5× to a clustered 0.56–0.65×. See
`params.M2_Channel.normalization` for the measured A/B.
