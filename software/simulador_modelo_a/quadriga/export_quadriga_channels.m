% =====================================================================================
% Export QuaDriGa channels over the band, for the model-A simulator.
%
% Same drops as ../../simulador/quadriga/export_quadriga_channels.m (same scenario, fc,
% array, layout and seeds).  The only change is the frequency axis: instead of one
% subcarrier, the frequency response is taken at n_carriers points equally spaced over
% the band, one per sampled PRB.  Carrier 1 is f0 in both scripts, so carrier 1 here
% must equal the single-carrier export (checked by convert_quadriga_export.py).
%
% Model A (Zhao footnote 4, paper.md:821): the noise covariance is estimated by
% averaging over frequency, so H and Hbar are needed across the band.
%
%   Zhao, Li, Wang, Song, Chang, Shi, "Efficient LMMSE Equalization for Massive MIMO
%   Systems Under Decentralized Baseband Processing Architecture", IEEE JSAC 2025.
%
% Writes one .mat per (M, K, r) config used by Figure 8:
%   H    : M x K x n_carriers x n_realizations   target-UE channels   (single)
%   Hbar : M x r x n_carriers x n_realizations   interfering-UE channels (single)
% into ../dados/channels_quadriga_mc_*.mat.  Then run:  .venv/bin/python quadriga/convert_quadriga_export.py
%
% -------------------------------------------------------------------------------------
% PROVENANCE  (full argument in simulation_parameters.md)
%
% Stated by the article (L577): 100 realizations; UEs uniform in a 120 deg sector,
%   radius 50-100 m, BS at centre; K target + r interfering UEs, interferers "modeled
%   similarly"; M = 128 or 256; QuaDriGa as generator with large- and small-scale fading.
%
% NOT stated - chosen here:
%   SCENARIO   2A.1  UMi and UMa .conf both declare "valid distance 10-5000 m", so the
%                    50-100 m radius does not discriminate.  The discriminator is the
%                    header's "Valid BS antenna height": UMi 10 m vs UMa 25 m, and
%                    qd_layout's default tx height is 25 m -> UMa.
%   VERSION    2A.3  v2.8.1 (maintained release, runs on this MATLAB).
%   FREQUENCY  2B    never stated, not set by any .conf.  REPORT THIS VALUE.
%   ARRAY      2B    never stated.  Half-wavelength ULA, vertically polarised omni.
%   FLAT H     2B.4  the article's model is flat per PRB (L614).  One frequency
%                    response point per sampled PRB.
%   BAND       A.1   NOT from the article.  100 MHz, the upper end of mid-band NR
%                    channels (Lin & Lee, 5G and Beyond, ch. 1: mid-band 1-7 GHz,
%                    50-100 MHz).  Table I of the article implies 120 kHz SCS and
%                    275 PRBs (FR2), which does not match fc = 3.5 GHz.
%   CARRIERS   A.2   NOT from the article.  64 points equally spaced over the band
%                    (one per sampled PRB, 1.5625 MHz apart), to keep the files small.
%
% Normalization is deliberately NOT applied here: the Python side applies it
% (per-UE power control, params.M2_Channel.normalization) so that choice lives in
% exactly one place.  The values in cfg below are mirrored in dbp_sim/params.py
% (M2_Channel); keep both in sync.
% =====================================================================================

here = fileparts(mfilename('fullpath'));                        % .../simulador/quadriga
if isempty(here), here = pwd; end
base = fileparts(here);                                          % .../simulador_modelo_a
addpath(fullfile(fileparts(base), 'simulador', 'QuaDRiGa_latest', 'quadriga_src'));  % 2A.3

cfg.scenario    = '3GPP_38.901_UMa_NLOS';   % 2A.1
cfg.center_freq = 3.5e9;                    % 2B   <-- NOT from the article
cfg.bandwidth   = 100e6;                    % A.1  <-- NOT from the article
cfg.n_carriers  = 64;                       % A.2  <-- NOT from the article
cfg.bs_height_m = 25;                       % 2A.4 (QuaDriGa default = UMa spec)
cfg.ue_height_m = 1.5;                      % 2A.4 (randomize_rx_positions default)
cfg.n_real      = 100;                      % L577
cfg.sector_deg  = 120;                      % L577
cfg.r_min_m     = 50;                       % L577
cfg.r_max_m     = 100;                      % L577
cfg.seed        = 0;                        % 2B (reproducibility only)

configs = [128 8 8; 256 8 8; 128 12 8];     % (M, K, r) needed by Figure 8

fprintf('QuaDriGa %s | MATLAB %s\n', qd_simulation_parameters.version, version);
fprintf('scenario=%s  fc=%.3g Hz\n\n', cfg.scenario, cfg.center_freq);

lambda = 299792458 / cfg.center_freq;

for ci = 1:size(configs,1)
    M = configs(ci,1);  K = configs(ci,2);  r = configs(ci,3);
    n_ue = K + r;                            % interferers drawn like targets (L577)
    fprintf('=== M=%d K=%d r=%d (%d UEs) ===\n', M, K, r, n_ue);

    H    = complex(zeros(M, K, cfg.n_carriers, cfg.n_real, 'single'));
    Hbar = complex(zeros(M, r, cfg.n_carriers, cfg.n_real, 'single'));
    t0 = tic;

    for rr = 1:cfg.n_real
        rng(cfg.seed + rr);                  % independent drop per realization (2B.5)

        s = qd_simulation_parameters;
        s.center_frequency   = cfg.center_freq;
        s.show_progress_bars = 0;
        s.use_absolute_delays = 0;

        l = qd_layout(s);
        l.tx_position = [0; 0; cfg.bs_height_m];

        a = qd_arrayant('omni');             % 2B: half-wavelength ULA along y
        a.no_elements = M;
        a.element_position = [zeros(1,M); ((0:M-1)-(M-1)/2)*lambda/2; zeros(1,M)];
        l.tx_array = a;

        l.no_rx = n_ue;
        l.rx_array = qd_arrayant('omni');

        % uniform in AREA over the annulus, uniform in angle over the sector (L577)
        ang = (rand(1,n_ue) - 0.5) * cfg.sector_deg * pi/180;
        rad = sqrt(rand(1,n_ue)*(cfg.r_max_m^2 - cfg.r_min_m^2) + cfg.r_min_m^2);
        pos = [rad.*cos(ang); rad.*sin(ang); repmat(cfg.ue_height_m,1,n_ue)];
        for u = 1:n_ue
            l.rx_track(1,u).initial_position = pos(:,u);
        end
        l.set_scenario(cfg.scenario);

        c = l.get_channels();

        for u = 1:n_ue
            % one flat channel per sampled PRB (2B.4, A.2); carrier 1 = f0
            fr = c(u).fr(cfg.bandwidth, cfg.n_carriers);   % n_rx x n_tx x n_carr x n_snap
            v  = single(reshape(fr(1,:,:,1), M, cfg.n_carriers));   % M x n_carr
            if u <= K
                H(:,u,:,rr) = reshape(v, M, 1, cfg.n_carriers);
            else
                Hbar(:,u-K,:,rr) = reshape(v, M, 1, cfg.n_carriers);
            end
        end

        if mod(rr,10)==0
            fprintf('  %3d/%d  (%.1f s elapsed)\n', rr, cfg.n_real, toc(t0));
        end
    end

    fn = fullfile(base, 'dados', sprintf('channels_quadriga_mc_M%d_K%d_r%d.mat', M, K, r));
    save(fn, 'H', 'Hbar', 'cfg', '-v7');     % -v7 so scipy.io.loadmat can read it
    fprintf('  wrote %s  (%.1f s)\n\n', fn, toc(t0));
end

fprintf('Done.\n');
exit;
