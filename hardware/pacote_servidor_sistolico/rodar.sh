#!/usr/bin/env bash
# Roda os testes das versoes sistolicas (152 e 114) em outra maquina. Ver LEIAME.md.
#
# Uso: VITIS_SETTINGS=<caminho do settings64.sh> [NUCLEOS=0-7] ./rodar.sh <versao> [etapas]
#   versao: 152_sistolico, 114_sistolico ou todas
#   etapas: cosim, vivado e potencia, nesta ordem (padrao: as tres)
#     cosim     sintese C + co-simulacao com as 20 matrizes do TDLA30-5, e confere que a
#               saida do RTL e igual a do C byte a byte
#     vivado    sintese C + sintese RTL e implementacao no Vivado (100 MHz)
#     potencia  potencia nos 5 cenarios (potencia.py), com a netlist roteada do Vivado
# Cada etapa que termina bem grava versoes/<versao>/trabalho/<etapa>/FEITO e e pulada
# na proxima chamada. Para refazer, apague esse FEITO.
#   ex.: VITIS_SETTINGS=/opt/Xilinx/2026.1/Vitis/settings64.sh ./rodar.sh todas

set -uo pipefail
PACOTE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ $# -ge 1 ] || { sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
: "${VITIS_SETTINGS:?defina VITIS_SETTINGS com o caminho do settings64.sh do Vitis}"
[ -f "$VITIS_SETTINGS" ] || { echo "nao achei $VITIS_SETTINGS"; exit 1; }
NUCLEOS="${NUCLEOS:-}"
TASKSET=""; [ -n "$NUCLEOS" ] && TASKSET="taskset -c $NUCLEOS"
# O settings64.sh usa variaveis que podem nao existir, entao sem o -u aqui
set +u; source "$VITIS_SETTINGS" >/dev/null 2>&1; set -u

VERSOES="$1"; shift
[ "$VERSOES" = todas ] && VERSOES="152_sistolico 114_sistolico"
ETAPAS="${*:-cosim vivado potencia}"

# Mesmo formato e mesmas opcoes das sinteses de referencia: <24,12> RND_ZERO/WRAP, 16 x 16
CFLAGS="-DCHOL_N=16 -DCHOL_INT_BITS=12 -DCHOL_FRAC_BITS=12 -DCHOL_QUANT=AP_RND_ZERO -DCHOL_OVERFLOW=AP_WRAP"
FONTES="cholesky.h cholesky_ops.h lu_decomposition.cpp dv_step.cpp s_step.cpp g_step.cpp foward_substitution.cpp inversion.cpp cholesky_top.cpp"

# hls.cfg com os caminhos desta maquina. $1: pasta da versao; $2: linhas extras
escrever_cfg() {
  {
    echo "part=xcu50-fsvh2104-2-e"
    echo
    echo "[hls]"
    echo "flow_target=vivado"
    echo "clock=10ns"
    echo "syn.compile.pipeline_loops=0"
    echo "syn.top=cholesky_inverse"
    echo "syn.cflags=$CFLAGS"
    for f in $FONTES; do echo "syn.file=$1/$f"; done
    printf '%b' "$2"
  }
}

etapa_cosim() {
  local v="$1" d="$PACOTE/versoes/$1/trabalho/cosim"
  rm -rf "$d"; mkdir -p "$d"
  sed "s#^#$PACOTE/#" "$PACOTE/listas/lista_TDLA30-5.txt" > "$d/lista_TDLA30-5.txt"
  escrever_cfg "$PACOTE/versoes/$v" "tb.cflags=$CFLAGS\ntb.file=$PACOTE/versoes/$v/tb_potencia.cpp\ncosim.tool=xsim\ncosim.argv=$d/lista_TDLA30-5.txt\n" > "$d/hls.cfg"
  (cd "$d" && $TASKSET v++ -c --mode hls --config hls.cfg --work_dir w > log_sintese.txt 2>&1 \
     && $TASKSET vitis-run --mode hls --cosim --config hls.cfg --work_dir w > log_cosim.txt 2>&1) || return 1
  local tv="$d/w/hls/sim/tv" ok=1 n=0
  for c in "$tv"/cdatafile/c.cholesky_inverse.autotvout_inverse*.dat; do
    n=$((n + 1))
    cmp -s "$c" "$tv/rtldatafile/rtl.${c##*/c.}" || ok=0
  done
  {
    grep -E "Verilog" "$d"/w/hls/sim/report/cholesky_inverse_cosim.rpt
    grep -E "POTENCIA" "$d/log_cosim.txt" | head -1
    if [ $ok = 1 ] && [ $n -gt 0 ]; then echo "RTL == C byte a byte ($n portas)"; else echo "RTL DIFERENTE do C"; fi
  } | tee "$d/resumo.txt"
  [ $ok = 1 ] && [ $n -gt 0 ]
}

etapa_vivado() {
  local v="$1" d="$PACOTE/versoes/$1/trabalho/vivado"
  rm -rf "$d"; mkdir -p "$d"
  escrever_cfg "$PACOTE/versoes/$v" "package.output.format=ip_catalog\npackage.output.syn=false\nvivado.flow=impl\nvivado.clock=10ns\n" > "$d/hls.cfg"
  (cd "$d" && $TASKSET v++ -c --mode hls --config hls.cfg --work_dir w > log.txt 2>&1 \
     && $TASKSET vitis-run --mode hls --impl --config hls.cfg --work_dir w >> log.txt 2>&1) || return 1
  grep -E "^LUT:|^FF:|^DSP:|^BRAM:|^URAM:|CP achieved post-impl|Timing met|Timing not met" "$d/log.txt" | tail -8 | tee "$d/resumo.txt"
}

etapa_potencia() {
  local v="$1"
  mkdir -p "$PACOTE/versoes/$v/trabalho/potencia"
  python3 "$PACOTE/potencia.py" "$v" --vitis "$VITIS_SETTINGS" --nucleos "$NUCLEOS" \
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
