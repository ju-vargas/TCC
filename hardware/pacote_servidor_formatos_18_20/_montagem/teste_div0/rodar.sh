#!/usr/bin/env bash
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
taskset -c 4-5 v++ -c --mode hls --config cosim.cfg --work_dir w > sintese.log 2>&1 || { echo FALHOU sintese; exit 1; }
diff -r w/hls/syn/verilog ../18-8_sem_otimizacao/w/hls/syn/verilog > diff_rtl.txt && echo "RTL igual" || echo "RTL DIFERENTE"
taskset -c 4-5 vitis-run --mode hls --cosim --config cosim.cfg --work_dir w > cosim.log 2>&1 || { echo FALHOU cosim; exit 1; }
t=w/hls/sim/tv; n=0; d=0
for c in $t/cdatafile/c.cholesky_inverse.autotvout_inverse*.dat; do r=$t/rtldatafile/rtl.${c##*/c.}; n=$((n+1)); cmp -s $c $r || d=$((d+1)); done
echo "arquivos $n, diferentes $d"; grep -E "POTENCIA|PASS|FAIL" cosim.log
