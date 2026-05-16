function [H_tgt, H_itf] = generate_quadriga_channel(p)
%GENERATE_QUADRIGA_CHANNEL  One channel realisation via QuaDRiGa v2.2.0.
%
%  Matches paper Section VI-A:
%    - 3GPP 38.901 UMa, 120-degree sector, UEs at 50-100 m
%    - Per-UE LOS/NLOS by 3GPP 38.901 Table 7.4.2-1 probability
%    - Implemented by generating LOS and NLOS batches separately,
%      then selecting per-UE based on distance probability
%    - Global power normalisation: avg received power per antenna = 1
%
%  Compatible with QuaDRiGa v2.2.0 and MATLAB R2014a.

n_UE_total = p.K + p.r;
fc         = 2.0e9;
lambda     = 3e8 / fc;
h_BS       = 25.0;
h_UE       = 1.5;

%% -----------------------------------------------------------------------
%  1. Place UEs: uniform in 120-degree sector, 50-100 m
%% -----------------------------------------------------------------------
r_ue   = 50 + 50 * rand(1, n_UE_total);
phi_ue = (-60 + 120 * rand(1, n_UE_total)) * pi/180;
rx_x   = r_ue .* cos(phi_ue);
rx_y   = r_ue .* sin(phi_ue);

%% -----------------------------------------------------------------------
%  2. Compute per-UE LOS probability (3GPP TR 38.901 Table 7.4.2-1 UMa)
%% -----------------------------------------------------------------------
d_2D  = sqrt(rx_x.^2 + rx_y.^2);
P_LOS = min(18./d_2D, 1) .* (1 - exp(-d_2D/63)) + exp(-d_2D/63);
is_LOS = rand(1, n_UE_total) < P_LOS;   % 1=LOS, 0=NLOS

%% -----------------------------------------------------------------------
%  3. Generate ONE channel vector per UE using the correct scenario
%     by running two separate QuaDRiGa layouts (LOS-only, NLOS-only)
%     and then selecting columns based on is_LOS.
%% -----------------------------------------------------------------------
H_full = zeros(p.M, n_UE_total);

% Indices of LOS and NLOS UEs
idx_LOS  = find(is_LOS);
idx_NLOS = find(~is_LOS);

% Generate LOS channels if any UEs are LOS
if ~isempty(idx_LOS)
    H_los = quadriga_batch(rx_x(idx_LOS), rx_y(idx_LOS), ...
                           h_BS, h_UE, fc, lambda, p.M, ...
                           '3GPP_38.901_UMa_LOS');
    H_full(:, idx_LOS) = H_los;
end

% Generate NLOS channels if any UEs are NLOS
if ~isempty(idx_NLOS)
    H_nlos = quadriga_batch(rx_x(idx_NLOS), rx_y(idx_NLOS), ...
                            h_BS, h_UE, fc, lambda, p.M, ...
                            '3GPP_38.901_UMa_NLOS');
    H_full(:, idx_NLOS) = H_nlos;
end

%% -----------------------------------------------------------------------
%  4. Global normalisation: avg power per antenna across all UEs = 1
%% -----------------------------------------------------------------------
avg_power = mean(sum(abs(H_full).^2, 1)) / p.M;
if avg_power > 0
    H_full = H_full / sqrt(avg_power);
end

H_tgt = H_full(:, 1:p.K);
H_itf = H_full(:, p.K+1:end);
end


%% -----------------------------------------------------------------------
function H = quadriga_batch(rx_x, rx_y, h_BS, h_UE, fc, lambda, M, scenario)
%QUADRIGA_BATCH  Generate M x n_UE channel matrix for a batch of UEs
%  all sharing the same scenario string. Uses a single qd_layout call.

n_UE = numel(rx_x);

s = qd_simulation_parameters;
s.center_frequency   = fc;
s.use_3GPP_baseline  = 1;
s.show_progress_bars = 0;

l = qd_layout(s);
l.no_tx = 1;
l.tx_position = [0; 0; h_BS];

A_tx = qd_arrayant('omni');
A_tx.no_elements = M;
z_pos = ((0:M-1) - (M-1)/2) * lambda/2;
A_tx.element_position = [zeros(1,M); zeros(1,M); z_pos];
l.tx_array = A_tx;

l.no_rx = n_UE;
l.rx_position = [rx_x(:).'; rx_y(:).'; h_UE * ones(1,n_UE)];
l.rx_array = qd_arrayant('omni');

% Single scenario for all UEs in this batch — guaranteed to work
l.set_scenario(scenario);

b    = l.init_builder;
b.gen_parameters;
chan = b.get_channels;   % 1 x n_UE array of qd_channel objects

% Extract flat-fading vectors: coeff is [1 x M x n_paths x n_snap]
H = zeros(M, n_UE);
for k = 1:n_UE
    h_row   = sum(chan(k).coeff(1,:,:,1), 3);  % 1 x M
    H(:,k)  = h_row.';                          % M x 1
end
end
