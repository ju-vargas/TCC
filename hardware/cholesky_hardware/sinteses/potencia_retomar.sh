#!/usr/bin/env bash
# Retoma a cadeia de potencia_modo_fixo.sh depois da queda da sessão em 2026-10-30 00:16:
# o netlist do 24-12_32x32 já estava pronto, então roda só a potência dele; depois o
# 28-14_32x32 inteiro. Núcleos 0 a 3.
cd "$(dirname "$0")"
LOG=potencia_modo_fixo.log
echo "retomada $(date -Iseconds)" >> $LOG
echo "24-12_32x32 potencia $(date -Iseconds)" >> $LOG
( cd 24-12_32x32_RND_ZERO_WRAP_vivado/potencia && source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1 \
  && taskset -c 0-3 python3 rodar_potencia.py > rodada.log 2>&1 )
echo "24-12_32x32 terminou com codigo $? em $(date -Iseconds)" >> $LOG
p=28-14_32x32
echo "$p inicio $(date -Iseconds)" >> $LOG
taskset -c 0-3 ./${p}_RND_ZERO_WRAP_vivado/tudo_potencia.sh >> $LOG 2>&1
echo "$p terminou com codigo $? em $(date -Iseconds)" >> $LOG
echo "fim $(date -Iseconds)" >> $LOG
