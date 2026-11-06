#!/usr/bin/env bash
# Roda o Vivado e a potencia das versoes do pacote no servidor (Vivado 2023.2). Ver LEIAME.md.
#
# Uso: [NUCLEOS=0-7] ./rodar.sh <versao> [etapas]
#   versao: 455, 152_sistolico, 114_sistolico ou todas (nesta ordem)
#   etapas: vivado e potencia, nesta ordem (padrao: as duas)
#     vivado    sintese RTL e implementacao (vivado.tcl), 100 MHz
#     potencia  simulacao da netlist com SAIF e report_power nos 5 cenarios (potencia.py)
# Antes: module load vivado/2023.2-enterprise (ou o settings64.sh do Vivado no PATH).
# Cada etapa que termina bem grava versoes/<versao>/trabalho/<etapa>/FEITO e e pulada
# na proxima chamada. Para refazer, apague esse FEITO.
#   ex.: module load vivado/2023.2-enterprise; ./rodar.sh todas

set -uo pipefail
PACOTE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ $# -ge 1 ] || { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
for f in vivado xelab xsim python3; do
  command -v $f > /dev/null || { echo "nao achei $f no PATH (module load vivado/2023.2-enterprise?)"; exit 1; }
done
NUCLEOS="${NUCLEOS:-}"
TASKSET=""; [ -n "$NUCLEOS" ] && TASKSET="taskset -c $NUCLEOS"

VERSOES="$1"; shift
[ "$VERSOES" = todas ] && VERSOES="455 152_sistolico 114_sistolico"
ETAPAS="${*:-vivado potencia}"

etapa_vivado() {
  local v="$1" d="$PACOTE/versoes/$1/trabalho/vivado"
  rm -rf "$d"; mkdir -p "$d"
  (cd "$d" && $TASKSET vivado -mode batch -nojournal -log log.txt -source "$PACOTE/vivado.tcl" \
     -tclargs "$PACOTE/versoes/$v/rtl" "$d" > /dev/null 2>&1) || return 1
  python3 "$PACOTE/resumo_vivado.py" "$d" | tee "$d/resumo.txt"
}

etapa_potencia() {
  local v="$1"
  mkdir -p "$PACOTE/versoes/$v/trabalho/potencia"
  python3 "$PACOTE/potencia.py" "$v" --nucleos "$NUCLEOS" \
    < /dev/null 2>&1 | tee "$PACOTE/versoes/$v/trabalho/potencia/log.txt"
  return "${PIPESTATUS[0]}"
}

for v in $VERSOES; do
  [ -d "$PACOTE/versoes/$v" ] || { echo "versao desconhecida: $v"; exit 1; }
  for e in $ETAPAS; do
    marca="$PACOTE/versoes/$v/trabalho/$e/FEITO"
    if [ -f "$marca" ]; then echo "$v $e: ja feito ($(cat "$marca"))"; continue; fi
    echo "$(date -Iseconds) $v $e: inicio" | tee -a "$PACOTE/rodar.log"
    if "etapa_$e" "$v"; then
      date -Iseconds > "$marca"
      echo "$(date -Iseconds) $v $e: ok" | tee -a "$PACOTE/rodar.log"
    else
      echo "$(date -Iseconds) $v $e: FALHOU (ver versoes/$v/trabalho/$e/)" | tee -a "$PACOTE/rodar.log"
      break
    fi
  done
done
