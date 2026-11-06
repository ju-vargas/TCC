#!/usr/bin/env bash
# Roda o Vivado e a potencia das versoes do pacote no servidor (Vivado 2023.2). Ver LEIAME.md.
#
# Uso: [JOBS=4] [NUCLEOS=0-7] ./rodar.sh <versao...|todas> [-- etapas]
#   versao: nome de uma pasta em versoes/ (ex.: 24-12_9090), ou todas (na ordem do fila.txt)
#   etapas: vivado e potencia, nesta ordem (padrao: as duas)
#     vivado    sintese RTL e implementacao (vivado.tcl), 100 MHz
#     potencia  simulacao da netlist com SAIF e report_power nos cenarios da versao (potencia.py)
#   JOBS: quantas versoes rodam ao mesmo tempo (padrao 4). Cada Vivado usa ate 8 threads e,
#     na 114 em <24,12>, 16 GB de memoria.
# Antes: module load vivado/2023.2-enterprise (ou o settings64.sh do Vivado no PATH).
# Cada etapa que termina bem grava versoes/<versao>/trabalho/<etapa>/FEITO e e pulada
# na proxima chamada. Para refazer, apague esse FEITO.
#   ex.: module load vivado/2023.2-enterprise; nohup ./rodar.sh todas > /dev/null 2>&1 &

set -uo pipefail
PACOTE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ $# -ge 1 ] || { sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
for f in vivado xelab xsim python3; do
  command -v $f > /dev/null || { echo "nao achei $f no PATH (module load vivado/2023.2-enterprise?)"; exit 1; }
done
NUCLEOS="${NUCLEOS:-}"
JOBS="${JOBS:-4}"
TASKSET=""; [ -n "$NUCLEOS" ] && TASKSET="taskset -c $NUCLEOS"

VERSOES=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do VERSOES+=("$1"); shift; done
[ "${1:-}" = "--" ] && shift
ETAPAS="${*:-vivado potencia}"
[ "${VERSOES[0]}" = todas ] && mapfile -t VERSOES < "$PACOTE/fila.txt"

etapa_vivado() {
  local v="$1" d="$PACOTE/versoes/$1/trabalho/vivado"
  rm -rf "$d"; mkdir -p "$d"
  (cd "$d" && $TASKSET vivado -mode batch -nojournal -log log.txt -source "$PACOTE/vivado.tcl" \
     -tclargs "$PACOTE/versoes/$v/rtl" "$d" > /dev/null 2>&1) || return 1
  python3 "$PACOTE/resumo_vivado.py" "$d" > "$d/resumo.txt"
}

etapa_potencia() {
  local v="$1"
  mkdir -p "$PACOTE/versoes/$v/trabalho/potencia"
  python3 "$PACOTE/potencia.py" "$v" --nucleos "$NUCLEOS" \
    < /dev/null > "$PACOTE/versoes/$v/trabalho/potencia/log.txt" 2>&1
}

# Uma versao: as etapas em ordem; para na primeira que falha
rodar_versao() {
  local v="$1" e marca
  [ -d "$PACOTE/versoes/$v" ] || { echo "versao desconhecida: $v"; return 1; }
  for e in $ETAPAS; do
    marca="$PACOTE/versoes/$v/trabalho/$e/FEITO"
    if [ -f "$marca" ]; then echo "$v $e: ja feito ($(cat "$marca"))"; continue; fi
    echo "$(date -Iseconds) $v $e: inicio" | tee -a "$PACOTE/rodar.log"
    if "etapa_$e" "$v"; then
      date -Iseconds > "$marca"
      echo "$(date -Iseconds) $v $e: ok" | tee -a "$PACOTE/rodar.log"
    else
      echo "$(date -Iseconds) $v $e: FALHOU (ver versoes/$v/trabalho/$e/)" | tee -a "$PACOTE/rodar.log"
      return 1
    fi
  done
}

if [ "${RODAR_UMA:-}" = 1 ]; then rodar_versao "${VERSOES[0]}"; exit; fi
# Cada versao num processo proprio, JOBS de cada vez (as pastas de trabalho sao separadas)
printf '%s\n' "${VERSOES[@]}" | RODAR_UMA=1 xargs -P "$JOBS" -I{} "$0" {} -- $ETAPAS
