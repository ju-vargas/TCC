#!/usr/bin/env python3
"""Main entry point for the Massive MIMO DBP simulator.

Usage:
    python main.py [fig_select] [--N_mc N] [--quick]

Examples:
    python main.py fig8a              # Full run (100 MC)
    python main.py fig8a --quick      # Quick sanity check (5 MC, fewer SNR)
    python main.py fig6 --N_mc 20     # 20 MC realisations
"""

import sys
import os
import argparse
import numpy as np

# Ensure this directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import make_config
from constellation import get_constellation
from run_sim import run_ser_sweep
from plot_results import plot_results


def main():
    parser = argparse.ArgumentParser(description='Massive MIMO DBP Simulator')
    parser.add_argument('fig', nargs='?', default='fig8a',
                        choices=['fig6', 'fig7', 'fig8a', 'fig8b', 'fig8c',
                                 'fig8e', 'fig8f', 'fig8g'],
                        help='Figure to reproduce (default: fig8a)')
    parser.add_argument('--N_mc', type=int, default=None,
                        help='Override number of Monte Carlo realisations')
    parser.add_argument('--quick', action='store_true',
                        help='Quick mode: 5 MC, coarser SNR grid')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed (default: 42)')
    parser.add_argument('--channel', choices=['rayleigh', 'mat_file'],
                        default='rayleigh',
                        help='Channel generation mode')
    parser.add_argument('--mat_file', type=str, default='',
                        help='Path to .mat file for channel data')
    args = parser.parse_args()

    np.random.seed(args.seed)

    overrides = {'channel_mode': args.channel}
    if args.mat_file:
        overrides['mat_file'] = args.mat_file

    if args.quick:
        overrides['N_mc'] = 5
        overrides['SNR_dB'] = np.arange(-10, 12, 4, dtype=float)
    if args.N_mc is not None:
        overrides['N_mc'] = args.N_mc

    cfg = make_config(args.fig, **overrides)

    # Get constellation (for display)
    const, bpS = get_constellation(cfg.mod)
    print(f"Constellation: {cfg.mod}, {len(const)} points, {bpS} bpS")

    # Run simulation
    SER = run_ser_sweep(cfg, args.fig)

    # Print results
    print("\n--- SER Results ---")
    print(f"{'SNR':>6s}", end='')
    for a in SER:
        print(f"  {a:>12s}", end='')
    print()
    for i, snr in enumerate(cfg.SNR_dB):
        print(f"{snr:6.1f}", end='')
        for a in SER:
            print(f"  {SER[a][i]:12.6f}", end='')
        print()

    # Plot
    out_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(out_dir, f'SER_{args.fig}_M{cfg.M}_C{cfg.C}_K{cfg.K}.png')
    plot_results(SER, cfg.SNR_dB, args.fig, cfg, save_path)


if __name__ == '__main__':
    main()
