function rate_table = fronthaul_data_rate(p_scenarios)
%FRONTHAUL_DATA_RATE  Compute total fronthaul data rates (Table I).
%
%  Replicates Table I of the paper for given system parameter scenarios.
%
%  p_scenarios : array of structs, each with fields:
%    .M, .K, .C, .N, .r, .T_bcd, .Ncoh, .w, .Nu, .NPRB,
%    .Nsc_PRB, .TOFDM_inv  (1/TOFDM in Hz)
%
%  rate_table : struct array with .CentralMMSE .DR_MMSE .BCD_MMSE .BCD_LRD
%               all in Tbps

fprintf('\n%s\n', repmat('=',1,65));
fprintf('%-20s %10s %10s %10s %10s\n', ...
        'Scenario', 'C-MMSE', 'DR-MMSE', 'BCD-MMSE', 'BCD-LRD');
fprintf('%s\n', repmat('-',1,65));

rate_table = struct();

for k = 1:numel(p_scenarios)
    q      = p_scenarios(k);
    M      = q.M;   K = q.K;   C = q.C;
    N      = q.N;   r = q.r;
    T      = q.T_bcd;
    Ncoh   = q.Ncoh;
    w      = q.w;
    Nu     = q.Nu;
    NPRB   = q.NPRB;
    TOFDM_inv = q.TOFDM_inv;   % = 1/TOFDM  [Hz]

    % Number of real entries (complex -> x2 for real + imag)
    re = @(x) 2*x;

    %% Centralised MMSE: transfer H (M x K), y (M x 1), N_samp (M x N)
    %  Average over coherence block:
    %  SA_cmmse = M*K + M*N  (formulation)
    %  Ss_cmmse = M          (filtering, per symbol)
    SA_cmmse  = re(M*K + M*N);
    Ss_cmmse  = re(M);
    R_form_c  = w * SA_cmmse * NPRB / (Ncoh * TOFDM_inv^(-1));
    % Correct formula from paper: R_total = w*SA*NPRB/TOFDM
    % (bits per OFDM symbol duration, not per second — re-check units)
    % Paper evaluates: total bits / TOFDM, expressed in Tbps
    % R_form [bps] = w * SA * NPRB / TOFDM
    % R_fil  [bps] = w * Ss * Nu  / TOFDM
    TOFDM     = 1 / TOFDM_inv;   % [s]
    R_form_c  = w * SA_cmmse * NPRB / TOFDM;      % bps
    R_fil_c   = w * Ss_cmmse * Nu  / TOFDM;        % bps
    R_cmmse   = (R_form_c + R_fil_c) / 1e12;       % Tbps

    %% DR-MMSE (sDR or cDR — same communication):
    %  Each DU sends: Qc*Hc (K x K), {Qc*n^i_c} (K x N), Qc*yc (K x 1)
    %  Total formulation: C * (K^2 + K*N)   [complex entries]
    %  Total filtering:   C * K              [complex entries per symbol]
    SA_dr    = re(C * (K^2 + K*N));
    Ss_dr    = re(C * K);
    R_form_dr = w * SA_dr * NPRB / TOFDM;
    R_fil_dr  = w * Ss_dr * Nu   / TOFDM;
    R_dr      = (R_form_dr + R_fil_dr) / 1e12;

    %% BCD-MMSE:
    %  Preprocessing (BDAC): C*(K^2)  (Gram matrices)
    %  Per BCD iteration: C*(K^2 + K*N) (A and b variables)
    %  Filtering: C*K per symbol
    SA_bcd_pre  = re(C * K^2);
    SA_bcd_iter = re(T * C * (K^2 + K*N));
    Ss_bcd      = re(C * K);
    R_form_bcd  = w * (SA_bcd_pre + SA_bcd_iter) * NPRB / TOFDM;
    R_fil_bcd   = w * Ss_bcd * Nu / TOFDM;
    R_bcd       = (R_form_bcd + R_fil_bcd) / 1e12;

    %% BCD-MMSE (LRD):
    %  LRD algorithm: (C-1)*M*r + 4*C*N*r  (daisy-chain passes)
    %  Preprocessing:  C*(4*K^2 + 2*K*r)
    %  Per iteration:  T*C*(K^2 + K*r)*2  (A and B variables)
    %  Filtering:      C*K per symbol
    SA_lrd_lrd  = re((C-1)*M*r + 4*C*N*r);
    SA_lrd_pre  = re(C * (4*K^2 + 2*K*r));
    SA_lrd_iter = re(T * C * (K^2 + K*r));
    Ss_lrd      = re(C*K);
    R_form_lrd  = w * (SA_lrd_lrd + SA_lrd_pre + SA_lrd_iter) * NPRB / TOFDM;
    R_fil_lrd   = w * Ss_lrd * Nu / TOFDM;
    R_lrd       = (R_form_lrd + R_fil_lrd) / 1e12;

    fprintf('M=%d K=%d C=%d  %10.2f %10.2f %10.2f %10.2f\n', ...
            M, K, C, R_cmmse, R_dr, R_bcd, R_lrd);

    rate_table(k).CentralMMSE = R_cmmse;
    rate_table(k).DR_MMSE     = R_dr;
    rate_table(k).BCD_MMSE    = R_bcd;
    rate_table(k).BCD_LRD     = R_lrd;
end
fprintf('%s\n', repmat('=',1,65));
fprintf('(All rates in Tbps)\n');
end
