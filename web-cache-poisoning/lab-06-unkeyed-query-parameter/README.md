# Lab 6: Web Cache Poisoning via an Unkeyed Query Parameter

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning via an unkeyed query parameter](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-param)

## Overview

Unlike Lab 5 where the entire query string is unkeyed, here only a specific parameter is excluded from the cache key (typically an analytics/tracking param like `utm_content`). Other parameters remain keyed. Param Miner identifies the unkeyed parameter, whose value is reflected in the response and can be used to inject an XSS payload.

## Key Concepts

- **Selective unkeyed parameter:** the cache excludes specific known tracking parameters (e.g., `utm_*`) from the cache key while keeping others. Only the excluded ones are poison vectors.
- **Param Miner:** discovers which parameters are unkeyed by testing each one and comparing cache behaviour.
- **Same sink, different discovery:** once the unkeyed param is found, the injection technique is identical to Lab 5 — reflected value → XSS in canonical link or script tag.

## Solution

### Step 1 — Discover the unkeyed parameter

Run Param Miner → "Guess query params" on `GET /`. It identifies a parameter (e.g., `utm_content`) that shares the same cache entry as `GET /` regardless of its value.

### Step 2 — Confirm it's unkeyed

Send `GET /?utm_content=foo` and `GET /?utm_content=bar`. Both get `X-Cache: hit` for the same entry. Send `GET /?other=foo` — this creates a new cache entry (keyed parameter).

### Step 3 — Find the reflection

The `utm_content` value reflects in the response (e.g., in `<link rel="canonical">`):
```html
<link rel="canonical" href="https://lab/?utm_content=foo"/>
```

### Step 4 — Inject the payload

```
GET /?utm_content='/><script>alert(1)</script>
```

### Step 5 — Poison the cache

Send until `X-Cache: hit`.

### Step 6 — Verify

Visit `/` without the parameter — `alert(1)` fires for all visitors. Lab solved.

## Remediation

- Do not exclude user-controllable parameters from cache keys unless they are strictly non-functional.
- If tracking params must be excluded, strip them from the response before caching (don't reflect them).
- Use `Vary` to properly scope cache entries.

## Key Takeaways

- Not all query params are unkeyed — Param Miner is essential to identify which specific ones are excluded.
- Tracking/analytics parameters (`utm_*`, `fbclid`, etc.) are commonly excluded from cache keys by CDN configs, making them frequent targets.
- The injection technique is the same as an unkeyed query string; the challenge is finding the right parameter.
