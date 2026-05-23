import numpy as np
from config import make_config
from constellation import get_constellation, draw_symbols
from channel import generate_channel_from_mat
from utils import partition_clusters, cluster_indices, compute_local_cov, apply_equalizer, detect, count_errors
from equalizers import lmmse_centralised, lrd_algorithm, bcd_mmse_lrd_update, bdac_mmse

def main():
    cfg = make_config('fig8a', channel_mode='mat_file', mat_file='../channels_fig8a_M128_C8_K8.mat', N_mc=5)
    const, bpS = get_constellation(cfg.mod)
    cfg.SNR_dB = np.array([2.0])  # Only test 2 dB
    
    e_lmmse, e_lrd4_est, e_lrd4_true = 0, 0, 0
    t_lmmse, t_lrd4_est, t_lrd4_true = 0, 0, 0
    
    for mc in range(cfg.N_mc):
        H_tgt, H_itf = generate_channel_from_mat(cfg.mat_file, mc, cfg)
        SNR_lin = 10 ** (cfg.SNR_dB[0] / 10)
        sigma2 = cfg.Es / (SNR_lin * bpS)
        IoT_lin = 10 ** (cfg.IoT_dB / 10)
        beta = (IoT_lin - 1) * sigma2 / cfg.r
        
        R_true = beta * (H_itf @ H_itf.conj().T) + sigma2 * np.eye(cfg.M)
        R_reg = R_true + 1e-12 * np.real(np.trace(R_true)) / cfg.M * np.eye(cfg.M)
        Lc = np.linalg.cholesky(R_reg)
        
        z = (np.random.randn(cfg.M, cfg.N_samples) + 1j * np.random.randn(cfg.M, cfg.N_samples)) / np.sqrt(2)
        N_mat = Lc @ z
        
        Hc, _, Nc = partition_clusters(H_tgt, None, N_mat, cfg)
        
        # Local covs: Estimated
        Rcc_est, Rcc_est_inv = compute_local_cov(Nc, cfg, sigma2)
        
        # Local covs: True
        Rcc_true = []
        Rcc_true_inv = []
        from utils import inv_stable
        for c in range(cfg.C):
            idx = cluster_indices(c, cfg)
            R_block = R_true[np.ix_(idx, idx)]
            Rcc_true.append(R_block)
            Rcc_true_inv.append(inv_stable(R_block))
            
        S_tx = draw_symbols(const, cfg.K, cfg.N_sym)
        z_rx = (np.random.randn(cfg.M, cfg.N_sym) + 1j * np.random.randn(cfg.M, cfg.N_sym)) / np.sqrt(2)
        Y_rx = H_tgt @ S_tx + Lc @ z_rx
        Yc = [Y_rx[cluster_indices(c, cfg), :] for c in range(cfg.C)]
        
        # LMMSE
        W_lmmse = lmmse_centralised(H_tgt, R_true, cfg.Es)
        e, t = count_errors(detect(W_lmmse @ Y_rx, const), S_tx)
        e_lmmse += e; t_lmmse += t
        
        # LRD4 with R_est
        G_est = lrd_algorithm(Nc, cfg.r, cfg)
        Gc_est = [G_est[cluster_indices(c, cfg), :] for c in range(cfg.C)]
        W_lrd_est = bdac_mmse(Hc, Rcc_est_inv, cfg)
        for _ in range(4):
            W_lrd_est = bcd_mmse_lrd_update(W_lrd_est, Hc, Gc_est, Rcc_est, cfg)
        e, t = count_errors(detect(apply_equalizer(W_lrd_est, Yc, cfg), const), S_tx)
        e_lrd4_est += e; t_lrd4_est += t
        
        # LRD (True) - 100 iterations
        G_true = np.sqrt(beta) * H_itf
        Gc_true = [G_true[cluster_indices(c, cfg), :] for c in range(cfg.C)]
        W_lrd_true = bdac_mmse(Hc, Rcc_true_inv, cfg)
        for _ in range(100):
            W_lrd_true = bcd_mmse_lrd_update(W_lrd_true, Hc, Gc_true, Rcc_true, cfg)
        e, t = count_errors(detect(apply_equalizer(W_lrd_true, Yc, cfg), const), S_tx)
        e_lrd4_true += e; t_lrd4_true += t
        
        # BCD (True) - 100 iterations
        from equalizers import bcd_mmse_update
        # N_mat_true should act like true noise. But BCD uses (1/N) * Nc @ Nc^H
        # We can't easily fake Nc to have R_true unless we use Lc.
        # But wait! bcd_mmse_update uses Nc directly. We can't fake it easily.


    print(f"LMMSE: {e_lmmse/t_lmmse:.6f}")
    print(f"LRD4 (Est): {e_lrd4_est/t_lrd4_est:.6f}")
    print(f"LRD4 (True): {e_lrd4_true/t_lrd4_true:.6f}")

if __name__ == '__main__':
    main()
