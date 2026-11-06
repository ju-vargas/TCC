# uso: vivado -mode batch -source potencia.tcl -tclargs <saif> <relatorio>
open_checkpoint /home/juliana/GitHub/TCC/hardware/cholesky_hardware_diretivas_455/vivado/w/hls/impl/verilog/project.runs/impl_1/bd_0_wrapper_routed.dcp
read_saif -strip_path apatb_cholesky_inverse_top [lindex $argv 0]
report_power -file [lindex $argv 1]
