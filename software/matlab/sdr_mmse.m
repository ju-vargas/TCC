function S_hat = sdr_mmse(Hc, Nc, Rcc_inv, Yc, p)
%SDR_MMSE  Superimposed Dimensionality Reduction MMSE (Algorithm 1).
%
%  Each DU c computes local compression matrix Qc = Hc'*Rcc_inv (K x Mc)
%  and sends compressed data to the CU, which superimposes and runs LMMSE.
%
%  Hc      : C-cell of Mc x K  channel blocks
%  Nc      : C-cell of Mc x N  noise sample blocks
%  Rcc_inv : C-cell of Mc x Mc inverse local covariance blocks
%  Yc      : C-cell of Mc x Ns received signal blocks
%  p       : parameter struct (p.K, p.C, p.N_samples, p.Es)
%
%  S_hat   : K x Ns  soft symbol estimates

N  = p.N_samples;
Ns = size(Yc{1}, 2);

%% DU preprocessing: each DU computes Qc and sends compressed data to CU
y_check = zeros(p.K, Ns);      % Eq. (13a): superimposed Qc*yc
H_check = zeros(p.K, p.K);    % superimposed Qc*Hc
QN_sum  = zeros(p.K, N);       % superimposed Qc*Nc  (for R_check)

for c = 1:p.C
    Qc      = Hc{c}' * Rcc_inv{c};          % K x Mc
    y_check = y_check + Qc * Yc{c};
    H_check = H_check + Qc * Hc{c};
    QN_sum  = QN_sum  + Qc * Nc{c};
end

%% CU: compressed noise covariance R_check (Eq. 14)
R_check = (QN_sum * QN_sum') / N;            % K x K

%% CU: LMMSE on compressed model (Eq. 15-16)
W     = lmmse_centralised(H_check, R_check, p.Es);   % K x K
S_hat = W * y_check;                                  % K x Ns
end
