
---

## QuaDRiGa v2.2.0 + MATLAB R2014a: Complete Implementation Guide

---

### Step 1 — Path Setup

```matlab
% Add QuaDRiGa to path. Must include the top-level quadriga_src folder.
addpath(genpath('/path/to/QuaDRiGa_v2.2.0/quadriga_src'));
savepath;
```

**⚠️ Version difference:** In v2.8+, `quadriga_src` also ships MEX binaries that accelerate computation. In v2.2.0 there are no MEX files — all computation is pure MATLAB, which is slower but fully compatible with R2014a.

---

### Step 2 — Simulation Parameters Object

```matlab
s = qd_simulation_parameters;
s.center_frequency   = 2e9;   % 2 GHz carrier frequency
s.use_3GPP_baseline  = 1;     % disable spatial consistency (static drops)
s.show_progress_bars = 0;     % suppress output inside loops
```

**⚠️ Version difference:** `s.use_random_initial_phase` exists in v2.2.0 (default = 1) and can be left at its default. In v2.8+ there are additional properties like `use_spherical_waves` — do not set these as they do not exist in v2.2.0 and will throw errors.

**⚠️ R2014a note:** `qd_simulation_parameters` is a handle class. Do NOT copy it with `s2 = s` — this creates a reference, not a copy. Use `s2 = s.copy` if you need an independent copy.

---

### Step 3 — Layout Creation

```matlab
l = qd_layout(s);       % attach simulation parameters to layout
l.no_tx = 1;            % 1 BS
l.no_rx = n_UE_total;   % K + r UEs
```

**⚠️ Version difference:** In v2.8+, `qd_layout` has a `no_sectors` property. This does not exist in v2.2.0 — ignore it.

---

### Step 4 — BS Antenna (Vertical ULA)

```matlab
lambda = 3e8 / 2e9;   % wavelength
M      = 128;          % total BS antennas

A_tx = qd_arrayant('omni');        % start from single isotropic element
A_tx.no_elements = M;              % expand to M elements
z_pos = ((0:M-1) - (M-1)/2) * lambda/2;   % z-axis positions, centred
A_tx.element_position = [zeros(1,M); zeros(1,M); z_pos];
l.tx_array = A_tx;
```

**⚠️ Version difference:** In v2.8+, `qd_arrayant` accepts `'3gpp-macro'` and other shortcuts that do not exist in v2.2.0. The `'omni'` type plus manual `element_position` setting shown above works in all versions.

**⚠️ R2014a note:** `A_tx.no_elements = M` must be set BEFORE setting `element_position`. Setting `element_position` first will throw a dimension mismatch error.

---

### Step 5 — UE Placement

```matlab
% 120-degree sector, 50-100 m from BS
r_ue   = 50 + 50 * rand(1, n_UE_total);
phi_ue = (-60 + 120 * rand(1, n_UE_total)) * pi/180;  % R2014a: no deg2rad
rx_x   = r_ue .* cos(phi_ue);
rx_y   = r_ue .* sin(phi_ue);
h_UE   = 1.5;

l.rx_position = [rx_x; rx_y; h_UE * ones(1, n_UE_total)];
l.rx_array    = qd_arrayant('omni');   % single isotropic element per UE
l.tx_position = [0; 0; 25];           % BS at 25 m height
```

**⚠️ R2014a note:** `deg2rad` requires the Mapping Toolbox in R2014a. Always use `x * pi/180` instead.

---

### Step 6 — Scenario Assignment

```matlab
% In v2.2.0, set_scenario ONLY accepts a single string.
% It applies the same scenario to all UEs in the layout.
l.set_scenario('3GPP_38.901_UMa_NLOS');
```

**⚠️ Version difference — critical:** In v2.8+, `set_scenario` accepts a cell array of strings for per-UE assignment. In v2.2.0 it strictly requires a plain `char` string. Passing a cell array throws: `"Scenario must be a string"`.

**Solution for mixed LOS/NLOS in v2.2.0:** Run two separate `qd_layout` objects — one containing all LOS UEs, one containing all NLOS UEs — then concatenate the resulting channel matrices. This is exactly what our `quadriga_batch` helper does.

**How to find available scenario names in v2.2.0:**
```matlab
% config files are in quadriga_src/config/, NOT in @qd_layout/config/
conf_dir = fullfile(fileparts(fileparts(which('qd_layout'))), 'config');
d = dir(fullfile(conf_dir, '*UMa*.conf'));
for i = 1:length(d), disp(d(i).name); end
```
This prints the available UMa scenarios. The scenario string is the filename without `.conf`.

**⚠️ Version difference:** In v2.8+, `qd_layout.supported_scenarios` lists all scenarios. In v2.2.0 this method does not exist on `qd_layout`. It DOES exist on `qd_builder` — use `b.supported_scenarios` after creating a builder.

---

### Step 7 — Channel Generation (Builder Flow)

```matlab
b    = l.init_builder;   % creates qd_builder object(s)
b.gen_parameters;        % generates ALL parameters (LSF + SSF)
chan = b.get_channels;   % returns 1 x n_UE array of qd_channel objects
```

**⚠️ Version difference — critical:** This three-step flow is specific to v2.x. In v2.8+ there is an alternative one-step shortcut `l.get_channels` directly, but this does not exist in v2.2.0.

**⚠️ Common mistake in v2.2.0:** Do NOT call `gen_lsf_parameters` and `gen_ssf_parameters` separately after `gen_parameters`. Looking at the source code of `qd_builder.m`, both `gen_lsf_parameters` and `gen_ssf_parameters` internally call `gen_parameters` again, which deletes all previously computed parameters and restarts from scratch, producing the flood of `"Existing parameters deleted"` warnings we observed. The correct call is `gen_parameters` alone — it handles everything internally.

The correct methods available on `qd_builder` in v2.2.0 (verified with `methods(b)`):

| Method | Purpose |
|---|---|
| `gen_parameters` | Generate ALL channel parameters (use this only) |
| `gen_lsf_parameters` | Internal — do not call directly |
| `gen_ssf_parameters` | Internal — do not call directly |
| `get_channels` | Retrieve `qd_channel` objects |
| `get_los_channels` | Retrieve LOS-only channel objects |
| `supported_scenarios` | List available scenario strings |

---

### Step 8 — Coefficient Extraction

```matlab
% VERIFIED dimensions in v2.2.0:
%   chan(k).coeff is [M_rx x M_tx x n_paths x n_snapshots]
%                  = [1    x M    x n_paths x n_snap]
% where M_rx=1 (single UE antenna) and M_tx=M (BS ULA)

H = zeros(M, n_UE);
for k = 1:n_UE
    h_row  = sum(chan(k).coeff(1, :, :, 1), 3);  % 1 x M, sum over paths
    H(:,k) = h_row.';                              % M x 1, transpose
end
```

**⚠️ Version difference — critical:** The dimension ordering is `[M_rx × M_tx × n_paths × n_snap]`. Do NOT assume `[M_tx × M_rx × ...]` as in some other channel simulators. The old (incorrect) extraction `coeff(:,1,:,1)` extracts only the first column (first BS antenna element repeated), producing a near-zero vector because `M_rx=1` gives a 1-element first dimension.

**⚠️ Version difference:** In v2.8+, `chan` can be a 2D array `[n_rx × n_tx]` when there are multiple transmitters. In v2.2.0 with a single BS (`no_tx=1`), `chan` is always a 1D array of length `n_rx`, indexed as `chan(k)` not `chan(k,1)`.

---

### Step 9 — Normalisation

```matlab
% Scale H so that average power per receive antenna = 1.
% This makes SNR = Es/sigma2 the effective operating SNR,
% consistent with the paper's definition.
avg_power = mean(sum(abs(H_full).^2, 1)) / M;
if avg_power > 0
    H_full = H_full / sqrt(avg_power);
end
```

**Why this is needed:** QuaDRiGa includes physical path loss (~95 dB at 2 GHz, 75 m). Without normalisation the channel vectors have magnitude ~10⁻⁵, making the received signal negligible compared to any noise level. Per-column unit-norm is wrong because it destroys inter-UE power differences and the massive MIMO array gain.

---

### Summary of All v2.2.0 vs v2.8+ Differences

| Feature | v2.2.0 (your version) | v2.8+ |
|---|---|---|
| `set_scenario` input | Plain string only | String or cell array |
| `supported_scenarios` | On `qd_builder` only | On `qd_layout` |
| `l.get_channels` | Does not exist | Available as shortcut |
| `gen_lsf_parameters` | Internal — causes warnings if called directly | Same |
| `coeff` dimensions | `[M_rx × M_tx × paths × snap]` | Same |
| `chan` indexing (1 TX) | `chan(k)` — 1D array | `chan(k,1)` — 2D array |
| MEX acceleration | None — pure MATLAB | Optional MEX binaries |
| `deg2rad` function | Requires Mapping Toolbox | Same |
| Config file location | `quadriga_src/config/` | Same |
| Object copy | Must use `.copy` method | Same |
| `no_sectors` property | Does not exist | Available |