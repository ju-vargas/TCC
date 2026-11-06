#!/usr/bin/env python3
"""
Potência do <28,14> AP_RND_ZERO/AP_WRAP 32 x 32 com matrizes G_c reais, um cenário por vez.

Para cada cenário:
1. escolhe 20 matrizes de hardware/testes/2_amostra_matrizes (configurações 9 a 12,
   espalhadas pelas configurações e sorteadas com semente fixa), em lista_<cenário>.txt;
2. prepara a co-simulação do HLS com o tb_potencia.cpp (cosim.setup), que inverte as
   20 matrizes uma atrás da outra;
3. troca o RTL do HLS pela netlist roteada do Vivado (netlist_roteada.v, de
   write_verilog -mode funcsim da célula bd_0_i/hls_inst/inst) e simula no xsim,
   gravando a atividade de todos os sinais do inversor num SAIF;
4. confere que as inversas da netlist são iguais, byte a byte, às do C;
5. lê o SAIF no projeto roteado e roda o report_power (potencia_<cenário>.rpt).

A tabela de todos os cenários vai para potencia.csv. Uso (nesta pasta):
    python3 rodar_potencia.py [--k 20] [--cenarios TDLA30-5,...]
"""

import argparse
import csv
import random
import re
import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SINTESE = AQUI.parent
SIM = SINTESE / "w" / "hls" / "sim"
AMOSTRA = SINTESE.parents[2] / "testes" / "2_amostra_matrizes"
VITIS = "/home/juliana/2026.1/Vitis/settings64.sh"
CENARIOS = {"TDLA30-5": "amostras192_fc3.5GHz", "TDLA30-75": "amostras192_fc28GHz",
            "TDLA30-300": "amostras168_fc28GHz", "TDLC300-100": "amostras132_fc3.5GHz",
            "TDLB100-400": "amostras24_fc3.5GHz"}
CONFIGS = range(9, 13)
SEMENTE = 2026
PERIODO_NS = 10.0


def sh(cmd: str, cwd: Path, log: Path) -> None:
    with open(log, "w") as fh:
        r = subprocess.run(["bash", "-c", f"source {VITIS} >/dev/null 2>&1 && {cmd}"],
                           cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise SystemExit(f"falhou ({r.returncode}): {cmd} (ver {log})")


def escolher(cenario: str, k: int) -> list[Path]:
    pasta = AMOSTRA / CENARIOS[cenario] / "32x32"
    linhas = list(csv.DictReader(open(pasta / "indice.csv")))
    assert all(cenario in r["condicoes"] for r in linhas), cenario
    sorteio = random.Random(f"{SEMENTE}-{cenario}")
    por_config = {c: [r for r in linhas if int(r["configuracao"]) == c] for c in CONFIGS}
    for v in por_config.values():
        sorteio.shuffle(v)
    escolhidas = []
    while len(escolhidas) < k:   # uma de cada configuração por vez
        for c in CONFIGS:
            if por_config[c] and len(escolhidas) < k:
                escolhidas.append(por_config[c].pop())
    return [pasta / f"{r['arquivo']}.bits" for r in escolhidas]


def preparar_netlist(destino: Path) -> None:
    """Copia a simulação que o cosim.setup gerou e põe a netlist roteada no lugar do RTL."""
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(SIM / "verilog", destino, ignore=shutil.ignore_patterns("xsim.dir", "*.saif"))
    shutil.copy(AQUI / "netlist_roteada.v", destino / "netlist_roteada.v")
    prj = [l for l in (destino / "cholesky_inverse.prj").read_text().splitlines()
           if not re.search(r'"cholesky_inverse(_[^"]*)?\.v"', l)]
    (destino / "cholesky_inverse.prj").write_text(
        "\n".join(prj + ['verilog xil_defaultlib "netlist_roteada.v"']) + "\n")
    # O monitor do HLS olha sinais internos do RTL, que a netlist não tem
    (destino / "dataflow_monitor.sv").write_text(
        "`timescale 1ns/1ps\nmodule dataflow_monitor(input logic clock, input logic reset, "
        "input logic finish);\nendmodule\n")
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
    p.add_argument("--k", type=int, default=20, help="matrizes por cenário")
    p.add_argument("--cenarios", default=",".join(CENARIOS))
    a = p.parse_args()
    cfg_base = [l for l in (AQUI / "cosim_piloto.cfg").read_text().splitlines()
                if not l.startswith("cosim.argv=")]
    # Os cenários de rodadas anteriores que não são rodados de novo ficam na tabela
    csv_saida = AQUI / "potencia.csv"
    tabela = [r for r in csv.DictReader(open(csv_saida))
              if r["cenario"] not in a.cenarios.split(",")] if csv_saida.exists() else []
    for cen in a.cenarios.split(","):
        lista = AQUI / f"lista_{cen}.txt"
        lista.write_text("".join(f"{m}\n" for m in escolher(cen, a.k)))
        cfg = AQUI / f"cosim_{cen}.cfg"
        cfg.write_text("\n".join(cfg_base + [f"cosim.argv={lista}"]) + "\n")
        print(f"{cen}: co-simulação (setup)", flush=True)
        sh(f"vitis-run --mode hls --cosim --config {cfg} --work_dir w", SINTESE,
           AQUI / f"cosim_{cen}.log")
        netlist = AQUI / "sim_netlist"
        preparar_netlist(netlist)
        tv = SIM / "tv"
        (tv / "rtldatafile" / "rtl.cholesky_inverse.autotvout_inverse.dat").unlink(missing_ok=True)
        print(f"{cen}: simulação da netlist roteada", flush=True)
        sh("./run_saif.sh", netlist, AQUI / f"xsim_{cen}.log")
        c_out = (tv / "cdatafile" / "c.cholesky_inverse.autotvout_inverse.dat").read_bytes()
        rtl_out = (tv / "rtldatafile" / "rtl.cholesky_inverse.autotvout_inverse.dat").read_bytes()
        if c_out != rtl_out:
            raise SystemExit(f"{cen}: as inversas da netlist diferem das do C")
        saif = AQUI / f"atividade_{cen}.saif"
        sh(f"python3 {AQUI / 'saif_hierarquia.py'} {netlist / 'atividade.saif'} {saif}", AQUI,
           AQUI / f"saif_{cen}.log")
        duracao_ps = int(re.search(r"\(DURATION\s+(\d+)\)", saif.read_text()).group(1))
        rpt = AQUI / f"potencia_{cen}.rpt"
        print(f"{cen}: report_power", flush=True)
        sh(f"vivado -mode batch -nojournal -nolog -source {AQUI / 'potencia.tcl'} "
           f"-tclargs {saif} {rpt}", AQUI, AQUI / f"vivado_{cen}.log")
        d = {"cenario": cen, "matrizes": a.k, **ler_relatorio(rpt),
             "ciclos_medios": round(duracao_ps / 1000 / PERIODO_NS / a.k)}
        d["energia_por_inversao_uj"] = round(d["dinamica_w"] * d["ciclos_medios"] * PERIODO_NS * 1e-3, 2)
        tabela.append(d)
        tabela.sort(key=lambda r: list(CENARIOS).index(r["cenario"]))
        print(f"{cen}: {d}", flush=True)
        with open(csv_saida, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(d))
            w.writeheader()
            w.writerows(tabela)


if __name__ == "__main__":
    main()
