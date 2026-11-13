# Lab 3: Web Cache Poisoning with Multiple Headers

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning with multiple headers](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-multiple-headers)

## Overview

No single unkeyed header is sufficient here. The app uses `X-Forwarded-Scheme` to detect the protocol and `X-Forwarded-Host` to build URLs. Using both together causes the app to serve a script import pointing to an attacker-controlled host, which gets cached and served to all visitors.

## Key Concepts

- **Multi-header dependency:** neither header alone produces a useful reflection. `X-Forwarded-Scheme: http` triggers a protocol redirect; `X-Forwarded-Host` controls where that redirect points. Combined, they redirect the script resource URL to the exploit server.
- **Resource poisoning vs page poisoning:** instead of poisoning the home page response directly, poison a JS resource (`/resources/js/tracking.js`) whose URL is reflected in the home page's script import.

## Solution

### Step 1 — Test headers individually

- `X-Forwarded-Scheme: http` → 302 redirect (but to the same host)
- `X-Forwarded-Host: exploit-server` alone → no useful change
- Both together → redirect or script src points to `https://exploit-server/resources/js/tracking.js`

### Step 2 — Identify the poisonable resource

The home page imports:
```html
<script src="https://exploit-server/resources/js/tracking.js"></script>
```
(when both headers are present)

### Step 3 — Host the malicious script

On the exploit server, create `/resources/js/tracking.js`:
```javascript
alert(document.cookie)
```

### Step 4 — Poison the cache

Send `GET /resources/js/tracking.js` (or `GET /`) with both headers:
```
X-Forwarded-Host: <exploit-server-host>
X-Forwarded-Scheme: http
```
Repeat until `X-Cache: hit`.

### Step 5 — Verify

Visit the home page without the headers. The cached response loads your script. Lab solved.

## Remediation

- Treat any header combination that influences response URLs as a cache poisoning risk.
- Strip or validate `X-Forwarded-*` headers at the edge before they reach the application.
- Include all headers that influence the response in the cache key, or use `Vary`.

## Key Takeaways

- Some poisoning vectors only appear when multiple headers are combined — always test pairs.
- Poisoning a JS resource is as effective as poisoning the page itself; every page that imports it is affected.
- Protocol-downgrade headers (`X-Forwarded-Scheme: http`) combined with host headers are a classic multi-header vector.
