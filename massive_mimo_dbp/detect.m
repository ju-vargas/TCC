function S_det = detect(S_hat, const)
%DETECT  Hard minimum-distance symbol detection.
%
%  S_hat : K x Ns  soft estimates
%  const : Mc x 1  constellation vector
%  S_det : K x Ns  detected symbols

[K, Ns] = size(S_hat);
S_det   = complex(zeros(K, Ns));   % R2014a-safe (no 'like' syntax)
for k = 1:K
    d2         = abs(bsxfun(@minus, S_hat(k,:).', const.')).^2;  % Ns x Mc
    [~, best]  = min(d2, [], 2);
    S_det(k,:) = const(best).';
end
end
