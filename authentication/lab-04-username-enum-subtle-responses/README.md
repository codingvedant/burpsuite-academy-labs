# Lab 4: Username Enumeration via Subtly Different Responses

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Username enumeration via subtly different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses)

## Overview

The login endpoint attempts a consistent error message for all failures but introduces a subtle difference — a trailing space or missing period — for valid usernames. Response length comparison (not text matching) reliably identifies the valid username.

## Key Concepts

- **Subtle enumeration:** the error message text looks the same at a glance but the response body length differs by one character (e.g. "Invalid username or password." vs "Invalid username or password ").
- **Length-based detection:** comparing `len(response.text)` across all candidates finds the outlier without needing to match a specific string.

## Solution

### Step 1 — Collect response lengths for all usernames

POST to `/login` with each candidate username and a dummy password. Record the response length for each.

### Step 2 — Identify the outlier

The valid username produces a response of a different length from all others (usually shorter or longer by one character due to a subtle message difference).

### Step 3 — Brute-force the password

With the confirmed username, iterate over the password list. A 302 redirect indicates success.

### Step 4 — Log in

Use the found credentials. Lab solved.

## Remediation

- Use a constant-length generic error string for all authentication failures — do not vary message text, punctuation, or whitespace based on whether the username exists.
- Constant-time response (server-side sleep if needed) prevents timing-based variants of this attack.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-04-username-enum-subtle-responses/solve.py)

Collects response lengths for all usernames, identifies the statistical outlier, then brute-forces the password.

## Key Takeaways

- Response length is as revealing as response text — even a one-character difference is exploitable at scale.
- Use Burp Intruder's "Response received" column or a script to compare lengths across a large wordlist.
- Subtle differences are often introduced by copy/paste errors in error message strings.
