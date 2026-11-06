#!/usr/bin/env bash
# Sintese HLS + Vivado (sintese RTL e implementacao) desta versao, como em
# ../../cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/rodar.sh.
# <24,12> AP_RND_ZERO/AP_WRAP, 16 x 16, 100 MHz. Presa aos nucleos 6 e 7.
# Apaga so a pasta de trabalho (w) e a marca (FEITO) desta pasta vivado/.
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
rm -rf w FEITO
echo "inicio $(date -Iseconds)"
taskset -c 6-7 v++ -c --mode hls --config hls.cfg --work_dir w && echo "csynth ok $(date -Iseconds)" \
  && taskset -c 6-7 vitis-run --mode hls --impl --config hls.cfg --work_dir w
r=$?
echo "fim com codigo $r em $(date -Iseconds)"
[ $r -eq 0 ] && date -Iseconds > FEITO
exit $r
