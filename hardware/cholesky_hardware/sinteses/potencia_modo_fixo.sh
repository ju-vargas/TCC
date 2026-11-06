#!/usr/bin/env bash
# Espera as sínteses do modo fixo (rodar.sh de cada pasta) e roda a potência com 20 matrizes por
# cenário, uma pasta por vez, presa aos núcleos 0 a 3 (no máximo 4 núcleos).
cd "$(dirname "$0")"
PASTAS="22-12_16x16 22-12_32x32 24-12_32x32 28-14_32x32"
LOG=potencia_modo_fixo.log
for p in $PASTAS; do
    until grep -q "fim com codigo" ${p}_RND_ZERO_WRAP_vivado/log.txt 2>/dev/null; do sleep 300; done
done
for p in $PASTAS; do
    echo "$p inicio $(date -Iseconds)" >> $LOG
    systemd-inhibit --what=handle-lid-switch:sleep:idle --who=TCC-potencia --why=testbench \
        taskset -c 0-3 ./${p}_RND_ZERO_WRAP_vivado/tudo_potencia.sh >> $LOG 2>&1
    echo "$p terminou com codigo $? em $(date -Iseconds)" >> $LOG
done
echo "fim $(date -Iseconds)" >> $LOG
