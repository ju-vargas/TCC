open_saif atividade.saif
set n 0
foreach s [concat [list /apatb_cholesky_inverse_top/AESL_inst_cholesky_inverse] [get_scopes -r /apatb_cholesky_inverse_top/AESL_inst_cholesky_inverse/*]] {
  current_scope $s
  set o [get_objects *]
  if {[llength $o]} { log_saif $o; incr n [llength $o] }
}
puts "SAIF: $n objetos"
run all
close_saif
quit
