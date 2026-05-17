%% =========================================================================
%  EXPORT QUADRIGA CHANNELS TO .MAT FILE
%  Generates N_mc channel realisations using QuaDRiGa v2.2.0 and saves
%  them to a .mat file for use in the Python simulator.
%
%  Usage:
%    1. Open MATLAB, navigate to massive_mimo_dbp/
%    2. Run this script
%    3. Use the exported .mat file in Python:
%       python main.py fig8a --channel mat_file --mat_file channels_fig8a.mat
% =========================================================================
clear; clc; close all;
rng(42);  % reproducibility

addpath(genpath('.'));

%% ---- Select scenario ---------------------------------------------------
fig_select = 'fig8a';   % Change this to export other scenarios

%% ---- Parameters (must match Python config.py) --------------------------
p.N_mc      = 100;
p.IoT_dB    = 10;
p.mod       = '16QAM';
p.Es        = 1;
p.r         = 8;

switch fig_select
    case 'fig6',  p.M=128; p.C=8;  p.K=8;
    case 'fig7',  p.M=128; p.C=8;  p.K=8;
    case 'fig8a', p.M=128; p.C=8;  p.K=8;
    case 'fig8b', p.M=256; p.C=8;  p.K=8;
    case 'fig8c', p.M=256; p.C=16; p.K=8;
    case 'fig8e', p.M=128; p.C=8;  p.K=12;
    case 'fig8f', p.M=128; p.C=8;  p.K=8;  p.IoT_dB=20;
    case 'fig8g', p.M=128; p.C=8;  p.K=8;  p.mod='QPSK';
    otherwise,    error('Unknown fig_select: %s', fig_select);
end
p.Mc = p.M / p.C;

fprintf('=== Exporting QuaDRiGa channels: %s | M=%d C=%d K=%d r=%d ===\n', ...
        fig_select, p.M, p.C, p.K, p.r);

%% ---- Generate and store channels --------------------------------------
H_tgt_all = zeros(p.M, p.K, p.N_mc);
H_itf_all = zeros(p.M, p.r, p.N_mc);

fprintf('Progress: ');
for mc = 1:p.N_mc
    if mod(mc, 10) == 0
        fprintf('%d/%d ', mc, p.N_mc);
    end
    [H_tgt, H_itf] = generate_quadriga_channel(p);
    H_tgt_all(:, :, mc) = H_tgt;
    H_itf_all(:, :, mc) = H_itf;
end
fprintf('\nDone generating.\n');

%% ---- Save to .mat file -------------------------------------------------
out_file = sprintf('channels_%s_M%d_C%d_K%d.mat', fig_select, p.M, p.C, p.K);

% Save with metadata for the Python loader
save(out_file, 'H_tgt_all', 'H_itf_all', ...
     'fig_select', 'p', '-v7');
%  -v7 ensures compatibility with scipy.io.loadmat

fprintf('Saved %d channel realisations to: %s\n', p.N_mc, out_file);
fprintf('Size: H_tgt_all = [%d x %d x %d], H_itf_all = [%d x %d x %d]\n', ...
        size(H_tgt_all), size(H_itf_all));
fprintf('\nTo use in Python:\n');
fprintf('  python main.py %s --channel mat_file --mat_file %s\n', ...
        fig_select, out_file);
