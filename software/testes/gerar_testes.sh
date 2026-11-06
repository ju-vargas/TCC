#!/usr/bin/env bash
#
# Gera os resultados das condições de teste 3GPP (TDLA30-5 ... TDLB100-400):
#
#   curvas    SER do LMMSE, do ZF e do BCD-MMSE com 1, 2, 3 e 4 iterações, para as
#             configurações 1 a 16 do texto (run_figure8.py --bcd-iterations 1,2,3,4),
#             mais as figuras por configuração (curvas_por_configuracao.py) e a
#             tabela única ser_todas.csv (tabela_ser.py)
#   matrizes  as matrizes M_c x M_c que o BCD-MMSE inverte (16 x 16 e 32 x 32),
#             em .txt (decimal exato) e .bits (64 bits IEEE 754 da parte real e da
#             imaginária), com a amostragem de hardware/testes/exportar_matrizes.py
#
# As condições mudam o número N de amostras de ruído e a portadora (3,5 GHz em FR1,
# 28 GHz em FR2), conforme params.M1_Driver.test_conditions. Condições com o mesmo
# par (N, portadora) dão os mesmos resultados, então cada par roda uma vez:
#
#   N = 192, 3,5 GHz   TDLA30-5, TDLA30-10
#   N = 192, 28 GHz    TDLA30-75
#   N = 168, 28 GHz    TDLA30-300
#   N = 132, 3,5 GHz   TDLC300-100
#   N = 24,  3,5 GHz   TDLB100-400
#
# N vem do DM-RS duplo, no pior símbolo de dados do slot (Tabela tab:n-condicao do
# texto). HST tem N = 0 nesse caso e fica de fora. O caso médio (--caso media) existe
# para consulta, mas não corresponde a um receptor real: nenhum símbolo tem esse N.
#
# Uso:
#   ./gerar_testes.sh [opções]
#
#   --curvas        só as curvas
#   --matrizes      só as matrizes
#   -c CONDICOES    condições, ex. "TDLA30-5,TDLB100-400" (padrão: all)
#   --caso CASOS    pior, media ou pior,media (padrão: pior)
#   -p PAINEIS      configurações das curvas: a,b,c,e,f,g (1 a 6), 7 a 16, "extra"
#                   (7 a 16) ou "all" (1 a 16) (padrão: all)
#   -s NOME         subpasta das curvas dentro da pasta de resultados (padrão: curvas)
#   -r DIR          pasta das curvas (padrão: resultados/<data-hora>/)
#   --rapido        teste rápido: poucas realizações (curvas com --quick, matrizes
#                   com 3 realizações) e saída em resultados/<data-hora>_rapido/
#   -h              esta ajuda
#
# Saídas:
#   curvas    <pasta>/curvas/<condições>_N<N>_<portadora>GHz/ (bcd_iterations.png/.pdf,
#             _data.csv e _results.json), <pasta>/por_configuracao/configuracao_<k>.*,
#             <pasta>/ser_todas.csv e curvas.log
#   matrizes  hardware/testes/2_amostra_matrizes/amostras<N>_fc<portadora>GHz/<n>x<n>/
#             (no modo --rapido, dentro da pasta de resultados) e matrizes.log
#
# Para rodar a inversão do hardware em um par: hardware/testes/rodar_inversoes.sh
# -m ../../hardware/testes/2_amostra_matrizes/amostras24_fc3.5GHz (CHOL_N igual ao tamanho).

set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIMULADOR="$AQUI/../simulador"
HW_TESTES="$AQUI/../../hardware/testes"
PY="$SIMULADOR/.venv/bin/python"

CURVAS=1
MATRIZES=1
CONDICOES="all"
CASO="pior"
PAINEIS="all"
SUB="curvas"
SAIDA=""
RAPIDO=0

ajuda() { sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }
falha() { echo "ERRO: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
    case "$1" in
        --curvas) MATRIZES=0; shift ;;
        --matrizes) CURVAS=0; shift ;;
        -c) CONDICOES="$2"; shift 2 ;;
        --caso) CASO="$2"; shift 2 ;;
        -p) PAINEIS="$2"; shift 2 ;;
        -s) SUB="$2"; shift 2 ;;
        -r) SAIDA="$2"; shift 2 ;;
        --rapido) RAPIDO=1; shift ;;
        -h|--help) ajuda; exit 0 ;;
        *) falha "opção desconhecida: $1 (use -h)" ;;
    esac
done

[ -x "$PY" ] || falha "não achei o Python do simulador em $PY"

if [ -z "$SAIDA" ]; then
    SAIDA="$AQUI/resultados/$(date +%Y%m%d-%H%M%S)"
    [ "$RAPIDO" -eq 1 ] && SAIDA="${SAIDA}_rapido"
fi
mkdir -p "$SAIDA"
SAIDA="$(cd "$SAIDA" && pwd)"

{
    echo "data: $(date -Iseconds)"
    echo "commit: $(git -C "$SIMULADOR" rev-parse HEAD 2>/dev/null || echo '?')"
    git -C "$SIMULADOR" status --short -- . "$HW_TESTES" 2>/dev/null \
        | sed 's/^/alterado: /' || true
    echo "condicoes: $CONDICOES  caso: $CASO  paineis: $PAINEIS  subpasta: $SUB  rapido: $RAPIDO"
    echo
} >> "$SAIDA/execucao.txt"

if [ "$CURVAS" -eq 1 ]; then
    echo "== curvas -> $SAIDA/$SUB/"
    extra=()
    [ "$RAPIDO" -eq 1 ] && extra+=(--quick)
    n_case="${CASO//pior/worst}"; n_case="${n_case//media/mean}"
    "$PY" "$SIMULADOR/run_figure8.py" --conditions "$CONDICOES" --n-case "$n_case" \
        --panels "$PAINEIS" --bcd-iterations 1,2,3,4 --figdir "$SAIDA/$SUB" "${extra[@]}" \
        2>&1 | tee "$SAIDA/$SUB.log"
    "$PY" "$AQUI/curvas_por_configuracao.py" "$SAIDA"
    "$PY" "$AQUI/tabela_ser.py" "$SAIDA"
fi

if [ "$MATRIZES" -eq 1 ]; then
    if [ "$RAPIDO" -eq 1 ]; then
        destino="$SAIDA/matrizes"
        extra=(--n-realizacoes 3)
    else
        destino="$HW_TESTES/2_amostra_matrizes"
        extra=()
    fi
    echo "== matrizes -> $destino/"
    (cd "$HW_TESTES" && "$PY" exportar_matrizes.py --amostra --condicoes "$CONDICOES" \
        --casos "$CASO" \
        -o "$destino" "${extra[@]}") 2>&1 | tee "$SAIDA/matrizes.log"
fi

echo "pronto: $SAIDA"
