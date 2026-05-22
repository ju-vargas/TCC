import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from utils import cluster_indices, detect, count_errors, inv_stable, apply_equalizer

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB/10)
snr_db = 2.0
SNR_lin = 10**(snr_db/10)
sigma2 = cfg.Es / (SNR_lin * bpS)
beta = (IoT_lin - 1) * sigma2 / cfg.r

err_bcd = 0; tot = 0
for mc in range(20):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    Y_rx = H_tgt @ S_tx + Lc @ z_rx
    
    Hc = [H_tgt[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    Rcc_true = [R_true[cluster_indices(c, cfg), :][:, cluster_indices(c, cfg)] for c in range(cfg.C)]
    Rcc_inv = [inv_stable(R) for R in Rcc_true]
    
    # BDAC (Iter 0)
    Gram = np.zeros((cfg.K, cfg.K), dtype=complex)
    for c in range(cfg.C):
        Gram += Hc[c].conj().T @ Rcc_inv[c] @ Hc[c]
    A_inv = inv_stable(Gram + (1.0 / cfg.Es) * np.eye(cfg.K))
    W_bdac = [A_inv @ Hc[c].conj().T @ Rcc_inv[c] for c in range(cfg.C)]
    
    # BCD1 with R_true
    W_bcd = list(W_bdac)
    A_prev = np.zeros((cfg.K, cfg.K), dtype=complex)
    B_prev = np.zeros((cfg.K, cfg.M), dtype=complex)
    for c in range(cfg.C):
        A_prev += W_bcd[c] @ Hc[c]
        B_prev[:, cluster_indices(c, cfg)] = W_bcd[c]
        
    for c in range(cfg.C):
        idx = cluster_indices(c, cfg)
        local_M = cfg.Es * Hc[c] @ Hc[c].conj().T + Rcc_true[c]
        local_M_inv = inv_stable(local_M)
        
        A_minus = A_prev - W_bcd[c] @ Hc[c]
        B_minus = np.copy(B_prev)
        B_minus[:, idx] = 0
        
        # Cross noise covariance: E[ N_minus @ N_c^H ] = B_minus @ R_true[:, idx]
        num = cfg.Es * (np.eye(cfg.K) - A_minus) @ Hc[c].conj().T - B_minus @ R_true[:, idx]
        W_bcd[c] = num @ local_M_inv
        
        A_prev = A_minus + W_bcd[c] @ Hc[c]
        B_prev = B_minus
        B_prev[:, idx] = W_bcd[c]
        
    S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
    e, t = count_errors(S_det, S_tx)
    err_bcd += e; tot += t

print(f"BCD1(R_true) at 2dB: {err_bcd/tot:.6f}")
