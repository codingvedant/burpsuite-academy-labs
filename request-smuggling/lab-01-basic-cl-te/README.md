# Lab 1: HTTP request smuggling, basic CL.TE vulnerability

**Category:** HTTP Request Smuggling
**Difficulty:** Apprentice
**Lab link:** [HTTP request smuggling, basic CL.TE vulnerability](https://portswigger.net/web-security/request-smuggling/lab-basic-cl-te)

## Overview

The front-end honours `Content-Length`; the back-end honours `Transfer-Encoding: chunked`. Sending a request that contains both lets the two servers disagree about where the body ends. The attacker leaves a trailing byte in the back-end's socket buffer; the next request on that connection gets prefixed with it, producing an invalid method (`GPOST`) and the lab's solve condition.

## Key Concepts

- **CL.TE:** Front-end `Content-Length`, back-end `Transfer-Encoding`. The front-end reads the full body (CL bytes); the back-end stops at the terminating `0`-length chunk and leaves anything after it in the socket buffer.
- **Connection reuse is the vulnerability.** Front-end to back-end connections are long-lived and pipeline many users' requests back-to-back. Leftover bytes bleed into the next request.
- **Chunked body format:** `<hex-length>\r\n<data>\r\n...0\r\n\r\n`. A body of exactly `0\r\n\r\n` is a valid, empty chunked body.
- **HTTP/1 required.** The intended solution only works downgraded; HTTP/2 is immune when used end-to-end.

## Burp Setup

- Repeater → Inspector → **Request attributes** → set to HTTP/1.
- Repeater → turn **off** "Update Content-Length" auto-fix (otherwise Burp fixes the deliberate mismatch).
- Send twice on the same tab so the connection is reused.

## Solution

In Repeater, send this request **twice**:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

Body bytes (exactly 6): `0 \r \n \r \n G`.

Second response contains `Unrecognized method GPOST` → lab solved.

## How the Desync Works

Both servers see:
- `Content-Length: 6`
- `Transfer-Encoding: chunked`
- Body: `0\r\n\r\nG` (6 bytes)

**Front-end (CL):** reads 6 bytes, forwards the whole thing — including the trailing `G` — to the back-end.

**Back-end (TE):** parses chunks. First chunk is `0` → body ends. Treats bytes after `0\r\n\r\n` as the *start of the next request*. The `G` sits in the socket buffer.

**Second request:** the next `POST / HTTP/1.1` arrives on the same connection. Back-end concatenates: `GPOST / HTTP/1.1` → unknown method → error → lab solved.

## Why It Worked

Three design decisions had to collide:

1. **HTTP spec allows both CL and TE headers** on the same request. RFC 7230 says TE should win, but implementations have varied for years.
2. **Front-end and back-end are different software** with different parsers. Any disagreement about header precedence creates a desync.
3. **Connections are reused across users.** A leftover byte in the back-end buffer becomes the start of someone else's request.

## Remediation

- **Normalize at the front-end.** Reject any request that has both `Content-Length` and `Transfer-Encoding`, or strip one before forwarding.
- **Use HTTP/2 end-to-end.** HTTP/2 encodes body length in its framing layer, eliminating the CL vs TE ambiguity. Downgrade to HTTP/1 on the back-end re-introduces it.
- **Terminate connections between front-end and back-end** on parse errors instead of reusing them.
- **Keep front-end and back-end on the same parsing library** where possible.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-01-basic-cl-te/solve.py)

Note: smuggling exploits need exact byte-level control. The script uses raw sockets, not `requests`, because `requests` normalises conflicting headers.

## Key Takeaways

- **Two headers that both describe body length = ambiguity = desync.** Any time you see CL + TE on one request, assume smuggling is possible.
- **Smuggling is a byte-perfect exploit.** Trailing whitespace, extra newlines, auto-fixed Content-Length all break it. Use raw sockets or a Burp session that respects your bytes.
- **The smuggled bytes attach to the *next* request on the connection** — your own replay, or a real user's. Impact tiers from parser-error log noise to session theft.
- **HTTP/1 is a landmine.** Modern stacks mostly speak HTTP/2 to clients but downgrade to HTTP/1 internally — which is exactly where smuggling lives.
