#!/usr/bin/env python3
"""
Inverte as matrizes da seleção pelo caminho do simulador e compara, bit a bit, com a
C-simulation do Vitis.

Para cada matriz de 3_selecao_matrizes/<par>/<n>x<n>/:
  1. monta o inversor como o simulador monta (dbp_sim.hw_inverse.make_inverter,
     "cholesky_hw"), com o formato de parametros.env, e inverte a matriz em float64;
  2. reconstrói os bits da inversa a partir do resultado do simulador: cada valor é
     um múltiplo exato de 2^-F, então round(x * 2^F) em complemento de dois, com a
     largura do tipo, devolve o registrador do hardware. Grava sim_08_inverse.bits
     no mesmo formato dos .bits do testbench;
  3. compara com o golden_08_inverse.bits do golden_cholesky.py (confere a
     reconstrução) e com o hw_08_inverse.bits da C-simulation.

Lê a C-simulation de <validacao>/<par>/hls/ (saída de rodar_inversoes.sh com
--manter) e grava <validacao>/<par>/simulador/<n>x<n>/<matriz>/sim_08_inverse.bits,
<validacao>/relatorio.csv (uma linha por matriz) e <validacao>/resumo.txt.

O simulador usa o mesmo módulo golden_cholesky.py que a C-simulation tem como
referência. O que esta comparação acrescenta: (a) o hardware contra o modelo Python
nas 8 etapas (status do rodar_inversoes.sh) e (b) que o simulador monta o mesmo
formato do hardware e que a conversão para float e de volta preserva os bits.

Uso (com o Python do simulador):
    ../../software/simulador/.venv/bin/python inverter_no_simulador.py 3_validacao_bits/validacao_<data>
"""

import argparse
import contextlib
import csv
import io
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
SIMULADOR = AQUI.parents[1] / "software" / "simulador"
sys.path.insert(0, str(SIMULADOR))

from dbp_sim import hw_inverse  # noqa: E402

INTERMEDIARIOS = hw_inverse.INTERMEDIATES     # mulin, prod, cmul, num, norm, quot, sum, sqrt


def ler_env(caminho: Path) -> dict:
    valores = {}
    for linha in caminho.read_text().splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            nome, valor = linha.split("=", 1)
            valores[nome.strip()] = valor.strip()
    return valores


def montar_inversor(env: dict):
    """O inversor do simulador com o formato do parametros.env (campo vazio = padrão)."""
    def num(chave):
        v = env.get(chave, "")
        return int(v) if v else None

    def txt(chave):
        return env.get(chave, "") or None

    inter = []
    for nome in INTERMEDIARIOS:
        pre = f"CHOL_{nome.upper()}_"
        campos = ((num(pre + "INT_BITS"), num(pre + "FRAC_BITS"))
                  if nome in hw_inverse.BITS_ONLY else
                  (num(pre + "INT_BITS"), num(pre + "FRAC_BITS"), txt(pre + "QUANT"),
                   txt(pre + "OVERFLOW")))
        if any(c is not None for c in campos):
            inter.append((nome, campos + (None,) * (4 - len(campos))))
    return hw_inverse.make_inverter(
        "cholesky_hw", int(env["CHOL_INT_BITS"]), int(env["CHOL_FRAC_BITS"]),
        num("CHOL_ACC_INT_BITS"), num("CHOL_ACC_FRAC_BITS"),
        env["CHOL_QUANT"], env["CHOL_OVERFLOW"], txt("CHOL_ACC_QUANT"),
        txt("CHOL_ACC_OVERFLOW"), tuple(inter))


def tipos(fmt) -> str:
    """As linhas "TIPO ..." do formato, no texto do testbench e do golden_cholesky.py."""
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        hw_inverse._load().print_types(fmt)
    return saida.getvalue()


def bits_da_inversa(inv: np.ndarray, fix) -> list[list[str]]:
    """Registradores do hardware a partir da inversa do simulador (múltiplos de 2^-F)."""
    escala = 1 << fix.frac
    mascara = (1 << fix.width) - 1
    linhas = []
    for linha in inv:
        elems = []
        for z in linha:
            partes = []
            for x in (z.real, z.imag):
                v = int(round(x * escala))
                if v / escala != x:
                    raise ValueError(f"{x!r} não é múltiplo de 2^-{fix.frac}")
                partes.append(format(v & mascara, f"0{fix.width}b"))
            elems.append(":".join(partes))
        linhas.append(elems)
    return linhas


_INV = None


def _iniciar(env: dict):
    global _INV
    _INV = montar_inversor(env)


def _inverter(tarefa):
    """(entrada.bits, saida.bits) -> "ok" ou "div0"."""
    entrada, saida = tarefa
    n, A = hw_inverse._load().read_float_bits(str(entrada))
    inv = _INV(np.array(A, dtype=complex))
    saida.parent.mkdir(parents=True, exist_ok=True)
    if np.isnan(inv).any():
        saida.with_name("sim_div0").write_text("divisão por zero no simulador\n")
        return "div0"
    fix = _INV.fmt.fix
    if fix.width <= BITS_FLOAT64:
        with open(saida, "w") as fh:
            fh.write(f"{n}\n")
            for linha in bits_da_inversa(inv, fix):
                fh.write(" ".join(linha) + "\n")
        return "ok"
    # Acima de 53 bits, a inversa em float64 do simulador não guarda todos os bits do
    # registrador. Os bits vêm, então, do mesmo modelo e do formato que o simulador
    # montou, e o float do simulador tem que ser exatamente a conversão desses bits.
    modelo = hw_inverse._load()
    regs = modelo.cholesky_decomposition(modelo.quantize_matrix(A, fix), _INV.fmt)["inverse"]
    if not np.array_equal(np.array(modelo.to_complex_matrix(regs, fix), dtype=complex), inv):
        raise ValueError(f"{entrada.name}: a inversa do simulador não é a dos registradores")
    modelo.write_bits(str(saida), n, regs, fix)
    return "ok"


#: Bits da mantissa do float64: até essa largura, a inversa do simulador guarda o
#: registrador inteiro, e os bits podem ser reconstruídos a partir dela.
BITS_FLOAT64 = 53


def ler_registradores(caminho: Path, fix) -> np.ndarray:
    """Valores de um .bits de saída (complemento de dois com a largura do tipo)."""
    linhas = [l.split() for l in caminho.read_text().splitlines()[1:] if l.strip()]
    meio, cheio, escala = 1 << (fix.width - 1), 1 << fix.width, 2.0 ** -fix.frac

    def valor(b):
        v = int(b, 2)
        return (v - cheio if v >= meio else v) * escala
    return np.array([[complex(*(valor(p) for p in e.split(":"))) for e in l] for l in linhas])


def contra_float(hw_bits: Path, entrada: Path, fix):
    """Hardware contra a inversão em float64 das curvas (np.linalg.inv, a mesma conta
    de np.linalg.solve do BCD-MMSE). Devolve (erro máximo em LSB, erro relativo de
    Frobenius, fração de partes iguais à inversa em float64 arredondada para o tipo),
    ou None se o hardware não tem saída (divisão por zero)."""
    if not hw_bits.exists():
        return None
    _, A = hw_inverse._load().read_float_bits(str(entrada))
    X_f = np.linalg.inv(np.array(A, dtype=complex))
    X_hw = ler_registradores(hw_bits, fix)
    lsb = 2.0 ** -fix.frac
    dif = X_hw - X_f
    erro_lsb = float(np.max(np.maximum(np.abs(dif.real), np.abs(dif.imag)))) / lsb
    erro_rel = float(np.linalg.norm(dif) / np.linalg.norm(X_f))
    arred = np.concatenate([np.round(X_f.real / lsb).ravel(), np.round(X_f.imag / lsb).ravel()])
    regs = np.concatenate([np.round(X_hw.real / lsb).ravel(), np.round(X_hw.imag / lsb).ravel()])
    return erro_lsb, erro_rel, float(np.mean(arred == regs))


def iguais(a: Path, b: Path):
    """True/False se os dois .bits existem; None se algum falta."""
    if not (a.exists() and b.exists()):
        return None
    return a.read_text().split() == b.read_text().split()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("validacao", help="Pasta da validação (3_validacao_bits/validacao_<data>)")
    parser.add_argument("--selecao", default=str(AQUI / "3_selecao_matrizes"),
                        help="Pasta da seleção (padrão: 3_selecao_matrizes/)")
    parser.add_argument("--env", default=str(AQUI / "parametros.env"),
                        help="Formato do hardware (padrão: parametros.env)")
    parser.add_argument("-j", "--jobs", type=int, default=None,
                        help="Processos em paralelo (padrão: núcleos)")
    args = parser.parse_args()

    env = ler_env(Path(args.env))
    fmt = montar_inversor(env).fmt
    texto_tipos = tipos(fmt)
    validacao = Path(args.validacao)
    q, o = env["CHOL_QUANT"], env["CHOL_OVERFLOW"]

    linhas, tarefas = [], []
    for indice in sorted(Path(args.selecao).glob("*/*x*/indice.csv")):
        par, tam = indice.parent.parent.name, indice.parent.name
        hls = validacao / par / "hls" / f"q_{q}__o_{o}" / tam
        if not hls.exists():
            raise SystemExit(f"falta a C-simulation de {par}/{tam} em {hls}")
        tipos_py = (hls / "tipos_py.txt").read_text()
        if sorted(tipos_py.strip().splitlines()) != sorted(texto_tipos.strip().splitlines()):
            raise SystemExit(f"{par}/{tam}: o formato do simulador não é o do hardware\n"
                             f"simulador:\n{texto_tipos}\ngolden_cholesky.py:\n{tipos_py}")
        with open(indice, newline="") as fh:
            for l in csv.DictReader(fh):
                nome = l["arquivo"]
                saida = validacao / par / "simulador" / tam / nome / "sim_08_inverse.bits"
                tarefas.append((indice.parent / f"{nome}.bits", saida))
                linhas.append({"par": par, "tamanho": tam, "hls_dir": hls / "matrizes" / nome,
                               "saida": saida, **l})

    print(f"{len(tarefas)} matrizes; formato:\n{texto_tipos}", flush=True)
    with ProcessPoolExecutor(args.jobs, initializer=_iniciar, initargs=(env,)) as ex:
        resultados = list(ex.map(_inverter, tarefas, chunksize=4))

    relatorio = []
    for l, sim in zip(linhas, resultados):
        d = l["hls_dir"]
        linha_hls = (d / "linha.csv").read_text().strip().split(",") \
            if (d / "linha.csv").exists() else []
        status_hls = linha_hls[5] if len(linha_hls) > 5 else "sem_resultado"
        sim_vs_golden = iguais(l["saida"], d / "py" / "golden_08_inverse.bits")
        sim_vs_hw = iguais(l["saida"], d / "hw" / "hw_08_inverse.bits")
        cf = contra_float(d / "hw" / "hw_08_inverse.bits",
                          Path(args.selecao) / l["par"] / l["tamanho"] / f"{l['arquivo']}.bits",
                          fmt.fix)
        if status_hls == "igual" and sim == "ok" and sim_vs_hw and sim_vs_golden:
            final = "igual"
        elif status_hls == "ambos_div0" and sim == "div0":
            final = "ambos_div0"
        else:
            final = "divergente"
        relatorio.append({
            "par": l["par"], "tamanho": l["tamanho"], "arquivo": l["arquivo"],
            "configuracao": l["configuracao"], "rotulo": l["rotulo"], "snr_db": l["snr_db"], "selecao": l["selecao"],
            "max_abs_parte": l["max_abs_parte"],
            "hls_vs_golden_8_etapas": status_hls, "simulador": sim,
            "simulador_vs_golden_08": {True: "igual", False: "diferente", None: "-"}[sim_vs_golden],
            "simulador_vs_hls_08": {True: "igual", False: "diferente", None: "-"}[sim_vs_hw],
            "resultado": final,
            "hls_vs_float_erro_max_lsb": "-" if cf is None else f"{cf[0]:.4g}",
            "hls_vs_float_erro_rel": "-" if cf is None else f"{cf[1]:.4g}",
            "hls_vs_float_partes_iguais_ao_arredondado": "-" if cf is None else f"{cf[2]:.4f}"})

    with open(validacao / "relatorio.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(relatorio[0]))
        w.writeheader()
        w.writerows(relatorio)

    resumo = [f"Formato (parametros.env):\n{texto_tipos}",
              f"{'par':24s} {'tam':6s} {'total':>6s} {'igual':>6s} {'ambos_div0':>11s} "
              f"{'divergente':>11s}"]
    grupos = {}
    for r in relatorio:
        grupos.setdefault((r["par"], r["tamanho"]), []).append(r["resultado"])
    for (par, tam), rs in sorted(grupos.items()):
        resumo.append(f"{par:24s} {tam:6s} {len(rs):6d} {rs.count('igual'):6d} "
                      f"{rs.count('ambos_div0'):11d} {rs.count('divergente'):11d}")
    todos = [r["resultado"] for r in relatorio]
    resumo.append(f"{'total':24s} {'':6s} {len(todos):6d} {todos.count('igual'):6d} "
                  f"{todos.count('ambos_div0'):11d} {todos.count('divergente'):11d}")
    resumo.append("\nigual: hardware = golden_cholesky.py nas 8 etapas e simulador = hardware "
                  "na inversa (bits)\nambos_div0: hardware, golden e simulador dividem por zero "
                  "(alguma parte acima da faixa do tipo); não testa bits\ndivergente: qualquer "
                  "outro caso (ver relatorio.csv)")
    resumo.append(f"\nHardware contra a inversão em float64 das curvas (matrizes 'igual'; "
                  f"LSB = 2^-{fmt.fix.frac}):")
    resumo.append(f"{'par':24s} {'tam':6s} {'erro rel. mediano':>18s} {'erro rel. máx.':>15s} "
                  f"{'erro máx. (LSB)':>16s} {'partes = arredondado':>21s}")
    for (par, tam), _ in sorted(grupos.items()):
        rs = [r for r in relatorio if (r["par"], r["tamanho"]) == (par, tam)
              and r["resultado"] == "igual"]
        if not rs:
            continue
        rel = [float(r["hls_vs_float_erro_rel"]) for r in rs]
        lsb = [float(r["hls_vs_float_erro_max_lsb"]) for r in rs]
        ig = [float(r["hls_vs_float_partes_iguais_ao_arredondado"]) for r in rs]
        resumo.append(f"{par:24s} {tam:6s} {np.median(rel):18.3g} {max(rel):15.3g} "
                      f"{max(lsb):16.3g} {np.mean(ig):21.1%}")
    resumo.append("")
    (validacao / "resumo.txt").write_text("\n".join(resumo) + "\n")
    print("\n".join(resumo))


if __name__ == "__main__":
    main()
