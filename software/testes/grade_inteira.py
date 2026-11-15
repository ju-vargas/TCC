#!/usr/bin/env python3
"""
Aumento de SNR do formato na grade inteira de SNR, a mesma das barras de descentralização e
das curvas de SER: ponto fixo das rodadas [5] e referência float da [1], com a mesma semente.

- 16-QAM (configurações 1 a 4 e 9 a 16): grade -10 a 10 dB, referência 1_referencia_float/curvas;
- QPSK do grupo 1 (5 a 8): grade -20 a 10 dB, referência curvas_qpsk_128;
- QPSK dos grupos 2 e 3 (17 a 24): grade -20 a 10 dB, referência curvas_qpsk_256.

O ponto fixo vem das pastas que as barras leem (modo_fixo_3dB, _iot10, _qpsk_128, _qpsk_256)
e, para os formatos que só o mapa e os perfis usam, de modo_fixo_mapa
(rodada6_mapa_grade_inteira.sh). Aumento = max(0, SNR do ponto fixo - SNR do BCD-MMSE float)
em SER = 10^-2 (snr_no_alvo, interpolação em log10), None se um dos dois não chega lá.

Só os modos simulados na grade inteira (o modo fixo de cada formato e grupo) aparecem; a
escolha do modo continua na [4] v4/v5, com os 35 modos.
"""

import json
from functools import lru_cache
from pathlib import Path

from figuras_formatos import snr_no_alvo

AQUI = Path(__file__).resolve().parent
CAND = AQUI / "resultados" / "5_candidatos"
REF = AQUI / "resultados" / "1_referencia_float"
BCD1 = "BCD-MMSE (iter 1)"
QPSK_128 = (5, 6, 7, 8)


def pastas(k):
    if k in QPSK_128:
        base = ["modo_fixo_3dB_qpsk_128"]
    elif k >= 17:
        base = ["modo_fixo_3dB_qpsk_256"]
    else:
        base = ["modo_fixo_3dB", "modo_fixo_3dB_iot10"]
    return [CAND / p / "dados" for p in base + ["modo_fixo_mapa"]]


@lru_cache(maxsize=None)
def referencia(k, cond):
    """(grade, SER do BCD-MMSE float, iteração 1) da configuração k na condição cond."""
    from dbp_sim.params import PANELS_BY_LABEL, TCC_CONFIGURATION
    raiz = REF / ("curvas_qpsk_128" if k in QPSK_128 else
                  "curvas_qpsk_256" if k >= 17 else "curvas")
    pasta = next(p for p in raiz.iterdir() if cond in p.name.split("_")[0].split("+"))
    tudo = json.loads((pasta / "bcd_iterations_results.json").read_text())
    rotulo = PANELS_BY_LABEL[next(l for l in PANELS_BY_LABEL if TCC_CONFIGURATION.get(l) == k)].label
    return tuple(tudo.get("snr_db", range(-10, 11, 2))), tuple(tudo[rotulo][BCD1])


def arquivo(k, cond, I, F, q, o):
    nome = f"{I}_{F}_{q}_{o}.json"
    return next((p / cond / f"configuracao_{k}" / nome for p in pastas(k)
                 if (p / cond / f"configuracao_{k}" / nome).exists()), None)


def perda(k, cond, I, F, q, o):
    """Aumento de SNR em dB, None se não atinge SER = 10^-2; KeyError se não foi simulado."""
    arq = arquivo(k, cond, I, F, q, o)
    if arq is None:
        raise KeyError((k, cond, I, F, q, o))
    d = json.loads(arq.read_text())
    grade, sr = referencia(k, cond)
    assert tuple(d["snr_db"]) == grade, arq     # mesma grade e mesmos sorteios da referência
    xr, xh = snr_no_alvo(grade, sr), snr_no_alvo(d["snr_db"], d["ser"][BCD1])
    return None if xr is None or xh is None else max(0.0, xh - xr)


class Perdas(dict):
    """Dicionário {(config, cond, I, F, q, o): aumento} preenchido sob demanda, com as mesmas
    chaves de figuras_formatos.perdas."""

    def __missing__(self, chave):
        v = perda(*chave)
        self[chave] = v
        return v
