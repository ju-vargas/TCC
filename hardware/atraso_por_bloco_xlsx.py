"""Planilha com as contas de vazão e de atraso por bloco, com fórmulas.

Entrada: resultados_servidor/latencia_por_bloco.csv (gerado por latencia_por_bloco.py,
a partir dos logs xsim do servidor). Só a latência e o intervalo do lote vêm do CSV;
o resto é calculado por fórmulas na planilha.

Saída: resultados_servidor/atraso_por_bloco.xlsx
Depois de gerar, recalcular com o recalc.py do skill de xlsx (LibreOffice).
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(AQUI, "resultados_servidor", "latencia_por_bloco.csv")
SAIDA = os.path.join(AQUI, "resultados_servidor", "atraso_por_bloco.xlsx")

FONTE = "Arial"
F = Font(name=FONTE, size=10)
F_B = Font(name=FONTE, size=10, bold=True)
F_IN = Font(name=FONTE, size=10, color="0000FF")  # entradas (valores fixos)
F_T = Font(name=FONTE, size=12, bold=True)
CAB = PatternFill("solid", start_color="D9E2F3")
FINO = Side(style="thin", color="999999")
BORDA = Border(bottom=FINO)
QUEBRA = Alignment(wrap_text=True, vertical="top")

wb = Workbook()

# ---------------------------------------------------------------- Parâmetros
p = wb.active
p.title = "Parametros"
p["A1"] = "Parâmetros"; p["A1"].font = F_T
params = [
    ("N_PRB (PRBs por bloco)", 275, "Pior caso do 5G NR adotado por Zhao et al. (2025); ver modelo-de-sistema.tex."),
    ("Clock (MHz)", 100, "Escolha da autora (Seção Tools and Target Device)."),
    ("REs de DM-RS por PRB e por slot", 48, "4 símbolos x 12 subportadoras (TS 38.211, Tab. 6.4.1.1.3-4)."),
    ("Duração do slot em FR1 (ms)", 0.5, "SCS de 30 kHz (TS 38.211, Tab. 4.3.2-1)."),
    ("Duração do slot em FR2 (ms)", 0.125, "SCS de 120 kHz (TS 38.211, Tab. 4.3.2-1)."),
]
p["A3"], p["B3"], p["C3"] = "Parâmetro", "Valor", "Fonte"
for c in "ABC":
    p[f"{c}3"].font = F_B; p[f"{c}3"].fill = CAB
for i, (nome, val, fonte) in enumerate(params, start=4):
    p[f"A{i}"], p[f"B{i}"], p[f"C{i}"] = nome, val, fonte
    p[f"A{i}"].font = F; p[f"B{i}"].font = F_IN; p[f"C{i}"].font = F
p.column_dimensions["A"].width = 34
p.column_dimensions["B"].width = 10
p.column_dimensions["C"].width = 70
N_PRB, CLOCK, RE_SLOT, SLOT_FR1, SLOT_FR2 = ("Parametros!$B$4", "Parametros!$B$5", "Parametros!$B$6",
                                             "Parametros!$B$7", "Parametros!$B$8")

# ---------------------------------------------------------------- Condições
c = wb.create_sheet("Condicoes")
c["A1"] = "Condições de teste"; c["A1"].font = F_T
cab = ["Condição", "f_D (Hz)", "Faixa", "N", "T_c (ms)", "Duração do slot (ms)", "t_coleta (ms)"]
for j, h in enumerate(cab, start=1):
    cel = c.cell(row=3, column=j, value=h); cel.font = F_B; cel.fill = CAB; cel.alignment = QUEBRA
conds = [("TDLA30-5", 5, "FR1", 192), ("TDLA30-10", 10, "FR1", 192), ("TDLA30-75", 75, "FR2", 192),
         ("TDLA30-300", 300, "FR2", 168), ("TDLC300-100", 100, "FR1", 132), ("TDLB100-400", 400, "FR1", 24)]
for i, (nome, fd, fr, n) in enumerate(conds, start=4):
    c[f"A{i}"], c[f"B{i}"], c[f"C{i}"], c[f"D{i}"] = nome, fd, fr, n
    c[f"E{i}"] = f"=1/(8*B{i})*1000"
    c[f"F{i}"] = f'=IF(C{i}="FR1",{SLOT_FR1},{SLOT_FR2})'
    c[f"G{i}"] = f"=MIN(E{i},ROUNDUP(D{i}/{RE_SLOT},0)*F{i})"
    for col in "ACEFG":
        c[f"{col}{i}"].font = F
    for col in "BD":
        c[f"{col}{i}"].font = F_IN
    c[f"E{i}"].number_format = "0.0000"
    c[f"F{i}"].number_format = "0.000"
    c[f"G{i}"].number_format = "0.0000"
ult_c = 3 + len(conds)
notas_c = [
    "T_c = 1/(8 f_D) (Tse e Viswanath, p. 31 e 70). f_D: TS 38.104, Anexo G.",
    "N: Tabela tab:condicoes_teste (limitado a 192).",
    "t_coleta = min(T_c, ceil(N/48) x duração do slot): tempo para juntar as N amostras, com a espera.",
]
for k, txt in enumerate(notas_c, start=ult_c + 2):
    c[f"A{k}"] = txt; c[f"A{k}"].font = F
for j, w in enumerate([14, 9, 7, 6, 10, 12, 12], start=1):
    c.column_dimensions[get_column_letter(j)].width = w
c.row_dimensions[3].height = 30
RNG_COND = f"Condicoes!$A$4:$A${ult_c}"
RNG_TC = f"Condicoes!$E$4:$E${ult_c}"
RNG_COLETA = f"Condicoes!$G$4:$G${ult_c}"

# ---------------------------------------------------------------- Atraso
a = wb.create_sheet("Atraso")
a["A1"] = "Vazão e atraso por bloco de N_PRB matrizes"; a["A1"].font = F_T
cab = ["Formato", "Quantização / overflow", "Arquitetura", "Condição alvo",
       "Matrizes por lote", "Latência do lote (ciclos)", "Intervalo do lote (ciclos)",
       "Lotes por bloco", "Entrada do bloco (ms)", "Fim do bloco (ms)", "T_c (ms)",
       "Entrada <= T_c (vazão)", "Fim <= T_c", "Excesso sobre T_c (ms)",
       "t_coleta (ms)", "Atraso total (ms)"]
for j, h in enumerate(cab, start=1):
    cel = a.cell(row=3, column=j, value=h); cel.font = F_B; cel.fill = CAB; cel.alignment = QUEBRA
a.row_dimensions[3].height = 42

linhas = list(csv.DictReader(open(CSV, encoding="utf-8-sig"), delimiter=";"))
for i, d in enumerate(linhas, start=4):
    a[f"A{i}"] = d["formato"]
    a[f"B{i}"] = d["quantizacao/overflow"]
    a[f"C{i}"] = d["arquitetura"]
    a[f"D{i}"] = d["condicao_alvo"]
    a[f"E{i}"] = int(d["matrizes_por_lote"])
    a[f"F{i}"] = int(d["latencia_lote_ciclos"])
    a[f"G{i}"] = int(d["intervalo_lote_ciclos"])
    a[f"H{i}"] = f"=ROUNDUP({N_PRB}/E{i},0)"
    a[f"I{i}"] = f"=H{i}*G{i}/({CLOCK}*1000)"
    a[f"J{i}"] = f"=(F{i}+(H{i}-1)*G{i})/({CLOCK}*1000)"
    a[f"K{i}"] = f"=INDEX({RNG_TC},MATCH(D{i},{RNG_COND},0))"
    a[f"L{i}"] = f'=IF(I{i}<=K{i},"sim","não")'
    a[f"M{i}"] = f'=IF(J{i}<=K{i},"sim","não")'
    a[f"N{i}"] = f"=MAX(0,J{i}-K{i})"
    a[f"O{i}"] = f"=INDEX({RNG_COLETA},MATCH(D{i},{RNG_COND},0))"
    a[f"P{i}"] = f"=O{i}+J{i}"
    for col in "ABCDHIJKLMNOP":
        a[f"{col}{i}"].font = F
    for col in "EFG":
        a[f"{col}{i}"].font = F_IN
    for col in "IJKNOP":
        a[f"{col}{i}"].number_format = "0.000"
    a[f"F{i}"].number_format = "#,##0"
    a[f"G{i}"].number_format = "#,##0"
    a[f"F{i}"].comment = None
ult_a = 3 + len(linhas)
a["F3"].comment = Comment("Fim do primeiro lote menos o início, nos logs xsim do servidor "
                          "(resultados_servidor/xsim; ver coluna log de latencia_por_bloco.csv).", "TCC")
a["G3"].comment = Comment("Maior espaço entre o fim de dois lotes seguidos, nos mesmos logs.", "TCC")

notas = [
    "Valores em azul: medidos nos logs xsim do servidor (Vivado 2023.2). O resto é fórmula.",
    "Lotes por bloco = ROUNDUP(N_PRB / matrizes por lote). O último lote vai incompleto e conta como cheio.",
    "Entrada do bloco = lotes x intervalo / clock: tempo para aceitar as N_PRB matrizes. <= T_c garante a vazão.",
    "Fim do bloco = (latência + (lotes - 1) x intervalo) / clock: quando termina a última inversão do bloco.",
    "Excesso sobre T_c: quanto o fim do bloco passa de T_c. Não acumula entre blocos se a entrada <= T_c.",
    "Atraso total = t_coleta + fim do bloco: da primeira amostra do bloco até a última inversão pronta.",
    "  Não inclui a equalização. Cada PRB só precisa da sua inversão, então muitos PRBs ficam prontos antes.",
]
for k, txt in enumerate(notas, start=ult_a + 2):
    a[f"A{k}"] = txt; a[f"A{k}"].font = F
larg = [10, 20, 14, 13, 9, 11, 11, 8, 10, 10, 9, 10, 9, 10, 9, 10]
for j, w in enumerate(larg, start=1):
    a.column_dimensions[get_column_letter(j)].width = w
a.freeze_panes = "E4"
for j in range(1, len(cab) + 1):
    a.cell(row=3, column=j).border = BORDA

wb.move_sheet("Atraso", offset=-2)
wb.active = 0
wb.calculation.fullCalcOnLoad = True
wb.save(SAIDA)
print(f"{len(linhas)} linhas em {os.path.relpath(SAIDA, AQUI)}")
