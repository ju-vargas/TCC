"""M5 - Colored-noise generation, and M6 - covariance estimation.

Noise model (L577, L113)::

    n ~ CN(0, R),   R = beta * Hbar Hbar^H + sigma^2 I

Note the article draws the noise directly from this Gaussian (L577); Eq. (5)'s
``Hbar s_bar + n_bar`` construction is the physical motivation, not the operative
statement.

`beta` from IoT
---------------
``IoT = 10*log10((beta + N_0)/sigma^2)`` (L577) and ``N_0`` is defined nowhere in the
article.  ``[P] L207`` identifies ``N_0`` as thermal-noise power, giving
``beta = sigma^2 (10^(IoT/10) - 1)``.

But ``beta`` is the per-interferer power while the *per-antenna* interference power is
``beta * (Hbar Hbar^H)_mm ~ beta * r``.  Taken literally the formula would realise
~18.6 dB of interference at a nominal IoT of 10 dB with r = 8.  We therefore scale beta
so the realised per-antenna interference-to-thermal ratio equals IoT.  Both readings are
selectable via `params.M5_Noise.beta_convention`.
"""

from __future__ import annotations

import numpy as np


def beta_from_iot(iot_db: float, sigma2: float, Hbar: np.ndarray,
                  convention: str = "realised_per_antenna") -> float:
    """Interference power scale for the given IoT."""
    target = sigma2 * (10.0 ** (iot_db / 10.0) - 1.0)
    if convention == "literal_formula":
        return target
    if convention == "realised_per_antenna":
        M = Hbar.shape[0]
        # mean_m (Hbar Hbar^H)_mm  ==  ||Hbar||_F^2 / M
        mean_diag = float(np.vdot(Hbar, Hbar).real) / M
        if mean_diag <= 0:
            raise ValueError("degenerate Hbar")
        return target / mean_diag
    raise ValueError(f"unknown beta convention {convention!r}")


def noise_covariance(Hbar: np.ndarray, beta: float, sigma2: float) -> np.ndarray:
    """R = beta * Hbar Hbar^H + sigma^2 I."""
    M = Hbar.shape[0]
    return beta * (Hbar @ Hbar.conj().T) + sigma2 * np.eye(M)


def cholesky_factor(R: np.ndarray) -> np.ndarray:
    """Lower-triangular L with L L^H = R (R is positive definite thanks to sigma^2 I)."""
    return np.linalg.cholesky(R)


def draw_noise(L: np.ndarray, n_draws: int, rng: np.random.Generator) -> np.ndarray:
    """M x n_draws draws from CN(0, L L^H)."""
    M = L.shape[0]
    w = (rng.standard_normal((M, n_draws))
         + 1j * rng.standard_normal((M, n_draws))) / np.sqrt(2)
    return L @ w


def scaled_sample_matrix(noise_samples: np.ndarray) -> np.ndarray:
    """N = (1/sqrt(N)) [n^1 ... n^N] (Eq. 32), so that N N^H == R_hat exactly."""
    N = noise_samples.shape[1]
    return noise_samples / np.sqrt(N)


# --------------------------------------------------------------------------------------
# M6 - covariance estimation
# --------------------------------------------------------------------------------------


def sample_covariance(S: np.ndarray) -> np.ndarray:
    """R_hat = S S^H for the scaled sample matrix S (equivalently Eq. 6)."""
    return S @ S.conj().T


def load_diagonal(A: np.ndarray, epsilon: float) -> np.ndarray:
    """Diagonal loading A -> A + epsilon*(tr A / dim)*I (Conditioner mode 'fixed').

    *** epsilon is NOT from the article - see params.M6_Covariance.fixed_epsilon. ***
    epsilon = 0 returns A untouched.
    """
    if epsilon == 0.0:
        return A
    d = A.shape[0]
    lam = epsilon * float(np.trace(A).real) / d
    return A + lam * np.eye(d)


# --------------------------------------------------------------------------------------
# M6 - conditioning of the sample covariance
# --------------------------------------------------------------------------------------
#
# Eq. (3) needs R^-1, footnote 5 (L822) directs that R_hat be used as R, and
# rank(R_hat) <= N = 192 < 256 = M.  So *some* conditioning is forced by the article's own
# equations - see simulation_parameters.md, 2A.6.  Which one is not stated.
#
# The default is Ledoit-Wolf: its shrinkage intensity is computed from the samples, so it
# adds no free parameter.  Fixed diagonal loading is available for sweeps but is not
# adopted: `eps * tr(A)/dim` scales with the LARGEST eigenvalues, so on an anisotropic
# covariance (r large interference eigenvalues over a sigma^2 floor) it swamps exactly
# the directions LMMSE needs.  At IoT = 20 dB the loading is 10x the noise floor and
# centralized LMMSE loses its optimality.


def ledoit_wolf_rho(S: np.ndarray) -> float:
    """Optimal shrinkage intensity toward mu*I (Ledoit & Wolf, 2004).

    `S` is the scaled sample matrix (`S S^H == R_hat`), so the underlying samples are
    ``n_i = sqrt(N) * S[:, i]``.  Uses the closed form

        sum_i ||n_i n_i^H - R||_F^2  ==  sum_i ||n_i||^4 - N ||R||_F^2

    which makes the estimate O(MN) rather than O(N M^2).
    """
    M, N = S.shape
    R = S @ S.conj().T
    mu = float(np.trace(R).real) / M
    d2 = float(np.linalg.norm(R - mu * np.eye(M), "fro") ** 2) / M
    if d2 <= 0:
        return 1.0
    norms_sq = (np.abs(S) ** 2).sum(axis=0) * N          # ||n_i||^2
    b2 = float((norms_sq ** 2).sum() - N * np.linalg.norm(R, "fro") ** 2) / (N ** 2) / M
    return float(min(max(min(b2, d2) / d2, 0.0), 1.0))


def shrink(A: np.ndarray, rho: float) -> np.ndarray:
    """(1 - rho) * A + rho * (tr A / dim) * I."""
    if rho <= 0.0:
        return A
    d = A.shape[0]
    mu = float(np.trace(A).real) / d
    return (1.0 - rho) * A + rho * mu * np.eye(d)


class Conditioner:
    """How a sample covariance is made invertible before it is inverted.

    mode='ledoit_wolf'  intensity computed per covariance from its own samples; no knob.
    mode='fixed'        diagonal loading A -> A + eps*(tr A/dim)*I  (not adopted; see above).
    mode='none'         raw R_hat; pinv is used where it is singular.
    """

    def __init__(self, mode: str = "ledoit_wolf", epsilon: float = 0.0):
        if mode not in ("ledoit_wolf", "fixed", "none"):
            raise ValueError(f"unknown conditioner mode {mode!r}")
        self.mode = mode
        self.epsilon = epsilon
        self._fallback_rho = 0.0     # used when a block has too few columns for LW

    def prime(self, S: np.ndarray) -> None:
        """Record a fallback intensity from the full sample matrix (for the LRD path)."""
        if self.mode == "ledoit_wolf":
            self._fallback_rho = ledoit_wolf_rho(S)

    def covariance(self, S_block: np.ndarray) -> np.ndarray:
        """Conditioned covariance for a block of the scaled sample matrix."""
        R = S_block @ S_block.conj().T
        if self.mode == "none":
            return R
        if self.mode == "fixed":
            return load_diagonal(R, self.epsilon)
        rho = (ledoit_wolf_rho(S_block) if S_block.shape[1] >= S_block.shape[0]
               else self._fallback_rho)
        return shrink(R, rho)

    def condition(self, A: np.ndarray) -> np.ndarray:
        """Condition an already-formed covariance (used where samples are unavailable)."""
        if self.mode == "none":
            return A
        if self.mode == "fixed":
            return load_diagonal(A, self.epsilon)
        return shrink(A, self._fallback_rho)

    def solve(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Solve A X = B, conditioning A first; pinv only where A can be singular."""
        Ac = self.condition(A) if self.mode != "none" else A
        if self.mode == "none" and Ac.shape[0] > np.linalg.matrix_rank(Ac):
            return np.linalg.pinv(Ac) @ B
        return np.linalg.solve(Ac, B)

    def __repr__(self) -> str:
        extra = f", eps={self.epsilon}" if self.mode == "fixed" else ""
        return f"Conditioner({self.mode}{extra})"
