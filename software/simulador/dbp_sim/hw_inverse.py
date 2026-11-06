"""Hardware model of the M_c x M_c inversion in the BCD-MMSE update.

Loads the bit-exact Python model of the fixed-point Cholesky inverter
(``hardware/golden_cholesky.py``, validated against the Vitis HLS C-simulation) and
exposes it as an `inverse(A)` callable for `m7_equalizers.bcd_mmse_path`.

The fixed-point format is a parameter (`make_inverter`): integer and fractional bits,
quantization mode (AP_TRN, AP_RND_CONV, ...) and overflow mode (AP_SAT, AP_WRAP, ...),
for data, accumulators and the intermediates (product, complex product, divisor,
quotient, accumulated sum).  The default is the current hardware, ap_fixed<16, 8,
AP_TRN, AP_SAT> data and ap_fixed<32, 16, AP_TRN, AP_SAT> accumulators.  No scaling is
applied before the inversion, so entries of ``den`` beyond the integer range overflow
exactly as they would in the hardware.

A pivot that truncation drives to <= 0 makes the hardware divide by zero (undefined
in the C++).  Here that inversion returns NaN, so the affected equalizer detects
garbage and the failure shows up as symbol errors; `stats` counts every occurrence.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

#: TCC/hardware/golden_cholesky.py, from TCC/software/simulador/dbp_sim/
MODEL_PATH = Path(__file__).resolve().parents[3] / "hardware" / "golden_cholesky.py"

_model = None

#: Counters since the last `reset_stats()`.
stats = {"calls": 0, "overflow_calls": 0, "failed_calls": 0}


def _load():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"hardware model not found: {MODEL_PATH}")
        spec = importlib.util.spec_from_file_location("golden_cholesky", MODEL_PATH)
        _model = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_model)
    return _model


def reset_stats() -> None:
    for key in stats:
        stats[key] = 0


def cholesky_hw_inverse(A: np.ndarray, fmt=None) -> np.ndarray:
    """A^-1 as the fixed-point hardware computes it.

    ``fmt`` is the model's `Formats` (data, accumulator and intermediate types);
    None takes the current hardware.  Build it with `make_inverter`.
    """
    model = _load()
    model.reset_overflow_count()
    stats["calls"] += 1
    try:
        inv = np.array(model.invert(A, fmt or model.FORMATS), dtype=complex)
    except ZeroDivisionError:
        stats["failed_calls"] += 1
        return np.full(A.shape, np.nan, dtype=complex)
    if model.get_overflow_count():
        stats["overflow_calls"] += 1
    return inv


#: Intermediate types of the hardware (cholesky.h: CHOL_MULIN_*, CHOL_PROD_*, ...).
#: 'sqrt' takes bits only: hls::sqrt accepts only the default ap_fixed modes.
INTERMEDIATES = ("mulin", "prod", "cmul", "num", "norm", "quot", "sum", "sqrt")
BITS_ONLY = ("sqrt",)


def make_inverter(name: str, int_bits: int = 8, frac_bits: int = 8,
                  acc_int_bits: int | None = None, acc_frac_bits: int | None = None,
                  quant: str = "AP_TRN", overflow: str = "AP_SAT",
                  acc_quant: str | None = None, acc_overflow: str | None = None,
                  intermediates: tuple = ()):
    """Inverse for the BCD-MMSE update. None = floating-point solve.

    Integer bits include the sign.  Accumulator bits default to twice the data bits
    and accumulator modes to the data modes, as in cholesky.h.  ``intermediates``
    holds ``(name, (int_bits, frac_bits, quant, overflow))`` pairs for any of
    `INTERMEDIATES`; a None field keeps that field's default ('mulin' with no field
    set means no conversion; 'sqrt' takes only the two bit counts).
    """
    if name == "float":
        return None
    if name == "hls":
        # The HLS hardware itself (C-simulation server); only the data format and its
        # modes are parameters, the rest follows cholesky.h's defaults
        if (acc_int_bits, acc_frac_bits, acc_quant, acc_overflow) != (None,) * 4 or intermediates:
            raise ValueError("'hls' takes only int/frac bits, quant and overflow")
        from dbp_sim.hls_inverse import make_hls_inverter
        return make_hls_inverter(int_bits, frac_bits, quant, overflow)
    if name == "cholesky_hw":
        model = _load()
        fix = model.fixed_type(int_bits, frac_bits, quant, overflow)
        acc = model.default_acc(fix)
        acc = model.fixed_type(acc.int_bits if acc_int_bits is None else acc_int_bits,
                               acc.frac if acc_frac_bits is None else acc_frac_bits,
                               acc_quant or quant, acc_overflow or overflow)
        base = model.make_formats(fix, acc)
        chosen = {key: model.resolve_intermediate(base, key, *vals)
                  for key, vals in intermediates}
        fmt = model.make_formats(fix, acc, **chosen)
        # Fails here, not mid-run, if the format is outside what the model reproduces
        model.check_formats(fmt)

        def inverse(A):
            return cholesky_hw_inverse(A, fmt)
        inverse.fmt = fmt        # the format actually built, for checks against the hardware
        return inverse
    raise ValueError(f"unknown inverse {name!r}")
