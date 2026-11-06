# 2026-09-17T13:11:29.240947766
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

vitis.dispose()

