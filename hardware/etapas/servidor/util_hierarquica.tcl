# Abre cada projeto roteado (roteado.dcp) e gera a utilizacao por hierarquia.
# uso: vivado -mode batch -source util_hierarquica.tcl -tclargs <lista.txt>
# lista.txt: um caminho de roteado.dcp por linha. Saida: util_hierarquica.rpt na mesma pasta.
set f [open [lindex $argv 0]]
set dcps [split [string trim [read $f]] "\n"]
close $f
foreach dcp $dcps {
    set saida [file join [file dirname $dcp] util_hierarquica.rpt]
    if {[file exists $saida]} { puts "ja existe: $saida"; continue }
    puts "inicio: $dcp [clock format [clock seconds]]"
    open_checkpoint $dcp
    report_utilization -hierarchical -hierarchical_depth 3 -file $saida.tmp
    file rename -force $saida.tmp $saida
    close_design
    puts "ok: $saida [clock format [clock seconds]]"
}
