"""Ajusta a netlist do write_verilog -mode funcsim para o testbench do HLS: o módulo de
cima passa a se chamar cholesky_inverse (o nome que o testbench instancia) e sai o
módulo glbl do fim do arquivo, que já vem no glbl.v da simulação.
Uso: python3 limpar_netlist.py <netlist bruta> <netlist de saída>"""
import re
import sys

linhas = open(sys.argv[1]).read().split("\n")
topo = [i for i, l in enumerate(linhas) if re.fullmatch(r"module bd_0_hls_inst_0_cholesky_inverse\s*", l)]
assert len(topo) == 1, topo
linhas[topo[0]] = "module cholesky_inverse"
glbl = [i for i, l in enumerate(linhas) if l.startswith("`ifndef GLBL")]
assert len(glbl) == 1 and any(l.startswith("module glbl") for l in linhas[glbl[0]:]), glbl
open(sys.argv[2], "w").write("\n".join(linhas[:glbl[0]]).rstrip() + "\n")
