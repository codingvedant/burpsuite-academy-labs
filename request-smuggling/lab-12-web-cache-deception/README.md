# Lab 12: Exploiting HTTP request smuggling to perform web cache deception

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to perform web cache deception](https://portswigger.net/web-security/request-smuggling/exploiting/lab-perform-web-cache-deception)

## Overview

Inverse of Lab 11. Instead of poisoning the cache with attacker content, we trick the cache into storing the **admin's authenticated `/my-account` response** under a static-URL cache key. The dangling `X-Ignore:` header absorbs the admin's cookies as subsequent headers; the back-end processes `GET /my-account` **as the admin**; the cache stores the response (containing the admin's API key) under whatever static resource the admin was actually fetching. Attacker opens the lab in incognito, pulls the cached static files, grep for `Your API Key`.

## Key Concepts

- **Web cache deception vs poisoning:** poisoning stores attacker content under victim URLs; deception stores **victim data** under attacker-readable URLs.
- **Dangling `X-Ignore:` header** absorbs the admin's full request headers (including `Cookie: session=ADMIN`) as the smuggled request's extended header value, giving the back-end the admin's credentials.
- **Static-URL cache paths** (`/resources/js/*`) are cacheable — binding the admin's dynamic response to one makes it readable by any unauthenticated client.
- **The admin's authenticated response contains their API key.** Submission of that key solves the lab.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.

## Prerequisite

1. Log in as `wiener:peter`.
2. Visit `/my-account` once to confirm the API key format.
3. **Wait 30 seconds** after first opening the lab (gives the simulated admin's session time to establish).

## Solution

Send 3-5 times, spaced ~30s apart:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 42
Transfer-Encoding: chunked

0

GET /my-account HTTP/1.1
X-Ignore: X
```

Byte count (42):
```
0\r\n                                = 3
\r\n                                 = 2
GET /my-account HTTP/1.1\r\n         = 26
X-Ignore: X                          = 11
----
                                       42
```

Between sends, open the lab home page in incognito, let it load all static resources, then search Burp HTTP history for `Your API Key`. The matching cached response is the admin's account page.

Submit the API key to the lab's solution form → lab solved.

## How the Deception Works

**Smuggle:** standard CL.TE shape. Back-end parks `GET /my-account` with `X-Ignore:` header open (no terminator).

**Admin's request arrives** on the connection, e.g. `GET /resources/js/labHeader.js HTTP/1.1\r\nCookie: session=ADMIN...\r\nHost: ...\r\n\r\n`.

**Back-end merges** the parked request with the admin's bytes:

```
GET /my-account HTTP/1.1
X-Ignore: XGET /resources/js/labHeader.js HTTP/1.1
Cookie: session=ADMIN-SESSION
Host: LAB-ID...
(etc.)
```

Back-end sees:
- Method/path: `GET /my-account`
- Header `X-Ignore` value: `XGET /resources/js/labHeader.js HTTP/1.1`
- Header `Cookie`: admin's session
- Processes **`/my-account` as the admin** → response contains their API key.

**Front-end pairing:** admin's request `labHeader.js` was pending in the response queue. The 200 OK response (with the account HTML and API key) gets paired with `labHeader.js` and stored in the cache.

**Attacker reads the cache:** anyone requesting `labHeader.js` now receives the admin's account page HTML.

## Why `X-Ignore:` Dangles

The smuggled request ends mid-header deliberately — no trailing `\r\n` after `X-Ignore: X`. This makes the back-end treat the admin's request-line and headers as a continuation of the `X-Ignore` value plus subsequent headers of a merged request. Specifically:
- Admin's request-line `GET /resources/js/labHeader.js HTTP/1.1` gets eaten as part of the `X-Ignore` value.
- Admin's `Cookie:` header slots in as a real header on the merged request.
- Back-end processes the merged request as `GET /my-account` with admin's cookies.

Same pattern as Lab 4's differential-response probe, now weaponized against authentication.

## Why Submit the Admin's Key, Not Yours

The lab's completion check watches for a key that doesn't belong to `wiener`. Submitting your own API key does nothing. Only the admin's stolen key solves the lab.

## Why It Worked

- `/my-account` has no `Cache-Control: no-store` / `Pragma: no-cache` headers.
- Front-end caches responses based on URL alone — doesn't check that the response's content type or Set-Cookie headers suggest it's user-specific.
- Smuggling binds a user-specific response to a shared cache key.

## Remediation

- **Set `Cache-Control: no-store, private` on all authenticated responses.** Alone this would stop this attack.
- Cache keys should include authentication context (user, cookie) when the response varies by user.
- Reject requests with both `Content-Length` and `Transfer-Encoding`.
- Use HTTP/2 end-to-end.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-12-web-cache-deception/solve.py)

Raw TLS sockets. Sends the smuggle, then polls the lab's static resources looking for `Your API Key` in cached responses.

## Key Takeaways

- **Deception = reverse of poisoning.** Store victim data under attacker-readable cache keys instead of storing attacker content under victim-readable keys.
- **Dangling header gadget** (`X-Ignore: X` with no CRLF) is the same primitive used for differential-response probes — now stealing authenticated responses.
- **`/my-account` + no cache-control = deception primitive.** Any authenticated endpoint without explicit no-cache headers is at risk when cached by a smuggling-vulnerable proxy.
- **Fix is cache-side**, not smuggling-side — mark authenticated responses as uncacheable even if smuggling is possible.
- **Combined with Lab 11's poisoning,** this becomes a full credential-harvesting pipeline at scale.
