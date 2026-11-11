# Lab 3: User Role Controlled by Request Parameter

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [User role controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter)

## Overview

The application stores the user's admin status in a cookie (`Admin=false`). The server reads this cookie on each request to decide whether to grant access. Because cookies are client-controlled, an attacker can flip the value to `Admin=true` and gain full admin access.

## Key Concepts

- **Never trust client-supplied authorization signals.** Cookies, hidden fields, URL parameters, and request headers are all attacker-controlled. Role/privilege must be derived from the server-side session.
- **Parameter-based privilege escalation:** changing a single request parameter (here a cookie) grants a higher privilege level.
- **Cookie manipulation:** browsers and tools like Burp make cookie editing trivial — any value sent in a request can be intercepted and changed.

## Solution

### Step 1 — Log in

Use the provided credentials: `wiener` / `peter`.

### Step 2 — Inspect cookies

In Burp Proxy intercept (or DevTools → Application → Cookies), observe the `Admin` cookie:
```
Cookie: session=...; Admin=false
```

### Step 3 — Change the cookie value

Set `Admin=true`:
```
Cookie: session=...; Admin=true
```

In Burp Repeater, or by editing directly in DevTools.

### Step 4 — Access the admin panel

Navigate to `/admin`. The server reads `Admin=true` from the cookie and renders the admin UI.

### Step 5 — Delete carlos

Click **Delete** next to `carlos`. Lab solved.

## How It Works

The server-side logic looks roughly like:
```python
if request.cookies.get('Admin') == 'true':
    show_admin_panel()
```

Since this reads directly from the client-supplied cookie with no cross-reference to a server-side session record, the attacker fully controls the outcome.

## Remediation

- Store role/privilege in the server-side session (e.g. the session record in the database), keyed by the session token.
- Never read authorization decisions from cookies, hidden fields, or any other client-supplied value.
- The session token itself should be an opaque random string — the server looks up the user's role from it, never from additional client-sent values.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-03-role-request-parameter/solve.py)

Logs in as `wiener`, then sets `Admin=true` cookie and deletes `carlos`.

## Key Takeaways

- Client-supplied values (cookies, hidden fields, URL params) must never carry authorization decisions.
- Privilege must be derived from a server-side session record, not from what the client sends.
- Cookie manipulation is trivial — any tool that intercepts HTTP can modify it.
