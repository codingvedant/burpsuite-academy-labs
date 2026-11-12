# Lab 1: Username Enumeration via Different Responses

**Category:** Authentication
**Difficulty:** Apprentice
**Lab link:** [Username enumeration via different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses)

## Overview

The login endpoint returns "Invalid username" for unknown usernames and "Incorrect password" for valid usernames with a wrong password. This difference allows an attacker to enumerate valid usernames, then brute-force the password for the confirmed user.

## Key Concepts

- **Username enumeration:** distinct error messages expose whether a username exists, reducing brute-force effort from |users| × |passwords| to |users| + |passwords|.
- **Two-phase attack:** first find the valid username, then brute-force only that account's password.

## Solution

### Step 1 — Enumerate usernames

POST to `/login` with each candidate username and a dummy password. Look for a response that says "Incorrect password" instead of "Invalid username".

```
POST /login HTTP/1.1
username=candidate&password=dummy&csrf=TOKEN
```

### Step 2 — Brute-force the password

With the confirmed username, POST to `/login` again iterating over the PortSwigger password list. A 302 redirect (or absence of "Incorrect password") indicates success.

### Step 3 — Log in

Use the found credentials to access `/my-account`. Lab solved.

## Remediation

- Use a **generic error message** for all login failures: "Invalid username or password."
- Apply the same response time regardless of whether the username exists (constant-time comparison).
- Rate-limit login attempts per IP and per account.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-01-username-enum-different-responses/solve.py)

Enumerates usernames by checking for "Incorrect password", then brute-forces the password with the confirmed username.

## Key Takeaways

- Different error messages for bad username vs bad password are a classic information leak.
- Always test both phases: enumerate first, then brute-force — it is far faster than a full credential matrix.
- PortSwigger provides a canonical username and password wordlist for these labs.
