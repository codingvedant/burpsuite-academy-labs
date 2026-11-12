# Lab 8: 2FA Broken Logic

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [2FA broken logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic)

## Overview

The 2FA implementation ties the verification code to a `verify` POST parameter rather than the authenticated session. After logging in as wiener, an attacker can change `verify=carlos` on the `/login2` endpoint and brute-force the 4-digit MFA code to log in as carlos without knowing their password.

## Key Concepts

- **Session vs parameter binding:** the 2FA code should be tied to the authenticated session on the server. Using a user-supplied parameter (`verify=carlos`) means any user can claim to be verifying any account.
- **Small keyspace:** 4-digit numeric codes (0000–9999) have only 10,000 possibilities — easily brute-forced even without rate limiting.

## Solution

### Step 1 — Log in as wiener

POST `/login` with wiener/peter. Observe the GET `/login2` request — it sets `verify=wiener` via a cookie or parameter. Note the POST `/login2` takes `mfa-code` and `verify`.

### Step 2 — Trigger a code for carlos

Send `GET /login2` with `verify=carlos` in the cookie/parameter. This causes the server to generate and send a 2FA code to carlos's device.

### Step 3 — Brute-force the MFA code

POST `/login2` with `verify=carlos` and `mfa-code=0000` through `9999`. A 302 redirect indicates success.

### Step 4 — Follow the redirect

The 302 response sets a session cookie for carlos. Load `/my-account` to confirm and retrieve the API key.

## Remediation

- Bind the pending 2FA verification to the **server-side session**, not a client-supplied parameter.
- Rate-limit and lock 2FA attempts after N failures.
- Use cryptographically random codes with short expiry (< 5 minutes).

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-08-2fa-broken-logic/solve.py)

Logs in as wiener, triggers a code for carlos via GET /login2?verify=carlos, then brute-forces mfa-code 0000–9999.

## Key Takeaways

- 2FA is only secure if the code is tied to the session that just authenticated — not to an arbitrary user parameter.
- 4-digit codes are brute-forceable in seconds without rate limiting.
- Always test whether the `verify` / `username` parameter on a 2FA endpoint can be tampered with.
