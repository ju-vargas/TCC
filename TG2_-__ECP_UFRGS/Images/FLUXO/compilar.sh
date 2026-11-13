#!/bin/sh
# Recompila as figuras TikZ (src/*.tex) em PDF. Rodar na raiz do projeto:
#   sh Images/FLUXO/compilar.sh            (todas)
#   sh Images/FLUXO/compilar.sh dmrs_n     (uma)
# Depois de editar uma figura em src/, recompile e suba o PDF junto com o projeto.
cd "$(dirname "$0")/src" || exit 1
for f in ${@:-*.tex}; do
  f=${f%.tex}
  pdflatex -interaction=nonstopmode "$f.tex" >/dev/null || echo "ERRO em $f"
  mv "$f.pdf" ..
  rm -f "$f.aux" "$f.log"
done
