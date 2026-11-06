"""M4 - Symbol source.

16-QAM throughout Figure 8 except panel (g), which uses QPSK (L577, L608).
Constellations are normalised to unit average energy so that Es = 1 (see
`params.M4_Source.Es`: this is a free normalization, not an assumption).
"""

from __future__ import annotations

import numpy as np


def constellation(modulation: str) -> np.ndarray:
    """Unit-average-energy constellation points."""
    if modulation == "16QAM":
        levels = np.array([-3.0, -1.0, 1.0, 3.0])
        pts = (levels[:, None] + 1j * levels[None, :]).ravel()
    elif modulation == "QPSK":
        pts = np.array([-1 - 1j, -1 + 1j, 1 - 1j, 1 + 1j], dtype=complex)
    else:
        raise ValueError(f"unknown modulation {modulation!r}")
    return pts / np.sqrt((np.abs(pts) ** 2).mean())


def draw_symbols(alphabet: np.ndarray, K: int, n_symbols: int,
                 rng: np.random.Generator) -> np.ndarray:
    """K x n_symbols matrix of i.i.d. symbols (L577)."""
    return alphabet[rng.integers(0, alphabet.size, (K, n_symbols))]
