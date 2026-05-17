function [H_tgt, H_itf] = generate_quadriga_channel(p)
%GENERATE_QUADRIGA_CHANNEL  One i.i.d. channel drop using QuaDRiGa v2.2.0.
%
%  Implements Section VI-A of Zhao et al. (2025):
%    - 3GPP 38.901 UMa scenario
%    - 120-degree sector, UEs at 50-100 m from BS
%    - Vertical ULA at BS with M half-wavelength-spaced elements
%    - LOS/NLOS assigned per UE by 3GPP 38.901 distance probability
%    - Global power normalisation: avg received power per antenna = 1
%
%  Verified API for QuaDRiGa v2.2.0 + MATLAB R2014a.
%
%  VERIFIED FACTS FROM DEBUGGING:
%    chan(k).coeff dimensions: [M_rx x M_tx x n_paths x n_snapshots]
%                            = [1    x M    x n_paths x n_snap]
%    Correct extraction: sum(chan(k).coeff(1,:,:,1), 3)  ->  1 x M
%    gen_parameters alone handles all LSF + SSF internally
%    set_scenario accepts only a single string (not cell arrays)
%    LOS/NLOS must be implemented by running two separate layouts
%    config files are in quadriga_src/config/ (NOT @qd_layout/config/)
%
%  Inputs
%    p.M : total BS antennas
%    p.K : number of target UEs
%    p.r : number of interfering UEs

n_UE_total = p.K + p.r;
fc     = 2.0e9;           % carrier frequency [Hz]
lambda = 3e8 / fc;        % wavelength [m]
h_BS   = 25.0;            % BS height [m]
h_UE   = 1.5;             % UE height [m]

%% 1. Place UEs uniformly in 120-degree sector, 50-100 m from BS
r_ue   = 50 + 50 * rand(1, n_UE_total);
phi_ue = (-60 + 120 * rand(1, n_UE_total)) * pi/180;  % R2014a: no deg2rad
rx_x   = r_ue .* cos(phi_ue);
rx_y   = r_ue .* sin(phi_ue);

%% 2. Per-UE LOS probability: 3GPP TR 38.901 Table 7.4.2-1 UMa
d_2D   = sqrt(rx_x.^2 + rx_y.^2);
P_LOS  = min(18./d_2D, 1) .* (1 - exp(-d_2D/63)) + exp(-d_2D/63);
is_LOS = rand(1, n_UE_total) < P_LOS;

%% 3. Generate channels in two batches (one scenario string each)
%    This is the only reliable way in v2.2.0 to mix LOS/NLOS per UE,
%    since set_scenario does not accept cell arrays.
H_full = zeros(p.M, n_UE_total);

idx_LOS  = find( is_LOS);
idx_NLOS = find(~is_LOS);

if ~isempty(idx_LOS)
    H_full(:, idx_LOS) = quadriga_batch( ...
        rx_x(idx_LOS), rx_y(idx_LOS), ...
        h_BS, h_UE, fc, lambda, p.M, '3GPP_38.901_UMa_LOS');
end
if ~isempty(idx_NLOS)
    H_full(:, idx_NLOS) = quadriga_batch( ...
        rx_x(idx_NLOS), rx_y(idx_NLOS), ...
        h_BS, h_UE, fc, lambda, p.M, '3GPP_38.901_UMa_NLOS');
end

%% 4. Global normalisation
%    Scale H so that average power per receive antenna = 1.
%    Preserves inter-UE power differences (near/far) while making
%    SNR = Es/sigma2 the effective operating point.
avg_power = mean(sum(abs(H_full).^2, 1)) / p.M;
if avg_power > 0
    H_full = H_full / sqrt(avg_power);
end

H_tgt = H_full(:, 1:p.K);
H_itf = H_full(:, p.K+1:end);
end


%% -----------------------------------------------------------------------
function H = quadriga_batch(rx_x, rx_y, h_BS, h_UE, fc, lambda, M, scenario)
%QUADRIGA_BATCH  Generate M x n_UE channel matrix for one scenario type.

n_UE = numel(rx_x);

%-- Simulation parameters -----------------------------------------------
s = qd_simulation_parameters;
s.center_frequency   = fc;
s.use_3GPP_baseline  = 1;   % static drop: disable spatial consistency maps
s.show_progress_bars = 0;   % suppress console output

%-- Layout --------------------------------------------------------------
l = qd_layout(s);
l.no_tx = 1;
l.tx_position = [0; 0; h_BS];

%-- BS antenna: vertical ULA, M elements, lambda/2 spacing -------------
A_tx = qd_arrayant('omni');
A_tx.no_elements = M;
z_pos = ((0:M-1) - (M-1)/2) * lambda/2;
A_tx.element_position = [zeros(1,M); zeros(1,M); z_pos];
l.tx_array = A_tx;

%-- UE antennas: single isotropic element per UE -----------------------
l.no_rx = n_UE;
l.rx_position = [rx_x(:).'; rx_y(:).'; h_UE * ones(1,n_UE)];
l.rx_array = qd_arrayant('omni');

%-- Scenario: single string — accepted by v2.2.0 set_scenario ----------
l.set_scenario(scenario);

%-- Channel generation: v2.2.0 three-step builder flow -----------------
%   Verified method names from:  disp(methods(b))
%   gen_parameters handles ALL parameter generation (LSF + SSF).
%   Calling gen_lsf_parameters or gen_ssf_parameters SEPARATELY causes
%   "existing parameters deleted" warnings because they call
%   gen_parameters internally, wiping previous results.
b    = l.init_builder;   % creates qd_builder object(s)
b.gen_parameters;        % generates all large + small scale parameters
chan = b.get_channels;   % returns 1 x n_UE array of qd_channel objects

%-- Extract flat-fading channel vectors --------------------------------
%   VERIFIED coeff dimensions in v2.2.0:
%     chan(k).coeff is [M_rx x M_tx x n_paths x n_snapshots]
%                    = [1    x M    x n_paths x n_snap]
%   M_rx=1  (single UE antenna)
%   M_tx=M  (BS ULA with M elements)
%   Extraction: take row 1 (M_rx), all columns (M_tx), sum paths (dim3),
%               snapshot 1 (dim4) -> result is 1 x M, then transpose.
H = zeros(M, n_UE);
for k = 1:n_UE
    h_row  = sum(chan(k).coeff(1, :, :, 1), 3);   % 1 x M
    H(:,k) = h_row.';                               % M x 1
end
end
