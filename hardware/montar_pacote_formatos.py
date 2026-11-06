#!/usr/bin/env python3
"""
Monta o pacote_servidor_formatos: RTL e vetores de teste gerados aqui com o HLS 2026.1, para o
servidor rodar só o Vivado e o xsim (2023.2). Mesmo fluxo do montar_pacote_2023.py, agora para
cada formato e cada arquitetura (alvo de ciclos), com a versão sem otimização de ciclos também.

Para cada versão (formato x arquitetura x tamanho):
1. síntese C (v++ -c) com o hls.cfg da arquitetura e o syn.cflags do formato, numa pasta de
   trabalho (pacote_servidor_formatos/_montagem/, fora do tar);
2. confere se cabe na XCU50 pela estimativa do HLS (DSP até 5.952; LUT até 90% de 871.680, porque
   o Vivado deu até 7,8% acima do HLS na 114). Se não cabe, fica fora do pacote (viabilidade.csv);
3. se já existe uma síntese com os mesmos fontes e o mesmo syn.cflags, confere que o RTL é igual;
4. para cada cenário da arquitetura, cosim.setup com o tb_potencia.cpp e as 20 matrizes da
   referência, e copia os vetores e o número de matrizes;
5. copia a simulação sem o RTL do HLS, que no servidor vira a netlist roteada.

Cenários da potência: as arquiteturas otimizadas só com o cenário do seu alvo; a versão sem
otimização com os 5. O TDLA30-10 usa as matrizes do TDLA30-5 (mesmo N e mesma portadora,
testes/AMOSTRAGEM.md).

<26,12> e <30,14> TRN/SAT nunca foram conferidos bit a bit nas arquiteturas otimizadas; elas só
entram com o arquivo de conferência da pasta da arquitetura (conferir_formatos_novos.sh) sem
diferenças.

<18,8> (RND_ZERO/WRAP e TRN/SAT) e <20,8> entraram depois (2026-11-03), num pacote separado
(pacote_servidor_formatos_18_20/), para não mexer no que já rodou. Com o mesmo nome de formato em
dois modos, o do TRN/SAT leva o modo no nome (18-8-TRN-SAT).

Uso (em hardware/):  python3 montar_pacote_formatos.py [--versoes 24-12_9090,...] [--nucleos 4,5]
    pacote novo:     python3 montar_pacote_formatos.py --pacote pacote_servidor_formatos_18_20 \
                         --formatos 18-8,18-8-TRN-SAT,20-8
"""

import argparse
import csv
import filecmp
import re
import queue
import shutil
import subprocess
import threading
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HW = Path(__file__).resolve().parent
SINTESES = HW / "cholesky_hardware" / "sinteses"
VITIS = "/home/juliana/2026.1/Vitis/settings64.sh"
PACOTE = HW / "pacote_servidor_formatos"
ORDEM = ["TDLA30-5", "TDLA30-10", "TDLA30-75", "TDLA30-300", "TDLC300-100", "TDLB100-400"]
# Lista de matrizes de cada cenário (o TDLA30-10 tem as mesmas matrizes do TDLA30-5)
LISTA = {c: c for c in ORDEM} | {"TDLA30-10": "TDLA30-5"}
DSP_MAX, LUT_MAX = 5952, 0.9 * 871680

# formato -> (I, F, quantização, estouro)
FORMATOS = {
    "24-12": (12, 12, "AP_RND_ZERO", "AP_WRAP"),
    "22-12": (12, 10, "AP_RND_ZERO", "AP_WRAP"),
    "28-14": (14, 14, "AP_RND_ZERO", "AP_WRAP"),
    "26-12": (12, 14, "AP_RND_ZERO", "AP_WRAP"),
    "30-14": (14, 16, "AP_TRN", "AP_SAT"),
    "18-8": (8, 10, "AP_RND_ZERO", "AP_WRAP"),
    "18-8-TRN-SAT": (8, 10, "AP_TRN", "AP_SAT"),
    "20-8": (8, 12, "AP_RND_ZERO", "AP_WRAP"),
}
# Formatos do primeiro pacote (pacote_servidor_formatos/)
PRIMEIROS = ["24-12", "22-12", "28-14", "26-12", "30-14"]
# arquitetura -> (hls.cfg de base, testbench, cenários, pasta com a síntese <24,12> já feita)
SEM = SINTESES / "24-12_16x16_RND_ZERO_WRAP_vivado"
ARQUITETURAS = {
    "sem_otimizacao": (SEM / "hls.cfg", HW / "cholesky_hardware" / "tb_potencia.cpp",
                       ["TDLA30-5", "TDLA30-75", "TDLA30-300", "TDLC300-100", "TDLB100-400"], None),
    "9090": ("cholesky_hardware_diretivas", ["TDLA30-5"], "vivado"),
    "4545": ("cholesky_hardware_diretivas_4545", ["TDLA30-10"], "vivado"),
    "606": ("cholesky_hardware_diretivas_606", ["TDLA30-75"], "vivado"),
    "152_sistolico": ("cholesky_hardware_diretivas_152_sistolico", ["TDLA30-300"], "vivado"),
    "455": ("cholesky_hardware_diretivas_455", ["TDLC300-100"], "vivado"),
    "114_sistolico": ("cholesky_hardware_diretivas_114_sistolico", ["TDLB100-400"], "cosim"),
}
for _a, _v in list(ARQUITETURAS.items()):
    if len(_v) == 3:
        _p = HW / _v[0]
        ARQUITETURAS[_a] = (_p / "vivado" / "hls.cfg", _p / "tb_potencia.cpp", _v[1], _p / _v[2])
# Já rodadas no servidor com o pacote_servidor_2023
JA_FEITAS = {"24-12_152_sistolico", "24-12_114_sistolico"}
RTL_HLS = re.compile(r"^cholesky_inverse(_.*)?\.(v|vh|dat)$")
# viabilidade.csv e fila.txt são escritos pelos dois trabalhos
TRAVA = threading.Lock()


def todas_versoes(formatos: list) -> list:
    """Na ordem dos formatos (<24,12> primeiro no primeiro pacote); 32 x 32 no fim."""
    vs = [f"{f}_{a}" for f in formatos for a in ARQUITETURAS]
    vs = [v for v in vs if v not in JA_FEITAS]
    return vs + [f"{f}_sem_otimizacao_32x32" for f in formatos]


def decompor(v: str):
    n = 32 if v.endswith("_32x32") else 16
    f, a = v.removesuffix("_32x32").split("_", 1)
    return f, a, n


def cflags(f: str, n: int) -> str:
    I, F, q, o = FORMATOS[f]
    return f"-DCHOL_N={n} -DCHOL_INT_BITS={I} -DCHOL_FRAC_BITS={F} -DCHOL_QUANT={q} -DCHOL_OVERFLOW={o}"


def sh(cmd: str, cwd: Path, log: Path, nucleo: str) -> None:
    with open(log, "w") as fh:
        r = subprocess.run(["bash", "-c", f"source {VITIS} >/dev/null 2>&1 && taskset -c {nucleo} {cmd}"],
                           cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise RuntimeError(f"falhou ({r.returncode}): {cmd} (ver {log})")


def conferida(f: str, a: str) -> bool:
    """Fora <22,12>, <24,12> e <28,14>: só com a conferência bit a bit da arquitetura sem diferenças."""
    if a == "sem_otimizacao" or f in ("24-12", "22-12", "28-14"):
        return True
    I, F, q, o = FORMATOS[f]
    arq = ARQUITETURAS[a][0].parent.parent / f"conferencia_{I}_{F}_{q}_{o}.txt"
    return arq.exists() and "; 0 diferentes ou com erro" in arq.read_text()


def estimativa(w: Path) -> dict:
    r = ET.parse(w / "hls" / "syn" / "report" / "csynth.xml").getroot().find("AreaEstimates/Resources")
    return {k: int(r.find(k).text) for k in ("DSP", "LUT", "FF", "BRAM_18K", "URAM")}


def sintese_antiga(f: str, a: str, n: int, cfl: str):
    """Pasta syn/verilog de uma síntese já feita com os mesmos fontes e o mesmo syn.cflags."""
    if a == "sem_otimizacao":
        I, F, q, o = FORMATOS[f]
        pasta = SINTESES / f"{f}_{n}x{n}_{q.removeprefix('AP_')}_{o.removeprefix('AP_')}_vivado"
    else:
        pasta = ARQUITETURAS[a][3]
    cfg = pasta / "hls.cfg" if a == "sem_otimizacao" else ARQUITETURAS[a][0]
    syn = pasta / "w" / "hls" / "syn" / "verilog"
    if not (cfg.exists() and syn.exists()):
        return None
    if next(l for l in cfg.read_text().splitlines() if l.startswith("syn.cflags=")) != f"syn.cflags={cfl}":
        return None
    return syn


def registrar(v: str, d: dict) -> None:
    with TRAVA:
        _registrar(v, d)


def _registrar(v: str, d: dict) -> None:
    arq = PACOTE / "viabilidade.csv"
    linhas = [r for r in csv.DictReader(open(arq)) if r["versao"] != v] if arq.exists() else []
    linhas.append({"versao": v, **d})
    campos = ["versao", "situacao", "DSP", "LUT", "FF", "BRAM_18K", "URAM"]
    with open(arq, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(sorted(linhas, key=lambda r: r["versao"]))


def montar(v: str, nucleo: str) -> str:
    f, a, n = decompor(v)
    if not conferida(f, a):
        registrar(v, {"situacao": "sem conferencia bit a bit"})
        return f"{v}: pulada, sem a conferência bit a bit"
    base_cfg, tb, cenarios, _ = ARQUITETURAS[a]
    cfl = cflags(f, n)
    trab = PACOTE / "_montagem" / v
    if trab.exists():
        shutil.rmtree(trab)
    trab.mkdir(parents=True)
    destino = PACOTE / "versoes" / v
    if destino.exists():
        shutil.rmtree(destino)

    # CHOL_DIV0_COMO_RTL: na divisão por zero o C dá o mesmo valor do divisor do RTL em vez de
    # morrer (cholesky_ops.h, só fora da síntese; o RTL não muda). Só pesa com I = 8.
    cfl_c = f"{cfl} -DCHOL_DIV0_COMO_RTL"
    base = [f"syn.cflags={cfl_c}" if l.startswith("syn.cflags=") else l
            for l in base_cfg.read_text().splitlines() if not l.startswith(("vivado.", "package."))]
    base += [f"tb.cflags={cfl_c}", f"tb.file={tb}", "cosim.tool=xsim", "cosim.setup=true"]
    (trab / "sintese.cfg").write_text("\n".join(base) + "\n")
    print(f"{v}: síntese C", flush=True)
    sh("v++ -c --mode hls --config sintese.cfg --work_dir w", trab, trab / "sintese.log", nucleo)

    est = estimativa(trab / "w")
    if est["DSP"] > DSP_MAX or est["LUT"] > LUT_MAX:
        registrar(v, {"situacao": "nao cabe", **est})
        return f"{v}: não cabe na XCU50 pela estimativa do HLS ({est})"

    syn = trab / "w" / "hls" / "syn" / "verilog"
    antigo = sintese_antiga(f, a, n, cfl)
    if antigo:
        c = filecmp.dircmp(syn, antigo)
        assert not (c.left_only or c.right_only or c.diff_files), (v, c.left_only, c.right_only, c.diff_files)
    shutil.copytree(syn, destino / "rtl")
    # O xdc do HLS só tem o relógio de 10 ns, igual em todas as versões
    shutil.copy(HW / "cholesky_hardware_diretivas_455/vivado/w/hls/impl/verilog/cholesky_inverse.xdc",
                destino / "rtl")

    ref = SINTESES / f"24-12_{n}x{n}_RND_ZERO_WRAP_vivado" / "potencia"
    sim = trab / "w" / "hls" / "sim"
    for cen in cenarios:
        cfg = trab / f"cosim_{cen}.cfg"
        cfg.write_text("\n".join(base + [f"cosim.argv={ref / f'lista_{LISTA[cen]}.txt'}"]) + "\n")
        log = trab / f"cosim_{cen}.log"
        sh(f"vitis-run --mode hls --cosim --config {cfg} --work_dir w", trab, log, nucleo)
        m = int(re.search(r"POTENCIA (\d+) matrizes", log.read_text()).group(1))
        dcen = destino / "cenarios" / cen
        shutil.copytree(sim / "tv" / "cdatafile", dcen / "tv" / "cdatafile")
        (dcen / "matrizes.txt").write_text(f"{m}\n")
        tpl = destino / "sim"
        if not tpl.exists():
            shutil.copytree(sim / "verilog", tpl, ignore=lambda d, fs: [
                x for x in fs if x in ("xsim.dir", "xsim.jou", "xsim.log", "xelab.log", "xelab.pb")
                or x.endswith((".wdb", ".saif")) or (Path(d) == sim / "verilog" and RTL_HLS.match(x))])
        else:
            # O testbench tem que ser o mesmo em todos os cenários (só os vetores mudam)
            for x in ("cholesky_inverse.autotb.v", "cholesky_inverse.prj"):
                assert filecmp.cmp(sim / "verilog" / x, tpl / x, shallow=False), (v, cen, x)
    registrar(v, {"situacao": "no pacote", **est})
    with TRAVA, open(PACOTE / "fila.txt", "a") as fh:
        fh.write(v + "\n")
    # A síntese ocupa espaço e não vai no tar; fica só o log
    shutil.rmtree(trab / "w")
    return f"{v}: pronto ({'RTL igual ao já sintetizado' if antigo else 'sem síntese anterior para comparar'})"


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--pacote", default="pacote_servidor_formatos", help="pasta do pacote, em hardware/")
    p.add_argument("--formatos", default=",".join(PRIMEIROS))
    p.add_argument("--versoes", help="padrão: todas as versões dos formatos")
    p.add_argument("--nucleos", default="4,5", help="um trabalho por núcleo")
    a = p.parse_args()
    global PACOTE
    PACOTE = HW / a.pacote
    (PACOTE / "versoes").mkdir(parents=True, exist_ok=True)
    if not a.versoes:
        a.versoes = ",".join(todas_versoes(a.formatos.split(",")))
    nucleos = a.nucleos.split(",")
    versoes = a.versoes.split(",")
    feitas = set((PACOTE / "fila.txt").read_text().split()) if (PACOTE / "fila.txt").exists() else set()
    versoes = [v for v in versoes if v not in feitas]

    livres = queue.Queue()
    for nc in nucleos:
        livres.put(nc)

    def tarefa(v):
        nc = livres.get()
        try:
            return montar(v, nc)
        except Exception as e:  # uma versão que falha não para as outras
            return f"{v}: FALHOU: {e}"
        finally:
            livres.put(nc)

    # Um trabalho por núcleo; cada um pega o núcleo que ficou livre
    with ThreadPoolExecutor(len(nucleos)) as ex:
        for msg in ex.map(tarefa, versoes):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
