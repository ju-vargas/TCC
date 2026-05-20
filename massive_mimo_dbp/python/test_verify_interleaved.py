"""Verification: run with interleaved clustering using the updated code."""
import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import (lmmse_centralised, zf_centralised, sdr_mmse, cdr_mmse,
                        bdac_mmse, bcd_mmse_update, lrd_algorithm, bcd_mmse_lrd_update)
from utils import partition_clusters, cluster_indices, compute_local_cov, apply_equalizer, detect, count_errors

# Config with interleaved clustering (new default)
cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, 
                mod='16QAM', cluster_mode='interleaved')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB / 10)
N_mc = 50

print(f"Cluster mode: {cfg.cluster_mode}")
print(f"Mc={cfg.Mc}, C={cfg.C}, M={cfg.M}")

# Verify cluster indices
for c in range(3):
    idx = cluster_indices(c, cfg)
    print(f"  Cluster {c} indices (first 5): {idx[:5]}")

SNR_dB_range = np.arange(-10, 12, 2, dtype=float)
algs = ['LMMSE', 'ZF', 'BCD1', 'LRD4', 'sDR', 'cDR']
err = {a: np.zeros(len(SNR_dB_range)) for a in algs}
tot = {a: np.zeros(len(SNR_dB_range)) for a in algs}

for isnr, snr_db in enumerate(SNR_dB_range):
    SNR_lin = 10**(snr_db / 10)
    sigma2 = cfg.Es / (SNR_lin * bpS)
    beta = (IoT_lin - 1) * sigma2 / cfg.r
    
    for mc in range(N_mc):
        H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
        R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
        R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
        Lc_ = np.linalg.cholesky(R_reg)
        
        z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
        N_mat = Lc_ @ z
        
        Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
        Rcc, Rcc_inv = compute_local_cov(Nc, cfg)
        
        S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
        Y_rx = H_tgt @ S_tx + Lc_ @ (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
        Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
        
        # LMMSE
        W = lmmse_centralised(H_tgt, R_true, cfg.Es)
        S_det = detect(W @ Y_rx, const)
        e, t = count_errors(S_det, S_tx)
        err['LMMSE'][isnr] += e; tot['LMMSE'][isnr] += t
        
        # ZF
        W = zf_centralised(H_tgt)
        S_det = detect(W @ Y_rx, const)
        e, t = count_errors(S_det, S_tx)
        err['ZF'][isnr] += e; tot['ZF'][isnr] += t
        
        # BCD1
        W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)
        W_bcd = bcd_mmse_update(list(W_bdac), Hc, Nc, cfg)
        S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
        e, _ = count_errors(S_det, S_tx); err['BCD1'][isnr] += e; tot['BCD1'][isnr] += t
        
        # LRD4
        G = lrd_algorithm(Nc, cfg.r, cfg)
        Gc = [G[cluster_indices(c, cfg), :] for c in range(cfg.C)]
        W_lrd = list(W_bdac)
        for it in range(4):
            W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
        S_det = detect(apply_equalizer(W_lrd, Yc, cfg), const)
        e, _ = count_errors(S_det, S_tx); err['LRD4'][isnr] += e; tot['LRD4'][isnr] += t
        
        # sDR
        S_hat = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
        S_det = detect(S_hat, const)
        e, _ = count_errors(S_det, S_tx); err['sDR'][isnr] += e; tot['sDR'][isnr] += t
        
        # cDR
        S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
        S_det = detect(S_hat, const)
        e, _ = count_errors(S_det, S_tx); err['cDR'][isnr] += e; tot['cDR'][isnr] += t

print(f"\n{'SNR':>6s}  {'LMMSE':>10s}  {'ZF':>10s}  {'BCD1':>10s}  {'LRD4':>10s}  {'sDR':>10s}  {'cDR':>10s}")
for i, snr in enumerate(SNR_dB_range):
    vals = {a: err[a][i] / max(tot[a][i], 1) for a in algs}
    print(f"{snr:+6.1f}  {vals['LMMSE']:10.6f}  {vals['ZF']:10.6f}  {vals['BCD1']:10.6f}  "
          f"{vals['LRD4']:10.6f}  {vals['sDR']:10.6f}  {vals['cDR']:10.6f}")

# Paper comparison summary
print("\n=== Paper Fig 8a comparison (SER ~ 10^-4 crossings) ===")
for a in algs:
    ser_arr = np.array([err[a][i] / max(tot[a][i], 1) for i in range(len(SNR_dB_range))])
    # Find approximate SNR where SER crosses 10^-4
    for i in range(len(SNR_dB_range)-1):
        if ser_arr[i] > 1e-4 and ser_arr[i+1] <= 1e-4:
            # Linear interpolation in log domain
            if ser_arr[i+1] > 0:
                frac = (np.log10(ser_arr[i]) - (-4)) / (np.log10(ser_arr[i]) - np.log10(ser_arr[i+1]))
                snr_cross = SNR_dB_range[i] + frac * 2
            else:
                snr_cross = SNR_dB_range[i+1]
            print(f"  {a:>6s}: SER=10^-4 at SNR ≈ {snr_cross:+.1f} dB")
            break
    else:
        if ser_arr[-1] > 1e-4:
            print(f"  {a:>6s}: did not reach 10^-4")
