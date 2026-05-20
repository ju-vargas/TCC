import numpy as np
from python.config import SimConfig
from python.channel import generate_channel_from_mat
from python.constellation import get_constellation, draw_symbols
from python.equalizers import lmmse_centralised
from python.utils import detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)

mat_file = '/home/juliana/GitHub/TCC/massive_mimo_dbp/channels_fig8a_M128_C8_K8.mat'

SNR_dB = 6.0
SNR = 10**(SNR_dB/10)
sigma2 = cfg.Es / SNR

err = 0
total = 0
for mc in range(100):
    H_tgt, _ = generate_channel_from_mat(mat_file, mc, cfg)
    
    R_awgn = sigma2 * np.eye(cfg.M)
    Lc = np.linalg.cholesky(R_awgn)
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    noise_rx = Lc @ z_rx
    Y_rx = H_tgt @ S_tx + noise_rx
    
    W = lmmse_centralised(H_tgt, R_awgn, cfg.Es)
    S_det = detect(W @ Y_rx, const)
    e, t = count_errors(S_det, S_tx)
    err += e
    total += t

print(f"AWGN SER at {SNR_dB} dB: {err/total:.6f}")
