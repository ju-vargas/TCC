#!/usr/bin/env bash
# Sintese C (estimativa do HLS) das 6 arquiteturas otimizadas em 32 x 32, <24,12> RND_ZERO/WRAP,
# para ver os ciclos e se cabem na XCU50. Fontes das pastas das versoes, so o CHOL_N trocado.
# Duas de cada vez, nos nucleos 4 a 7 (a maquina tem 15 GB).
cd "$(dirname "$0")"
source /home/juliana/2026.1/Vitis/settings64.sh > /dev/null 2>&1
uma() {
  (cd "$1" && taskset -c 4-7 v++ -c --mode hls --config hls.cfg --work_dir w > log.txt 2>&1)
  echo "$(date -Iseconds) $1 fim $?" >> andamento.txt
}
export -f uma
printf '%s\n' 9090 4545 606 455 152_sistolico 114_sistolico | xargs -P 2 -I{} bash -c 'uma {}'
echo "$(date -Iseconds) todas" >> andamento.txt
