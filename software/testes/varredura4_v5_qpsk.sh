#!/usr/bin/env bash
# Varredura [4] v5: os mesmos 10 formatos, 35 modos e 5 cenários da v4, nas configurações
# 17 a 24 (QPSK com M = 256, params.QPSK_256_PANELS), para que os grupos 2 (M = 256, C = 8)
# e 3 (M = 256, C = 16) tenham QPSK como o grupo 1. As SNRs em volta de SER = 10^-2 vêm da
# referência float numa grade a partir de -20 dB (referencia_qpsk_256.py, rodada antes, em
# resultados/1_referencia_float/curvas_qpsk_256). As sínteses HLS são as da v4 (não mudam
# com a modulação). Em duas etapas, para que cada grupo saia inteiro: 21 a 24 (16 x 16) e
# 17 a 20 (32 x 32). Pode ser rodado de novo: as rodadas com JSON são puladas.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
SAIDA="${1:-$AQUI/resultados/4_varredura_formatos/v5_qpsk_grupos_2_3}"
REF="$AQUI/resultados/1_referencia_float/curvas_qpsk_256"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CHAVE=org.gnome.settings-daemon.plugins.power
ANTES=$(gsettings get $CHAVE sleep-inactive-battery-type)
gsettings set $CHAVE sleep-inactive-battery-type nothing
trap 'gsettings set $CHAVE sleep-inactive-battery-type "$ANTES"; echo "energia restaurada ($ANTES) $(date -Iseconds)" >> "$LOG"' EXIT
# <14,6> <16,6> <18,8> <20,8> <22,12> <24,12> <26,12> <28,12> <28,14> <30,14>
FORMATOS="6:8 6:10 8:10 8:12 12:10 12:12 12:14 12:16 14:14 14:16"
CONDICOES=TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
INIBIR=(systemd-inhibit --what=handle-lid-switch:sleep:idle --who="TCC varredura [4] v5" --why="rodada longa")
{
echo "inicio $(date -Iseconds)"
[ -f "$REF/TDLB100-400_N24_3.5GHz/bcd_iterations_results.json" ] || \
    "$PY" -u "$AQUI/referencia_qpsk_256.py" -j 8
rodar() {  # $1 = nome, $2 = rótulos das configurações (params.TCC_CONFIGURATION)
    "${INIBIR[@]}" "$PY" "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 8 --snr-perto \
        --extra-direita 2 --referencia "$REF" --configuracoes "$2" \
        --formatos "${FORMATOS// /,}" --condicoes $CONDICOES
    echo "$1 terminou com codigo $? em $(date -Iseconds)"
    mv "$SAIDA/parametros.json" "$SAIDA/parametros_$1.json"
}
rodar configs_21_a_24 21,22,23,24
rodar configs_17_a_20 17,18,19,20
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
