%% =========================================================================
%  MAIN SIMULATION SCRIPT
%  "Efficient LMMSE Equalization for Massive MIMO Systems Under
%   Decentralized Baseband Processing Architecture"
%  Zhao et al., IEEE JSAC, Vol. 43, No. 3, March 2025
%
%  Replicates Figures 6, 7, and 8 (SER vs SNR).
%  Uses i.i.d. Rayleigh fading instead of QuaDRiGa.
% =========================================================================
clear; clc; close all;
rng(42);  % reproducibility

addpath(genpath('.'));

%% ---- Select which figure to reproduce --------------------------------
% 'fig6'  -> BCD-MMSE iterations 1-4,  panel (a): M=128, C=8
%            Change p.M/p.C below for panels (b) M=256 C=8, (c) M=256 C=16
% 'fig7'  -> BCD-MMSE(LRD) iterations 1-4, panel (a): M=128, C=8
% 'fig8a' -> All equalizers, M=128, C=8,  K=8
% 'fig8b' -> All equalizers, M=256, C=8,  K=8
% 'fig8c' -> All equalizers, M=256, C=16, K=8
% 'fig8e' -> All equalizers, M=128, C=8,  K=12
% 'fig8f' -> All equalizers, M=128, C=8,  K=8,  IoT=20 dB
% 'fig8g' -> All equalizers, M=128, C=8,  K=8,  QPSK
fig_select = 'fig8a';

%% ---- Base parameters (Section VI-A) -----------------------------------
p.SNR_dB    = -10:2:10;   % SNR sweep [dB]
p.N_samples = 192;        % noise samples for covariance estimation
p.N_sym     = 480;        % transmitted symbols per channel realisation
p.N_mc      = 100;        % Monte Carlo channel realisations
p.IoT_dB    = 10;         % interference-over-thermal [dB] (default)
p.T_bcd     = 4;          % max BCD iterations
p.mod       = '16QAM';    % modulation: '16QAM' or 'QPSK'
p.Es        = 1;          % symbol energy (normalised)

% Number of non-target (interfering) UEs — fixed at 8 in ALL scenarios
% Paper Section VI-A: "The number of target and non-target UEs is both
% set to K = 8". For fig8e K_target becomes 12 but r stays 8.
p.r = 8;

%% ---- Scenario-specific overrides -------------------------------------
switch fig_select
    case 'fig6',  p.M=128; p.C=8;  p.K=8;
    case 'fig7',  p.M=128; p.C=8;  p.K=8;
    case 'fig8a', p.M=128; p.C=8;  p.K=8;
    case 'fig8b', p.M=256; p.C=8;  p.K=8;
    case 'fig8c', p.M=256; p.C=16; p.K=8;
    case 'fig8e', p.M=128; p.C=8;  p.K=12;  % r stays 8 (set above)
    case 'fig8f', p.M=128; p.C=8;  p.K=8;   p.IoT_dB=20;
    case 'fig8g', p.M=128; p.C=8;  p.K=8;   p.mod='QPSK';
    otherwise,    error('Unknown fig_select: %s', fig_select);
end
p.Mc = p.M / p.C;   % antennas per cluster

fprintf('=== Simulation: %s | M=%d C=%d K=%d r=%d IoT=%ddB mod=%s ===\n', ...
        fig_select, p.M, p.C, p.K, p.r, p.IoT_dB, p.mod);

%% ---- Constellation ----------------------------------------------------
[p.const, p.bpS] = get_constellation(p.mod);

%% ---- Run SER sweep ----------------------------------------------------
SER = run_ser_sweep(p, fig_select);

%% ---- Plot results -----------------------------------------------------
plot_results(SER, p.SNR_dB, fig_select, p);
