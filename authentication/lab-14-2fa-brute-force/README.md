# Lab 14: 2FA Bypass Using a Brute-Force Attack

**Category:** Authentication
**Difficulty:** Expert
**Lab link:** [2FA bypass using a brute-force attack](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack)

## Overview

Carlos's account uses 2FA with a 4-digit code (0000–9999). After 2 wrong attempts the app invalidates the session and redirects back to login, preventing naive brute-force. The bypass: use a Burp Macro to automatically re-login as carlos before every Intruder attempt, giving a fresh session (and fresh attempt counter) for each code tried. The 2FA code is static for the account — the macro only resets the lockout, not the code.

## Key Concepts

- **Static 2FA code per account:** the code is tied to the account and doesn't change between re-logins. Re-logging in via macro resets the session's attempt counter (0/2) without changing the underlying code.
- **Burp Macro:** a recorded sequence of requests Burp replays automatically before each Intruder/Repeater request. Used here to maintain a valid "logged-in, awaiting 2FA" session state for every attempt.
- **Session Handling Rule:** tells Burp which tools and URL scope the macro applies to. Without it, the macro doesn't fire.
- **Why lockout fails:** the lockout is per-session (2 attempts), not per-account. Creating a new session via re-login resets the counter. A proper lockout would be per-account with an exponential backoff.

## Solution

### Step 1 — Understand the flow

Log in as `carlos` / `montoya`. Observe:
- `POST /login` → session cookie + redirect to `/login2`
- `POST /login2` with `mfa-code=XXXX` → 302 (correct) or 200 (wrong)
- After 2 wrong codes → session invalidated, redirected to `/login`

### Step 2 — Record the macro

`Project options → Sessions → Macros → Add`
- Record `POST /login` with `username=carlos&password=montoya`
- Burp captures the resulting `session` cookie
- Configure the macro item to extract and propagate the `session` cookie to subsequent requests

### Step 3 — Create a Session Handling Rule

`Project options → Sessions → Session Handling Rules → Add`
- Action: **Run a macro** → select the login macro
- Scope tab → Tools: check **Intruder**
- Scope tab → URL: `https://<lab>/login2`

### Step 4 — Set up Intruder

Send `POST /login2` to Intruder with `mfa-code=§0000§`:
- Attack type: **Sniper**
- Payload type: **Numbers**
  - From: `0`, To: `9999`, Step: `1`
  - Min integer digits: `4`, Max integer digits: `4` (adds leading zeros: 0001, 0023, etc.)

### Step 5 — Run and find the hit

Start the attack. For each attempt, the macro re-logs in as carlos first, giving a fresh session. Look for the **302** response — that's the correct code.

### Step 6 — Log in manually

Use the correct code to log in as carlos. Lab solved.

## Why the Macro Works

```
Macro:    POST /login (carlos/montoya) → new session cookie
Intruder: POST /login2 Cookie=<new> mfa-code=XXXX → 200 (wrong) or 302 (correct)
```

The code is fixed for the account. The macro gives a 2-attempt window for each code tried. With 10,000 iterations the correct code is found and returns a 302.

## Remediation

- Implement **account-level** lockout after N failed 2FA attempts, not session-level.
- Use time-based OTP (TOTP) so the code rotates every 30 seconds — a static code is brute-forceable even with rate limiting.
- Add exponential backoff and CAPTCHA after repeated 2FA failures.
- Alert and require re-authentication after a suspicious number of failed 2FA attempts from the same account.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-14-2fa-brute-force/solve.py)

Replicates the macro approach in code: for each code, re-logs in as carlos to get a fresh session, then POSTs to /login2. Stops on first 302.

## Key Takeaways

- 2FA lockout must be per-account, not per-session — otherwise re-logging in resets the counter.
- Burp Macros are the standard tool for stateful brute-force where session state must be reset between attempts.
- A 4-digit code (10,000 possibilities) is far too small — TOTP or longer codes are essential.
- Static 2FA codes (not time-based) are brute-forceable regardless of attempt limits if re-authentication is possible.
