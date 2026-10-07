#!/usr/bin/env python3
"""Convert QuaDriGa MATLAB exports to the .npz layout `dbp_sim` expects.

    matlab -batch "run('quadriga/export_quadriga_channels.m')"   # writes dados/channels_*.mat
    .venv/bin/python quadriga/convert_quadriga_export.py         # writes dados/channels_*.npz

MATLAB stores ``H`` as ``(M, K, n_realizations)``; the Python side wants
``(n_realizations, M, K)``.  The export's ``cfg`` struct is carried through so every
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

    if H.ndim != 3 or Hbar.ndim != 3:
        raise ValueError(f"{mat_path}: expected 3-D H/Hbar, got {H.shape}/{Hbar.shape}")
    if not (np.iscomplexobj(H) and np.iscomplexobj(Hbar)):
        raise ValueError(f"{mat_path}: channels must be complex")
    if H.shape[0] != Hbar.shape[0] or H.shape[2] != Hbar.shape[2]:
        raise ValueError(f"{mat_path}: H {H.shape} and Hbar {Hbar.shape} disagree")
    if not (np.isfinite(H).all() and np.isfinite(Hbar).all()):
        raise ValueError(f"{mat_path}: non-finite entries")

    H = np.transpose(H, (2, 0, 1))          # n_real x M x K
    Hbar = np.transpose(Hbar, (2, 0, 1))    # n_real x M x r

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

    n, M, K = H.shape
    r = Hbar.shape[2]
    per_ue = (np.abs(H[0]) ** 2).sum(0)
    spread = 10 * np.log10(per_ue.max() / per_ue.min())
    print(f"  {Path(mat_path).name}  ->  {out.name}")
    print(f"      {n} realizations, M={M}, K={K}, r={r}; "
          f"per-UE power spread {spread:.1f} dB (real path loss)")
    if meta:
        keep = {k: meta[k] for k in ("scenario", "center_freq", "bs_height_m")
                if k in meta}
        print(f"      {keep}")
    return out


def main() -> None:
    dados = Path(__file__).resolve().parent.parent / "dados"
    mats = sorted(glob.glob(str(dados / "channels_quadriga_*.mat")))
    if not mats:
        raise SystemExit(f"no channels_quadriga_*.mat found in {dados} - run "
                         "quadriga/export_quadriga_channels.m in MATLAB first")
    print(f"converting {len(mats)} export(s):")
    for m in mats:
        convert(m)


if __name__ == "__main__":
    main()
