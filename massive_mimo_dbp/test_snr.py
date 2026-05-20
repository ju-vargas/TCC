import numpy as np
from python.config import SimConfig
from python.channel import generate_channel_from_mat
from python.constellation import get_constellation, draw_symbols
from python.equalizers import bdac_mmse, bcd_mmse_update, cdr_mmse, sdr_mmse
from python.utils import partition_clusters, compute_local_cov, apply_equalizer, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)

mat_file = '/home/juliana/GitHub/TCC/massive_mimo_dbp/channels_fig8a_M128_C8_K8.mat'

SNR_dB = 5.0
SNR = 10**(SNR_dB/10)
sigma2 = cfg.Es / (SNR * bpS)
IoT_lin = 10**(cfg.IoT_dB/10)
beta = (IoT_lin - 1) * sigma2 / cfg.r   # WITH /r

err_bcd1 = 0
err_cdr = 0
err_sdr = 0
total = 0
for mc in range(100):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    noise_rx = Lc @ z_rx
    Y_rx = H_tgt @ S_tx + noise_rx
    
    z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
    N_mat = Lc @ z
    
    Hc, Yc, Nc = partition_clusters(H_tgt, Y_rx, N_mat, cfg)
    Rcc, Rcc_inv = compute_local_cov(Nc, cfg)
    
    W_bcd = bdac_mmse(Hc, Rcc_inv, cfg)
    W_bcd1 = bcd_mmse_update(W_bcd, Hc, Nc, cfg)
    S_det_bcd1 = detect(apply_equalizer(W_bcd1, Yc, cfg), const)
    
    S_hat_cdr = cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
    S_det_cdr = detect(S_hat_cdr, const)

    S_hat_sdr = sdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
    S_det_sdr = detect(S_hat_sdr, const)
    
    e1, t1 = count_errors(S_det_bcd1, S_tx)
    e2, _ = count_errors(S_det_cdr, S_tx)
    e3, _ = count_errors(S_det_sdr, S_tx)
    err_bcd1 += e1
    err_cdr += e2
    err_sdr += e3
    total += t1

print(f"SER at {SNR_dB} dB: BCD(1)={err_bcd1/total:.6f}, cDR={err_cdr/total:.6f}, sDR={err_sdr/total:.6f}")
