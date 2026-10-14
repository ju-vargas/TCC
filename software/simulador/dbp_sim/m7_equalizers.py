"""M7 - Equalizers.

Every equalizer returns W with ``s_hat = W @ y`` for the *full* received vector, so the
driver and metric stay uniform.  Decentralization is real inside each routine: no
equalizer ever touches a matrix larger than the article permits.

Figure 8 plots six of these: LMMSE, ZF, BCD-MMSE (1 iteration), BCD-MMSE LRD
(4 iterations), sDR-MMSE and cDR-MMSE.  BDAC-MMSE (Eq. 7) is not plotted in Fig. 8 but
is required as the BCD initialiser.

Conditioning
------------
Every routine takes a `Conditioner` (see `m5_noise`) rather than a raw covariance, and asks
it for the conditioned covariance of whatever sample block it is entitled to see.  This
keeps the decentralization honest - a DU conditions its own `S_c`, never the global matrix -
and keeps the choice of conditioning rule in one place.

Conditioning is *forced* by the article's own equations for the centralized LMMSE at
M = 256, where ``rank(R_hat) <= N = 192 < 256``.  The decentralized methods only ever
invert ``M_c x M_c`` blocks (M_c <= 32 with N = 192) and would run unconditioned.
"""

from __future__ import annotations

import numpy as np

from .m5_noise import Conditioner


# --------------------------------------------------------------------------------------
# Centralized baselines
# --------------------------------------------------------------------------------------


def lmmse(H: np.ndarray, S: np.ndarray, Es: float, cond: Conditioner) -> np.ndarray:
    """Eq. (3): W = (H^H R^-1 H + (1/Es) I)^-1 H^H R^-1, with R = R_hat (footnote 5)."""
    K = H.shape[1]
    R = cond.covariance(S)                                     # the one global inversion
    # R is Hermitian, so H^H R^-1 == (R^-1 H)^H: one M x K solve replaces the
    # M x M inverse the expression appears to require.
    X = cond.solve(R, H) if cond.mode == "none" else np.linalg.solve(R, H)
    A = H.conj().T @ X + np.eye(K) / Es
    return np.linalg.solve(A, X.conj().T)


def zero_forcing(H: np.ndarray) -> np.ndarray:
    """W = (H^H H)^-1 H^H.

    The article lists ZF as a baseline (L581) but never writes the formula; this is the
    standard reading.  See params.M7_Equalizers.zf_form.
    """
    return np.linalg.solve(H.conj().T @ H, H.conj().T)


# --------------------------------------------------------------------------------------
# Decentralized: block-diagonal approximation (Eq. 7) - the BCD initialiser
# --------------------------------------------------------------------------------------


def bdac_mmse(H: np.ndarray, S: np.ndarray, clusters: list[np.ndarray],
              Es: float, cond: Conditioner) -> np.ndarray:
    """Eq. (7): block-diagonal approximate covariance MMSE.

    Each DU inverts only its own ``R_hat_cc`` (M_c x M_c); the K x K sum is then formed
    centrally and broadcast back.
    """
    M, K = H.shape
    G = np.eye(K, dtype=complex) / Es
    blocks = []
    for idx in clusters:
        Rcc = cond.covariance(S[idx])                          # DU c conditions its own block
        X = np.linalg.solve(Rcc, H[idx])                       # R_cc^-1 H_c
        G += H[idx].conj().T @ X
        blocks.append(X.conj().T)                              # H_c^H R_cc^-1
    Ginv = np.linalg.inv(G)
    W = np.zeros((K, M), dtype=complex)
    for idx, B in zip(clusters, blocks):
        W[:, idx] = Ginv @ B
    return W


# --------------------------------------------------------------------------------------
# Decentralized: dimensionality reduction for the star architecture
# --------------------------------------------------------------------------------------


def _local_compressors(H: np.ndarray, S: np.ndarray, clusters: list[np.ndarray],
                       cond: Conditioner) -> list[np.ndarray]:
    """Q_c = H_c^H R_cc^-1, shape K x M_c (L184)."""
    out = []
    for idx in clusters:
        Rcc = cond.covariance(S[idx])
        out.append(np.linalg.solve(Rcc, H[idx]).conj().T)
    return out


def sdr_mmse(H: np.ndarray, S: np.ndarray, clusters: list[np.ndarray],
             Es: float, cond: Conditioner) -> np.ndarray:
    """Algorithm 1 - superimposed DR-MMSE, Eqs. (11)-(16).

    The CU sums the compressed contributions, so the effective system is K-dimensional.
    """
    M, K = H.shape
    Qs = _local_compressors(H, S, clusters, cond)

    Qcheck = np.zeros((K, M), dtype=complex)                   # [Q_1 ... Q_C], Eq. (11)
    for idx, Q in zip(clusters, Qs):
        Qcheck[:, idx] = Q

    H_eff = Qcheck @ H                                         # Eq. (13a)
    # Eq. (14) sums the COMPRESSED noise samples {Q_c n_c^i}, which Algorithm 1 says the
    # DUs transmit.  Building R_eff from them (rather than from Q R_hat Q^H) lets the CU
    # condition its own estimate, exactly as a DU conditions R_cc.
    R_eff = cond.covariance(Qcheck @ S)                        # Eq. (14)

    X = np.linalg.solve(R_eff, H_eff)
    A = H_eff.conj().T @ X + np.eye(K) / Es                    # Eq. (15)
    return np.linalg.solve(A, X.conj().T) @ Qcheck


def cdr_mmse(H: np.ndarray, S: np.ndarray, clusters: list[np.ndarray],
             Es: float, cond: Conditioner) -> np.ndarray:
    """Algorithm 2 - concatenated DR-MMSE, Eqs. (17)-(23).

    The CU stacks rather than sums, so it inverts a CK x CK matrix - more capable than
    sDR (Proposition 1) at higher cost.
    """
    M, K = H.shape
    C = len(clusters)
    Qs = _local_compressors(H, S, clusters, cond)

    Qtil = np.zeros((C * K, M), dtype=complex)                 # blkdiag(Q_1..Q_C), Eq.(17)
    for c, (idx, Q) in enumerate(zip(clusters, Qs)):
        Qtil[c * K:(c + 1) * K, idx] = Q

    H_eff = Qtil @ H                                           # Eq. (19)
    # Eq. (20)-(21) from the compressed samples the CU receives (Algorithm 2).  This one
    # matters: R_eff is CK x CK (128 at C=16) estimated from N=192 samples, and measured
    # cond ~1.4e5 - squarely in the regime where the estimate must be conditioned.
    R_eff = cond.covariance(Qtil @ S)                          # Eq. (20)

    X = np.linalg.solve(R_eff, H_eff)
    A = H_eff.conj().T @ X + np.eye(K) / Es                    # Eq. (22)
    return np.linalg.solve(A, X.conj().T) @ Qtil


# --------------------------------------------------------------------------------------
# Decentralized: block coordinate descent for the daisy chain
# --------------------------------------------------------------------------------------


def bcd_mmse(H: np.ndarray, S: np.ndarray, clusters: list[np.ndarray],
             Es: float, n_iter: int, cond: Conditioner,
             W0: np.ndarray | None = None,
             S_full: np.ndarray | None = None,
             inverse=None) -> np.ndarray:
    """Algorithm 3 - BCD-MMSE after ``n_iter`` iterations. See `bcd_mmse_path`."""
    return bcd_mmse_path(H, S, clusters, Es, n_iter, cond, W0, S_full, inverse)[-1]


def bcd_mmse_path(H: np.ndarray, S: np.ndarray, clusters: list[np.ndarray],
                  Es: float, n_iter: int, cond: Conditioner,
                  W0: np.ndarray | None = None,
                  S_full: np.ndarray | None = None,
                  inverse=None) -> list[np.ndarray]:
    """Algorithm 3 - BCD-MMSE, Eqs. (26)/(28)/(29)/(30).

    Returns ``W`` after each of the ``n_iter`` iterations (element ``l - 1`` is the
    equalizer after iteration ``l``), so one run gives every iteration count.

    Parameters
    ----------
    S
        Scaled sample matrix, ``M x n`` with ``S S^H == R_hat``.  Pass the full
        ``N = (1/sqrt(N))[n^1..n^N]`` for plain BCD-MMSE, or the rank-r factor ``G`` from
        `lrd_decomposition` for BCD-MMSE (LRD).
    W0
        Initialiser; defaults to BDAC-MMSE (Eq. 7) as the article specifies.
    inverse
        Callable ``A -> A^-1`` for the ``M_c x M_c`` inversion of the update, e.g.
        `hw_inverse.cholesky_hw_inverse`.  None solves in floating point.

    Each DU c updates ``W_c`` from local data plus the two running variables it receives
    from its predecessor: ``A`` (K x K) and ``B`` (K x n).  Gauss-Seidel order with the
    ring convention ``A_0^l = A_C^(l-1)`` (footnote 6).
    """
    M, K = H.shape
    W = (bdac_mmse(H, S_full if S_full is not None else S, clusters, Es, cond)
         if W0 is None else W0.copy())

    A = W @ H                                                  # sum_j W_j H_j
    B = W @ S                                                  # sum_j W_j S_j

    path = []
    for _ in range(n_iter):
        for idx in clusters:
            Hc, Sc, Wc = H[idx], S[idx], W[:, idx]
            A_rest = A - Wc @ Hc                               # sum over j != c
            B_rest = B - Wc @ Sc

            num = Es * (np.eye(K) - A_rest) @ Hc.conj().T - B_rest @ Sc.conj().T
            # LRD passes the rank-r factor G, not samples: its columns cannot feed
            # Ledoit-Wolf, so G_c G_c^H takes the primed intensity instead.
            Rcc = (cond.covariance(Sc) if S_full is None
                   else cond.condition(Sc @ Sc.conj().T))
            den = Es * (Hc @ Hc.conj().T) + Rcc                 # M_c x M_c

            # W_new = num @ den^-1, with den Hermitian
            if inverse is None:
                W_new = np.linalg.solve(den.conj().T, num.conj().T).conj().T
            else:
                W_new = num @ inverse(den)

            W[:, idx] = W_new
            A, B = A_rest + W_new @ Hc, B_rest + W_new @ Sc
        path.append(W.copy())
    return path


def bcd_objective(W: np.ndarray, H: np.ndarray, R_hat: np.ndarray, Es: float) -> float:
    """Objective of problem (24). Must decrease monotonically (Theorem 2, L463)."""
    E = W @ H - np.eye(H.shape[1])
    return float(Es * np.trace(E @ E.conj().T).real
                 + np.trace(W @ R_hat @ W.conj().T).real)


# --------------------------------------------------------------------------------------
# Low-rank decomposition (Algorithm 4)
# --------------------------------------------------------------------------------------


def lrd_decomposition(S: np.ndarray, clusters: list[np.ndarray], r: int) -> np.ndarray:
    """Algorithm 4 - decentralized rank-r decomposition of the sample matrix.

    Walks the daisy chain accumulating a rank-r sketch, then broadcasts the final right
    singular vectors so each DU can form ``G_c = S_c V_C`` locally.  Returns G (M x r)
    with ``G G^H`` approximating ``R_hat``.

    The per-hop transfer is ``(M + n) x r`` rather than ``M x n`` - the point of the
    algorithm.  Reproduced here for fidelity even though a centralised SVD would give the
    same G, because the sketching is lossy and that loss is part of the method.
    """
    M = S.shape[0]
    D_prev: np.ndarray | None = None
    V_prev: np.ndarray | None = None

    for c, idx in enumerate(clusters):
        Sc = S[idx]
        if c == 0:
            stacked = Sc
        else:
            assert D_prev is not None and V_prev is not None
            stacked = np.vstack([D_prev @ V_prev.conj().T, Sc])   # [N~_{c-1}; S_c]
        U, sv, Vh = np.linalg.svd(stacked, full_matrices=False)
        k = min(r, sv.size)
        D_prev = U[:, :k] * sv[:k]                                # D_c = U_c Sigma_c
        V_prev = Vh[:k].conj().T                                  # V_c

    assert V_prev is not None
    V_final = V_prev
    G = np.zeros((M, V_final.shape[1]), dtype=complex)
    for idx in clusters:
        G[idx] = S[idx] @ V_final                                 # G_c = S_c V_C
    return G
