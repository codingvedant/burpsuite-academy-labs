# Lab 7: Parameter Cloaking

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Parameter cloaking](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-parameter-cloaking)

## Overview

The cache and the backend parse query strings differently. The cache strips the unkeyed `utm_content` parameter entirely. The backend uses `;` as a parameter separator within parameter values. By smuggling a second `callback=alert(1)` inside the `utm_content` value using a semicolon, the backend sees two `callback` parameters — last value wins — and returns a poisoned JSONP response cached under the legitimate callback key.

## Key Concepts

- **Parameter cloaking:** hide a parameter from the cache by embedding it inside an unkeyed parameter's value using a delimiter the cache ignores but the backend parses (`;`).
- **Semicolon parsing (Ruby/Rack):** some frameworks treat `;` as a query string separator, so `utm_content=foo;callback=bar` → `utm_content=foo` AND `callback=bar`.
- **Duplicate parameter last-value-wins:** when two `callback` values exist, the backend uses the last one (`alert(1)`), while the cache keys on the first (`setCountryCookie`).
- **JSONP callback injection:** the callback parameter is reflected directly into the response body as a function name: `alert(1)({"countryCode":"..."})`.

## Solution

### Step 1 — Find the JSONP endpoint

`GET /js/geolocate.js?callback=setCountryCookie` returns:
```javascript
setCountryCookie({"countryCode":"XX", ...})
```
The callback value is reflected unsanitised.

### Step 2 — Confirm `utm_content` is unkeyed

From Lab 6: `utm_content` is excluded from the cache key.

### Step 3 — Cloak the payload inside `utm_content`

```
GET /js/geolocate.js?callback=setCountryCookie&utm_content=foo;callback=alert(1) HTTP/1.1
```

**Cache sees:** `?callback=setCountryCookie` (strips `utm_content`) → keys on this.  
**Backend sees:** `utm_content=foo`, then `;callback=alert(1)` as a second parameter. Last `callback` wins → returns `alert(1)({"countryCode":"..."})`.

### Step 4 — Poison the cache

Send until `X-Cache: hit`. The poisoned response is now stored under `?callback=setCountryCookie`.

### Step 5 — Verify

Visit the home page — it imports `/js/geolocate.js?callback=setCountryCookie`, gets the poisoned entry, fires `alert(1)`. Lab solved.

## Why This Variant Works Better

An alternative approach is `?callback=setCountryCookie;utm_content=alert(1)//` — the semicolon comes after the callback value. But this is less reliable because the cache might not recognise `utm_content` when it appears as part of another parameter's value. The working variant places the smuggled `callback` inside `utm_content`'s value, ensuring the cache strips `utm_content` normally while the backend sees the second `callback`.

## Remediation

- Normalise query strings before caching — apply the same parser the backend uses.
- Do not exclude parameters from cache keys if their values can influence the response.
- Sanitise JSONP callback values: allow only `[a-zA-Z0-9_]`.

## Key Takeaways

- Parameter cloaking exploits parser inconsistency between cache and backend, not a reflection bug alone.
- Semicolons as parameter separators (Ruby/Rack, some PHP configs) are a classic cloaking enabler.
- JSONP endpoints are high-value targets because the callback is always reflected into executable JS.
