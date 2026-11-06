#!/usr/bin/env bash
# Conferencia bit a bit dos 3 formatos novos e depois a montagem do pacote (nucleos 4-5).
cd "$(dirname "$0")/.."
FORMATOS="8:10 AP_RND_ZERO:AP_WRAP;8:10 AP_TRN:AP_SAT;8:12 AP_RND_ZERO:AP_WRAP" \
  ./conferir_formatos_novos.sh 4-5 > pacote_servidor_formatos_18_20/conferencia.log 2>&1
python3 montar_pacote_formatos.py --pacote pacote_servidor_formatos_18_20 \
  --formatos 18-8,18-8-TRN-SAT,20-8 --nucleos 4,5 > pacote_servidor_formatos_18_20/montagem.log 2>&1
echo FIM >> pacote_servidor_formatos_18_20/montagem.log
