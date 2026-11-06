#!/usr/bin/env python3
"""Reproduce Figure 8 of Zhao et al., IEEE JSAC 2025 (DOI 10.1109/JSAC.2025.3531524).

Usage
-----
    python run_figure8.py --provenance          print the parameter provenance table
    python run_figure8.py --panels a            run one panel
    python run_figure8.py --quick               fast smoke run (few realizations)
    python run_figure8.py                       all panels at the article's settings
    python run_figure8.py --bcd-iterations 1,2,3,4
                                                BCD-MMSE iteration study: LMMSE, ZF and
                                                one BCD-MMSE curve per iteration count
    python run_figure8.py --n-noise-samples 12,48,192
                                                one run per number of noise samples N
    python run_figure8.py --conditions all      the 3GPP test conditions (TDLA30-5 ... HST500),
                                                one run per distinct (N, carrier)
    python run_figure8.py --conditions all --n-case worst,mean
                                                the same, with N of the worst case and of the
                                                mean over the data symbols

Every number this produces depends on decisions the article does not state.  Run
``--provenance`` and read ``simulation_parameters.md`` before quoting any result.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from dbp_sim import hls_inverse, hw_inverse
from dbp_sim.m1_driver import SimConfig, curve_names, run_panel
from dbp_sim.plotting import BCD_ITERATION_RAMP
from dbp_sim.params import (ALL_PANELS, EXTRA_PANELS, FIG8A_TARGETS_AT_MINUS4DB, M1_Driver,
                            TCC_CONFIGURATION,
                            M2_Channel, M6_Covariance, M7_Equalizers, assumptions,
                            provenance_table)

TEST_CONDITIONS = M1_Driver.test_conditions.value


def _banner(cfg: SimConfig, panel_label: str) -> None:
    print(f"\n{'=' * 78}\nConfiguracao {TCC_CONFIGURATION[panel_label]} (panel {panel_label}):  "
          f"M={cfg.M}  C={cfg.C}  K={cfg.K}  "
          f"r={cfg.r}  IoT={cfg.iot_db:g} dB  {cfg.modulation}")
    print(f"  channel={cfg.channel_backend}  mapping={cfg.mapping}  "
          f"cond={cfg.shrinkage}  norm={cfg.normalization}  N={cfg.n_noise_samples}  "
          f"fc={cfg.carrier_hz / 1e9:g} GHz  "
          f"realizations={cfg.n_realizations}x{cfg.n_symbols} symbols")
    if cfg.channel_backend == "standin_ula":
        print("  NOTE: stand-in channel, NOT QuaDriGa - absolute SNR placement is not "
              "the article's.")
    print("=" * 78)


def _table(snr_grid, results) -> None:
    head = f"  {'SNR':>5s} | " + " | ".join(f"{c:>21s}" for c in results)
    print(head)
    print("  " + "-" * (len(head) - 2))
    for i, snr in enumerate(snr_grid):
        row = " | ".join(f"{results[c][i]:21.5f}" for c in results)
        print(f"  {snr:5.0f} | {row}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provenance", action="store_true",
                    help="print the parameter provenance table and exit")
    ap.add_argument("--panels", default="a,b,c,e,f,g",
                    help="configurations to run, by panel label: a,b,c,e,f,g (Fig. 8 of the "
                         "article, which has no panel (d)) and/or 7-16 (params.EXTRA_PANELS; "
                         "labels, not TCC numbers - see params.TCC_CONFIGURATION); "
                         "'extra' = labels 7-16, 'all' = every configuration "
                         "(default: a,b,c,e,f,g)")
    ap.add_argument("--quick", action="store_true",
                    help="few realizations/symbols for a smoke test")
    ap.add_argument("--shrinkage", default=None,
                    choices=["ledoit_wolf", "fixed", "none"],
                    help="covariance conditioning rule (default: ledoit_wolf)")
    ap.add_argument("--epsilon", type=float, default=None,
                    help="loading level for --shrinkage fixed (not adopted)")
    ap.add_argument("--mapping", default=None, choices=["contiguous", "interleaved"],
                    help="override the Tier-2B antenna->cluster mapping")
    ap.add_argument("--normalization", default=None,
                    choices=["unit_mean_entry_power", "per_ue_power_control"],
                    help="channel normalization (2A.2); per_ue_power_control "
                         "equalises UE receive powers, i.e. ideal uplink power control")
    ap.add_argument("--channel", default=None,
                    choices=["standin_ula", "quadriga_file"],
                    help="override the channel backend")
    ap.add_argument("--bcd-iterations", default=None,
                    help="comma-separated BCD-MMSE iteration counts, e.g. 1,2,3,4 (at "
                         f"most {len(BCD_ITERATION_RAMP)}); computes only LMMSE, ZF and "
                         "one BCD-MMSE curve per count")
    ap.add_argument("--n-noise-samples", default=None,
                    help="comma-separated numbers of noise samples N, e.g. 12,48,192; one "
                         "run (and one output folder) per value (default: 192)")
    ap.add_argument("--conditions", default=None,
                    help="comma-separated 3GPP test conditions, or 'all'; conditions with "
                         "the same N and carrier (params.M1_Driver.test_conditions) share "
                         "one run (" + ", ".join(c for c, *_ in TEST_CONDITIONS) + ")")
    ap.add_argument("--n-case", default="worst",
                    help="with --conditions: worst, mean or worst,mean - N of the worst "
                         "data symbol or the mean over the data symbols "
                         "(params.M1_Driver.test_conditions; default: worst)")
    ap.add_argument("--bcd-inverse", default=None, choices=["float", "cholesky_hw", "hls"],
                    help="M_c x M_c inversion of the BCD-MMSE update: float (default), "
                         "cholesky_hw (the bit-exact model in hardware/golden_cholesky.py) or "
                         "hls (the HLS hardware itself, a C-simulation server from "
                         "hardware/cholesky_hardware_servidor; takes --hw-int-bits, "
                         "--hw-frac-bits, --hw-quant, --hw-overflow)")
    ap.add_argument("--hw-int-bits", type=int, default=None,
                    help="cholesky_hw: integer bits of the data type, sign included "
                         "(default 8)")
    ap.add_argument("--hw-frac-bits", type=int, default=None,
                    help="cholesky_hw: fractional bits of the data type (default 8)")
    ap.add_argument("--hw-acc-int-bits", type=int, default=None,
                    help="cholesky_hw: accumulator integer bits (default: twice "
                         "--hw-int-bits)")
    ap.add_argument("--hw-acc-frac-bits", type=int, default=None,
                    help="cholesky_hw: accumulator fractional bits (default: twice "
                         "--hw-frac-bits)")
    QUANT = ["AP_TRN", "AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF", "AP_RND_CONV"]
    OVERFLOW = ["AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM"]
    ap.add_argument("--hw-quant", default=None, choices=QUANT,
                    help="cholesky_hw: quantization of the fractional part (default AP_TRN)")
    ap.add_argument("--hw-overflow", default=None, choices=OVERFLOW,
                    help="cholesky_hw: overflow of the integer part (default AP_SAT)")
    ap.add_argument("--hw-acc-quant", default=None, choices=QUANT,
                    help="cholesky_hw: accumulator quantization (default: --hw-quant)")
    ap.add_argument("--hw-acc-overflow", default=None, choices=OVERFLOW,
                    help="cholesky_hw: accumulator overflow (default: --hw-overflow)")
    inter = ap.add_argument_group(
        "cholesky_hw intermediates (cholesky.h CHOL_<NAME>_*); default: the cholesky.h "
        "default, which reproduces the hardware without intermediate types")
    for name in hw_inverse.INTERMEDIATES:
        inter.add_argument(f"--hw-{name}-int-bits", type=int, default=None)
        inter.add_argument(f"--hw-{name}-frac-bits", type=int, default=None)
        if name in hw_inverse.BITS_ONLY:
            continue
        inter.add_argument(f"--hw-{name}-quant", default=None, choices=QUANT)
        inter.add_argument(f"--hw-{name}-overflow", default=None, choices=OVERFLOW)
    ap.add_argument("--out", default=None, help="write results to this JSON file")
    ap.add_argument("--figdir", default=None,
                    help="output folder; default is a new timestamped folder "
                         "results/<UTC timestamp>_<channel> so runs are never overwritten")
    ap.add_argument("--no-plot", action="store_true", help="skip rendering")
    args = ap.parse_args()

    if args.provenance:
        print(provenance_table())
        print("\nEverything below required a decision the article does not make:\n")
        for mod, name, p in assumptions():
            print(f"  [{p.status}/{p.tier}] {mod}.{name} = {p.value}")
        return

    overrides: dict = {}
    if args.shrinkage is not None:
        overrides["shrinkage"] = args.shrinkage
    if args.epsilon is not None:
        overrides["fixed_epsilon"] = args.epsilon
        overrides.setdefault("shrinkage", "fixed")
    if args.mapping is not None:
        overrides["mapping"] = args.mapping
    if args.channel is not None:
        overrides["channel_backend"] = args.channel
    if args.normalization is not None:
        overrides["normalization"] = args.normalization
    if args.bcd_inverse is not None:
        overrides["bcd_inverse"] = args.bcd_inverse
    for flag in ("hw_int_bits", "hw_frac_bits", "hw_acc_int_bits", "hw_acc_frac_bits",
                 "hw_quant", "hw_overflow", "hw_acc_quant", "hw_acc_overflow"):
        if getattr(args, flag) is not None:
            if args.bcd_inverse not in ("cholesky_hw", "hls"):
                raise SystemExit(f"--{flag.replace('_', '-')} needs --bcd-inverse cholesky_hw or hls")
            overrides[flag] = getattr(args, flag)
    hw_inter = []
    for name in hw_inverse.INTERMEDIATES:
        vals = tuple(getattr(args, f"hw_{name}_{f}", None)
                     for f in ("int_bits", "frac_bits", "quant", "overflow"))
        if any(v is not None for v in vals):
            if args.bcd_inverse != "cholesky_hw":
                raise SystemExit(f"--hw-{name}-* needs --bcd-inverse cholesky_hw")
            hw_inter.append((name, vals))
    if hw_inter:
        overrides["hw_intermediates"] = tuple(hw_inter)
    bcd_its: tuple = ()
    if args.bcd_iterations:
        try:
            bcd_its = tuple(sorted({int(x) for x in args.bcd_iterations.split(",") if x.strip()}))
        except ValueError:
            raise SystemExit("--bcd-iterations takes integers, e.g. 1,2,3,4")
        if not bcd_its or bcd_its[0] < 1:
            raise SystemExit("--bcd-iterations: every count must be >= 1")
        if len(bcd_its) > len(BCD_ITERATION_RAMP):
            raise SystemExit(f"--bcd-iterations: at most {len(BCD_ITERATION_RAMP)} counts "
                             "per figure")
        overrides["bcd_iteration_list"] = bcd_its
    stem = "bcd_iterations" if bcd_its else "figure8"
    if args.quick:
        overrides.update(n_realizations=3, n_symbols=200,
                         snr_db_grid=(-10, -6, -4, -2, 0))

    # Each run is (condition label or None, overrides); empty overrides keep the defaults.
    runs: list[tuple[str | None, dict]] = [(None, {})]
    if args.n_noise_samples and args.conditions:
        raise SystemExit("use --n-noise-samples or --conditions, not both")
    if args.n_noise_samples:
        try:
            ns = sorted({int(x) for x in args.n_noise_samples.split(",") if x.strip()})
        except ValueError:
            raise SystemExit("--n-noise-samples takes integers, e.g. 12,48,192")
        if not ns or ns[0] < 1:
            raise SystemExit("--n-noise-samples: every N must be >= 1")
        runs = [(None, {"n_noise_samples": n}) for n in ns]
    if args.conditions:
        table = {c: {"worst": nw, "mean": nm, "fc": fc} for c, nw, nm, fc in TEST_CONDITIONS}
        names = (list(table) if args.conditions.strip() == "all"
                 else [c.strip() for c in args.conditions.split(",") if c.strip()])
        unknown = [c for c in names if c not in table]
        if unknown:
            raise SystemExit(f"unknown condition(s) {unknown}; known: {', '.join(table)}")
        cases = [x.strip() for x in args.n_case.split(",") if x.strip()]
        if not cases or any(x not in ("worst", "mean") for x in cases):
            raise SystemExit("--n-case takes worst, mean or worst,mean")
        # Conditions with the same (N, carrier) give the same curves: run each key once.
        # A mean-case label carries the suffix "-media" when it is not also the worst case.
        groups: dict[tuple, list[str]] = {}
        for case in cases:
            for c in names:
                n = table[c][case]
                if n == 0:
                    print(f"  {c}: N = 0 in the {case} case - per-T_c estimation is "
                          "infeasible, skipped")
                    continue
                label = c if case == "worst" or table[c]["worst"] == n else f"{c}-media"
                labels = groups.setdefault((n, table[c]["fc"]), [])
                if label not in labels:
                    labels.append(label)
        runs = [("+".join(cs), {"n_noise_samples": n, "carrier_hz": fc})
                for (n, fc), cs in groups.items()]
        print("runs (conditions with the same N and carrier share one):")
        for label, ov in runs:
            print(f"  N = {ov['n_noise_samples']:3d}  fc = {ov['carrier_hz'] / 1e9:g} GHz  "
                  f"{label}")

    if args.panels.strip() == "all":
        wanted = [p.label for p in ALL_PANELS]
    elif args.panels.strip() == "extra":
        wanted = [p.label for p in EXTRA_PANELS]
    else:
        wanted = [p.strip() for p in args.panels.split(",") if p.strip()]
    panels = [p for p in ALL_PANELS if p.label in wanted]
    missing = set(wanted) - {p.label for p in panels}
    if missing:
        extra = " (panel (d) is unrecoverable from the article and is not implemented)" \
                if "d" in missing else ""
        raise SystemExit(f"unknown panel(s): {sorted(missing)}{extra}")

    for cond, run_ov in runs:
        run_overrides = {**overrides, **run_ov}
        suffix = ""
        if "n_noise_samples" in run_ov:
            n = run_ov["n_noise_samples"]
            suffix = f"_{cond}_N{n}" if cond else f"_N{n}"
            if "carrier_hz" in run_ov:
                suffix += f"_{run_ov['carrier_hz'] / 1e9:g}GHz"
        if len(runs) > 1:
            print(f"\n{'#' * 78}\n# {suffix.lstrip('_')}\n{'#' * 78}")
        figdir = args.figdir
        # With --conditions every run gets its own <conditions>_N<N>_<GHz>GHz folder, even a
        # single one, so the per-configuration scripts always find the same layout
        per_run = len(runs) > 1 or bool(args.conditions)
        if figdir is not None and per_run:
            figdir = str(Path(figdir) / suffix.lstrip("_"))
        out = args.out
        if out and per_run:
            out = str(Path(out).with_name(f"{Path(out).stem}{suffix}{Path(out).suffix}"))
        _run(args, panels, run_overrides, bcd_its, stem, figdir, out, suffix, cond)


def figure_subtitle(cfg: SimConfig, cond: str | None) -> str:
    """Line above the figure: test condition, N and carrier. What is the same in every
    figure (channel, conditioning, 100 x 480 averaging) is shown only when it differs
    from the default, so a non-standard run is never mistaken for a standard one."""
    parts = []
    if cond:
        parts.append("Condição de teste: "
                     + cond.replace("+", ", ").replace("-media", " (média)"))
    parts.append(f"$N$ = {cfg.n_noise_samples}")
    parts.append(f"$f_c$ = {cfg.carrier_hz / 1e9:g} GHz".replace(".", ","))
    if cfg.channel_backend != M2_Channel.backend.value:
        parts.append(f"canal: {cfg.channel_backend}")
    if cfg.shrinkage != M6_Covariance.shrinkage.value:
        parts.append(f"condicionamento: {cfg.shrinkage}")
    if cfg.bcd_inverse != M7_Equalizers.bcd_inverse.value:
        parts.append(f"inversa: {cfg.bcd_inverse} ap_fixed<{cfg.hw_int_bits + cfg.hw_frac_bits},"
                     f"{cfg.hw_int_bits},{cfg.hw_quant},{cfg.hw_overflow}>")
    if (cfg.n_realizations, cfg.n_symbols) != (M1_Driver.n_realizations.value,
                                               M1_Driver.n_symbols.value):
        parts.append(f"{cfg.n_realizations} realizações x {cfg.n_symbols} símbolos")
    return "   |   ".join(parts)


def _run(args, panels, overrides: dict, bcd_its: tuple, stem: str,
         figdir: str | None, out: str | None, suffix: str, cond: str | None) -> None:
    """Run every panel with one set of overrides and write its JSON and figure."""
    if figdir is None:
        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        chan = args.channel or M2_Channel.backend.value
        norm = args.normalization or M2_Channel.normalization.value
        tag = "pc" if norm == "per_ue_power_control" else "nopc"
        if bcd_its:
            tag += "_bcdit" + "-".join(map(str, bcd_its))
        if args.bcd_inverse in ("cholesky_hw", "hls"):
            tag += (f"_hwinv{overrides.get('hw_int_bits', M7_Equalizers.hw_int_bits.value)}"
                    f"-{overrides.get('hw_frac_bits', M7_Equalizers.hw_frac_bits.value)}"
                    f"_{overrides.get('hw_quant', M7_Equalizers.hw_quant.value)}"
                    f"_{overrides.get('hw_overflow', M7_Equalizers.hw_overflow.value)}")
            for name, (ib, fb, _q, _o) in overrides.get("hw_intermediates", ()):
                tag += f"_{name}{'' if ib is None else ib}-{'' if fb is None else fb}"
        tag += suffix
        figdir = str(Path(__file__).resolve().parent / "results" / f"{stamp}_{chan}_{tag}")

    shr = overrides.get("shrinkage", M6_Covariance.shrinkage.value)
    print(f"conditioning = {shr}  [Tier 2A - the article does not specify how R_hat is "
          f"conditioned; see params.M6_Covariance.shrinkage]")
    print(f"channel = {overrides.get('channel_backend', M2_Channel.backend.value)}")

    all_results: dict[str, dict] = {}
    for panel in panels:
        cfg = SimConfig.from_panel(panel, **overrides)
        _banner(cfg, panel.label)
        if panel.note:
            print(f"  caveat: {panel.note}\n")
        t0 = time.time()
        hw_inverse.reset_stats()
        hls_inverse.reset_stats()
        results = run_panel(cfg, progress=not args.quick)
        print(f"  ({time.time() - t0:.1f} s)\n")
        if cfg.bcd_inverse == "cholesky_hw":
            st = hw_inverse.stats
            print(f"  hardware inverse ap_fixed<{cfg.hw_int_bits + cfg.hw_frac_bits},"
                  f"{cfg.hw_int_bits},{cfg.hw_quant},{cfg.hw_overflow}>: {st['calls']} "
                  f"calls, {st['overflow_calls']} with overflow, {st['failed_calls']} "
                  f"failed (pivot <= 0)\n")
        if cfg.bcd_inverse == "hls":
            st = hls_inverse.stats
            print(f"  HLS hardware ap_fixed<{cfg.hw_int_bits + cfg.hw_frac_bits},"
                  f"{cfg.hw_int_bits},{cfg.hw_quant},{cfg.hw_overflow}>: {st['calls']} "
                  f"inversions, {st['hls_calls']} sent to the hardware, {st['failed_calls']} "
                  f"failed (division by zero or timeout)\n")
        _table(np.asarray(cfg.snr_db_grid, dtype=float), results)
        all_results[panel.label] = {k: list(map(float, v)) for k, v in results.items()}

        if panel.label == "a" and -4 in list(cfg.snr_db_grid):
            i = list(cfg.snr_db_grid).index(-4)
            print("\n  vs Fig. 8(a) read-off targets at SNR = -4 dB "
                  "(status F, +-30% - order-of-magnitude check only):")
            for curve, target in FIG8A_TARGETS_AT_MINUS4DB.items():
                if curve not in results:
                    continue
                got = results[curve][i]
                ratio = got / target if target else float("nan")
                print(f"    {curve:24s} got {got:8.4f}   target {target:6.3f}   "
                      f"ratio {ratio:5.2f}x")

    if out is None:
        out = str(Path(figdir) / f"{stem}_results.json")
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as fh:
            json.dump(all_results, fh, indent=2)
        print(f"\nwrote {out}")

    if not args.no_plot and all_results:
        from dbp_sim.plotting import save_figure8
        cfg0 = SimConfig.from_panel(panels[0], **overrides)
        sub = figure_subtitle(cfg0, cond)
        png, csvp = save_figure8(all_results, panels, cfg0.snr_db_grid,
                                 figdir, subtitle=sub, curves=curve_names(cfg0),
                                 bcd_iterations=bcd_its, stem=stem)
        print(f"\nwrote {png}\nwrote {csvp}")


if __name__ == "__main__":
    main()
