import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised
from utils import detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB/10)

snr_db = 0.0
SNR_lin = 10**(snr_db/10)
sigma2 = cfg.Es / (SNR_lin * bpS)
beta = (IoT_lin - 1) * sigma2 / cfg.r

err_true = 0
err_est = 0
tot = 0

for mc in range(100):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    
    z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
    N_mat = Lc @ z
    R_est = (N_mat @ N_mat.conj().T) / cfg.N_samples
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    Y_rx = H_tgt @ S_tx + Lc @ z_rx
    
    W_true = lmmse_centralised(H_tgt, R_true, cfg.Es)
    S_det_true = detect(W_true @ Y_rx, const)
    e, t = count_errors(S_det_true, S_tx)
    err_true += e; tot += t
    
    W_est = lmmse_centralised(H_tgt, R_est, cfg.Es)
    S_det_est = detect(W_est @ Y_rx, const)
    e, _ = count_errors(S_det_est, S_tx)
    err_est += e

print(f"LMMSE(R_true) at 0dB: {err_true/tot:.6f}")
print(f"LMMSE(R_est) at 0dB:  {err_est/tot:.6f}")
