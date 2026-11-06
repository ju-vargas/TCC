#!/usr/bin/env bash
#
# Roda a inversão por Cholesky no hardware (C-simulation do Vitis) e no modelo
# golden_cholesky.py, com entrada .bits, para todas as combinações de
# quantização (7 modos) e estouro (5 modos), e compara as saídas bit a bit.
#
# Para cada combinação e cada tamanho de matriz (pasta 2_amostra_matrizes/<par>/<n>x<n>/):
#   1. gera um hls_config.cfg próprio (nunca edita o do componente), com os
#      mesmos -D em syn.cflags e tb.cflags e CHOL_N igual ao tamanho da pasta;
#   2. roda vitis-run --csim, que compila e executa o testbench na primeira
#      matriz (csim.argv);
#   3. confere que os -D chegaram ao hardware e ao testbench (csim.mk) e que os
#      tipos impressos pelo testbench são os mesmos do golden_cholesky.py;
#   4. roda as outras matrizes no mesmo csim.exe que o Vitis compilou, como o
#      run_sim.tcl do Vitis faz (com --vitis-por-matriz, cada matriz passa por
#      um vitis-run, o que é muito mais lento);
#   5. roda o golden_cholesky.py em cada matriz e compara os .bits das 8 etapas
#      com cmp.
#
# A quantização e o estouro da combinação valem para os dados (CHOL_QUANT e
# CHOL_OVERFLOW); acumulador e intermediários seguem esses modos, a não ser que
# o parametros.env defina modos próprios para eles. A raiz é sempre AP_TRN e
# AP_WRAP (o hls::sqrt só aceita esses).
#
# Status de cada matriz (resumo.csv):
#   igual          as 8 etapas com os mesmos bits
#   diferente      alguma etapa difere
#   ambos_div0     hardware e modelo dividem por zero (pivô <= 0): concordam
#   so_hw_falhou   só o hardware falhou       \  divergência
#   so_py_falhou   só o modelo falhou         /
#   erro           erro de leitura ou de execução (ver os logs da matriz)
#
# Uso:
#   ./rodar_inversoes.sh [opções]
#
#   -e ARQ        parametros.env (padrão: o desta pasta)
#   -m DIR        pasta das matrizes, com as pastas <n>x<n> dentro; as exportadas
#                 ficam por par (N, portadora), ex. 2_amostra_matrizes/amostras24_fc3.5GHz
#   -t TAMANHOS   pastas de tamanho, ex. "16x16" (padrão: todas)
#   -q MODOS      modos de quantização, ex. "AP_TRN AP_RND_CONV" (padrão: os 7)
#   -o MODOS      modos de estouro, ex. "AP_SAT AP_WRAP" (padrão: os 5)
#   -s PADRAO     só as matrizes cujo nome casa com o padrão, ex. "painel_a_*"
#   -n N          no máximo N matrizes por tamanho (para testes rápidos)
#   -j N          processos em paralelo para as matrizes (padrão: núcleos)
#   -r DIR        pasta de resultados (padrão: 3_validacao_bits/<data-hora>_<par>/)
#   --manter      guarda saídas e logs de todas as matrizes (padrão: nas iguais
#                 não fica nada; nas ambos_div0 ficam os logs; nas outras, tudo)
#   --vitis-por-matriz  roda cada matriz por um vitis-run
#   -h            esta ajuda

set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARDWARE="$(dirname "$AQUI")"
GOLDEN="$HARDWARE/golden_cholesky.py"
VITIS_SETTINGS="${VITIS_SETTINGS:-$HOME/2026.1/Vitis/settings64.sh}"

ENV_FILE="$AQUI/parametros.env"
MATRIZES="$AQUI/2_amostra_matrizes"
TAMANHOS=""
QUANTS="AP_TRN AP_TRN_ZERO AP_RND AP_RND_ZERO AP_RND_MIN_INF AP_RND_INF AP_RND_CONV"
OVERFLOWS="AP_SAT AP_SAT_ZERO AP_SAT_SYM AP_WRAP AP_WRAP_SM"
PADRAO="*"
LIMITE=0
JOBS="$(nproc)"
RESULTADOS=""
MANTER=0
VITIS_POR_MATRIZ=0

ETAPAS="00_A 01_L 02_U 03_D 05_S 06_G 07_G_inv 08_inverse"

ajuda() { sed -n '2,/^set -uo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }
falha() { echo "ERRO: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
    case "$1" in
        -e) ENV_FILE="$2"; shift 2 ;;
        -m) MATRIZES="$2"; shift 2 ;;
        -t) TAMANHOS="$2"; shift 2 ;;
        -q) QUANTS="$2"; shift 2 ;;
        -o) OVERFLOWS="$2"; shift 2 ;;
        -s) PADRAO="$2"; shift 2 ;;
        -n) LIMITE="$2"; shift 2 ;;
        -j) JOBS="$2"; shift 2 ;;
        -r) RESULTADOS="$2"; shift 2 ;;
        --manter) MANTER=1; shift ;;
        --vitis-por-matriz) VITIS_POR_MATRIZ=1; shift ;;
        -h|--help) ajuda; exit 0 ;;
        *) falha "opção desconhecida: $1 (use -h)" ;;
    esac
done

# O Vitis roda em outra pasta, então a pasta das matrizes precisa ser absoluta
[ -d "$MATRIZES" ] || falha "não existe a pasta de matrizes $MATRIZES"
MATRIZES="$(cd "$MATRIZES" && pwd)"

# Cada vitis-run por matriz usa a mesma pasta de trabalho do Vitis da combinação
[ "$VITIS_POR_MATRIZ" -eq 1 ] && JOBS=1

[ -f "$ENV_FILE" ] || falha "não achei $ENV_FILE"
[ -f "$GOLDEN" ] || falha "não achei $GOLDEN"
[ -f "$VITIS_SETTINGS" ] || falha "não achei $VITIS_SETTINGS (defina VITIS_SETTINGS)"
# O settings64.sh do Vitis usa variáveis não definidas, que o set -u trataria como erro
set +u
# shellcheck disable=SC1090
source "$VITIS_SETTINGS" > /dev/null 2>&1
set -u
command -v vitis-run > /dev/null || falha "vitis-run não está no PATH depois do settings64.sh"

# ---------------------------------------------------------------------------
# Parâmetros do .env
# ---------------------------------------------------------------------------

declare -A ENV=()
while IFS= read -r linha || [ -n "$linha" ]; do
    linha="${linha%$'\r'}"
    [[ "$linha" =~ ^[[:space:]]*(#|$) ]] && continue
    [[ "$linha" == *=* ]] || continue
    nome="${linha%%=*}"; valor="${linha#*=}"
    ENV["${nome//[[:space:]]/}"]="${valor//[[:space:]]/}"
done < "$ENV_FILE"

case "${ENV[VERSAO]:-completa}" in
    completa) COMPONENTE="$HARDWARE/cholesky_hardware" ;;
    apfixed)  COMPONENTE="$HARDWARE/cholesky_hardware_apfixed" ;;
    *) [ -d "$HARDWARE/${ENV[VERSAO]}" ] \
           || falha "VERSAO=${ENV[VERSAO]} no .env; use completa, apfixed ou o nome de uma pasta de componente em $HARDWARE"
       COMPONENTE="$HARDWARE/${ENV[VERSAO]}" ;;
esac

INTERMEDIARIOS="MULIN PROD CMUL NUM NORM QUOT SUM SQRT"
for nome in "${!ENV[@]}"; do
    [ -n "${ENV[$nome]}" ] || continue
    for inter in $INTERMEDIARIOS; do
        if [[ "$nome" == CHOL_${inter}_* && "${ENV[VERSAO]:-completa}" == apfixed ]]; then
            falha "$nome definido no .env, mas a versão apfixed não tem intermediários"
        fi
    done
    if [[ "$nome" =~ ^CHOL_.+_(QUANT|OVERFLOW)$ ]]; then
        echo "ATENCAO: $nome=${ENV[$nome]} no .env não segue a combinação testada" >&2
    fi
done

# -D do hardware e opções do golden_cholesky.py, a partir das CHOL_* com valor,
# menos CHOL_N (vem da pasta) e CHOL_QUANT/CHOL_OVERFLOW (vêm da combinação).
# CHOL_QUOT_FRAC_BITS -> -DCHOL_QUOT_FRAC_BITS=v e --quot-frac-bits v
DFLAGS_BASE=""
PYARGS_BASE=""
for nome in $(printf '%s\n' "${!ENV[@]}" | sort); do
    valor="${ENV[$nome]}"
    [[ "$nome" == CHOL_* && -n "$valor" ]] || continue
    case "$nome" in CHOL_N|CHOL_QUANT|CHOL_OVERFLOW) continue ;; esac
    DFLAGS_BASE+=" -D$nome=$valor"
    opcao="${nome#CHOL_}"; opcao="${opcao,,}"; opcao="${opcao//_/-}"
    PYARGS_BASE+=" --$opcao $valor"
done

# ---------------------------------------------------------------------------
# Matrizes
# ---------------------------------------------------------------------------

if [ -z "$TAMANHOS" ]; then
    TAMANHOS="$(cd "$MATRIZES" && ls -d [0-9]*x[0-9]* 2>/dev/null | tr '\n' ' ')"
fi
if [ -z "$TAMANHOS" ]; then
    pares="$(cd "$MATRIZES" && ls -d amostras*_fc* 2>/dev/null | tr '\n' ' ')"
    [ -n "$pares" ] && falha "nenhuma pasta <n>x<n> em $MATRIZES; as matrizes estão por par (N, portadora): use -m $MATRIZES/<par>, com <par> em: $pares"
    falha "nenhuma pasta <n>x<n> em $MATRIZES"
fi

declare -A LISTA=()
for tam in $TAMANHOS; do
    [ -d "$MATRIZES/$tam" ] || falha "não existe $MATRIZES/$tam"
    mapfile -t arquivos < <(cd "$MATRIZES/$tam" && ls $PADRAO.bits 2>/dev/null | sort)
    [ "${#arquivos[@]}" -gt 0 ] || falha "nenhuma matriz .bits em $MATRIZES/$tam casa com '$PADRAO'"
    if [ "$LIMITE" -gt 0 ] && [ "${#arquivos[@]}" -gt "$LIMITE" ]; then
        arquivos=("${arquivos[@]:0:$LIMITE}")
    fi
    LISTA[$tam]="${arquivos[*]}"
done

# O par (N, portadora) entra no nome da pasta, quando -m aponta para um deles
PAR="$(basename "$MATRIZES")"
case "$PAR" in amostras*_fc*) PAR="_$PAR" ;; *) PAR="" ;; esac
RESULTADOS="${RESULTADOS:-$AQUI/3_validacao_bits/$(date +%Y%m%d-%H%M%S)$PAR}"
[ -e "$RESULTADOS" ] && falha "$RESULTADOS já existe; use outra pasta (-r)"
mkdir -p "$RESULTADOS"
cp "$ENV_FILE" "$RESULTADOS/parametros.env"
echo "combinacao,quant,overflow,tamanho,matriz,status,etapas_diferentes,primeira_diferenca" \
    > "$RESULTADOS/resumo.csv"

n_comb=$(( $(wc -w <<< "$QUANTS") * $(wc -w <<< "$OVERFLOWS") ))
echo "Componente: $COMPONENTE"
echo "Combinações: $n_comb; tamanhos: $TAMANHOS"
for tam in $TAMANHOS; do echo "  $tam: $(wc -w <<< "${LISTA[$tam]}") matrizes"; done
echo "Resultados em $RESULTADOS"

# ---------------------------------------------------------------------------
# Uma matriz: hardware (csim.exe ou vitis-run), modelo e comparação
# ---------------------------------------------------------------------------

# Configuração do Vitis para uma combinação: arquivos com caminho absoluto e os
# mesmos -D no hardware e no testbench
escrever_cfg() {   # cfg dflags [argv]
    local cfg="$1" dflags="$2" argv="${3:-}" f
    {
        grep -m1 '^part=' "$COMPONENTE/hls_config.cfg"
        echo
        echo "[hls]"
        echo "syn.top=cholesky_decomposition"
        echo "syn.cflags=-I$COMPONENTE$dflags"
        echo "tb.cflags=-I$COMPONENTE$dflags"
        [ -n "$argv" ] && echo "csim.argv=$argv"
        for f in $(grep '^syn.file=' "$COMPONENTE/hls_config.cfg" | cut -d= -f2); do
            echo "syn.file=$COMPONENTE/$f"
        done
        for f in $(grep '^tb.file=' "$COMPONENTE/hls_config.cfg" | cut -d= -f2); do
            echo "tb.file=$COMPONENTE/$f"
        done
    } > "$cfg"
}

rodar_matriz() {   # dir_combinacao tamanho arquivo.bits
    local dc="$1" tam="$2" arq="$3"
    local nome="${arq%.bits}" entrada="$MATRIZES/$tam/$arq"
    local d="$dc/$tam/matrizes/$nome"
    mkdir -p "$d"

    # Hardware (a primeira matriz já foi rodada pelo vitis-run na compilação)
    if [ ! -f "$d/hw.rc" ]; then
        if [ "$VITIS_POR_MATRIZ" -eq 1 ]; then
            escrever_cfg "$d/hls_config.cfg" "$(cat "$dc/$tam/dflags")" "$entrada $d/hw"
            (cd "$d" && vitis-run --mode hls --csim --config "$d/hls_config.cfg" \
                --work_dir "$dc/$tam/vitis" > "$d/hw.log" 2>&1)
            if grep -q "CSim done with 0 errors" "$d/hw.log"; then echo 0; else echo 1; fi > "$d/hw.rc"
        else
            # Subshell: sem core dump e sem a mensagem do bash quando o
            # hardware divide por zero (o código de saída continua em hw.rc).
            # Sem exec: o aviso da falha precisa sair do subshell, cujo stderr
            # vai para /dev/null, e não do shell de fora
            (
                ulimit -c 0
                LD_LIBRARY_PATH="$(cat "$dc/$tam/ld_library_path")" \
                    "$dc/$tam/csim.exe" "$entrada" "$d/hw" > "$d/hw.log" 2>&1
            ) 2> /dev/null
            echo $? > "$d/hw.rc"
        fi
    fi

    # Modelo
    # shellcheck disable=SC2086
    python3 "$GOLDEN" "$entrada" -o "$d/py" $(cat "$dc/$tam/pyargs") > "$d/py.log" 2>&1
    local py_rc=$? hw_ok=1 py_ok=1 e difs=0 primeira=""
    for e in $ETAPAS; do
        [ -f "$d/hw/hw_$e.bits" ] || hw_ok=0
        [ -f "$d/py/golden_$e.bits" ] || py_ok=0
    done

    local status
    if [ "$hw_ok" -eq 1 ] && [ "$py_ok" -eq 1 ]; then
        for e in $ETAPAS; do
            if ! cmp -s "$d/hw/hw_$e.bits" "$d/py/golden_$e.bits"; then
                difs=$((difs + 1)); [ -z "$primeira" ] && primeira="$e"
            fi
        done
        if [ "$difs" -eq 0 ]; then status=igual; else status=diferente; fi
    elif grep -q "nao corresponde\|Nao foi possivel\|nao tem a forma\|Erro ao ler" "$d/hw.log" \
         || { [ "$py_rc" -ne 0 ] && [ "$py_rc" -ne 2 ]; }; then
        status=erro
    elif [ "$hw_ok" -eq 0 ] && [ "$py_rc" -eq 2 ]; then
        status=ambos_div0
    elif [ "$hw_ok" -eq 0 ]; then
        status=so_hw_falhou
    else
        status=so_py_falhou
    fi

    echo "$(basename "$dc"),${dc##*/q_},${tam},${nome},${status},${difs},${primeira}" \
        | awk -F, -v OFS=, '{split($2, m, "__o_"); print $1, m[1], m[2], $3, $4, $5, $6, $7}' \
        > "$d/linha.csv"

    # O testbench imprime todas as matrizes no log (~45 KB por execução), então
    # nas matrizes iguais ficam só hw.rc e linha.csv
    if [ "$MANTER" -eq 0 ]; then
        case "$status" in
            igual) rm -rf "$d/hw" "$d/py" "$d/hw.log" "$d/py.log" ;;
            ambos_div0) rm -rf "$d/hw" "$d/py" ;;
        esac
    fi
}
export -f rodar_matriz escrever_cfg
export MATRIZES GOLDEN ETAPAS MANTER VITIS_POR_MATRIZ COMPONENTE

# ---------------------------------------------------------------------------
# Laço das combinações
# ---------------------------------------------------------------------------

i=0
for q in $QUANTS; do
    for o in $OVERFLOWS; do
        i=$((i + 1))
        dc="$RESULTADOS/q_${q}__o_${o}"
        for tam in $TAMANHOS; do
            n="${tam%%x*}"
            dt="$dc/$tam"
            mkdir -p "$dt/matrizes"
            dflags="$DFLAGS_BASE -DCHOL_N=$n -DCHOL_QUANT=$q -DCHOL_OVERFLOW=$o"
            echo "$dflags" > "$dt/dflags"
            echo "$PYARGS_BASE --quant $q --overflow $o" > "$dt/pyargs"

            read -r -a arquivos <<< "${LISTA[$tam]}"
            primeira="${arquivos[0]%.bits}"
            mkdir -p "$dt/matrizes/$primeira"

            # Compilação e primeira matriz pelo Vitis, em work_dir novo
            printf '[%2d/%d] %-14s %-11s %s: compilando no Vitis... ' "$i" "$n_comb" "$q" "$o" "$tam"
            escrever_cfg "$dt/hls_config.cfg" "$dflags" \
                "$MATRIZES/$tam/${arquivos[0]} $dt/matrizes/$primeira/hw"
            (cd "$dt" && vitis-run --mode hls --csim --config "$dt/hls_config.cfg" \
                --work_dir "$dt/vitis" > "$dt/vitis.log" 2>&1)
            build="$dt/vitis/hls/csim/build"
            if [ ! -x "$build/csim.exe" ]; then
                echo "FALHOU (ver $dt/vitis.log)"
                echo "$(basename "$dc"),$q,$o,$tam,,erro_compilacao,," >> "$RESULTADOS/resumo.csv"
                continue
            fi
            cp "$dt/vitis.log" "$dt/matrizes/$primeira/hw.log"
            if grep -q "CSim done with 0 errors" "$dt/vitis.log"; then echo 0; else echo 1; fi \
                > "$dt/matrizes/$primeira/hw.rc"
            cp "$build/csim.exe" "$dt/csim.exe"

            # Os -D precisam estar na regra do testbench e nas do hardware
            regras_tb=$(grep -c -- "-DCHOL_QUANT=$q -DCHOL_OVERFLOW=$o" "$build/csim.mk")
            regras_hw=$(grep -- "-DCHOL_QUANT=$q -DCHOL_OVERFLOW=$o" "$build/csim.mk" | grep -c -- "-fhls-csim")
            if [ "$regras_hw" -lt 1 ] || [ "$regras_tb" -le "$regras_hw" ]; then
                echo "FALHOU (os -D não chegaram ao hardware e ao testbench; ver $build/csim.mk)"
                echo "$(basename "$dc"),$q,$o,$tam,,erro_flags,," >> "$RESULTADOS/resumo.csv"
                continue
            fi

            # Tipos do testbench (Vitis) == tipos do golden_cholesky.py
            grep '^TIPO ' "$dt/vitis.log" | sort -u > "$dt/tipos_hw.txt"
            # shellcheck disable=SC2046
            python3 "$GOLDEN" "$MATRIZES/$tam/${arquivos[0]}" -o "$dt/tipos_py_saida" \
                $(cat "$dt/pyargs") 2>/dev/null | grep '^TIPO ' \
                | grep -F -f <(awk '{print "TIPO " $2 " "}' "$dt/tipos_hw.txt") \
                | sort -u > "$dt/tipos_py.txt"
            rm -rf "$dt/tipos_py_saida"
            if [ ! -s "$dt/tipos_hw.txt" ] || ! diff -q "$dt/tipos_hw.txt" "$dt/tipos_py.txt" > /dev/null; then
                echo "FALHOU (tipos diferentes entre testbench e modelo; ver $dt/tipos_*.txt)"
                echo "$(basename "$dc"),$q,$o,$tam,,erro_tipos,," >> "$RESULTADOS/resumo.csv"
                continue
            fi

            # Mesmo LD_LIBRARY_PATH que o run_sim.tcl do Vitis monta: cada
            # "set" põe um caminho na frente (por isso tac) e o último acrescenta
            # lnx64/csim no fim
            caminhos="$(sed -n 's/^set ::env(LD_LIBRARY_PATH) \([^:$]*\):.*/\1/p' \
                "$build/run_sim.tcl" | tac | paste -sd:)"
            echo "$caminhos${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}:$XILINX_VITIS/lnx64/csim" \
                > "$dt/ld_library_path"

            printf 'rodando %d matrizes... ' "${#arquivos[@]}"
            printf '%s\n' "${arquivos[@]}" \
                | xargs -P "$JOBS" -I{} bash -c 'rodar_matriz "$1" "$2" "$3"' _ "$dc" "$tam" {}

            cat "$dt"/matrizes/*/linha.csv >> "$RESULTADOS/resumo.csv"
            awk -F, -v t="$tam" '$4 == t {c[$6]++} END {for (s in c) printf "%s %d  ", s, c[s]; print ""}' \
                <(cat "$dt"/matrizes/*/linha.csv)
            # Do trabalho do Vitis só ficam o csim.mk (com os -D usados) e o
            # vitis.log; o binário copiado é apagado junto
            cp "$build/csim.mk" "$dt/csim.mk"
            rm -rf "$dt/vitis" "$dt/csim.exe"
        done
    done
done

# ---------------------------------------------------------------------------
# Resumo
# ---------------------------------------------------------------------------

STATUS="igual diferente ambos_div0 so_hw_falhou so_py_falhou erro erro_compilacao erro_flags erro_tipos"
{
    echo "Resumo por combinação (matrizes por status)"
    echo
    printf '%-15s %-12s %-6s' quant overflow tam
    for st in $STATUS; do printf ' %15s' "$st"; done
    echo
    awk -F, 'NR > 1 {print $2, $3, $4}' "$RESULTADOS/resumo.csv" | sort -u \
        | while read -r q o t; do
            printf '%-15s %-12s %-6s' "$q" "$o" "$t"
            for st in $STATUS; do
                printf ' %15d' "$(awk -F, -v q="$q" -v o="$o" -v t="$t" -v s="$st" \
                    'NR > 1 && $2 == q && $3 == o && $4 == t && $6 == s' \
                    "$RESULTADOS/resumo.csv" | wc -l)"
            done
            echo
        done
    echo
    divergencias=$(awk -F, 'NR > 1 && $6 != "igual" && $6 != "ambos_div0"' "$RESULTADOS/resumo.csv" | wc -l)
    total=$(($(wc -l < "$RESULTADOS/resumo.csv") - 1))
    echo "Total: $total (matriz, combinação); fora de igual e ambos_div0: $divergencias"
} | tee "$RESULTADOS/resumo.txt"
