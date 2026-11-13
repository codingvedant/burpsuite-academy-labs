# Lab 4: Targeted Web Cache Poisoning Using an Unknown Header

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Targeted web cache poisoning using an unknown header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-targeted-using-an-unknown-header)

## Overview

The unkeyed header is not well-known — it must be discovered with Param Miner. The cache also uses `Vary: User-Agent`, meaning separate cache entries are stored per User-Agent. To hit the victim, the poisoned entry must be created with the victim's exact User-Agent, which is first leaked via a comment that lures the victim's browser to the exploit server.

## Key Concepts

- **Unknown unkeyed header:** not `X-Forwarded-Host` but something like `X-Host` — discovered via Param Miner header guessing.
- **`Vary: User-Agent`:** the cache keys on User-Agent as well as URL. Generic poisoning (with your own UA) only affects users with your same UA. Must match the victim's.
- **User-Agent leakage via comment:** posting a comment with a link to the exploit server causes the victim's browser to request it, logging their UA in the exploit server access logs.

## Solution

### Step 1 — Discover the unkeyed header

Right-click request in Burp → Extensions → Param Miner → "Guess headers". Param Miner finds a header (e.g., `X-Host`) whose value reflects in the response:
```html
<script src="//HEADER_VALUE/resources/js/tracking.js"></script>
```

### Step 2 — Confirm `Vary: User-Agent`

Check the response headers. `Vary: User-Agent` confirms each User-Agent gets its own cache entry.

### Step 3 — Leak the victim's User-Agent

Post a comment on a blog post with `website` set to the exploit server URL. When the victim views the post and their browser fetches the link preview, the exploit server access log captures their `User-Agent`.

### Step 4 — Host malicious script

Create `/resources/js/tracking.js` on the exploit server:
```javascript
alert(document.cookie)
```

### Step 5 — Poison the cache for the victim's User-Agent

Send `GET /` with:
- The discovered unkeyed header pointing to your exploit server
- `User-Agent` set to the victim's UA (copied from exploit server logs)

Repeat until `X-Cache: hit`.

### Step 6 — Verify

When the victim visits the home page, their UA matches the poisoned cache entry. They load your script. Lab solved.

## Remediation

- Audit all custom headers for reflection in responses; include any that influence output in the cache key.
- Be cautious with `Vary` — a broad `Vary: User-Agent` can create an enormous number of cache variations that are individually poisonable.
- Sanitise all user-controllable input before reflecting it into HTML or JS.

## Key Takeaways

- Param Miner is essential for finding non-obvious unkeyed headers — manual testing misses them.
- `Vary: User-Agent` is not a security control; it just changes which users are affected by which poisoned entry.
- Leaking the victim's UA before poisoning is a two-step targeted attack pattern unique to `Vary`-restricted caches.
