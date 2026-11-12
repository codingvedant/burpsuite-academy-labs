# Lab 7: Username Enumeration via Account Lock

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Username enumeration via account lock](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock)

## Overview

The app locks accounts after several failed login attempts. This lockout message is distinct from the generic "Invalid username or password" response, revealing that the username is valid. Once the valid username is identified, brute-force the password after the lockout window expires.

## Key Concepts

- **Account lockout as an oracle:** a lockout response leaks that the username is real — an invalid username never locks.
- **Timing the unlock:** PortSwigger labs typically unlock after ~1 minute; wait before brute-forcing the password.
- **Wordlists:** PortSwigger provides username and password candidate lists for these labs.

## Solution

### Step 1 — Enumerate usernames

For each candidate username, send 5 failed login attempts (any wrong password). If the response contains "You have made too many incorrect login attempts" → username is valid.

### Step 2 — Wait for unlock

Wait ~1 minute for the lockout to expire.

### Step 3 — Brute-force the password

For the valid username, try each password candidate. The correct password returns a 302 redirect instead of a login error.

### Step 4 — Log in and retrieve API key

Log in with the found credentials, fetch `/my-account`, extract and submit the API key.

## Remediation

- Use generic error messages — "account locked" should not distinguish valid from invalid usernames.
- Implement CAPTCHA after repeated failures rather than a time-based lockout.
- Apply lockout to both valid and invalid usernames equally (silent drop).

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-07-username-enum-account-lock/solve.py)

Sends 5 attempts per username to trigger lockout, identifies the valid username, waits for unlock, then brute-forces the password.

## Key Takeaways

- Account lockout is a double-edged feature — it protects against brute-force but leaks username validity.
- Always test whether lockout messages differ from generic auth failure messages.
- Brute-forcing after lockout still works; the lockout just adds a delay.
