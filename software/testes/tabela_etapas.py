"""Tabelas do apêndice com a porcentagem de cada etapa em LUT, DSP e potência dinâmica, formato a formato.

Mesmos dados da Figura etapas_dominantes (hardware/etapas/etapas_dominantes.csv), sem a média entre formatos.
Saída: hardware/resultados_servidor/tabelas/tabela_etapas.tex (colar em chapters/APENDICE/recursos.tex).
"""
import csv
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent.parent / "hardware" / "etapas" / "etapas_dominantes.csv"
SAIDA = AQUI.parent.parent / "hardware" / "resultados_servidor" / "tabelas" / "tabela_etapas.tex"

FORMATOS = [("18-8", r"$\langle 18,8\rangle$"), ("18-8-TRN-SAT", r"$\langle 18,8\rangle$$^{*}$"),
            ("20-8", r"$\langle 20,8\rangle$"), ("22-12", r"$\langle 22,12\rangle$"),
            ("24-12", r"$\langle 24,12\rangle$"), ("26-12", r"$\langle 26,12\rangle$"),
            ("28-14", r"$\langle 28,14\rangle$"), ("30-14", r"$\langle 30,14\rangle$$^{*}$")]
ARQS = [("sem_otimizacao", r"Without opt., 16 $\times$ 16"), ("sem_otimizacao_32x32", r"Without opt., 32 $\times$ 32"),
        ("9090", "TDLA30-5"), ("4545", "TDLA30-10"), ("606", "TDLA30-75"), ("455", "TDLC300-100"),
        ("152_sistolico", "TDLA30-300"), ("114_sistolico", "TDLB100-400")]
ETAPAS = [("lu", "LU"), ("df", "D and F"), ("fs", "Forward subst."), ("inv", "Inversion"),
          ("restante", "Other")]
GRANDEZAS = [("lut", "tab:etapas-lut", "Porcentagem das LUTs usada por cada etapa da inversão, por arquitetura e formato."),
             ("dsp", "tab:etapas-dsp", "Porcentagem dos DSPs usada por cada etapa da inversão, por arquitetura e formato."),
             ("pdin_w", "tab:etapas-potencia", "Porcentagem da potência dinâmica usada por cada etapa da inversão, por arquitetura e formato.")]


def ler():
    d = defaultdict(dict)
    for r in csv.DictReader(open(DADOS)):
        t = float(r["total"])
        d[(r["grandeza"], r["arquitetura"])][r["formato"]] = (
            {e: 100 * float(r[e]) / t for e, _ in ETAPAS} if t else None)
    return d


def tabela(d, g, rotulo, titulo):
    cab = " & ".join([r"\textbf{Architecture}", r"\textbf{Step}"] + [rf"\textbf{{{n}}}" for _, n in FORMATOS])
    out = [r"\begin{table}[htbp]", rf"\caption{{\textcolor{{red}}{{{titulo}}}}}", rf"\label{{{rotulo}}}",
           r"\vspace{4pt} % a classe zera o espaço entre a caption e a tabela", r"\centering", r"\scriptsize",
           r"\color{red}", r"\renewcommand{\arraystretch}{1.05}", r"\setlength{\tabcolsep}{3pt}",
           r"\begin{tabular}{llcccccccc}", r"\toprule", cab + r" \\", r"\midrule"]
    blocos = [a for a in ARQS if d.get((g, a[0]))]
    for i, (arq, nome) in enumerate(blocos):
        for j, (e, ne) in enumerate(ETAPAS):
            cel = []
            for fmt, _ in FORMATOS:
                v = d[(g, arq)].get(fmt)
                cel.append("--" if v is None else f"{v[e]:.0f}")
            pre = rf"\multirow{{{len(ETAPAS)}}}{{*}}{{{nome}}}" if j == 0 else ""
            out.append(" & ".join([pre, ne] + cel) + r" \\")
        if i < len(blocos) - 1:
            out.append(r"\midrule")
    out += [r"\bottomrule", r"\end{tabular}", r"\vspace{4pt}",
            r"\legend{\textcolor{red}{Fonte: a autora. Vivado, projeto roteado. Other: memórias entre as etapas e controle. "
            r"$^{*}$\texttt{AP\_TRN}/\texttt{AP\_SAT}; os outros, \texttt{AP\_RND\_ZERO}/\texttt{AP\_WRAP}. "
            r"--: não cabe no FPGA" + (r" ou sem DSP" if g == "dsp" else "") + ".}}",
            r"\end{table}"]
    return "\n".join(out)


def main():
    d = ler()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n\n".join(tabela(d, *gr) for gr in GRANDEZAS) + "\n")
    print(SAIDA)


if __name__ == "__main__":
    main()
