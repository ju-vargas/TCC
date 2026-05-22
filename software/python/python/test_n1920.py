import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lrd_algorithm, bcd_mmse_lrd_update, bdac_mmse
from utils import partition_clusters, cluster_indices, compute_local_cov, apply_equalizer, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=1920, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB/10)
snr_db = 2.0
SNR_lin = 10**(snr_db/10)
sigma2 = cfg.Es / (SNR_lin * bpS)
beta = (IoT_lin - 1) * sigma2 / cfg.r

err = 0; tot = 0
for mc in range(20):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    
    z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
    N_mat = Lc @ z
    Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
    Rcc, Rcc_inv = compute_local_cov(Nc, cfg)
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    Y_rx = H_tgt @ S_tx + Lc @ z_rx
    Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    
    W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)
    G = lrd_algorithm(Nc, cfg.r, cfg)
    Gc = [G[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    W_lrd = list(W_bdac)
    for it in range(4):
        W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
    S_det = detect(apply_equalizer(W_lrd, Yc, cfg), const)
    e, t = count_errors(S_det, S_tx)
    err += e; tot += t

print(f"LRD4 at 2dB with N=1920: {err/tot:.6f}")
