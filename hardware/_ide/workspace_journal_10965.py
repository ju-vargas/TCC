# 2026-09-17T16:28:18.084036976
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

cfg = client.get_config_file(path="/home/juliana/GitHub/TCC/hardware/cholesky_hardware/hls_config.cfg")

cfg.set_values(key="syn.file", values=["cholesky.h", "cholesky_decomposition.cpp", "lu_decomposition.cpp", "dv_step.cpp", "s_step.cpp", "g_step.cpp", "foward_substitution.cpp"])

cfg.set_values(key="syn.file", values=["cholesky.h", "cholesky_decomposition.cpp", "lu_decomposition.cpp", "dv_step.cpp", "s_step.cpp", "g_step.cpp", "foward_substitution.cpp", "inversion.cpp"])

vitis.dispose()

