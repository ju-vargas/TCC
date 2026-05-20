"""Utility functions: partitioning, detection, error counting, stable inversion."""

import numpy as np
from config import SimConfig


def inv_stable(A: np.ndarray) -> np.ndarray:
    """Regularised (Tikhonov) matrix inversion.

    Adds a small diagonal to avoid numerical singularity.
    """
    n = A.shape[0]
    tr = np.real(np.trace(A))
    reg = max(tr / n * 1e-10, 1e-14)
    return np.linalg.solve(A + reg * np.eye(n), np.eye(n))


def cluster_indices(c: int, cfg: SimConfig) -> np.ndarray:
    """Return the antenna indices belonging to cluster c.

    In 'contiguous' mode:   [c*Mc, c*Mc+1, ..., (c+1)*Mc-1]
    In 'interleaved' mode:  [c, c+C, c+2C, ..., c+(Mc-1)*C]
    """
    if cfg.cluster_mode == 'interleaved':
        return np.arange(c, cfg.M, cfg.C)
    else:
        return np.arange(c * cfg.Mc, (c + 1) * cfg.Mc)


def partition_clusters(H, Y, N_mat, cfg: SimConfig):
    """Split M-dimensional arrays into C antenna clusters.

    Supports both contiguous and interleaved antenna-to-cluster mapping,
    controlled by cfg.cluster_mode.

    Parameters
    ----------
    H : np.ndarray, shape (M, K)
    Y : np.ndarray or None, shape (M, Ns)
    N_mat : np.ndarray, shape (M, N)

    Returns
    -------
    Hc : list of np.ndarray, each (Mc, K)
    Yc : list of np.ndarray, each (Mc, Ns) or list of None
    Nc : list of np.ndarray, each (Mc, N)
    """
    Hc = []
    Yc = []
    Nc = []
    for c in range(cfg.C):
        idx = cluster_indices(c, cfg)
        Hc.append(H[idx, :])
        Nc.append(N_mat[idx, :])
        if Y is not None:
            Yc.append(Y[idx, :])
        else:
            Yc.append(None)
    return Hc, Yc, Nc


def compute_local_cov(Nc, cfg: SimConfig):
    """Compute local diagonal blocks of noise covariance.

    Parameters
    ----------
    Nc : list of np.ndarray, each (Mc, N)

    Returns
    -------
    Rcc : list of np.ndarray, each (Mc, Mc)
    Rcc_inv : list of np.ndarray, each (Mc, Mc)
    """
    Rcc = []
    Rcc_inv = []
    for c in range(cfg.C):
        R = (Nc[c] @ Nc[c].conj().T) / cfg.N_samples
        Rcc.append(R)
        Rcc_inv.append(inv_stable(R))
    return Rcc, Rcc_inv


def apply_equalizer(W_list, Yc, cfg: SimConfig) -> np.ndarray:
    """Apply block equalizer to partitioned received signal.

    Parameters
    ----------
    W_list : list of np.ndarray, each (K, Mc)
    Yc : list of np.ndarray, each (Mc, Ns)

    Returns
    -------
    S_hat : np.ndarray, shape (K, Ns)
    """
    Ns = Yc[0].shape[1]
    S_hat = np.zeros((cfg.K, Ns), dtype=complex)
    for c in range(cfg.C):
        S_hat += W_list[c] @ Yc[c]
    return S_hat


def detect(S_hat: np.ndarray, const: np.ndarray) -> np.ndarray:
    """Hard minimum-distance symbol detection.

    Parameters
    ----------
    S_hat : np.ndarray, shape (K, Ns) — soft estimates
    const : np.ndarray, shape (Mc,)   — constellation

    Returns
    -------
    S_det : np.ndarray, shape (K, Ns) — detected symbols
    """
    K, Ns = S_hat.shape
    S_det = np.empty((K, Ns), dtype=complex)
    for k in range(K):
        # (Ns, 1) - (1, Mc) → (Ns, Mc) distance matrix
        d2 = np.abs(S_hat[k, :, None] - const[None, :]) ** 2
        best = np.argmin(d2, axis=1)
        S_det[k, :] = const[best]
    return S_det


def count_errors(S_det: np.ndarray, S_tx: np.ndarray):
    """Count symbol errors.

    Returns
    -------
    n_err : int
    n_total : int
    """
    n_err = int(np.sum(S_det.ravel() != S_tx.ravel()))
    n_total = S_tx.size
    return n_err, n_total
