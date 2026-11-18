# Lab 6: Exploiting Cache Server Normalization for Web Cache Deception

**Category:** Web Cache Deception
**Difficulty:** Expert
**Lab link:** [Exploiting cache server normalization for web cache deception](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-cache-server-normalization)

## Overview

The cache and origin server normalize URL paths differently. Two discrepancies are chained:

1. **Delimiter discrepancy:** The origin treats `%23` (URL-encoded `#`) as a path delimiter — anything after it is ignored and the origin returns `/my-account`. The cache does **not** treat `%23` as a delimiter — it sees and keys on the full path.

2. **Path normalization discrepancy:** The cache resolves percent-encoded dot-segments (`%2f%2e%2e%2f` = `/../`), applies a caching rule for paths under `/resources`, and stores the response. The origin does **not** decode `%2f`, so it ignores the traversal entirely.

Combining both: `/my-account%23%2f%2e%2e%2fresources` — the origin sees `/my-account` and returns the authenticated account page; the cache resolves the dot-segment, identifies a `/resources` path, and caches the response for all unauthenticated users.

## Key Concepts

- **Delimiter discrepancy:** Different characters act as path terminators for the cache vs. the origin. `%23` (encoded `#`) is treated as a delimiter by the origin but not the cache.
- **Cache normalization:** The cache decodes and resolves `%2f..%2f` (encoded `/../`) before applying caching rules; the origin does not.
- **Static directory rule:** The cache caches responses to paths beginning with `/resources` — the normalization discrepancy makes an arbitrary response appear to come from that path.
- **Cache buster parameter:** Appending `?wcd` ensures a unique cache entry for the victim's response, preventing collision with other cached entries.

## Finding the Delimiter

Use Burp Intruder (Sniper) on:
```
GET /my-account§§abc
```
Load the delimiter list from `/web-security/web-cache-deception/wcd-lab-delimiter-list`. Disable URL-encoding of payloads. Payloads that return a 200 with account data are delimiters the origin recognises. `%23` works; skip bare `#` (browser strips it before it reaches the server).

## Confirming Cache Normalization

Send `/aaa/..%2fresources/anything` twice:
- First: `X-Cache: miss`
- Second: `X-Cache: hit`

This confirms the cache resolves `..%2f` and applies the `/resources` caching rule.

## Exploit URL

```
/my-account%23%2f%2e%2e%2fresources?wcd
```

- **Origin sees:** `/my-account` → returns authenticated account page
- **Cache sees:** path resolves to something under `/resources` → caches it
- **`?wcd`:** unique cache buster

## Solution

### Step 1 — Find the delimiter

Intruder Sniper on `/my-account§§abc` with the lab's delimiter list (URL-encoding off). Confirm `%23` returns 200 with account data.

### Step 2 — Confirm cache normalization

Send `GET /aaa/..%2fresources/anything` twice. Confirm `X-Cache: miss` → `hit`.

### Step 3 — Build and test the exploit URL

Send `GET /my-account%23%2f%2e%2e%2fresources?wcd` while logged in as wiener. Confirm the response contains your account data and shows `X-Cache: hit` on the second send.

### Step 4 — Deliver to victim

On the exploit server:
```html
<script>document.location="https://<lab>/my-account%23%2f%2e%2e%2fresources?wcd"</script>
```
Click "Deliver exploit to victim". Carlos visits, his account page is cached at that URL.

### Step 5 — Retrieve the API key

Visit `https://<lab>/my-account%23%2f%2e%2e%2fresources?wcd` unauthenticated. The cache serves Carlos's account page. Copy the API key and submit.

## Remediation

- Normalize URLs consistently at both cache and origin before keying or processing.
- Apply `Cache-Control: no-store` or `private` to all authenticated responses.
- Do not rely solely on path prefix rules for caching — validate the full normalized path.
- Strip or reject ambiguous delimiter characters (`%23`, `%3f`) at the cache layer.

## Key Takeaways

- Two small discrepancies (delimiter handling + path normalization) chain into a full cache deception attack.
- The attacker doesn't modify the response — just tricks the cache into storing the victim's private response.
- Always test with the delimiter list; different origins treat different characters as terminators.
- `%23` is powerful because browsers strip bare `#` before sending — encoded form bypasses this.
