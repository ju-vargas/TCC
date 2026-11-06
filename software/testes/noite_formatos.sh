#!/usr/bin/env bash
# Noite de 2026-10-15: espera a conferência nativo x Vitis (35 modos) terminar e, se
# tudo for igual, roda a varredura de formatos sem deixar o computador suspender.
set -uo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HW="$AQUI/../../hardware/testes"
PY="$AQUI/../simulador/.venv/bin/python"
SAIDA="$AQUI/resultados/4_varredura_formatos/v1_configs_1_11_12"
mkdir -p "$SAIDA"
LOG="$SAIDA/noite.log"
{
echo "inicio $(date -Iseconds)"
while pgrep -f "python conferir_nativo.py" > /dev/null || pgrep -f "/python conferir_nativo.py" > /dev/null; do sleep 30; done
cp "$HW/3_validacao_bits/conferir_nativo.log" "$SAIDA/conferir_nativo.log"
CSV="$HW/3_validacao_bits/conferir_nativo.csv"
total=$(( $(wc -l < "$CSV") - 1 ))
iguais=$(grep -c ",igual," "$CSV")
echo "conferencia nativo x Vitis: $iguais iguais de $total"
if [ "$total" -ne 140 ] || [ "$iguais" -ne "$total" ]; then
    echo "PAROU: o servidor nativo nao deu os mesmos bits do Vitis em todos os casos (ver conferir_nativo.log)"
    echo "fim $(date -Iseconds)"; touch "$SAIDA/FIM"; exit 1
fi
# Os servidores da conferência foram compilados com a versão anterior do testbench
# (sem a saída rápida na divisão por zero); a varredura recompila todos
rm -rf "$AQUI/../../hardware/cholesky_hardware_servidor/build"
echo "varredura $(date -Iseconds)"
systemd-inhibit --what=sleep:idle --who="TCC varredura de formatos" --why="simulacao longa" \
    "$PY" "$AQUI/varredura_formatos.py" -o "$SAIDA" -j 8
echo "varredura terminou com codigo $? em $(date -Iseconds)"
touch "$SAIDA/FIM"
} >> "$LOG" 2>&1
