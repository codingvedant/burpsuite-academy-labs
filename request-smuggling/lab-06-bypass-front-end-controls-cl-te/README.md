# Lab 6: Exploiting HTTP request smuggling to bypass front-end security controls (CL.TE)

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te)

## Overview

The front-end blocks external access to `/admin`. The back-end allows the admin panel only if `Host: localhost`. Smuggling bypasses both: the front-end never inspects the smuggled bytes, and the smuggled request can set any Host it wants on the back-end side. Smuggle a `GET /admin/delete?username=carlos` with `Host: localhost` → carlos is removed → lab solved.

## Key Concepts

- **Front-end access controls are layer-7 inspection** — they only see what the front-end parses. Smuggled bytes bypass them entirely.
- **Back-end trust of internal markers** (`Host: localhost`, `X-Forwarded-For: 127.0.0.1`, `X-Internal: true`) assumes those markers can't be forged. Smuggling lets the attacker forge any header the back-end reads.
- **Smuggled `Content-Length`** on the inner request makes pipelining predictable — the back-end eats a known number of bytes from the next real request as the smuggled body.
- **This is the first lab with real impact** — not a parser error, not a 404 probe, but an actual destructive admin action.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Body hex view → ends with `30 0D 0A 0D 0A` after the final `0`.

## Solution

Send twice:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 139
Transfer-Encoding: chunked

0

GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=
```

Second response triggers the smuggled delete → carlos removed → lab solved.

## How the Bypass Works

**Front-end (CL: 139):** reads 139 bytes of body, sees `POST /` on the outside, forwards. Never inspects anything smuggled, so `/admin` block doesn't apply.

**Back-end (TE):** stops at `0\r\n\r\n` after 5 body bytes. The full `GET /admin/delete?...` request with `Host: localhost` parks in the socket buffer.

**Second request arrives:** back-end parses the leftover as a new request. Smuggled `Content-Length: 10` with body `x=` consumes 8 more bytes from the second request's start as the smuggled body — predictable termination.

Back-end processes `GET /admin/delete?username=carlos` with `Host: localhost` → trusts the host → executes the delete.

## Byte Count (139)

```
0\r\n                                               = 3
\r\n                                                = 2
GET /admin/delete?username=carlos HTTP/1.1\r\n      = 44
Host: localhost\r\n                                 = 17
Content-Type: application/x-www-form-urlencoded\r\n = 49
Content-Length: 10\r\n                              = 20
\r\n                                                = 2
x=                                                  = 2
----
total                                               = 139
```

## Why `Host: localhost` Matters

The back-end admin check is `if (request.host == "localhost") allow();`. External requests normally arrive with `Host: lab-id.web-security-academy.net`, which fails the check. A smuggled request lets us set any Host we want on the back-end side — the front-end never inspects or rewrites it. `Host: localhost` → check passes → admin executes.

This is the broader pattern: **internal-trust markers are only safe if they can't be injected cross-origin**. Request smuggling makes them injectable.

## Why `Content-Length: 10` on the Smuggled Request

Same reason as Labs 4-5: it makes pipelining predictable. The smuggled request eats 10 body bytes before considering itself complete; `x=` is 2 bytes parked, back-end reads 8 more from the next incoming request's start to finish, then moves on cleanly. Without this, the back-end might parse the next request from an unpredictable offset and the delete might not fire reliably.

## Why It Worked

- Layered defence: front-end has access control, back-end has internal-only trust.
- Both assumptions assume **the only requests the back-end sees are ones the front-end approved**. Smuggling violates that invariant.
- The front-end can't inspect what it doesn't parse; the back-end can't tell "forged Host from a smuggled request" from "legitimate internal traffic."

## Real-World Equivalents

Same pattern applies to:

- **Path-based WAF rules** — "block anything to `/admin`" → smuggle → bypass.
- **IP allow-lists at the front-end** — "only office IPs can POST to `/wire-transfer`" → smuggle → bypass.
- **Rate limiting / bot detection** — smuggled requests fly under the counters.
- **Authentication at the proxy** — "require JWT for `/api/*`" → smuggle → bypass.

## Remediation

- Reject requests with both `Content-Length` and `Transfer-Encoding` at the edge.
- Perform access control at the back-end, not just the front-end — defence in depth.
- Don't trust `Host: localhost` or similar internal markers for authorization. Use authenticated internal mTLS or signed internal tokens.
- Normalize headers at the front-end before forwarding.
- Use HTTP/2 end-to-end.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-06-bypass-front-end-controls-cl-te/solve.py)

Raw TLS sockets. Script asserts the body is exactly 139 bytes before sending.

## Key Takeaways

- **Smuggling = front-end bypass** for any layer-7 rule the back-end doesn't duplicate. WAFs, access control, rate limits, auth gateways.
- **Internal-trust markers (`Host: localhost`, internal IPs, etc.) are forgeable via smuggling.** Don't rely on them for authorization.
- **Give the smuggled request its own `Content-Length`** to make pipelining deterministic.
- **This is the first "real" smuggling impact** — all later labs in the category build on this bypass + payload shape.
