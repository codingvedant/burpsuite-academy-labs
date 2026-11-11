# Lab 8: User ID Controlled by Request Parameter with Password Disclosure

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [User ID controlled by request parameter with password disclosure](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-password-disclosure)

## Overview

The account page pre-populates the password field with the user's current password. Combined with the IDOR on the `id` parameter, accessing `/my-account?id=administrator` reveals the administrator's password in the HTML source. Use it to log in as admin and delete `carlos`.

## Key Concepts

- **IDOR leading to credential disclosure:** the missing ownership check on the account page exposes not just an API key but the actual account password.
- **Password pre-population in HTML:** the `<input type="password" value="...">` pattern sends the plaintext password to the browser — visible in source even though the field displays as dots.
- **Privilege escalation chain:** horizontal IDOR (view admin's page) → vertical escalation (use admin password to log in as admin).

## Solution

### Step 1 — Log in

Credentials: `wiener` / `peter`.

### Step 2 — Access administrator's account page

Navigate to:
```
/my-account?id=administrator
```

### Step 3 — Read the password from the source

View page source (Ctrl+U) and search for `password`. You'll find:
```html
<input required type="password" name="password" value="ADMIN-PASSWORD-HERE">
```

### Step 4 — Log in as administrator

Log out, then log in with `administrator` / `<disclosed password>`.

### Step 5 — Delete carlos

Go to `/admin` and delete `carlos`. Lab solved.

## How It Works

The server renders the account page for whichever user the `id` parameter names. The template includes the password field pre-filled with the current password. No ownership check is performed, so requesting `id=administrator` renders the admin's page complete with their password in the HTML.

## Two Bugs in One

1. **IDOR** — no ownership check on `/my-account?id=`.
2. **Password reflected in HTML** — passwords should never be sent to the client, even as masked input fields.

Either bug alone would be serious; together they enable full admin compromise.

## Remediation

- Server-side ownership check on every account resource.
- Never pre-populate password fields with current passwords. For a "change password" flow, require the current password to be re-entered, not pre-filled.
- Passwords should be hashed server-side and never sent to the client in any form.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-08-userid-password-disclosure/solve.py)

Logs in as `wiener`, fetches `/my-account?id=administrator`, extracts the password from the HTML, re-logs in as admin, and deletes `carlos`.

## Key Takeaways

- Password fields with `value=` attributes send the password to the browser in plaintext HTML.
- IDOR + password disclosure = full account takeover chain.
- Never return credentials in HTTP responses regardless of how they're rendered client-side.
