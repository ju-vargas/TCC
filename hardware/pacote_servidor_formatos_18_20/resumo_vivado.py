#!/usr/bin/env python3
"""Resumo da etapa vivado: recursos depois do roteamento (utilizacao.rpt) e caminho crítico
(timing.rpt). BRAM sai em blocos de 36 kb (Block RAM Tile) e em BRAM_18K (o dobro), que é a
unidade dos resumos do HLS. Uso: python3 resumo_vivado.py <pasta da etapa vivado>"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
u = (d / "utilizacao.rpt").read_text()
num = lambda rotulo: float(re.search(rf"^\| {re.escape(rotulo)}\s*\|\s*([0-9.]+)", u, re.M).group(1))
t = (d / "timing.rpt").read_text()
wns = float(re.search(r"WNS\(ns\).*\n.*\n\s*(-?[0-9.]+)", t).group(1))
bram = num("Block RAM Tile")
print(f"LUT: {num('CLB LUTs'):.0f}")
print(f"FF: {num('CLB Registers'):.0f}")
print(f"DSP: {num('DSPs'):.0f}")
print(f"BRAM: {bram:g} blocos de 36 kb ({2 * bram:g} BRAM_18K)")
print(f"URAM: {num('URAM'):.0f}")
print(f"WNS: {wns:.3f} ns; caminho critico {10 - wns:.3f} ns; "
      + ("Timing met" if wns >= 0 else "Timing not met"))
