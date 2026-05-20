import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised, sdr_mmse, bcd_mmse_update, bdac_mmse
from utils import partition_clusters, compute_local_cov, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'

SNR_dB = 2.0
SNR = 10**(SNR_dB/10)
sigma2 = cfg.Es / (SNR * bpS)
IoT_lin = 10**(cfg.IoT_dB/10)
beta = (IoT_lin - 1) * sigma2 / cfg.r

tot, e_lmmse, e_sdr, e_bcd = 0, 0, 0, 0
for mc in range(20):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    noise_rx = Lc @ ((np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2))
    Y_rx = H_tgt @ S_tx + noise_rx
    
    N_mat = Lc @ ((np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2))
    Hc, Yc, Nc = partition_clusters(H_tgt, Y_rx, N_mat, cfg)
    Rcc, Rcc_inv = compute_local_cov(Nc, cfg)
    
    # Standard
    W_lmmse = lmmse_centralised(H_tgt, R_true, cfg.Es)
    # UNBIASING!
    D = np.diag(W_lmmse @ H_tgt)
    W_lmmse_unb = np.diag(1/D) @ W_lmmse
    S_det_lmmse = detect(W_lmmse_unb @ Y_rx, const)
    
    S_hat_sdr = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
    # How to unbias sDR? It uses W @ Y_check where W is LMMSE(H_check, R_check)
    # H_check = sum Qc Hc. W @ H_check is the effective channel.
    H_check = sum(Hc[c].conj().T @ Rcc_inv[c] @ Hc[c] for c in range(cfg.C))
    R_check = sum(Hc[c].conj().T @ Rcc_inv[c] @ Nc[c] for c in range(cfg.C))
    R_check = (R_check @ R_check.conj().T) / cfg.N_samples
    W_sdr = lmmse_centralised(H_check, R_check, cfg.Es)
    D_sdr = np.diag(W_sdr @ H_check)
    S_hat_sdr_unb = np.diag(1/D_sdr) @ S_hat_sdr
    S_det_sdr = detect(S_hat_sdr_unb, const)

    W_bcd = bdac_mmse(Hc, Rcc_inv, cfg)
    W_bcd1 = bcd_mmse_update(W_bcd, Hc, Nc, cfg)
    S_hat_bcd1 = np.sum([W_bcd1[c] @ Yc[c] for c in range(cfg.C)], axis=0)
    # Effective channel for BCD1 is sum W_bcd1[c] @ Hc[c]
    H_eff_bcd1 = np.sum([W_bcd1[c] @ Hc[c] for c in range(cfg.C)], axis=0)
    D_bcd1 = np.diag(H_eff_bcd1)
    S_hat_bcd1_unb = np.diag(1/D_bcd1) @ S_hat_bcd1
    S_det_bcd1 = detect(S_hat_bcd1_unb, const)
    
    e1, t1 = count_errors(S_det_lmmse, S_tx)
    e2, _ = count_errors(S_det_sdr, S_tx)
    e3, _ = count_errors(S_det_bcd1, S_tx)
    e_lmmse += e1; e_sdr += e2; e_bcd += e3
    tot += t1

print(f"UNBIASED SNR=2dB: LMMSE={e_lmmse/tot:.6f}, sDR={e_sdr/tot:.6f}, BCD1={e_bcd/tot:.6f}")
