function W_new = bcd_mmse_update(W_old, Hc, Nc, p)
%BCD_MMSE_UPDATE  One Gauss-Seidel BCD sweep over all C clusters (Eq. 30).
%
%  W_old  : C-cell of K x Mc matrices (current equalization blocks)
%  Hc     : C-cell of Mc x K channel blocks
%  Nc     : C-cell of Mc x N noise sample blocks
%  p      : parameter struct
%
%  W_new  : C-cell of K x Mc updated equalization blocks
%
%  Interaction variables (daisy-chain):
%    A_{c}   = sum_{j=1}^{c} W_j * H_j          (K x K running sum)
%    b_{c,i} = sum_{j=1}^{c} W_j * n^i_j        (K x 1 running sum, per sample)

N  = p.N_samples;
W_new = W_old;

%% Initialise interaction variables  A_0 = sum over ALL clusters (ring)
%  For the unidirectional daisy-chain with ring, A^{l}_{0} = A^{l-1}_{C}
%  On the very first call W_old already carries the BDAC init.
A_prev = zeros(p.K, p.K);
for c = 1:p.C
    A_prev = A_prev + W_old{c} * Hc{c};
end

%  b_{0,i} = sum_j W_j * n^i_j  for all i
b_prev = zeros(p.K, N);   % K x N
for c = 1:p.C
    b_prev = b_prev + W_old{c} * Nc{c};
end

%% Gauss-Seidel sequential update
for c = 1:p.C
    %-- Local quantities at DU c
    HcHc_T = Hc{c} * Hc{c}';                      % Mc x Mc
    NcNc_T = (Nc{c} * Nc{c}') / N;               % Mc x Mc
    local_M = p.Es * HcHc_T + NcNc_T;             % Mc x Mc
    local_M_inv = inv_stable(local_M);

    %-- Remove old contribution of cluster c from running sums
    A_minus = A_prev - W_old{c} * Hc{c};          % K x K
    b_minus = b_prev - W_old{c} * Nc{c};          % K x N

    %-- Numerator of update (Eq. 30 numerator)
    %   p.Es * (I - A_minus) * Hc{c}'
    %   - (1/N) * sum_i b_minus_i * (n^i_c)'
    %   = p.Es*(I - A_minus)*Hc{c}' - b_minus*Nc{c}'/N
    num = p.Es * (eye(p.K) - A_minus) * Hc{c}' ...
          - (b_minus * Nc{c}') / N;               % K x Mc

    %-- Update W_c
    W_new{c} = num * local_M_inv;                 % K x Mc

    %-- Update interaction variables with new W_c
    A_prev = A_minus + W_new{c} * Hc{c};
    b_prev = b_minus + W_new{c} * Nc{c};
end
end
