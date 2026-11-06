#!/usr/bin/env bash
# Fila da noite de 2026-10-30, depois da do Vivado: espera o fila_vivado.sh
# acabar, roda ele de novo (pega pastas acrescentadas no fim; as com FEITO sao
# puladas) e depois mede a potencia (potencia_versoes.py, so TDLA30-5) de cada
# pasta de fila_vivado.txt com vivado/FEITO e sem potencia/potencia.csv, uma de
# cada vez, nos nucleos 6 e 7. Uma por vez para nao faltar memoria. Log em
# fila_potencia.log.
cd "$(dirname "$0")"
while pgrep -f "fila_vivado.sh" > /dev/null; do sleep 60; done
./fila_vivado.sh
while read -r d; do
  [ -z "$d" ] && continue
  [ -f "$d/vivado/FEITO" ] || continue
  [ -f "$d/potencia/potencia.csv" ] && continue
  echo "$(date -Iseconds) inicio $d" >> fila_potencia.log
  mkdir -p "$d/potencia"
  if python3 potencia_versoes.py "$d" --cenarios TDLA30-5 --nucleos 6-7 < /dev/null > "$d/potencia/rodada.log" 2>&1; then
    echo "$(date -Iseconds) ok $d" >> fila_potencia.log
  else
    echo "$(date -Iseconds) FALHOU $d (ver $d/potencia/rodada.log)" >> fila_potencia.log
  fi
done < fila_vivado.txt
echo "$(date -Iseconds) fila vazia" >> fila_potencia.log
