#!/usr/bin/env bash
# Conferencia bit a bit (comparar_com_original.py) das arquiteturas otimizadas nos formatos que
# ainda nao tinham sido conferidos: <26,12> RND_ZERO/WRAP e <30,14> TRN/SAT, 16 x 16 e 32 x 32.
# Grava <pasta>/conferencia_<I>_<F>_<quant>_<estouro>.txt; o montar_pacote_formatos.py so poe
# essas versoes no pacote se a ultima linha disser "0 diferentes ou com erro".
# 2026-11-03: <18,8> RND_ZERO/WRAP e TRN/SAT e <20,8> RND_ZERO/WRAP, com
#   FORMATOS="8:10 AP_RND_ZERO:AP_WRAP;8:10 AP_TRN:AP_SAT;8:12 AP_RND_ZERO:AP_WRAP"
# Uso (em hardware/): [FORMATOS="I:F Q:O;..."] ./conferir_formatos_novos.sh [nucleos, padrao 4-5]
NUCLEOS="${1:-4-5}"
FORMATOS="${FORMATOS:-12:14 AP_RND_ZERO:AP_WRAP;14:16 AP_TRN:AP_SAT}"
PY=../../software/simulador/.venv/bin/python
for d in cholesky_hardware_diretivas cholesky_hardware_diretivas_4545 cholesky_hardware_diretivas_606 \
         cholesky_hardware_diretivas_455 cholesky_hardware_diretivas_152_sistolico \
         cholesky_hardware_diretivas_114_sistolico; do
  IFS=';' read -ra LISTA <<< "$FORMATOS"
  for fm in "${LISTA[@]}"; do
    set -- $fm
    saida="conferencia_${1/:/_}_${2/:/_}.txt"
    echo "$(date -Iseconds) $d $1 $2"
    (cd "$d" && taskset -c "$NUCLEOS" $PY comparar_com_original.py --formatos "$1" --modo "$2" \
       --por-tamanho 1000 -j 2 > "$saida" 2>&1)
    tail -1 "$d/$saida"
  done
done
