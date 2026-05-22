function W = lmmse_centralised(H, R_est, Es)
%LMMSE_CENTRALISED  Centralised LMMSE equalizer (Eq. 3).
%
%  W = (H'*R^{-1}*H + (1/Es)*I)^{-1} * H'*R^{-1}
%
%  H     : M x K  channel matrix
%  R_est : M x M  noise covariance (estimated or true)
%  Es    : scalar, average symbol energy
%  W     : K x M  equalization matrix

K     = size(H, 2);
R_inv = inv_stable(R_est);
A     = H' * R_inv * H + (1/Es) * eye(K);
W     = inv_stable(A) * (H' * R_inv);
end
