# Lab 11: Password Reset Poisoning via Middleware

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware)

## Overview

The password reset flow constructs the reset link using the `Host` header (or a middleware override header like `X-Forwarded-Host`). An attacker poisons the reset request with their own server's hostname, causing the reset email sent to carlos to contain a link pointing to the attacker's server. The attacker captures the token from their server logs and uses it to reset carlos's password.

## Key Concepts

- **Host header injection:** the app trusts `X-Forwarded-Host` (set by a reverse proxy) to build absolute URLs. Supplying an attacker-controlled value redirects the reset link.
- **Reset token leakage:** the token is a secret — once it appears in a request to the attacker's server, it can be replayed against the real app.
- **Middleware trust:** headers like `X-Forwarded-Host`, `X-Forwarded-For`, `X-Original-URL` are proxy hints that apps may trust implicitly.

## Solution

### Step 1 — Trigger a reset for carlos

POST `/forgot-password` with `username=carlos`. Before sending, add:
```
X-Forwarded-Host: <your-exploit-server-host>
```

### Step 2 — Capture the token

Carlos's simulated email client clicks the link, which now points to your exploit server. Check the exploit server's access log for:
```
GET /forgot-password?temp-forgot-password-token=<TOKEN>
```

### Step 3 — Use the token

Send `GET /forgot-password?temp-forgot-password-token=<TOKEN>` to the **lab** (not the exploit server), then POST the new password.

### Step 4 — Log in as carlos

Use the new password to log in. Lab solved.

## Remediation

- Build reset URLs using the application's configured base URL (from config), not from request headers.
- Validate or strip `X-Forwarded-Host` at the perimeter; don't pass it through to application logic.
- Bind reset tokens to the user's email/IP and expire them quickly (< 15 minutes, single use).

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-11-password-reset-poisoning-middleware/solve.py)

Triggers the poisoned reset, then (given the captured token) resets carlos's password and logs in.

## Key Takeaways

- Never use `Host` or `X-Forwarded-Host` headers to construct security-sensitive URLs.
- Password reset tokens in URLs are secrets — any redirect leaks them to the destination server's logs.
- Middleware trust headers must be explicitly allowlisted and stripped from untrusted requests.
