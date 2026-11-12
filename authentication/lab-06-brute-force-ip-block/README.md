# Lab 6: Broken Brute-Force Protection, IP Block

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Broken brute-force protection, IP block](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-ip-block)

## Overview

The app blocks an IP after a fixed number of consecutive failed login attempts. The counter resets on a successful login. By interleaving a valid login (wiener:peter) between every attack attempt, the failed-attempt counter never reaches the threshold, allowing unlimited brute-force of carlos's password.

## Key Concepts

- **Counter reset on success:** IP-based blocks that reset on any successful login from the same IP are bypassable by the attacker owning a valid account.
- **Interleaving pattern:** attack request → valid login → attack request → valid login → … keeps the counter at 1 or 2, never reaching the block threshold.

## Solution

### Step 1 — Understand the block threshold

After N (usually 3) failed logins from the same IP, the app blocks further attempts.

### Step 2 — Interleave valid logins

For each password to test against carlos:
1. POST `/login` with `username=carlos&password=<candidate>` — this is the attack attempt.
2. POST `/login` with `username=wiener&password=peter` — this resets the counter.

### Step 3 — Detect success

When the attack POST returns a 302 (or no "Incorrect password" message), carlos's password is found.

### Step 4 — Log in as carlos

Use the found credentials. Lab solved.

## Remediation

- Reset the failed-attempt counter only on a successful login **for the same account**, not any account from that IP.
- Use per-username lockout in addition to per-IP rate limiting.
- Consider CAPTCHA after N failures regardless of subsequent successes.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-06-brute-force-ip-block/solve.py)

Interleaves a valid wiener:peter login between each carlos password attempt to keep the IP block counter below the threshold.

## Key Takeaways

- IP-based rate limiting that resets on success is bypassable by any attacker who has a valid account.
- Brute-force protection must be per-username, not just per-IP.
- The interleave bypass is a standard technique — always test it when you observe an IP block reset on success.
