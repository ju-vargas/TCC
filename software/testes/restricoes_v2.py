#!/usr/bin/env python3
"""
Preenche restricoes_varredura_4.csv (na pasta da [4] v2) a partir dos mesmos dados dos
mapas de perda (1 e 4 iterações). Para cada cenário, configuração e lado do mapa (I com
F = 32, escolhendo I e estouro; F com I = 14, escolhendo F e quantização):
  linha 1: a combinação de menor ocupação com perda <= 3 dB;
  linha 2: a combinação de menor ocupação com perda <= 0,1 dB.
Ocupação = maior % da XCU50 entre LUT, DSP, FF e BRAM, da síntese do mesmo formato e modo.
Perda e ocupação são comparadas com o arredondamento do mapa (0,01 dB e 0,1 %).

Quando AP_RND_ZERO e AP_RND_INF empatam na ocupação (mesmo formato e estouro), fica
AP_RND_ZERO: as duas dão os mesmos DSP, FF e BRAM, e AP_RND_ZERO usa 44 LUTs a menos.
AP_RND_INF perde até 0,04 dB a menos, e AP_RND_ZERO continua dentro dos dois limites.

Desempate, nesta ordem:
  1. maior repetição: a opção (formato e modo do lado) que empata em mais células da tabela;
  2. no lado de F, AP_RND_ZERO, a quantização que mais se repete na tabela (decide só em
     TDLB100-400, 4 iterações, configurações 10 e 12, F = 14, contra AP_TRN, que perde
     0,06 dB contra 0,09 dB);
  3. menor perda;
  4. a ordem dos modos no mapa.
O modo do outro lado (quantização no lado de I, estouro no lado de F) não vai para a
tabela; ele fica em restricoes_varredura_4_detalhe.csv.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python restricoes_v2.py
"""

import csv
from collections import Counter
from pathlib import Path

from figuras_formatos import OVERFLOWS, QUANTS, ler, ocupacao, perdas

AQUI = Path(__file__).resolve().parent
V2 = AQUI / "resultados" / "4_varredura_formatos" / "v2_casos_extremos"
TABELA = V2 / "restricoes_varredura_4.csv"
DETALHE = V2 / "restricoes_varredura_4_detalhe.csv"
LIMITES = (3.0, 0.1)
ORDEM = {m: k for k, m in enumerate((q, o) for q in QUANTS for o in OVERFLOWS)}


def candidatos(p, occ, cond, k, lado, limite):
    """[(ocupação, perda, opção, (I, F, q, o))] que passam no limite; opção = (I, estouro)
    no lado de I e (F, quantização) no lado de F."""
    saida = []
    for (cfg, c, I, F, q, o), v in p.items():
        no_lado = F == 32 if lado == "I" else I == 14
        if cfg == k and c == cond and no_lado and v is not None and round(v, 2) <= limite \
                and (I, F, q, o) in occ:
            opcao = (I, o) if lado == "I" else (F, q)
            saida.append((round(occ[(I, F, q, o)], 1), round(v, 2), opcao, (I, F, q, o)))
    return saida


def main():
    rodadas = ler(V2)
    occ = ocupacao()
    linhas = list(csv.reader(TABELA.open(encoding="utf-8")))
    # Cada bloco: a linha do título tem o nome do cenário nas colunas 2 (1 it) e 12 (4 it)
    celulas = []   # (linha da tabela, coluna inicial, iteração, cenário, config, lado, limite)
    for n, lin in enumerate(linhas):
        if len(lin) > 2 and "ITERAÇ" in lin[1]:
            for col, it in ((1, 1), (11, 4)):
                cond = lin[col + 1].split()[0]
                for m in range(n + 2, n + 12):
                    k = int(linhas[m][col])
                    limite = LIMITES[(m - n - 2) % 2]
                    celulas += [(m, col, it, cond, k, lado, limite) for lado in ("I", "F")]
    p = {it: perdas(rodadas, f"BCD-MMSE (iter {it})") for it in (1, 4)}
    cand = {c: candidatos(p[c[2]], occ, *c[3:]) for c in celulas}
    empates = {}
    for c, cs in cand.items():
        menor = min(x[0] for x in cs)
        es = [x for x in cs if x[0] == menor]
        zero = {x[3][:2] + x[3][3:] for x in es if x[3][2] == "AP_RND_ZERO"}
        empates[c] = [x for x in es if not (x[3][2] == "AP_RND_INF" and x[3][:2] + x[3][3:] in zero)]
    repeticao = Counter((c[5], x[2]) for c, es in empates.items() for x in {e[2]: e for e in es}.values())
    detalhe = []
    for c in celulas:
        m, col, it, cond, k, lado, limite = c
        es = empates[c]
        oc, v, opcao, (I, F, q, o) = min(es, key=lambda x: (-repeticao[(lado, x[2])],
                                                             lado == "F" and x[2][1] != "AP_RND_ZERO", x[1],
                                                             ORDEM[x[3][2:]], x[3][0] + x[3][1]))
        base = col + 1 if lado == "I" else col + 5
        linhas[m][base:base + 4] = [str(I if lado == "I" else F), o if lado == "I" else q,
                                    f"{v:.2f}".replace(".", ","), f"{oc:.1f}".replace(".", ",")]
        outras = sorted({x[2] for x in es} - {opcao})
        detalhe.append({"iteracoes": it, "cenario": cond, "configuracao": k, "lado": lado,
                        "limite_db": limite, "formato": f"<{I + F},{I}>", "quant": q,
                        "estouro": o, "perda_db": v, "ocupacao_pct": oc,
                        "empatadas_na_ocupacao": " ".join(f"{a}/{b}" for a, b in outras)})
    with TABELA.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh, lineterminator="\n").writerows(linhas)
    with DETALHE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(detalhe[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(detalhe)
    print(f"{TABELA}: {len(celulas)} células; {DETALHE}")


if __name__ == "__main__":
    main()
