# JWT Attacks

JWTs are signed blobs of JSON that applications often use as self-contained session tokens. The dangerous part is that all trust moves into token verification. If the server accepts the wrong algorithm, trusts attacker-supplied key material, uses a weak secret, or reads the wrong key from disk, the token becomes an access-control bypass.

The pattern across these labs is simple: get a normal token as `wiener`, change the identity to `administrator`, make the server accept the modified token, then delete `carlos`.

[PortSwigger reference](https://portswigger.net/web-security/jwt)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | JWT authentication bypass via unverified signature | Apprentice | Solved |
| 2 | JWT authentication bypass via flawed signature verification | Apprentice | Solved |
| 3 | JWT authentication bypass via weak signing key | Practitioner | Solved |
| 4 | JWT authentication bypass via jwk header injection | Practitioner | Solved |
| 5 | JWT authentication bypass via jku header injection | Practitioner | Solved |
| 6 | JWT authentication bypass via kid header path traversal | Practitioner | Solved |
| 7 | JWT authentication bypass via algorithm confusion | Expert | Solved |
| 8 | JWT authentication bypass via algorithm confusion with no exposed key | Expert | Solved |

## Running

Most scripts only need the lab URL.

```bash
python jwt/lab-01-unverified-signature/solve.py https://0aXX00...web-security-academy.net
```

Some labs need one extra value:

- Lab 5 needs the exploit-server URL where `jwks.json` is hosted.
- Lab 8 needs the PEM public key derived from two valid tokens using PortSwigger's `jwt_forgery.py` helper.
