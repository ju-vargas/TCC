#!/usr/bin/env python3
"""SER of LMMSE, ZF and BCD-MMSE under model A (covariance averaged over the band).

Model A follows footnote 4 of Zhao et al., IEEE JSAC 2025 (paper.md:821): the noise
covariance is estimated by averaging noise samples over frequency, and one R_hat serves
every PRB.  Model B is what the article simulates (L577): R_hat comes from the covariance
of the PRB being equalized.  Both run on the same band channels, so the gap between
them is the effect of the covariance model alone.

Usage
-----
    python run_modelo_a.py --provenance          parameter provenance table
    python run_modelo_a.py --quick --panels a    fast smoke run
    python run_modelo_a.py --panels a            panel (a), models A and B
    python run_modelo_a.py --model A             model A only, all panels

Needs the band exports dados/channels_quadriga_mc_*.npz (see quadriga/).  With
--channel standin_ula it runs on a substitute channel instead (NOT QuaDriGa).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from dbp_sim import hw_inverse
from dbp_sim.m1_driver import SimConfig, curve_names, run_panel_band
from dbp_sim.params import (FIGURE8_PANELS, M2_Channel, M5_Noise, assumptions,
                            provenance_table)
from dbp_sim.plotting import BCD_ITERATION_RAMP


def _table(snr_grid, results) -> None:
    head = f"  {'SNR':>5s} | " + " | ".join(f"{c:>18s}" for c in results)
    print(head)
    print("  " + "-" * (len(head) - 2))
    for i, snr in enumerate(snr_grid):
        print(f"  {snr:5.0f} | " + " | ".join(f"{results[c][i]:18.5f}" for c in results))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provenance", action="store_true",
                    help="print the parameter provenance table and exit")
    ap.add_argument("--panels", default="a,b,c,e,f,g",
                    help="comma-separated panel labels of Fig. 8 (default: all)")
    ap.add_argument("--model", default="AB", choices=["A", "B", "AB"],
                    help="covariance model: A (band average), B (per PRB), AB (both, "
                         "default)")
    ap.add_argument("--bcd-iterations", default="1,2,3,4",
                    help="BCD-MMSE iteration counts (default 1,2,3,4)")
    ap.add_argument("--n-eval-prbs", type=int, default=None,
                    help=f"PRBs evaluated per realization (default "
                         f"{M5_Noise.n_eval_prbs.value})")
    ap.add_argument("--channel", default=None, choices=["quadriga_file", "standin_ula"],
                    help="channel backend (default quadriga_file)")
    ap.add_argument("--bcd-inverse", default=None, choices=["float", "cholesky_hw"],
                    help="M_c x M_c inversion of the BCD-MMSE update")
    ap.add_argument("--hw-int-bits", type=int, default=None)
    ap.add_argument("--hw-frac-bits", type=int, default=None)
    ap.add_argument("--quick", action="store_true",
                    help="few realizations/symbols for a smoke test")
    ap.add_argument("--figdir", default=None,
                    help="output folder; default results/<UTC timestamp>_modelo_<model>")
    ap.add_argument("--no-plot", action="store_true", help="skip rendering")
    args = ap.parse_args()

    if args.provenance:
        print(provenance_table())
        print("\nEverything below required a decision the article does not make:\n")
        for mod, name, p in assumptions():
            print(f"  [{p.status}/{p.tier}] {mod}.{name} = {p.value}")
        return

    try:
        bcd_its = tuple(sorted({int(x) for x in args.bcd_iterations.split(",") if x.strip()}))
    except ValueError:
        raise SystemExit("--bcd-iterations takes integers, e.g. 1,2,3,4")
    if not bcd_its or bcd_its[0] < 1 or len(bcd_its) > len(BCD_ITERATION_RAMP):
        raise SystemExit(f"--bcd-iterations: 1 to {len(BCD_ITERATION_RAMP)} counts >= 1")

    overrides: dict = {"bcd_iteration_list": bcd_its}
    if args.n_eval_prbs is not None:
        overrides["n_eval_prbs"] = args.n_eval_prbs
    if args.channel is not None:
        overrides["channel_backend"] = args.channel
    if args.bcd_inverse is not None:
        overrides["bcd_inverse"] = args.bcd_inverse
    for flag in ("hw_int_bits", "hw_frac_bits"):
        if getattr(args, flag) is not None:
            if args.bcd_inverse != "cholesky_hw":
                raise SystemExit(f"--{flag.replace('_', '-')} needs --bcd-inverse cholesky_hw")
            overrides[flag] = getattr(args, flag)
    if args.quick:
        overrides.update(n_realizations=3, n_symbols=200, n_eval_prbs=4,
                         snr_db_grid=(-10, -6, -4, -2, 0))

    wanted = [p.strip() for p in args.panels.split(",") if p.strip()]
    panels = [p for p in FIGURE8_PANELS if p.label in wanted]
    missing = set(wanted) - {p.label for p in panels}
    if missing:
        raise SystemExit(f"unknown panel(s): {sorted(missing)}")

    models = list(args.model)
    chan = overrides.get("channel_backend", M2_Channel.backend.value)
    if args.figdir is None:
        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        args.figdir = str(Path(__file__).resolve().parent / "results"
                          / f"{stamp}_modelo_{args.model}_{chan}")
    outdir = Path(args.figdir)

    all_results: dict[str, dict[str, dict]] = {m: {} for m in models}
    diags: dict[str, dict] = {}
    for panel in panels:
        for model in models:
            cfg = SimConfig.from_panel(panel, covariance_model=model, **overrides)
            print(f"\n{'=' * 78}\nFig. 8({panel.label}) setup, model {model}:  M={cfg.M}  "
                  f"C={cfg.C}  K={cfg.K}  r={cfg.r}  IoT={cfg.iot_db:g} dB  "
                  f"{cfg.modulation}")
            print(f"  channel={cfg.channel_backend}  N={cfg.n_noise_samples}  "
                  f"{cfg.n_realizations} realizations x {cfg.n_eval_prbs} PRBs x "
                  f"{cfg.n_symbols} symbols")
            if cfg.channel_backend == "standin_ula":
                print("  NOTE: stand-in channel, NOT QuaDriGa.")
            print("=" * 78)
            t0 = time.time()
            hw_inverse.reset_stats()
            diag: dict = {}
            res = run_panel_band(cfg, progress=not args.quick, diagnostics=diag)
            print(f"  ({time.time() - t0:.1f} s)")
            if cfg.bcd_inverse == "cholesky_hw":
                st = hw_inverse.stats
                print(f"  hardware inverse: {st['calls']} calls, {st['overflow_calls']} "
                      f"with overflow, {st['failed_calls']} failed (pivot <= 0)")
            diags[panel.label] = diag
            print(f"  interference dimensions (eigenvalues above the noise floor): "
                  f"{diag['interference_dims_per_prb']:.1f} per PRB, "
                  f"{diag['interference_dims_band_average']:.1f} after band averaging\n")
            _table(np.asarray(cfg.snr_db_grid, dtype=float), res)
            all_results[model][panel.label] = {k: list(map(float, v)) for k, v in res.items()}

        if len(models) == 2:
            a, b = all_results["A"][panel.label], all_results["B"][panel.label]
            print(f"\n  SER ratio model A / model B, panel {panel.label}:")
            _table(np.asarray(cfg.snr_db_grid, dtype=float),
                   {c: [x / y if y > 0 else float("nan") for x, y in zip(a[c], b[c])]
                    for c in a})

    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "modelo_a_results.json"
    with open(out, "w") as fh:
        json.dump({"results": all_results, "diagnostics": diags,
                   "snr_db_grid": list(cfg.snr_db_grid)}, fh, indent=2)
    print(f"\nwrote {out}")

    if not args.no_plot:
        from dbp_sim.plotting import save_figure8
        cfg0 = SimConfig.from_panel(panels[0], **overrides)
        for model in models:
            sub = (f"Model {model} ("
                   + ("covariance averaged over the band, Zhao fn. 4" if model == "A"
                      else "per-PRB covariance, as in Zhao Sec. VI")
                   + f")  |  channel: {chan}"
                   + ("  (STAND-IN, not QuaDriGa)" if chan == "standin_ula" else "")
                   + f"  |  {cfg0.n_realizations} realizations x {cfg0.n_eval_prbs} PRBs"
                   + f" x {cfg0.n_symbols} symbols")
            png, csvp = save_figure8(all_results[model], panels, cfg0.snr_db_grid, outdir,
                                     subtitle=sub, curves=curve_names(cfg0),
                                     bcd_iterations=bcd_its, stem=f"modelo_{model}")
            print(f"wrote {png}\nwrote {csvp}")


if __name__ == "__main__":
    main()
