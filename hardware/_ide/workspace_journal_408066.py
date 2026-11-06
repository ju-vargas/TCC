# 2026-09-17T14:17:33.609665615
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

comp = client.get_component(name="cholesky_hardware")
comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

comp.run(operation="C_SIMULATION")

vitis.dispose()

