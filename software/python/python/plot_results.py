"""Plot SER vs SNR results matching paper style."""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Style definitions matching paper figures
STYLES = {
    'LMMSE':    dict(color='blue',    marker='o', ls='-',  lw=2, label='LMMSE (centralised)'),
    'ZF':       dict(color='#228B22', marker='s', ls='--', lw=2, label='ZF (centralised)'),
    'MMSE_AWGN':dict(color='gray',    marker='^', ls='-.', lw=1.5, label='MMSE (AWGN)'),
    'BDAC':     dict(color='brown',   marker='v', ls=':',  lw=1.5, label='BDAC-MMSE'),
    'BCD1':     dict(color='red',     marker='d', ls=':',  lw=1.5, label='BCD-MMSE: Iter 1'),
    'BCD2':     dict(color='#FF6600', marker='p', ls=':',  lw=1.5, label='BCD-MMSE: Iter 2'),
    'BCD3':     dict(color='#CC00CC', marker='h', ls=':',  lw=1.5, label='BCD-MMSE: Iter 3'),
    'BCD4':     dict(color='#8B0000', marker='*', ls=':',  lw=1.5, label='BCD-MMSE: Iter 4'),
    'LRD1':     dict(color='#00BFFF', marker='d', ls='-.', lw=1.5, label='BCD-MMSE(LRD): Iter 1'),
    'LRD2':     dict(color='#1E90FF', marker='p', ls='-.', lw=1.5, label='BCD-MMSE(LRD): Iter 2'),
    'LRD3':     dict(color='#4169E1', marker='h', ls='-.', lw=1.5, label='BCD-MMSE(LRD): Iter 3'),
    'LRD4':     dict(color='cyan',    marker='v', ls='-.', lw=1.5, label='BCD-MMSE(LRD): Iter 4'),
    'sDR':      dict(color='magenta', marker='^', ls='-',  lw=1.5, label='sDR-MMSE'),
    'cDR':      dict(color='#FFD700', marker='<', ls='--', lw=1.5, label='cDR-MMSE'),
}


def plot_results(SER: dict, SNR_dB: np.ndarray, fig_select: str,
                 cfg=None, save_path: str = None):
    """Generate SER vs SNR plot.

    Parameters
    ----------
    SER : dict mapping algorithm name → np.ndarray of SER values
    SNR_dB : np.ndarray
    fig_select : str
    cfg : SimConfig (optional, for title info)
    save_path : str (optional, defaults to SER_{fig_select}.png)
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    for alg_name, ser_vals in SER.items():
        style = STYLES.get(alg_name, dict(marker='x', ls='-', lw=1, label=alg_name))
        # Clip zeros for log scale
        ser_plot = np.where(ser_vals > 0, ser_vals, np.nan)
        ax.semilogy(SNR_dB, ser_plot, markersize=7, **style)

    ax.set_xlabel('SNR [dB]', fontsize=13)
    ax.set_ylabel('SER', fontsize=13)

    if cfg is not None:
        title = (f'SER vs SNR | {fig_select}  '
                 f'M={cfg.M} C={cfg.C} K={cfg.K} IoT={cfg.IoT_dB}dB {cfg.mod}')
    else:
        title = f'SER vs SNR | {fig_select}'
    ax.set_title(title, fontsize=14)

    ax.legend(loc='lower left', fontsize=9, framealpha=0.9)
    ax.grid(True, which='both', alpha=0.3)
    ax.set_xlim(SNR_dB[0], SNR_dB[-1])
    ax.set_ylim(1e-4, 1)

    plt.tight_layout()

    if save_path is None:
        save_path = f'SER_{fig_select}.png'
    fig.savefig(save_path, dpi=150)
    print(f"Plot saved to {save_path}")
    plt.close(fig)
