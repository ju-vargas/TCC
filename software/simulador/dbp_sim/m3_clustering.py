"""M3 - Antenna clustering.

Partitions the M BS antennas into C clusters of equal size M_c = M/C (L577, L85).
The *mapping* from antenna index to cluster is not stated by the article; see
`params.M3_Clustering.mapping` for the evidence behind the contiguous default and for
the measured impact of the choice (1.07x to 1.43x in SER on the QuaDriGa channels).
"""

from __future__ import annotations

import numpy as np


def cluster_indices(M: int, C: int, mapping: str = "contiguous") -> list[np.ndarray]:
    """Return C arrays of antenna indices, one per cluster.

    contiguous   cluster c takes antennas [c*M_c, (c+1)*M_c)  -- matches [DBP] :305
    interleaved  cluster c takes antennas c, c+C, c+2C, ...
    """
    if M % C:
        raise ValueError(f"M={M} not divisible by C={C}; the article assumes equal clusters")
    a = np.arange(M)
    if mapping == "contiguous":
        Mc = M // C
        return [a[c * Mc:(c + 1) * Mc] for c in range(C)]
    if mapping == "interleaved":
        return [a[c::C] for c in range(C)]
    raise ValueError(f"unknown mapping {mapping!r}")
