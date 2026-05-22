import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from equalizers import lmmse_centralised, bcd_mmse_update, bdac_mmse
from utils import partition_clusters, compute_local_cov

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB/10)
snr_db = 2.0
SNR_lin = 10**(snr_db/10)
sigma2 = cfg.Es / (SNR_lin * 4) # bpS=4
beta = (IoT_lin - 1) * sigma2 / cfg.r

H_tgt, H_itf = generate_channel_from_mat(mat_file, 0, cfg)
R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
N_mat = Lc @ z
R_est = (N_mat @ N_mat.conj().T) / cfg.N_samples

W_lmmse = lmmse_centralised(H_tgt, R_est, cfg.Es)

Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
Rcc, Rcc_inv = compute_local_cov(Nc, cfg)

W_bcd = bdac_mmse(Hc, Rcc_inv, cfg)
for it in range(20):
    W_bcd = bcd_mmse_update(W_bcd, Hc, Nc, cfg)
    W_concat = np.hstack(W_bcd)
    diff = np.linalg.norm(W_concat - W_lmmse) / np.linalg.norm(W_lmmse)
    print(f"Iter {it+1}: relative error to LMMSE(R_est) = {diff:.6f}")
