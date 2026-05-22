"""Channel generation: correlated Rayleigh and .mat file loading."""

import numpy as np
from config import SimConfig


def generate_channel_rayleigh(cfg: SimConfig):
    """Generate one channel realisation using i.i.d. Rayleigh fading.

    Each element of H is drawn i.i.d. from CN(0, 1).
    After generation, the channel is normalised so that the average
    received power per antenna per UE equals 1 (matching the MATLAB code).

    This is the standard baseline model for testing massive MIMO
    equalizer algorithms. For realistic 3GPP channels, use
    generate_channel_from_mat() with exported QuaDRiGa data.

    Parameters
    ----------
    cfg : SimConfig

    Returns
    -------
    H_tgt : np.ndarray, shape (M, K) — target UE channels
    H_itf : np.ndarray, shape (M, r) — interfering UE channels
    """
    n_UE = cfg.K + cfg.r

    # i.i.d. Rayleigh: each element ~ CN(0, 1)
    H_full = (np.random.randn(cfg.M, n_UE)
              + 1j * np.random.randn(cfg.M, n_UE)) / np.sqrt(2)

    # Per-column normalisation: ||h_k||^2 / M = 1
    for k in range(n_UE):
        col_pow = np.sum(np.abs(H_full[:, k]) ** 2) / cfg.M
        if col_pow > 0:
            H_full[:, k] /= np.sqrt(col_pow)

    H_tgt = H_full[:, :cfg.K]
    H_itf = H_full[:, cfg.K:]
    return H_tgt, H_itf


_mat_cache = {}  # module-level cache: filepath -> (H_tgt_all, H_itf_all)


def _normalize_per_column(H_all):
    """Normalize each UE column so that ||h_k||^2 / M = 1.

    H_all : (M, n_UE, N_mc)
    """
    M = H_all.shape[0]
    for mc in range(H_all.shape[2]):
        for k in range(H_all.shape[1]):
            col_pow = np.sum(np.abs(H_all[:, k, mc]) ** 2) / M
            if col_pow > 0:
                H_all[:, k, mc] /= np.sqrt(col_pow)
    return H_all


def generate_channel_from_mat(filepath: str, mc_idx: int, cfg: SimConfig):
    """Load pre-generated QuaDRiGa channels from a .mat file.

    The file is loaded once, per-column normalized, and cached.

    Expected .mat file structure (saved with -v7 from MATLAB):
      H_tgt_all : (M, K, N_mc) complex array
      H_itf_all : (M, r, N_mc) complex array

    Parameters
    ----------
    filepath : str
        Path to .mat file exported by export_quadriga_channels.m.
    mc_idx : int
        Monte Carlo realisation index (0-based).
    cfg : SimConfig

    Returns
    -------
    H_tgt : np.ndarray, shape (M, K)
    H_itf : np.ndarray, shape (M, r)
    """
    global _mat_cache
    if filepath not in _mat_cache:
        from scipy.io import loadmat
        print(f"  Loading channels from {filepath}...")
        data = loadmat(filepath)
        H_tgt_all = data['H_tgt_all'].copy()
        H_itf_all = data['H_itf_all'].copy()

        # Per-column normalization: ||h_k||^2 / M = 1 for every UE
        print("  Applying per-column normalization...")
        H_tgt_all = _normalize_per_column(H_tgt_all)
        H_itf_all = _normalize_per_column(H_itf_all)

        n_mc_avail = H_tgt_all.shape[2]
        print(f"  Loaded {n_mc_avail} realisations: "
              f"H_tgt={H_tgt_all.shape}, H_itf={H_itf_all.shape}")
        _mat_cache[filepath] = (H_tgt_all, H_itf_all)

    H_tgt_all, H_itf_all = _mat_cache[filepath]

    if mc_idx >= H_tgt_all.shape[2]:
        raise IndexError(
            f"mc_idx={mc_idx} but .mat file only has "
            f"{H_tgt_all.shape[2]} realisations. "
            f"Set --N_mc <= {H_tgt_all.shape[2]}")

    H_tgt = H_tgt_all[:, :, mc_idx]
    H_itf = H_itf_all[:, :, mc_idx]
    return H_tgt, H_itf
