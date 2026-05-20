"""Test with UPA antenna geometry in QuaDRiGa channel generation."""
import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat
from constellation import get_constellation, draw_symbols
from equalizers import (lmmse_centralised, bdac_mmse, bcd_mmse_update,
                        lrd_algorithm, bcd_mmse_lrd_update, sdr_mmse, cdr_mmse)
from utils import inv_stable, detect, count_errors

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB / 10)
Mc = cfg.M // cfg.C

# For a UPA with 8 rows x 16 columns = 128 antennas
# Paper clusters: "C=8 clusters"
# With UPA and 8 clusters: 2 columns per cluster (column-based partitioning)
# Or: 1 row per cluster (row-based partitioning)
# With row-based: Cluster c gets row c -> spatially diverse along columns

# But wait: the .mat file was generated with a vertical ULA
# With a ULA, the BEST we can do is interleaved assignment
# Let's also try randomised assignment to find the pattern

def partition_random_interleaved(H, N_mat, Y_rx, cfg, seed=42):
    """Random assignment of antennas to clusters."""
    rng = np.random.RandomState(seed)
    perm = rng.permutation(cfg.M)
    Hc, Nc, Yc = [], [], []
    for c in range(cfg.C):
        idx = perm[c*Mc:(c+1)*Mc]
        Hc.append(H[idx, :])
        Nc.append(N_mat[idx, :])
        Yc.append(Y_rx[idx, :])
    return Hc, Nc, Yc

def compute_local_cov_custom(Nc, cfg):
    Rcc, Rcc_inv = [], []
    for c in range(cfg.C):
        R = (Nc[c] @ Nc[c].conj().T) / cfg.N_samples
        R += 1e-10 * np.eye(Mc) * np.real(np.trace(R)) / Mc
        Rcc.append(R)
        Rcc_inv.append(inv_stable(R))
    return Rcc, Rcc_inv

def apply_eq(W_list, Yc, cfg):
    return np.sum([W_list[c] @ Yc[c] for c in range(cfg.C)], axis=0)

def run_point(snr_db, mode='contiguous', n_mc=50):
    SNR_lin = 10**(snr_db / 10)
    sigma2 = cfg.Es / (SNR_lin * bpS)
    beta = (IoT_lin - 1) * sigma2 / cfg.r
    
    e = {'LMMSE': 0, 'BCD1': 0, 'LRD4': 0, 'cDR': 0}
    tot = 0
    for mc in range(n_mc):
        H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
        R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
        R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
        Lc_ = np.linalg.cholesky(R_reg)
        
        z = (np.random.randn(cfg.M, cfg.N_samples) + 1j*np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
        N_mat = Lc_ @ z
        
        S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
        Y_rx = H_tgt @ S_tx + Lc_ @ (np.random.randn(cfg.M, cfg.N_sym) + 1j*np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
        
        if mode == 'interleaved':
            Hc, Nc = [], []
            Yc = []
            for c in range(cfg.C):
                idx = np.arange(c, cfg.M, cfg.C)
                Hc.append(H_tgt[idx, :]); Nc.append(N_mat[idx, :]); Yc.append(Y_rx[idx, :])
        elif mode == 'random':
            Hc, Nc, Yc = partition_random_interleaved(H_tgt, N_mat, Y_rx, cfg, seed=mc)
        else:
            Hc = [H_tgt[c*Mc:(c+1)*Mc, :] for c in range(cfg.C)]
            Nc = [N_mat[c*Mc:(c+1)*Mc, :] for c in range(cfg.C)]
            Yc = [Y_rx[c*Mc:(c+1)*Mc, :] for c in range(cfg.C)]
        
        Rcc, Rcc_inv = compute_local_cov_custom(Nc, cfg)
        
        W = lmmse_centralised(H_tgt, R_true, cfg.Es)
        S_det = detect(W @ Y_rx, const)
        e1, t = count_errors(S_det, S_tx); e['LMMSE'] += e1; tot += t
        
        W_bdac = bdac_mmse(Hc, Rcc_inv, cfg)
        W_bcd = bcd_mmse_update(list(W_bdac), Hc, Nc, cfg)
        S_det = detect(apply_eq(W_bcd, Yc, cfg), const)
        e1, _ = count_errors(S_det, S_tx); e['BCD1'] += e1
        
        G = lrd_algorithm(Nc, cfg.r, cfg)
        Gc = [G[c*Mc:(c+1)*Mc, :] for c in range(cfg.C)]
        W_lrd = list(W_bdac)
        for it in range(4):
            W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, cfg)
        S_det = detect(apply_eq(W_lrd, Yc, cfg), const)
        e1, _ = count_errors(S_det, S_tx); e['LRD4'] += e1
        
        S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, cfg)
        S_det = detect(S_hat, const)
        e1, _ = count_errors(S_det, S_tx); e['cDR'] += e1
    
    return {a: e[a]/max(tot, 1) for a in e}

for mode in ['contiguous', 'interleaved', 'random']:
    print(f"\n=== {mode.upper()} clustering ===")
    for snr in [-4, -2, 0, 2]:
        r = run_point(snr, mode, 50)
        print(f"  SNR={snr:+3d}: LMMSE={r['LMMSE']:.6f} BCD1={r['BCD1']:.6f} LRD4={r['LRD4']:.6f} cDR={r['cDR']:.6f}")
