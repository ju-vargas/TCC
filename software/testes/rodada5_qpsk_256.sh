#!/usr/bin/env bash
# [5] para as configurações 17 a 24 (QPSK com M = 256): os formatos escolhidos dos grupos 2 e
# 3 na grade inteira de SNR, de -20 a 10 dB, com a mesma semente da referência
# curvas_qpsk_256 (como a [5] das 16 configurações usa a grade e a semente da [1]). Para as
# curvas de SER do TCC. Depois, retoma a verificação v6 (verificacao_ate_10db.py).
# Com 2 processos e prioridade mínima, para não atrapalhar o uso da máquina.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../simulador/.venv/bin/python"
SAIDA="$AQUI/resultados/5_candidatos/modo_fixo_3dB_qpsk_256"
mkdir -p "$SAIDA"
LOG="$SAIDA/log.txt"
CONDICOES=TDLA30-5,TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400
{
echo "inicio $(date -Iseconds)"
rodar() {  # $1 = nome, $2 = modo, $3 = formatos
    nice -n 19 ionice -c3 "$PY" -u "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 2 --snr-min -20 \
        --configuracoes 17,18,19,20,21,22,23,24 --formatos "$3" --modos "$2" \
        --condicoes $CONDICOES
    echo "$1 terminou com codigo $? em $(date -Iseconds)"
    mv "$SAIDA/parametros.json" "$SAIDA/parametros_$1.json"
}
# <24,12> e <28,14> em RND_ZERO/WRAP; <30,14> em TRN/SAT (Tabela tab:formatos-escolhidos)
rodar rnd_zero_wrap AP_RND_ZERO:AP_WRAP 12:12,14:14
rodar trn_sat AP_TRN:AP_SAT 14:16
touch "$SAIDA/FIM"
echo "fim $(date -Iseconds)"
} >> "$LOG" 2>&1
V6="$AQUI/resultados/4_varredura_formatos/v6_verificacao_ate_10dB"
nice -n 19 ionice -c3 "$PY" -u "$AQUI/verificacao_ate_10db.py" -j 2 >> "$V6/log.txt" 2>&1
