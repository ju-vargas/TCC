# 2026-09-21T12:42:34.224091550
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

comp = client.get_component(name="cholesky_hardware")
comp.run(operation="SYNTHESIS")

vitis.dispose()

