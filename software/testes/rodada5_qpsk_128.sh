#!/usr/bin/env bash
# QPSK do grupo 1 (configurações 5 a 8 = 1C, 1G, 1D, 1H) a partir de -20 dB, como o QPSK dos
# grupos 2 e 3: na grade -10 a 10 da [1], o LMMSE já está abaixo de 10^-2 em -10 dB e a parte
# da descentralização é só um limite inferior. Referência float (curvas_qpsk_128) e os
# formatos escolhidos do grupo 1 (<18,8>, <22,12>, <24,12>, <28,14>, RND_ZERO/WRAP) na grade
# -20 a 10 dB, mesma semente. Espera a rodada5_iot10.sh, para a v6 e a religa no fim.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
ANTES="$AQUI/resultados/5_candidatos/modo_fixo_3dB_iot10"
REF="$AQUI/resultados/1_referencia_float/curvas_qpsk_128"
SAIDA="$AQUI/resultados/5_candidatos/modo_fixo_3dB_qpsk_128"
V6="$AQUI/resultados/4_varredura_formatos/v6_verificacao_ate_10dB"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
while [ ! -f "$ANTES/FIM" ]; do sleep 60; done
sleep 20
pkill -TERM -f "verificacao_ate_10db.py" && \
    echo "interrompida $(date -Iseconds) para a rodada5_qpsk_128.sh; retomada no fim dela" >> "$V6/log.txt"
{
echo "inicio $(date -Iseconds)"
nice -n 19 ionice -c3 "$PY" -u "$AQUI/referencia_qpsk_256.py" -j 2 --min -20 \
    --configuracoes g,15,14,16 --saida "$REF"
echo "referencia terminou com codigo $? em $(date -Iseconds)"
nice -n 19 ionice -c3 "$PY" -u "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 2 --snr-min -20 \
    --configuracoes g,15,14,16 --formatos 8:10,12:10,12:12,14:14 --modos AP_RND_ZERO:AP_WRAP \
    --condicoes TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
echo "formatos terminou com codigo $? em $(date -Iseconds)"
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
nice -n 19 ionice -c3 "$PY" -u "$AQUI/verificacao_ate_10db.py" -j 2 >> "$V6/log.txt" 2>&1
