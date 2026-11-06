#!/usr/bin/env bash
# Varredura [4] v4: os formatos juntos (I e F ao mesmo tempo) das combinações escolhidas em
# restricoes_varredura_4.csv da [4] v2, nas 16 configurações, nos 5 cenários e nos 35 modos.
# Primeiro as sínteses HLS (35 modos), em 16 x 16 (sinteses/modos_16x16) e em 32 x 32
# (sinteses/modos_32x32): o G_c tem 32 x 32 nas configurações 9 a 12 (M = 256, C = 8) e
# 16 x 16 nas outras. Depois a simulação, mesmas SNRs em volta de SER = 10^-2 da v2 e da v3,
# em três etapas, para que cada grupo de configurações saia inteiro: 1 a 8, 13 a 16, 9 a 12.
# As rodadas da v3 dos mesmos formatos (<24,12>, <28,12>, <30,14>; configurações 1, 6, 8, 10
# e 12; 4 cenários) e as referências float são copiadas, e não rodadas de novo. Pode ser
# rodado de novo: as sínteses com csynth.xml e as rodadas com JSON são puladas.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
V3="$AQUI/resultados/4_varredura_formatos/v3_formatos_juntos"
SAIDA="${1:-$AQUI/resultados/4_varredura_formatos/v4_formatos_juntos_16_configs}"
HW="$AQUI/../../hardware/cholesky_hardware"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CHAVE=org.gnome.settings-daemon.plugins.power
ANTES=$(gsettings get $CHAVE sleep-inactive-battery-type)
gsettings set $CHAVE sleep-inactive-battery-type nothing
trap 'gsettings set $CHAVE sleep-inactive-battery-type "$ANTES"; echo "energia restaurada ($ANTES) $(date -Iseconds)" >> "$LOG"' EXIT
# <14,6> <16,6> <18,8> <20,8> <22,12> <24,12> <26,12> <28,12> <28,14> <30,14>
FORMATOS="6:8 6:10 8:10 8:12 12:10 12:12 12:14 12:16 14:14 14:16"
CONDICOES=TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
INIBIR=(systemd-inhibit --what=handle-lid-switch:sleep:idle --who="TCC varredura [4] v4" --why="rodada longa")
{
echo "inicio $(date -Iseconds)"
for n in 16 32; do
    "${INIBIR[@]}" "$PY" -u "$HW/sintetizar_formatos.py" --n $n --modos todos --paralelo 4 $FORMATOS
    echo "síntese ${n}x${n} terminou com codigo $? em $(date -Iseconds)"
done
[ -d "$SAIDA/referencias" ] || cp -r "$V3/referencias" "$SAIDA/referencias"
for f in 12_12 12_16 14_16; do
    (cd "$V3" && find dados -name "${f}_AP_*.json" -exec cp -n --parents {} "$SAIDA/" \;)
done
echo "copiadas $(find "$SAIDA/dados" -name '*.json' | wc -l) rodadas da v3"
rodar() {  # $1 = nome, $2 = rótulos das configurações (params.TCC_CONFIGURATION)
    "${INIBIR[@]}" "$PY" "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 8 --snr-perto \
        --extra-direita 2 --configuracoes "$2" --formatos "${FORMATOS// /,}" --condicoes $CONDICOES
    echo "$1 terminou com codigo $? em $(date -Iseconds)"
    mv "$SAIDA/parametros.json" "$SAIDA/parametros_$1.json"
}
rodar configs_1_a_8 a,f,e,7,g,15,14,16
rodar configs_13_a_16 c,12,11,13
rodar configs_9_a_12 b,9,8,10
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
