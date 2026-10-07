"""M1 - Monte-Carlo driver.

Structure per the article (L577): 100 channel realizations, 480 symbols each, swept over
the SNR grid.  For every realization the driver

  1. draws H, Hbar                                       (M2)
  2. partitions the antennas                             (M3)
  3. for each SNR point: sets sigma^2, derives beta       (M5)
  4. draws the N = 192 estimation samples and forms R_hat (M5, M6)
  5. builds every equalizer once                          (M7)
  6. draws 480 symbols and an independent noise block, measures SER (M4, M8)

Step 5 happens once per (realization, SNR) and is reused across the 480 symbols, which
is what makes the equalization-matrix framing of the article meaningful (L61, L561).

The noise for step 6 is drawn independently of the estimation samples in step 4 - the
physically honest reading.  It is also the reading that requires R_hat to be
conditioned: with an unregularised R_hat at N = 192 the curve ordering inverts.  See
params.M5_Noise.data_noise_independent and params.M6_Covariance.shrinkage.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import hw_inverse, m2_channel, m3_clustering, m4_source, m5_noise, m7_equalizers, m8_metric
from .params import (M1_Driver, M2_Channel, M3_Clustering, M4_Source, M5_Noise,
                     M6_Covariance, M7_Equalizers, M8_Metric, Panel)


@dataclass(frozen=True)
class SimConfig:
    """Plain values, resolved from the provenance-tagged parameters."""

    M: int
    C: int
    K: int
    r: int
    iot_db: float
    modulation: str

    n_realizations: int = M1_Driver.n_realizations.value
    n_symbols: int = M1_Driver.n_symbols.value
    snr_db_grid: tuple = M1_Driver.snr_db_grid.value
    seed: int = M1_Driver.rng_seed.value

    n_noise_samples: int = M5_Noise.n_noise_samples.value
    beta_convention: str = M5_Noise.beta_convention.value
    data_noise_independent: bool = M5_Noise.data_noise_independent.value

    shrinkage: str = M6_Covariance.shrinkage.value
    fixed_epsilon: float = M6_Covariance.fixed_epsilon.value
    Es: float = M4_Source.Es.value
    mapping: str = M3_Clustering.mapping.value
    remove_bias: bool = M8_Metric.bias_removal.value

    bcd_iterations: int = M7_Equalizers.bcd_iterations.value
    #: Iteration-study mode: when non-empty, only LMMSE, ZF and one BCD-MMSE curve per
    #: iteration count are computed (e.g. (1, 2, 3, 4)). Empty = the six Figure 8 curves.
    bcd_iteration_list: tuple = ()
    lrd_iterations: int = M7_Equalizers.lrd_iterations.value
    lrd_rank: int = M7_Equalizers.lrd_rank.value
    #: M_c x M_c inversion of the BCD-MMSE update: 'float' or 'cholesky_hw'.
    bcd_inverse: str = M7_Equalizers.bcd_inverse.value
    #: Fixed-point format of 'cholesky_hw' (int bits include the sign). None = twice.
    hw_int_bits: int = M7_Equalizers.hw_int_bits.value
    hw_frac_bits: int = M7_Equalizers.hw_frac_bits.value
    hw_acc_int_bits: int | None = M7_Equalizers.hw_acc_int_bits.value
    hw_acc_frac_bits: int | None = M7_Equalizers.hw_acc_frac_bits.value
    #: ap_fixed modes of 'cholesky_hw'. None = same as the data type.
    hw_quant: str = M7_Equalizers.hw_quant.value
    hw_overflow: str = M7_Equalizers.hw_overflow.value
    hw_acc_quant: str | None = M7_Equalizers.hw_acc_quant.value
    hw_acc_overflow: str | None = M7_Equalizers.hw_acc_overflow.value
    #: Intermediate types, as (name, (int_bits, frac_bits, quant, overflow)) pairs.
    hw_intermediates: tuple = M7_Equalizers.hw_intermediates.value

    channel_backend: str = M2_Channel.backend.value
    normalization: str = M2_Channel.normalization.value
    channel_kwargs: dict = field(default_factory=dict)

    @classmethod
    def from_panel(cls, panel: Panel, **overrides) -> "SimConfig":
        base = dict(M=panel.M, C=panel.C, K=panel.K, r=panel.r,
                    iot_db=panel.iot_db, modulation=panel.modulation)
        base.update(overrides)
        return cls(**base)


#: The six curves of Figure 8, in the article's own legend order.
FIGURE8_CURVES = M7_Equalizers.curves.value


def bcd_curve_name(n_iter: int) -> str:
    return f"BCD-MMSE (iter {n_iter})"


def curve_names(cfg: SimConfig) -> tuple[str, ...]:
    """The curves `run_panel` computes for this configuration, in legend order."""
    if not cfg.bcd_iteration_list:
        return FIGURE8_CURVES
    return ("LMMSE", "ZF") + tuple(bcd_curve_name(n) for n in cfg.bcd_iteration_list)


def build_equalizers(cfg: SimConfig, H, S, cond, clusters) -> dict[str, np.ndarray]:
    """Every equalizer of `curve_names(cfg)` for one (realization, SNR) point."""
    eq: dict[str, np.ndarray] = {}
    eq["LMMSE"] = m7_equalizers.lmmse(H, S, cfg.Es, cond)
    eq["ZF"] = m7_equalizers.zero_forcing(H)
    inverse = hw_inverse.make_inverter(cfg.bcd_inverse, cfg.hw_int_bits, cfg.hw_frac_bits,
                                       cfg.hw_acc_int_bits, cfg.hw_acc_frac_bits,
                                       cfg.hw_quant, cfg.hw_overflow,
                                       cfg.hw_acc_quant, cfg.hw_acc_overflow,
                                       cfg.hw_intermediates)

    if cfg.bcd_iteration_list:
        W0 = m7_equalizers.bdac_mmse(H, S, clusters, cfg.Es, cond)
        path = m7_equalizers.bcd_mmse_path(
            H, S, clusters, cfg.Es, max(cfg.bcd_iteration_list), cond, W0=W0,
            inverse=inverse)
        for n in cfg.bcd_iteration_list:
            eq[bcd_curve_name(n)] = path[n - 1]
        return eq

    eq["sDR-MMSE"] = m7_equalizers.sdr_mmse(H, S, clusters, cfg.Es, cond)
    eq["cDR-MMSE"] = m7_equalizers.cdr_mmse(H, S, clusters, cfg.Es, cond)

    W0 = m7_equalizers.bdac_mmse(H, S, clusters, cfg.Es, cond)
    eq["BCD-MMSE (iter 1)"] = m7_equalizers.bcd_mmse(
        H, S, clusters, cfg.Es, cfg.bcd_iterations, cond, W0=W0, inverse=inverse)

    G = m7_equalizers.lrd_decomposition(S, clusters, cfg.lrd_rank)
    eq["BCD-MMSE LRD (iter 4)"] = m7_equalizers.bcd_mmse(
        H, G, clusters, cfg.Es, cfg.lrd_iterations, cond, W0=W0, S_full=S,
        inverse=inverse)
    return eq


def run_panel(cfg: SimConfig, progress: bool = False) -> dict[str, np.ndarray]:
    """SER for every curve over the SNR grid. Returns {curve: array over snr_db_grid}."""
    rng = np.random.default_rng(cfg.seed)
    backend = m2_channel.make_backend(
        cfg.channel_backend,
        path=M2_Channel.quadriga_export_path.value,
        spread_deg=M2_Channel.standin_angular_spread_deg.value,
        n_paths=M2_Channel.standin_paths_per_ue.value,
        sector_deg=M2_Channel.sector_deg.value,
        radius_min_m=M2_Channel.radius_min_m.value,
        radius_max_m=M2_Channel.radius_max_m.value,
        normalization=cfg.normalization,
        **cfg.channel_kwargs)

    clusters = m3_clustering.cluster_indices(cfg.M, cfg.C, cfg.mapping)
    alphabet = m4_source.constellation(cfg.modulation)
    snr_grid = np.asarray(cfg.snr_db_grid, dtype=float)

    curves = curve_names(cfg)
    errors = {name: np.zeros(snr_grid.size) for name in curves}
    counts = np.zeros(snr_grid.size)

    for real_idx in range(cfg.n_realizations):
        H, Hbar = backend.generate(cfg.M, cfg.K, cfg.r, real_idx, rng)

        # beta is proportional to sigma^2, so R_true = sigma^2 * (SNR-independent
        # shape).  Factor the shape once per realization and rescale per SNR point
        # instead of repeating an M x M Cholesky 11 times.
        beta_unit = m5_noise.beta_from_iot(cfg.iot_db, 1.0, Hbar, cfg.beta_convention)
        L_shape = m5_noise.cholesky_factor(
            m5_noise.noise_covariance(Hbar, beta_unit, 1.0))

        for k, snr_db in enumerate(snr_grid):
            sigma2 = cfg.Es * 10.0 ** (-snr_db / 10.0)
            L = np.sqrt(sigma2) * L_shape

            noise_samples = m5_noise.draw_noise(L, cfg.n_noise_samples, rng)
            S = m5_noise.scaled_sample_matrix(noise_samples)

            cond = m5_noise.Conditioner(cfg.shrinkage, cfg.fixed_epsilon)
            cond.prime(S)                     # fallback intensity for the LRD path
            eqs = build_equalizers(cfg, H, S, cond, clusters)

            s = m4_source.draw_symbols(alphabet, cfg.K, cfg.n_symbols, rng)
            if cfg.data_noise_independent:
                n = m5_noise.draw_noise(L, cfg.n_symbols, rng)
            else:
                # Data noise consistent with R_hat: no covariance-estimation error.
                Lhat = np.linalg.cholesky(
                    m5_noise.shrink(S @ S.conj().T, max(cond._fallback_rho, 1e-9)))
                n = m5_noise.draw_noise(Lhat, cfg.n_symbols, rng)
            y = H @ s + n

            for name, W in eqs.items():
                errors[name][k] += m8_metric.symbol_error_rate(
                    W @ y, s, alphabet, cfg.remove_bias)
            counts[k] += 1

        if progress and (real_idx + 1) % 10 == 0:
            print(f"    realization {real_idx + 1}/{cfg.n_realizations}", flush=True)

    return {name: errors[name] / counts for name in curves}
