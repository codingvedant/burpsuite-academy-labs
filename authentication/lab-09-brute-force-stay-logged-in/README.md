# Lab 9: Brute-Forcing a Stay-Logged-In Cookie

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Brute-forcing a stay-logged-in cookie](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie)

## Overview

The "stay logged in" cookie is constructed as `base64(username:md5(password))`. Knowing the cookie format, an attacker can forge valid cookies for any user by computing `base64(carlos:md5(candidate_password))` for each password in a wordlist, without ever authenticating.

## Key Concepts

- **Predictable cookie construction:** encoding credentials in a cookie (even hashed) is dangerous if the construction algorithm is discoverable — log in as a known user to reverse-engineer it.
- **Offline attack:** once the format is known, the brute-force runs locally (computing hashes) + one HTTP request per candidate — no login rate limiting applies.
- **MD5 is broken:** MD5 is fast to compute and has no salt here, making it trivial to brute-force common passwords.

## Solution

### Step 1 — Reverse-engineer the cookie format

Log in as wiener/peter with "Stay logged in" checked. Decode the `stay-logged-in` cookie:
```
base64_decode("d2llbmVyOjUxZGMzMGRkYzQ3M2Q0M2E2MDExZTllYmJhNmNhNzcw")
→ wiener:51dc30ddc473d43a6011e9ebba6ca770
md5("peter") == 51dc30ddc473d43a6011e9ebba6ca770  ✓
```
Format confirmed: `base64(username:md5(password))`.

### Step 2 — Forge cookies for carlos

For each password candidate:
```python
cookie = base64(f"carlos:{md5(password)}")
```

### Step 3 — Send forged cookie

GET `/my-account` with `stay-logged-in=<forged_cookie>` (no session cookie). A 200 response with account content → password found.

### Step 4 — Extract API key

Parse the API key from the `/my-account` response and submit it.

## Remediation

- Use opaque, cryptographically random session tokens — never encode credentials in cookies.
- If a persistent login token is needed, store a random token server-side and map it to the user; never derive it from the password.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-09-brute-force-stay-logged-in/solve.py)

For each password candidate, computes `base64(carlos:md5(password))` and sends it as the stay-logged-in cookie.

## Key Takeaways

- Credential-derived cookies are equivalent to storing the password in plaintext if the format is known.
- MD5 without a salt is trivially reversible for common passwords.
- "Stay logged in" tokens must be random and server-validated, not client-computable.
