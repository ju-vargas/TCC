#!/usr/bin/env bash
# Fila da noite de 2026-10-30: roda vivado/rodar.sh de cada pasta listada em
# fila_vivado.txt, uma de cada vez, nos nucleos 6 e 7. Pula as que ja tem
# vivado/FEITO ou vivado/FALHOU. Le a lista de novo a cada passo, entao pastas
# acrescentadas depois tambem entram. Log em fila_vivado.log.
cd "$(dirname "$0")"
while true; do
  proxima=""
  while read -r d; do
    [ -z "$d" ] && continue
    if [ ! -f "$d/vivado/FEITO" ] && [ ! -f "$d/vivado/FALHOU" ]; then proxima="$d"; break; fi
  done < fila_vivado.txt
  [ -z "$proxima" ] && break
  echo "$(date -Iseconds) inicio $proxima" >> fila_vivado.log
  if "$proxima/vivado/rodar.sh" > "$proxima/vivado/log.txt" 2>&1; then
    echo "$(date -Iseconds) ok $proxima" >> fila_vivado.log
  else
    date -Iseconds > "$proxima/vivado/FALHOU"
    echo "$(date -Iseconds) FALHOU $proxima (ver $proxima/vivado/log.txt)" >> fila_vivado.log
  fi
done
echo "$(date -Iseconds) fila vazia" >> fila_vivado.log
