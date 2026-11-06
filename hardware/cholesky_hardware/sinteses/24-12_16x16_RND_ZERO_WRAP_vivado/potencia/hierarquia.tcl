open_checkpoint /home/juliana/GitHub/TCC/hardware/cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/w/hls/impl/verilog/project.runs/impl_1/bd_0_wrapper_routed.dcp
puts "TOPO [get_property NAME [current_design]]"
foreach c [get_cells -hier -filter {REF_NAME == cholesky_inverse || ORIG_REF_NAME == cholesky_inverse}] { puts "INST $c" }
