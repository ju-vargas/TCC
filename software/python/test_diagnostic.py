"""Diagnostic: test all 4 sigma2/beta combinations against the paper's Figure 8a benchmarks.

Paper Figure 8(a) benchmarks:
  LMMSE: SER between 10^-4 and 10^-3 at SNR ≈ 0 dB
  LRD4:  SER < 10^-4 near SNR ≈ 1-2 dB
  BCD1:  SER ~ 2×10^-4 near SNR ≈ 2 dB
  cDR:   SER ~ 2×10^-4 near SNR ≈ 2 dB
  sDR:   SER ≈ 10^-4 at SNR ≈ 5-6 dB
  ZF:    SER ~ 10^-3 at SNR = 10 dB, never reaches 10^-4
"""
import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import (lmmse_centralised, zf_centralised, bdac_mmse,
                        bcd_mmse_update, lrd_algorithm, bcd_mmse_lrd_update,
                        sdr_mmse, cdr_mmse)
from utils import (partition_clusters, cluster_indices, compute_local_cov,
                   apply_equalizer, detect, count_errors)

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480,
                IoT_dB=10.0, mod='16QAM', cluster_mode='contiguous')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10 ** (cfg.IoT_dB / 10)

N_mc = 50  # quick test
SNR_dB_range = np.array([-2, 0, 2, 4, 6, 8, 10], dtype=float)

combos = {
    'A: Es/SNR, beta*(no/r)':    dict(use_bps=False, use_r=False),
    'B: Es/SNR, beta/r':         dict(use_bps=False, use_r=True),
    'C: Es/(SNR*bpS), beta*(no/r)': dict(use_bps=True, use_r=False),
    'D: Es/(SNR*bpS), beta/r':   dict(use_bps=True, use_r=True),
}

algs = ['LMMSE', 'ZF', 'BCD1', 'LRD4', 'cDR', 'sDR']

for label, opts in combos.items():
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    
    err = {a: np.zeros(len(SNR_dB_range)) for a in algs}
    tot = np.zeros(len(SNR_dB_range))
    
    for mc in range(N_mc):
        H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
        
        for isnr, snr_db in enumerate(SNR_dB_range):
            SNR_lin = 10 ** (snr_db / 10)
            
            if opts['use_bps']:
                sigma2 = cfg.Es / (SNR_lin * bpS)
            else:
                sigma2 = cfg.Es / SNR_lin
            
            if opts['use_r']:
                beta = (IoT_lin - 1) * sigma2 / cfg.r
            else:
                beta = (IoT_lin - 1) * sigma2
            
            R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
            R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
            Lc = np.linalg.cholesky(R_reg)
            
            z = (np.random.randn(cfg.M, cfg.N_samples)
                 + 1j * np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
            N_mat = Lc @ z
            Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
            Rcc, Rcc_inv = compute_local_cov(Nc, cfg, sigma2)
            
            S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
            z_rx = (np.random.randn(cfg.M, cfg.N_sym)
                    + 1j * np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
            Y_rx = H_tgt @ S_tx + Lc @ z_rx
            Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
            
            # LMMSE
            W = lmmse_centralised(H_tgt, R_true, cfg.Es)
            S_det = detect(W @ Y_rx, const)
            e, t = count_errors(S_det, S_tx)
            err['LMMSE'][isnr] += e; tot[isnr] += t
            
            # ZF
            W = zf_centralised(H_tgt)
            S_det = detect(W @ Y_rx, const)
            e, _ = count_errors(S_det, S_tx)
            err['ZF'][isnr] += e
            
            # BCD1
            W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)
            W_bcd = list(W_bdac)
            W_bcd = bcd_mmse_update(W_bcd, Hc, Nc, Rcc, cfg)
            S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
            e, _ = count_errors(S_det, S_tx)
            err['BCD1'][isnr] += e
            
            # LRD4
            G = lrd_algorithm(Nc, cfg.r, cfg)
            Gc = [G[cluster_indices(c, cfg), :] for c in range(cfg.C)]
            W_lrd = list(W_bdac)
            for it in range(4):
                W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
            S_det = detect(apply_equalizer(W_lrd, Yc, cfg), const)
            e, _ = count_errors(S_det, S_tx)
            err['LRD4'][isnr] += e
            
            # cDR
            S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
            S_det = detect(S_hat, const)
            e, _ = count_errors(S_det, S_tx)
            err['cDR'][isnr] += e
            
            # sDR
            S_hat = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
            S_det = detect(S_hat, const)
            e, _ = count_errors(S_det, S_tx)
            err['sDR'][isnr] += e
    
    print(f"  {'SNR':>5s}  {'LMMSE':>10s}  {'ZF':>10s}  {'BCD1':>10s}  {'LRD4':>10s}  {'cDR':>10s}  {'sDR':>10s}")
    for i, snr in enumerate(SNR_dB_range):
        vals = {a: err[a][i] / max(tot[i], 1) for a in algs}
        print(f"  {snr:+5.1f}  {vals['LMMSE']:10.6f}  {vals['ZF']:10.6f}  {vals['BCD1']:10.6f}  {vals['LRD4']:10.6f}  {vals['cDR']:10.6f}  {vals['sDR']:10.6f}")
    
    # Report approximate 10^-4 crossings and key checks
    print("\n  Paper benchmarks check:")
    for a in algs:
        ser = np.array([err[a][i] / max(tot[i], 1) for i in range(len(SNR_dB_range))])
        for i in range(len(SNR_dB_range)-1):
            if ser[i] > 1e-4 and ser[i+1] <= 1e-4:
                if ser[i+1] > 0:
                    frac = (np.log10(ser[i]) - (-4)) / (np.log10(ser[i]) - np.log10(ser[i+1]))
                    snr_cross = SNR_dB_range[i] + frac * (SNR_dB_range[i+1] - SNR_dB_range[i])
                else:
                    snr_cross = SNR_dB_range[i+1]
                print(f"    {a:>6s} crosses 10^-4 at ~{snr_cross:+.1f} dB")
                break
        else:
            if ser[-1] > 1e-4:
                print(f"    {a:>6s}: does NOT reach 10^-4 in range")
    
    # Key paper checks
    lmmse_at_0 = err['LMMSE'][list(SNR_dB_range).index(0)] / max(tot[list(SNR_dB_range).index(0)], 1)
    zf_at_10 = err['ZF'][list(SNR_dB_range).index(10)] / max(tot[list(SNR_dB_range).index(10)], 1)
    print(f"    LMMSE at SNR=0 dB: {lmmse_at_0:.6f}  (paper: between 10^-4 and 10^-3)")
    print(f"    ZF at SNR=10 dB:   {zf_at_10:.6f}  (paper: ~10^-3)")
