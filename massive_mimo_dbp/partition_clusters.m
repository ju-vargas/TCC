function [Hc, Yc, Nc] = partition_clusters(H, Y, N_mat, p)
%PARTITION_CLUSTERS  Split M-dimensional arrays into C antenna clusters.
%
%  H     : M x K  channel matrix
%  Y     : M x Ns received signal; pass [] if not needed
%  N_mat : M x N  noise sample matrix
%
%  Hc    : C x 1 cell, each Mc x K
%  Yc    : C x 1 cell, each Mc x Ns  (empty cells when Y=[])
%  Nc    : C x 1 cell, each Mc x N

Hc = cell(p.C, 1);
Yc = cell(p.C, 1);
Nc = cell(p.C, 1);

for c = 1:p.C
    idx    = (c-1)*p.Mc + (1:p.Mc);
    Hc{c}  = H(idx, :);
    Nc{c}  = N_mat(idx, :);
    if ~isempty(Y)
        Yc{c} = Y(idx, :);
    end
end
end
