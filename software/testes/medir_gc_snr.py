#!/usr/bin/env python3
"""Mede, em cada ponto de SNR, o tamanho das matrizes G_c que o BCD-MMSE inverte e quantas
estouram num formato de ponto fixo (modelo bit a bit do hardware, hardware/golden_cholesky.py).

G_c = E_s H_c H_c^H + R_cc (m7_equalizers.bcd_mmse_path) não depende da iteração nem da
modulação, só da SNR, do canal e das amostras de ruído. O sorteio segue o de
m1_driver.run_panel (amostras de ruído, símbolos, ruído dos dados), então as primeiras
realizações têm as mesmas matrizes da simulação.

Saída: uma linha por SNR com o percentil 50 e 99 do maior |parte real ou imaginária| de cada
matriz, a fração de matrizes acima de 2^(I-1) e a fração com estouro no modelo do hardware.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python medir_gc_snr.py --config 5 --condicao TDLC300-100 \\
        --realizacoes 20 --formato 18,8 -o saida.csv
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

from dbp_sim import m2_channel, m3_clustering, m4_source, m5_noise, hw_inverse  # noqa: E402
from dbp_sim.m1_driver import SimConfig  # noqa: E402
from dbp_sim.params import (M1_Driver, M2_Channel, PANELS_BY_LABEL,  # noqa: E402
                            TCC_CONFIGURATION)

GRADE = tuple(range(-20, 11, 2))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", type=int, required=True, help="número da configuração (1 a 24)")
    ap.add_argument("--condicao", default="TDLC300-100")
    ap.add_argument("--realizacoes", type=int, default=20)
    ap.add_argument("--formato", default="18,8", help="W,I")
    ap.add_argument("--quant", default="AP_RND_ZERO")
    ap.add_argument("--overflow", default="AP_WRAP")
    ap.add_argument("-o", "--saida", type=Path)
    a = ap.parse_args()

    rotulo = {k: r for r, k in TCC_CONFIGURATION.items()}[a.config]
    n, fc = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}[a.condicao]
    cfg = SimConfig.from_panel(PANELS_BY_LABEL[rotulo], n_noise_samples=n, carrier_hz=fc,
                               snr_db_grid=GRADE)
    W, I = map(int, a.formato.split(","))
    modelo = hw_inverse._load()
    inv = hw_inverse.make_inverter("cholesky_hw", I, W - I, quant=a.quant, overflow=a.overflow)
    limite = 2.0 ** (I - 1)

    rng = np.random.default_rng(cfg.seed)
    backend = m2_channel.make_backend(
        cfg.channel_backend, path=M2_Channel.quadriga_export_path.value,
        spread_deg=M2_Channel.standin_angular_spread_deg.value,
        n_paths=M2_Channel.standin_paths_per_ue.value, sector_deg=M2_Channel.sector_deg.value,
        radius_min_m=M2_Channel.radius_min_m.value, radius_max_m=M2_Channel.radius_max_m.value,
        normalization=cfg.normalization, carrier_hz=cfg.carrier_hz, **cfg.channel_kwargs)
    clusters = m3_clustering.cluster_indices(cfg.M, cfg.C, cfg.mapping)
    alfabeto = m4_source.constellation(cfg.modulation)

    assert cfg.data_noise_independent, "o sorteio abaixo segue só esse caso"
    maior = {s: [] for s in GRADE}
    estouro = {s: 0 for s in GRADE}
    for r in range(a.realizacoes):
        H, Hbar = backend.generate(cfg.M, cfg.K, cfg.r, r, rng)
        beta = m5_noise.beta_from_iot(cfg.iot_db, 1.0, Hbar, cfg.beta_convention)
        L_forma = m5_noise.cholesky_factor(m5_noise.noise_covariance(Hbar, beta, 1.0))
        for snr in GRADE:
            sigma2 = cfg.Es * 10.0 ** (-snr / 10.0)
            L = np.sqrt(sigma2) * L_forma
            S = m5_noise.scaled_sample_matrix(m5_noise.draw_noise(L, cfg.n_noise_samples, rng))
            cond = m5_noise.Conditioner(cfg.shrinkage, cfg.fixed_epsilon)
            cond.prime(S)
            for idx in clusters:
                Hc, Sc = H[idx], S[idx]
                G = cfg.Es * (Hc @ Hc.conj().T) + cond.covariance(Sc)
                maior[snr].append(max(np.abs(G.real).max(), np.abs(G.imag).max()))
                modelo.reset_overflow_count()
                inv(G)
                estouro[snr] += modelo.get_overflow_count() > 0
            # mesmos sorteios de run_panel depois das amostras de ruído
            m4_source.draw_symbols(alfabeto, cfg.K, cfg.n_symbols, rng)
            m5_noise.draw_noise(L, cfg.n_symbols, rng)

    linhas = []
    for snr in GRADE:
        v = np.array(maior[snr])
        linhas.append([snr, round(float(np.percentile(v, 50)), 1),
                       round(float(np.percentile(v, 99)), 1),
                       round(float(np.mean(v >= limite)), 3), round(estouro[snr] / v.size, 3)])
    cab = ["snr_db", "maior_parte_p50", "maior_parte_p99", "frac_acima_limite",
           "frac_estouro_modelo"]
    print(f"configuração {a.config} ({rotulo}), {a.condicao}, <{W},{I}> {a.quant}/{a.overflow}, "
          f"limite {limite:g}, {a.realizacoes} realizações x {cfg.C} DUs")
    print("\t".join(cab))
    for l in linhas:
        print("\t".join(map(str, l)))
    if a.saida:
        with open(a.saida, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(cab)
            w.writerows(linhas)


if __name__ == "__main__":
    main()
