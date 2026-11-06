# Sintese RTL e implementacao de uma versao, fora de contexto, a 100 MHz.
# Mesmos passos e opcoes do fluxo que o HLS 2026.1 gerou para as outras versoes
# (w/hls/impl/verilog/run_vivado.tcl): synth_design -directive sdx_optimization_effort_high
# -mode out_of_context; opt_design, place_design, phys_opt_design e route_design com as opcoes
# padrao. A diferenca e que aqui o topo e o proprio cholesky_inverse, sem o block design em volta.
# uso: vivado -mode batch -source vivado.tcl -tclargs <pasta do rtl> <pasta de saida>
set rtl [file normalize [lindex $argv 0]]
set saida [file normalize [lindex $argv 1]]
set parte xcu50-fsvh2104-2-e
cd $saida

read_verilog [glob $rtl/*.v]
read_xdc $rtl/cholesky_inverse.xdc
synth_design -top cholesky_inverse -part $parte -include_dirs $rtl \
    -directive sdx_optimization_effort_high -mode out_of_context
report_utilization -file utilizacao_sintese.rpt

opt_design
place_design
phys_opt_design
route_design
write_checkpoint -force roteado.dcp
report_utilization -file utilizacao.rpt
report_timing_summary -file timing.rpt
# Netlist para a simulacao com SAIF (o topo continua cholesky_inverse)
write_verilog -mode funcsim -force netlist_roteada.v
