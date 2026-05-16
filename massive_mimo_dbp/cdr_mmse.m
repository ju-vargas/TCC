function S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, p)
%CDR_MMSE  Concatenated Dimensionality Reduction MMSE (Algorithm 2).
%
%  Same DU preprocessing as sDR-MMSE, but the CU concatenates compressed
%  data instead of superimposing, giving a CK-dimensional observation.
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
CK = p.C * p.K;

%% DU preprocessing: compress local data (same Qc as sDR)
y_tilde = zeros(CK, Ns);    % Eq. (19): concatenated [Q1*y1; ...; QC*yC]
H_tilde = zeros(CK, p.K);  % concatenated [Q1*H1; ...; QC*HC]
Qn_cell = cell(p.C, 1);    % Qc*Nc for each cluster

for c = 1:p.C
    Qc   = Hc{c}' * Rcc_inv{c};              % K x Mc
    rows = (c-1)*p.K + (1:p.K);
    y_tilde(rows, :) = Qc * Yc{c};
    H_tilde(rows, :) = Qc * Hc{c};
    Qn_cell{c}       = Qc * Nc{c};           % K x N
end

%% CU: block noise covariance R_tilde (Eq. 20)
%  (m,l)-th block = (1/N) * (Qm*Nm) * (Ql*Nl)'
R_tilde = zeros(CK, CK);
for m = 1:p.C
    rows_m = (m-1)*p.K + (1:p.K);
    for l = 1:p.C
        rows_l = (l-1)*p.K + (1:p.K);
        R_tilde(rows_m, rows_l) = (Qn_cell{m} * Qn_cell{l}') / N;
    end
end

%% CU: LMMSE on CK-dimensional compressed model (Eq. 22-23)
W     = lmmse_centralised(H_tilde, R_tilde, p.Es);   % K x CK
S_hat = W * y_tilde;                                  % K x Ns
end
