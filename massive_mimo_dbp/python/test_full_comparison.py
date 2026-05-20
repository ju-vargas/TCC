"""Full comparison: mat channels vs rayleigh, with bpS (current code definition)."""
import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat, generate_channel_rayleigh
from constellation import get_constellation, draw_symbols
from equalizers import (lmmse_centralised, zf_centralised, sdr_mmse, cdr_mmse, 
                        bdac_mmse, bcd_mmse_update, lrd_algorithm, bcd_mmse_lrd_update)
from utils import partition_clusters, compute_local_cov, apply_equalizer, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB / 10)
N_mc = 50

def run_sweep(channel_type, snr_range, n_mc):
    results = {}
    algs = ['LMMSE', 'BCD1', 'LRD4', 'sDR', 'cDR']
    for a in algs:
        results[a] = []
    
    for snr_db in snr_range:
        SNR_lin = 10**(snr_db / 10)
        sigma2 = cfg.Es / (SNR_lin * bpS)
        beta = (IoT_lin - 1) * sigma2 / cfg.r
        
        err = {a: 0 for a in algs}
        tot = 0
        
        for mc in range(n_mc):
            if channel_type == 'mat':
                H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
            else:
                H_tgt, H_itf = generate_channel_rayleigh(cfg)
            
            R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
            R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
            Lc = np.linalg.cholesky(R_reg)
            
            z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
            N_mat = Lc @ z
            Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
            Rcc, Rcc_inv = compute_local_cov(Nc, cfg)
            
            S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
            z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
            Y_rx = H_tgt @ S_tx + Lc @ z_rx
            Yc = [Y_rx[c*cfg.Mc:(c+1)*cfg.Mc, :] for c in range(cfg.C)]
            
            # LMMSE
            W = lmmse_centralised(H_tgt, R_true, cfg.Es)
            S_det = detect(W @ Y_rx, const)
            e, t = count_errors(S_det, S_tx)
            err['LMMSE'] += e; tot += t
            
            # BCD1
            W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)
            W_bcd = bcd_mmse_update(list(W_bdac), Hc, Nc, cfg)
            S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
            e, _ = count_errors(S_det, S_tx); err['BCD1'] += e
            
            # LRD4
            G = lrd_algorithm(Nc, cfg.r, cfg)
            Gc = [G[c*cfg.Mc:(c+1)*cfg.Mc, :] for c in range(cfg.C)]
            W_lrd = list(W_bdac)
            for it in range(4):
                W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
            S_det = detect(apply_equalizer(W_lrd, Yc, cfg), const)
            e, _ = count_errors(S_det, S_tx); err['LRD4'] += e
            
            # sDR
            S_hat = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
            S_det = detect(S_hat, const)
            e, _ = count_errors(S_det, S_tx); err['sDR'] += e
            
            # cDR
            S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
            S_det = detect(S_hat, const)
            e, _ = count_errors(S_det, S_tx); err['cDR'] += e
        
        for a in algs:
            results[a].append(err[a] / max(tot, 1))
    
    return results

# Run with Rayleigh channels
print("=== Rayleigh channels (with bpS) ===")
snr_range_ray = np.arange(-10, 12, 2, dtype=float)
res_ray = run_sweep('rayleigh', snr_range_ray, N_mc)
print(f"{'SNR':>6s}  {'LMMSE':>10s}  {'BCD1':>10s}  {'LRD4':>10s}  {'sDR':>10s}  {'cDR':>10s}")
for i, snr in enumerate(snr_range_ray):
    print(f"{snr:+6.1f}  {res_ray['LMMSE'][i]:10.6f}  {res_ray['BCD1'][i]:10.6f}  {res_ray['LRD4'][i]:10.6f}  {res_ray['sDR'][i]:10.6f}  {res_ray['cDR'][i]:10.6f}")

# Run with MAT channels  
print("\n=== MAT channels (with bpS) ===")
snr_range_mat = np.arange(-10, 12, 2, dtype=float)
res_mat = run_sweep('mat', snr_range_mat, N_mc)
print(f"{'SNR':>6s}  {'LMMSE':>10s}  {'BCD1':>10s}  {'LRD4':>10s}  {'sDR':>10s}  {'cDR':>10s}")
for i, snr in enumerate(snr_range_mat):
    print(f"{snr:+6.1f}  {res_mat['LMMSE'][i]:10.6f}  {res_mat['BCD1'][i]:10.6f}  {res_mat['LRD4'][i]:10.6f}  {res_mat['sDR'][i]:10.6f}  {res_mat['cDR'][i]:10.6f}")
