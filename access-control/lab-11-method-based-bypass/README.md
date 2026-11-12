# Lab 11: Method-Based Access Control Can Be Circumvented

**Category:** Access Control Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Method-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented)

## Overview

The admin panel enforces role checks only on `POST` requests to `/admin-roles`. The same endpoint accepts `GET` requests with query parameters but skips the role check entirely, allowing a low-privileged user to upgrade their own account.

## Key Concepts

- **Method-based access control flaw:** access control is applied per HTTP method rather than per endpoint. A developer may secure `POST` (which mutates state) but forget that `GET` to the same route can also trigger the same logic.
- **HTTP method override:** some apps also accept `X-HTTP-Method-Override: GET` header to bypass method checks without changing the actual method — worth trying if GET doesn't work.

## Solution

### Step 1 — Observe the admin action

Log in as `administrator` / `admin`. Open the admin panel and upgrade any user. Observe the request in Burp:
```
POST /admin-roles HTTP/1.1
...
username=carlos&action=upgrade
```

### Step 2 — Log in as wiener

Log out. Log in as `wiener` / `peter`.

### Step 3 — Change method to GET

Take the `POST /admin-roles` request and convert it to GET, moving body params to the query string:
```
GET /admin-roles?username=wiener&action=upgrade HTTP/1.1
Host: <lab>
Cookie: session=<wiener-session>
```

In Burp Repeater: right-click → **Change request method** to auto-convert.

### Step 4 — Send

The back-end processes the upgrade without checking wiener's role. Lab solved.

## Remediation

- Enforce access control at the **endpoint level**, not the method level.
- Apply the same role check regardless of HTTP method — `GET /admin-roles` and `POST /admin-roles` must both verify admin role.
- Treat `GET` requests that have side effects as equivalent to `POST` for authorization purposes.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-11-method-based-bypass/solve.py)

Logs in as administrator to get the CSRF token, then logs in as wiener and sends `GET /admin-roles?username=wiener&action=upgrade`.

## Key Takeaways

- Access control must be enforced uniformly across all HTTP methods for a given endpoint.
- `GET` with query params is functionally equivalent to `POST` with body params for many back-ends.
- Burp's "Change request method" is a quick way to test method-based bypasses.
