%% =========================================================================
%  TABLE I: FRONTHAUL DATA RATE COMPARISON
%  Reproduces Table I of the paper (Section VI-D).
% =========================================================================
clear; clc;
addpath(genpath('.'));

% 5G NR worst-case parameters (Section VI-D)
Nsc_PRB   = 12;
NPRB      = 275;
Nu        = Nsc_PRB * NPRB;   % = 3300 subcarriers
TOFDM     = 1 / 120e3;        % symbol duration at 120 kHz SCS [s]
w         = 12;                % bit-width per element
Ncoh      = 1;                 % coherence block (1 OFDM symbol for worst case)
N         = 192;               % noise samples
r         = 8;                 % LRD rank
T_bcd     = 2;                 % BCD iterations for table

% Three scenarios from Table I
scenarios(1).M=128; scenarios(1).K=8;  scenarios(1).C=2;
scenarios(2).M=128; scenarios(2).K=8;  scenarios(2).C=4;
scenarios(3).M=256; scenarios(3).K=8;  scenarios(3).C=4;

for k = 1:3
    scenarios(k).N         = N;
    scenarios(k).r         = r;
    scenarios(k).T_bcd     = T_bcd;
    scenarios(k).Ncoh      = Ncoh;
    scenarios(k).w         = w;
    scenarios(k).Nu        = Nu;
    scenarios(k).NPRB      = NPRB;
    scenarios(k).Nsc_PRB   = Nsc_PRB;
    scenarios(k).TOFDM_inv = 1/TOFDM;
end

rate_table = fronthaul_data_rate(scenarios);
