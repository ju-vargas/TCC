#!/usr/bin/env python3
"""
Varredura de formatos de ponto fixo da inversão do BCD-MMSE, com o próprio hardware
HLS fazendo a inversão dentro do simulador (--bcd-inverse hls): o simulador manda
cada matriz den ao servidor do hardware (hardware/cholesky_hardware_servidor) e usa
a inversa que ele devolve.

Formatos (I bits inteiros com o sinal, F fracionários):
  varredura de I, com F = 32:  I = 6, 8, 10, 12, 14, 16, 20, 24, 32
  varredura de F, com I = 14:  F = 4, 6, 8, 10, 12, 16, 20, 24, 32
  larguras menores, I = F:     ap_fixed<12,6> e ap_fixed<14,7>
Modos: as 35 combinações de quantização (7) e estouro (5) do ap_fixed.
Configurações 1, 11 e 12 do texto (rótulos a, 8 e 10); condições TDLA30-75 (N = 192, 28 GHz) e
TDLB100-400 (N = 24, 3,5 GHz). Curvas: BCD-MMSE com 1 a 4 iterações. LMMSE e ZF
não dependem da inversão do BCD e vêm da referência ideal (float64).

Com --snr-perto, cada (configuração, condição) roda só as SNRs em volta do ponto em
que a referência ideal cruza SER = 10^-2: do ponto da grade logo abaixo do cruzamento
com 4 iterações ao ponto logo acima do cruzamento com 1 iteração, mais --extra-direita
pontos à direita (padrão 2), para medir perdas de até uns 5 dB. Como o simulador sorteia
canais, ruído e símbolos em sequência, SNR a SNR, pular SNRs muda os sorteios; por isso a
referência ideal (float64) é simulada de novo nas mesmas SNRs, com a mesma semente, e vai
em cada JSON (ser_referencia). Sem --snr-perto, a referência é a rodada completa de
resultados/1_referencia_float.

Cada rodada (formato, modo, configuração, condição) vira um JSON em
<saida>/dados/<condição>/configuracao_<k>/<I>_<F>_<Q>_<O>.json, gravado de uma vez;
uma rodada que já tem o JSON é pulada, então a varredura pode ser retomada.

Uso (com o Python do simulador):
    ../simulador/.venv/bin/python varredura_formatos.py [-o PASTA] [-j 8]
        [--formatos 6:32,14:8] [--modos AP_TRN:AP_SAT] [--configuracoes a,8,10]
        [--condicoes TDLA30-75,TDLB100-400] [--snr-perto [--extra-direita 2] [--referencia DIR]]
        [--rapido]
"""

import argparse
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "simulador"))

QUANTS = ("AP_TRN", "AP_TRN_ZERO", "AP_RND", "AP_RND_ZERO", "AP_RND_MIN_INF", "AP_RND_INF",
          "AP_RND_CONV")
OVERFLOWS = ("AP_SAT", "AP_SAT_ZERO", "AP_SAT_SYM", "AP_WRAP", "AP_WRAP_SM")
FORMATOS = sorted({(i, 32) for i in (6, 8, 10, 12, 14, 16, 20, 24, 32)}
                  | {(14, f) for f in (4, 6, 8, 10, 12, 14, 16, 20, 24, 32)}
                  | {(6, 6), (7, 7)}, key=lambda x: (x[0] + x[1], x[0]))
ITERACOES = (1, 2, 3, 4)
GRADE = tuple(range(-10, 11, 2))
REFERENCIA = AQUI / "resultados" / "1_referencia_float" / "curvas"


def grade_perto(rotulo: str, cond: str, extra: int, referencia: Path = REFERENCIA) -> tuple:
    """SNRs da grade em volta do cruzamento da referência ideal com SER = 10^-2. A grade é a
    do arquivo de referência ("snr_db", se houver; senão GRADE)."""
    from dbp_sim.params import M1_Driver
    from figuras_formatos import snr_no_alvo
    n, fc = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}[cond]
    pasta = next(p for p in referencia.iterdir()
                 if p.name.endswith(f"_N{n}_{fc / 1e9:g}GHz") and cond in p.name.split("_")[0].split("+"))
    tudo = json.loads((pasta / "bcd_iterations_results.json").read_text())
    grade = tuple(tudo.get("snr_db", GRADE))
    ref = tudo[rotulo]
    cruz = [snr_no_alvo(grade, ref[f"BCD-MMSE (iter {it})"]) for it in ITERACOES]
    cruz = [c for c in cruz if c is not None]
    if not cruz:
        raise SystemExit(f"{rotulo} {cond}: a referência não cruza SER = 10^-2 dentro da "
                         f"grade {grade[0]} a {grade[-1]} dB")
    lo = max(g for g in grade if g <= min(cruz))
    hi = min(g for g in grade if g >= max(cruz))
    hi = max(hi, lo + 2)
    return tuple(g for g in grade if lo <= g <= hi + 2 * extra)


def caminho_ref(saida: Path, cond: str, config: int) -> Path:
    return saida / "referencias" / cond / f"configuracao_{config}.json"


def rodar_referencia(tarefa):
    """Referência ideal (inversão em float64) nas SNRs de grade, com a mesma semente."""
    rotulo, cond, grade, saida = tarefa
    from dbp_sim.m1_driver import SimConfig, run_panel
    from dbp_sim.params import PANELS_BY_LABEL, M1_Driver, TCC_CONFIGURATION
    k = TCC_CONFIGURATION[rotulo]
    destino = caminho_ref(saida, cond, k)
    if destino.exists():
        return f"referência configuracao_{k} {cond}: já existe"
    n, fc = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}[cond]
    painel = PANELS_BY_LABEL[rotulo]
    cfg = SimConfig.from_panel(painel, n_noise_samples=n, carrier_hz=fc,
                               bcd_iteration_list=ITERACOES, skip_reference_curves=True,
                               snr_db_grid=grade)
    t0 = time.time()
    ser = run_panel(cfg)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps({"rotulo": rotulo, "configuracao": k, "condicao": cond,
                                   "snr_db": list(grade),
                                   "ser": {c: list(map(float, v)) for c, v in ser.items()}}))
    return f"referência configuracao_{k} {cond} {list(grade)}: {time.time() - t0:.0f} s"


def caminho(saida: Path, cond: str, config: int, fmt) -> Path:
    I, F, q, o = fmt
    return saida / "dados" / cond / f"configuracao_{config}" / f"{I}_{F}_{q}_{o}.json"


def rodar_formato(tarefa):
    """Todas as (configuração, condição) de um formato e modo, no mesmo processo, para
    reaproveitar os servidores do hardware. Devolve uma linha de log por rodada."""
    fmt, rodadas, saida, rapido, grades = tarefa
    from dbp_sim import hls_inverse
    from dbp_sim.m1_driver import SimConfig, run_panel
    from dbp_sim.params import PANELS_BY_LABEL as paineis, M1_Driver, TCC_CONFIGURATION
    condicoes = {c: (n, fc) for c, n, _, fc in M1_Driver.test_conditions.value}
    I, F, q, o = fmt
    log = []
    for rotulo, cond in rodadas:
        k = TCC_CONFIGURATION[rotulo]
        destino = caminho(saida, cond, k, fmt)
        if destino.exists():
            continue
        n, fc = condicoes[cond]
        extra = dict(n_realizations=3, n_symbols=200, snr_db_grid=(-10, -6, -4, -2, 0)) \
            if rapido else {}
        ref = None
        if grades:
            extra["snr_db_grid"] = grades[(rotulo, cond)]
            ref = json.loads(caminho_ref(saida, cond, k).read_text())
            assert tuple(ref["snr_db"]) == tuple(extra["snr_db_grid"])
        cfg = SimConfig.from_panel(paineis[rotulo], n_noise_samples=n, carrier_hz=fc,
                                   bcd_iteration_list=ITERACOES, skip_reference_curves=True,
                                   bcd_inverse="hls", hw_int_bits=I, hw_frac_bits=F,
                                   hw_quant=q, hw_overflow=o, **extra)
        hls_inverse.reset_stats()
        t0 = time.time()
        ser = run_panel(cfg)
        st = dict(hls_inverse.stats)
        # Ordem das chamadas: realização -> SNR -> 4 iterações x C clusters
        esperado = cfg.n_realizations * len(cfg.snr_db_grid) * len(ITERACOES) * cfg.C
        if st["calls"] != esperado:
            raise RuntimeError(f"{destino.name}: {st['calls']} inversões, esperado {esperado}")
        dados = {"int_bits": I, "frac_bits": F, "quant": q, "overflow": o,
                 "configuracao": k, "rotulo": rotulo, "condicao": cond, "n_amostras": n,
                 "portadora_ghz": fc / 1e9, "snr_db": list(cfg.snr_db_grid),
                 "ser": {c: list(map(float, v)) for c, v in ser.items()},
                 "inversoes": st["calls"], "matrizes_no_hardware": st["hls_calls"],
                 "falhas": st["failed_calls"], "timeouts": st["timeouts"],
                 "segundos": round(time.time() - t0, 1),
                 "realizacoes": cfg.n_realizations, "simbolos": cfg.n_symbols}
        if ref is not None:
            dados["ser_referencia"] = ref["ser"]
        destino.parent.mkdir(parents=True, exist_ok=True)
        tmp = destino.with_suffix(".tmp")
        tmp.write_text(json.dumps(dados))
        tmp.replace(destino)
        log.append(f"{I}_{F}_{q}_{o} configuracao_{k} {cond}: {dados['segundos']} s, "
                   f"{st['failed_calls']} falhas em {st['hls_calls']} matrizes")
    hls_inverse.close_all()
    return log


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("-o", "--saida", default=None,
                        help="Pasta (padrão: resultados/4_varredura_formatos/<data-hora>/)")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count())
    parser.add_argument("--formatos", default=None, help="I:F,... (padrão: a grade inteira)")
    parser.add_argument("--modos", default=None, help="QUANT:OVERFLOW,... (padrão: os 35)")
    parser.add_argument("--configuracoes", default="a,8,10",
                        help="Rótulos das configurações (padrão: a,8,10 = configurações 1, 11 e 12)")
    parser.add_argument("--condicoes", default="TDLA30-75,TDLB100-400")
    parser.add_argument("--snr-perto", action="store_true",
                        help="Só as SNRs em volta do cruzamento com 10^-2, com a referência "
                             "simulada junto")
    parser.add_argument("--extra-direita", type=int, default=2,
                        help="Pontos da grade à direita do cruzamento (com --snr-perto)")
    parser.add_argument("--referencia", default=str(REFERENCIA),
                        help="Pasta da referência float que escolhe as SNRs (com --snr-perto; "
                             "padrão: resultados/1_referencia_float/curvas)")
    parser.add_argument("--rapido", action="store_true",
                        help="3 realizações x 200 símbolos, 5 SNRs (teste)")
    args = parser.parse_args()

    # Uma thread por processo: são vários simuladores e servidores nos mesmos núcleos
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"
    saida = Path(args.saida) if args.saida else \
        AQUI / "resultados" / "4_varredura_formatos" / f"{time.strftime('%Y%m%d-%H%M%S')}"
    saida.mkdir(parents=True, exist_ok=True)
    formatos = ([tuple(int(x) for x in f.split(":")) for f in args.formatos.split(",")]
                if args.formatos else FORMATOS)
    modos = ([tuple(m.split(":")) for m in args.modos.split(",")] if args.modos
             else list(itertools.product(QUANTS, OVERFLOWS)))
    rodadas = [(r.strip(), c.strip()) for r in args.configuracoes.split(",")
               for c in args.condicoes.split(",")]
    # Modo por modo, com todos os formatos de cada um: AP_TRN/AP_SAT (o hardware atual)
    # sai primeiro inteiro, mesmo que a varredura seja interrompida
    # Uma tarefa por (formato, modo, configuração), com as condições dentro: com poucos
    # formatos, as configurações também se dividem entre os núcleos
    grades = ({(r, c): grade_perto(r, c, args.extra_direita, Path(args.referencia))
               for r, c in rodadas}
              if args.snr_perto else None)
    tarefas = [((I, F, q, o), [(r, c) for r2, c in rodadas if r2 == r], saida, args.rapido,
                grades)
               for (q, o), (I, F) in itertools.product(modos, formatos)
               for r in dict.fromkeys(r for r, _ in rodadas)]
    (saida / "parametros.json").write_text(json.dumps({
        "formatos": formatos, "modos": modos, "rodadas": rodadas, "rapido": args.rapido,
        "snr_perto": args.snr_perto, "extra_direita": args.extra_direita,
        "grades": {f"{r}|{c}": g for (r, c), g in grades.items()} if grades else None,
        "referencia": ("simulada junto, nas mesmas SNRs (referencias/)" if grades else
                       "software/testes/resultados/1_referencia_float (float64)")}, indent=1))
    print(f"{len(tarefas)} tarefas (formato x modo x configuração), "
          f"{len(tarefas) * len(rodadas) // max(1, len(dict.fromkeys(r for r, _ in rodadas)))} "
          f"rodadas -> {saida}", flush=True)
    feitos, t0 = 0, time.time()
    if grades:
        with ProcessPoolExecutor(args.jobs) as ex:
            for linha in ex.map(rodar_referencia, [(r, c, g, saida) for (r, c), g in grades.items()]):
                print(linha, flush=True)
    with ProcessPoolExecutor(args.jobs) as ex:
        futuros = [ex.submit(rodar_formato, t) for t in tarefas]
        for f in as_completed(futuros):
            feitos += 1
            for linha in f.result():
                print(linha, flush=True)
            print(f"[{feitos}/{len(tarefas)}] {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
