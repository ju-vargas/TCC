#!/usr/bin/env bash
# Formatos escolhidos só com IoTh de 10 dB (Tabela tab:formatos-escolhidos, configurações A
# a D) que faltavam na grade inteira de SNR: <18,8> no grupo 1 (configurações 1 a 8, grade
# -10 a 10 dB, semente da [1]) e <22,12> no QPSK dos grupos 2 e 3 (17 a 24, grade -20 a
# 10 dB, semente da curvas_qpsk_256). Espera a rodada5_qpsk_256.sh terminar, para a
# verificação v6 que ela religa e a religa no fim. 2 processos, prioridade mínima.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
QPSK="$AQUI/resultados/5_candidatos/modo_fixo_3dB_qpsk_256"
SAIDA="$AQUI/resultados/5_candidatos/modo_fixo_3dB_iot10"
V6="$AQUI/resultados/4_varredura_formatos/v6_verificacao_ate_10dB"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CONDICOES=TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
while [ ! -f "$QPSK/FIM" ]; do sleep 60; done
sleep 20
pkill -TERM -f "verificacao_ate_10db.py" && \
    echo "interrompida $(date -Iseconds) para a rodada5_iot10.sh; retomada no fim dela" >> "$V6/log.txt"
{
echo "inicio $(date -Iseconds)"
nice -n 19 ionice -c3 "$PY" -u "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 2 \
    --configuracoes a,f,e,7,g,15,14,16 --formatos 8:10 --modos AP_RND_ZERO:AP_WRAP \
    --condicoes $CONDICOES
echo "18_8 terminou com codigo $? em $(date -Iseconds)"
nice -n 19 ionice -c3 "$PY" -u "$AQUI/varredura_formatos.py" -o "$QPSK" -j 2 --snr-min -20 \
    --configuracoes 17,18,19,20,21,22,23,24 --formatos 12:10 --modos AP_RND_ZERO:AP_WRAP \
    --condicoes $CONDICOES
echo "22_12 qpsk terminou com codigo $? em $(date -Iseconds)"
mv "$QPSK/parametros.json" "$QPSK/parametros_rnd_zero_wrap_22_12.json"
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
nice -n 19 ionice -c3 "$PY" -u "$AQUI/verificacao_ate_10db.py" -j 2 >> "$V6/log.txt" 2>&1
