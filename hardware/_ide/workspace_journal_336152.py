# 2026-09-17T10:33:32.662754152
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

vitis.dispose()

