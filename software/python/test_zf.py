import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import zf_centralised
from utils import detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'

for snr_db in [4, 6, 8, 10, 12]:
    SNR = 10**(snr_db/10)
    sigma2 = cfg.Es / SNR  # WITHOUT bpS
    
    e_zf = 0
    tot = 0
    for mc in range(20):
        H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
        R_true = 0 * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M) # ZF doesn't care about interference power
        Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
        
        S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
        noise_rx = Lc @ ((np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2))
        Y_rx = H_tgt @ S_tx + noise_rx
        
        W_zf = zf_centralised(H_tgt)
        S_det_zf = detect(W_zf @ Y_rx, const)
        
        e, t = count_errors(S_det_zf, S_tx)
        e_zf += e
        tot += t
    print(f"SNR={snr_db}dB, ZF={e_zf/tot:.6f}")
