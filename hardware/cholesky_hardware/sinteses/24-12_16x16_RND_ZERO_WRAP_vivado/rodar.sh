#!/usr/bin/env bash
# Síntese HLS + Vivado (síntese RTL e implementação) de <24,12> AP_RND_ZERO/AP_WRAP, 16 x 16.
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
echo "inicio $(date -Iseconds)"
v++ -c --mode hls --config hls.cfg --work_dir w && echo "csynth ok $(date -Iseconds)" \
  && vitis-run --mode hls --impl --config hls.cfg --work_dir w
echo "fim com codigo $? em $(date -Iseconds)"
