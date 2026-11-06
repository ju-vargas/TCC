open_checkpoint /home/juliana/GitHub/TCC/hardware/cholesky_hardware/sinteses/24-12_16x16_RND_ZERO_WRAP_vivado/w/hls/impl/verilog/project.runs/impl_1/bd_0_wrapper_routed.dcp
foreach n [lrange [get_nets -hier -filter {NAME =~ *ap_start* || NAME =~ *A_matrix_address0*}] 0 8] { puts "NET $n" }
foreach c [lrange [get_cells -hier -filter {NAME =~ *L_M_real_U*}] 0 3] { puts "CELL $c" }
puts "NCELLS_INST [llength [get_cells bd_0_i/hls_inst/inst/*]]"
