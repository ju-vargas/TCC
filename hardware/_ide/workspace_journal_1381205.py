# 2026-09-24T16:24:12.177364941
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

vitis.dispose()

