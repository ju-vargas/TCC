#!/usr/bin/env bash
# Varredura [4] v3: os formatos juntos (I e F ao mesmo tempo), em vez de I e F separados.
# Para cada cenário, os formatos da configuração mais exigente (6 e 8) na primeira coluna
# sem × e na primeira coluna com perda zero da [4] v2, com 1 e 4 iterações. Mesmas
# configurações (1, 6, 8, 10 e 12), 35 modos e SNRs em volta de SER = 10^-2 da [4] v2; a
# referência float é a mesma (copiada da v2: mesma grade e mesmas sementes). Espera a
# síntese de sintetizar_formatos.py terminar, para não disputar os núcleos. Pode ser
# rodado de novo: as rodadas que já têm JSON são puladas.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
V2="$AQUI/resultados/4_varredura_formatos/v2_casos_extremos"
SAIDA="${1:-$AQUI/resultados/4_varredura_formatos/v3_formatos_juntos}"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CHAVE=org.gnome.settings-daemon.plugins.power
ANTES=$(gsettings get $CHAVE sleep-inactive-battery-type)
gsettings set $CHAVE sleep-inactive-battery-type nothing
trap 'gsettings set $CHAVE sleep-inactive-battery-type "$ANTES"; echo "energia restaurada ($ANTES) $(date -Iseconds)" >> "$LOG"' EXIT
CONFIGS=a,15,16,9,10   # configurações 1, 6, 8, 10 e 12 (params.TCC_CONFIGURATION)
{
echo "inicio $(date -Iseconds)"
while pgrep -f "sintetizar_formatos.py" > /dev/null; do sleep 30; done
echo "síntese terminou; simulação começa $(date -Iseconds)"
[ -d "$SAIDA/referencias" ] || cp -r "$V2/referencias" "$SAIDA/referencias"
rodar() {  # $1 = nome, $2 = formatos I:F, $3 = condições
    systemd-inhibit --what=handle-lid-switch:sleep:idle --who="TCC varredura [4] v3" \
        --why="simulacao longa" \
        "$PY" "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 8 --snr-perto --extra-direita 2 \
        --configuracoes $CONFIGS --formatos "$2" --condicoes "$3"
    echo "$1 terminou com codigo $? em $(date -Iseconds)"
    mv "$SAIDA/parametros.json" "$SAIDA/parametros_$1.json"
}
# <24,12> <28,12> <30,14> <34,14>
rodar n_grande 12:12,12:16,14:16,14:20 TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100
# <22,10> <26,10> <32,12> <36,12>
rodar tdlb 10:12,10:16,12:20,12:24 TDLB100-400
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
