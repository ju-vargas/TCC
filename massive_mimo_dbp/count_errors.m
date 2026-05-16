function [n_err, n_total] = count_errors(S_det, S_tx, ~)
%COUNT_ERRORS  Count symbol errors.
%  Third argument (bpS) accepted but unused — SER is symbol-level.
n_err   = sum(S_det(:) ~= S_tx(:));
n_total = numel(S_tx);
end
