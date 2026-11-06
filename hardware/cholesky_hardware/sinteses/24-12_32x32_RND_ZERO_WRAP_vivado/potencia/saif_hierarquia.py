"""Põe o SAIF do xsim na hierarquia do projeto roteado: o testbench do HLS chama o
inversor de apatb_cholesky_inverse_top/AESL_inst_cholesky_inverse, e no projeto
fora de contexto ele é bd_0_i/hls_inst/inst. O potencia.tcl tira o primeiro nível
(-strip_path apatb_cholesky_inverse_top).
Uso: python3 saif_hierarquia.py <saif do xsim> <saif de saída>"""
import sys

linhas = open(sys.argv[1]).read().split("\n")
assert linhas[11].strip() == "(INSTANCE  apatb_cholesky_inverse_top"
assert linhas[12].strip() == "(INSTANCE  AESL_inst_cholesky_inverse"
linhas[12] = "      (INSTANCE  bd_0_i\n      (INSTANCE  hls_inst\n      (INSTANCE  inst"
while linhas[-1].strip() == "":
    linhas.pop()
assert linhas[-1].strip() == ")"
linhas.insert(len(linhas) - 1, ")\n)")
open(sys.argv[2], "w").write("\n".join(linhas) + "\n")
