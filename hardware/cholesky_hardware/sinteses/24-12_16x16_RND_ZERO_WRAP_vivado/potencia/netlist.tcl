open_checkpoint /home/juliana/GitHub/TCC/hardware/cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/w/hls/impl/verilog/project.runs/impl_1/bd_0_wrapper_routed.dcp
set c [get_cells bd_0_i/hls_inst/inst]
puts "REF [get_property REF_NAME $c] ORIG [get_property ORIG_REF_NAME $c]"
write_verilog -mode funcsim -cell bd_0_i/hls_inst/inst -force /home/juliana/GitHub/TCC/hardware/cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/potencia/sim_netlist/netlist_roteada.v
