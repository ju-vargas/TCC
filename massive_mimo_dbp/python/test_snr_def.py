"""Test two SNR definitions to find which matches the paper's Fig 8a."""
import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised, sdr_mmse, cdr_mmse, bdac_mmse, bcd_mmse_update, lrd_algorithm, bcd_mmse_lrd_update
from utils import partition_clusters, compute_local_cov, apply_equalizer, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'

SNR_dB_range = np.arange(-10, 12, 2, dtype=float)
IoT_lin = 10**(cfg.IoT_dB / 10)

for label, use_bps in [("SNR=Es/sigma2 (no bpS)", False), ("SNR=Eb/N0 (with bpS)", True)]:
    print(f"\n=== {label} ===")
    for snr_db in SNR_dB_range:
        SNR_lin = 10**(snr_db / 10)
        if use_bps:
            sigma2 = cfg.Es / (SNR_lin * bpS)
        else:
            sigma2 = cfg.Es / SNR_lin
        
        beta = (IoT_lin - 1) * sigma2 / cfg.r
        
        e_lmmse, e_bcd1, e_lrd4, tot = 0, 0, 0, 0
        for mc in range(min(50, 100)):
            H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
            R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
            R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
            Lc = np.linalg.cholesky(R_reg)
            
            z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
            N_mat = Lc @ z
            Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
            Rcc, Rcc_inv = compute_local_cov(Nc, cfg)
            
            S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
            z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
            noise_rx = Lc @ z_rx
            Y_rx = H_tgt @ S_tx + noise_rx
            Yc = [Y_rx[c*cfg.Mc:(c+1)*cfg.Mc, :] for c in range(cfg.C)]
            
            # LMMSE
            W = lmmse_centralised(H_tgt, R_true, cfg.Es)
            S_det = detect(W @ Y_rx, const)
            e, t = count_errors(S_det, S_tx)
            e_lmmse += e; tot += t
            
            # BCD1
            W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)
            W_bcd = bcd_mmse_update(list(W_bdac), Hc, Nc, cfg)
            S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
            e, _ = count_errors(S_det, S_tx)
            e_bcd1 += e
            
            # LRD4
            G = lrd_algorithm(Nc, cfg.r, cfg)
            Gc = [G[c*cfg.Mc:(c+1)*cfg.Mc, :] for c in range(cfg.C)]
            W_lrd = list(W_bdac)
            for it in range(4):
                W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
            S_det = detect(apply_equalizer(W_lrd, Yc, cfg), const)
            e, _ = count_errors(S_det, S_tx)
            e_lrd4 += e
        
        ser_l = e_lmmse / max(tot, 1)
        ser_b = e_bcd1 / max(tot, 1)
        ser_r = e_lrd4 / max(tot, 1)
        if ser_l > 0 or snr_db <= 4:
            print(f"  SNR={snr_db:+5.1f}dB: LMMSE={ser_l:.6f}  BCD1={ser_b:.6f}  LRD4={ser_r:.6f}")
