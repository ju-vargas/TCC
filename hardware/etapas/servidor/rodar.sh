#!/usr/bin/env bash
# Utilizacao por hierarquia (LUT, FF, DSP, BRAM por etapa) dos projetos roteados do servidor.
# Nao refaz a implementacao: so abre cada roteado.dcp e roda report_utilization -hierarchical.
# uso (no servidor): module load vivado/2023.2-enterprise; cd ~/TCC/etapas_vivado
#                   setsid nohup bash rodar.sh > rodar.log 2>&1 &      (JOBS=2 por padrao)
cd "$(dirname "$0")"
# Antes: module load vivado/2023.2-enterprise
command -v vivado > /dev/null || { echo "nao achei vivado no PATH (module load vivado/2023.2-enterprise?)"; exit 1; }
mkdir -p ~/TCC/tmp; export TMPDIR=~/TCC/tmp
JOBS=${JOBS:-2}
ls ~/TCC/pacote_servidor_formatos/versoes/*/trabalho/vivado/roteado.dcp \
   ~/TCC/pacote_servidor_formatos_18_20/versoes/*/trabalho/vivado/roteado.dcp \
   ~/TCC/pacote_servidor_2023/versoes/152_sistolico/trabalho/vivado/roteado.dcp \
   ~/TCC/pacote_servidor_2023/versoes/114_sistolico/trabalho/vivado/roteado.dcp > todos.txt
echo "$(wc -l < todos.txt) projetos roteados"
rm -f parte_*
split -n r/$JOBS todos.txt parte_
for p in parte_*; do
    vivado -mode batch -nojournal -log log_$p.txt -source util_hierarquica.tcl -tclargs $p > /dev/null 2>&1 &
done
wait
echo "fim $(date -Iseconds)"
echo "relatorios: $(ls ~/TCC/pacote_servidor_formatos*/versoes/*/trabalho/vivado/util_hierarquica.rpt ~/TCC/pacote_servidor_2023/versoes/*/trabalho/vivado/util_hierarquica.rpt 2>/dev/null | wc -l)"
