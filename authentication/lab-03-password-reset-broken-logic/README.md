# Lab 3: Password Reset Broken Logic

**Category:** Authentication
**Difficulty:** Apprentice
**Lab link:** [Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic)

## Overview

The password reset flow issues a token via email and accepts it at `/forgot-password?temp-forgot-password-token=TOKEN`. The token is not cryptographically bound to the target username — the final POST includes a `username` field that the server trusts unconditionally. Changing `username` to `carlos` while using your own valid token resets carlos's password.

## Key Concepts

- **Token not bound to identity:** the reset token proves the request is "from a reset flow" but the server doesn't verify it was issued for the specific user in the POST body.
- **Parameter tampering:** client-supplied `username` parameter in the final reset step is trusted without cross-checking against the token's original owner.

## Solution

### Step 1 — Trigger a reset for yourself

Request a password reset for `wiener`. Check the email client for the reset link containing `temp-forgot-password-token`.

### Step 2 — Intercept the final reset POST

Follow the reset link to load the form. Submit a new password but intercept the POST:
```
POST /forgot-password?temp-forgot-password-token=YOUR_TOKEN
username=wiener&new-password-1=newpass&new-password-2=newpass&temp-forgot-password-token=YOUR_TOKEN
```

### Step 3 — Change the username

Modify `username=wiener` → `username=carlos` in the POST body. Keep your own valid token. Submit. Carlos's password is now reset.

### Step 4 — Log in as carlos

Use the new password to log in as carlos. Lab solved.

## Remediation

- Bind the reset token to a specific username server-side at issuance time. On redemption, ignore the client-supplied username — use only the username stored with the token.
- Use short-lived, single-use tokens stored in the database with the associated user ID.
- Never trust a client-supplied username parameter in a privileged flow — derive identity from the session or token, not from request parameters.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-03-password-reset-broken-logic/solve.py)

Triggers a reset for wiener, extracts the token from the email client endpoint, then resets carlos's password by substituting the username parameter.

## Key Takeaways

- Password reset tokens must be bound to a specific user at creation — the server must ignore user identity claims in the final POST.
- Always check: does the reset form include a username field? If so, it's likely injectable.
- Single-use tokens prevent replay; short expiry limits the window.
