#!/usr/bin/env bash
# Síntese HLS das células (formato, modo) do mapa de perda da [4] v2, em
# hardware/cholesky_hardware/sinteses/modos_16x16/. Em cada linha do mapa (I com F = 32;
# F com I = 14), as colunas até a primeira com perda zero em tudo, inclusive; nelas, cada
# célula com perda <= 6 dB em algum caso (celulas_sintese.py). Espera a simulação da [4]
# v2 terminar, para não disputar os núcleos. Pode ser rodado de novo: as sínteses que já
# têm csynth.xml são puladas.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
V2="$AQUI/resultados/4_varredura_formatos/v2_casos_extremos"
HW="$AQUI/../../hardware/cholesky_hardware"
LOG="$HW/sinteses/modos_16x16/log_v2.txt"
CHAVE=org.gnome.settings-daemon.plugins.power
{
echo "inicio $(date -Iseconds)"
while pgrep -f "[v]arredura_formatos.py" > /dev/null || [ ! -f "$V2/FIM" ]; do sleep 30; done
echo "simulação terminou $(date -Iseconds)"
# Depois da simulação, que já devolveu a configuração de energia dela
ANTES=$(gsettings get $CHAVE sleep-inactive-battery-type)
gsettings set $CHAVE sleep-inactive-battery-type nothing
trap 'gsettings set $CHAVE sleep-inactive-battery-type "$ANTES"; echo "energia restaurada ($ANTES) $(date -Iseconds)" >> "$LOG"' EXIT
CELULAS=$(cd "$AQUI" && "$PY" celulas_sintese.py "$V2")
echo "$(echo "$CELULAS" | wc -l) células"
systemd-inhibit --what=handle-lid-switch:sleep:idle --who="TCC sintese v2" --why="sintese longa" \
    "$PY" -u "$HW/sintetizar_formatos.py" --paralelo 4 $CELULAS
echo "síntese terminou com codigo $? em $(date -Iseconds)"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
