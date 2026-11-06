# 2026-10-06T14:57:05.476972070
import vitis

client = vitis.create_client()
client.set_workspace(path="hardware")

vitis.dispose()

