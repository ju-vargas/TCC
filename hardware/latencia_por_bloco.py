"""Tempo para inverter um bloco de N_PRB = 275 matrizes, por arquitetura e formato.

Lê os logs da simulação da netlist no servidor (Vivado 2023.2), em
resultados_servidor/xsim/*/versoes/*/trabalho/potencia/xsim_<condição>.log.
Cada log tem o instante em que cada lote (ou matriz) termina.

  latência do lote  = fim do primeiro lote - início
  intervalo do lote = maior espaço entre dois fins seguidos
  entrada do bloco  = lotes por bloco x intervalo do lote   (restrição de vazão)
  fim do bloco      = latência + (lotes por bloco - 1) x intervalo do lote

O último lote do bloco vai incompleto (275 não é múltiplo do lote) e é contado
como cheio. Clock de 100 MHz.

Saída: resultados_servidor/latencia_por_bloco.csv (separador ";" e vírgula
decimal, como resultados_vivado_servidor_planilha.csv).
"""
import csv
import glob
import math
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
XSIM = os.path.join(AQUI, "resultados_servidor", "xsim")
SAIDA = os.path.join(AQUI, "resultados_servidor", "latencia_por_bloco.csv")

N_PRB = 275
CICLOS_POR_MS = 100_000  # 100 MHz

ARQUITETURAS = {
    # nome: (matrizes por lote, condição alvo, f_D em Hz)
    "9090": (1, "TDLA30-5", 5),
    "4545": (1, "TDLA30-10", 10),
    "606": (12, "TDLA30-75", 75),
    "455": (16, "TDLC300-100", 100),
    "152_sistolico": (32, "TDLA30-300", 300),
    "114_sistolico": (32, "TDLB100-400", 400),
}
ORDEM_FORMATOS = ["18-8", "18-8-TRN-SAT", "20-8", "22-12", "24-12", "26-12", "28-14", "30-14"]


def ler_fins(caminho):
    texto = open(caminho, errors="ignore").read()
    return [int(t) for t in re.findall(r'RTL Simulation : \d+ / \d+ \[[^\]]*\] @ "(\d+)"', texto)]


def versao(pasta):
    """Devolve (formato, arquitetura) a partir do nome da pasta da versão."""
    nome = os.path.basename(pasta)
    if nome in ARQUITETURAS:  # pacote_servidor_2023: só <24,12>
        return "24-12", nome
    m = re.match(r"(.+?)_(" + "|".join(ARQUITETURAS) + r")$", nome)
    return (m.group(1), m.group(2)) if m else (None, None)


def formato_legivel(fmt):
    w, i = fmt.split("-")[:2]
    modo = "AP_TRN/AP_SAT" if "TRN-SAT" in fmt else "AP_RND_ZERO/AP_WRAP"
    return f"<{w},{i}>", modo


def br(x, casas):
    return f"{x:.{casas}f}".replace(".", ",")


linhas = []
for pasta in sorted(glob.glob(os.path.join(XSIM, "*", "versoes", "*"))):
    fmt, arq = versao(pasta)
    if fmt is None:
        continue
    lote, alvo, f_d = ARQUITETURAS[arq]
    log = os.path.join(pasta, "trabalho", "potencia", f"xsim_{alvo}.log")
    if not os.path.exists(log):
        logs = sorted(glob.glob(os.path.join(pasta, "trabalho", "potencia", "xsim_*.log")))
        if not logs:
            continue
        log = logs[0]
    t = ler_fins(log)  # em ps; período de 10 ns = 10.000 ps
    if len(t) < 3:
        continue
    latencia = (t[1] - t[0]) / 10_000
    intervalo = max(t[i + 1] - t[i] for i in range(1, len(t) - 1)) / 10_000
    lotes = math.ceil(N_PRB / lote)
    entrada = lotes * intervalo
    fim = latencia + (lotes - 1) * intervalo
    t_c_ms = 1 / (8 * f_d) * 1e3
    t_c = t_c_ms * CICLOS_POR_MS
    formato, modo = formato_legivel(fmt)
    linhas.append({
        "formato": formato,
        "quantizacao/overflow": modo,
        "arquitetura": arq,
        "condicao_alvo": alvo,
        "log": os.path.relpath(log, AQUI),
        "lotes_medidos": len(t) - 1,
        "matrizes_por_lote": lote,
        "lotes_por_bloco": lotes,
        "latencia_lote_ciclos": round(latencia),
        "intervalo_lote_ciclos": round(intervalo),
        "entrada_bloco_ms": br(entrada / CICLOS_POR_MS, 3),
        "fim_bloco_ms": br(fim / CICLOS_POR_MS, 3),
        "Tc_ms": br(t_c_ms, 4),
        "entrada_atende_Tc": "sim" if entrada <= t_c else "nao",
        "fim_atende_Tc": "sim" if fim <= t_c else "nao",
        "fim_em_relacao_a_Tc_pct": br((fim / t_c - 1) * 100, 1),
        "_ordem": (ORDEM_FORMATOS.index(fmt) if fmt in ORDEM_FORMATOS else 99, list(ARQUITETURAS).index(arq)),
    })

linhas.sort(key=lambda d: d["_ordem"])
campos = [c for c in linhas[0] if c != "_ordem"]
with open(SAIDA, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
    w.writeheader()
    w.writerows(linhas)
print(f"{len(linhas)} linhas em {os.path.relpath(SAIDA, AQUI)}")
