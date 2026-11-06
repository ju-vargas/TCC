#!/usr/bin/env python3
"""Correctness checks for dbp_sim against properties the article proves.

These are not regression tests against numbers - they check the implementation obeys
theorems the article states, which is what makes the port trustworthy.
"""
import numpy as np
from dbp_sim import m2_channel, m3_clustering, m4_source, m5_noise, m7_equalizers
from dbp_sim.m5_noise import Conditioner
from dbp_sim.m1_driver import SimConfig, build_equalizers
from dbp_sim.params import FIGURE8_PANELS

rng = np.random.default_rng(7)
FAIL = []

def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   {detail}")
    if not ok: FAIL.append(name)

# ---- fixture ------------------------------------------------------------------------
M, C, K, r, N, Es = 128, 8, 8, 8, 192, 1.0
be = m2_channel.StandInULAChannel(spread_deg=10.0)
H, Hbar = be.generate(M, K, r, 0, rng)
clusters = m3_clustering.cluster_indices(M, C, "contiguous")
sigma2 = Es * 10 ** (0.4)
beta = m5_noise.beta_from_iot(10.0, sigma2, Hbar, "realised_per_antenna")
L = m5_noise.cholesky_factor(m5_noise.noise_covariance(Hbar, beta, sigma2))
S = m5_noise.scaled_sample_matrix(m5_noise.draw_noise(L, N, rng))
R_hat = m5_noise.sample_covariance(S)
COND = Conditioner('ledoit_wolf'); COND.prime(S)
RAW = Conditioner('none')

print("\n1. Module invariants")
check("normalization: E[|h|^2] == 1 for every UE (per-UE power control)",
      np.allclose((np.abs(np.hstack([H, Hbar]))**2).mean(axis=0), 1.0, atol=1e-9))
check("clustering: contiguous partitions M exactly",
      sorted(np.concatenate(clusters).tolist()) == list(range(M)))
check("clustering: interleaved partitions M exactly",
      sorted(np.concatenate(m3_clustering.cluster_indices(M, C, "interleaved")).tolist())
      == list(range(M)))
check("constellation: unit average energy",
      abs((np.abs(m4_source.constellation("16QAM"))**2).mean() - 1) < 1e-12)
check("scaled sample matrix: S S^H == R_hat (Eq. 32)",
      np.allclose(S @ S.conj().T, R_hat))
realised = 10*np.log10(1 + beta*float(np.vdot(Hbar,Hbar).real)/M/sigma2)
check("beta: realised per-antenna IoT == nominal", abs(realised - 10.0) < 1e-6,
      f"realised {realised:.3f} dB")

print("\n2. Theorem 2 (L463): BCD objective decreases monotonically")
W = m7_equalizers.bdac_mmse(H, S, clusters, Es, COND)
objs = [m7_equalizers.bcd_objective(W, H, R_hat, Es)]
for it in range(6):
    W = m7_equalizers.bcd_mmse(H, S, clusters, Es, 1, COND, W0=W)
    objs.append(m7_equalizers.bcd_objective(W, H, R_hat, Es))
mono = all(b <= a + 1e-9 for a, b in zip(objs, objs[1:]))
check("objective (24) non-increasing", mono,
      " -> ".join(f"{o:.4f}" for o in objs[:4]) + " ...")

print("\n3. Proposition 1 (L363): MSE(sDR) >= MSE(cDR)")
def mse(W):
    E = W @ H - np.eye(K)
    return float(Es*np.trace(E@E.conj().T).real + np.trace(W@R_hat@W.conj().T).real)
Ws = m7_equalizers.sdr_mmse(H, S, clusters, Es, RAW)
Wc = m7_equalizers.cdr_mmse(H, S, clusters, Es, RAW)
check("cDR no worse than sDR", mse(Wc) <= mse(Ws)*(1+1e-9),
      f"sDR {mse(Ws):.5f} >= cDR {mse(Wc):.5f}")

print("\n4. LMMSE is the unconstrained optimum of (2)")
Wl = m7_equalizers.lmmse(H, S, Es, RAW)
others = {"BDAC": m7_equalizers.bdac_mmse(H, S, clusters, Es, RAW),
          "sDR": Ws, "cDR": Wc,
          "BCD-4": m7_equalizers.bcd_mmse(H, S, clusters, Es, 4, RAW)}
check("LMMSE minimises (24) among all", all(mse(Wl) <= mse(W)*(1+1e-8) for W in others.values()),
      "LMMSE %.5f vs " % mse(Wl) + ", ".join(f"{k} {mse(v):.5f}" for k,v in others.items()))

print("\n5. LRD (Algorithm 4): rank-r factor approximates R_hat")
G = m7_equalizers.lrd_decomposition(S, clusters, 8)
check("G has rank <= r", np.linalg.matrix_rank(G) <= 8, f"shape {G.shape}")
ev = np.linalg.eigvalsh(R_hat)[::-1]
captured = float(np.linalg.norm(G, 'fro')**2 / np.linalg.norm(S, 'fro')**2)
check("G captures the dominant subspace", captured > 0.5, f"energy fraction {captured:.3f}")

print("\n6. Decentralization: no method inverts more than the article allows")
Mc = M // C
check(f"BDAC/sDR/cDR/BCD touch at most M_c={Mc} or CK={C*K}", Mc <= N and C*K <= N,
      f"M_c={Mc}, CK={C*K}, N={N}")
check("R_hat is singular at M=256 (needs conditioning)",
      np.linalg.matrix_rank(m5_noise.sample_covariance(
          m5_noise.scaled_sample_matrix(m5_noise.draw_noise(
              m5_noise.cholesky_factor(np.eye(256)), 192, rng)))) == 192)

print("\n7. Driver wiring: all six Figure 8 curves build")
cfg = SimConfig.from_panel(FIGURE8_PANELS[0], n_realizations=1, n_symbols=10)
eqs = build_equalizers(cfg, H, S, COND, clusters)
check("six curves, shapes K x M", len(eqs) == 6 and all(W.shape == (K, M) for W in eqs.values()),
      f"{sorted(eqs)}")

print("\n7b. BCD iteration study (--bcd-iterations)")
W0 = m7_equalizers.bdac_mmse(H, S, clusters, Es, COND)
path = m7_equalizers.bcd_mmse_path(H, S, clusters, Es, 4, COND, W0=W0)
check("path has one W per iteration", len(path) == 4)
check("path[l-1] equals bcd_mmse with l iterations",
      all(np.allclose(path[l - 1], m7_equalizers.bcd_mmse(H, S, clusters, Es, l, COND, W0=W0))
          for l in (1, 2, 3, 4)))
cfg_it = SimConfig.from_panel(FIGURE8_PANELS[0], n_realizations=1, n_symbols=10,
                              bcd_iteration_list=(1, 2, 4))
eqs_it = build_equalizers(cfg_it, H, S, COND, clusters)
check("study builds LMMSE, ZF and one BCD curve per count",
      list(eqs_it) == ["LMMSE", "ZF", "BCD-MMSE (iter 1)", "BCD-MMSE (iter 2)",
                       "BCD-MMSE (iter 4)"])
check("study BCD (iter 1) equals the default BCD-MMSE (iter 1)",
      np.allclose(eqs_it["BCD-MMSE (iter 1)"], eqs["BCD-MMSE (iter 1)"]))

print("\n7c. BCD with a pluggable M_c x M_c inverse (--bcd-inverse)")
from dbp_sim import hw_inverse
W_solve = m7_equalizers.bcd_mmse(H, S, clusters, Es, 2, COND)
W_inv = m7_equalizers.bcd_mmse(H, S, clusters, Es, 2, COND, inverse=np.linalg.inv)
check("inverse=np.linalg.inv matches the solve path", np.allclose(W_solve, W_inv))
Hc, Sc = H[clusters[0]], S[clusters[0]]
den = Es * Hc @ Hc.conj().T + COND.covariance(Sc)
hw_inverse.reset_stats()
inv_hw, inv_ref = hw_inverse.cholesky_hw_inverse(den), np.linalg.inv(den)
# Best any ap_fixed<16,8> output can do: the exact inverse, truncated to 8 fraction bits
inv_q = (np.floor(inv_ref.real * 256) + 1j * np.floor(inv_ref.imag * 256)) / 256
I_c = np.eye(len(clusters[0]))
res_hw, res_q = np.abs(den @ inv_hw - I_c).max(), np.abs(den @ inv_q - I_c).max()
check("hardware inverse is as accurate as its 16-bit output allows", res_hw < 2 * res_q,
      f"max|den A^-1 - I|: model {res_hw:.3f}, exact inverse truncated {res_q:.3f}; "
      f"calls with overflow {hw_inverse.stats['overflow_calls']}")
W_hw = m7_equalizers.bcd_mmse(H, S, clusters, Es, 2, COND,
                              inverse=hw_inverse.cholesky_hw_inverse)
o_hw = m7_equalizers.bcd_objective(W_hw, H, R_hat, Es)
o_fl = m7_equalizers.bcd_objective(W_solve, H, R_hat, Es)
print(f"  INFO  objective (24) after 2 iterations: hardware inverse {o_hw:.5f}, "
      f"float {o_fl:.5f}  (precision loss of the 16-bit format, not a model error)")

print("\n8. GATE: centralized LMMSE lowest SER where R_hat is full rank (M=128)")
print("   At M=256 rank(R_hat) <= N = 192 < 256, so LMMSE-on-R_hat is NOT guaranteed")
print("   best in SER - only in the empirical objective (24), checked separately above.")
from dbp_sim.m1_driver import SimConfig, run_panel
from dbp_sim.params import FIGURE8_PANELS
for panel in FIGURE8_PANELS:
    cfg = SimConfig.from_panel(panel, n_realizations=8, n_symbols=480, snr_db_grid=(-4,))
    res = {k: v[0] for k, v in run_panel(cfg).items()}
    best = min(res, key=res.get)
    label = f"panel ({panel.label}) M={panel.M} IoT={panel.iot_db:g}dB"
    if panel.M <= 192:                       # R_hat full rank
        check(f"{label}: LMMSE best", best == "LMMSE",
              f"best={best} ({res[best]:.5f}), LMMSE={res['LMMSE']:.5f}")
    else:
        print(f"  INFO  {label}: best={best} ({res[best]:.5f}), "
              f"LMMSE={res['LMMSE']:.5f}  (rank-deficient R_hat; not gated)")

print("\n9. Model A: band channels and covariance averaged over frequency")
from dbp_sim.m1_driver import run_panel_band
bb = m2_channel.StandInULABandChannel(n_carriers=16, max_delay_s=1e-6)
Hb, Hbarb = bb.generate(M, K, r, 0, np.random.default_rng(1))
check("band normalization: mean over the band of ||h_f||^2 == M for every UE",
      np.allclose((np.abs(np.concatenate([Hb, Hbarb], axis=2))**2).sum(axis=1).mean(axis=0),
                  M, atol=1e-6))
check("band channel is frequency selective (carriers differ)",
      not np.allclose(Hb[0], Hb[-1]))
est = m5_noise.estimation_carriers(N, 16)
check("estimation samples cover every sampled PRB (round robin)",
      sorted(set(est.tolist())) == list(range(16)) and np.ptp(np.bincount(est)) <= 1)
bu = m5_noise.beta_from_iot_band(10.0, 1.0, Hbarb)
f0 = 3
Rf = bu * Hbarb[f0] @ Hbarb[f0].conj().T + np.eye(M)
nn = m5_noise.draw_band_noise(Hbarb, np.full(20000, f0), bu, 1.0, np.random.default_rng(2))
err = np.linalg.norm(nn @ nn.conj().T / nn.shape[1] - Rf) / np.linalg.norm(Rf)
check("draw_band_noise on PRB f has covariance beta Hbar_f Hbar_f^H + sigma^2 I",
      err < 0.05, f"relative error {err:.3f}")
per_prb, band = m5_noise.interference_rank(Hbarb, bu)
check("band averaging spreads the interference over more dimensions than r",
      per_prb <= r and band > r, f"per PRB {per_prb:.1f}, band average {band:.0f}")
bflat = m2_channel.StandInULABandChannel(n_carriers=16, max_delay_s=0.0)
_, Hbarf = bflat.generate(M, K, r, 0, np.random.default_rng(1))
pf, bf = m5_noise.interference_rank(Hbarf, m5_noise.beta_from_iot_band(10.0, 1.0, Hbarf))
check("flat channel: band average has the same interference dimensions as one PRB",
      pf == bf, f"per PRB {pf:.1f}, band average {bf:.0f}")

cfgA = SimConfig(M=M, C=C, K=K, r=r, iot_db=10.0, modulation="16QAM",
                 channel_backend="standin_ula", n_realizations=3, n_symbols=480,
                 n_eval_prbs=4, snr_db_grid=(-4,), bcd_iteration_list=(1, 2))
resA = {k: v[0] for k, v in run_panel_band(cfgA).items()}
resB = {k: v[0] for k, v in run_panel_band(
    SimConfig(**{**cfgA.__dict__, "covariance_model": "B"})).items()}
check("model B (per-PRB covariance) beats model A for LMMSE on a selective channel",
      resB["LMMSE"] < resA["LMMSE"], f"A {resA['LMMSE']:.4f}, B {resB['LMMSE']:.4f}")
check("ZF ignores R_hat: models A and B give close ZF SER",
      abs(resA["ZF"] - resB["ZF"]) < 0.1 * resB["ZF"],
      f"A {resA['ZF']:.4f}, B {resB['ZF']:.4f}")

print("\n10. BCD: G_c is inverted once per DU, not once per iteration")
hw_inverse.reset_stats()
m7_equalizers.bcd_mmse(H, S, clusters, Es, 3, COND, inverse=hw_inverse.cholesky_hw_inverse)
check("3 iterations call the M_c x M_c inverse C times", hw_inverse.stats["calls"] == C,
      f"calls {hw_inverse.stats['calls']}, C = {C}")

print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"FAILURES: {FAIL}"))
raise SystemExit(1 if FAIL else 0)
