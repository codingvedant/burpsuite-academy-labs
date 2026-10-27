# Lab 4: Confirming a CL.TE vulnerability via differential responses

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [HTTP request smuggling, confirming a CL.TE vulnerability via differential responses](https://portswigger.net/web-security/request-smuggling/finding/lab-confirming-cl-te-via-differential-responses)

## Overview

Labs 1–3 relied on a lab-specific `Unrecognized method GPOST` error to confirm desync. Real targets rarely surface a parser error — you need a technique that works regardless. The move: smuggle a complete-looking `GET /404` request as a prefix. The next request on the connection gets routed to `/404`, and the second response is `404` — a **differential response** that confirms smuggling even in production.

## Key Concepts

- **Differential-response confirmation:** send two identical requests; if the second comes back with a status/content that disagrees with the first, something between the two parsed differently → desync.
- **Smuggle a GET-to-known-path.** `/404` gives a stable, obvious response code; `/admin`, `/robots.txt`, etc. generalize to real targets.
- **The dangling `X-Ignore:` trick.** Ending the smuggled payload mid-header lets the smuggled request *absorb the next incoming request* cleanly instead of colliding with it on the back-end.
- **Byte count is exact.** The CL must match the smuggled portion precisely — one byte off and either the front-end rejects or the back-end doesn't park the smuggled bytes correctly.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Confirm the body hex ends correctly (details below).

## Solution

Send twice over the same connection:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 35
Transfer-Encoding: chunked

0

GET /404 HTTP/1.1
X-Ignore: X
```

Body (exactly 35 bytes): `0\r\n\r\nGET /404 HTTP/1.1\r\nX-Ignore: X`.

**Second response: `404 Not Found` → lab solved.**

## How the Desync Works

**Front-end (CL: 35):** reads 35 bytes, forwards everything.

**Back-end (TE: chunked):** stops at `0\r\n\r\n` after reading 5 body bytes. The remaining 30 bytes (`GET /404 HTTP/1.1\r\nX-Ignore: X`) sit in the socket buffer as the start of the next request. Note: the smuggled portion ends mid-header — the `X-Ignore` header has no terminating `\r\n`.

**Second request arrives:** `POST / HTTP/1.1\r\n...`. The back-end concatenates it with the open header value:

```
GET /404 HTTP/1.1
X-Ignore: XPOST / HTTP/1.1   ← 'X' + 'POST / HTTP/1.1' merged into one header value
Host: LAB-ID.web-security-academy.net
Content-Type: ...
(etc.)
```

Back-end sees one combined request: `GET /404` with the second request's headers absorbed. Responds `404`.

## Why `X-Ignore: X` With No Trailing Newline

Without the dangling header, the smuggled request would terminate at `GET /404 HTTP/1.1\r\n\r\n` and the back-end would try to parse the second request independently — producing response-pipelining confusion that often fails. The dangling header:

1. **Absorbs the next request's request-line** into itself as a bogus header value.
2. **Keeps the whole shape parseable** — second request's other headers slot in as additional headers on the combined request.
3. **Ends headers naturally** — the second request's own `\r\n\r\n` terminates the combined request cleanly.

## Byte Count

```
0\r\n        = 3 bytes
\r\n         = 2 bytes
GET /404 HTTP/1.1\r\n  = 19 bytes
X-Ignore: X  = 11 bytes
total        = 35 bytes
```

## Why It Worked

Same CL.TE primitive as Lab 1. The novelty is in confirmation, not exploitation: build the smuggled prefix as a *complete, valid request to a different path* instead of a single byte. The back-end routes it as a real request, and the resulting response code is attacker-observable proof of desync.

## Beyond This Lab

The differential-response technique is the standard **confirmation** step in a real-world smuggling workflow:

1. Probe with CL+TE or obfuscated headers to see if a desync is possible.
2. Confirm by smuggling a known-path request and watching for the differential response.
3. Only then move to exploitation (control bypass, session theft, cache poisoning).

PortSwigger's **HTTP Request Smuggler** BApp automates step 1; this technique is step 2.

## Remediation

- Reject requests with both `Content-Length` and `Transfer-Encoding` at the edge.
- Terminate back-end connections on parse errors.
- Normalize headers before forwarding.
- Use HTTP/2 end-to-end.
- Monitor for anomalous response codes (unexpected 404s or redirects on common paths) as a smuggling IOC.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-04-confirming-cl-te-differential/solve.py)

Raw TLS sockets. Script asserts the body is exactly 35 bytes before sending.

## Key Takeaways

- **Differential responses confirm smuggling without a lab-only parser error.** `/404` or any known-path smuggled request gives attacker-observable proof.
- **Dangling `X-Ignore:` absorbs the next request** cleanly — a reusable gadget for turning two separate requests into one combined one on the back-end.
- **Byte-exact counting still matters.** 35 bytes, no more, no less.
- **This is the real-world confirmation step.** Fundamentals (Labs 1-3) prove the concept; differential responses prove the bug in production.
