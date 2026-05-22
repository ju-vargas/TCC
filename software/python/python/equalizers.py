"""Equalizer implementations for the Massive MIMO DBP simulator.

All algorithms from Zhao et al. (2025):
  - Centralised LMMSE (Eq. 3)
  - Centralised ZF
  - BDAC-MMSE (Eq. 7)
  - sDR-MMSE (Algorithm 1)
  - cDR-MMSE (Algorithm 2)
  - BCD-MMSE update (Algorithm 3)
  - LRD algorithm (Algorithm 4)
  - BCD-MMSE LRD update (Section IV-B)
"""

import numpy as np
from scipy.sparse.linalg import svds
from config import SimConfig
from utils import inv_stable, cluster_indices


# ============================================================================
# Centralised baselines
# ============================================================================

def lmmse_centralised(H: np.ndarray, R_est: np.ndarray, Es: float) -> np.ndarray:
    """Centralised LMMSE equalizer (Eq. 3).

    W = (H^H R^{-1} H + (1/Es)I)^{-1} H^H R^{-1}

    Parameters
    ----------
    H     : (M, K)
    R_est : (M, M) — estimated noise covariance
    Es    : scalar — symbol energy

    Returns
    -------
    W : (K, M)
    """
    K = H.shape[1]
    R_inv = inv_stable(R_est)
    A = H.conj().T @ R_inv @ H + (1.0 / Es) * np.eye(K)
    W = inv_stable(A) @ (H.conj().T @ R_inv)
    return W


def zf_centralised(H: np.ndarray) -> np.ndarray:
    """Centralised Zero-Forcing equalizer.

    W = (H^H H)^{-1} H^H

    Parameters
    ----------
    H : (M, K)

    Returns
    -------
    W : (K, M)
    """
    return inv_stable(H.conj().T @ H) @ H.conj().T


# ============================================================================
# Decentralised equalizers
# ============================================================================

def bdac_mmse(Hc: list, Rcc_inv: list, cfg: SimConfig) -> list:
    """BDAC-MMSE equalizer (Eq. 7).

    Block-diagonal approximate covariance MMSE.

    Returns
    -------
    W_list : list of (K, Mc) arrays
    """
    Gram = np.zeros((cfg.K, cfg.K), dtype=complex)
    for c in range(cfg.C):
        Gram += Hc[c].conj().T @ Rcc_inv[c] @ Hc[c]
    A_inv = inv_stable(Gram + (1.0 / cfg.Es) * np.eye(cfg.K))

    W_list = []
    for c in range(cfg.C):
        W_list.append(A_inv @ Hc[c].conj().T @ Rcc_inv[c])
    return W_list


def sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg: SimConfig, R_true: np.ndarray = None) -> np.ndarray:
    """Superimposed DR-MMSE (Algorithm 1).

    Returns
    -------
    S_hat : (K, Ns)
    """
    N = cfg.N_samples
    Ns = Yc[0].shape[1]

    y_check = np.zeros((cfg.K, Ns), dtype=complex)
    H_check = np.zeros((cfg.K, cfg.K), dtype=complex)
    QN_sum = np.zeros((cfg.K, N), dtype=complex)

    for c in range(cfg.C):
        Qc = Hc[c].conj().T @ Rcc_inv[c]  # K × Mc
        y_check += Qc @ Yc[c]
        H_check += Qc @ Hc[c]
        QN_sum += Qc @ Nc[c]

    if cfg.ideal_covariance and R_true is not None:
        Q_all = np.zeros((cfg.K, cfg.M), dtype=complex)
        for c in range(cfg.C):
            idx = cluster_indices(c, cfg)
            Q_all[:, idx] = Hc[c].conj().T @ Rcc_inv[c]
        R_check = Q_all @ R_true @ Q_all.conj().T
    else:
        R_check = (QN_sum @ QN_sum.conj().T) / N
    W = lmmse_centralised(H_check, R_check, cfg.Es)
    return W @ y_check


def cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg: SimConfig, R_true: np.ndarray = None) -> np.ndarray:
    """Concatenated DR-MMSE (Algorithm 2).

    Returns
    -------
    S_hat : (K, Ns)
    """
    N = cfg.N_samples
    Ns = Yc[0].shape[1]
    CK = cfg.C * cfg.K

    y_tilde = np.zeros((CK, Ns), dtype=complex)
    H_tilde = np.zeros((CK, cfg.K), dtype=complex)
    Qn_list = []

    for c in range(cfg.C):
        Qc = Hc[c].conj().T @ Rcc_inv[c]  # K × Mc
        rows = slice(c * cfg.K, (c + 1) * cfg.K)
        y_tilde[rows, :] = Qc @ Yc[c]
        H_tilde[rows, :] = Qc @ Hc[c]
        Qn_list.append(Qc @ Nc[c])  # K × N

    # Block noise covariance
    if cfg.ideal_covariance and R_true is not None:
        R_tilde = np.zeros((CK, CK), dtype=complex)
        for m in range(cfg.C):
            rows_m = slice(m * cfg.K, (m + 1) * cfg.K)
            idx_m = cluster_indices(m, cfg)
            Qm = Hc[m].conj().T @ Rcc_inv[m]
            for l in range(cfg.C):
                rows_l = slice(l * cfg.K, (l + 1) * cfg.K)
                idx_l = cluster_indices(l, cfg)
                Ql = Hc[l].conj().T @ Rcc_inv[l]
                R_ml = R_true[np.ix_(idx_m, idx_l)]
                R_tilde[rows_m, rows_l] = Qm @ R_ml @ Ql.conj().T
    else:
        R_tilde = np.zeros((CK, CK), dtype=complex)
        for m in range(cfg.C):
            rows_m = slice(m * cfg.K, (m + 1) * cfg.K)
            for l in range(cfg.C):
                rows_l = slice(l * cfg.K, (l + 1) * cfg.K)
                R_tilde[rows_m, rows_l] = (Qn_list[m] @ Qn_list[l].conj().T) / N

    W = lmmse_centralised(H_tilde, R_tilde, cfg.Es)
    return W @ y_tilde


def bcd_mmse_update(W_old: list, Hc: list, Nc: list, Rcc: list, cfg: SimConfig) -> list:
    """One Gauss-Seidel BCD sweep over all C clusters (Eq. 30).

    Parameters
    ----------
    W_old : list of (K, Mc) — current equalizer blocks
    Hc    : list of (Mc, K) — local channels
    Nc    : list of (Mc, N) — local noise samples
    Rcc   : list of (Mc, Mc) — local regularized covariance blocks
    cfg   : SimConfig

    Returns
    -------
    W_new : list of (K, Mc)
    """
    N = cfg.N_samples
    W_new = list(W_old)  # shallow copy

    A_prev = np.zeros((cfg.K, cfg.K), dtype=complex)
    b_prev = np.zeros((cfg.K, N), dtype=complex)
    for c in range(cfg.C):
        A_prev += W_old[c] @ Hc[c]
        b_prev += W_old[c] @ Nc[c]

    for c in range(cfg.C):
        HcHc_T = Hc[c] @ Hc[c].conj().T
        local_M = cfg.Es * HcHc_T + Rcc[c]
        local_M_inv = inv_stable(local_M)

        A_minus = A_prev - W_old[c] @ Hc[c]
        b_minus = b_prev - W_old[c] @ Nc[c]

        # Numerator (Eq. 30)
        num = cfg.Es * (np.eye(cfg.K) - A_minus) @ Hc[c].conj().T \
              - (b_minus @ Nc[c].conj().T) / N

        W_new[c] = num @ local_M_inv

        A_prev = A_minus + W_new[c] @ Hc[c]
        b_prev = b_minus + W_new[c] @ Nc[c]

    return W_new


def lrd_algorithm(Nc: list, r_rank: int, cfg: SimConfig) -> np.ndarray:
    """Decentralised low-rank decomposition (Algorithm 4).

    Parameters
    ----------
    Nc     : list of (Mc, N) noise blocks
    r_rank : target rank
    cfg    : SimConfig

    Returns
    -------
    G : (M, r) global low-rank factor s.t. G @ G^H ≈ R_est
    """
    scale = 1.0 / np.sqrt(cfg.N_samples)

    D_prev = None
    V_prev = None

    for c in range(cfg.C - 1):
        Nc_scaled = scale * Nc[c]

        if c == 0:
            U1, S1, V1h = svds(Nc_scaled, k=r_rank)
            D_prev = U1 * S1[np.newaxis, :]  # (Mc, r)
            V_prev = V1h.conj().T             # (N, r)
        else:
            N_approx = D_prev @ V_prev.conj().T
            N_stack = np.vstack([N_approx, Nc_scaled])
            Uc, Sc, Vch = svds(N_stack, k=r_rank)
            D_prev = Uc * Sc[np.newaxis, :]
            V_prev = Vch.conj().T

    # Last cluster
    Nc_scaled = scale * Nc[cfg.C - 1]
    if cfg.C == 1:
        UC, SC, VCh = svds(Nc_scaled, k=r_rank)
        V_prev = VCh.conj().T
    else:
        N_approx = D_prev @ V_prev.conj().T
        N_stack = np.vstack([N_approx, Nc_scaled])
        UC, SC, VCh = svds(N_stack, k=r_rank)
        V_prev = VCh.conj().T

    # Each DU computes Gc = (scale * Nc{c}) * V_prev
    G = np.zeros((cfg.M, r_rank), dtype=complex)
    for c in range(cfg.C):
        idx = cluster_indices(c, cfg)
        G[idx, :] = (scale * Nc[c]) @ V_prev

    return G


def bcd_mmse_lrd_update(W_old: list, Hc: list, Gc: list,
                         Rcc: list, cfg: SimConfig) -> list:
    """One BCD sweep using LRD (Section IV-B).

    Parameters
    ----------
    W_old : list of (K, Mc)
    Hc    : list of (Mc, K)
    Gc    : list of (Mc, r)
    Rcc   : list of (Mc, Mc) — full local sample covariance
    cfg   : SimConfig

    Returns
    -------
    W_new : list of (K, Mc)
    """
    W_new = list(W_old)
    r_rank = Gc[0].shape[1]

    # Initialise running sums (ring)
    A_prev = np.zeros((cfg.K, cfg.K), dtype=complex)
    B_prev = np.zeros((cfg.K, r_rank), dtype=complex)
    for c in range(cfg.C):
        A_prev += W_old[c] @ Hc[c]
        B_prev += W_old[c] @ Gc[c]

    for c in range(cfg.C):
        # Local denominator: full Rcc (includes σ²I correctly)
        local_M = cfg.Es * (Hc[c] @ Hc[c].conj().T) + Rcc[c]
        local_M_inv = inv_stable(local_M)

        # Remove old contribution
        A_minus = A_prev - W_old[c] @ Hc[c]
        B_minus = B_prev - W_old[c] @ Gc[c]

        # Numerator: cross-cluster noise via low-rank factors
        num = cfg.Es * (np.eye(cfg.K) - A_minus) @ Hc[c].conj().T \
              - B_minus @ Gc[c].conj().T

        W_new[c] = num @ local_M_inv

        # Update running sums
        A_prev = A_minus + W_new[c] @ Hc[c]
        B_prev = B_minus + W_new[c] @ Gc[c]

    return W_new
