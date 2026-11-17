# Lab 9: URL Normalization

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [URL normalization](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-normalization)

## Overview

The cache normalises URLs (URL-decodes percent-encoded characters) before computing the cache key, but the backend reflects the raw encoded path in 404 error pages. By injecting an XSS payload as a URL-encoded path, the poisoned 404 response gets cached and served when the victim visits the encoded URL — triggering the XSS via the normalised cache hit.

## Key Concepts

- **URL normalisation:** the cache decodes percent-encoded characters before keying, so `%3Cscript%3E` and `<script>` map to the same cache entry.
- **Backend reflection of raw path:** the 404 error page reflects the path as received — including angle brackets when the backend doesn't decode before reflecting.
- **Victim-targeted delivery:** unlike previous labs that poison `/`, this poisons a specific crafted URL. The exploit server delivers the encoded link to the victim.
- **Normalisation discrepancy:** cache and backend handle encoding differently — the cache normalises while the backend reflects raw bytes, creating a mismatch that enables the attack.

## Solution

### Step 1 — Find the reflection sink

`GET /anythingthatdoesntexist` returns a 404 with the path reflected in the error message:
```html
<p>Not Found: /anythingthatdoesntexist</p>
```

### Step 2 — Inject XSS via URL-encoded path

```
GET /random%3Cscript%3Ealert(1)%3C/script%3E HTTP/1.1
```

The cache normalises this to `/random<script>alert(1)</script>` for the cache key.  
The backend reflects the decoded path into the 404 page, producing:
```html
<p>Not Found: /random<script>alert(1)</script></p>
```

### Step 3 — Poison the cache

Send the encoded request until `X-Cache: hit`.

### Step 4 — Deliver to victim

Host an exploit page that redirects the victim to the encoded URL:
```html
<script>location='https://<lab>/random%3Cscript%3Ealert(1)%3C/script%3E'</script>
```

When the victim's browser requests that URL, the cache serves the poisoned 404 response (matched via normalised key), firing `alert(1)`. Lab solved.

## Why this is different from previous labs

Previous labs poison a high-traffic URL (`/`, `/js/geolocate.js`) so any visitor triggers it passively. This lab requires active delivery — you must send the victim the specific encoded URL. The normalisation is what allows the cache hit: the victim's browser sends the encoded URL, the cache normalises it to match your poisoned entry.

## Remediation

- Apply consistent URL normalisation at both the cache and backend before comparing paths.
- Encode output before reflecting URL paths in error pages.
- Do not cache 404 responses for user-controlled paths, or strip path content from the cache key.

## Key Takeaways

- Cache/backend normalisation mismatches are a subtle but powerful vector — same content, different representations.
- 404 pages that reflect the path are XSS sinks commonly overlooked in security reviews.
- This attack requires victim delivery (exploit server) rather than passive poisoning of a shared resource.
