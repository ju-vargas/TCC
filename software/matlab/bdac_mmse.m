function W_cell = bdac_mmse(Hc, Rcc_inv, p)
%BDAC_MMSE  Block-Diagonal Approximate Covariance MMSE equalizer (Eq. 7).
%
%  Each DU computes Hc{c}' * Rcc_inv{c} * Hc{c}  (K x K local Gram).
%  CU sums them, inverts, and broadcasts.  Each DU gets its local W slice.
%
%  Returns W_cell : C-cell, each K x Mc

%% Step 1: each DU computes local Gram  sum_c  Hc'*Rcc_inv*Hc
Gram = zeros(p.K, p.K);
for c = 1:p.C
    Gram = Gram + Hc{c}' * Rcc_inv{c} * Hc{c};
end
A_inv = inv_stable(Gram + (1/p.Es) * eye(p.K));  % K x K global inversion

%% Step 2: broadcast A_inv; each DU computes its local slice
W_cell = cell(p.C, 1);
for c = 1:p.C
    W_cell{c} = A_inv * Hc{c}' * Rcc_inv{c};   % K x Mc
end
end
