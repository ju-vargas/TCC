# 2026-11-05T17:03:36.980041161
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

comp = client.get_component(name="cholesky_hardware")
comp.run(operation="SYNTHESIS")

vitis.dispose()

