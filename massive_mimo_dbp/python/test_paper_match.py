import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised, sdr_mmse, bcd_mmse_update, bdac_mmse
from utils import partition_clusters, compute_local_cov, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'

def run_point(snr_db, use_r, use_bps):
    SNR = 10**(snr_db/10)
    sigma2 = cfg.Es / (SNR * (bpS if use_bps else 1.0))
    IoT_lin = 10**(cfg.IoT_dB/10)
    beta = (IoT_lin - 1) * sigma2 / (cfg.r if use_r else 1.0)
    
    e_lmmse, e_sdr, e_bcd = 0, 0, 0
    tot = 0
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

        W_bcd = bdac_mmse(Hc, Rcc_inv, cfg)
        W_bcd1 = bcd_mmse_update(W_bcd, Hc, Nc, cfg)
        S_det_bcd1 = detect(np.sum([W_bcd1[c] @ Yc[c] for c in range(cfg.C)], axis=0), const)
        
        e1, t1 = count_errors(S_det_lmmse, S_tx)
        e2, _ = count_errors(S_det_sdr, S_tx)
        e3, _ = count_errors(S_det_bcd1, S_tx)
        e_lmmse += e1; e_sdr += e2; e_bcd += e3
        tot += t1
    return e_lmmse/tot, e_sdr/tot, e_bcd/tot

# Test if paper used use_r=False and use_bps=False
print("Testing use_r=False, use_bps=False")
for snr in [-2, 0, 2, 4, 6]:
    l, s, b = run_point(snr, use_r=False, use_bps=False)
    print(f"SNR={snr:2d}dB: LMMSE={l:.6f}, sDR={s:.6f}, BCD1={b:.6f}")
