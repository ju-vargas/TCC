"""Analyze the covariance structure of the channels."""
import numpy as np
from config import SimConfig
from channel import generate_channel_from_mat, generate_channel_rayleigh
from constellation import get_constellation

cfg = SimConfig(M=128, K=8, C=8, r=8, N_samples=192, N_sym=480, IoT_dB=10.0, mod='16QAM')
const, bpS = get_constellation(cfg.mod)
mat_file = '../channels_fig8a_M128_C8_K8.mat'
IoT_lin = 10**(cfg.IoT_dB / 10)

SNR_dB = 0.0
SNR_lin = 10**(SNR_dB / 10)
sigma2 = cfg.Es / SNR_lin  # Paper: SNR = Es/sigma2
beta = (IoT_lin - 1) * sigma2

# Test block-diagonal quality for MAT channels
print("=== MAT channels: Cross-cluster correlation analysis ===")
off_diag_fracs = []
for mc in range(20):
    H_tgt, H_itf = generate_channel_from_mat(mat_file, mc, cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    
    # Compute block diagonal fraction
    total_energy = np.sum(np.abs(R_true)**2)
    diag_energy = 0.0
    for c in range(cfg.C):
        idx = slice(c*cfg.Mc, (c+1)*cfg.Mc)
        diag_energy += np.sum(np.abs(R_true[idx, idx])**2)
    
    off_diag_frac = 1 - diag_energy / total_energy
    off_diag_fracs.append(off_diag_frac)
    
    # Channel condition number
    cond = np.linalg.cond(H_tgt)
    
    # Correlation between columns of H_tgt
    H_norm = H_tgt / np.sqrt(np.sum(np.abs(H_tgt)**2, axis=0, keepdims=True))
    G = H_norm.conj().T @ H_norm  # KxK Gram matrix
    np.fill_diagonal(G, 0)
    max_corr = np.max(np.abs(G))
    avg_corr = np.mean(np.abs(G))
    
    if mc < 5:
        print(f"  mc={mc}: cond(H)={cond:.1f}, off_diag_frac={off_diag_frac:.4f}, "
              f"max_corr={max_corr:.4f}, avg_corr={avg_corr:.4f}")

print(f"\n  Avg off-diagonal fraction: {np.mean(off_diag_fracs):.4f}")

# Compare with Rayleigh
print("\n=== Rayleigh channels: Cross-cluster correlation analysis ===")
off_diag_fracs_ray = []
for mc in range(20):
    H_tgt, H_itf = generate_channel_rayleigh(cfg)
    R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
    
    total_energy = np.sum(np.abs(R_true)**2)
    diag_energy = 0.0
    for c in range(cfg.C):
        idx = slice(c*cfg.Mc, (c+1)*cfg.Mc)
        diag_energy += np.sum(np.abs(R_true[idx, idx])**2)
    
    off_diag_frac = 1 - diag_energy / total_energy
    off_diag_fracs_ray.append(off_diag_frac)
    
    cond = np.linalg.cond(H_tgt)
    H_norm = H_tgt / np.sqrt(np.sum(np.abs(H_tgt)**2, axis=0, keepdims=True))
    G = H_norm.conj().T @ H_norm
    np.fill_diagonal(G, 0)
    max_corr = np.max(np.abs(G))
    avg_corr = np.mean(np.abs(G))
    
    if mc < 5:
        print(f"  mc={mc}: cond(H)={cond:.1f}, off_diag_frac={off_diag_frac:.4f}, "
              f"max_corr={max_corr:.4f}, avg_corr={avg_corr:.4f}")

print(f"\n  Avg off-diagonal fraction: {np.mean(off_diag_fracs_ray):.4f}")
