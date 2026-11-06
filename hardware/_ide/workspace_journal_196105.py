# 2026-09-16T15:29:08.547207250
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

comp = client.get_component(name="cholesky_hardware")
comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

cfg = client.get_config_file(path="/home/juliana/GitHub/TCC/hardware/cholesky_hardware/hls_config.cfg")

cfg.set_values(key="syn.file", values=["cholesky.h", "lu_decomposition.cpp"])

cfg.set_values(key="syn.file", values=["cholesky.h", "lu_decomposition.cpp", "dv_decomposition.cpp"])

cfg.set_values(key="syn.file", values=["cholesky.h", "lu_decomposition.cpp", "dv_step.cpp"])

cfg.set_values(key="syn.file", values=["cholesky.h", "lu_decomposition.cpp", "dv_step.cpp", "s_step.cpp"])

cfg.set_values(key="syn.file", values=["cholesky.h", "lu_decomposition.cpp", "dv_step.cpp", "s_step.cpp", "g_step"])

cfg.set_values(key="syn.file", values=["cholesky.h", "lu_decomposition.cpp", "dv_step.cpp", "s_step.cpp", "g_step.cpp"])

vitis.dispose()

