function SER = run_ser_sweep(p, fig_select)
%RUN_SER_SWEEP  Monte-Carlo SER vs SNR for all selected equalizers.
%  Compatible with MATLAB R2014a and later.
%
%  Algorithm sets per figure match the paper exactly:
%
%  Fig. 6  : LMMSE, ZF, MMSE(AWGN), BDAC, BCD-MMSE Iter 1-4
%  Fig. 7  : LMMSE, ZF, BDAC, BCD-MMSE(LRD) Iter 1-4
%  Fig. 8x : LMMSE, ZF, BCD-MMSE Iter1, BCD-MMSE(LRD) Iter4, sDR, cDR
%            (BCD:Iter1 and LRD:Iter4 chosen for equal bandwidth budget
%             per Section VI-C of the paper)

nSNR = numel(p.SNR_dB);

%% Algorithm sets matching each paper figure exactly
switch fig_select
    case 'fig6'
        % Fig. 6: SER of BCD-MMSE with iterations 1-4
        % Baselines: centralised LMMSE, ZF, MMSE(AWGN), BDAC-MMSE
        algs = {'LMMSE','ZF','MMSE_AWGN','BDAC','BCD1','BCD2','BCD3','BCD4'};

    case 'fig7'
        % Fig. 7: SER of BCD-MMSE(LRD) with iterations 1-4
        % Baselines: centralised LMMSE, ZF, BDAC-MMSE
        algs = {'LMMSE','ZF','BDAC','LRD1','LRD2','LRD3','LRD4'};

    otherwise
        % Fig. 8(a-g): all proposed equalizers at representative iterations
        % BCD-MMSE at Iter 1, BCD-MMSE(LRD) at Iter 4 — equal bandwidth
        % No BDAC (it is only an initialiser here, not a featured method)
        algs = {'LMMSE','ZF','BCD1','LRD4','sDR','cDR'};
end

%% Pre-compute membership flags (isfield is R2014a-safe)
has = struct();
for a = 1:numel(algs)
    has.(algs{a}) = true;
end

run_LMMSE   = isfield(has, 'LMMSE');
run_ZF      = isfield(has, 'ZF');
run_AWGN    = isfield(has, 'MMSE_AWGN');
run_BDAC    = isfield(has, 'BDAC');
run_BCD     = isfield(has,'BCD1') || isfield(has,'BCD2') || ...
              isfield(has,'BCD3') || isfield(has,'BCD4');
run_LRD     = isfield(has,'LRD1') || isfield(has,'LRD2') || ...
              isfield(has,'LRD3') || isfield(has,'LRD4');
run_sDR     = isfield(has, 'sDR');
run_cDR     = isfield(has, 'cDR');
need_bdac_w = run_BDAC || run_BCD || run_LRD;

%% Initialise error / symbol counters
err   = struct();
total = struct();
for a = 1:numel(algs)
    err.(algs{a})   = zeros(1, nSNR);
    total.(algs{a}) = zeros(1, nSNR);
end

%% Monte-Carlo loop
fprintf('Progress: ');
for mc = 1:p.N_mc
    if mod(mc, 10) == 0
        fprintf('%d/%d ', mc, p.N_mc);
    end

    % QuaDRiGa v2.2.0 channel (large- and small-scale fading)
    [H_tgt, H_itf] = generate_quadriga_channel(p);

    for isnr = 1:nSNR
        SNR    = 10^(p.SNR_dB(isnr)/10);
        sigma2 = p.Es / (SNR * p.bpS);
        IoT_lin = 10^(p.IoT_dB/10);

        % Interference scaling (Eq. 5): R = beta * H_itf * H_itf' + sigma2 * I
        %   Per-antenna interference power = beta * trace(H_itf*H_itf')/M ≈ beta * r
        %   IoT = (beta*r + sigma2) / sigma2  =>  beta = (IoT_lin - 1)*sigma2 / r
        beta = (IoT_lin - 1) * sigma2 / p.r;

        % True covariance and Cholesky factor
        R_true = beta * (H_itf * H_itf') + sigma2 * eye(p.M);
        R_reg  = R_true + 1e-12 * trace(R_true) / p.M * eye(p.M);
        Lc     = chol(R_reg, 'lower');

        % N noise samples for covariance estimation (Gaussian, Eq. 6)
        N_mat = Lc * (randn(p.M, p.N_samples) + ...
                      1j*randn(p.M, p.N_samples)) / sqrt(2);

        % Partition into clusters (R2014a: no ~ in non-final position)
        [Hc, Yc_dummy, Nc] = partition_clusters(H_tgt, [], N_mat, p); %#ok<ASGLU>

        % Local diagonal covariance blocks
        [Rcc, Rcc_inv] = compute_local_cov(Nc, p);

        % Symbol block
        S_tx     = draw_symbols(p.const, p.K, p.N_sym);
        noise_rx = Lc * (randn(p.M, p.N_sym) + ...
                         1j*randn(p.M, p.N_sym)) / sqrt(2);
        Y_rx = H_tgt * S_tx + noise_rx;
        Yc   = mat2cell(Y_rx, repmat(p.Mc, 1, p.C), p.N_sym);

        % Estimated covariance for centralised methods
        R_est = (N_mat * N_mat') / p.N_samples;

        %------------------------------------------------------------------
        if run_LMMSE
            W     = lmmse_centralised(H_tgt, R_true, p.Es);
            S_det = detect(W * Y_rx, p.const);
            [e,t] = count_errors(S_det, S_tx, p.bpS);
            err.LMMSE(isnr)   = err.LMMSE(isnr)   + e;
            total.LMMSE(isnr) = total.LMMSE(isnr) + t;
        end

        if run_ZF
            W     = zf_centralised(H_tgt);
            S_det = detect(W * Y_rx, p.const);
            [e,t] = count_errors(S_det, S_tx, p.bpS);
            err.ZF(isnr)   = err.ZF(isnr)   + e;
            total.ZF(isnr) = total.ZF(isnr) + t;
        end

        if run_AWGN
            W     = lmmse_centralised(H_tgt, sigma2 * eye(p.M), p.Es);
            S_det = detect(W * Y_rx, p.const);
            [e,t] = count_errors(S_det, S_tx, p.bpS);
            err.MMSE_AWGN(isnr)   = err.MMSE_AWGN(isnr)   + e;
            total.MMSE_AWGN(isnr) = total.MMSE_AWGN(isnr) + t;
        end

        % BDAC-MMSE: used as initialiser for BCD/LRD, and as a plotted
        % curve in Figs. 6 and 7
        if need_bdac_w
            W_bdac = bdac_mmse(Hc, Rcc_inv, p);
        end

        if run_BDAC
            S_det = detect(apply_equalizer(W_bdac, Yc, p), p.const);
            [e,t] = count_errors(S_det, S_tx, p.bpS);
            err.BDAC(isnr)   = err.BDAC(isnr)   + e;
            total.BDAC(isnr) = total.BDAC(isnr) + t;
        end

        % BCD-MMSE iterations
        if run_BCD
            W_bcd = W_bdac;
            for iter = 1:4
                W_bcd = bcd_mmse_update(W_bcd, Hc, Nc, p);
                tag   = sprintf('BCD%d', iter);
                if isfield(has, tag)
                    S_det = detect(apply_equalizer(W_bcd, Yc, p), p.const);
                    [e,t] = count_errors(S_det, S_tx, p.bpS);
                    err.(tag)(isnr)   = err.(tag)(isnr)   + e;
                    total.(tag)(isnr) = total.(tag)(isnr) + t;
                end
            end
        end

        % BCD-MMSE (LRD) iterations
        if run_LRD
            G     = lrd_algorithm(Nc, p.r, p);
            Gc    = mat2cell(G, repmat(p.Mc, 1, p.C), p.r);
            W_lrd = W_bdac;
            for iter = 1:4
                W_lrd = bcd_mmse_lrd_update(W_lrd, Hc, Gc, Rcc, p);
                tag   = sprintf('LRD%d', iter);
                if isfield(has, tag)
                    S_det = detect(apply_equalizer(W_lrd, Yc, p), p.const);
                    [e,t] = count_errors(S_det, S_tx, p.bpS);
                    err.(tag)(isnr)   = err.(tag)(isnr)   + e;
                    total.(tag)(isnr) = total.(tag)(isnr) + t;
                end
            end
        end

        if run_sDR
            S_hat = sdr_mmse(Hc, Nc, Rcc_inv, Yc, p);
            S_det = detect(S_hat, p.const);
            [e,t] = count_errors(S_det, S_tx, p.bpS);
            err.sDR(isnr)   = err.sDR(isnr)   + e;
            total.sDR(isnr) = total.sDR(isnr) + t;
        end

        if run_cDR
            S_hat = cdr_mmse(Hc, Nc, Rcc_inv, Yc, p);
            S_det = detect(S_hat, p.const);
            [e,t] = count_errors(S_det, S_tx, p.bpS);
            err.cDR(isnr)   = err.cDR(isnr)   + e;
            total.cDR(isnr) = total.cDR(isnr) + t;
        end

    end % isnr
end % mc
fprintf('\nDone.\n');

%% Compute SER
SER = struct();
for a = 1:numel(algs)
    SER.(algs{a}) = err.(algs{a}) ./ max(total.(algs{a}), 1);
end
end
