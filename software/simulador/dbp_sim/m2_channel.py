"""M2 - Channel generation.

The article generates H and Hbar with QuaDriGa (L577), which is MATLAB-only.  Two
backends are provided:

``QuaDriGaFileChannel``
    Loads channels exported from QuaDriGa.  **This is the faithful path** and the one
    used for the results.  Export
    ``H`` of shape ``(n_realizations, M, K)`` and ``Hbar`` of shape
    ``(n_realizations, M, r)`` to an ``.npz``.

``StandInULAChannel``
    A documented substitute: a uniform linear array with limited per-UE angular spread.
    **This is not the article's channel.**  It exists so ``test_dbp_sim.py`` can check
    the SNR-axis-independent claims (curve ordering, convergence) without MATLAB.

Normalization
-------------
Both backends apply the convention of ``params.M2_Channel.normalization``.  The default,
``per_ue_power_control``, scales every UE column of ``H`` and ``Hbar`` to
``E[|h_mk|^2] = 1`` (ideal uplink power control).  ``unit_mean_entry_power`` applies one
joint factor instead and keeps the per-UE power differences.  This is the single most
result-determining choice in the simulator; see the parameter note for the measured A/B.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

#: The simulator folder (parent of the ``dbp_sim`` package). Relative data paths start here.
SIMULATOR_ROOT = Path(__file__).resolve().parent.parent


def normalize_jointly(H: np.ndarray, Hbar: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """One common scale factor so that mean |entry|^2 == 1 over [H Hbar].

    Preserves the per-UE power differences the channel model produced - i.e. NO uplink
    power control.  With real QuaDriGa channels over the article's 50-100 m annulus this
    leaves a ~13 dB median spread across UEs, and SER is then dominated by the
    worst-placed one.
    """
    total_power = float(np.vdot(H, H).real + np.vdot(Hbar, Hbar).real)
    n_entries = H.size + Hbar.size
    if total_power <= 0:
        raise ValueError("degenerate channel: zero total power")
    alpha = np.sqrt(n_entries / total_power)
    return alpha * H, alpha * Hbar


def normalize_per_ue(H: np.ndarray, Hbar: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Scale each UE's column to E[|h_mk|^2] = 1 - i.e. ideal uplink power control.

    Every UE arrives at the BS with the same average power, which is what a system with
    closed-loop power control achieves.  The article never mentions power control, but it
    also never mentions the large per-UE spread that its own geometry implies; see
    params.M2_Channel.normalization.
    """
    M = H.shape[0]
    def scale(X):
        p = (np.abs(X) ** 2).sum(axis=0, keepdims=True)     # 1 x n_ue
        if np.any(p <= 0):
            raise ValueError("degenerate channel: a UE has zero power")
        return X * np.sqrt(M / p)
    return scale(H), scale(Hbar)


NORMALIZERS = {
    "unit_mean_entry_power": normalize_jointly,
    "per_ue_power_control": normalize_per_ue,
}


class ChannelBackend:
    """Interface: produce (H, Hbar) for one realization."""

    def generate(self, M: int, K: int, r: int, realization: int,
                 rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError


@dataclass
class QuaDriGaFileChannel(ChannelBackend):
    """Load QuaDriGa-generated channels from .npz exports. The faithful path.

    Figure 8 needs three different (M, K, r) configurations, so the backend resolves
    ``dados/channels_quadriga_M{M}_K{K}_r{r}.npz`` per panel and caches each file once.
    A relative ``path`` is taken from the simulator folder, not from the working
    directory; it may also be a single explicit path, used for every configuration.
    """

    path: str = "dados/channels_quadriga_M{M}_K{K}_r{r}.npz"
    normalization: str = "per_ue_power_control"
    _cache: dict = field(default_factory=dict)

    def _load(self, M: int, K: int, r: int):
        key = (M, K, r)
        if key in self._cache:
            return self._cache[key]
        p = Path(self.path.format(M=M, K=K, r=r))
        if not p.is_absolute():
            p = SIMULATOR_ROOT / p
        if not p.exists():
            raise FileNotFoundError(
                f"QuaDriGa export not found: {p}\n"
                "Generate it with:\n"
                "  matlab -nodisplay -r \"run('quadriga/export_quadriga_channels.m')\"\n"
                "  .venv/bin/python quadriga/convert_quadriga_export.py\n"
                "Or use --channel standin_ula for the substitute channel (NOT the "
                "article's).")
        data = np.load(p, allow_pickle=False)
        H, Hbar = data["H"], data["Hbar"]
        if H.shape[1:] != (M, K) or Hbar.shape[1:] != (M, r):
            raise ValueError(
                f"{p}: shape mismatch - got H{H.shape}, Hbar{Hbar.shape}; "
                f"expected (*, {M}, {K}) and (*, {M}, {r})")
        self._cache[key] = (H, Hbar)
        return H, Hbar

    def generate(self, M, K, r, realization, rng):
        H, Hbar = self._load(M, K, r)
        n = H.shape[0]
        if realization >= n:
            raise IndexError(
                f"requested realization {realization} but the export holds only {n}. "
                "Re-export with more realizations rather than cycling, which would "
                "silently reuse channels.")
        return NORMALIZERS[self.normalization](H[realization], Hbar[realization])


@dataclass
class StandInULAChannel(ChannelBackend):
    """Substitute channel - NOT QuaDriGa, NOT the article's model.

    Half-wavelength ULA; each UE gets `n_paths` rays inside +-`spread_deg` of a mean
    angle drawn uniformly in the article's 120 degree sector.  The radial coordinate is
    drawn in [radius_min, radius_max] but only enters through free-space path loss, which
    the joint normalization then largely removes - so this backend reproduces the
    article's *angular* geometry, not its large-scale fading.
    """

    spread_deg: float = 10.0
    n_paths: int = 20
    sector_deg: float = 120.0
    radius_min_m: float = 50.0
    radius_max_m: float = 100.0
    normalization: str = "per_ue_power_control"

    def _one(self, M: int, n_ue: int, rng: np.random.Generator) -> np.ndarray:
        m = np.arange(M)
        out = np.zeros((M, n_ue), dtype=complex)
        half = self.sector_deg / 2.0
        for k in range(n_ue):
            mean_deg = rng.uniform(-half, half)
            rays = np.deg2rad(mean_deg + rng.uniform(-self.spread_deg,
                                                     self.spread_deg, self.n_paths))
            steering = np.exp(1j * np.pi * m[:, None] * np.sin(rays)[None, :])
            gains = (rng.standard_normal(self.n_paths)
                     + 1j * rng.standard_normal(self.n_paths)) / np.sqrt(2)
            radius = rng.uniform(self.radius_min_m, self.radius_max_m)
            out[:, k] = (steering @ gains) / np.sqrt(self.n_paths) / radius
        return out

    def generate(self, M, K, r, realization, rng):
        return NORMALIZERS[self.normalization](self._one(M, K, rng), self._one(M, r, rng))


def make_backend(name: str, **kwargs) -> ChannelBackend:
    if name == "quadriga_file":
        return QuaDriGaFileChannel(
            path=kwargs["path"],
            normalization=kwargs.get("normalization", "per_ue_power_control"))
    if name == "standin_ula":
        return StandInULAChannel(
            spread_deg=kwargs.get("spread_deg", 10.0),
            n_paths=kwargs.get("n_paths", 20),
            sector_deg=kwargs.get("sector_deg", 120.0),
            radius_min_m=kwargs.get("radius_min_m", 50.0),
            radius_max_m=kwargs.get("radius_max_m", 100.0),
            normalization=kwargs.get("normalization", "per_ue_power_control"))
    raise ValueError(f"unknown channel backend {name!r}")
