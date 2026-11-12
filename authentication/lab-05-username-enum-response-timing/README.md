# Lab 5: Username Enumeration via Response Timing

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Username enumeration via response timing](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing)

## Overview

The login endpoint processes the password check (bcrypt hash comparison) only for valid usernames. For invalid usernames it returns immediately. By submitting a very long password with each candidate username and measuring response time, valid usernames can be identified by their longer processing time.

## Key Concepts

- **Timing side-channel:** bcrypt is intentionally slow. For a valid username, bcrypt runs; for an invalid username, the server short-circuits. A 100+ character password amplifies this difference.
- **IP-based rate limiting bypass:** the lab blocks IPs after several failed attempts. Use `X-Forwarded-For` with a unique IP per request to rotate past the block.

## Solution

### Step 1 — Rotate IP via X-Forwarded-For

Add `X-Forwarded-For: <unique-ip>` header to each request. Increment the last octet per request.

### Step 2 — Send timing probes

For each candidate username, POST to `/login` with a 100-character password and record elapsed time.

### Step 3 — Identify the valid username

The request that takes significantly longer than others corresponds to the valid username (bcrypt ran on it).

### Step 4 — Brute-force the password

With IP rotation still active, brute-force the confirmed username with normal-length passwords.

### Step 5 — Log in

Use the found credentials. Lab solved.

## Remediation

- Apply constant-time processing for all login attempts regardless of whether the username exists (always run a dummy bcrypt check for invalid usernames).
- Do not short-circuit on username validation before the password check.
- Rate-limit on a combination of IP, username, and session — not IP alone.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-05-username-enum-response-timing/solve.py)

Uses X-Forwarded-For rotation and a long password probe to identify the valid username by timing, then brute-forces the password.

## Key Takeaways

- Timing attacks require only a network connection — no special access needed.
- Always perform a dummy credential check even for invalid usernames to prevent timing leaks.
- `X-Forwarded-For` is trivially forgeable — it must not be the sole basis for IP-based rate limiting.
