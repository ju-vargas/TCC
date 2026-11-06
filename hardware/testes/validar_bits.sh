#!/usr/bin/env bash
#
# Validação bit a bit da inversão: C-simulation do Vitis contra a inversão do
# simulador, nas matrizes selecionadas da amostra (2_amostra_matrizes/).
#
#   1. selecionar_matrizes.py: escolhe as matrizes de cada par (N, portadora),
#      tamanho e configuração, em 3_selecao_matrizes/;
#   2. rodar_inversoes.sh: C-simulation e golden_cholesky.py em cada par, só com a
#      quantização e o estouro do parametros.env, guardando os .bits (--manter);
#   3. inverter_no_simulador.py: inverte pelo caminho do simulador, grava
#      sim_08_inverse.bits e compara com o hardware; escreve relatorio.csv e
#      resumo.txt.
#
# Uso:
#   ./validar_bits.sh [opções]
#
#   -e ARQ      formato do hardware (padrão: parametros.env; a versão de 64 bits,
#               na cópia cholesky_hardware_64bits/, é parametros_64bits.env)
#   --manter-selecao  usa a 3_selecao_matrizes/ que já existe, sem refazer (para rodar outro
#               formato nas mesmas matrizes)
#   -r DIR      pasta da validação (padrão: 3_validacao_bits/validacao_<data-hora>_<formato>/)
#   --snr LISTA SNRs da cobertura (padrão: -10,-6,-2,2,6,10)
#   -j N        processos em paralelo (padrão: núcleos)
#   -h          esta ajuda

set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../../software/simulador/.venv/bin/python"
SAIDA=""
ENV_FILE="$AQUI/parametros.env"
MANTER_SELECAO=0
SNR="-10,-6,-2,2,6,10"
JOBS="$(nproc)"

ajuda() { sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
    case "$1" in
        -r) SAIDA="$2"; shift 2 ;;
        -e) ENV_FILE="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; shift 2 ;;
        --manter-selecao) MANTER_SELECAO=1; shift ;;
        --snr) SNR="$2"; shift 2 ;;
        -j) JOBS="$2"; shift 2 ;;
        -h|--help) ajuda; exit 0 ;;
        *) echo "opção desconhecida: $1 (use -h)" >&2; exit 1 ;;
    esac
done

W="$(( $(grep '^CHOL_INT_BITS=' "$ENV_FILE" | cut -d= -f2) + $(grep '^CHOL_FRAC_BITS=' "$ENV_FILE" | cut -d= -f2) ))"
SAIDA="${SAIDA:-$AQUI/3_validacao_bits/validacao_$(date +%Y%m%d-%H%M%S)_${W}bits}"
mkdir -p "$SAIDA"
SAIDA="$(cd "$SAIDA" && pwd)"
Q="$(grep '^CHOL_QUANT=' "$ENV_FILE" | cut -d= -f2)"
O="$(grep '^CHOL_OVERFLOW=' "$ENV_FILE" | cut -d= -f2)"
cp "$ENV_FILE" "$SAIDA/"

if [ "$MANTER_SELECAO" -eq 1 ] && [ -d "$AQUI/3_selecao_matrizes" ]; then
    echo "== seleção: usando a que já existe em $AQUI/3_selecao_matrizes/"
else
    echo "== seleção -> $AQUI/3_selecao_matrizes/"
    "$PY" "$AQUI/selecionar_matrizes.py" --snr="$SNR" | tee "$SAIDA/selecao.log"
fi

for par_dir in "$AQUI"/3_selecao_matrizes/*/; do
    par="$(basename "$par_dir")"
    echo "== C-simulation: $par ($Q, $O)"
    mkdir -p "$SAIDA/$par"
    # rodar_inversoes.sh sai com código 1 quando alguma matriz não é "igual" (os
    # ambos_div0 contam); o relatório do passo 3 separa os casos
    "$AQUI/rodar_inversoes.sh" -e "$ENV_FILE" -m "${par_dir%/}" -q "$Q" -o "$O" --manter -j "$JOBS" \
        -r "$SAIDA/$par/hls" > "$SAIDA/$par/hls.log" 2>&1 || true
    tail -4 "$SAIDA/$par/hls.log"
done

echo "== simulador"
"$PY" "$AQUI/inverter_no_simulador.py" "$SAIDA" --env "$ENV_FILE" -j "$JOBS" | tee "$SAIDA/simulador.log"
echo "pronto: $SAIDA"
