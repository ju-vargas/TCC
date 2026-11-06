"""M8 - Detection and metric.

The article slices each entry of s_hat to the nearest constellation point (L79) and
reports symbol error rate (L581).  Whether any scaling or bias removal happens first is
not stated - see params.M8_Metric.bias_removal (spec item 2B.11); the default here is
"no", matching the article's wording literally.
"""

from __future__ import annotations

import numpy as np


def slice_to_constellation(estimates: np.ndarray, alphabet: np.ndarray) -> np.ndarray:
    """Nearest-neighbour quantisation (L79)."""
    return alphabet[np.abs(estimates[..., None] - alphabet).argmin(-1)]


def symbol_error_rate(estimates: np.ndarray, transmitted: np.ndarray,
                      alphabet: np.ndarray, remove_bias: bool = False) -> float:
    """SER over all users and symbols.

    remove_bias
        Divide each user's estimate by its own effective gain before slicing.  NOT
        specified by the article; off by default.
    """
    if remove_bias:
        gain = (estimates * transmitted.conj()).mean(axis=1, keepdims=True)
        gain = np.where(np.abs(gain) < 1e-12, 1.0, gain)
        estimates = estimates / gain
    return float((slice_to_constellation(estimates, alphabet) != transmitted).mean())
