# 2026-09-15T22:13:36.835451571
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

comp = client.get_component(name="cholesky_hardware")
comp.run(operation="C_SIMULATION")

cfg = client.get_config_file(path="/home/juliana/GitHub/TCC/hardware/cholesky_hardware/hls_config.cfg")

cfg.set_value(section="hls", key="syn.top", value="LU_decomposition")

comp.run(operation="C_SIMULATION")

vitis.dispose()

