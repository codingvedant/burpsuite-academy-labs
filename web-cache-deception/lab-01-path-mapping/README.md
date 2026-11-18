# Lab 1: Exploiting Path Mapping for Web Cache Deception

**Category:** Web Cache Deception
**Difficulty:** Apprentice
**Lab link:** [Exploiting path mapping for web cache deception](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-mapping)

## Overview

The cache and the origin server map URL paths differently. The origin server ignores extra path segments after `/my-account`, always returning the authenticated account page. The cache treats any path ending in a static extension (`.js`, `.css`) as a static file and caches it. Appending a fake `.js` segment makes the cache store a private, per-user authenticated response — which an attacker can then fetch unauthenticated.

## Key Concepts

- **Web cache deception vs. cache poisoning:** Deception tricks the cache into storing a *victim's private response* so the attacker can read it. Poisoning injects malicious content into a cached response to attack visitors.
- **Path mapping discrepancy:** Backend ignores extra path segments; cache keys on the full path including extension — the mismatch is the vulnerability.
- **Static extension heuristic:** Many caches assume `.js`/`.css`/`.png` paths are static and cacheable, even when served by a dynamic endpoint.

## Solution

### Step 1 — Confirm path mapping discrepancy

Send `GET /my-account/abc.js` while logged in as `wiener`. The backend ignores `/abc.js` and returns the account page. Check cache headers:
- First send → `X-Cache: miss`
- Second send within 30s → `X-Cache: hit`

This confirms the cache stores the response based on the `.js` extension.

### Step 2 — Craft exploit

On the exploit server, set the body to:
```html
<script>document.location="https://<lab>/my-account/wcd.js"</script>
```
Use a fresh path (`wcd.js`) so the victim doesn't receive your earlier cached response.

### Step 3 — Deliver to victim

Click "Deliver exploit to victim". Carlos visits the exploit page, his browser requests `/my-account/wcd.js` while authenticated → the cache stores his account page response under that URL.

### Step 4 — Retrieve cached response

Visit `https://<lab>/my-account/wcd.js` in your browser (or unauthenticated in Repeater). The cache serves Carlos's account page containing his API key.

### Step 5 — Submit

Copy the API key from the response and submit the solution.

## Remediation

- Do not cache responses to URLs with arbitrary path suffixes — validate that the full path maps to a known static resource.
- Apply `Cache-Control: no-store` or `private` to all authenticated responses.
- Use explicit cache rules based on content type rather than URL extension heuristics.

## Key Takeaways

- Web cache deception requires the cache to be more eager to cache than the backend expects.
- The attacker doesn't need to modify the response — they just need the cache to store it and serve it back.
- Use a unique path per exploit delivery so you don't accidentally serve your own cached response to the victim.
