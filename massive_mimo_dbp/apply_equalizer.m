function S_hat = apply_equalizer(W_cell, Yc, p)
%APPLY_EQUALIZER  Apply block equalizer W_cell to partitioned received signal.
%
%  W_cell : C-cell of K x Mc matrices
%  Yc     : C-cell of Mc x Ns matrices
%  S_hat  : K x Ns

Ns    = size(Yc{1}, 2);
S_hat = zeros(p.K, Ns);
for c = 1:p.C
    S_hat = S_hat + W_cell{c} * Yc{c};
end
end
