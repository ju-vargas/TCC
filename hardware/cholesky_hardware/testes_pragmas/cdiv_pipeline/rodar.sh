#!/usr/bin/env bash
# Sintese C (sem Vivado) da cdiv sequencial e com pipeline, <24,12> RND_ZERO/WRAP.
# Presa aos nucleos 4 a 7.
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh >/dev/null 2>&1
for v in seq pipe; do
  (cd $v && taskset -c 4-7 v++ -c --mode hls --config hls.cfg --work_dir w > log.txt 2>&1; echo "$v fim codigo $?") &
done
wait
