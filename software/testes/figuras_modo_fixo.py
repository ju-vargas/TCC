#!/usr/bin/env python3
"""
Figuras de iterações do BCD-MMSE no molde da bcd_iterations de resultados/1_referencia_float,
mas com a inversa de G_c no hardware HLS, nos formatos e modos fixos do
mapa_perda_modo_fixo_ate_3dB (mapa_cenarios_v4.py). Uma figura por formato e cenário, um
painel por configuração, SNR de -10 a 10 dB. LMMSE e ZF não usam a inversa do BCD e vêm
da referência float64 (os mesmos sorteios, porque a grade e a semente são as mesmas); as 4
iterações do BCD-MMSE vêm de varredura_formatos.py.

Saída: <pasta>/figuras/<W>-<I>_<Q>_<O>/<cenário>_N<N>_<GHz>GHz/bcd_iterations.{png,pdf}
(e o _data.csv da figura).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python figuras_modo_fixo.py [resultados/5_candidatos/modo_fixo_3dB]
"""

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

from dbp_sim.m1_driver import SimConfig, curve_names  # noqa: E402
from dbp_sim.params import ALL_PANELS, M1_Driver, TCC_CONFIGURATION  # noqa: E402
from dbp_sim.plotting import save_figure8              # noqa: E402
from run_figure8 import figure_subtitle                # noqa: E402

PASTA = AQUI / "resultados" / "5_candidatos" / "modo_fixo_3dB"
REFERENCIA = AQUI / "resultados" / "1_referencia_float" / "curvas"
STEM = "bcd_iterations"
ITERACOES = (1, 2, 3, 4)
# Formatos (I, F) e modos do mapa_perda_modo_fixo_ate_3dB, iguais com 1 e 4 iterações e
# em 16 x 16 e 32 x 32
FORMATOS = (((12, 10), "AP_RND_ZERO", "AP_WRAP"), ((12, 12), "AP_RND_ZERO", "AP_WRAP"),
            ((12, 14), "AP_RND_ZERO", "AP_WRAP"), ((14, 14), "AP_RND_ZERO", "AP_WRAP"),
            ((14, 16), "AP_TRN", "AP_SAT"))
BCD = [f"BCD-MMSE (iter {it})" for it in ITERACOES]


def pasta_referencia(cond: str) -> Path:
    """Pasta da referência float do cenário (TDLA30-5 está junto com TDLA30-10)."""
    return next(p for p in REFERENCIA.iterdir() if cond in p.name.split("_")[0].split("+"))


def main() -> None:
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else PASTA
    condicoes = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}
    for (I, F), q, o in FORMATOS:
        nome = f"{I + F}-{I}_{q.removeprefix('AP_')}_{o.removeprefix('AP_')}"
        # Só os cenários simulados (TDLA30-10 tem o mesmo N e portadora de TDLA30-5)
        for cond in sorted(p.name for p in (pasta / "dados").iterdir()):
            n, fc = condicoes[cond]
            ref_pasta = pasta_referencia(cond)
            ref = json.loads((ref_pasta / f"{STEM}_results.json").read_text())
            resultados, grade = {}, None
            for rotulo in ref:
                k = TCC_CONFIGURATION[rotulo]
                arq = pasta / "dados" / cond / f"configuracao_{k}" / f"{I}_{F}_{q}_{o}.json"
                if not arq.exists():
                    raise SystemExit(f"falta {arq}")
                d = json.loads(arq.read_text())
                if grade is None:
                    grade = d["snr_db"]
                # Mesma grade da referência: a comparação ponto a ponto vale
                assert d["snr_db"] == grade and len(ref[rotulo]["LMMSE"]) == len(grade), arq
                assert (d["int_bits"], d["frac_bits"], d["quant"], d["overflow"]) == (I, F, q, o)
                resultados[rotulo] = {"LMMSE": ref[rotulo]["LMMSE"], "ZF": ref[rotulo]["ZF"],
                                      **{c: d["ser"][c] for c in BCD}}
            paineis = [p for p in ALL_PANELS if p.label in resultados]
            cfg = SimConfig.from_panel(paineis[0], n_noise_samples=n, carrier_hz=fc,
                                       bcd_iteration_list=ITERACOES, bcd_inverse="hls",
                                       hw_int_bits=I, hw_frac_bits=F, hw_quant=q,
                                       hw_overflow=o)
            png, _ = save_figure8(resultados, paineis, grade,
                                  pasta / "figuras" / nome / ref_pasta.name,
                                  subtitle=figure_subtitle(cfg, ref_pasta.name.split("_")[0]),
                                  curves=curve_names(cfg), bcd_iterations=ITERACOES,
                                  stem=STEM)
            print(png)


if __name__ == "__main__":
    main()
