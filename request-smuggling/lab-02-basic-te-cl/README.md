# Lab 2: HTTP request smuggling, basic TE.CL vulnerability

**Category:** HTTP Request Smuggling
**Difficulty:** Apprentice
**Lab link:** [HTTP request smuggling, basic TE.CL vulnerability](https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl)

## Overview

Mirror image of Lab 1. The front-end honours `Transfer-Encoding`; the back-end honours `Content-Length`. The front-end greedily consumes a whole chunk and forwards it; the back-end stops short at `Content-Length` bytes, leaving the chunk contents — an entire valid HTTP request — in its socket buffer. The next request on the connection gets prefixed with that smuggled request, producing a `GPOST` method error.

## Key Concepts

- **TE.CL:** Front-end TE, back-end CL. Smuggled bytes live *inside* a chunk, not after the chunked terminator.
- **Chunk-size byte count must be exact.** The hex chunk size (`5c` = 92) is the byte count of the smuggled request text through the end of its body. One wrong byte and the front-end TE parser fails.
- **Smuggled payload is a full request.** Unlike Lab 1's single-byte prefix, TE.CL lets you smuggle any method/path/headers/body — the primitive the later labs build on.
- **Chunked body termination:** `0\r\n\r\n`. The *trailing blank line after `0` is mandatory* — the front-end TE parser waits for it before considering the body complete.

## Burp Setup

- Repeater → Inspector → Request attributes → HTTP/1.
- Repeater menu → uncheck **Update Content-Length** (auto-fix would rewrite the deliberately-short CL).
- Verify the body in the Inspector's hex view: last five bytes must be `30 0D 0A 0D 0A` (`0 \r \n \r \n`).

## Solution

Send this twice over the same connection:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

Second response: `Unrecognized method GPOST` → lab solved.

## How the Desync Works

Body on the wire:

```
5c\r\n
GPOST / HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 15\r\n\r\nx=1\r\n
0\r\n
\r\n
```

**Front-end (TE):** reads chunk size `5c` (92 decimal), consumes exactly 92 bytes of chunk data (`GPOST / HTTP/1.1\r\n...x=1`), reads `\r\n`, reads next chunk size `0` → body complete. Forwards everything.

**Back-end (CL: 4):** reads 4 bytes of body = `5c\r\n`. Treats the request as done. The remaining `GPOST / HTTP/1.1\r\n...x=1\r\n0\r\n\r\n` sits in its socket buffer.

**Next request on connection:** back-end parses the leftover as a new request:
```
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
<empty line>
x=1<pad from the next real request's bytes>
```

`GPOST` isn't a valid method → `Unrecognized method GPOST`.

## Common Gotchas (encountered during the solve)

- **Content-Length auto-corrected to `101`** by Burp's "Update Content-Length" setting. Must be unchecked for smuggling to work — the whole exploit depends on a deliberately-wrong CL.
- **"Read timeout" (HTTP 400) from the front-end:** means the chunked body wasn't terminated. The final `0` *must* be followed by a blank line. If Burp strips trailing CRLFs on paste, add them back manually.
- **Chunk size must match the smuggled request bytes exactly.** `5c` works only if the smuggled portion through `x=1` is 92 bytes. Any change (adding/removing headers, hostname length, etc.) requires recalculating.

## Why It Worked

Same fundamentals as Lab 1 — two servers disagree about which header defines body length, and connection reuse lets leftover bytes become someone else's request. The difference is directionality: TE.CL smuggles *inside* a chunk, not after it, which lets the attacker shape a full request as the leftover.

## Remediation

Same as Lab 1:
- Reject requests with both `Content-Length` and `Transfer-Encoding`.
- Terminate the back-end connection on parse errors.
- Use HTTP/2 end-to-end.
- Match front-end and back-end parser implementations.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-02-basic-te-cl/solve.py)

Raw TLS sockets — `requests` would normalize the headers and break the exploit.

## Key Takeaways

- **TE.CL smuggles a full request.** The leftover in the back-end buffer is a complete HTTP request shape — any method, any path, any body. All the "steal cookies / bypass controls / deliver XSS" labs build on this primitive.
- **Chunk sizes are byte-exact.** `5c` = 92 bytes. Count twice before sending.
- **Chunked bodies need trailing CRLF after `0`.** No blank line = read timeout = Burp returns 400 before anything smuggles.
- **Burp's auto-fix is enemy #1 for smuggling.** Any auto-correction of lengths or chunk sizes kills the exploit. Verify in the Inspector's hex view.
