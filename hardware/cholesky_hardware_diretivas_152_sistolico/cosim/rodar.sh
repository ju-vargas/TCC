#!/usr/bin/env bash
# Sintese C + co-simulacao RTL (xsim) de cholesky_inverse com os fontes desta
# pasta, <24,12> AP_RND_ZERO/AP_WRAP, 16 x 16, 100 MHz. O testbench e o
# tb_potencia.cpp, com as mesmas 20 matrizes do TDLA30-5 da referencia
# (lista_TDLA30-5.txt, copia de sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/potencia/).
# Presa aos nucleos 4 e 5.
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
rm -rf w
echo "inicio $(date -Iseconds)"
taskset -c 4-5 v++ -c --mode hls --config hls.cfg --work_dir w > log_sintese.txt 2>&1 \
  && taskset -c 4-5 vitis-run --mode hls --cosim --config hls.cfg --work_dir w > log_cosim.txt 2>&1
echo "fim com codigo $? em $(date -Iseconds)"
