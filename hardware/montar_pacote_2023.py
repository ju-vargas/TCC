#!/usr/bin/env python3
"""
Monta o pacote_servidor_2023: o RTL e os vetores de teste gerados aqui com o HLS 2026.1, para
o servidor rodar só o Vivado e o xsim (2023.2).

Para cada versão (455 como calibração, 152_sistolico e 114_sistolico):
1. síntese C (v++ -c) com o hls.cfg da pasta vivado/ da versão, numa pasta de trabalho nova
   (pacote_servidor_2023/_montagem/, fora do tar), sem mexer nas pastas das versões;
2. copia o RTL (syn/verilog) e confere que é igual ao da síntese já feita na versão;
3. para cada cenário, cosim.setup com o tb_potencia.cpp e as 20 matrizes da referência, e
   copia os vetores (sim/tv/cdatafile) e o número de matrizes da linha "POTENCIA N matrizes";
4. copia a pasta da simulação (sim/verilog) sem o RTL do HLS, que no servidor vira a netlist.

Uso (em hardware/):  python3 montar_pacote_2023.py [--versoes 455,...] [--nucleos 4-5]
"""

import argparse
import filecmp
import re
import shutil
import subprocess
from pathlib import Path

HW = Path(__file__).resolve().parent
REF = HW / "cholesky_hardware" / "sinteses" / "24-12_16x16_RND_ZERO_WRAP_vivado" / "potencia"
VITIS = "/home/juliana/2026.1/Vitis/settings64.sh"
PACOTE = HW / "pacote_servidor_2023"
ORDEM = ["TDLA30-5", "TDLA30-75", "TDLA30-300", "TDLC300-100", "TDLB100-400"]
# Pasta da versão e onde está o RTL da síntese já feita (a 114 não chegou ao Vivado)
VERSOES = {
    "455": ("cholesky_hardware_diretivas_455", "vivado"),
    "152_sistolico": ("cholesky_hardware_diretivas_152_sistolico", "vivado"),
    "114_sistolico": ("cholesky_hardware_diretivas_114_sistolico", "cosim"),
}
RTL_HLS = re.compile(r"^cholesky_inverse(_.*)?\.(v|vh|dat)$")


def sh(cmd: str, cwd: Path, log: Path, nucleos: str) -> None:
    with open(log, "w") as fh:
        r = subprocess.run(["bash", "-c", f"source {VITIS} >/dev/null 2>&1 && taskset -c {nucleos} {cmd}"],
                           cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise SystemExit(f"falhou ({r.returncode}): {cmd} (ver {log})")


def montar(v: str, nucleos: str) -> None:
    pasta, origem = VERSOES[v]
    pasta = HW / pasta
    trab = PACOTE / "_montagem" / v
    if trab.exists():
        shutil.rmtree(trab)
    trab.mkdir(parents=True)
    destino = PACOTE / "versoes" / v
    if destino.exists():
        shutil.rmtree(destino)

    base = [l for l in (pasta / "vivado" / "hls.cfg").read_text().splitlines()
            if not l.startswith(("vivado.", "package."))]
    cflags = next(l for l in base if l.startswith("syn.cflags=")).split("=", 1)[1]
    base += [f"tb.cflags={cflags}", f"tb.file={pasta / 'tb_potencia.cpp'}",
             "cosim.tool=xsim", "cosim.setup=true"]
    (trab / "sintese.cfg").write_text("\n".join(base) + "\n")
    print(f"{v}: síntese C", flush=True)
    sh("v++ -c --mode hls --config sintese.cfg --work_dir w", trab, trab / "sintese.log", nucleos)

    syn = trab / "w" / "hls" / "syn" / "verilog"
    antigo = pasta / origem / "w" / "hls" / "syn" / "verilog"
    cmp = filecmp.dircmp(syn, antigo)
    assert not (cmp.left_only or cmp.right_only or cmp.diff_files), (v, cmp.left_only, cmp.right_only, cmp.diff_files)
    shutil.copytree(syn, destino / "rtl")
    # O xdc do HLS só tem o relógio de 10 ns, igual em todas as versões (a 114 não tem o seu)
    shutil.copy(HW / VERSOES["455"][0] / "vivado/w/hls/impl/verilog/cholesky_inverse.xdc", destino / "rtl")
    print(f"{v}: RTL igual ao da síntese já feita ({len(list(syn.iterdir()))} arquivos)", flush=True)

    sim = trab / "w" / "hls" / "sim"
    for cen in ORDEM:
        cfg = trab / f"cosim_{cen}.cfg"
        cfg.write_text("\n".join(base + [f"cosim.argv={REF / f'lista_{cen}.txt'}"]) + "\n")
        print(f"{v} {cen}: cosim.setup", flush=True)
        log = trab / f"cosim_{cen}.log"
        sh(f"vitis-run --mode hls --cosim --config {cfg} --work_dir w", trab, log, nucleos)
        n = int(re.search(r"POTENCIA (\d+) matrizes", log.read_text()).group(1))
        dcen = destino / "cenarios" / cen
        shutil.copytree(sim / "tv" / "cdatafile", dcen / "tv" / "cdatafile")
        (dcen / "matrizes.txt").write_text(f"{n}\n")
        tpl = destino / "sim"
        if not tpl.exists():
            shutil.copytree(sim / "verilog", tpl, ignore=lambda d, fs: [
                f for f in fs if f in ("xsim.dir", "xsim.jou", "xsim.log", "xelab.log", "xelab.pb")
                or f.endswith((".wdb", ".saif")) or (Path(d) == sim / "verilog" and RTL_HLS.match(f))])
        else:
            # O testbench tem que ser o mesmo em todos os cenários (só os vetores mudam)
            for f in ("cholesky_inverse.autotb.v", "cholesky_inverse.prj"):
                assert filecmp.cmp(sim / "verilog" / f, tpl / f, shallow=False), (v, cen, f)
    print(f"{v}: pronto", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--versoes", default=",".join(VERSOES))
    p.add_argument("--nucleos", default="4-5")
    a = p.parse_args()
    for v in a.versoes.split(","):
        montar(v, a.nucleos)


if __name__ == "__main__":
    main()
