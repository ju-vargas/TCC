#!/usr/bin/env bash
# Depois da potencia do TDLA30-5: espera a rodada das 4 versoes acabar (a linha
# da 455 em fila_potencia.log) e mede os outros 4 cenarios, uma versao de cada
# vez, nos nucleos 6 e 7. O potencia.csv de cada versao guarda os cenarios ja
# medidos. Log em fila_potencia.log.
cd "$(dirname "$0")"
until grep -qE "(ok|FALHOU) cholesky_hardware_diretivas_455$" fila_potencia.log; do sleep 60; done
for d in cholesky_hardware_diretivas cholesky_hardware_diretivas_4545 cholesky_hardware_diretivas_606 cholesky_hardware_diretivas_455; do
  echo "$(date -Iseconds) inicio $d (4 cenarios)" >> fila_potencia.log
  if python3 potencia_versoes.py "$d" --cenarios TDLA30-75,TDLA30-300,TDLC300-100,TDLB100-400 \
       --nucleos 6-7 < /dev/null > "$d/potencia/rodada_cenarios.log" 2>&1; then
    echo "$(date -Iseconds) ok $d (4 cenarios)" >> fila_potencia.log
  else
    echo "$(date -Iseconds) FALHOU $d (4 cenarios)" >> fila_potencia.log
  fi
done
echo "$(date -Iseconds) fila dos cenarios vazia" >> fila_potencia.log
