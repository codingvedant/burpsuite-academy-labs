# Lab 5: Confirming a TE.CL vulnerability via differential responses

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [HTTP request smuggling, confirming a TE.CL vulnerability via differential responses](https://portswigger.net/web-security/request-smuggling/finding/lab-confirming-te-cl-via-differential-responses)

## Overview

Mirror of Lab 4. Front-end TE, back-end CL. Smuggle a complete `POST /404` inside a chunk; the back-end stops at `CL: 4` and parks the chunk contents in its socket buffer. The next request on the connection gets routed to `/404` and returns a 404 — differential confirmation of the desync.

## Key Concepts

- **TE.CL smuggles inside a chunk** (vs CL.TE smuggling after the terminator). The leftover is a self-contained request shape.
- **`POST /404` with its own `Content-Length: 15`** deliberately consumes some bytes from the following request, giving the back-end's parser a predictable termination point.
- **No dangling header needed** — unlike CL.TE's `X-Ignore: X` trick. The smuggled request is complete and parses cleanly.
- **Chunk size must match exactly** — `5e` = 94 bytes = byte count through `x=1`.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Body hex view → ends with `30 0D 0A 0D 0A`.

## Solution

Send twice:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5e
POST /404 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

Second response: `404 Not Found` → lab solved.

## How the Desync Works

**Front-end (TE):** reads chunk size `5e` (94), consumes 94 bytes of chunk data (the smuggled `POST /404 ... x=1`), reads chunk delimiter, reads `0` terminator → body complete. Forwards.

**Back-end (CL: 4):** reads 4 bytes of body = `5e\r\n`. Request complete. Everything from `POST /404 HTTP/1.1` onwards parks in the socket buffer.

**Second request arrives:** `POST / HTTP/1.1\r\n...`. Back-end parses the leftover as a new request:

```
POST /404 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1<+12 bytes from the second request>
```

Smuggled request has `CL: 15` but only `x=1` (3 bytes) is parked. Back-end reads 12 more bytes from the next incoming request to complete the body, processes it as `POST /404`, responds `404`.

## Byte Count

```
POST /404 HTTP/1.1\r\n                              = 20 bytes
Content-Type: application/x-www-form-urlencoded\r\n = 49 bytes
Content-Length: 15\r\n                              = 20 bytes
\r\n                                                = 2 bytes
x=1                                                 = 3 bytes
----
total                                               = 94 bytes = 0x5e
```

## Lab 4 vs Lab 5

| Dimension | Lab 4 (CL.TE) | Lab 5 (TE.CL) |
|-----------|---------------|---------------|
| Front-end parser | Content-Length | Transfer-Encoding |
| Back-end parser | Transfer-Encoding | Content-Length |
| Smuggled position | After chunked terminator | Inside the chunk |
| Trailing-header trick | `X-Ignore: X` (dangling) | Not needed |
| Smuggled method | `GET /404` | `POST /404` |

## Why `POST` + `CL: 15` Instead of `GET`

The smuggled request's own `Content-Length` tells the back-end how many body bytes to consume from the *next* request before considering the smuggled request complete. That makes the pipelining predictable: back-end finishes the smuggled POST, then starts parsing whatever's left of the second request from a known offset.

A bare `GET` with no body would make the back-end try to parse the second request from arbitrary mid-request bytes — timing-dependent failures. `POST` with a positive CL is the robust shape.

## Why It Worked

Same TE.CL primitive as Lab 2 — only the smuggled method changed. `GPOST` (Lab 2) produced a parser error; `POST /404` (Lab 5) produces a 404. The confirmation technique generalizes beyond the lab environment: any known-path smuggled request produces an attacker-observable differential response on real targets.

## Remediation

- Reject requests with both `Content-Length` and `Transfer-Encoding`.
- Terminate the back-end connection on parse errors instead of reusing it.
- Use HTTP/2 end-to-end.
- Monitor for anomalous response codes on common paths as smuggling IOCs.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-05-confirming-te-cl-differential/solve.py)

Raw TLS sockets. Script asserts the smuggled chunk is exactly 0x5e bytes.

## Key Takeaways

- **Differential responses confirm smuggling in both directions.** CL.TE (Lab 4) and TE.CL (Lab 5) have different payload shapes but the same confirmation principle.
- **TE.CL leftover is self-contained** — a full parseable request. No dangling-header absorption trick needed.
- **Giving the smuggled request its own `Content-Length`** makes the pipelining predictable.
- **Chunk size byte-exactness still matters.** `5e` works only if the smuggled portion is exactly 94 bytes.
