#!/usr/bin/env bash
# Potência do <22,12> AP_RND_ZERO/AP_WRAP 32 x 32 com matrizes G_c reais (20 por cenário), depois
# da síntese e implementação (rodar.sh), no mesmo fluxo do 28-14_16x16_RND_ZERO_WRAP_vivado.
set -e
cd "$(dirname "$0")"
grep -q "fim com codigo 0" log.txt
cd potencia
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
echo "netlist $(date -Iseconds)"
vivado -mode batch -nojournal -nolog -source netlist.tcl > netlist.log 2>&1
python3 limpar_netlist.py netlist_bruta.v netlist_roteada.v
echo "potencia $(date -Iseconds)"
python3 rodar_potencia.py > rodada.log 2>&1
echo "fim $(date -Iseconds)"
