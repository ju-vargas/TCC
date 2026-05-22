function G = lrd_algorithm(Nc, r, p)
%LRD_ALGORITHM  Decentralised low-rank decomposition (Algorithm 4).
%
%  Sequentially passes a rank-r approximation of the stacked noise matrix
%  [N1; N2; ...; NC] along the daisy-chain.
%
%  Nc  : C-cell of Mc x N_samples noise blocks
%  r   : target rank
%  p   : parameter struct (p.C, p.M, p.Mc, p.N_samples)
%
%  G   : M x r  global low-rank factor  s.t.  G*G' ~= R_est

scale = 1 / sqrt(p.N_samples);

D_prev = [];
V_prev = [];

for c = 1:p.C-1
    Nc_scaled = scale * Nc{c};

    if c == 1
        [U1, S1, V1] = svds(Nc_scaled, r);
        D_prev = U1 * S1;
        V_prev = V1;
    else
        N_approx = D_prev * V_prev';
        N_stack  = [N_approx; Nc_scaled];
        [Uc, Sc, Vc] = svds(N_stack, r);
        D_prev = Uc * Sc;
        V_prev = Vc;
    end
end

% Last DU
Nc_scaled = scale * Nc{p.C};
if p.C == 1
    [UC, SC, VC] = svds(Nc_scaled, r);
    D_prev = UC * SC;   %#ok<NASGU>
    V_prev = VC;
else
    N_approx  = D_prev * V_prev';
    N_stack   = [N_approx; Nc_scaled];
    % R2014a: avoid tilde in middle — capture all three outputs explicitly
    [UC, SC, VC] = svds(N_stack, r);   %#ok<ASGLU>
    V_prev = VC;
end

% Each DU computes Gc = (scale * Nc{c}) * V_prev
G = zeros(p.M, r);
for c = 1:p.C
    idx      = (c-1)*p.Mc + (1:p.Mc);
    G(idx,:) = (scale * Nc{c}) * V_prev;
end
end
