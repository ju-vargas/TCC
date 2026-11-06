#!/usr/bin/env python3
"""
Células (formato, modo) do mapa de perda da [4] v2 que vão para a síntese HLS
(sintetizar_v2.sh). Em cada linha do mapa (I com F = 32; F com I = 14), entram as
colunas até a primeira com perda zero em tudo (< 0,05 dB em todos os modos,
configurações, pares e em 1 e 4 iterações), inclusive. Nessas colunas, entra cada célula
com perda <= 6 dB em algum caso; as que dão × em todos os casos ou passam de 6 dB em
todos ficam de fora.

Escreve uma célula por linha, como I:F:QUANT:ESTOURO (a entrada de sintetizar_formatos.py).

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python celulas_sintese.py resultados/4_varredura_formatos/v2_casos_extremos
"""

import sys
from pathlib import Path

from figuras_formatos import ler, perdas

LIMITE, ZERO, ITERACOES = 6.0, 0.05, (1, 4)


def main():
    rodadas = ler(Path(sys.argv[1]))
    valores = {}
    for it in ITERACOES:
        for (_, _, I, F, q, o), v in perdas(rodadas, f"BCD-MMSE (iter {it})").items():
            valores.setdefault((I, F), {}).setdefault((q, o), []).append(v)
    linhas = {"I (F = 32)": sorted(f for f in valores if f[1] == 32),
              "F (I = 14)": sorted(f for f in valores if f[0] == 14)}
    escolhidas = []
    for nome, formatos in linhas.items():
        for fmt in formatos:
            modos = valores[fmt]
            escolhidas += [(fmt, m) for m, vs in modos.items()
                           if any(v is not None and v <= LIMITE for v in vs)]
            if all(v is not None and v < ZERO for vs in modos.values() for v in vs):
                print(f"linha {nome}: até <{sum(fmt)},{fmt[0]}>", file=sys.stderr)
                break
    for (I, F), (q, o) in dict.fromkeys(escolhidas):
        print(f"{I}:{F}:{q}:{o}")


if __name__ == "__main__":
    main()
