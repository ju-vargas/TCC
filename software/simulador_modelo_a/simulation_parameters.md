> **Simulador modelo A:** este arquivo descreve o simulador original (modelo B). Os parâmetros novos do modelo A estão em `dbp_sim/params.py` (`covariance_model`, `bandwidth_hz`, `n_carriers`, `estimation_spread`, `n_eval_prbs`) e em `README.md`.

# Simulator Replication Spec

**Target article:** X. Zhao, M. Li, B. Wang, E. Song, T.-H. Chang, Q. Shi, *"Efficient LMMSE
Equalization for Massive MIMO Systems Under Decentralized Baseband Processing Architecture"*,
IEEE JSAC, DOI `10.1109/JSAC.2025.3531524`.

Every value below is also declared in `dbp_sim/params.py` as a `Param(value, status, tier,
source, note)` record. The two must match.

## Sources and precedence

| Mark | Source | Weight |
| :-- | :-- | :-- |
| *(bare, e.g. `L577`)* | The target article, `referencias/zhao2025_jsac/paper.md` | authoritative |
| `[P]` | Zhao, Guan, Li, Shi, GLOBECOM 2021 (ref. [1] at L753, "an earlier version", L11). `referencias/zhao2021_globecom/bf0a85d1-….md` | same group, different paper (metric: uncoded BER) |
| `[DBP]` | `referencias/DBP-master/` — MATLAB code released for K. Li *et al.*, JETCAS 2017 (ref. [6]). Cited as `[DBP] uplink/DBP_detector_sim.m:135` | different group; field convention only |

**Conflict rule:** the target article wins. `JSAC > [P] > [DBP]`. A `[P]`/`[DBP]` value may fill a
gap the article leaves open, never override something it states.

## Status tags

| Tag | Meaning |
| :-- | :-- |
| **S** | Stated in the article |
| **D** | Derived from the article's own equations |
| **F** | Read from a figure |
| **A** | Absent — needed, not supplied |
| **X** | **Introduced by this analysis; no counterpart in the article. Never cite as the paper's** |

## Tiers

**1** — the article states it. **2A** — the article forces it, a value is justifiable from external
evidence. **2B** — the article forces it, nothing pins it: declare it. **3** — the article does not
force it; an assumption. **No tier-3 parameter is in force in the default configuration.**

## Verdict

Curve-for-curve reproduction is not achievable from the article alone. Order-of-magnitude
reproduction of Fig. 8 is, and Tier 1 alone reproduces Table I exactly. The Tier 2 channel choices
govern *where curves sit on the SNR axis*; the conditioning of `R̂` (2A.6) governs *their relative
ordering* — without it centralized LMMSE stops being the best curve.

## Default configuration

| Item | Value |
| :-- | :-- |
| Channel | QuaDriGa v2.8.1-0 exports, `3GPP_38.901_UMa_NLOS`, 3.5 GHz |
| Normalization | per-UE power control |
| Cluster mapping | contiguous |
| Conditioning of `R̂` | Ledoit–Wolf shrinkage |
| Monte Carlo | 100 realizations × 480 symbols, seed 0 |
| Result used in the TCC | `results/20260810-203348_quadriga_file_pc` (log `run_final.log` in the same folder) |

---

# TIER 1 — Stated in the article

> **Tier 1 is not entirely assumption-free.** Three classes of entry below carry judgement:
>
> * **`F`-tagged rows are inferences from images, not statements.** The SNR grid (−10:2:10 dB) is
>   read from *marker positions*; a plotting library can decimate markers, so the simulated grid may
>   be finer. The Fig. 8(a) targets carry ±30 %.
> * **The Table I `×2` rule (§1.4) is empirical.** It reproduces all twelve published entries, but
>   its justification is unknown.
> * **Some quoted phrases do not determine an implementation.** "Interferers modeled similarly to the
>   target UEs" and "quantize to the nearest neighbour point" are stated *and* under-determined —
>   tracked as 2B.12 and 2B.11.

## 1.1 System parameters

| Symbol | Meaning | Value | Status | Source | `params.py` |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `M` | BS antennas | 128 or 256 | S | L577 | `Panel.M` |
| `C` | Clusters / DUs | 8 or 16 (SER figs); 2 or 4 (Table I) | S | L577, L601 | `Panel.C` |
| `M_c` | Antennas per cluster | `M/C`, equal | S | L577, L85 | `M3_Clustering.equal_cluster_size` |
| `K` | Target UEs (single-antenna) | 8; **12** in Fig. 8(e) | S | L577; L593 | `Panel.K` |
| `r` | Interfering UEs | 8 — "both set to K = 8" | S | L577 | `Panel.r` |
| `N` | Noise samples for covariance | 192 | S | L577, L640 | `M5_Noise.n_noise_samples` |
| `IoT` | Interference over thermal | 10 dB; **20 dB** in Fig. 8(f) | S | L577; L593 | `Panel.iot_db` |
| `SNR` | Definition | `10·log10(E_s/σ²)` | S | L577 | `M5_Noise.snr_definition` |
| `E_s`, `σ²` | — | `E_s = 1`, `σ² = 10^(−SNR/10)` (only ratios enter (3),(7),(15),(22),(26),(30)) | D | L577, L79 | `M4_Source.Es` |
| — | Modulation | 16-QAM; **QPSK** in Fig. 8(g) | S | L577; L608 | `Panel.modulation` |
| — | Monte Carlo | 100 channel realizations × 480 symbols | S | L577 | `M1_Driver.n_realizations`, `n_symbols` |
| — | SNR sweep | −10 : 2 : 10 dB | F | figure markers | `M1_Driver.snr_db_grid` |
| — | SER axis | 1e−4 … 1e0 | F | figure axes | — |
| — | CSI | perfect `H`; channel estimation out of scope | S | L63, fn 2 (L817) | `M7_Equalizers.perfect_csi` |
| — | Cell | single cell, one BS | S | L577 | `M2_Channel.n_cells` |
| — | UE placement | uniform, 120° sector, radius 50–100 m, BS at centre | S | L577 | `M2_Channel.sector_deg`, `radius_min_m`, `radius_max_m` |
| — | Interferer placement | "modeled similarly to the target UEs" — under-determined, see 2B.12 | S | L577 | `M2_Channel.interferers_like_targets` |
| — | Colored noise | `n ~ CN(0, β·H̄H̄ᴴ + σ²I)` | S | L113, L577 | `M5_Noise.noise_model` |
| — | Covariance | `R̂ = (1/N)Σ nⁱ(nⁱ)ᴴ`; blocks `R̂_cc = (1/N)Σ n_c^i(n_c^i)ᴴ` | S | Eq. (6) L119, L125 | `M6_Covariance.estimator` |
| — | `R̂` vs `R` | no distinction made after Eq. (6) | S | fn 5 (L822) | — |
| — | Covariance rank | "approximately low-rank" — justifies the LRD *approximation*, **not** the value of `r` | S | L577; `r` from L587 | — |
| — | Dimension regime | `min{M,N} > M_c > K` — **not** `N > M` | S | L552 | — |
| — | Detection / metric | nearest-neighbour slicing / SER — scaling/bias step unspecified, see 2B.11 | S | L79, L581 | `M8_Metric.detection`, `metric` |
| — | Decision count | 100 × 480 × 8 = 384 000 → SER floor ≈ 2.6e−6 | D | matches the 1e−4 floor plotted | — |

## 1.2 Per-figure configuration

| Figure | `M` | `C` | `K` | IoT | Mod. | Curves |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 6(a)(b)(c) | 128/256/256 | 8/8/16 | 8 | 10 dB | 16-QAM | MMSE, ZF, BDAC, BCD iter 1–4, MMSE(AWGN) |
| 7(a)(b)(c) | 128/256/256 | 8/8/16 | 8 | 10 dB | 16-QAM | LMMSE, ZF, BDAC, BCD(LRD) iter 1–4 |
| 8(a) | 128 | 8 | 8 | 10 dB | 16-QAM | LMMSE, ZF, BCD **iter 1**, BCD(LRD) **iter 4**, sDR, cDR |
| 8(b) | 256 | 8 | 8 | 10 dB | 16-QAM | idem |
| 8(c) | 256 | 16 | 8 | 10 dB | 16-QAM | idem |
| **8(d)** | — | — | — | — | — | **absent from the figure and never cited in the text; not simulated** |
| 8(e) | 128 | 8 | **12** | 10 dB | 16-QAM | idem |
| 8(f) | 128 | 8 | 8 | **20 dB** | 16-QAM | idem |
| 8(g) | 128 | 8 | 8 | 10 dB | **QPSK** | idem |

Per-panel `M`/`C` come from the figure **sub-captions** (status **F**); `K = 12`, IoT = 20 dB and
QPSK are also stated in the text (L593, L608). In code: `FIGURE8_PANELS` in `params.py`.

Iteration counts: Figs. 6–7 plot 1–4; **Fig. 8 uses BCD = 1, LRD = 4** (L591); Table I uses `T = 2`
(L640). LRD rank `r = K = 8` (L587, L591). In code: `M7_Equalizers.bcd_iterations`,
`lrd_iterations`, `lrd_rank`.

## 1.3 Equalizers

| # | Method | Specification | Source |
| :-- | :-- | :-- | :-- |
| 1 | Centralized LMMSE | `W = (Hᴴ R⁻¹ H + (1/E_s)I)⁻¹ Hᴴ R⁻¹` | Eq. (3), L75 |
| 2 | Centralized ZF | **form not written out** — see 2B.8 | L581 |
| 3 | MMSE(AWGN) | `(HᴴH + (σ_0²/E_s)I)⁻¹Hᴴ` — not plotted in Fig. 8 | fn 3 (L819) |
| 4 | BDAC-MMSE | `(Σ_c H_cᴴR_cc⁻¹H_c + (1/E_s)I)⁻¹·[H_1ᴴR_11⁻¹, …]` | Eq. (7), L136 |
| 5 | sDR-MMSE | Alg. 1; `Q_c = H_cᴴR_cc⁻¹`; (13),(14),(15),(16) | L216–L256 |
| 6 | cDR-MMSE | Alg. 2; (19),(20)–(21),(22),(23) | L271–L337, L344–L357 |
| 7 | BCD-MMSE | Alg. 3; init `W⁰`=(7); updates (30),(28) L442,(29) L444; Gauss–Seidel `c=1..C`; ring `A_0^l ≡ A_C^{l−1}` | L407–L436, L504, fn 6 |
| 8 | BCD-MMSE (LRD) | Alg. 4, then Alg. 3 with `N → G`; `G = argmin_{rank≤r}‖R−GGᴴ‖_F² = NṼ` | L509–L529, Eqs. (31),(34) |

Figure 8 plots six of them (`M7_Equalizers.curves`): LMMSE, ZF, BCD-MMSE (iter 1), BCD-MMSE LRD
(iter 4), sDR-MMSE, cDR-MMSE.

Compression dimension **`L = K`** — status **D**: L150 states only `L_c = L` ("for brevity"); `L = K`
follows from `Q_c ∈ ℂ^{K×M_c}` (L184) and is confirmed by L593. `W` is computed once per
(realization, SNR) and reused across the 480 symbols — status **D**: L61 and L561 both justify reuse
across a coherence block, and the 480 symbols are exactly such a block.

## 1.4 Fronthaul model — reproduces Table I exactly

`w = 12`, `N_u = 3300`, `N_PRB = 275`, `N_sc,PRB = 12`, `T_OFDM = 1/120 kHz`, `N = 192`, `r = 8`,
`T = 2` (L640). `R_form = w·S_A·N_PRB/T_OFDM`, `R_fil = w·S_s·N_u/T_OFDM`, `R_total = R_form + R_fil` (L619, L631, L637).
`N_coh` is never assigned; the OFDM framing implies `N_coh = N_u/N_PRB = 12` (D).

Transfer sizes (L563–L571): centralized `2M(N_coh+K+N)/N_coh`; DR `2CK(N_coh+K+N)/N_coh`;
BCD `C(4K²+2NK)/N_coh + 2TCK(N+K)/N_coh + 2CK`;
LRD `((C−1)Mr+4CNr)/N_coh + C(4K²+2Kr)/N_coh + 2TCK(r+K)/N_coh + 2CK`.

> **To reproduce Table I: evaluate the formulas at `w = 12` with sizes in real entries, then
> multiply by 2.** Eleven of twelve entries match exactly; the twelfth (C-MMSE, `M=256`) gives 85.967
> against a printed 85.98, a rounding artifact in the article. The factor 2 is exactly 2.0000 for all
> four methods despite structurally different size expressions, so it is a global counting
> convention; its origin is not recoverable.

## 1.5 Fig. 8(a) targets — the order-of-magnitude reference

Read at **SNR = −4 dB**, `M = 128`, `C = 8`, `K = 8`, IoT = 10 dB, 16-QAM (status F):

| LMMSE | BCD it1 | BCD(LRD) it4 | cDR | sDR | ZF |
| --: | --: | --: | --: | --: | --: |
| 0.023 | 0.055 | 0.033 | 0.065 | 0.16 | 0.62 |

> Read by eye off a log axis in a compressed raster: accurate to roughly **±30 %** (≈ ±1 dB
> horizontally). Adequate as an order-of-magnitude target; not adequate for any quantitative
> agreement claim.

---

# TIER 2 — Forced by the article; value from external evidence

## 2A — Justifiable

| ID | Parameter | **Adopted** | Basis | `params.py` |
| :-- | :-- | :-- | :-- | :-- |
| 2A.1 | QuaDriGa scenario | **`3GPP_38.901_UMa_NLOS`** | Note A | `M2_Channel.quadriga_scenario` |
| 2A.2 | Channel normalization | **Per-UE power control**: every column of `H` and `H̄` scaled to `E[\|h_mk\|²] = 1` | Note B | `M2_Channel.normalization` |
| 2A.3 | QuaDriGa version | **v2.8.1-0** (`QuaDRiGa_latest`) | Note C | `M2_Channel.quadriga_version` |
| 2A.4 | Engine settings; BS / UE height | QuaDriGa defaults: `use_3GPP_baseline = false`, `autocorrelation_function = 'Comb300'`, `use_absolute_delays = false`, `use_random_initial_phase = true`, `sample_density = 2.5`; **BS 25 m, UE 1.5 m** | Article silent; QuaDriGa defaults (`qd_layout.m`, `randomize_rx_positions.m`); heights inside the UMa `.conf` valid ranges | `M2_Channel.bs_height_m`, `ue_height_m` |
| 2A.5 | `β` from IoT | **`β = σ²(10^(IoT/10) − 1) · M/‖H̄‖_F²`** = `σ²(10^(IoT/10) − 1)/r` under 2A.2 | Note D | `M5_Noise.beta_convention` |
| 2A.6 | Conditioning of `R̂` | **Ledoit–Wolf shrinkage** | Note E | `M6_Covariance.shrinkage` |

**Note A — scenario.** Choosing a `.conf` fixes ~60 statistical parameters at once (`DS_*`, `AS_*`,
`ES_*`, `KF_*`, `SF_sigma`, decorrelation distances, cross-correlations, `NumClusters`,
`NumSubPaths`, `PerCluster*`, `XPR_*`, and the full `PL_*` model). No `.conf` sets
`center_frequency`, any `qd_arrayant` property, any position, or `sample_density`.
Both `UMi_NLOS.conf` and `UMa_NLOS.conf` declare "Valid distance range: 10 to 5000 m", so the
article's 50–100 m radius does **not** discriminate. The discriminator is the header's "Valid BS
antenna height": **UMi 10 m, UMa 25 m** — and `qd_layout.m` sets `Ptx_track.initial_position =
[0;0;25]`, i.e. QuaDriGa's default BS height is 25 m, the UMa value. The article specifies the UE
radius but never the BS height, so the default is the likely value.
Values of the adopted scenario: 21 clusters, 20 sub-paths per cluster, shadow-fading STD 6 dB;
valid range 0.5–100 GHz, 10–5000 m, BS 25 m, MT 1.5–22.5 m.
Sensitivity axis: `3GPP_38.901_UMi_NLOS` (10 m) and the `_LOS` variants.

**Note B — normalization.** `SNR = 10·log10(E_s/σ²)` (L577) is transmit-side; error rate is
governed by post-equalization SINR, so the offset is the channel gain. Two conventions are
possible: a **joint** scale preserving per-UE power differences (no power control), or **per-UE**
scaling (ideal uplink power control).

The article's geometry forces the issue: UEs uniform over a 50–100 m annulus (L577) produce a
**measured 16.2 dB per-UE power spread** in one drop, **13.0 dB median over 100 drops** (max
22.2 dB). Without power control the SER average is dominated by the worst-placed UE.

Measured against the Fig. 8(a) targets (panel (a), SNR = −4 dB, 20 realizations,
ratio = ours/target):

| | LMMSE | BCD it1 | LRD it4 | cDR | sDR | ZF |
| :-- | --: | --: | --: | --: | --: | --: |
| no power control | 7.52× | 3.62× | 5.22× | 3.67× | 1.36× | 0.81× |
| **per-UE power control** | **0.57×** | **0.56×** | **0.59×** | 0.87× | 0.31× | 0.65× |

Without power control the ratios span 0.8–7.5× with no pattern. With it, four of six cluster at
**0.56–0.65×** — a single common factor across methods, meaning only the operating point differs,
not the relative behaviour. The article never mentions power control, so this is a stated,
evidence-backed assumption. The joint convention stays selectable (`--normalization
unit_mean_entry_power`).

**Note C — version.** v2.8.1-0 is the maintained, obtainable release. Record
`qd_simulation_parameters.version` with every export (`quadriga/quadriga_export.log`).

**Note D — `β`.** `IoT = 10·log10((β + N_0)/σ²)` (L577), and `N_0` is defined nowhere in the
article. `[P]` measures SNR as "**Es/N0**" (`[P] L207`) with Fig. 4's axis literally `Es/N0 (dB)`, so
`N_0` is the group's symbol for thermal-noise power — the quantity the JSAC calls `σ²`. Corroborated
by ref. [6]'s MMSE regularizer `N₀/(2E_s)`. This gives `β = σ²(10^(IoT/10) − 1)`. But `β` is the
per-UE interferer power, while the per-antenna interference power is `β·(H̄H̄ᴴ)_mm ≈ β·r`. `β` is
therefore scaled so the **realised** per-antenna interference-to-thermal ratio equals IoT:
`β = σ²(10^(IoT/10) − 1)·M/‖H̄‖_F²`. Under 2A.2 this is `σ²(10^(IoT/10) − 1)/r`. Taking the formula
literally would realise ≈ 18.6 dB at IoT = 10 dB, r = 8 (convention `literal_formula`).

**Note E — conditioning of `R̂`.** Some conditioning is *forced* by the article's own equations:
Eq. (3) requires `R⁻¹`; fn 5 (L822) directs that `R̂` be used as `R`; and
`rank(R̂) ≤ N = 192 < 256 = M`. The `M = 256` panels cannot be computed without it.

*Which rule is not stated.* A search of `paper.md` for `regulari*`, `diagonal load*`, `epsilon`,
`ill-condition*`, `condition number`, `pseudo-inverse`, `Moore`, `Penrose`, `pinv`,
`numerical stab*`, `rank-defic*`, `shrinkage`, `ridge`, `damping` returns no relevant hit — every
match is "singular *values*" in the SVD/LRD derivation (L532, L540, L544), "invertible matrix
**P**" in Theorem 1 (L180, L676), or "Cambridge" in the bibliography. `[P]` likewise has none. The
article's only regularization is Eq. (3)'s `(1/E_s)·I`, which conditions the **`K×K`** matrix
`HᴴR⁻¹H` rather than the `M×M` inverse, and Eq. (30)'s rank-`K` `E_s·H_cH_cᴴ` term.

*Adopted: Ledoit & Wolf (2004), J. Multivariate Analysis 88(2).* `R̂ → (1−ρ)R̂ + ρ·(tr R̂/M)·I`,
where `ρ` has a closed form computed from the samples. Because `ρ` is *estimated rather than
chosen*, this introduces **no free parameter**. It selects `ρ = 0.042` at IoT = 10 dB and `0.035`
at 20 dB. Report it as *"the article does not specify how `R̂` is conditioned; this work uses
Ledoit–Wolf shrinkage."*

*Alternative not adopted: fixed diagonal loading* `λ = ε·tr(A)/dim`. The loading scales with the
**largest** eigenvalues. Here `R = β·H̄H̄ᴴ + σ²I` has `r = 8` large interference eigenvalues over a
`σ²` floor, so the loading tracks the interference, not the floor it is meant to protect:

| IoT | cond(R) | λ / σ² | λ / λ_min |
| --: | --: | --: | --: |
| 10 dB | 243 | 0.97 | 0.97 |
| 20 dB | 2659 | 10.09 | **10.09** |

At IoT = 20 dB the loading is 10× the eigenvalues LMMSE must exploit, and centralized LMMSE stops
being the best equalizer — violating the optimality Eq. (3) guarantees. Measured on panel (f),
SNR = −4 dB:

| `ε` | LMMSE | cDR | LMMSE best? |
| --: | --: | --: | :-- |
| 0.00 | 0.148 | 0.184 | yes |
| 0.01 | 0.038 | 0.173 | yes |
| 0.03 | 0.051 | 0.156 | yes |
| 0.10 | 0.183 | 0.134 | **no** |

The workable `ε` window depends on IoT — `[0.1, 0.5]` at 10 dB, `[0.01, 0.03]` at 20 dB, with no
overlap — so no single constant serves both. Fixed loading stays selectable (`--shrinkage fixed
--epsilon …`, `M6_Covariance.fixed_epsilon`).

## 2B — Forced but arbitrary: declared

| ID | Parameter | **Adopted** | Notes | `params.py` |
| :-- | :-- | :-- | :-- | :-- |
| 2B.1 | Antenna → cluster mapping | **contiguous** | `[DBP] :305` and ref. [6] fn 3; the article's notation `H = [H_1ᵀ,…,H_Cᵀ]ᵀ` (L96) has the same form. Measured effect vs interleaved: **1.07×** (panel a), **1.43×** (panel c, `M=256, C=16`); grows with `C` | `M3_Clustering.mapping` |
| 2B.2 | Array geometry | **ULA, `M` omni elements along y, spacing `λ/2`; 120° sector centred on broadside (x axis); one omni element per UE** | `M = 128/256` admits several factorizations; the article gives no element pattern, polarization, downtilt or boresight | `M2_Channel.array_geometry` |
| 2B.3 | UE placement rule | **uniform in area**: angle uniform in the sector, radius `√(U·(r_max²−r_min²)+r_min²)` | `[P]` uses a deterministic 10° grid, which conflicts with the article (Defect 4) | `M2_Channel.ue_placement` |
| 2B.4 | CIR → flat `H` | **frequency response at one subcarrier**, bandwidth 20 MHz (only sets the subcarrier grid) | Model is flat per PRB (L614); extraction unstated | `M2_Channel.flat_channel_extraction`, `bandwidth_hz` |
| 2B.5 | 100 realizations | **independent drops**: new UE positions per realization (`rng(seed + realization)`) | L577 vs L614 | `M2_Channel.independent_drops` |
| 2B.6 | `r` in Fig. 8(e) when `K = 12` | **8** | L577 ties `r` to `K`; panel (e) raises only `K`. `r = 12` is equally defensible. Also sets the LRD rank | `FIGURE8_PANELS` |
| 2B.7 | `σ_0²` in MMSE(AWGN) | **open** — not needed for Fig. 8 | Background `σ²` only, or total noise power? | — |
| 2B.8 | ZF form; constellation energy | **`W = (HᴴH)⁻¹Hᴴ`; unit average energy** | `[DBP] :94` derives `E_s` from integer symbols — equivalent, only ratios enter | `M7_Equalizers.zf_form`, `M4_Source.unit_energy_constellation` |
| 2B.9 | Noise-sample policy | **data noise independent of the 192 estimation samples; samples redrawn per realization** | The physically honest reading; requires the conditioning of 2A.6 | `M5_Noise.data_noise_independent`, `resample_noise_per_realization` |
| 2B.10 | RNG seed | **0**, shared by the QuaDriGa export and the Python driver | Reproducibility only | `M1_Driver.rng_seed` |
| 2B.11 | Scaling / bias removal before slicing | **none** | The article says only "quantize … to the nearest neighbour point" (L79). MMSE estimates are biased; removing the bias would change SER | `M8_Metric.bias_removal` |
| 2B.12 | "Interferers modeled similarly to the target UEs" (L577) | **same sector and radius, same placement rule, drawn independently** | An interferer may coincide in angle with a target UE; that interference is essentially un-nullable | `M2_Channel.interferers_like_targets` |
| 2B.13 | Carrier frequency | **3.5 GHz** | Not set by any `.conf`; couples to the scenario's frequency-dependent terms. No source in the article | `M2_Channel.center_frequency_hz` |

---

# TIER 3 — Assumptions

No tier-3 parameter is in force in the default configuration. Three **X** records exist in
`params.py`; each applies only to a non-default option:

| Record | Active only when |
| :-- | :-- |
| `M2_Channel.standin_angular_spread_deg` | `backend == 'standin_ula'` (substitute channel used by the tests) |
| `M2_Channel.standin_paths_per_ue` | ” |
| `M6_Covariance.fixed_epsilon` | `shrinkage == 'fixed'` |

`python run_figure8.py --provenance` reports this directly.

---

# Known defects in the article

| # | Defect |
| :-- | :-- |
| 1 | **Table I prose vs numbers.** L640 claims 23 % / 44 % / 37 % of C-MMSE. The table gives 12.49/36.55/28.55, 25.01/73.13/58.96, 12.50/36.56/32.31 %. The DR ratio is `CK/M` **exactly** — `w`, `N_coh`, `N_PRB`, `N_u`, `T_OFDM` and the factor 2 all cancel — giving 12.5/25/12.5 % under *any* constants. "23 %" is unrecoverable. **Table I is authoritative** |
| 2 | `w = 12` vs the tabulated rates: exactly 2× (§1.4) |
| 3 | `N_0` never defined; externally resolved via `[P]` (2A.5) |
| 4 | **UE placement conflicts with `[P]`**: "uniformly distributed within a 120° sector" (L577) vs "evenly scattered with an interval of 10 degrees on an arc" (`[P] L207`). 16 UEs on a 10° grid span 150° > 120°. **Article wins** |
| 5 | `N_coh` used throughout Section V-B, never assigned (recoverable as 12) |
| 6 | "Single-cell" (L577) vs interference "from neighbouring cells" (L33, L105), with interferers then placed like the served users |
| 7 | Eq. (5) builds noise as `H̄s̄ + n̄`; L577 draws it from `CN(0, βH̄H̄ᴴ+σ²I)`. **Follow L577** |
| 8 | Fig. 8 lettered (a)(b)(c)(e)(f)(g) — no (d), never cited |
| 9 | Eq. (3) needs `R⁻¹`, fn 5 mandates `R = R̂`, and `R̂` is singular at `M = 256`. Both cannot hold in half the panels |
| 10 | **`N ≫ K` is the wrong sufficiency condition.** L123 and fn 5 justify `R̂`'s accuracy by `N ≫ K` (192 ≫ 8); an `M×M` covariance needs `N ≫ M`, and 192 < 256. L552 states only `min{M,N} > M_c > K`; `[P] L192` likewise states only `N > M_c` and `N > K`. The condition the *centralized baseline* needs is stated nowhere |
| 11 | Convergence claim: "2 to 3 iterations" (L585) matches ref. [6] nearly verbatim, while the group's own `[P] L209` reports "4 to 5" for the same algorithm |

---

# Implementation notes

**Ordering is reproducible; the SNR axis is not.** All equalizers consume the same `(H, R̂, E_s)`,
so any channel change moves them identically. The ordering is pointwise and distribution-free:
`E_sDR ⪰ E_cDR` (Appendix B, a range-space argument); BCD's objective is non-increasing (Theorem 2,
L463; proof L465); BCD ≤ BDAC by construction (BDAC is `W⁰`); LMMSE lower-bounds all ((3) minimizes
(2)). Rescaling `H` by `α` and `σ²` by `α²` changes nothing. The abscissa, by contrast, is set by
the channel gains and the scenario's effect on conditioning — i.e. by Tier 2.
*Limits:* adjacent pairs with no governing theorem may swap (BCD vs cDR, "comparable" L593; ZF vs
MMSE(AWGN), "close" L585); LRD-above-BCD in Fig. 8 follows from the stated 4-vs-1 iteration
counts; only the sign of the gaps reproduces, not their size.

**`[DBP]` conventions.** `N0 = par.U*par.Es*10^(-SNRdB/10)` (`[DBP] :145`) is a receive-side
per-antenna SNR; the article's is per-user transmit. At `K = 8` the factor `U` is a **9.03 dB**
offset on every curve, so it is not used. Its ADMM/CG detectors, white noise and `CHEST='on'` are
outside the article's model.

**Module map.**

```
M1 Monte-Carlo driver                                        [Tier 1 + 2B.10]
   └─ M2 Channel (QuaDriGa exports)     ──► H, H̄             [Tier 2A/2B]
        └─ M3 Antenna clustering        ──► H_c, y_c, n_c    [Tier 1 + 2B.1]
   └─ M4 Symbol source                  ──► s, 480/real.     [Tier 1]
   └─ M5 Colored-noise generation       ──► n, {n^i}         [Tier 1 + 2A.5 + 2B.9]
        └─ M6 Covariance estimation     ──► R̂, {R̂_cc}       [Tier 1 + 2A.6]
   └─ M7 Equalizers                     ──► W                [Tier 1 + 2B.8]
   └─ M8 Detection & SER                ──► SER(SNR)         [Tier 1 + 2B.11]
M9 Fronthaul calculator (independent of M1–M8)               [Tier 1, exact]
```

---

# Running

**Files.**

| Path | Role |
| :-- | :-- |
| `dbp_sim/` | The simulator, one file per module; `params.py` holds every constant |
| `run_figure8.py` | Entry point; writes to `results/<UTC timestamp>_<channel>_<tag>/` |
| `test_dbp_sim.py` | Correctness checks |
| `requirements.txt` | Python packages (numpy, scipy, matplotlib) |
| `quadriga/export_quadriga_channels.m` | Generates `H`, `H̄` in QuaDriGa (MATLAB) → `dados/channels_quadriga_M*_K*_r*.mat` |
| `quadriga/convert_quadriga_export.py` | `dados/*.mat` → `dados/*.npz`, carrying the export's `cfg` as metadata |
| `quadriga/quadriga_export.log` | Log of the export (QuaDriGa version, scenario, frequency) |
| `dados/channels_quadriga_M*_K*_r*.npz` | The channels used by the simulator (three `(M, K, r)` configs) |
| `results/<run>/` | Figure, CSV, JSON and, for the run used in the TCC, `run_final.log` |
| `referencias/` | `zhao2025_jsac/paper.md` (target article), `zhao2021_globecom/` (`[P]`), `li2017_jetcas/` (ref. [6]), `DBP-master/` (`[DBP]`) |
| `QuaDRiGa_latest/` | QuaDriGa v2.8.1 (git submodule) |

**Pipeline.**

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt  # once
matlab -nodisplay -nosplash -r "run('quadriga/export_quadriga_channels.m')"   # ~15 min, writes dados/*.mat
.venv/bin/python quadriga/convert_quadriga_export.py                          # dados/*.mat -> dados/*.npz
.venv/bin/python run_figure8.py                                      # all panels
.venv/bin/python test_dbp_sim.py
```

`python run_figure8.py --provenance` prints the parameter table; `--panels a` runs one panel;
`--quick` runs a reduced Monte Carlo; `--mapping`, `--normalization`, `--shrinkage`, `--epsilon`
and `--channel` override the open choices.

`--bcd-iterations 1,2,3,4` runs the BCD-MMSE iteration study: only LMMSE, ZF and one BCD-MMSE
curve per iteration count (at most four), all from the same BDAC-MMSE start. One BCD run gives
every count (`m7_equalizers.bcd_mmse_path`). Output: `bcd_iterations.png/.pdf`,
`bcd_iterations_data.csv` and `bcd_iterations_results.json` in
`results/<stamp>_<channel>_<tag>_bcdit1-2-3-4/`.

**Verification.** `test_dbp_sim.py` checks properties the article *proves* rather than numbers it
reports: Theorem 2 (objective (24) monotonically decreasing), Proposition 1 (`MSE(sDR) ≥ MSE(cDR)`),
LMMSE minimising (24) among all equalizers, LMMSE best in every panel, and that no routine inverts
more than the article permits.

**Reporting.** Report as a qualitative replication. Reproducible: curve ordering, BCD convergence in
a few iterations, trends with `M`, `C`, `K`, IoT, order-of-magnitude SER. Not reproducible: absolute
SNR offsets and gap sizes.

**Where the unresolved values might be found** (outside the article — label anything imported):
ref. [1] `[P]`; ref. [6] and `github.com/VIP-Group/DBP`; ref. [20] Zhao *et al.*, TSP 71, 2023;
corresponding author Q. Shi, `shiqj@tongji.edu.cn` (L16).
