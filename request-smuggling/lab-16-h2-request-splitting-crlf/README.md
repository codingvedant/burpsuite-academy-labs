# Lab 16: HTTP/2 request splitting via CRLF injection

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [HTTP/2 request splitting via CRLF injection](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-splitting-via-crlf-injection)

## Overview

Lab 15's CRLF-injection primitive combined with Lab 13's response queue poisoning. Instead of smuggling a single header, inject a full `\r\n\r\n<request-line>\r\n<headers>` into an HTTP/2 header value. After downgrade, the back-end sees two complete HTTP/1 requests and sends two responses — the front-end only expected one, so the response queue goes off-by-one. The admin's post-login `Set-Cookie` response ends up delivered to the attacker's next request. Use the stolen cookie to delete carlos.

## Key Concepts

- **CRLF injection smuggles arbitrary HTTP/1 content**, not just single headers. Four Shift+Enters build a full second request-line + Host + headers-terminator.
- **Response queue poisoning via request splitting** — same mechanic as Lab 13 (H2.TE), different attack vector (CRLF instead of smuggled TE header).
- **The front-end auto-appends its own `\r\n\r\n`** when downgrading, which completes the smuggled request's headers block for free.
- **`/x` as the path** keeps attacker responses as predictable 404s so victim responses (any non-404) stand out.

## Burp Setup

- Repeater → Inspector → **HTTP/2**.
- Repeater menu → uncheck **Update Content-Length**.
- Change request path to `/x`.

## Direct Steps

### Step 1 — Add the CRLF-split header

Inspector → Request Attributes → Add header:

**Name:** `foo`

**Value** (build in order):
1. Type `bar`
2. **Shift+Enter**
3. **Shift+Enter**
4. Type `GET /x HTTP/1.1`
5. **Shift+Enter**
6. Type `Host: LAB-ID.web-security-academy.net`

Value field should visibly span four lines (second line is empty).

### Step 2 — Poison the queue

Send once. Response: 404.

### Step 3 — Capture admin's post-login response

Wait ~5s. Send `GET / HTTP/2` repeatedly:
- `404` → extra queued response, resend
- `200` → off-by-one consumed, re-poison from Step 2
- `302 Set-Cookie: session=...` → **copy the cookie**

### Step 4 — Exploit

```
GET /admin/delete?username=carlos HTTP/2
Host: LAB-ID.web-security-academy.net
Cookie: session=STOLEN
```

carlos deleted → lab solved.

## How the Split Works

**HTTP/2 wire (one request):** attacker-controlled `foo` header with HPACK-encoded value containing `bar\r\n\r\nGET /x HTTP/1.1\r\nHost: LAB-ID...` as raw bytes.

**Front-end:** sees one opaque header value — no visible HTTP/1 syntax to sanitize.

**Downgrade to HTTP/1:**
```
GET /x HTTP/1.1
Host: LAB-ID...
foo: bar

GET /x HTTP/1.1
Host: LAB-ID...

```

(Front-end auto-appends the final `\r\n\r\n`, completing the smuggled request's headers.)

**Back-end:** two complete HTTP/1 requests. Processes both. Sends two 404 responses.

**Front-end state:**
- Request queue: `[GET /x]` — one.
- Response queue: `[404, 404]` — two.
- Hands first 404 to attacker. Extra 404 sits in queue → pipeline off-by-one.

**Admin logs in:** admin's `POST /login` arrives. Back-end returns `302 Set-Cookie: session=ADMIN`. Front-end pairs admin's request with the queued extra 404 (admin gets wrong response). Admin's 302 waits in queue for next client.

**Attacker sends `GET /`:** front-end pairs it with admin's 302 → attacker receives admin's session cookie.

## Lab 13 vs Lab 15 vs Lab 16

| Dimension | Lab 13 (H2.TE) | Lab 15 (CRLF → H2.TE) | Lab 16 (CRLF Split) |
|---|---|---|---|
| Injection vector | Direct `Transfer-Encoding` header | CRLF-injected TE in header value | CRLF-injected request-line in header value |
| Front-end sanitizer defeat | None needed | Hides TE inside opaque HPACK value | Hides full request inside opaque HPACK value |
| Smuggled payload | Complete HTTP/1 request | TE header + oversized CL POST | Complete HTTP/1 request |
| Exploitation | Response queue poisoning | Capture via oversized CL | Response queue poisoning |
| Impact | Admin session hijack | Admin session hijack | Admin session hijack |

Lab 16 is the "most direct" response queue poisoning technique when top-level TE/CL headers are stripped by the front-end — bypasses both the sanitizer and the downgrade-length validation in one move.

## Why Front-End Auto-Appends `\r\n\r\n`

Standard HTTP/1 downgrade behavior: after writing all headers, write a blank line to signal end-of-headers before any body. If our injected value already ends with `Host: ...`, the auto-appended `\r\n\r\n` perfectly terminates the smuggled request's headers.

## Why It Worked

- Front-end accepts HTTP/2 header values containing CRLF without validation.
- Front-end copies header-value bytes verbatim into HTTP/1 ASCII during downgrade.
- Back-end's HTTP/1 parser sees two complete requests on one connection.
- Front-end's response pairing uses connection-level FIFO ordering — extra response desynchronizes the pipeline.

## Remediation

- **Validate HTTP/2 header values at the front-end.** Reject CRLF, NUL, control characters per RFC 9113 §8.1.1.
- **Normalize headers during downgrade.** Strip anything that isn't a legitimate HTTP/2 pseudo-header or valid header.
- **Use HTTP/2 end-to-end** to eliminate the downgrade step.
- **Validate response count per connection** — a smuggled extra response should flush the pipeline instead of being paired with another client's request.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-16-h2-request-splitting-crlf/solve.py)

Documentation-first — HTTP/2 CRLF injection requires low-level HPACK framing. Manual Burp Inspector + Shift+Enter is the clean path.

## Key Takeaways

- **CRLF injection smuggles complete requests, not just headers.** Four Shift+Enters build the full second request-line + Host + headers-terminator inside one HTTP/2 header value.
- **Response queue poisoning via CRLF split** = Lab 13's impact + Lab 15's bypass primitive.
- **The front-end auto-appending `\r\n\r\n`** means we don't need to inject the trailing terminator ourselves.
- **`/x` as a smuggled target** makes attacker responses predictable (404) so victim responses stand out.
- **Fix lives at the HTTP/2 → HTTP/1 translator.** Every byte of attacker-controlled header values must be validated before downgrade.
