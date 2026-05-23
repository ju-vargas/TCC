"""Monte Carlo SER vs SNR sweep."""

import numpy as np
from config import SimConfig
from constellation import get_constellation, draw_symbols
from channel import generate_channel_rayleigh, generate_channel_from_mat
from utils import partition_clusters, cluster_indices, compute_local_cov, apply_equalizer, detect, count_errors
from equalizers import (lmmse_centralised, zf_centralised, bdac_mmse,
                        sdr_mmse, cdr_mmse, bcd_mmse_update,
                        lrd_algorithm, bcd_mmse_lrd_update)


def get_algorithm_set(fig_select: str) -> list:
    """Return algorithm names for each paper figure."""
    if fig_select == 'fig6':
        return ['LMMSE', 'ZF', 'MMSE_AWGN', 'BDAC',
                'BCD1', 'BCD2', 'BCD3', 'BCD4']
    elif fig_select == 'fig7':
        return ['LMMSE', 'ZF', 'BDAC',
                'LRD1', 'LRD2', 'LRD3', 'LRD4']
    else:
        return ['LMMSE', 'ZF', 'BCD1', 'LRD4', 'sDR', 'cDR']


def run_ser_sweep(cfg: SimConfig, fig_select: str) -> dict:
    """Run the Monte Carlo SER simulation.

    Parameters
    ----------
    cfg : SimConfig
    fig_select : str

    Returns
    -------
    SER : dict mapping algorithm name → np.ndarray of SER values
    """
    const, bpS = get_constellation(cfg.mod)
    algs = get_algorithm_set(fig_select)
    nSNR = len(cfg.SNR_dB)

    # Flags
    has = set(algs)
    run_LMMSE = 'LMMSE' in has
    run_ZF = 'ZF' in has
    run_AWGN = 'MMSE_AWGN' in has
    run_BDAC = 'BDAC' in has
    run_BCD = any(f'BCD{i}' in has for i in range(1, 5))
    run_LRD = any(f'LRD{i}' in has for i in range(1, 5))
    run_sDR = 'sDR' in has
    run_cDR = 'cDR' in has
    need_bdac = run_BDAC or run_BCD or run_LRD

    # Counters
    err = {a: np.zeros(nSNR) for a in algs}
    total = {a: np.zeros(nSNR) for a in algs}

    print(f"=== Simulation: {fig_select} | M={cfg.M} C={cfg.C} K={cfg.K} "
          f"r={cfg.r} IoT={cfg.IoT_dB}dB mod={cfg.mod} ===")
    print(f"    N_mc={cfg.N_mc}, N_sym={cfg.N_sym}, N_samples={cfg.N_samples}"
          f", cluster_mode={cfg.cluster_mode}")
    print(f"    Algorithms: {algs}")
    print("Progress: ", end='', flush=True)

    for mc in range(cfg.N_mc):
        if (mc + 1) % 10 == 0:
            print(f"{mc+1}/{cfg.N_mc} ", end='', flush=True)

        # --- Channel generation ---
        if cfg.channel_mode == 'rayleigh':
            H_tgt, H_itf = generate_channel_rayleigh(cfg)
        else:
            H_tgt, H_itf = generate_channel_from_mat(cfg.mat_file, mc, cfg)

        for isnr in range(nSNR):
            SNR_lin = 10 ** (cfg.SNR_dB[isnr] / 10)
            # The figure x-axis is Eb/N0, so sigma2 = Es / (SNR_lin * bpS)
            sigma2 = cfg.Es / (SNR_lin * bpS)
            IoT_lin = 10 ** (cfg.IoT_dB / 10)

            # Interference scaling must be divided by r to match the ZF performance
            beta = (IoT_lin - 1) * sigma2 / cfg.r

            # True covariance and Cholesky factor
            R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
            R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
            Lc = np.linalg.cholesky(R_reg)  # lower triangular

            # N noise samples for covariance estimation (Gaussian, Eq. 6)
            z = (np.random.randn(cfg.M, cfg.N_samples)
                 + 1j * np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
            N_mat = Lc @ z

            # Partition into clusters
            Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)

            # Local diagonal covariance blocks (with optional diagonal loading)
            if cfg.ideal_covariance:
                from utils import inv_stable
                Rcc = []
                Rcc_inv = []
                for c in range(cfg.C):
                    idx = cluster_indices(c, cfg)
                    R_block = R_true[np.ix_(idx, idx)]
                    Rcc.append(R_block)
                    Rcc_inv.append(inv_stable(R_block))
            else:
                Rcc, Rcc_inv = compute_local_cov(Nc, cfg, sigma2)

            # Symbol block
            S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
            z_rx = (np.random.randn(cfg.M, cfg.N_sym)
                    + 1j * np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
            noise_rx = Lc @ z_rx
            Y_rx = H_tgt @ S_tx + noise_rx

            # Partition received signal
            Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]

            # Estimated covariance for centralised methods
            R_est = (N_mat @ N_mat.conj().T) / cfg.N_samples

            # ----- Equalizers -----
            if run_LMMSE:
                W = lmmse_centralised(H_tgt, R_true, cfg.Es)
                S_det = detect(W @ Y_rx, const)
                e, t = count_errors(S_det, S_tx)
                err['LMMSE'][isnr] += e
                total['LMMSE'][isnr] += t

            if run_ZF:
                W = zf_centralised(H_tgt)
                S_det = detect(W @ Y_rx, const)
                e, t = count_errors(S_det, S_tx)
                err['ZF'][isnr] += e
                total['ZF'][isnr] += t

            if run_AWGN:
                W = lmmse_centralised(H_tgt, sigma2 * np.eye(cfg.M), cfg.Es)
                S_det = detect(W @ Y_rx, const)
                e, t = count_errors(S_det, S_tx)
                err['MMSE_AWGN'][isnr] += e
                total['MMSE_AWGN'][isnr] += t

            # BDAC-MMSE
            if need_bdac:
                W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)

            if run_BDAC:
                S_det = detect(apply_equalizer(W_bdac, Yc, cfg), const)
                e, t = count_errors(S_det, S_tx)
                err['BDAC'][isnr] += e
                total['BDAC'][isnr] += t

            # BCD-MMSE iterations
            if run_BCD:
                W_bcd = list(W_bdac)
                for it in range(1, 5):
                    W_bcd = bcd_mmse_update(W_bcd, Hc, Nc, Rcc, cfg)
                    tag = f'BCD{it}'
                    if tag in has:
                        S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
                        e, t = count_errors(S_det, S_tx)
                        err[tag][isnr] += e
                        total[tag][isnr] += t

            # BCD-MMSE (LRD) iterations
            if run_LRD:
                if cfg.ideal_covariance:
                    G = np.sqrt(beta) * H_itf
                else:
                    G = lrd_algorithm(Nc, cfg.r, cfg)
                Gc = [G[cluster_indices(c, cfg), :] for c in range(cfg.C)]
                W_lrd = list(W_bdac)
                for it in range(1, 5):
                    W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
                    tag = f'LRD{it}'
                    if tag in has:
                        S_det = detect(apply_equalizer(W_lrd, Yc, cfg), const)
                        e, t = count_errors(S_det, S_tx)
                        err[tag][isnr] += e
                        total[tag][isnr] += t

            if run_sDR:
                S_hat = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg, R_true)
                S_det = detect(S_hat, const)
                e, t = count_errors(S_det, S_tx)
                err['sDR'][isnr] += e
                total['sDR'][isnr] += t

            if run_cDR:
                S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg, R_true)
                S_det = detect(S_hat, const)
                e, t = count_errors(S_det, S_tx)
                err['cDR'][isnr] += e
                total['cDR'][isnr] += t

    print("\nDone.")

    # Compute SER
    SER = {}
    for a in algs:
        SER[a] = err[a] / np.maximum(total[a], 1)

    return SER
