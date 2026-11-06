# 2026-08-24T15:45:04.732059583
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

comp = client.create_hls_component(name = "cholesky_hardware",part = "xcu50-fsvh2104-2-e",cfg_file = ["hls_config.cfg"],template = "empty_hls_component")

cfg = client.get_config_file(path="/home/juliana/GitHub/TCC/hardware/cholesky_hardware/hls_config.cfg")

cfg.set_values(key="syn.file", values=["main.cpp"])

cfg.set_value(section="hls", key="syn.top", value="soma_hls")

vitis.dispose()

