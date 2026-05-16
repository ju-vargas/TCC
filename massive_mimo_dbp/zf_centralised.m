function W = zf_centralised(H)
%ZF_CENTRALISED  Centralised Zero-Forcing equalizer.
%
%  W = (H'*H)^{-1} * H'
%
%  H : M x K  channel matrix
%  W : K x M  equalization matrix

W = inv_stable(H' * H) * H';
end
