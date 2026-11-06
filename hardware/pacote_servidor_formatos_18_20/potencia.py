#!/usr/bin/env python3
"""
Potência de uma versão do pacote, depois da etapa vivado (rodar.sh). Mesmo fluxo de
hardware/potencia_versoes.py, mas sem o HLS: o testbench e os vetores de cada cenário já vêm
prontos do HLS 2026.1 (versoes/<versão>/sim e cenarios/<cenário>/tv).

Para cada cenário:
1. copia a simulação e os vetores, e põe a netlist roteada no lugar do RTL;
2. simula a netlist no xsim e grava o SAIF;
3. confere que as inversas da netlist são iguais, byte a byte, às do C (um arquivo por porta);
4. tira o "\\ " do fim dos nomes escapados do SAIF (sem isso o read_saif não acha parte das redes);
5. lê o SAIF no projeto roteado e roda o report_power.

ciclos_medios = duração da simulação / número de matrizes (inclui o enchimento do pipeline).
Resultados em versoes/<versão>/trabalho/potencia/. Chamado pelo rodar.sh:
    python3 potencia.py <versão> [--nucleos 0-7] [--cenarios TDLA30-5,...]
Sem --cenarios, roda os cenários que a versão tem em cenarios/ (as arquiteturas otimizadas só
o do seu alvo; a versão sem otimização os 5).
"""

import argparse
import csv
import re
import shlex
import shutil
import subprocess
from pathlib import Path

PACOTE = Path(__file__).resolve().parent
PERIODO_NS = 10.0
ORDEM = ["TDLA30-5", "TDLA30-10", "TDLA30-75", "TDLA30-300", "TDLC300-100", "TDLB100-400"]
# Bibliotecas do xelab que o testbench usa. As outras do run_xsim.sh do HLS são de IPs de
# AXI e de ponto flutuante, com o número da versão 2026.1 no nome
BIBLIOTECAS = {"xil_defaultlib", "unisims_ver", "xpm", "uvm"}


def sh(cmd: str, cwd: Path, log: Path, nucleos: str) -> None:
    prefixo = f"taskset -c {nucleos} " if nucleos else ""
    with open(log, "w") as fh:
        r = subprocess.run(["bash", "-c", prefixo + cmd], cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise SystemExit(f"falhou ({r.returncode}): {cmd} (ver {log})")


def comandos_xsim(run_xsim: str) -> str:
    """xelab e xsim do run_xsim.sh do HLS, com os executáveis do PATH (2023.2), só as
    bibliotecas de BIBLIOTECAS, -debug typical (para o SAIF) e o saif.tcl."""
    linhas = [shlex.split(l) for l in run_xsim.splitlines() if re.search(r"/(xelab|xsim) ", l)]
    assert len(linhas) == 2, run_xsim
    xelab, xsim = linhas
    args = ["xelab"]
    i = 1
    while i < len(xelab):
        if xelab[i] == "-L":
            if xelab[i + 1] in BIBLIOTECAS:
                args += xelab[i:i + 2]
            i += 2
            continue
        if xelab[i] == "-s":
            args += ["-debug", "typical"]
        args.append(xelab[i])
        i += 1
    xsim = ["xsim"] + xsim[1:]
    j = xsim.index("-tclbatch")
    xsim[j + 1] = "saif.tcl"
    junta = lambda c: " ".join(shlex.quote(x) for x in c)  # shlex.join só existe a partir do Python 3.8
    return "set -e\n" + junta(args) + "\n" + junta(xsim) + "\n"


def preparar(versao: Path, cen: str, destino: Path, netlist: Path) -> None:
    """Pasta do cenário: sim/ (testbench + netlist) e tv/ (vetores), como o HLS espera."""
    if destino.exists():
        shutil.rmtree(destino)
    sim = destino / "sim"
    shutil.copytree(versao / "sim", sim)
    shutil.copytree(versao / "cenarios" / cen / "tv", destino / "tv")
    (destino / "tv" / "rtldatafile").mkdir()
    shutil.copy(netlist, sim / "netlist_roteada.v")
    # O RTL do HLS já não está na pasta; as linhas dele saem do prj
    prj = [l for l in (sim / "cholesky_inverse.prj").read_text().splitlines()
           if not re.search(r'"cholesky_inverse(_[^"]*)?\.v"', l)]
    (sim / "cholesky_inverse.prj").write_text(
        "\n".join(prj + ['verilog xil_defaultlib "netlist_roteada.v"']) + "\n")
    # O monitor e o detector de deadlock do HLS olham sinais internos do RTL, que a netlist não tem
    (sim / "dataflow_monitor.sv").write_text(
        "`timescale 1ns/1ps\nmodule dataflow_monitor(input logic clock, input logic reset, "
        "input logic finish);\nendmodule\n")
    if (sim / "AESL_deadlock_detector.v").exists():
        (sim / "AESL_deadlock_detector.v").write_text(
            "`timescale 1ns/1ps\nmodule AESL_deadlock_detector(input dl_reset, input all_finish, "
            "input dl_clock);\nendmodule\n")
    # Com "#pragma HLS dependence", o testbench confere as dependencias olhando sinais internos
    # do RTL. O HLS deixa essa conferencia dentro de `ifndef POST_SYN, para simular netlists
    tb = sim / "cholesky_inverse.autotb.v"
    tb.write_text("`define POST_SYN\n" + tb.read_text())
    # Um log_saif por escopo: o get_objects -r de tudo de uma vez leva horas em netlists grandes.
    # current_scope em vez de "$s/*": nos escopos de generate (gen_buffer[1]....) os colchetes
    # viram curinga e o padrão não acha os sinais (na 4545, 158 redes ficavam sem atividade)
    raiz = "/apatb_cholesky_inverse_top/AESL_inst_cholesky_inverse"
    (sim / "saif.tcl").write_text(
        "open_saif atividade.saif\n"
        "set n 0\n"
        f"foreach s [concat [list {raiz}] [get_scopes -r {raiz}/*]] {{\n"
        "  current_scope $s\n"
        "  set o [get_objects *]\n"
        "  if {[llength $o]} { log_saif $o; incr n [llength $o] }\n"
        "}\n"
        'puts "SAIF: $n objetos"\n'
        "run all\nclose_saif\nquit\n")
    (sim / "run_saif.sh").write_text(comandos_xsim((sim / "run_xsim.sh").read_text()))
    (sim / "run_saif.sh").chmod(0o755)


def ler_relatorio(rpt: Path) -> dict:
    t = rpt.read_text()
    num = lambda rotulo: float(re.search(rf"\| {re.escape(rotulo)}\s*\|\s*([0-9.]+)", t).group(1))
    casadas = re.search(r"Design Nets Matched\s*\|\s*(\d+)%\s*\((\d+)/(\d+)\)", t)
    d = {"total_w": num("Total On-Chip Power (W)"), "dinamica_w": num("Dynamic (W)"),
         "estatica_w": num("Device Static (W)"),
         "redes_casadas_pct": int(casadas.group(1)),
         "confianca": re.search(r"Overall confidence level\s*\|\s*(\w+)", t).group(1)}
    for parte, chave in (("Clocks", "relogio_w"), ("CLB Logic", "logica_w"),
                         ("Signals", "sinais_w"), ("Block RAM", "bram_w"), ("DSPs", "dsp_w")):
        d[chave] = num(parte)
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("versao", help="nome da pasta em versoes/ (ex.: 455)")
    p.add_argument("--nucleos", default="", help="núcleos para o taskset (vazio: todos)")
    p.add_argument("--cenarios", default="", help="padrão: os da pasta cenarios/ da versão")
    a = p.parse_args()
    versao = PACOTE / "versoes" / a.versao
    if not a.cenarios:
        a.cenarios = ",".join(c for c in ORDEM if (versao / "cenarios" / c).is_dir())
    viv = versao / "trabalho" / "vivado"
    dcp, netlist = viv / "roteado.dcp", viv / "netlist_roteada.v"
    if not (dcp.exists() and netlist.exists()):
        raise SystemExit(f"sem {dcp} ou {netlist}: rode antes ./rodar.sh {a.versao} vivado")
    aqui = versao / "trabalho" / "potencia"
    aqui.mkdir(parents=True, exist_ok=True)
    (aqui / "potencia.tcl").write_text(
        "# uso: vivado -mode batch -source potencia.tcl -tclargs <saif> <relatorio>\n"
        f"open_checkpoint {dcp}\n"
        "read_saif -strip_path apatb_cholesky_inverse_top/AESL_inst_cholesky_inverse [lindex $argv 0]\n"
        "report_power -file [lindex $argv 1]\n")

    csv_saida = aqui / "potencia.csv"
    tabela = [r for r in csv.DictReader(open(csv_saida))
              if r["cenario"] not in a.cenarios.split(",")] if csv_saida.exists() else []
    for cen in a.cenarios.split(","):
        n_mat = int((versao / "cenarios" / cen / "matrizes.txt").read_text())
        pasta = aqui / cen
        preparar(versao, cen, pasta, netlist)
        print(f"{cen}: simulação da netlist roteada ({n_mat} matrizes)", flush=True)
        sh("./run_saif.sh", pasta / "sim", aqui / f"xsim_{cen}.log", a.nucleos)
        tv = pasta / "tv"
        c_arqs = sorted((tv / "cdatafile").glob("c.cholesky_inverse.autotvout_inverse*.dat"))
        assert c_arqs
        for c in c_arqs:
            r = tv / "rtldatafile" / ("rtl." + c.name[2:])
            if not r.exists() or c.read_bytes() != r.read_bytes():
                raise SystemExit(f"{cen}: as inversas da netlist diferem das do C ({c.name})")
        saif = aqui / f"atividade_{cen}.saif"
        t = (pasta / "sim" / "atividade.saif").read_text()
        saif.write_text(t.replace("\\ ", ""))
        duracao_ps = int(re.search(r"\(DURATION\s+(\d+)\)", t).group(1))
        # A cópia da simulação ocupa espaço (xsim.dir); fica só o log
        shutil.rmtree(pasta)
        rpt = aqui / f"potencia_{cen}.rpt"
        print(f"{cen}: report_power", flush=True)
        sh(f"vivado -mode batch -nojournal -nolog -source {aqui / 'potencia.tcl'} -tclargs {saif} {rpt}",
           aqui, aqui / f"vivado_{cen}.log", a.nucleos)
        d = {"cenario": cen, "matrizes": n_mat, **ler_relatorio(rpt),
             "ciclos_medios": round(duracao_ps / 1000 / PERIODO_NS / n_mat)}
        d["energia_por_inversao_uj"] = round(d["dinamica_w"] * d["ciclos_medios"] * PERIODO_NS * 1e-3, 2)
        tabela.append(d)
        tabela.sort(key=lambda r: ORDEM.index(r["cenario"]))
        print(f"{cen}: {d}", flush=True)
        with open(csv_saida, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(d))
            w.writeheader()
            w.writerows(tabela)


if __name__ == "__main__":
    main()
