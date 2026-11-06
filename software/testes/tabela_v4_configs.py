#!/usr/bin/env python3
"""
Preenche varredura_formatos_sintese_all_configs.csv da [4] v4: para cada formato (linha) e
configuração (coluna), o melhor modo de quantização e estouro por dois critérios, perda até
3 dB e perda até 0,1 dB. Para cada critério: os cenários em que o modo fica dentro do limite,
o modo, a perda em dB em cada cenário e a maior ocupação da XCU50 (síntese HLS 16 x 16 do
mesmo formato e modo; 32 x 32 nas configurações 9 a 12). Um bloco com 1 iteração e outro com 4.

Melhor modo de cada critério, nesta ordem:
1. o que fica dentro do limite (perda arredondada a 0,01 dB <= limite, sem ×) em mais cenários;
2. entre esses, o de menor ocupação;
3. depois AP_RND_ZERO (a preferência da tabela restricoes_varredura_4.csv), depois a menor
   pior perda nesses cenários, depois a ordem dos modos (quantização TRN, TRN_ZERO, RND, ...;
   estouro SAT, SAT_ZERO, ...).

Só entram as configurações com todas as rodadas (os 10 formatos, 35 modos e 5 cenários).
Uso (com o Python do simulador):
    ../simulador/.venv/bin/python tabela_v4_configs.py
"""

import csv

from figuras_formatos import OVERFLOWS, QUANTS, ler, perdas
from pareto_modos import ABREV, CONDS
from pareto_v4 import CIRCUITOS, FORMATOS, N_MODOS, V4, ocupacao

SAIDA = V4 / "varredura_formatos_sintese_all_configs.csv"
CONFIGS = [*range(1, 9), *range(13, 17), *range(9, 13)]   # 16 x 16 primeiro, 32 x 32 no fim
MODOS = [(q, o) for q in QUANTS for o in OVERFLOWS]
CENARIOS = [c for c, _ in CONDS]
CRITERIOS = ((3, "até 3 dB"), (0.1, "até 0,1 dB"))


def num(v: float) -> str:
    return f"{v:.2f}".replace(".", ",")


def melhor(p, occ, k, I, F, limite):
    """(modo, cenários dentro do limite, {cenário: perda ou None}) do melhor modo, ou None se
    nenhum modo fica dentro do limite em algum cenário."""
    casos = []
    for q, o in MODOS:
        vs = {c: p[(k, c, I, F, q, o)] for c in CENARIOS}
        ok = [c for c in CENARIOS if vs[c] is not None and round(vs[c], 2) <= limite]
        if ok:
            casos.append(((q, o), ok, vs, max(vs[c] for c in ok)))
    if not casos:
        return None
    casos.sort(key=lambda c: (-len(c[1]), round(occ[(I, F, *c[0])][0], 3),
                              c[0][0] != "AP_RND_ZERO", c[3], MODOS.index(c[0])))
    return casos[0][:3]


def main():
    rodadas = ler(V4)
    contagem = {}
    for d in rodadas:
        contagem[d["configuracao"]] = contagem.get(d["configuracao"], 0) + 1
    configs = [k for k in CONFIGS if contagem.get(k) == len(FORMATOS) * N_MODOS * len(CENARIOS)]
    occ_n = {n: ocupacao(n) for n in CIRCUITOS}
    occ_k = {k: occ_n[n] for n, ks in CIRCUITOS.items() for k in ks}
    linhas = [[], ["", "", "", "", "CONFIGURAÇÕES"]]
    for t in (1, 4):
        p = perdas(rodadas, f"BCD-MMSE (iter {t})")
        linhas += [[], ["", f"{t} {'iterações' if t > 1 else 'iteração'}", "Critério", ""]
                   + [str(k) for k in configs]]
        for I, F in FORMATOS:
            nome = f"<{I + F},{I}>"
            for limite, rotulo in CRITERIOS:
                cen, modo, perda, ocup = [], [], [], []
                for k in configs:
                    m = melhor(p, occ_k[k], k, I, F, limite)
                    if m is None:
                        cen.append("nenhum")
                        modo += ["-"]; perda += ["-"]; ocup += ["-"]
                        continue
                    (q, o), ok, vs = m
                    fora = [c for c in CENARIOS if c not in ok]
                    cen.append("todos (5)" if not fora
                               else "\n".join(ok) + "\n(fora: " + ", ".join(fora) + ")")
                    modo.append(f"{ABREV[q]}/{ABREV[o]}")
                    perda.append("\n".join(f"{c}: {'×' if vs[c] is None else num(vs[c])}"
                                           for c in CENARIOS))
                    pct, rec = occ_k[k][(I, F, q, o)]
                    ocup.append(f"{num(pct)}% ({rec.replace('_18K', '')})")
                linhas += [["", nome, rotulo, "Cenários"] + cen, ["", "", "", "Modos"] + modo,
                           ["", "", "", "Perda em dB"] + perda, ["", "", "", "Maior ocupação"] + ocup]
                nome = ""
    linhas += [[], ["", "Melhor modo de cada critério: o que fica dentro do limite (perda <= 3 dB "
                    "ou <= 0,1 dB, sem ×) em mais cenários; entre esses, o de menor ocupação; depois "
                    "AP_RND_ZERO; depois a menor pior perda. Cenários: onde esse modo fica dentro do "
                    "limite; fora: × ou perda acima do limite; nenhum: nenhum modo fica dentro do limite "
                    "em nenhum cenário. Ocupação: maior % da XCU50 entre LUT, DSP, FF e BRAM, síntese "
                    "HLS 16 x 16 (32 x 32 nas configurações 9 a 12). Perda: dB de SNR em SER = 10^-2 "
                    "contra o float64. TDLA30-5 vale também para TDLA30-10. Configurações com dados "
                    f"completos: {', '.join(map(str, configs))}."]]
    with open(SAIDA, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh, lineterminator="\r\n").writerows(linhas)
    print(f"{SAIDA}: configurações {configs}")


if __name__ == "__main__":
    main()
