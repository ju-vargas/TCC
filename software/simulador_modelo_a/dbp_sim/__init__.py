"""Decentralized LMMSE equalization simulator - Figure 8 of Zhao et al., IEEE JSAC 2025.

Modules mirror the data flow of the target article:

    M1  driver        Monte-Carlo loop over realizations and SNR points
    M2  channel       H (M x K) and Hbar (M x r)
    M3  clustering    partition of the M antennas into C clusters
    M4  source        transmitted symbols
    M5  noise         colored noise and the N estimation samples
    M6  covariance    R_hat and its conditioning
    M7  equalizers    the six curves of Figure 8
    M8  metric        slicing and SER

All constants live in `params.py`, each tagged with its provenance.
"""

from .params import FIGURE8_PANELS, Panel, provenance_table

__all__ = ["FIGURE8_PANELS", "Panel", "provenance_table"]
