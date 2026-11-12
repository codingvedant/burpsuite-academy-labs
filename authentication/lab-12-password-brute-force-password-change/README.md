# Lab 12: Password Brute-Force via Password Change

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)

## Overview

The password change form at `/my-account/change-password` accepts `username`, `current-password`, `new-password-1`, and `new-password-2`. When `new-password-1 != new-password-2` and `current-password` is **correct**, the response says "New passwords do not match". When `current-password` is **wrong**, it says "Current password is incorrect". This oracle is not rate-limited, enabling brute-force of carlos's password.

## Key Concepts

- **Error message oracle:** different messages for wrong current password vs mismatched new passwords reveal whether the current password guess was correct.
- **No rate limiting on change-password:** the login endpoint may have protection, but the change-password endpoint often does not.
- **Username parameter:** the endpoint accepts a `username` field — submitting `username=carlos` targets carlos's account without being logged in as them (or while logged in as wiener).

## Solution

### Step 1 — Log in as wiener

Log in as wiener/peter to get an authenticated session.

### Step 2 — Brute-force carlos's password

POST `/my-account/change-password` with:
```
username=carlos
current-password=<candidate>
new-password-1=anything
new-password-2=different
```

- Response contains "New passwords do not match" → current-password is **correct**
- Response contains "Current password is incorrect" → wrong guess

### Step 3 — Log in as carlos

Use the found password to log in as carlos. Access `/my-account` and retrieve the API key.

## Remediation

- Apply the same rate limiting and lockout to the change-password endpoint as to the login endpoint.
- Do not accept a `username` parameter on the change-password endpoint — derive the user from the session.
- Use consistent error messages that don't distinguish wrong current password from mismatched new passwords.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-12-password-brute-force-password-change/solve.py)

Logs in as wiener, brute-forces carlos's password via the change-password oracle, then logs in as carlos and retrieves the API key.

## Key Takeaways

- Password change endpoints are frequently overlooked when hardening authentication flows.
- Different error messages for "wrong current password" vs "passwords don't match" is a classic oracle.
- Sensitive operations must derive the acting user from the session, not from a submitted `username` field.
