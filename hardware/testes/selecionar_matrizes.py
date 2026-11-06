#!/usr/bin/env python3
"""
Seleciona, dentre as matrizes amostradas em 2_amostra_matrizes/, as que vão para a validação
bit a bit (C-simulation do Vitis contra a inversão do simulador).

Para cada par (N, portadora), tamanho e configuração, entra uma matriz de cobertura
em cada SNR de --snr (a de menor realização e cluster entre as de cobertura daquele
ponto), mais todas as matrizes que entraram na amostra como extremo de alguma
métrica. Os arquivos (.txt e .bits) são copiados para
3_selecao_matrizes/<par>/<n>x<n>/, com um indice.csv próprio, que repete as colunas do
indice.csv da amostra e acrescenta "selecao" (o motivo da escolha).

Uso (com o Python do simulador):
    PY=../../software/simulador/.venv/bin/python
    $PY selecionar_matrizes.py                     # todos os pares, SNR -10,-6,-2,2,6,10
    $PY selecionar_matrizes.py --snr=-10,0,10 --pares amostras24_fc3.5GHz
"""

import argparse
import csv
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def selecionar(pasta: Path, snrs: list[int]) -> list[dict]:
    """Linhas do indice.csv da amostra escolhidas para a validação, com "selecao"."""
    with open(pasta / "indice.csv", newline="") as fh:
        linhas = list(csv.DictReader(fh))
    escolhidas: dict[str, dict] = {}

    def marcar(linha, motivo):
        atual = escolhidas.setdefault(linha["arquivo"], {**linha, "selecao": ""})
        partes = [m for m in atual["selecao"].split("+") if m]
        if motivo not in partes:
            atual["selecao"] = "+".join(partes + [motivo])

    cobertura = [l for l in linhas if "cobertura" in l["motivo"].split("+")]
    for painel in sorted({l["rotulo"] for l in linhas}):
        for x in snrs:
            pontos = [l for l in cobertura if l["rotulo"] == painel and int(l["snr_db"]) == x]
            if pontos:
                marcar(min(pontos, key=lambda l: (int(l["realizacao"]), int(l["cluster"]))),
                       f"cobertura_snr{x:+d}")
    for l in linhas:
        if any(m != "cobertura" for m in l["motivo"].split("+")):
            marcar(l, "extremo")
    return list(escolhidas.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("-m", "--matrizes", default=str(AQUI / "2_amostra_matrizes"),
                        help="Pasta da amostra (padrão: 2_amostra_matrizes/)")
    parser.add_argument("-o", "--saida", default=str(AQUI / "3_selecao_matrizes"),
                        help="Pasta da seleção (padrão: 3_selecao_matrizes/); é refeita do zero")
    parser.add_argument("--snr", default="-10,-6,-2,2,6,10",
                        help="SNRs da cobertura, com '=' por causa do sinal: --snr=-10,0,10 "
                             "(padrão: -10,-6,-2,2,6,10)")
    parser.add_argument("--pares", default=None,
                        help="Pares (N, portadora), ex. amostras24_fc3.5GHz (padrão: todos)")
    args = parser.parse_args()

    snrs = [int(x) for x in args.snr.split(",") if x.strip()]
    raiz = Path(args.matrizes)
    pares = (sorted(p.name for p in raiz.iterdir() if p.is_dir()) if not args.pares
             else [p.strip() for p in args.pares.split(",") if p.strip()])
    saida = Path(args.saida)
    if saida.exists():
        shutil.rmtree(saida)

    for par in pares:
        for pasta in sorted((raiz / par).glob("*x*")):
            linhas = selecionar(pasta, snrs)
            destino = saida / par / pasta.name
            destino.mkdir(parents=True)
            for l in linhas:
                for ext in (".txt", ".bits"):
                    shutil.copy2(pasta / f"{l['arquivo']}{ext}", destino / f"{l['arquivo']}{ext}")
            colunas = list(linhas[0].keys())
            with open(destino / "indice.csv", "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=colunas)
                w.writeheader()
                w.writerows(sorted(linhas, key=lambda l: l["arquivo"]))
            acima = sum(1 for l in linhas if float(l["max_abs_parte"]) > 128)
            print(f"  {par}/{pasta.name}: {len(linhas)} matrizes "
                  f"({len(linhas) - acima} com todas as partes até 128)")


if __name__ == "__main__":
    main()
