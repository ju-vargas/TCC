#!/usr/bin/env python3
"""Convert the model-A QuaDriGa band exports to the .npz layout `dbp_sim` expects.

    cd quadriga && matlab -nodisplay -nosplash -r export_quadriga_channels
    ../simulador/.venv/bin/python quadriga/convert_quadriga_export.py

MATLAB stores ``H`` as ``(M, K, n_carriers, n_realizations)``; the Python side wants
``(n_realizations, n_carriers, M, K)``, kept in complex64.

Regression check: the export uses the same drops as the single-carrier export of the
original simulator, and carrier 0 is f0 in both.  So carrier 0 must match
``dados/channels_quadriga_M*_K*_r*.npz`` (copied from ../simulador/dados) up to
single-precision rounding.  A mismatch means something other than the frequency axis
changed.  The export's ``cfg`` struct is carried through so every
figure can be traced back to the scenario, carrier frequency and array that produced it.

No normalization is applied here - `dbp_sim.m2_channel` owns that
(params.M2_Channel.normalization).
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import scipy.io as sio


def convert(mat_path: str) -> Path:
    d = sio.loadmat(mat_path, squeeze_me=False)
    H = np.asarray(d["H"])          # M x K x n_real
    Hbar = np.asarray(d["Hbar"])    # M x r x n_real

    if H.ndim != 4 or Hbar.ndim != 4:
        raise ValueError(f"{mat_path}: expected 4-D H/Hbar, got {H.shape}/{Hbar.shape}")
    if not (np.iscomplexobj(H) and np.iscomplexobj(Hbar)):
        raise ValueError(f"{mat_path}: channels must be complex")
    if H.shape[0] != Hbar.shape[0] or H.shape[2:] != Hbar.shape[2:]:
        raise ValueError(f"{mat_path}: H {H.shape} and Hbar {Hbar.shape} disagree")
    if not (np.isfinite(H).all() and np.isfinite(Hbar).all()):
        raise ValueError(f"{mat_path}: non-finite entries")

    H = np.transpose(H, (3, 2, 0, 1)).astype(np.complex64)        # n_real x n_carr x M x K
    Hbar = np.transpose(Hbar, (3, 2, 0, 1)).astype(np.complex64)  # n_real x n_carr x M x r

    # carry the provenance of the export forward
    meta = {}
    if "cfg" in d:
        c = d["cfg"]
        for name in c.dtype.names or ():
            v = c[name][0, 0]
            meta[name] = (v.item() if getattr(v, "size", 0) == 1
                          else str(np.squeeze(v)))

    out = Path(mat_path).with_suffix(".npz")
    np.savez_compressed(out, H=H, Hbar=Hbar, meta=json.dumps(meta))

    n, n_carr, M, K = H.shape
    r = Hbar.shape[3]
    print(f"  {Path(mat_path).name}  ->  {out.name}")
    print(f"      {n} realizations, {n_carr} carriers, M={M}, K={K}, r={r}")

    single = out.parent / f"channels_quadriga_M{M}_K{K}_r{r}.npz"
    if single.exists():
        ref = np.load(single)
        err = max(np.abs(H[:, 0] - ref["H"]).max() / np.abs(ref["H"]).max(),
                  np.abs(Hbar[:, 0] - ref["Hbar"]).max() / np.abs(ref["Hbar"]).max())
        status = "OK" if err < 1e-5 else "MISMATCH"
        print(f"      carrier 0 vs {single.name}: max relative error {err:.1e}  {status}")
        if status != "OK":
            raise SystemExit("carrier 0 does not match the single-carrier export")
    else:
        print(f"      (no {single.name} to check carrier 0 against)")
    if meta:
        keep = {k: meta[k] for k in ("scenario", "center_freq", "bs_height_m")
                if k in meta}
        print(f"      {keep}")
    return out


def main() -> None:
    dados = Path(__file__).resolve().parent.parent / "dados"
    mats = sorted(glob.glob(str(dados / "channels_quadriga_mc_*.mat")))
    if not mats:
        raise SystemExit(f"no channels_quadriga_mc_*.mat found in {dados} - run "
                         "quadriga/export_quadriga_channels.m in MATLAB first")
    print(f"converting {len(mats)} export(s):")
    for m in mats:
        convert(m)


if __name__ == "__main__":
    main()
