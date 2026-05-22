"""Constellation generation and symbol drawing."""

import numpy as np


def get_constellation(mod: str):
    """Return normalised constellation vector and bits-per-symbol.

    Parameters
    ----------
    mod : str
        '16QAM' or 'QPSK'.

    Returns
    -------
    const : np.ndarray, shape (Mc,)
        Normalised constellation points.
    bpS : int
        Bits per symbol.
    """
    mod = mod.upper()
    if mod == '16QAM':
        a = np.array([-3, -1, 1, 3], dtype=float)
        I, Q = np.meshgrid(a, a)
        const = (I + 1j * Q).ravel()
        const = const / np.sqrt(np.mean(np.abs(const) ** 2))
        return const, 4
    elif mod == 'QPSK':
        const = (1 / np.sqrt(2)) * np.array([1+1j, 1-1j, -1+1j, -1-1j])
        return const, 2
    else:
        raise ValueError(f"Unknown modulation: {mod}")


def draw_symbols(const: np.ndarray, K: int, Ns: int) -> np.ndarray:
    """Draw K × Ns i.i.d. symbols uniformly from constellation.

    Parameters
    ----------
    const : np.ndarray, shape (Mc,)
    K : int
        Number of rows (users).
    Ns : int
        Number of columns (symbols).

    Returns
    -------
    S : np.ndarray, shape (K, Ns)
    """
    idx = np.random.randint(0, len(const), size=(K, Ns))
    return const[idx]
