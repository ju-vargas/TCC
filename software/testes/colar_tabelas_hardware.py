#!/usr/bin/env python3
"""Troca, em TCC/chapters/RESULTADOS/hardware.tex, compromisso.tex e APENDICE/recursos.tex, cada tabela gerada por
analise_potencia_qualidade.py (hardware/resultados_servidor/tabelas/*.tex) pela versão nova,
pelo \\label. Só as tabelas do script; o texto em volta não muda.

Uso: python3 colar_tabelas_hardware.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVOS = [RAIZ / "TCC" / "chapters" / "RESULTADOS" / "hardware.tex",
            RAIZ / "TCC" / "chapters" / "RESULTADOS" / "compromisso.tex",
            RAIZ / "TCC" / "chapters" / "APENDICE" / "recursos.tex"]
textos = {a: a.read_text() for a in ARQUIVOS}
for arq in sorted((RAIZ / "hardware" / "resultados_servidor" / "tabelas").glob("tabela_*.tex")):
    novo = arq.read_text().rstrip()
    label = re.search(r"\\label\{([^}]+)\}", novo).group(1)
    padrao = re.compile(r"\\begin\{table\}\[[a-z!]+\]\n\\caption\{[^\n]*\}\n\\label\{" + re.escape(label)
                        + r"\}.*?\\end\{table\}", re.S)
    n = 0
    for a in ARQUIVOS:
        textos[a], k = padrao.subn(lambda m: novo, textos[a])
        n += k
    print(label, "trocada" if n else "não achada")
for a, s in textos.items():
    a.write_text(s)
