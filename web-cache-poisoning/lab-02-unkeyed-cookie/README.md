# Lab 2: Web Cache Poisoning with an Unkeyed Cookie

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning with an unkeyed cookie](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-cookie)

## Overview

The `fehost` cookie value is reflected inside a JavaScript object literal in the response body, but cookies are excluded from the cache key. By injecting a payload that breaks out of the JS string, the poisoned response gets cached and executes for every visitor — no exploit server required.

## Key Concepts

- **Unkeyed cookie:** caches typically strip `Cookie` headers from cache keys to avoid storing session-specific responses. Any cookie value that influences the response body is therefore an unkeyed input.
- **JS string injection:** the cookie value lands inside a quoted string in a `<script>` block. Breaking out of the string with `"-payload-"` turns a reflection into XSS.
- **No exploit server needed:** because the payload is injected directly into the JS, no external resource load is required.

## Solution

### Step 1 — Find the reflection

Send `GET /`. In the response, the `fehost` cookie is reflected inside a script block:
```javascript
data = {"host":"COOKIE_VALUE","path":"/"}
```

### Step 2 — Build the payload

Set the cookie to break out of the string:
```
fehost=somehost"-alert(1)-"
```

Injected result:
```javascript
data = {"host":"somehost"-alert(1)-"","path":"/"}
```

### Step 3 — Confirm it fires

Send the request with the payload cookie. Confirm `alert(1)` executes in the response.

### Step 4 — Poison the cache

Keep sending the same request until the response header shows `X-Cache: hit`. The poisoned response is now cached.

### Step 5 — Verify

Visit `/` in a clean browser (no modified cookie). The cached response fires `alert(1)`. Lab solved.

## Remediation

- Include relevant cookies in the cache key, or strip them before the response is cached.
- Never reflect cookie values into JavaScript without encoding/sanitisation.
- Use `Vary: Cookie` to prevent cookie values from being shared across different users' cached responses.

## Key Takeaways

- Cookies are almost always excluded from cache keys by default — any cookie reflected in the response is a likely poison vector.
- JS string context injection (`"-payload-"`) requires no external server.
- The attack is persistent: every user served the cached response is affected until the cache expires.
