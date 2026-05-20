import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised, sdr_mmse
from utils import partition_clusters, compute_local_cov, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'

SNR_dB = 6.0  # SNR=6dB => Eb/N0=0dB
SNR = 10**(SNR_dB/10)
sigma2 = cfg.Es / (SNR * bpS)
IoT_lin = 10**(cfg.IoT_dB/10)

for use_r in [True, False]:
    beta = (IoT_lin - 1) * sigma2 / (cfg.r if use_r else 1.0)
    err_lmmse = 0
    err_sdr = 0
    total = 0
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
        
        W_lmmse = lmmse_centralised(H_tgt, R_true, cfg.Es)
        S_det_lmmse = detect(W_lmmse @ Y_rx, const)
        
        S_hat_sdr = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
        S_det_sdr = detect(S_hat_sdr, const)
        
        e1, t1 = count_errors(S_det_lmmse, S_tx)
        e2, _ = count_errors(S_det_sdr, S_tx)
        err_lmmse += e1
        err_sdr += e2
        total += t1
        
    print(f"With /r={use_r}: LMMSE={err_lmmse/total:.6f}, sDR={err_sdr/total:.6f}")
