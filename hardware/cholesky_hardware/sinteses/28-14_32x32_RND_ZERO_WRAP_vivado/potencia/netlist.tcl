# Exporta a netlist roteada do inversor para a simulação da potência.
# No máximo 4 núcleos (a máquina divide com a simulação)
set_param general.maxThreads 4
open_checkpoint /home/juliana/GitHub/TCC/hardware/cholesky_hardware/sinteses/28-14_32x32_RND_ZERO_WRAP_vivado/w/hls/impl/verilog/project.runs/impl_1/bd_0_wrapper_routed.dcp
write_verilog -mode funcsim -cell bd_0_i/hls_inst/inst -force /home/juliana/GitHub/TCC/hardware/cholesky_hardware/sinteses/28-14_32x32_RND_ZERO_WRAP_vivado/potencia/netlist_bruta.v
