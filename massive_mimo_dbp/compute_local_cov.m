function [Rcc, Rcc_inv] = compute_local_cov(Nc, p)
%COMPUTE_LOCAL_COV  Local diagonal blocks of R estimated at each DU.
%
%  Rcc{c}     = (1/N) * Nc{c} * Nc{c}'   (Mc x Mc)
%  Rcc_inv{c} = inv(Rcc{c})

Rcc     = cell(p.C, 1);
Rcc_inv = cell(p.C, 1);
for c = 1:p.C
    Rcc{c}     = (Nc{c} * Nc{c}') / p.N_samples;
    Rcc_inv{c} = inv_stable(Rcc{c});
end
end
