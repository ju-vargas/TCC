#!/usr/bin/env bash
# Sintese C (estimativa do HLS) da 152 e da 114 em <30,14> TRN/SAT, para ver se cabem na XCU50.
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh > /dev/null 2>&1
(cd 152_sistolico && taskset -c 4 v++ -c --mode hls --config hls.cfg --work_dir w > log.txt 2>&1; echo "152 fim $?") &
(cd 114_sistolico && taskset -c 5 v++ -c --mode hls --config hls.cfg --work_dir w > log.txt 2>&1; echo "114 fim $?") &
wait
