function plot_results(SER, SNR_dB, fig_select, p)
%PLOT_RESULTS  Generate SER vs SNR plots matching paper figures.
%  Compatible with MATLAB R2014a and later.

figure('Name', fig_select, 'Position', [100 100 680 520]);
hold on;
grid on;

markers = {'o-','s--','d:','v-.','^-','<--','>:','p-.','h-','*--'};
colors  = lines(12);

alg_names  = fieldnames(SER);
n_algs     = numel(alg_names);
leg_labels = cell(1, n_algs);   % collect labels in the same order as plots

for a = 1:n_algs
    tag = alg_names{a};
    ser = SER.(tag);
    ser(ser == 0) = NaN;
    semilogy(SNR_dB, ser, markers{mod(a-1, numel(markers))+1}, ...
             'Color', colors(a,:), 'LineWidth', 1.5, 'MarkerSize', 7);
    leg_labels{a} = label_name(tag);
end

% Pass label strings explicitly — reliable in all MATLAB versions
legend(leg_labels, 'Location', 'SouthWest', 'FontSize', 9);

xlabel('SNR [dB]', 'FontSize', 12);
ylabel('SER',      'FontSize', 12);
xlim([SNR_dB(1) SNR_dB(end)]);
ylim([1e-4 1]);
set(gca, 'YScale', 'log', 'XGrid', 'on', 'YGrid', 'on');

title_str = sprintf('SER vs SNR  |  %s  M=%d C=%d K=%d IoT=%ddB %s', ...
            fig_select, p.M, p.C, p.K, p.IoT_dB, p.mod);
title(title_str, 'FontSize', 10);

out_name = sprintf('SER_%s_M%d_C%d_K%d.png', fig_select, p.M, p.C, p.K);
print(gcf, out_name, '-dpng', '-r150');
fprintf('Figure saved: %s\n', out_name);
end


function str = label_name(tag)
%LABEL_NAME  Human-readable legend labels.
map = { ...
    'LMMSE',     'LMMSE (centralised)'; ...
    'ZF',        'ZF (centralised)'; ...
    'MMSE_AWGN', 'MMSE(AWGN)'; ...
    'BDAC',      'BDAC-MMSE'; ...
    'BCD1',      'BCD-MMSE: Iter 1'; ...
    'BCD2',      'BCD-MMSE: Iter 2'; ...
    'BCD3',      'BCD-MMSE: Iter 3'; ...
    'BCD4',      'BCD-MMSE: Iter 4'; ...
    'LRD1',      'BCD-MMSE(LRD): Iter 1'; ...
    'LRD2',      'BCD-MMSE(LRD): Iter 2'; ...
    'LRD3',      'BCD-MMSE(LRD): Iter 3'; ...
    'LRD4',      'BCD-MMSE(LRD): Iter 4'; ...
    'sDR',       'sDR-MMSE'; ...
    'cDR',       'cDR-MMSE'; ...
};
idx = strcmp(map(:,1), tag);
if any(idx)
    str = map{idx, 2};
else
    str = tag;
end
end
