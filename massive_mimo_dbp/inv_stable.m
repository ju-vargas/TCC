function Ainv = inv_stable(A)
%INV_STABLE  Regularised (Tikhonov) matrix inversion.
%  Adds a small diagonal to avoid numerical singularity.
n   = size(A, 1);
tr  = real(trace(A));
reg = max(tr / n * 1e-10, 1e-14);
Ainv = (A + reg * eye(n)) \ eye(n);
end
