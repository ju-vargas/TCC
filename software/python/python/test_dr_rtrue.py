import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised, zf_centralised
from utils import cluster_indices, detect, count_errors, inv_stable

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB/10)
snr_db = 2.0
SNR_lin = 10**(snr_db/10)
sigma2 = cfg.Es / (SNR_lin * bpS)
beta = (IoT_lin - 1) * sigma2 / cfg.r

err_sdr = 0; err_cdr = 0; tot = 0
for mc in range(20):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    Y_rx = H_tgt @ S_tx + Lc @ z_rx
    
    # Partition
    Hc = [H_tgt[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    Rcc_true = [R_true[cluster_indices(c, cfg), :][:, cluster_indices(c, cfg)] for c in range(cfg.C)]
    Rcc_inv = [inv_stable(R) for R in Rcc_true]
    
    # sDR with R_true
    H_check = np.zeros((cfg.K, cfg.K), dtype=complex)
    y_check = np.zeros((cfg.K, cfg.N_sym), dtype=complex)
    Q = np.zeros((cfg.K, cfg.M), dtype=complex)
    for c in range(cfg.C):
        Qc = Hc[c].conj().T @ Rcc_inv[c]
        H_check += Qc @ Hc[c]
        y_check += Qc @ Yc[c]
        Q[:, cluster_indices(c, cfg)] = Qc
    
    R_check = Q @ R_true @ Q.conj().T
    W_sdr = lmmse_centralised(H_check, R_check, cfg.Es)
    S_det_sdr = detect(W_sdr @ y_check, const)
    e, t = count_errors(S_det_sdr, S_tx)
    err_sdr += e; tot += t
    
    # cDR with R_true
    CK = cfg.C * cfg.K
    H_tilde = np.zeros((CK, cfg.K), dtype=complex)
    y_tilde = np.zeros((CK, cfg.N_sym), dtype=complex)
    Q_tilde = np.zeros((CK, cfg.M), dtype=complex)
    for c in range(cfg.C):
        Qc = Hc[c].conj().T @ Rcc_inv[c]
        rows = slice(c*cfg.K, (c+1)*cfg.K)
        H_tilde[rows, :] = Qc @ Hc[c]
        y_tilde[rows, :] = Qc @ Yc[c]
        Q_tilde[rows, cluster_indices(c, cfg)] = Qc
        
    R_tilde = Q_tilde @ R_true @ Q_tilde.conj().T
    W_cdr = lmmse_centralised(H_tilde, R_tilde, cfg.Es)
    S_det_cdr = detect(W_cdr @ y_tilde, const)
    e, _ = count_errors(S_det_cdr, S_tx)
    err_cdr += e

print(f"sDR(R_true) at 2dB: {err_sdr/tot:.6f}")
print(f"cDR(R_true) at 2dB: {err_cdr/tot:.6f}")
