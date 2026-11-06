# 2026-09-15T15:40:05.927328061
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

cfg = client.get_config_file(path="/home/juliana/GitHub/TCC/hardware/cholesky_hardware/hls_config.cfg")

cfg.set_values(key="syn.file", values=["hardware.cpp"])

cfg.set_values(key="tb.file", values=["testbench.cpp"])

comp = client.get_component(name="cholesky_hardware")
comp.run(operation="C_SIMULATION")

cfg.set_values(key="syn.file", values=["hardware.cpp", "lu_decomposition.h"])

cfg.set_values(key="syn.file", values=["hardware.cpp", "lu_decomposition.h", "lu_decomposition.cpp"])

cfg.set_values(key="tb.file", values=["tb_lu_decomposition.cpp"])

comp.run(operation="C_SIMULATION")

cfg.set_values(key="syn.file", values=["lu_decomposition.h", "lu_decomposition.cpp"])

cfg.set_values(key="syn.blackbox.file", values=[])

comp.run(operation="C_SIMULATION")

vitis.dispose()

