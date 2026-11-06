#!/usr/bin/env bash
# Varredura [4] com os casos extremos escolhidos pelo G_c no ponto de operação
# (configurações 1, 6, 8, 10 e 12, nos 5 pares (N, portadora)), só nas SNRs em
# volta do cruzamento com SER = 10^-2 (--snr-perto). Impede a suspensão enquanto roda e
# devolve a configuração de energia ao final. Pode ser rodado de novo: as rodadas que já
# têm JSON são puladas.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
SAIDA="${1:-$AQUI/resultados/4_varredura_formatos/v2_casos_extremos}"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CHAVE=org.gnome.settings-daemon.plugins.power
ANTES=$(gsettings get $CHAVE sleep-inactive-battery-type)
gsettings set $CHAVE sleep-inactive-battery-type nothing
trap 'gsettings set $CHAVE sleep-inactive-battery-type "$ANTES"; echo "energia restaurada ($ANTES) $(date -Iseconds)" >> "$LOG"' EXIT
{
echo "inicio $(date -Iseconds)"
# Rótulos: a = configuração 1, 15 = 6, 16 = 8, 9 = 10, 10 = 12 (params.TCC_CONFIGURATION)
systemd-inhibit --what=handle-lid-switch:sleep:idle --who="TCC varredura [4]" --why="simulacao longa" \
    "$PY" "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 8 --snr-perto --extra-direita 2 \
    --configuracoes a,15,16,9,10 --condicoes TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
echo "varredura terminou com codigo $? em $(date -Iseconds)"
"$PY" "$AQUI/figuras_formatos.py" "$SAIDA"
"$PY" "$AQUI/figuras_formatos.py" "$SAIDA" --mapas
for it in 4; do "$PY" "$AQUI/figuras_formatos.py" "$SAIDA" --mapas --iteracao $it; done
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
