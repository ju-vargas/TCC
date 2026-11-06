"""All simulation constants for Figure 8, organised by module, with provenance.

Target article
--------------
X. Zhao, M. Li, B. Wang, E. Song, T.-H. Chang, Q. Shi, "Efficient LMMSE Equalization for
Massive MIMO Systems Under Decentralized Baseband Processing Architecture", IEEE JSAC,
DOI 10.1109/JSAC.2025.3531524.

Bare line references (``L577``) point at
``referencias/zhao2025_jsac/paper.md``.  Other sources:

    [P]    Zhao, Guan, Li, Shi, GLOBECOM 2021 (ref. [1]) - same group, earlier version
    [DBP]  referencias/DBP-master/uplink/DBP_detector_sim.m - reference code for ref. [6], other group

Conflict rule: the target article wins.  ``JSAC > [P] > [DBP]``.

Read ``simulation_parameters.md`` for the full argument behind each entry.  Run
``python -m dbp_sim.params`` to print the provenance table.
"""

from __future__ import annotations

from dataclasses import dataclass

from .provenance import Param, TIER_MEANING, STATUS_MEANING, collect

# --------------------------------------------------------------------------------------
# M1 - Monte-Carlo driver
# --------------------------------------------------------------------------------------


class M1_Driver:
    """Averaging structure and the SNR sweep."""

    n_realizations = Param(
        100, "S", "1", "L577",
        "'averaged over 100 randomly generated channel realizations'")

    n_symbols = Param(
        480, "S", "1", "L577",
        "'480 symbols are drawn independently from the 16-QAM constellation for each channel'")

    snr_db_grid = Param(
        tuple(range(-10, 11, 2)), "F", "1", "figure markers",
        "Read from marker positions on Figs. 6-8. A plotting library can decimate "
        "markers, so the simulated grid may have been finer. Range and endpoints are solid.")

    recompute_W_per_realization = Param(
        True, "D", "1", "L61, L561",
        "Implied, not stated: both lines justify reusing W across a coherence block, and "
        "the 480 symbols are exactly such a block. Spec item 2B.10.")

    rng_seed = Param(
        0, "A", "2B", "-",
        "Never stated. Any value is legitimate; fixing it makes runs reproducible. "
        "The same seed is used by quadriga/export_quadriga_channels.m (rng(seed + realization)). "
        "Spec item 2B.10.")

    test_conditions = Param(
        (("TDLA30-5", 192, 192, 3.5e9), ("TDLA30-10", 192, 192, 3.5e9),
         ("TDLA30-75", 192, 192, 28e9), ("TDLA30-300", 168, 168, 28e9),
         ("TDLC300-100", 132, 132, 3.5e9), ("TDLB100-400", 24, 39, 3.5e9),
         ("HST350", 0, 3, 3.5e9), ("HST500", 0, 3, 3.5e9)),
        "X", "3", "TCC Table tab:n-condicao (setup_simulacao.tex); TS 38.211 v18.6.0 "
        "Tabs. 6.4.1.1.3-4/-5; software/Restrições - Parâmetros.csv L12-13",
        "3GPP test conditions as (name, N worst case, N mean, carrier in Hz).\n"
        "N = noise samples per PRB inside T_c, capped at 192. K = 8 (type 1) and "
        "K = 12 (type 2) orthogonal DM-RS ports need double-symbol DM-RS (Tab. "
        "6.4.1.1.3-5); with PUSCH mapping type A over 14 symbols, l0 = 2 and "
        "dmrs-AdditionalPosition = pos1, the DM-RS symbols are 2, 3, 10, 11 (Tab. "
        "6.4.1.1.3-4), 12 REs each. For every data symbol, N is the largest number of DM-RS "
        "REs in a window of T_c symbols containing it. Worst case: the smallest value over "
        "the 14 data symbols of the slot (every symbol has at least that many). Mean: the "
        "average over the 14 symbols, rounded to the nearest integer (what a typical "
        "symbol has). Only TDLB100-400 (24 / 39) and HST (0 / 3) differ. "
        "Uplink is taken as continuous (every slot PUSCH); n78/n257 are TDD, so a real TDD "
        "pattern would lower N where T_c spans more than one slot. Best case (not run): "
        "TDLB100-400 48, HST 12. HST350/HST500 (T_c = 1 symbol): worst case N = 0, so "
        "per-T_c estimation is infeasible and they are skipped. Only the worst case is "
        "realisable by a receiver (every symbol has at least that many samples); the mean "
        "matches no symbol and is kept for reference only (--n-case mean).\n"
        "Carrier: FR1 conditions at 3.5 GHz (n78), FR2 conditions at 28 GHz (n257). The "
        "carrier matters because the UMa NLOS angular spreads depend on it (*_gamma in "
        "the .conf, log10(f_GHz) with no clamp; median ASA ~86 deg at 3.5 GHz, ~49 deg at "
        "28 GHz), which changes the spatial correlation of H and Hbar.\n"
        "Velocity enters only through T_c, hence N: the channel is block fading and flat "
        "per PRB, so Doppler and the TDL delay profiles are not modelled. Conditions with "
        "the same (N, carrier) give the same curves and are run once.")


# --------------------------------------------------------------------------------------
# M2 - Channel generation
# --------------------------------------------------------------------------------------


class M2_Channel:
    """Channel matrices H (M x K) and Hbar (M x r).

    The article uses QuaDriGa (L577), which is MATLAB-only.  Channels are generated by
    ``quadriga/export_quadriga_channels.m`` and loaded here (backend ``quadriga_file``).  The
    QuaDriGa entries below (scenario, frequency, array, ...) are the values that script
    uses; they are declared here for provenance and must be kept in sync with it.
    ``standin_ula`` is a substitute used only by ``test_dbp_sim.py``.
    """

    backend = Param(
        "quadriga_file", "A", "2B", "-",
        "The article names QuaDriGa but this is a Python port. 'quadriga_file' loads the "
        "exports of quadriga/export_quadriga_channels.m and is the path used for the results. "
        "'standin_ula' is NOT the article's channel; it exists so the tests run without "
        "MATLAB.",
        alternatives=("quadriga_file", "standin_ula"))

    quadriga_export_path = Param(
        "dados/channels_quadriga_M{M}_K{K}_r{r}.npz", "A", "2B", "-",
        "Filename pattern for the QuaDriGa exports (.npz with H (n_real, M, K) and "
        "Hbar (n_real, M, r)). Figure 8 spans three (M,K,r) configs, so the pattern is "
        "resolved per panel. Only used when backend == 'quadriga_file'.")

    # --- what the article does say about the geometry -------------------------------

    n_cells = Param(
        1, "S", "1", "L577",
        "Single cell with one BS. The export script places one tx at the origin.")

    sector_deg = Param(
        120.0, "S", "1", "L577",
        "'UEs are uniformly distributed within a 120 degree sector'")

    radius_min_m = Param(50.0, "S", "1", "L577", "'radius 50 ~ 100 m centered at BS'")
    radius_max_m = Param(100.0, "S", "1", "L577", "'radius 50 ~ 100 m centered at BS'")

    interferers_like_targets = Param(
        True, "S", "1", "L577",
        "'the non-target UEs are molded [modeled] similarly to the target UEs'. Quoted "
        "but under-determined: same sector and radius, drawn independently, may coincide "
        "in angle with a served UE? Spec item 2B.12.")

    # --- what it does not say: QuaDriGa configuration --------------------------------

    quadriga_scenario = Param(
        "3GPP_38.901_UMa_NLOS", "A", "2A", "config headers + qd_layout.m",
        "Never stated. Both UMi and UMa .conf headers declare 'Valid distance range: 10 "
        "to 5000 m', so the 50-100 m radius does not discriminate. The discriminator is "
        "'Valid BS antenna height': UMi 10 m, UMa 25 m - and qd_layout.m sets the default "
        "tx height to [0;0;25]. The article gives the UE radius but never the BS height.",
        alternatives=("3GPP_38.901_UMa_NLOS", "3GPP_38.901_UMa_LOS",
                      "3GPP_38.901_UMi_NLOS", "3GPP_38.901_UMi_LOS"))

    quadriga_version = Param(
        "2.8.1-0", "A", "2A", "QuaDRiGa_latest",
        "Never stated. v2.8.1-0 is the maintained, obtainable release. The version is "
        "recorded with every export (quadriga/quadriga_export.log).")

    center_frequency_hz = Param(
        3.5e9, "A", "2B", "quadriga/export_quadriga_channels.m",
        "Never stated, and NOT set by any .conf file. Couples to the scenario, whose "
        "*_gamma terms are frequency-dependent. 3.5 GHz chosen here; no source in the "
        "article. Must be reported.")

    bandwidth_hz = Param(
        20e6, "A", "2B", "quadriga/export_quadriga_channels.m",
        "Only sets the subcarrier grid passed to qd_channel.fr; H is read at one "
        "subcarrier (see flat_channel_extraction), so it does not change the result.")

    flat_channel_extraction = Param(
        "single_subcarrier", "A", "2B", "L614",
        "The article's model is flat per PRB (L614) but the extraction rule is unstated. "
        "H is the frequency response at the first subcarrier. Spec item 2B.4.")

    array_geometry = Param(
        "ULA, M omni elements along y, spacing lambda/2", "A", "2B",
        "quadriga/export_quadriga_channels.m",
        "Never stated: ULA vs UPA, rows x columns, element spacing, polarization, element "
        "pattern, downtilt, boresight. Chosen here: half-wavelength ULA of qd_arrayant "
        "('omni') elements; broadside is the x axis, so the 120 degree sector is centred "
        "on broadside. UEs also use one 'omni' element. Spec item 2B.2.")

    bs_height_m = Param(
        25.0, "A", "2A", "qd_layout.m default; UMa .conf header",
        "Never stated. QuaDriGa's default tx position is [0;0;25], which is also the "
        "'Valid BS antenna height' of the UMa scenario.")

    ue_height_m = Param(
        1.5, "A", "2A", "randomize_rx_positions.m default; UMa .conf header",
        "Never stated. 1.5 m is QuaDriGa's default user height and inside the UMa "
        "'Valid MT antenna height' range (1.5 to 22.5 m).")

    ue_placement = Param(
        "uniform_in_area", "A", "2B", "L577",
        "'uniformly distributed within a 120 degree sector' does not say whether the "
        "radius is uniform or the density is uniform over the area. Uniform in area is "
        "used: angle uniform in the sector, radius = sqrt(U*(rmax^2-rmin^2)+rmin^2). "
        "Spec item 2B.3.")

    independent_drops = Param(
        True, "A", "2B", "-",
        "Each of the 100 realizations draws new UE positions (rng(seed + realization) in "
        "the export script). Spec item 2B.5.")

    normalization = Param(
        "per_ue_power_control", "A", "2A", "L577 + measured A/B on real QuaDriGa channels",
        "How H and Hbar are scaled. TWO candidate conventions, and with REAL QuaDriGa "
        "channels they differ enormously - this is the single most result-determining "
        "choice in the simulator.\n"
        "  'unit_mean_entry_power' - one joint scale factor so E[|h_mk|^2] = 1 over "
        "[H Hbar], preserving the per-UE power differences the channel produced, i.e. NO "
        "uplink power control.\n"
        "  'per_ue_power_control'  - each UE column scaled to the same power, i.e. ideal "
        "closed-loop uplink power control.\n"
        "The article never mentions power control. But its own geometry (UEs uniform over "
        "a 50-100 m annulus, L577) produces a MEASURED per-UE power spread of 16.2 dB in "
        "one drop and a 13.0 dB median over 100 drops, and without power control the SER "
        "average is then dominated by the worst-placed UE.\n"
        "MEASURED A/B against the Fig. 8(a) read-off targets, real QuaDriGa channels, "
        "panel (a), SNR = -4 dB, 20 realizations (ratio = ours/target):\n"
        "  no power control : LMMSE 7.52x, BCD 3.62x, LRD 5.22x, cDR 3.67x, sDR 1.36x, "
        "ZF 0.81x  -> spread 0.8-7.5x, no consistent offset\n"
        "  power control    : LMMSE 0.57x, BCD 0.56x, LRD 0.59x, cDR 0.87x, sDR 0.31x, "
        "ZF 0.65x  -> four of six cluster at 0.56-0.65x\n"
        "A single common factor across methods means only the operating point differs, "
        "not the relative behaviour - which is what a correct normalization looks like. "
        "'per_ue_power_control' is therefore adopted. The article's SNR definition, "
        "[P] L74 and [DBP] :135 fix the scaling of the entries but say nothing about "
        "power control across UEs.",
        alternatives=("per_ue_power_control", "unit_mean_entry_power"))

    # --- substitute backend, used by the tests ----------------------------------------

    standin_angular_spread_deg = Param(
        10.0, "X", "3", "-",
        "Stand-in channel only (used by the tests). NOT from the article. Controls the "
        "per-UE angular spread of the substitute ULA channel.",
        only_if="M2_Channel.backend == 'standin_ula'")

    standin_paths_per_ue = Param(
        20, "X", "3", "-",
        "Stand-in channel only. NOT from the article.",
        only_if="M2_Channel.backend == 'standin_ula'")


# --------------------------------------------------------------------------------------
# M3 - Antenna clustering
# --------------------------------------------------------------------------------------


class M3_Clustering:
    """Partition of the M BS antennas into C clusters."""

    equal_cluster_size = Param(
        True, "S", "1", "L577, L85",
        "'each cluster has M_c = M/C antennas'")

    mapping = Param(
        "contiguous", "A", "2B", "[DBP] :305 + ref. [6] fn. 3",
        "The article states that M antennas are split into C clusters (L85) but never "
        "how. Default contiguous, on [DBP] :305 (H_c = H(S*(c-1)+1:S*c,:)) and ref. [6]'s "
        "row-wise partition with its footnote 3 ('other partitioning schemes may be "
        "possible but are not considered here'); the article's own notation "
        "H = [H_1^T,...,H_C^T]^T (L96) is the same form.\n"
        "MEASURED EFFECT on the QuaDriGa 38.901 UMa NLOS channels with per-UE power "
        "control (SER contiguous / interleaved, SNR = -4 dB): 1.07x in panel a and 1.43x "
        "in panel c (M = 256, C = 16). UMa NLOS has a rich angular spread, so the two "
        "mappings see similar local statistics. The effect grows with C.",
        alternatives=("contiguous", "interleaved"))


# --------------------------------------------------------------------------------------
# M4 - Symbol source
# --------------------------------------------------------------------------------------


class M4_Source:
    """Transmitted symbols."""

    modulation = Param(
        "16QAM", "S", "1", "L577; L608 for the QPSK panel",
        "16-QAM throughout; QPSK in Fig. 8(g). L60 mentions 16-QAM only as an 'e.g.'.",
        alternatives=("16QAM", "QPSK"))

    Es = Param(
        1.0, "D", "1", "L577, L79",
        "Free normalization: beta is tied to sigma^2 through IoT and R scales with "
        "sigma^2, so (3),(7),(15),(22),(26),(30) depend only on ratios. Setting Es = 1 "
        "with a unit-average-energy constellation is fully determined. [DBP] :94 instead "
        "derives Es from integer symbols - equivalent.")

    unit_energy_constellation = Param(
        True, "A", "2B", "-",
        "The article never states the constellation energy convention. Equivalent to any "
        "other by the Es note above. Spec item 2B.8.")


# --------------------------------------------------------------------------------------
# M5 - Colored-noise generation
# --------------------------------------------------------------------------------------


class M5_Noise:
    """Colored noise n ~ CN(0, beta*Hbar*Hbar^H + sigma^2*I)."""

    noise_model = Param(
        "CN(0, beta*Hbar*Hbar^H + sigma^2*I)", "S", "1", "L113, L577",
        "Colored noise: r interfering UEs plus white thermal noise. Built by "
        "m5_noise.noise_covariance. L577 is followed over Eq. (5).")

    snr_definition = Param(
        "Es_over_sigma2", "S", "1", "L577",
        "SNR = 10*log10(Es/sigma^2), where sigma^2 is the background AWGN power. NOTE "
        "this is a per-user TRANSMIT ratio. [DBP] :145 uses a different, receive-side "
        "per-antenna convention with an extra factor U - at K = 8 that is a 9.03 dB "
        "offset. Do not import it.")

    iot_db = Param(
        10.0, "S", "1", "L577; L593 for the 20 dB panel",
        "'IoT = 10 dB is a default setting in the simulation'. Fig. 8(f) uses 20 dB.",
        alternatives=(10.0, 20.0))

    beta_convention = Param(
        "realised_per_antenna", "D", "2A", "L577 + [P] L207",
        "The article defines IoT = 10*log10((beta + N_0)/sigma^2) and never defines N_0. "
        "[P] L207 measures SNR as 'Es/N0' with its Fig. 4 axis labelled Es/N0 (dB), so "
        "N_0 is the group's symbol for thermal-noise power = the article's sigma^2; "
        "corroborated by ref. [6]'s MMSE regulariser N_0/(2Es). That gives "
        "beta = sigma^2*(10^(IoT/10) - 1). BUT beta is the per-UE interferer power, while "
        "the per-antenna interference power is beta*(Hbar Hbar^H)_mm ~ beta*r. We "
        "therefore scale beta so the REALISED per-antenna interference-to-thermal ratio "
        "equals IoT, i.e. beta = sigma^2*(10^(IoT/10) - 1)*M/||Hbar||_F^2. Under the M2 "
        "normalization that is beta = sigma^2*(10^(IoT/10) - 1)/r. Taking the formula "
        "literally instead would realise ~18.6 dB at IoT = 10 dB, r = 8.",
        alternatives=("realised_per_antenna", "literal_formula"))

    n_noise_samples = Param(
        192, "S", "1", "L577, L640",
        "Default N = 192 pilot REs used to estimate the covariance, as in the article. "
        "[P] L54 notes N is 'typically 96 or 192'. Runs per 3GPP test condition override "
        "it with M1_Driver.test_conditions (N = 12 to 192).")

    data_noise_independent = Param(
        True, "A", "2B", "-",
        "Are the 480 data-symbol noise draws independent of the N estimation "
        "samples? Never stated, and it DECIDES THE CURVE ORDERING: with independent draws "
        "and no regularisation, extra BCD iterations make SER worse and BDAC becomes the "
        "best equaliser - the opposite of Fig. 6. True (independent) is the physically "
        "honest reading; combine it with M6.epsilon > 0. Spec item 2B.9.")

    resample_noise_per_realization = Param(
        True, "A", "2B", "-",
        "Are the N estimation samples redrawn for each channel realization? Implied yes "
        "since Hbar changes, but never stated. Spec item 2B.9.")


# --------------------------------------------------------------------------------------
# M6 - Covariance estimation
# --------------------------------------------------------------------------------------


class M6_Covariance:
    """Sample covariance and its conditioning."""

    estimator = Param(
        "sample_mean", "S", "1", "Eq. (6), L119",
        "R_hat = (1/N) sum_i n^i (n^i)^H; local blocks R_hat_cc likewise (L125). "
        "Footnote 5 (L822) then makes no distinction between R_hat and R.")

    shrinkage = Param(
        "ledoit_wolf", "A", "2A", "Ledoit & Wolf (2004), J. Multivariate Analysis 88(2)",
        "How R_hat is made invertible. The article never says - a search for regulari*, "
        "diagonal load*, epsilon, ill-condition*, condition number, pseudo-inverse, Moore, "
        "Penrose, pinv, numerical stab*, rank-defic*, shrinkage, ridge, damping returns no "
        "relevant hit, and [P] has none either.\n"
        "But SOME conditioning is FORCED by the article's own equations: Eq. (3) requires "
        "R^-1, footnote 5 (L822) directs that R_hat be used as R, and rank(R_hat) <= N = "
        "192 < 256 = M. The published M = 256 panels cannot exist without it.\n"
        "Ledoit-Wolf is chosen because its shrinkage intensity rho is computed from the "
        "samples in closed form, so it introduces NO free parameter - the conditioning "
        "question is answered by a citable standard estimator (tier 2A) rather than an "
        "invented constant. Report it as 'the article does not specify how R_hat is conditioned; "
        "this work uses Ledoit-Wolf shrinkage'.\n"
        "Alternative not adopted - fixed diagonal loading eps*(tr A/dim)*I: that scale is set "
        "by the LARGEST eigenvalues, so on this covariance (r = 8 interference eigenvalues "
        "over a sigma^2 floor) it swamps the floor. Measured: at IoT = 10 dB the loading is "
        "1.0x the smallest eigenvalue, at 20 dB it is 10.1x - and at 20 dB centralized "
        "LMMSE loses the optimality Eq. (3) guarantees. The workable eps window is "
        "[0.1, 0.5] at IoT = 10 dB but [0.01, 0.03] at 20 dB: no single value serves "
        "both. Selectable via mode='fixed' for sweeps.",
        alternatives=("ledoit_wolf", "fixed", "none"))

    fixed_epsilon = Param(
        0.1, "X", "3", "-",
        "Only used when shrinkage == 'fixed'. NOT from the article, and not adopted - "
        "see the shrinkage note. Available for sweeps.",
        only_if="M6_Covariance.shrinkage == 'fixed'")


# --------------------------------------------------------------------------------------
# M7 - Equalizers
# --------------------------------------------------------------------------------------


class M7_Equalizers:
    """The six curves plotted in Figure 8, plus the BDAC initialiser."""

    curves = Param(
        ("LMMSE", "ZF", "BCD-MMSE (iter 1)", "BCD-MMSE LRD (iter 4)", "sDR-MMSE",
         "cDR-MMSE"), "S", "1", "L581, Fig. 8",
        "The six curves of Figure 8.")

    perfect_csi = Param(
        True, "S", "1", "L63, fn. 2 (L817)",
        "The equalizers receive the true H; channel estimation is out of scope.")

    bcd_iterations = Param(
        1, "S", "1", "L591",
        "'we run the BCD-MMSE and the BCD-MMSE (LRD) equalizers for one and four "
        "iterations, respectively' - Fig. 8 only. Figs. 6-7 plot iterations 1-4.")

    lrd_iterations = Param(
        4, "S", "1", "L591", "Same sentence as above.")

    bcd_inverse = Param(
        "float", "X", "3", "-",
        "How the M_c x M_c matrix of the BCD-MMSE update (Eq. 30) is inverted. 'float' "
        "solves in double precision; 'cholesky_hw' uses the bit-exact model of this "
        "work's fixed-point Cholesky inverter (hardware/golden_cholesky.py, "
        "ap_fixed<16,8>, no input scaling). The article does not discuss arithmetic "
        "precision.",
        alternatives=("cholesky_hw",),
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_int_bits = Param(
        8, "X", "3", "-",
        "Integer bits, sign included, of the data type of the 'cholesky_hw' inverse "
        "(fixed_t in hardware/cholesky_hardware/cholesky.h).",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_frac_bits = Param(
        8, "X", "3", "-",
        "Fractional bits of the data type of the 'cholesky_hw' inverse.",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_acc_int_bits = Param(
        None, "X", "3", "-",
        "Integer bits of the accumulator (acc_fixed_t). None = twice hw_int_bits, as in "
        "cholesky.h.",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_acc_frac_bits = Param(
        None, "X", "3", "-",
        "Fractional bits of the accumulator. None = twice hw_frac_bits.",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_quant = Param(
        "AP_TRN", "X", "3", "-",
        "Quantization mode of the fractional part of the data type (ap_q_mode).",
        alternatives=("AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF",
                      "AP_RND_INF", "AP_RND_CONV"),
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_overflow = Param(
        "AP_SAT", "X", "3", "-",
        "Overflow mode of the integer part of the data type (ap_o_mode, N = 0).",
        alternatives=("AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM"),
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_acc_quant = Param(
        None, "X", "3", "-",
        "Quantization mode of the accumulator. None = same as hw_quant.",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_acc_overflow = Param(
        None, "X", "3", "-",
        "Overflow mode of the accumulator. None = same as hw_overflow.",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    hw_intermediates = Param(
        (), "X", "3", "-",
        "Intermediate types of the 'cholesky_hw' inverse (cholesky.h: CHOL_MULIN_*, "
        "CHOL_PROD_*, CHOL_CMUL_*, CHOL_NUM_*, CHOL_NORM_*, CHOL_QUOT_*, CHOL_SUM_*, "
        "CHOL_SQRT_*), as (name, (int_bits, frac_bits, quant, overflow)) pairs. Empty "
        "= the cholesky.h defaults, which reproduce the hardware without intermediate "
        "types.",
        only_if="M7_Equalizers.bcd_inverse == 'cholesky_hw'")

    lrd_rank = Param(
        8, "S", "1", "L587, L591",
        "'we set r = K for the LRD algorithm'. L587: 'the value of r is selected as the "
        "number of non-target UEs'. Note the article's separate remark that the noise "
        "covariance is 'approximately low-rank' (L577) justifies the LRD APPROXIMATION, "
        "not this value.")

    compression_dim = Param(
        "K", "D", "1", "L150, L184, L593",
        "L150 states only L_c = L ('for brevity'); L = K follows from Q_c in C^{K x M_c} "
        "(L184) and is confirmed by L593.")

    zf_form = Param(
        "pinv", "A", "2B", "L581",
        "The article lists centralized ZF as a baseline but never writes the formula. "
        "W_ZF = (H^H H)^-1 H^H is the standard reading. Spec item 2B.8.")

    bcd_update_rule = Param(
        "gauss_seidel", "S", "1", "L398, fn. 6 (L450)",
        "Sequential c = 1..C with the ring convention A_0^l = A_C^(l-1).")


# --------------------------------------------------------------------------------------
# M8 - Detection and metric
# --------------------------------------------------------------------------------------


class M8_Metric:
    """Slicing and the error metric."""

    detection = Param(
        "nearest_neighbour", "S", "1", "L79",
        "'the detector quantizes each entry of s_hat to the nearest neighbor point in the "
        "constellation set'.")

    bias_removal = Param(
        False, "A", "2B", "-",
        "The article says only 'quantize to the nearest neighbour point'. MMSE estimates "
        "are biased and removing the bias is common practice; it changes SER. The article "
        "states nothing - searched, no hit. Spec item 2B.11.")

    metric = Param(
        "SER", "S", "1", "L581",
        "Symbol error rate. Note [P] reports uncoded BER instead - a conflict resolved in "
        "favour of the target article.")


# --------------------------------------------------------------------------------------
# Figure 8 panel configurations
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Panel:
    """One sub-figure of Figure 8."""

    label: str
    M: int
    C: int
    K: int
    r: int
    iot_db: float
    modulation: str
    note: str = ""


#: Sub-captions give M and C (status F); K = 12, IoT = 20 dB and QPSK are also stated in
#: the text (L593, L608).  Panel (d) is absent from the extracted figure and never cited
#: anywhere in the article - its configuration is unrecoverable and is NOT guessed here.
FIGURE8_PANELS: tuple[Panel, ...] = (
    Panel("a", M=128, C=8,  K=8,  r=8,  iot_db=10.0, modulation="16QAM"),
    Panel("b", M=256, C=8,  K=8,  r=8,  iot_db=10.0, modulation="16QAM"),
    Panel("c", M=256, C=16, K=8,  r=8,  iot_db=10.0, modulation="16QAM"),
    # Panel("d", ...) - UNRECOVERABLE, deliberately omitted.
    Panel("e", M=128, C=8,  K=12, r=8,  iot_db=10.0, modulation="16QAM",
          note="r is NOT stated for this panel. L577 ties r to K ('both set to K = 8') "
               "but panel (e) raises only K. r = 8 kept here; r = 12 is equally "
               "defensible. Spec item 2B.6."),
    Panel("f", M=128, C=8,  K=8,  r=8,  iot_db=20.0, modulation="16QAM"),
    Panel("g", M=128, C=8,  K=8,  r=8,  iot_db=10.0, modulation="QPSK"),
)

#: Panel label -> configuration number in the TCC text (Table tab:paineis in
#: TCC/chapters/RESULTADOS/setup_simulacao.tex). The figures use these numbers.
#: Ordered by (M, C), then modulation (M = 128 only), then K, then IoT. The labels are only
#: stable names for files and results: "a"-"g" are the Fig. 8 panels and "7"-"16" are the
#: extra configurations in the order they were created, NOT their TCC numbers.
TCC_CONFIGURATION: dict[str, int] = {
    "a": 1, "f": 2, "e": 3, "7": 4,             # M = 128, C = 8, 16-QAM
    "g": 5, "15": 6, "14": 7, "16": 8,          # M = 128, C = 8, QPSK
    "b": 9, "9": 10, "8": 11, "10": 12,         # M = 256, C = 8
    "c": 13, "12": 14, "11": 15, "13": 16,      # M = 256, C = 16
    "17": 17, "18": 18, "19": 19, "20": 20,     # M = 256, C = 8, QPSK (QPSK_256_PANELS)
    "21": 21, "22": 22, "23": 23, "24": 24,     # M = 256, C = 16, QPSK (QPSK_256_PANELS)
}

#: Extra configurations of the TCC (Table tab:paineis): the four (M, C, modulation) bases
#: of panels a, b, c and g, crossed with K = 8 or 12 and IoT = 10 or 20 dB, minus the
#: combinations already in Figure 8. Not in the article. K = 8 and 12 are the maximum
#: orthogonal DM-RS ports of types 1 and 2 (TS 38.211 Tab. 6.4.1.1.3-5); IoT = 20 dB is
#: the article's Fig. 8(f) value. r = 8 throughout, as in panel e. Labels are not the TCC
#: numbers (see TCC_CONFIGURATION).
EXTRA_PANELS: tuple[Panel, ...] = (
    Panel("7",  M=128, C=8,  K=12, r=8, iot_db=20.0, modulation="16QAM"),
    Panel("8",  M=256, C=8,  K=12, r=8, iot_db=10.0, modulation="16QAM"),
    Panel("9",  M=256, C=8,  K=8,  r=8, iot_db=20.0, modulation="16QAM"),
    Panel("10", M=256, C=8,  K=12, r=8, iot_db=20.0, modulation="16QAM"),
    Panel("11", M=256, C=16, K=12, r=8, iot_db=10.0, modulation="16QAM"),
    Panel("12", M=256, C=16, K=8,  r=8, iot_db=20.0, modulation="16QAM"),
    Panel("13", M=256, C=16, K=12, r=8, iot_db=20.0, modulation="16QAM"),
    Panel("14", M=128, C=8,  K=12, r=8, iot_db=10.0, modulation="QPSK"),
    Panel("15", M=128, C=8,  K=8,  r=8, iot_db=20.0, modulation="QPSK"),
    Panel("16", M=128, C=8,  K=12, r=8, iot_db=20.0, modulation="QPSK"),
)

#: Every configuration of the TCC, in its numbering order.
ALL_PANELS: tuple[Panel, ...] = tuple(sorted(FIGURE8_PANELS + EXTRA_PANELS,
                                             key=lambda p: TCC_CONFIGURATION[p.label]))

#: QPSK in the two M = 256 bases (configurations 17 to 24), so that every (M, C) group has
#: both modulations: same K, IoT and r as configurations 9 to 16, in the same order. Only
#: for the format sweep [4] (software/testes/varredura4_v5_qpsk.sh); kept out of ALL_PANELS
#: so that the 16 configurations of the text, their tables and figures stay as they are.
QPSK_256_PANELS: tuple[Panel, ...] = tuple(
    Panel(str(17 + i + 4 * g), M=256, C=C, K=K, r=8, iot_db=iot, modulation="QPSK")
    for g, C in enumerate((8, 16)) for i, (K, iot) in enumerate(
        ((8, 10.0), (8, 20.0), (12, 10.0), (12, 20.0))))

#: Every panel by label, the 16 configurations and QPSK_256_PANELS.
PANELS_BY_LABEL: dict[str, Panel] = {p.label: p for p in ALL_PANELS + QPSK_256_PANELS}


#: Read from Fig. 8(a) at SNR = -4 dB (status F, +-30% - see spec 1.5).  Used only as an
#: order-of-magnitude sanity target, never as a fit objective.
FIG8A_TARGETS_AT_MINUS4DB = {
    "LMMSE": 0.023,
    "BCD-MMSE (iter 1)": 0.055,
    "BCD-MMSE LRD (iter 4)": 0.033,
    "cDR-MMSE": 0.065,
    "sDR-MMSE": 0.16,
    "ZF": 0.62,
}


MODULES = (M1_Driver, M2_Channel, M3_Clustering, M4_Source,
           M5_Noise, M6_Covariance, M7_Equalizers, M8_Metric)


# --------------------------------------------------------------------------------------
# Provenance report
# --------------------------------------------------------------------------------------


def provenance_table() -> str:
    """Render every parameter with its status, tier and source."""
    lines = ["", "=" * 100, "PARAMETER PROVENANCE", "=" * 100, ""]
    for tag, meaning in STATUS_MEANING.items():
        lines.append(f"  {tag}  {meaning}")
    lines.append("")
    for tag, meaning in TIER_MEANING.items():
        lines.append(f"  tier {tag:3s} {meaning}")
    lines.append("")

    counts: dict[str, int] = {}
    for mod in MODULES:
        lines.append("-" * 100)
        lines.append(f"{mod.__name__}  -  {(mod.__doc__ or '').strip().splitlines()[0]}")
        lines.append("-" * 100)
        for name, p in collect(mod).items():
            counts[p.status] = counts.get(p.status, 0) + 1
            flag = ("  <<< ASSUMPTION" if p.status == "X" and not p.only_if
                    else "  (only if " + p.only_if + ")" if p.only_if else "")
            lines.append(f"  {name:34s} = {str(p.value):<26s} [{p.status}/{p.tier}] "
                         f"{p.source}{flag}")
        lines.append("")

    lines.append("=" * 100)
    lines.append("  counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    active_x = [f"{m.__name__}.{n}" for m in MODULES
                for n, pp in collect(m).items() if pp.status == "X" and not pp.only_if]
    cond_x = [(f"{m.__name__}.{n}", pp.only_if) for m in MODULES
              for n, pp in collect(m).items() if pp.status == "X" and pp.only_if]
    lines.append(f"  X in force in the default configuration: {len(active_x)}"
                 + (f"  -> {', '.join(active_x)}" if active_x else "  (none)"))
    for name, cond in cond_x:
        lines.append(f"    conditional X: {name}   only when {cond}")
    lines.append("=" * 100)
    return "\n".join(lines)


def assumptions() -> list[tuple[str, str, Param]]:
    """Every parameter that is not simply stated by the article."""
    out = []
    for mod in MODULES:
        for name, p in collect(mod).items():
            if p.status != "S":
                out.append((mod.__name__, name, p))
    return out


if __name__ == "__main__":       # pragma: no cover
    print(provenance_table())
    print("\nNon-stated parameters (everything requiring a decision):\n")
    for mod, name, p in assumptions():
        print(f"  [{p.status}/{p.tier}] {mod}.{name}")
