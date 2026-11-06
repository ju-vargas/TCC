#!/usr/bin/env bash
# Sintese C (sem Vivado) de cholesky_inverse com os fontes desta pasta,
# <24,12> AP_RND_ZERO/AP_WRAP, 16 x 16, 100 MHz: o mesmo formato da referencia
# sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/. Presa aos nucleos 4 a 7.
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
rm -rf w
taskset -c 4-7 v++ -c --mode hls --config hls.cfg --work_dir w > log.txt 2>&1
echo "fim com codigo $?"
