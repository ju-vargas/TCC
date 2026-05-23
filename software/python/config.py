"""Simulation configuration for the Massive MIMO DBP simulator."""

from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class SimConfig:
    """Parameters matching Section VI-A of Zhao et al. (2025)."""
    M: int = 128            # BS antennas
    C: int = 8              # antenna clusters
    K: int = 8              # target UEs
    r: int = 8              # non-target (interfering) UEs — fixed at 8
    Mc: int = 0             # antennas per cluster (auto-computed)
    SNR_dB: np.ndarray = field(default_factory=lambda: np.arange(-10, 12, 2, dtype=float))
    N_samples: int = 192    # noise samples for covariance estimation
    N_sym: int = 480        # transmitted symbols per channel realisation
    N_mc: int = 100         # Monte Carlo channel realisations
    IoT_dB: float = 10.0    # interference-over-thermal [dB]
    T_bcd: int = 4          # max BCD iterations
    mod: str = '16QAM'      # modulation: '16QAM' or 'QPSK'
    Es: float = 1.0         # symbol energy (normalised)
    channel_mode: str = 'rayleigh'  # 'rayleigh' or 'mat_file'
    mat_file: str = ''      # path to .mat file (when channel_mode='mat_file')
    cluster_mode: str = 'contiguous'  # 'contiguous' or 'interleaved'
    diag_load_sigma2: float = 0.0     # diagonal loading multiplier for local covariance
    ideal_covariance: bool = False    # if true, bypasses N_samples and uses true local covariances

    def __post_init__(self):
        self.Mc = self.M // self.C
        if isinstance(self.SNR_dB, list):
            self.SNR_dB = np.array(self.SNR_dB, dtype=float)


def make_config(fig_select: str, **overrides) -> SimConfig:
    """Create a SimConfig for a specific paper figure."""
    cfg = SimConfig()

    scenarios = {
        'fig6':  dict(M=128, C=8,  K=8),
        'fig7':  dict(M=128, C=8,  K=8),
        'fig8a': dict(M=128, C=8,  K=8),
        'fig8b': dict(M=256, C=8,  K=8),
        'fig8c': dict(M=256, C=16, K=8),
        'fig8e': dict(M=128, C=8,  K=12),
        'fig8f': dict(M=128, C=8,  K=8, IoT_dB=20.0),
        'fig8g': dict(M=128, C=8,  K=8, mod='QPSK'),
    }

    if fig_select not in scenarios:
        raise ValueError(f"Unknown fig_select: {fig_select}")

    params = scenarios[fig_select]
    params.update(overrides)

    for k, v in params.items():
        setattr(cfg, k, v)

    cfg.Mc = cfg.M // cfg.C
    return cfg
