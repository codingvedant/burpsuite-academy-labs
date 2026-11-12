# Lab 13: Broken Brute-Force Protection, Multiple Credentials per Request

**Category:** Authentication
**Difficulty:** Expert
**Lab link:** [Broken brute-force protection, multiple credentials per request](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request)

## Overview

The login endpoint accepts JSON and applies brute-force protection per request rather than per credential tested. By sending an array of passwords instead of a single string, all passwords are evaluated in one request — completely bypassing the rate limiter.

## Key Concepts

- **Per-request rate limiting flaw:** the protection counts requests, not credential attempts. One request with 100 passwords costs only 1 attempt against the limiter.
- **JSON array type confusion:** the server likely iterates over the password value if it's an array, checking each one. This is a server-side logic flaw — the developer assumed `password` would always be a string.

## Solution

### Step 1 — Observe the login request

Intercept `POST /login`. Confirm it uses JSON: `{"username":"carlos","password":"foo"}`.

### Step 2 — Build the password array

Replace the password string with the full PortSwigger password list as a JSON array:
```json
{"username":"carlos","password":["123456","password","12345678","qwerty",...]}
```

The array is in `passwords.json` in this directory — copy its contents as the `password` value.

### Step 3 — Send

Send the request. When the server finds the correct password in the array it responds with **302** (redirect to account page) instead of 200 (invalid credentials).

### Step 4 — Follow the redirect

Log in as carlos. Lab solved.

## passwords.json

The file `passwords.json` in this directory contains the full PortSwigger 100-password list pre-formatted as a JSON array, ready to paste directly into the request body.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-13-multi-credentials-brute-force/solve.py)

Loads passwords.json, sends one POST with the full array, follows the redirect, and confirms login as carlos.

## Remediation

- Validate that `password` is a string type, not an array — reject requests where it is not.
- Apply rate limiting per credential attempt, not per request — count each element of an array separately.
- Use a strict JSON schema to reject unexpected field types at the API boundary.

## Key Takeaways

- Rate limiting that counts requests rather than auth attempts is trivially bypassed with array payloads.
- Always validate input types — a JSON array where a string is expected is an anomaly that should be rejected.
- One request can test hundreds of credentials if the server iterates over an array value.
