% =====================================================================================
% Export QuaDriGa channels for the Figure 8 reproduction.
%
%   Zhao, Li, Wang, Song, Chang, Shi, "Efficient LMMSE Equalization for Massive MIMO
%   Systems Under Decentralized Baseband Processing Architecture", IEEE JSAC 2025.
%
% Writes one .mat per (M, K, r) config used by Figure 8:
%   H    : M x K x n_realizations   target-UE channels
%   Hbar : M x r x n_realizations   interfering-UE channels
% into ../dados/.  Then run:  .venv/bin/python quadriga/convert_quadriga_export.py
%
% Carrier: 3.5 GHz by default (FR1, n78).  Set fc_override before running for another
% carrier; the file name then carries it, e.g. channels_quadriga_M128_K8_r8_fc28GHz.mat:
%   matlab -nodisplay -r "fc_override=28e9; run('quadriga/export_quadriga_channels.m')"
% 28 GHz (FR2, n257) is the carrier of the FR2 test conditions (TDLA30-75, TDLA30-300;
% software/Restrições - Parâmetros.csv).  The same seed gives the same UE drops.
% configs_override = [M K r; ...] exports only those configurations, e.g. [256 12 8].
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
%   FLAT H     2B.4  the article's model is flat per PRB (L614) but the extraction rule
%                    is unstated.  Taken as the frequency response at one subcarrier.
%
% Normalization is deliberately NOT applied here: the Python side applies it
% (per-UE power control, params.M2_Channel.normalization) so that choice lives in
% exactly one place.  The values in cfg below are mirrored in dbp_sim/params.py
% (M2_Channel); keep both in sync.
% =====================================================================================

here = fileparts(mfilename('fullpath'));                        % .../simulador/quadriga
if isempty(here), here = pwd; end
base = fileparts(here);                                          % .../simulador
addpath(fullfile(base, 'QuaDRiGa_latest', 'quadriga_src'));     % 2A.3

cfg.scenario    = '3GPP_38.901_UMa_NLOS';   % 2A.1
cfg.center_freq = 3.5e9;                    % 2B   <-- NOT from the article
if exist('fc_override', 'var'), cfg.center_freq = fc_override; end
if cfg.center_freq == 3.5e9
    fc_tag = '';                            % original file names, unchanged
else
    fc_tag = sprintf('_fc%gGHz', cfg.center_freq/1e9);
end
cfg.bandwidth   = 20e6;                     % 2B.4 (only sets the subcarrier grid)
cfg.bs_height_m = 25;                       % 2A.4 (QuaDriGa default = UMa spec)
cfg.ue_height_m = 1.5;                      % 2A.4 (randomize_rx_positions default)
cfg.n_real      = 100;                      % L577
cfg.sector_deg  = 120;                      % L577
cfg.r_min_m     = 50;                       % L577
cfg.r_max_m     = 100;                      % L577
cfg.seed        = 0;                        % 2B (reproducibility only)

configs = [128 8 8; 256 8 8; 128 12 8];     % (M, K, r) needed by Figure 8
if exist('configs_override', 'var'), configs = configs_override; end   % e.g. [256 12 8]

fprintf('QuaDriGa %s | MATLAB %s\n', qd_simulation_parameters.version, version);
fprintf('scenario=%s  fc=%.3g Hz\n\n', cfg.scenario, cfg.center_freq);

lambda = 299792458 / cfg.center_freq;

for ci = 1:size(configs,1)
    M = configs(ci,1);  K = configs(ci,2);  r = configs(ci,3);
    n_ue = K + r;                            % interferers drawn like targets (L577)
    fprintf('=== M=%d K=%d r=%d (%d UEs) ===\n', M, K, r, n_ue);

    H    = complex(zeros(M, K, cfg.n_real));
    Hbar = complex(zeros(M, r, cfg.n_real));
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
            % flat channel = frequency response at a single subcarrier (2B.4)
            fr = c(u).fr(cfg.bandwidth, 1);            % n_rx x n_tx x 1 x n_snap
            v  = reshape(fr(1,:,1,1), [], 1);          % M x 1
            if u <= K
                H(:,u,rr) = v;
            else
                Hbar(:,u-K,rr) = v;
            end
        end

        if mod(rr,10)==0
            fprintf('  %3d/%d  (%.1f s elapsed)\n', rr, cfg.n_real, toc(t0));
        end
    end

    fn = fullfile(base, 'dados', sprintf('channels_quadriga_M%d_K%d_r%d%s.mat', M, K, r, fc_tag));
    save(fn, 'H', 'Hbar', 'cfg', '-v7');     % -v7 so scipy.io.loadmat can read it
    fprintf('  wrote %s  (%.1f s)\n\n', fn, toc(t0));
end

fprintf('Done.\n');
exit;
