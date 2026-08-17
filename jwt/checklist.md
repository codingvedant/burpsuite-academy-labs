# JWT Testing Checklist

## Recon

1. **Find where the JWT lives** - usually the `session` cookie, but also check `Authorization: Bearer ...`
2. **Decode first, exploit later** - split on `.`, base64url-decode the header and payload, and read `alg`, `kid`, `jku`, `jwk`, `iss`, `sub`, `username`, and role claims
3. **Identify the trust decision** - does the app trust `sub`, `username`, `role`, `isAdmin`, or `administrator` from the token?
4. **Test the admin route** - `/admin` and `/admin/delete?username=carlos` are usually the final privilege check
5. **Watch what changes after login** - compare normal and modified tokens in Repeater before automating

## Exploitation Path

```
Have a JWT session token?
|
+-- Can I edit claims and keep any signature?
|   +-- Try changing sub/username to administrator without caring about the signature (Lab 1)
|
+-- Does the server accept alg none?
|   +-- Set {"alg":"none"}, remove the signature section, and resend (Lab 2)
|
+-- Is the token HMAC-signed with a weak secret?
|   +-- Crack with hashcat or a small wordlist, then sign as administrator (Lab 3)
|
+-- Does the server trust header-supplied keys?
|   +-- jwk: embed my public key in the header and sign with my private key (Lab 4)
|   +-- jku: host my JWKS on the exploit server and point the header at it (Lab 5)
|
+-- Does kid control key lookup?
|   +-- Use path traversal to point kid at /dev/null, then sign with an empty secret (Lab 6)
|
+-- Is RS256 confused with HS256?
    +-- Use the RSA public key as an HMAC secret and switch alg to HS256 (Lab 7)
    +-- If no key is exposed, derive it from two valid JWTs first (Lab 8)
```

## Burp Suite Notes

- JWT Editor - decode, edit, and re-sign tokens in Repeater
- Repeater - test each token variant against `/admin`
- Decoder - base64url-decode JWT sections quickly
- Comparer - compare a normal token and forged token
- Intruder - useful for testing weak HMAC secrets if hashcat is not available

## External Tools

- `hashcat -a 0 -m 16500 <jwt> <wordlist>` - crack weak HMAC secrets offline
- PortSwigger `jwt_forgery.py` - derive an RSA public key from two valid JWTs when the key is not exposed
- `openssl` - inspect PEM keys and convert formats when needed

## Script Reliability

- Labs 1, 2, 3, 4, 6, and 7 are reliable with only the lab URL.
- Lab 5 needs the exploit-server URL because the target must fetch the attacker-controlled JWKS.
- Lab 8 needs a derived public key. The exploit is reliable after that key is available, but deriving it is a separate crypto step.

