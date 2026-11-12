# Lab 2: 2FA Simple Bypass

**Category:** Authentication
**Difficulty:** Apprentice
**Lab link:** [2FA simple bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass)

## Overview

After completing the first login step (username/password), the app redirects to `/login2` for a 2FA code. The session is already created after step 1 — the 2FA page is just a check. Navigating directly to `/my-account` after step 1 bypasses the 2FA check entirely because the app doesn't verify completion of the second step.

## Key Concepts

- **Incomplete 2FA state check:** the session is marked "logged in" after the first factor. The 2FA page verifies the TOTP but the account page doesn't confirm it was passed.
- **2FA bypass pattern:** log in → get redirected to `/login2` → manually navigate to `/my-account` instead.

## Solution

### Step 1 — Log in with credentials

POST to `/login` with carlos's credentials (found via Lab 1 or given: `carlos` / `montoya`). The app sets a session cookie and redirects to `/login2`.

### Step 2 — Skip the 2FA page

Instead of following the redirect to `/login2`, navigate directly to `/my-account`. The session is already valid from step 1 and the app doesn't enforce 2FA completion. Lab solved.

## Remediation

- Mark the session as "awaiting 2FA" after step 1 and only promote it to "fully authenticated" after the 2FA code is verified.
- Redirect any partially authenticated session back to `/login2` on every protected page load.
- Never grant access to protected resources until all authentication factors are complete.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-02-2fa-simple-bypass/solve.py)

Logs in with carlos's credentials, then GETs `/my-account` directly without visiting `/login2`.

## Key Takeaways

- 2FA is only effective if the application enforces completion — a session created at step 1 must not grant full access.
- Always test: after step 1 of an MFA flow, can you jump directly to authenticated pages?
- Server-side state must track whether 2FA was completed, not just whether credentials were correct.
