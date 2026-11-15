#!/usr/bin/env bash
# [5] completa para o mapa de aumento de SNR e os perfis de mobilidade: os 10 formatos do
# mapa, cada um no modo fixo do seu grupo (mapa_cenarios_v4.modo_fixo, escolhido na [4]
# v4/v5), nas 24 configurações e 5 condições, na grade inteira de SNR e com a mesma semente
# das barras e das curvas de SER (16-QAM: -10 a 10 dB; QPSK: -20 a 10 dB). Só as 640 rodadas
# que ainda não existem em modo_fixo_3dB, _iot10, _qpsk_128 e _qpsk_256; nada é sobrescrito.
# Assim o mapa, os perfis, as barras e as curvas usam os mesmos arquivos.
# Com 2 processos e prioridade mínima, para não atrapalhar o uso da máquina.
# Retomável: as rodadas com JSON são puladas.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
SAIDA="$AQUI/resultados/5_candidatos/modo_fixo_mapa"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CONDICOES=TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
{
echo "inicio $(date -Iseconds)"
rodar() {  # $1 = nome, $2 = modo, $3 = formato, $4 = configurações, $5 = SNR mínima (- = -10)
    local grade=()
    [ "$5" != "-" ] && grade=(--snr-min "$5")
    nice -n 19 ionice -c3 "$PY" -u "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 2 "${grade[@]}" \
        --configuracoes "$4" --formatos "$3" --modos "$2" --condicoes $CONDICOES
    echo "$1 terminou com codigo $? em $(date -Iseconds)"
    mv "$SAIDA/parametros.json" "$SAIDA/parametros_$1.json"
}
# Formatos perto dos limites primeiro; <14,6> e <16,6> (quase só x na grade curta) no fim
rodar g1_16qam_8_12_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:12 a,f,e,7 -
rodar g1_16qam_12_16_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:16 a,f,e,7 -
rodar g1_qpsk_8_12_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:12 g,15,14,16 -20
rodar g1_qpsk_12_14_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:14 g,15,14,16 -20
rodar g1_qpsk_12_16_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:16 g,15,14,16 -20
rodar g1_qpsk_14_16_AP_TRN_AP_SAT AP_TRN:AP_SAT 14:16 g,15,14,16 -20
rodar g2_16qam_8_10_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:10 b,9,8,10 -
rodar g2_16qam_8_12_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:12 b,9,8,10 -
rodar g2_16qam_12_16_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:16 b,9,8,10 -
rodar g2_qpsk_8_10_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:10 17,18,19,20 -20
rodar g2_qpsk_8_12_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:12 17,18,19,20 -20
rodar g2_qpsk_12_14_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:14 17,18,19,20 -20
rodar g2_qpsk_12_16_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:16 17,18,19,20 -20
rodar g3_16qam_8_12_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:12 c,12,11,13 -
rodar g3_16qam_12_16_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:16 c,12,11,13 -
rodar g3_16qam_8_10_AP_TRN_AP_SAT AP_TRN:AP_SAT 8:10 c,12,11,13 -
rodar g3_qpsk_8_12_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 8:12 21,22,23,24 -20
rodar g3_qpsk_12_14_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:14 21,22,23,24 -20
rodar g3_qpsk_12_16_AP_RND_ZERO_AP_WRAP AP_RND_ZERO:AP_WRAP 12:16 21,22,23,24 -20
rodar g3_qpsk_8_10_AP_TRN_AP_SAT AP_TRN:AP_SAT 8:10 21,22,23,24 -20
rodar g1_16qam_6_8_AP_RND_MIN_INF_AP_SAT AP_RND_MIN_INF:AP_SAT 6:8 a,f,e,7 -
rodar g1_16qam_6_10_AP_TRN_AP_SAT AP_TRN:AP_SAT 6:10 a,f,e,7 -
rodar g1_qpsk_6_8_AP_RND_MIN_INF_AP_SAT AP_RND_MIN_INF:AP_SAT 6:8 g,15,14,16 -20
rodar g1_qpsk_6_10_AP_TRN_AP_SAT AP_TRN:AP_SAT 6:10 g,15,14,16 -20
rodar g2_16qam_6_8_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:8 b,9,8,10 -
rodar g2_16qam_6_10_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:10 b,9,8,10 -
rodar g2_qpsk_6_8_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:8 17,18,19,20 -20
rodar g2_qpsk_6_10_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:10 17,18,19,20 -20
rodar g3_16qam_6_8_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:8 c,12,11,13 -
rodar g3_16qam_6_10_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:10 c,12,11,13 -
rodar g3_qpsk_6_8_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:8 21,22,23,24 -20
rodar g3_qpsk_6_10_AP_RND_MIN_INF_AP_WRAP AP_RND_MIN_INF:AP_WRAP 6:10 21,22,23,24 -20
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
