#!/usr/bin/env bash
#
# Compila o servidor (tb_servidor.cpp + os fontes do hardware) para um formato e
# guarda o executável em <build>/<I>_<F>_<Q>_<O>_<N>/:
#   csim.exe          o servidor
#   ld_library_path   o LD_LIBRARY_PATH para rodá-lo (vazio no modo nativo)
#   tipos.txt         as linhas "TIPO ..." do executável (conferência dos -D)
# Se a pasta já tem um csim.exe, não compila de novo.
#
# Dois modos, com os mesmos fontes e os cabeçalhos ap_fixed do Vitis:
#   nativo (padrão)  g++ -O2 com os cabeçalhos do Vitis, em build/. Cerca de 15 a 35
#                    vezes mais rápido que a C-simulation; os bits foram conferidos
#                    iguais aos da C-simulation (testes/conferir_servidor.py e
#                    testes/conferir_nativo.sh)
#   --vitis          a C-simulation do Vitis (vitis-run --csim), em build_vitis/
#
# Uso: ./compilar_servidor.sh [--vitis] I F QUANT OVERFLOW N
#   ex.: ./compilar_servidor.sh 8 8 AP_TRN AP_SAT 16

set -euo pipefail

MODO=nativo
if [ "${1:-}" = "--vitis" ]; then MODO=vitis; shift; fi
[ $# -eq 5 ] || { sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
I="$1"; F="$2"; Q="$3"; O="$4"; N="$5"

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$AQUI/build"; [ "$MODO" = vitis ] && RAIZ="$AQUI/build_vitis"
NOME="${I}_${F}_${Q}_${O}_${N}"
DESTINO="$RAIZ/$NOME"
[ -x "$DESTINO/csim.exe" ] && { echo "$DESTINO"; exit 0; }
mkdir -p "$RAIZ"
# Uma compilação por formato de cada vez (vários processos podem pedir o mesmo)
exec 9> "$RAIZ/.trava_$NOME"
flock 9
[ -x "$DESTINO/csim.exe" ] && { echo "$DESTINO"; exit 0; }

VITIS="${XILINX_VITIS:-$HOME/2026.1/Vitis}"
DFLAGS="-DCHOL_N=$N -DCHOL_INT_BITS=$I -DCHOL_FRAC_BITS=$F -DCHOL_QUANT=$Q -DCHOL_OVERFLOW=$O"
FONTES="cholesky_decomposition.cpp lu_decomposition.cpp dv_step.cpp s_step.cpp g_step.cpp foward_substitution.cpp inversion.cpp"
TRABALHO="$(mktemp -d "$RAIZ/.trabalho_XXXXXX")"
trap 'rm -rf "$TRABALHO"' EXIT
SAIDA="$TRABALHO/saida"
mkdir -p "$SAIDA"

falha() {
    mkdir -p "$RAIZ/falhas"
    cp "$1" "$RAIZ/falhas/$NOME.log" 2>/dev/null || true
    echo "ERRO: não compilou (ver $RAIZ/falhas/$NOME.log)" >&2
    exit 1
}

if [ "$MODO" = nativo ]; then
    (cd "$AQUI" && g++ -std=gnu++17 -O2 -w -I"$AQUI" -I"$VITIS/include" $DFLAGS \
        tb_servidor.cpp $FONTES -o "$SAIDA/csim.exe") > "$TRABALHO/g++.log" 2>&1 \
        || falha "$TRABALHO/g++.log"
    : > "$SAIDA/ld_library_path"
else
    set +u
    # shellcheck disable=SC1090
    source "${VITIS_SETTINGS:-$HOME/2026.1/Vitis/settings64.sh}" > /dev/null 2>&1
    set -u
    {
        grep -m1 '^part=' "$AQUI/hls_config.cfg"
        echo
        echo "[hls]"
        echo "syn.top=cholesky_decomposition"
        echo "syn.cflags=-I$AQUI $DFLAGS"
        echo "tb.cflags=-I$AQUI $DFLAGS"
        echo "csim.argv=--tipos"
        for f in $(grep '^syn.file=' "$AQUI/hls_config.cfg" | cut -d= -f2); do echo "syn.file=$AQUI/$f"; done
        echo "tb.file=$AQUI/tb_servidor.cpp"
    } > "$TRABALHO/hls_config.cfg"
    (cd "$TRABALHO" && vitis-run --mode hls --csim --config "$TRABALHO/hls_config.cfg" \
        --work_dir "$TRABALHO/vitis" > "$TRABALHO/vitis.log" 2>&1) || true
    BUILD="$TRABALHO/vitis/hls/csim/build"
    [ -x "$BUILD/csim.exe" ] || falha "$TRABALHO/vitis.log"
    cp "$BUILD/csim.exe" "$SAIDA/csim.exe"
    caminhos="$(sed -n 's/^set ::env(LD_LIBRARY_PATH) \([^:$]*\):.*/\1/p' "$BUILD/run_sim.tcl" | tac | paste -sd:)"
    echo "$caminhos${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}:$XILINX_VITIS/lnx64/csim" \
        > "$SAIDA/ld_library_path"
fi

LD_LIBRARY_PATH="$(cat "$SAIDA/ld_library_path")" "$SAIDA/csim.exe" --tipos \
    > "$SAIDA/tipos.txt"
esperado="TIPO fix ap_fixed<$((I + F)),$I,$Q,$O>"
grep -qxF "$esperado" "$SAIDA/tipos.txt" && grep -qx "N $N" "$SAIDA/tipos.txt" || {
    echo "ERRO: o executável não tem o formato pedido ($esperado, N $N):" >&2
    cat "$SAIDA/tipos.txt" >&2
    exit 1; }
mv "$SAIDA" "$DESTINO"
echo "$DESTINO"
