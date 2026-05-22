import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import lmmse_centralised
from utils import partition_clusters, cluster_indices, compute_local_cov, inv_stable, apply_equalizer, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB/10)
snr_db = 2.0
SNR_lin = 10**(snr_db/10)
sigma2 = cfg.Es / (SNR_lin * bpS)
beta = (IoT_lin - 1) * sigma2 / cfg.r

N_mc = 30

experiments = {
    'Baseline cDR': {'load_sigma2': 0.0},
    'Load 1x sigma2 cDR': {'load_sigma2': 1.0},
}

results = {k: 0 for k in experiments}
tot = 0

for mc in range(N_mc):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    Lc = np.linalg.cholesky(R_true + 1e-12*np.eye(cfg.M))
    
    z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
    N_mat = Lc @ z
    Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
    
    S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
    z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
    Y_rx = H_tgt @ S_tx + Lc @ z_rx
    Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
    
    for name, opts in experiments.items():
        Rcc = []
        Rcc_inv = []
        for c in range(cfg.C):
            R = (Nc[c] @ Nc[c].conj().T) / cfg.N_samples
            if opts['load_sigma2'] > 0:
                R = R + opts['load_sigma2'] * sigma2 * np.eye(cfg.Mc)
            Rcc.append(R)
            Rcc_inv.append(inv_stable(R))
            
        N = cfg.N_samples
        Ns = Yc[0].shape[1]
        CK = cfg.C * cfg.K
        y_tilde = np.zeros((CK, Ns), dtype=complex)
        H_tilde = np.zeros((CK, cfg.K), dtype=complex)
        Qn_list = []
        for c in range(cfg.C):
            Qc = Hc[c].conj().T @ Rcc_inv[c]
            rows = slice(c * cfg.K, (c + 1) * cfg.K)
            H_tilde[rows, :] = Qc @ Hc[c]
            y_tilde[rows, :] = Qc @ Yc[c]
            Qn_list.append(Qc @ Nc[c])
            
        R_tilde = np.zeros((CK, CK), dtype=complex)
        for m in range(cfg.C):
            rows_m = slice(m * cfg.K, (m + 1) * cfg.K)
            for l in range(cfg.C):
                rows_l = slice(l * cfg.K, (l + 1) * cfg.K)
                R_tilde[rows_m, rows_l] = (Qn_list[m] @ Qn_list[l].conj().T) / N
                
        # Also regularize R_tilde? Let's just try regularizing Rcc
        W = lmmse_centralised(H_tilde, R_tilde, cfg.Es)
        S_det = detect(W @ y_tilde, const)
        
        e, t = count_errors(S_det, S_tx)
        results[name] += e
        if name == 'Baseline cDR':
            tot += t

print(f"Results for cDR at 2 dB:")
for name in experiments:
    print(f"  {name:25s}: {results[name]/tot:.6f}")
