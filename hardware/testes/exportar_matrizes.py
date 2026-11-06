#!/usr/bin/env python3
"""
Exporta as matrizes que o simulador realmente inverte no BCD-MMSE.

Cada DU c inverte den = Es * H_c H_c^H + R_cc (M_c x M_c, com o condicionamento
Ledoit-Wolf do simulador). O script roda o próprio run_panel do simulador, com
a mesma semente, e troca a função de inversão por uma que guarda cada den antes
de inverter. Assim as matrizes são exatamente as do simulador, na mesma
sequência de números aleatórios. den não muda entre as iterações do BCD, então
basta uma iteração.

As condições de teste (params.M1_Driver.test_conditions) mudam o número de
amostras de ruído e a portadora. Condições com os mesmos valores dão as mesmas
matrizes, então cada par (amostras, portadora) é rodado uma vez e vai para a
própria pasta, com uma pasta por tamanho dentro dela:
  2_amostra_matrizes/amostras192_fc3.5GHz/16x16/, .../32x32/, 2_amostra_matrizes/amostras24_fc3.5GHz/...
Cada matriz vira dois arquivos, com o painel no nome:
  .txt   formato do A.txt (n e depois as linhas com "re+imj"), com cada número
         em decimal exato: a leitura (std::stod no testbench, complex() no
         golden_cholesky.py) devolve exatamente o mesmo float64 do simulador
  .bits  os 64 bits IEEE 754 de cada parte, "real:imag" por elemento, no mesmo
         layout dos .bits do hardware
O indice.csv de cada pasta lista a origem e a faixa de cada matriz; uma nova
exportação atualiza as linhas dos mesmos arquivos e mantém as outras.

Uso (com o Python do simulador, que tem numpy e os dados do QuaDRiGa):
    PY=../../software/simulador/.venv/bin/python

    # manual: realizações, SNRs e clusters escolhidos
    $PY exportar_matrizes.py --painel a --realizacoes 0-4 --snr=-10,0,10 --clusters 0,1

    # amostra: métricas de todas as matrizes e exportação só de uma amostra
    # (cobertura por painel e SNR, extremos de cada métrica, estratos opcionais),
    # para cada par (amostras, portadora) das condições de teste
    $PY exportar_matrizes.py --amostra --condicoes all --casos pior,media

    # manual em uma condição de teste
    $PY exportar_matrizes.py --condicao HST350 --painel a --realizacoes 0 --snr=0
"""

import argparse
import csv
import math
import struct
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
SIMULADOR = AQUI.parents[1] / "software" / "simulador"
sys.path.insert(0, str(SIMULADOR))

from dbp_sim import hw_inverse                      # noqa: E402
from dbp_sim.m1_driver import SimConfig, run_panel  # noqa: E402
from dbp_sim.params import ALL_PANELS, M1_Driver, TCC_CONFIGURATION  # noqa: E402

#: Condições de teste: nome -> {"pior": N, "media": N, "fc": portadora em Hz}. "pior" é o
#: N do pior símbolo de dados do slot; "media", a média nos símbolos (Tabela tab:n-condicao)
CONDICOES = {c: {"pior": nw, "media": nm, "fc": fc}
             for c, nw, nm, fc in M1_Driver.test_conditions.value}
CASOS = ("pior", "media")


def ler_env(caminho: Path) -> dict:
    """NOME=valor por linha; ignora linhas vazias e comentários."""
    valores = {}
    for linha in caminho.read_text().splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, valor = linha.split("=", 1)
        valores[nome.strip()] = valor.strip()
    return valores


def intervalo(texto: str) -> list[int]:
    """Índices não negativos: "0-4" -> [0, 1, 2, 3, 4]; "0,3,7" -> [0, 3, 7]."""
    saida = []
    for parte in texto.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-", 1)
            saida += list(range(int(a), int(b) + 1))
        elif parte:
            saida.append(int(parte))
    return saida


def decimal_exato(x: float) -> str:
    """O valor exato do float64 em decimal posicional, sem expoente. O
    testbench separa real e imaginário pelo primeiro sinal depois do início do
    texto, então notação científica (1e-05) ou hexfloat (p+4) não servem."""
    texto = format(Decimal(x), "f")
    if math.copysign(1.0, x) < 0 and not texto.startswith("-"):
        texto = "-" + texto           # -0.0 mantém o sinal
    return texto


def bits64(x: float) -> str:
    """Os 64 bits IEEE 754 do float64, do mais significativo para o menos."""
    return format(struct.unpack("<Q", struct.pack("<d", x))[0], "064b")


def escrever_matriz(base: Path, A: np.ndarray):
    """Grava base.txt (decimal exato) e base.bits (bits IEEE 754)."""
    n = A.shape[0]
    with open(base.with_suffix(".txt"), "w") as f:
        f.write(f"{n}\n")
        for linha in A:
            elems = []
            for z in linha:
                im = decimal_exato(float(z.imag))
                elems.append(f"{decimal_exato(float(z.real))}"
                             f"{im if im.startswith('-') else '+' + im}j")
            f.write(" ".join(elems) + "\n")
    with open(base.with_suffix(".bits"), "w") as f:
        f.write(f"{n}\n")
        for linha in A:
            f.write(" ".join(f"{bits64(float(z.real))}:{bits64(float(z.imag))}"
                             for z in linha) + "\n")


def ler_txt(caminho: Path) -> np.ndarray:
    """Lê um .txt exportado (mesma regra do golden.py: complex() por elemento)."""
    linhas = [l.split() for l in caminho.read_text().splitlines() if l.strip()]
    return np.array([[complex(t) for t in l] for l in linhas[1:]])


def capturar(cfg: SimConfig) -> list[np.ndarray]:
    """Roda run_panel e devolve, na ordem das chamadas, cada den invertido."""
    dens = []

    def captura(den):
        dens.append(den.copy())
        return np.linalg.inv(den)

    original = hw_inverse.make_inverter
    hw_inverse.make_inverter = lambda *args, **kwargs: captura
    try:
        run_panel(cfg)
    finally:
        hw_inverse.make_inverter = original
    return dens


# ---------------------------------------------------------------------------
# Métricas, gravação e índice
# ---------------------------------------------------------------------------

# Colunas do indice.csv. As métricas resumem o que cada matriz testa:
#   max_abs_parte    maior |re| ou |im|; perto de 2^(I-1), estoura os bits inteiros
#   max_abs_inversa  maior entrada da inversa; precisa caber no tipo de dados
#   menor_autovalor  comparado com 2^-F, quanto da precisão sobra
#   numero_condicao  quanto o erro de arredondamento é amplificado
#   n_amostras e portadora_ghz: amostras de ruído e portadora da rodada; condicoes:
#   as condições de teste que têm esses valores ("-" = padrão do simulador)
#   configuracao: número da configuração no texto (Tabela tab:paineis); rotulo: o
#   rótulo interno do simulador, que é o que vai no nome do arquivo
COLUNAS = ["arquivo", "configuracao", "rotulo", "realizacao", "snr_db", "cluster", "n", "n_amostras",
           "portadora_ghz", "condicoes", "max_abs_parte", "max_abs_inversa",
           "menor_autovalor", "numero_condicao", "motivo"]


def metricas(den: np.ndarray) -> dict:
    autov = np.linalg.eigvalsh(den)
    partes = np.concatenate([den.real.ravel(), den.imag.ravel()])
    return {
        "max_abs_parte": float(np.abs(partes).max()),
        "max_abs_inversa": float(np.abs(np.linalg.inv(den)).max()),
        "menor_autovalor": float(autov[0]),
        "numero_condicao": float(autov[-1] / autov[0]),
    }


def nome_matriz(painel: str, r: int, snr: int, c: int) -> str:
    return f"painel_{painel}_r{r:03d}_snr{snr:+03d}_c{c:02d}"


def atualizar_csv(caminho: Path, linhas: list[dict], chave):
    """Grava linhas no CSV, trocando as que tiverem a mesma chave e mantendo as outras."""
    antigas = []
    if caminho.exists():
        with open(caminho, newline="") as f:
            antigas = list(csv.DictReader(f))
    novas = {chave(l) for l in linhas}
    todas = [l for l in antigas if chave(l) not in novas] + linhas
    todas.sort(key=lambda l: (int(l["configuracao"]), int(l["realizacao"]), int(l["snr_db"]),
                              int(l["cluster"])))
    with open(caminho, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS, restval="", extrasaction="ignore")
        w.writeheader()
        w.writerows(todas)
    return len(todas)


def linha_indice(painel: str, r: int, snr: int, c: int, n: int, m: dict, motivo: str,
                 grupo: dict):
    return {"arquivo": nome_matriz(painel, r, snr, c),
            "configuracao": TCC_CONFIGURATION[painel], "rotulo": painel, "realizacao": r,
            "snr_db": snr, "cluster": c, "n": n, "motivo": motivo,
            "n_amostras": grupo["n_noise_samples"],
            "portadora_ghz": f"{grupo['carrier_hz'] / 1e9:g}",
            "condicoes": grupo["condicoes"],
            **{k: f"{v:.6g}" for k, v in m.items()}}


def grupos_de_condicoes(texto: str | None, casos: str = "pior") -> list[dict]:
    """Agrupa as condições pedidas por (amostras, portadora), no caso pior, médio ou
    nos dois. Sem condições, um grupo só com os valores padrão do simulador. Cada grupo
    tem as chaves de SimConfig (n_noise_samples, carrier_hz), o nome das condições e a
    pasta de saída. Condições com N = 0 (HST no pior caso) ficam de fora."""
    if not texto:
        cfg = SimConfig(M=1, C=1, K=1, r=1, iot_db=0.0, modulation="QPSK")
        n, fc, nomes = cfg.n_noise_samples, cfg.carrier_hz, "-"
        return [{"n_noise_samples": n, "carrier_hz": fc, "condicoes": nomes,
                 "pasta": f"amostras{n}_fc{fc / 1e9:g}GHz"}]
    nomes = (list(CONDICOES) if texto.strip() == "all"
             else [c.strip() for c in texto.split(",") if c.strip()])
    desconhecidas = [c for c in nomes if c not in CONDICOES]
    if desconhecidas:
        raise SystemExit(f"condição desconhecida {desconhecidas}; use {', '.join(CONDICOES)}")
    lista_casos = [x.strip() for x in casos.split(",") if x.strip()]
    if not lista_casos or any(x not in CASOS for x in lista_casos):
        raise SystemExit(f"caso desconhecido {casos!r}; use pior, media ou pior,media")
    por_chave: dict[tuple, list[str]] = {}
    for caso in lista_casos:
        for c in nomes:
            n = CONDICOES[c][caso]
            if n == 0:
                print(f"  {c}: N = 0 no caso {caso}, estimação inviável; fica de fora")
                continue
            rotulo = (c if caso == "pior" or CONDICOES[c]["pior"] == n
                      else f"{c}-media")
            rotulos = por_chave.setdefault((n, CONDICOES[c]["fc"]), [])
            if rotulo not in rotulos:
                rotulos.append(rotulo)
    return [{"n_noise_samples": n, "carrier_hz": fc, "condicoes": "+".join(cs),
             "pasta": f"amostras{n}_fc{fc / 1e9:g}GHz"}
            for (n, fc), cs in por_chave.items()]


def exportar(pasta: Path, itens: list[tuple[dict, np.ndarray]]) -> int:
    """Grava .txt e .bits de cada (linha do índice, den) e atualiza o indice.csv."""
    pasta.mkdir(parents=True, exist_ok=True)
    for linha, den in itens:
        escrever_matriz(pasta / linha["arquivo"], den)
        # A leitura do .txt precisa devolver exatamente os mesmos bits
        if not np.array_equal(ler_txt(pasta / f"{linha['arquivo']}.txt"), den):
            raise SystemExit(f"{linha['arquivo']}.txt não reproduz o float64 exato")
    return atualizar_csv(pasta / "indice.csv", [l for l, _ in itens],
                         chave=lambda l: l["arquivo"])


def rodar_painel(painel, n_realizacoes: int, grupo: dict):
    """Roda o simulador e devolve (cfg, grade de SNR, dens na ordem das chamadas)."""
    cfg = SimConfig.from_panel(painel, n_realizations=n_realizacoes, bcd_iteration_list=(1,),
                               n_noise_samples=grupo["n_noise_samples"],
                               carrier_hz=grupo["carrier_hz"])
    grade = list(cfg.snr_db_grid)
    dens = capturar(cfg)
    esperado = n_realizacoes * len(grade) * painel.C
    if len(dens) != esperado:
        raise SystemExit(f"esperava {esperado} inversões, o simulador fez {len(dens)}; "
                         "a ordem das chamadas mudou e o índice não é confiável")
    return cfg, grade, dens


def conferir_env(caminho: Path, n: int, onde: str):
    if caminho.exists():
        n_env = ler_env(caminho).get("CHOL_N", "")
        if n_env and int(n_env) != n:
            print(f"ATENCAO: CHOL_N={n_env} em {caminho.name}, mas {onde} tem matrizes "
                  f"{n} x {n}. Ajuste CHOL_N antes de rodar o hardware nelas.")


# ---------------------------------------------------------------------------
# Modo manual: realizações, SNRs e clusters escolhidos
# ---------------------------------------------------------------------------

def modo_manual(args, paineis):
    painel = paineis[args.painel]
    C = painel.C
    Mc = painel.M // C
    reals = intervalo(args.realizacoes)
    clusters = intervalo(args.clusters) if args.clusters else list(range(C))
    for c in clusters:
        if not 0 <= c < C:
            raise SystemExit(f"cluster {c} não existe no painel {painel.label} (C = {C})")
    conferir_env(Path(args.env), Mc, f"o painel {painel.label}")
    grupos = grupos_de_condicoes(args.condicao, args.caso)
    if not grupos:
        raise SystemExit(f"{args.condicao} não tem amostras no caso {args.caso}")
    grupo = grupos[0]

    # As primeiras R realizações de uma rodada são as mesmas de uma rodada
    # completa (mesma semente), então basta rodar até a maior pedida.
    print(f"Painel {painel.label}: M={painel.M}, C={C}, M_c={Mc}, "
          f"amostras={grupo['n_noise_samples']}, portadora="
          f"{grupo['carrier_hz'] / 1e9:g} GHz; rodando o simulador...")
    cfg, grade, dens = rodar_painel(painel, max(reals) + 1, grupo)
    snrs = [int(x) for x in args.snr.split(",")] if args.snr else grade
    for x in snrs:
        if x not in grade:
            raise SystemExit(f"SNR {x} dB fora da grade do simulador {grade}")

    itens = []
    for r in reals:
        for x in snrs:
            for c in clusters:
                den = dens[(r * len(grade) + grade.index(x)) * C + c]
                itens.append((linha_indice(painel.label, r, x, c, Mc, metricas(den),
                                           "manual", grupo), den))
    pasta = Path(args.saida) / grupo["pasta"] / f"{Mc}x{Mc}"
    total = exportar(pasta, itens)
    print(f"{len(itens)} matrizes {Mc} x {Mc} em {pasta}/ "
          f"(.txt decimal exato e .bits IEEE 754; {total} no indice.csv)")


# ---------------------------------------------------------------------------
# Modo amostra: cobertura dos pontos de operação + extremos + estratos
# ---------------------------------------------------------------------------

# Extremos: (métrica, True = maiores valores, False = menores)
EXTREMOS = [("max_abs_parte", True), ("numero_condicao", True),
            ("max_abs_inversa", True), ("menor_autovalor", False)]


def semente_painel(rotulo: str) -> int:
    """Parte da semente da cobertura que vem do painel. Rótulos de um caractere (a a g,
    7 a 9) usam ord(), como antes, e a cobertura deles não muda; os de dois (10 a 16)
    usam 1000 + o número, que não coincide com nenhum ord() de letra ou dígito."""
    return ord(rotulo) if len(rotulo) == 1 else 1000 + int(rotulo)


def modo_amostra(args, paineis):
    """Roda a amostragem uma vez por par (amostras, portadora) das condições pedidas,
    cada um na própria pasta, para os extremos de um par não esconderem os do outro."""
    grupos = grupos_de_condicoes(args.condicoes, args.casos)
    print("pares (amostras, portadora); condições com os mesmos valores dividem um:")
    for g in grupos:
        print(f"  amostras = {g['n_noise_samples']:3d}  portadora = "
              f"{g['carrier_hz'] / 1e9:g} GHz  {g['condicoes']}  -> {g['pasta']}/")
    for g in grupos:
        print(f"\n=== {g['pasta']} ({g['condicoes']}) ===", flush=True)
        amostra_grupo(args, paineis, g)


def amostra_grupo(args, paineis, grupo: dict):
    """Calcula as métricas de todas as matrizes dos painéis pedidos e exporta só
    uma amostra, com o motivo de cada escolha na coluna "motivo":

      cobertura   --por-snr matrizes sorteadas para cada (painel, SNR)
      <métrica>   as --extremos maiores (ou menores, no menor autovalor) de cada
                  tamanho de matriz, para max_abs_parte, numero_condicao,
                  max_abs_inversa e menor_autovalor
      estrato     --por-estrato sorteadas em cada uma das --estratos faixas de
                  log10(numero_condicao), em cada tamanho (desligado com 0)

    O sorteio usa --semente, então a mesma chamada escolhe as mesmas matrizes.
    As métricas de todas vão para indice_completo.csv, na pasta de cada tamanho.
    """
    rotulos = [x.strip() for x in args.paineis.split(",") if x.strip()]
    for rot in rotulos:
        if rot not in paineis:
            raise SystemExit(f"painel {rot!r} não existe; use {sorted(paineis)}")

    # Por tamanho de matriz: lista de (linha do índice sem motivo, den)
    por_tamanho: dict[int, list] = {}
    for rot in rotulos:
        painel = paineis[rot]
        C, Mc = painel.C, painel.M // painel.C
        print(f"Painel {rot}: M={painel.M}, C={C}, M_c={Mc}; rodando o simulador "
              f"({args.n_realizacoes} realizações)...", flush=True)
        _, grade, dens = rodar_painel(painel, args.n_realizacoes, grupo)
        lista = por_tamanho.setdefault(Mc, [])
        for r in range(args.n_realizacoes):
            for k, x in enumerate(grade):
                for c in range(C):
                    den = dens[(r * len(grade) + k) * C + c]
                    lista.append((linha_indice(rot, r, x, c, Mc, metricas(den), "",
                                               grupo), den))
        del dens

    for Mc, lista in sorted(por_tamanho.items()):
        pasta = Path(args.saida) / grupo["pasta"] / f"{Mc}x{Mc}"
        pasta.mkdir(parents=True, exist_ok=True)
        conferir_env(Path(args.env), Mc, f"a pasta {pasta.name}")
        atualizar_csv(pasta / "indice_completo.csv", [l for l, _ in lista],
                      chave=lambda l: l["arquivo"])

        motivos: dict[int, list[str]] = {}   # índice em lista -> motivos

        def marcar(i, motivo):
            motivos.setdefault(i, [])
            if motivo not in motivos[i]:
                motivos[i].append(motivo)

        # 1. Cobertura: cada (painel, SNR) com a própria semente, para a escolha
        #    não depender de quais outros painéis entraram na chamada
        grupos: dict[tuple, list[int]] = {}
        for i, (l, _) in enumerate(lista):
            grupos.setdefault((l["rotulo"], l["snr_db"]), []).append(i)
        for (rot, x), idx in sorted(grupos.items()):
            rng = np.random.default_rng([args.semente, semente_painel(rot), x + 1000])
            for i in rng.choice(idx, size=min(args.por_snr, len(idx)), replace=False):
                marcar(int(i), "cobertura")

        # 2. Extremos de cada métrica, no tamanho inteiro
        for nome, maiores in EXTREMOS:
            valores = np.array([float(l[nome]) for l, _ in lista])
            ordem = np.argsort(-valores if maiores else valores, kind="stable")
            for i in ordem[:args.extremos]:
                marcar(int(i), nome)

        # 3. Estratos de log10(numero_condicao)
        if args.estratos > 0 and args.por_estrato > 0:
            logk = np.log10([float(l["numero_condicao"]) for l, _ in lista])
            bordas = np.quantile(logk, np.linspace(0, 1, args.estratos + 1))
            faixa = np.clip(np.searchsorted(bordas, logk, side="right") - 1,
                            0, args.estratos - 1)
            for e in range(args.estratos):
                idx = np.flatnonzero(faixa == e)
                rng = np.random.default_rng([args.semente, Mc, e, 7])
                for i in rng.choice(idx, size=min(args.por_estrato, len(idx)),
                                    replace=False):
                    marcar(int(i), f"estrato{e}")

        itens = []
        for i, ms in sorted(motivos.items()):
            linha, den = lista[i]
            itens.append(({**linha, "motivo": "+".join(ms)}, den))
        total = exportar(pasta, itens)
        contagem = {}
        for ms in motivos.values():
            for m in ms:
                chave_m = "estrato" if m.startswith("estrato") else m
                contagem[chave_m] = contagem.get(chave_m, 0) + 1
        print(f"{Mc} x {Mc}: {len(itens)} de {len(lista)} matrizes exportadas em {pasta}/ "
              f"({total} no indice.csv; motivos: "
              + ", ".join(f"{k} {v}" for k, v in contagem.items()) + ")")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    paineis = {p.label: p for p in ALL_PANELS}
    parser = argparse.ArgumentParser(
        description="Exporta as matrizes M_c x M_c que o BCD-MMSE do simulador inverte.")
    parser.add_argument("-o", "--saida", default=str(AQUI / "2_amostra_matrizes"),
                        help="Pasta de saída; as matrizes vão para "
                             "<saída>/amostras<N>_fc<GHz>GHz/<n>x<n>/ (padrão: testes/2_amostra_matrizes/)")
    parser.add_argument("--env", default=str(AQUI / "parametros.env"),
                        help="parametros.env, para conferir CHOL_N (padrão: o desta pasta)")

    manual = parser.add_argument_group("modo manual (padrão)")
    manual.add_argument("--painel", default="a", choices=sorted(paineis),
                        help="Painel da Fig. 8 (padrão: a)")
    manual.add_argument("--realizacoes", default="0",
                        help='Realizações de canal, ex. "0-4" ou "0,7" (padrão: 0)')
    manual.add_argument("--snr", default=None,
                        help="SNRs em dB, com '=' por causa do sinal: --snr=-10,0,10 "
                             "(padrão: toda a grade do simulador)")
    manual.add_argument("--clusters", default=None,
                        help='Clusters, ex. "0-3" (padrão: todos)')
    manual.add_argument("--condicao", default=None, choices=sorted(CONDICOES),
                        help="Condição de teste, que define as amostras de ruído e a "
                             "portadora (padrão: os valores padrão do simulador)")
    manual.add_argument("--caso", default="pior", choices=CASOS,
                        help="Caso do N da condição: pior ou media (padrão: pior)")

    amostra = parser.add_argument_group(
        "modo amostra (--amostra): métricas de todas as matrizes, exporta só uma amostra")
    amostra.add_argument("--amostra", action="store_true",
                         help="Ativa o modo amostra")
    amostra.add_argument("--paineis", default="a,b,c,e,f,7,8,9,10,11,12,13",
                         help="Configurações (padrão: a,b,c,e,f,7,8,9,10,11,12,13, ou seja, "
                              "1 a 5 e 7 a 13 do texto; 6, 14, 15 e 16 só mudam a modulação, "
                              "que não entra na matriz invertida; o g tem a mesma distribuição "
                              "de matrizes do a)")
    amostra.add_argument("--n-realizacoes", type=int, default=100,
                         help="Realizações de cada painel usadas no sorteio (padrão: 100)")
    amostra.add_argument("--por-snr", type=int, default=3,
                         help="Matrizes sorteadas por (painel, SNR) (padrão: 3)")
    amostra.add_argument("--extremos", type=int, default=5,
                         help="Matrizes mais extremas por métrica e tamanho (padrão: 5)")
    amostra.add_argument("--estratos", type=int, default=10,
                         help="Faixas de log10(numero_condicao) (padrão: 10)")
    amostra.add_argument("--por-estrato", type=int, default=0,
                         help="Matrizes sorteadas por faixa; 0 desliga (padrão: 0)")
    amostra.add_argument("--semente", type=int, default=0,
                         help="Semente do sorteio (padrão: 0)")
    amostra.add_argument("--casos", default="pior",
                         help='Caso do N: "pior", "media" ou "pior,media" (padrão: pior)')
    amostra.add_argument("--condicoes", default="all",
                         help='Condições de teste, ex. "TDLA30-5,HST350", ou "all" '
                              "(padrão); uma rodada por par (amostras, portadora)")
    args = parser.parse_args()

    if args.amostra:
        modo_amostra(args, paineis)
    else:
        modo_manual(args, paineis)


if __name__ == "__main__":
    main()
