function [const, bpS] = get_constellation(mod_type)
%GET_CONSTELLATION  Return normalised constellation and bits-per-symbol.
switch upper(mod_type)
    case '16QAM'
        a = [-3 -1 1 3];
        [I,Q] = meshgrid(a,a);
        const = I(:) + 1j*Q(:);
        const = const / sqrt(mean(abs(const).^2));
        bpS   = 4;
    case 'QPSK'
        const = (1/sqrt(2)) * [1+1j; 1-1j; -1+1j; -1-1j];
        bpS   = 2;
    otherwise
        error('Unknown modulation: %s', mod_type);
end
end
