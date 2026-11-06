#!/usr/bin/env python3
"""
Potência de uma versão do pacote (versoes/<versão>), depois do Vivado (rodar.sh vivado).
Mesmo fluxo de cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/potencia/rodar_potencia.py
e de hardware/potencia_versoes.py:

1. prepara a co-simulação do HLS (cosim.setup) na pasta de trabalho do Vivado, com o
   tb_potencia.cpp da versão e a lista de 20 matrizes do cenário (listas/);
2. gera a netlist roteada (write_verilog -mode funcsim) e troca o RTL do HLS por ela;
3. simula a netlist no xsim e grava o SAIF;
4. confere que as inversas da netlist são iguais, byte a byte, às do C (um arquivo por porta);
5. lê o SAIF no projeto roteado e roda o report_power.

O tb_potencia inverte lotes inteiros (pelo menos 3), então o número de matrizes sai da linha
"POTENCIA N matrizes" do testbench, e ciclos_medios = duração da simulação / N (inclui o
enchimento do pipeline).

Resultados em versoes/<versão>/trabalho/potencia/. Chamado pelo rodar.sh, que passa o settings64.sh do
Vitis e os núcleos:
    python3 potencia.py <versão> --vitis <settings64.sh> [--nucleos 0-7] [--cenarios ...]
"""

import argparse
import csv
import re
import shutil
import subprocess
from pathlib import Path

PACOTE = Path(__file__).resolve().parent
PERIODO_NS = 10.0
ORDEM = ["TDLA30-5", "TDLA30-75", "TDLA30-300", "TDLC300-100", "TDLB100-400"]


def sh(cmd: str, cwd: Path, log: Path, vitis: str, nucleos: str) -> None:
    prefixo = f"taskset -c {nucleos} " if nucleos else ""
    with open(log, "w") as fh:
        r = subprocess.run(["bash", "-c", f"source {vitis} >/dev/null 2>&1 && {prefixo}{cmd}"],
                           cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise SystemExit(f"falhou ({r.returncode}): {cmd} (ver {log})")


def preparar_netlist(sim: Path, destino: Path, netlist: Path) -> None:
    """Copia a simulação do cosim.setup e põe a netlist roteada no lugar do RTL."""
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(sim / "verilog", destino, ignore=shutil.ignore_patterns("xsim.dir", "*.saif"))
    # O write_verilog dá ao topo o nome bd_0_hls_inst_0_cholesky_inverse; o testbench do HLS
    # instancia cholesky_inverse
    texto = netlist.read_text()
    texto, n = re.subn(r"^module bd_0_hls_inst_0_cholesky_inverse$", "module cholesky_inverse",
                       texto, count=1, flags=re.M)
    assert n == 1, "topo da netlist nao encontrado"
    (destino / "netlist_roteada.v").write_text(texto)
    prj = [l for l in (destino / "cholesky_inverse.prj").read_text().splitlines()
           if not re.search(r'"cholesky_inverse(_[^"]*)?\.v"', l)]
    (destino / "cholesky_inverse.prj").write_text(
        "\n".join(prj + ['verilog xil_defaultlib "netlist_roteada.v"']) + "\n")
    # O monitor do HLS olha sinais internos do RTL, que a netlist não tem
    (destino / "dataflow_monitor.sv").write_text(
        "`timescale 1ns/1ps\nmodule dataflow_monitor(input logic clock, input logic reset, "
        "input logic finish);\nendmodule\n")
    # Com dataflow, o detector de deadlock do testbench tambem olha sinais internos do RTL
    if (destino / "AESL_deadlock_detector.v").exists():
        (destino / "AESL_deadlock_detector.v").write_text(
            "`timescale 1ns/1ps\nmodule AESL_deadlock_detector(input dl_reset, input all_finish, "
            "input dl_clock);\nendmodule\n")
    # O testbench abre os vetores em ../tv, a partir da pasta da simulacao (como o link
    # tv -> ../w/hls/sim/tv da referencia)
    tv = destino.parent / "tv"
    if tv.is_symlink() or tv.exists():
        tv.unlink()
    tv.symlink_to(sim / "tv")
    (destino / "saif.tcl").write_text(
        "open_saif atividade.saif\n"
        "log_saif [get_objects -r /apatb_cholesky_inverse_top/AESL_inst_cholesky_inverse/*]\n"
        "run all\nclose_saif\nquit\n")
    run = (destino / "run_xsim.sh").read_text()
    run = run.replace(" -s cholesky_inverse ", " -debug typical -s cholesky_inverse ")
    run = run.replace("-tclbatch cholesky_inverse.tcl", "-tclbatch saif.tcl")
    assert "-debug typical" in run and "saif.tcl" in run
    (destino / "run_saif.sh").write_text(run)
    (destino / "run_saif.sh").chmod(0o755)


def corrigir_saif(saif: Path) -> int:
    """Tira o "\\ " do fim dos nomes escapados (os que tem ponto, como loop[3].remd_tmp, dos
    divisores com pipeline). O read_saif le esse fim como um caractere nulo e nao acha a rede no
    projeto: na 4545, 62% das redes casavam; sem o "\\ ", 100%. Devolve quantos tirou."""
    t = saif.read_text()
    n = t.count("\\ ")
    if n:
        saif.write_text(t.replace("\\ ", ""))
    return n


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
    p.add_argument("versao", help="nome da pasta em versoes/ (ex.: 152_sistolico)")
    p.add_argument("--vitis", required=True, help="caminho do settings64.sh do Vitis")
    p.add_argument("--nucleos", default="", help="núcleos para o taskset (vazio: todos)")
    p.add_argument("--cenarios", default=",".join(ORDEM))
    a = p.parse_args()
    versao = PACOTE / "versoes" / a.versao
    viv = versao / "trabalho" / "vivado"
    dcp = viv / "w/hls/impl/verilog/project.runs/impl_1/bd_0_wrapper_routed.dcp"
    if not dcp.exists():
        raise SystemExit(f"sem {dcp}: rode antes ./rodar.sh {a.versao} vivado")
    sim = viv / "w" / "hls" / "sim"
    aqui = versao / "trabalho" / "potencia"
    aqui.mkdir(exist_ok=True)

    (aqui / "netlist.tcl").write_text(
        f"open_checkpoint {dcp}\n"
        f"write_verilog -mode funcsim -cell bd_0_i/hls_inst/inst -force {aqui / 'netlist_roteada.v'}\n")
    (aqui / "potencia.tcl").write_text(
        "# uso: vivado -mode batch -source potencia.tcl -tclargs <saif> <relatorio>\n"
        f"open_checkpoint {dcp}\n"
        "read_saif -strip_path apatb_cholesky_inverse_top [lindex $argv 0]\n"
        "report_power -file [lindex $argv 1]\n")
    if not (aqui / "netlist_roteada.v").exists():
        print("netlist roteada", flush=True)
        sh(f"vivado -mode batch -nojournal -nolog -source {aqui / 'netlist.tcl'}", aqui,
           aqui / "netlist.log", a.vitis, a.nucleos)

    # cfg da co-simulação: o da síntese no Vivado, sem as linhas vivado.*, mais o testbench
    base = [l for l in (viv / "hls.cfg").read_text().splitlines() if not l.startswith("vivado.")]
    cflags = next(l for l in base if l.startswith("syn.cflags=")).split("=", 1)[1]
    base += [f"tb.cflags={cflags}", f"tb.file={versao / 'tb_potencia.cpp'}",
             "cosim.tool=xsim", "cosim.setup=true"]

    csv_saida = aqui / "potencia.csv"
    tabela = [r for r in csv.DictReader(open(csv_saida))
              if r["cenario"] not in a.cenarios.split(",")] if csv_saida.exists() else []
    for cen in a.cenarios.split(","):
        # A lista do pacote tem caminhos relativos ao pacote; o testbench recebe absolutos
        lista = aqui / f"lista_{cen}.txt"
        lista.write_text("".join(f"{PACOTE / l}\n" for l in
                                 (PACOTE / "listas" / f"lista_{cen}.txt").read_text().split()))
        cfg = aqui / f"cosim_{cen}.cfg"
        cfg.write_text("\n".join(base + [f"cosim.argv={lista}"]) + "\n")
        print(f"{cen}: co-simulação (setup)", flush=True)
        log_cosim = aqui / f"cosim_{cen}.log"
        sh(f"vitis-run --mode hls --cosim --config {cfg} --work_dir w", viv, log_cosim,
           a.vitis, a.nucleos)
        m = re.search(r"POTENCIA (\d+) matrizes", log_cosim.read_text())
        n_mat = int(m.group(1)) if m else len(lista.read_text().split())
        netlist = aqui / "sim_netlist"
        preparar_netlist(sim, netlist, aqui / "netlist_roteada.v")
        tv = sim / "tv"
        for f in (tv / "rtldatafile").glob("rtl.cholesky_inverse.autotvout_inverse*.dat"):
            f.unlink()
        print(f"{cen}: simulação da netlist roteada", flush=True)
        sh("./run_saif.sh", netlist, aqui / f"xsim_{cen}.log", a.vitis, a.nucleos)
        c_arqs = sorted((tv / "cdatafile").glob("c.cholesky_inverse.autotvout_inverse*.dat"))
        assert c_arqs
        for c in c_arqs:
            r = tv / "rtldatafile" / ("rtl." + c.name[2:])
            if not r.exists() or c.read_bytes() != r.read_bytes():
                raise SystemExit(f"{cen}: as inversas da netlist diferem das do C ({c.name})")
        saif = aqui / f"atividade_{cen}.saif"
        sh(f"python3 {PACOTE / 'saif_hierarquia.py'} {netlist / 'atividade.saif'} {saif}", aqui,
           aqui / f"saif_{cen}.log", a.vitis, a.nucleos)
        (netlist / "atividade.saif").unlink()
        corrigir_saif(saif)
        duracao_ps = int(re.search(r"\(DURATION\s+(\d+)\)", saif.read_text()).group(1))
        rpt = aqui / f"potencia_{cen}.rpt"
        print(f"{cen}: report_power", flush=True)
        sh(f"vivado -mode batch -nojournal -nolog -source {aqui / 'potencia.tcl'} "
           f"-tclargs {saif} {rpt}", aqui, aqui / f"vivado_{cen}.log", a.vitis, a.nucleos)
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
