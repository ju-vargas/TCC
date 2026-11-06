"""Figure rendering for the Figure 8 reproduction.

Design notes
------------
Form: multi-series line chart on a log SER axis, small-multipled across the panels -
the article's own form, and the standard for error-rate curves.

Colour: categorical (six series = six identities, no magnitude or polarity). The six
hues below are a validated subset of the reference palette, chosen by enumerating all
C(8,6) subsets and keeping those that clear the **all-pairs** gates that small multiples
require::

    node scripts/validate_palette.js \\
      "#2a78d6,#1baf7a,#eda100,#008300,#4a3aa7,#e34948" --mode light --pairs all
    -> ALL CHECKS PASS  (normal-vision worst 15.6; CVD worst 6.9 -> 6-8 band)

Two consequences, both honoured here:

* CVD separation lands in the 6-8 band, which is legal **only with secondary encoding** -
  so every series carries a distinct marker shape as well as a hue.
* Three hues sit below 3:1 against the light surface, which triggers the relief rule -
  so `save_figure8` also writes a CSV table view beside the image.

The figure commits to a **light surface only**: it is a static raster destined for a
printed/embedded thesis figure, not a themed web page.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                        # noqa: E402

# --- validated palette (light surface) --------------------------------------------
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#8a8983"
GRID = "#e4e3df"

#: series -> (hue, marker), matching the ARTICLE's own Figure 8 colour assignment:
#: LMMSE red, ZF magenta, BCD-MMSE green, BCD-MMSE(LRD) orange, sDR dark blue,
#: cDR light blue.  Colour follows the entity, never its rank, so this mapping is fixed
#: regardless of which curves a panel shows.
#:
#: The exact hues are the nearest validated steps to the paper's, not the paper's raw
#: values.  The paper's literal palette FAILS the accessibility gates - notably its
#: green-vs-orange pair sits at deutan dE 4.3, and those are BCD-iter1 vs LRD-iter4, the
#: two curves a reader most needs to compare.  Re-stepping within the same six hue
#: identities clears every gate:
#:
#:   node scripts/validate_palette.js \
#:     "#d62828,#d64ad6,#0a7a30,#eda100,#3b4bbf,#35bcd9" --mode light --pairs all
#:   -> ALL CHECKS PASS (CVD worst 8.3 protan; normal-vision worst 23.5)
#:
#: CVD 8.3 meets the >=8 target, but red-vs-green is intrinsically the hardest pair for
#: deutan/protan vision, so every series also carries a distinct MARKER - identity is
#: never colour-alone.  Two hues sit below 3:1 on the light surface, which triggers the
#: relief rule, so `save_figure8` also writes the CSV table view.
SERIES_STYLE: dict[str, tuple[str, str]] = {
    "LMMSE":                 ("#d62828", "o"),   # red        - reference optimum
    "ZF":                    ("#d64ad6", "s"),   # magenta
    "BCD-MMSE (iter 1)":     ("#0a7a30", "v"),   # green
    "BCD-MMSE LRD (iter 4)": ("#eda100", "^"),   # orange
    "sDR-MMSE":              ("#3b4bbf", "D"),   # dark blue
    "cDR-MMSE":              ("#35bcd9", "<"),   # light blue
}


#: BCD-MMSE iteration study (--bcd-iterations): each iteration count is its own identity,
#: with a hue clearly apart from LMMSE, from ZF and from the other counts.  ZF moves from
#: magenta to pink here, because every blue step fell to protan dE 2.2 against magenta.
#: Chosen by exhaustive search over the reference palette steps, LMMSE red fixed:
#:   node scripts/validate_palette.js \
#:     "#d62828,#e87ba4,#eda100,#35bcd9,#2a78d6,#4a3aa7" --mode light --pairs all
#:   -> ALL CHECKS PASS (CVD worst 8.3 deutan; normal-vision worst 16.3)
#: Three hues sit below 3:1 on the surface, so every curve keeps a distinct marker and
#: `save_figure8` writes the CSV table view.  Iteration k always takes colour k (1-4).
ITERATION_ZF_COLOR = "#e87ba4"
BCD_ITERATION_RAMP: tuple[str, ...] = ("#eda100", "#35bcd9", "#2a78d6", "#4a3aa7")
BCD_ITERATION_MARKERS: tuple[str, ...] = ("v", "^", "D", "<")


def series_styles(curves, bcd_iterations=()) -> dict[str, tuple[str, str]]:
    """(colour, marker) for each curve.  In the iteration study each BCD iteration count
    keeps its own colour (iteration k -> colour k), so a figure with fewer counts never
    repaints the others; LMMSE stays red and ZF turns pink."""
    if not bcd_iterations:
        return {c: SERIES_STYLE[c] for c in curves}
    order = sorted(bcd_iterations)
    if len(order) > len(BCD_ITERATION_RAMP):
        raise ValueError(f"at most {len(BCD_ITERATION_RAMP)} BCD iteration curves per figure")
    slots = ([it - 1 for it in order] if order[-1] <= len(BCD_ITERATION_RAMP)
             else list(range(len(order))))
    out = {"LMMSE": SERIES_STYLE["LMMSE"], "ZF": (ITERATION_ZF_COLOR, SERIES_STYLE["ZF"][1])}
    for it, k in zip(order, slots):
        out[f"BCD-MMSE (iter {it})"] = (BCD_ITERATION_RAMP[k], BCD_ITERATION_MARKERS[k])
    return {c: out[c] for c in curves}


SER_FLOOR = 1e-4          # the article's y-axis floor

MODULATION_LABEL = {"16QAM": "16-QAM", "QPSK": "QPSK"}


def configuration_title(panel) -> str:
    """Panel title with the TCC numbering (Table tab:paineis): M, C, K, the IoT and
    the modulation. The IoT is shown because configuration 2 differs from 1 only in it."""
    from dbp_sim.params import TCC_CONFIGURATION
    mod = MODULATION_LABEL.get(panel.modulation, panel.modulation)
    return (f"Configuração {TCC_CONFIGURATION[panel.label]}\n$M$ = {panel.M}, "
            f"$C$ = {panel.C}, $K$ = {panel.K}, IoT = {panel.iot_db:g} dB, {mod}")


def _style_axes(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_yscale("log")
    ax.set_ylim(SER_FLOOR, 1.0)
    ax.grid(True, which="major", color=GRID, linewidth=0.7, zorder=0)
    ax.grid(True, which="minor", color=GRID, linewidth=0.4, alpha=0.6, zorder=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_MUTED)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9, length=3, width=0.8)


def save_figure8(results: dict[str, dict[str, list[float]]],
                 panels,
                 snr_grid,
                 outdir: str | Path,
                 subtitle: str = "",
                 curves=None,
                 bcd_iterations=(),
                 stem: str = "figure8") -> tuple[Path, Path]:
    """Render every panel into one figure; also write the table view.

    results         {panel_label: {curve: [ser per snr]}}
    panels          iterable of Panel records, in display order
    curves          curves to draw, in legend order (default: the six of Figure 8)
    bcd_iterations  iteration counts of the BCD study, if any (selects its ramp)
    stem            output file name without extension
    """
    styles = series_styles(curves if curves is not None else SERIES_STYLE.keys(),
                           bcd_iterations)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    snr = np.asarray(snr_grid, dtype=float)

    shown = [p for p in panels if p.label in results]
    ncols = min(3, len(shown)) or 1
    nrows = int(np.ceil(len(shown) / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(4.1 * ncols, 3.5 * nrows),
                             squeeze=False)
    fig.patch.set_facecolor(SURFACE)

    for i, panel in enumerate(shown):
        ax = axes[i // ncols][i % ncols]
        _style_axes(ax)
        for curve, (color, marker) in styles.items():
            if curve not in results[panel.label]:
                continue
            y = np.asarray(results[panel.label][curve], dtype=float)
            y = np.where(y <= 0, np.nan, y)          # log axis: drop zero-error points
            ax.plot(snr, y, color=color, marker=marker, markersize=5,
                    linewidth=1.8, markeredgecolor=SURFACE, markeredgewidth=0.6,
                    label=curve, zorder=3, clip_on=True)

        ax.set_title(configuration_title(panel), fontsize=9, color=INK_PRIMARY, pad=8)

        if i % ncols == 0:
            ax.set_ylabel("SER", fontsize=10, color=INK_SECONDARY)
        if i // ncols == nrows - 1:
            ax.set_xlabel("SNR [dB]", fontsize=10, color=INK_SECONDARY)

    for j in range(len(shown), nrows * ncols):
        axes[j // ncols][j % ncols].set_visible(False)

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(6, len(labels)),
               frameon=False, fontsize=9.5, labelcolor=INK_SECONDARY,
               bbox_to_anchor=(0.5, -0.005), handlelength=2.2, columnspacing=1.6)

    if subtitle:
        fig.text(0.5, 0.985, subtitle, ha="center", va="top",
                 fontsize=9.5, color=INK_SECONDARY)

    fig.tight_layout(rect=(0, 0.055, 1, 0.965 if subtitle else 1.0))
    png = outdir / f"{stem}.png"
    fig.savefig(png, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    pdf = outdir / f"{stem}.pdf"
    fig.savefig(pdf, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

    csv_path = _write_table(results, shown, snr, outdir, list(styles), stem)
    return png, csv_path


def _write_table(results, panels, snr, outdir: Path, curves, stem: str) -> Path:
    """Table view - required by the relief rule for the low-contrast hues."""
    path = outdir / f"{stem}_data.csv"
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "configuracao", "snr_db", *curves])
        from dbp_sim.params import TCC_CONFIGURATION
        for panel in panels:
            for i, s in enumerate(snr):
                w.writerow([panel.label, TCC_CONFIGURATION[panel.label], f"{s:g}"] +
                           [f"{results[panel.label][c][i]:.6g}"
                            if c in results[panel.label] else ""
                            for c in curves])
    return path
