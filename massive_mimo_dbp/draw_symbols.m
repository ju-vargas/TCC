function S = draw_symbols(const, K, Ns)
%DRAW_SYMBOLS  Draw K x Ns i.i.d. symbols uniformly from constellation.
Mc  = numel(const);
idx = randi(Mc, K, Ns);
S   = const(idx);
end
