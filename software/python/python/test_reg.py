import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from utils import partition_clusters, cluster_indices, compute_local_cov, inv_stable, apply_equalizer, detect, count_errors

def bdac_mmse_reg(Hc, Rcc_inv, cfg, alpha=1.0):
    Gram = np.zeros((cfg.K, cfg.K), dtype=complex)
    for c in range(cfg.C):
        Gram += Hc[c].conj().T @ Rcc_inv[c] @ Hc[c]
    A_inv = inv_stable(Gram + alpha * (1.0 / cfg.Es) * np.eye(cfg.K))
    W_list = []
    for c in range(cfg.C):
        W_list.append(A_inv @ Hc[c].conj().T @ Rcc_inv[c])
    return W_list

def bcd_mmse_update_reg(W_old, Hc, Nc, cfg, Rcc_reg=None):
    N = cfg.N_samples
    W_new = list(W_old)
    A_prev = np.zeros((cfg.K, cfg.K), dtype=complex)
    b_prev = np.zeros((cfg.K, N), dtype=complex)
    for c in range(cfg.C):
        A_prev += W_old[c] @ Hc[c]
        b_prev += W_old[c] @ Nc[c]
        
    for c in range(cfg.C):
        HcHc_T = Hc[c] @ Hc[c].conj().T
        if Rcc_reg is None:
            NcNc_T = (Nc[c] @ Nc[c].conj().T) / N
        else:
            NcNc_T = Rcc_reg[c]
            
        local_M = cfg.Es * HcHc_T + NcNc_T
        local_M_inv = inv_stable(local_M)
        
        A_minus = A_prev - W_old[c] @ Hc[c]
        b_minus = b_prev - W_old[c] @ Nc[c]
        
        num = cfg.Es * (np.eye(cfg.K) - A_minus) @ Hc[c].conj().T - (b_minus @ Nc[c].conj().T) / N
        W_new[c] = num @ local_M_inv
        
        A_prev = A_minus + W_new[c] @ Hc[c]
        b_prev = b_minus + W_new[c] @ Nc[c]
        
    return W_new

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
    'Baseline': {'alpha_bdac': 1.0, 'rho_shrink': 0.0, 'load_sigma2': 0.0},
    'Load 1x sigma2': {'alpha_bdac': 1.0, 'rho_shrink': 0.0, 'load_sigma2': 1.0},
    'Load 2x sigma2': {'alpha_bdac': 1.0, 'rho_shrink': 0.0, 'load_sigma2': 2.0},
    'Shrink 0.1': {'alpha_bdac': 1.0, 'rho_shrink': 0.1, 'load_sigma2': 0.0},
    'Shrink 0.5': {'alpha_bdac': 1.0, 'rho_shrink': 0.5, 'load_sigma2': 0.0},
    'BDAC alpha=2': {'alpha_bdac': 2.0, 'rho_shrink': 0.0, 'load_sigma2': 0.0},
    'BDAC alpha=4': {'alpha_bdac': 4.0, 'rho_shrink': 0.0, 'load_sigma2': 0.0},
    'BDAC alpha=8 (K)': {'alpha_bdac': 8.0, 'rho_shrink': 0.0, 'load_sigma2': 0.0},
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
            if opts['rho_shrink'] > 0:
                R = (1 - opts['rho_shrink']) * R + opts['rho_shrink'] * sigma2 * np.eye(cfg.Mc)
            if opts['load_sigma2'] > 0:
                R = R + opts['load_sigma2'] * sigma2 * np.eye(cfg.Mc)
            Rcc.append(R)
            Rcc_inv.append(inv_stable(R))
            
        W_bdac = bdac_mmse_reg(Hc, Rcc_inv, cfg, alpha=opts['alpha_bdac'])
        W_bcd = bcd_mmse_update_reg(W_bdac, Hc, Nc, cfg, Rcc_reg=Rcc)
        
        S_det = detect(apply_equalizer(W_bcd, Yc, cfg), const)
        e, t = count_errors(S_det, S_tx)
        results[name] += e
        if name == 'Baseline':
            tot += t

print(f"Results for BCD1 at 2 dB (Target ~0.000200):")
for name in experiments:
    print(f"  {name:20s}: {results[name]/tot:.6f}")
