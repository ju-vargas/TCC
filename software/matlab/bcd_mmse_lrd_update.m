function W_new = bcd_mmse_lrd_update(W_old, Hc, Gc, Rcc, p)
%BCD_MMSE_LRD_UPDATE  One Gauss-Seidel BCD sweep using LRD (Section IV-B).
%
%  Key insight: Gc (Mc x r) replaces Nc (Mc x N) ONLY in the inter-DU
%  interaction variable B = sum_j W_j*G_j (K x r), which is what gets
%  transferred between DUs. The LOCAL denominator still uses the full
%  local sample covariance Rcc = (1/N)*Nc*Nc', which correctly includes
%  the sigma2*I AWGN floor that a rank-r approximation would miss.
%
%  Interaction variables:
%    A_{c} = sum_j W_j * H_j          (K x K)  -- same as BCD-MMSE
%    B_{c} = sum_j W_j * G_j          (K x r)  -- replaces b (K x N)
%
%  Inputs:
%    W_old : C-cell of K x Mc  (current equalizer blocks)
%    Hc    : C-cell of Mc x K  (channel blocks)
%    Gc    : C-cell of Mc x r  (LRD factors: Gc*Gc' ≈ Rcc)
%    Rcc   : C-cell of Mc x Mc (local sample covariance, used in denominator)
%    p     : parameter struct

W_new  = W_old;
r_rank = size(Gc{1}, 2);

%% Initialise running sums (ring initialisation)
A_prev = zeros(p.K, p.K);
B_prev = zeros(p.K, r_rank);
for c = 1:p.C
    A_prev = A_prev + W_old{c} * Hc{c};
    B_prev = B_prev + W_old{c} * Gc{c};
end

%% Gauss-Seidel sweep
for c = 1:p.C
    % LOCAL denominator: use full Rcc (includes sigma2*I correctly)
    local_M     = p.Es * (Hc{c} * Hc{c}') + Rcc{c};   % Mc x Mc
    local_M_inv = inv_stable(local_M);

    % Remove old contribution of cluster c from running sums
    A_minus = A_prev - W_old{c} * Hc{c};   % K x K
    B_minus = B_prev - W_old{c} * Gc{c};   % K x r

    % Numerator: cross-cluster noise term uses B_minus * Gc{c}'
    % (approximates (1/N)*b_minus*Nc' via low-rank factors)
    num = p.Es * (eye(p.K) - A_minus) * Hc{c}' ...
          - B_minus * Gc{c}';               % K x Mc

    % Update W_c
    W_new{c} = num * local_M_inv;

    % Update running sums with new W_c
    A_prev = A_minus + W_new{c} * Hc{c};
    B_prev = B_minus + W_new{c} * Gc{c};
end
end
