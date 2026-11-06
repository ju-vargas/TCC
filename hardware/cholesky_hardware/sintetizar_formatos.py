#!/usr/bin/env python3
"""
Síntese HLS (só C synthesis) do topo cholesky_inverse para vários formatos ap_fixed<W,I>,
sem nenhuma diretiva (syn.compile.pipeline_loops=0), AP_TRN/AP_SAT, a 100 MHz, na
XCU50-FSVH2104-2-E. Serve para o eixo de custo da fronteira de Pareto (perda x DSP/LUT).

Cada formato é sintetizado numa pasta temporária. Só os relatórios (csynth.rpt e
csynth.xml) ficam em sinteses/formatos_16x16/<I>_<F>/, e a tabela de todos em
sinteses/formatos_16x16/recursos.csv. Formatos que já têm relatório são pulados.

Com --modos todos, cada formato é sintetizado nos 35 pares de quantização e estouro, e
os relatórios vão para sinteses/modos_<n>x<n>/<I>_<F>_<quant>_<estouro>/ (modos_16x16 ou
modos_32x32, pelo --n), com a tabela em sinteses/modos_<n>x<n>/recursos.csv. As sínteses de
formatos_16x16 (só AP_TRN/AP_SAT) não mudam. Um formato escrito como I:F:QUANT:ESTOURO é
sintetizado só nesse modo, também em modos_<n>x<n>.

Uso (nesta pasta):
    python3 sintetizar_formatos.py 14:4 14:6 12:12 ...   (I:F, I com o sinal)
        [--n 16] [--vitis /home/juliana/2026.1/Vitis] [--modos todos] [--paralelo 4]
"""

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DESTINO = AQUI / "sinteses" / "formatos_16x16"


def destino_modos(n: int) -> Path:
    return AQUI / "sinteses" / f"modos_{n}x{n}"
QUANTS = ("AP_TRN", "AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF",
          "AP_RND_CONV")
OVERFLOWS = ("AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM")
FONTES = ["cholesky.h", "cholesky_ops.h", "cholesky_decomposition.cpp", "lu_decomposition.cpp",
          "dv_step.cpp", "s_step.cpp", "g_step.cpp", "foward_substitution.cpp", "inversion.cpp",
          "cholesky_top.cpp"]
CAMPOS = ["int_bits", "frac_bits", "W", "n", "ciclos", "periodo_estimado_ns", "fmax_mhz",
          "BRAM_18K", "DSP", "FF", "LUT", "URAM"]


def config(i, f, n, q="AP_TRN", o="AP_SAT"):
    flags = (f"-DCHOL_N={n} -DCHOL_INT_BITS={i} -DCHOL_FRAC_BITS={f} "
             f"-DCHOL_QUANT={q} -DCHOL_OVERFLOW={o}")
    linhas = ["part=xcu50-fsvh2104-2-e", "", "[hls]", "clock=10ns",
              "syn.compile.pipeline_loops=0", "syn.top=cholesky_inverse",
              "package.output.format=ip_catalog", "package.output.syn=false",
              f"syn.cflags={flags}"]
    linhas += [f"syn.file={AQUI / a}" for a in FONTES]
    return "\n".join(linhas) + "\n"


def ler_xml(xml: Path) -> dict:
    raiz = ET.parse(xml).getroot()
    perf = raiz.find("PerformanceEstimates")
    rec = raiz.find("AreaEstimates/Resources")
    periodo = float(perf.find("SummaryOfTimingAnalysis/EstimatedClockPeriod").text)
    d = {"ciclos": int(perf.find("SummaryOfOverallLatency/Interval-max").text),
         "periodo_estimado_ns": periodo, "fmax_mhz": round(1000 / periodo, 1)}
    d.update({k: int(rec.find(k).text) for k in ("BRAM_18K", "DSP", "FF", "LUT", "URAM")})
    return d


def sintetizar(i, f, n, vitis: Path, modo=None) -> Path | None:
    """modo: None (AP_TRN/AP_SAT, em formatos_16x16) ou (quant, estouro), em modos_16x16."""
    if modo:
        pasta = destino_modos(n) / f"{i}_{f}_{modo[0]}_{modo[1]}"
    else:
        pasta = DESTINO / f"{i}_{f}" if n == 16 else DESTINO / f"{i}_{f}_n{n}"
    if (pasta / "csynth.xml").exists():
        return pasta
    with tempfile.TemporaryDirectory(prefix=f"sint_{i}_{f}_") as tmp:
        cfg = Path(tmp) / "hls.cfg"
        cfg.write_text(config(i, f, n, *(modo or ())))
        cmd = (f"source {vitis}/settings64.sh >/dev/null 2>&1 && "
               f"v++ -c --mode hls --config {cfg} --work_dir {tmp}/w")
        r = subprocess.run(["bash", "-c", cmd], cwd=tmp, capture_output=True, text=True)
        rel = Path(tmp) / "w" / "hls" / "syn" / "report"
        if r.returncode != 0 or not (rel / "csynth.xml").exists():
            pasta.mkdir(parents=True, exist_ok=True)
            (pasta / "erro.log").write_text(r.stdout + r.stderr)
            print(f"<{i + f},{i}>: FALHOU (ver {pasta / 'erro.log'})", flush=True)
            return None
        pasta.mkdir(parents=True, exist_ok=True)
        for nome in ("csynth.rpt", "csynth.xml"):
            shutil.copy(rel / nome, pasta / nome)
        (pasta / "hls.cfg").write_text(config(i, f, n, *(modo or ())))
    return pasta


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("formatos", nargs="+", help="I:F ou I:F:QUANT:ESTOURO")
    p.add_argument("--n", type=int, default=16)
    p.add_argument("--vitis", default="/home/juliana/2026.1/Vitis")
    p.add_argument("--modos", choices=["trn_sat", "todos"], default="trn_sat")
    p.add_argument("--paralelo", type=int, default=1, help="sínteses ao mesmo tempo")
    a = p.parse_args()
    modos = [(q, o) for q in QUANTS for o in OVERFLOWS] if a.modos == "todos" else [None]
    celulas = any(fmt.count(":") == 3 for fmt in a.formatos)
    tarefas = []
    for fmt in a.formatos:
        i, f, *m = fmt.split(":")
        tarefas += [(int(i), int(f), tuple(m) if m else x) for x in ([None] if m else modos)]

    def uma(t):
        i, f, m = t
        pasta = sintetizar(i, f, a.n, Path(a.vitis), m)
        if pasta:
            d = ler_xml(pasta / "csynth.xml")
            nome = f"<{i + f},{i}>" + (f" {m[0]}/{m[1]}" if m else "")
            print(f"{nome}: {d['ciclos']} ciclos, {d['DSP']} DSP, {d['LUT']} LUT, "
                  f"{d['fmax_mhz']} MHz", flush=True)

    with ThreadPoolExecutor(a.paralelo) as ex:
        list(ex.map(uma, tarefas))
    if a.modos == "todos" or celulas:
        tabela_modos(a.n)
        return
    DESTINO.mkdir(parents=True, exist_ok=True)
    linhas = []
    for x in sorted(DESTINO.glob("*/csynth.xml")):
        partes = x.parent.name.split("_")
        n = int(partes[2][1:]) if len(partes) > 2 else 16
        i, f = int(partes[0]), int(partes[1])
        linhas.append({"int_bits": i, "frac_bits": f, "W": i + f, "n": n, **ler_xml(x)})
    linhas.sort(key=lambda d: (d["n"], d["W"], d["int_bits"]))
    with open(DESTINO / "recursos.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(linhas)
    print(f"{DESTINO / 'recursos.csv'}: {len(linhas)} formatos")


def tabela_modos(n: int):
    destino = destino_modos(n)
    linhas = []
    for x in sorted(destino.glob("*/csynth.xml")):
        i, f, resto = x.parent.name.split("_", 2)
        q = next(q for q in sorted(QUANTS, key=len, reverse=True) if resto.startswith(q + "_"))
        linhas.append({"int_bits": int(i), "frac_bits": int(f), "W": int(i) + int(f), "n": n,
                       "quant": q, "overflow": resto[len(q) + 1:], **ler_xml(x)})
    ordem = {m: k for k, m in enumerate((q, o) for q in QUANTS for o in OVERFLOWS)}
    linhas.sort(key=lambda d: (d["W"], d["int_bits"], ordem[(d["quant"], d["overflow"])]))
    with open(destino / "recursos.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS[:4] + ["quant", "overflow"] + CAMPOS[4:])
        w.writeheader()
        w.writerows(linhas)
    print(f"{destino / 'recursos.csv'}: {len(linhas)} sínteses")


if __name__ == "__main__":
    main()
