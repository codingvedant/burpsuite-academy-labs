# Lab 13: Response queue poisoning via H2.TE request smuggling

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [Response queue poisoning via H2.TE request smuggling](https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning/lab-request-smuggling-h2-response-queue-poisoning-via-te-request-smuggling)

## Overview

Front-end speaks HTTP/2 and uses frame length for body boundaries; back-end speaks HTTP/1 and still honours a smuggled `Transfer-Encoding: chunked`. Classic desync — but we smuggle a **complete** request instead of a prefix. The back-end sends two responses for one outer request; the front-end only expected one, so the extra response poisons the back-end's response queue. From that point every subsequent client gets someone else's response. When the admin logs in on this connection, their `302 Set-Cookie: session=ADMIN` reply gets handed to us instead of them. We steal the session and delete carlos.

## Key Concepts

- **HTTP/2 downgrade smuggling (H2.TE):** HTTP/2 is immune end-to-end, but downgrade to HTTP/1 at the back-end re-introduces length ambiguity. Front-end uses frame length, back-end uses the preserved `Transfer-Encoding: chunked` header.
- **Response queue poisoning** goes beyond request injection — it **desynchronizes the response queue** so every subsequent client gets another client's response.
- **Smuggle a complete request, not a prefix.** Two requests in, two responses out, front-end only expected one → off-by-one queue state.
- **Victim's post-login response contains the session cookie.** Reading it = full session hijack.

## Burp Setup

- Repeater → Inspector → Request Attributes → **HTTP/2**.
- Repeater menu → uncheck **Update Content-Length**.

## Solution

### Step 1 — Poison the queue

```
POST /x HTTP/2
Host: LAB-ID.web-security-academy.net
Transfer-Encoding: chunked

0

GET /x HTTP/1.1
Host: LAB-ID.web-security-academy.net


```

Send once. Response: 404 (expected). The second queued 404 sits in the back-end's response queue.

### Step 2 — Capture a victim response

Wait ~5s. Send:

```
GET / HTTP/2
Host: LAB-ID.web-security-academy.net
```

Possible outcomes:
- **404** — got the extra queued 404. Resend.
- **200** — off-by-one got consumed elsewhere. Re-poison from Step 1.
- **302 Set-Cookie: session=…** — admin's post-login response. **Copy the cookie.**

Admin logs in every ~15s. Keep resending until the 302 arrives.

### Step 3 — Delete carlos with stolen session

```
GET /admin/delete?username=carlos HTTP/2
Host: LAB-ID.web-security-academy.net
Cookie: session=ADMIN-SESSION-TOKEN
```

Send → carlos deleted → lab solved.

## How Response Queue Poisoning Works

**Smuggle request:** outer `POST /x` carries a smuggled complete `GET /x`.
- Front-end (HTTP/2): parses body via frames. Sends to back-end as HTTP/1 with the `Transfer-Encoding: chunked` header preserved.
- Back-end (HTTP/1): honours TE. Reads chunks. Sees `0\r\n\r\n` → first request done. Treats the smuggled `GET /x HTTP/1.1\r\nHost: ...\r\n\r\n` as a complete second request.
- Back-end processes both requests, sends two 404 responses.

**Front-end state:**
- Request queue (what the front-end sent): `[POST /x]` — just one.
- Response queue (what the back-end sent back): `[404 for POST /x, 404 for GET /x]` — two.
- Front-end hands you the first 404 for your `POST /x`. The second 404 is **extra**.
- The back-end's response pipeline is now off by one: every future response is one ahead of its matching request.

**When admin logs in:**
- Admin's `POST /login` arrives on the connection.
- Back-end processes it, returns `302 Set-Cookie: session=ADMIN`.
- Front-end has: queued extra 404, plus the new admin 302.
- Front-end pairs the admin's `POST /login` request → with the queued 404 (handing admin the wrong response).
- Admin's 302 Set-Cookie now sits in the queue, waiting for the next client's request.

**We send `GET /`:**
- Front-end pairs it with the admin's 302 Set-Cookie response.
- We receive the admin's session cookie in a response to our innocent GET.

## Why `/x` as the Path

- Our own responses are predictable 404s.
- Any non-404 response is **someone else's data** — easy to spot.
- Any 200 we see is almost certainly a response meant for the admin.

## Why `\r\n\r\n` After `Host:` on the Smuggled Request

The smuggled request must be *complete* to produce a response. Headers must terminate with a blank line, otherwise the back-end waits for more input and the queue poisoning doesn't fire.

## Why Connection Resets Every 10 Requests

The back-end connection pool cycles connections after a fixed number of requests. If you've been playing around, send a few normal requests to reset state, then re-poison from Step 1. Spamming without re-poisoning won't produce admin responses.

## Why This Is Different From All Prior Labs

| Previous Labs | This Lab |
|---|---|
| HTTP/1 CL vs TE desync | HTTP/2 frame vs HTTP/1 TE desync |
| Smuggle a prefix (byte or partial request) | Smuggle a complete request |
| Attacker reads attacker's response | Attacker reads **another user's** response |
| Byte-exact chunk sizes required | HTTP/2 handles framing — only need TE header |
| Impact: one injected request | Impact: queue stays poisoned indefinitely |

## Why It Worked

- Front-end accepts HTTP/2 requests with a `Transfer-Encoding: chunked` header and blindly includes that header when downgrading to HTTP/1 for the back-end.
- Back-end honours the TE header, parses the smuggled chunked body independently of the HTTP/2 frame boundaries the front-end used.
- Front-end's response pairing uses connection-level request/response ordering, not any per-stream HTTP/2 identifier — so a smuggled extra response desynchronizes the queue.

## Remediation

- **Strip `Transfer-Encoding` from HTTP/2 requests at the front-end** before downgrading to HTTP/1 — HTTP/2 doesn't use TE, so any TE header is attacker-provided.
- **Reject HTTP/2 requests with `Transfer-Encoding` or `Content-Length` headers that disagree with the HTTP/2 frame length.** RFC 9113 §8.1.1 actually requires rejection.
- **Use HTTP/2 end-to-end** so no downgrade step exists.
- **Terminate the back-end connection on any protocol violation** instead of reusing it.
- **Validate response count against request count** per connection — an extra response should flush the pipeline.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-13-h2te-response-queue-poisoning/solve.py)

HTTP/2 over raw TLS using `httpx` or `hyper-h2` (annotated — automation is nontrivial because we need HTTP/2 framing but a tolerant TE header). Script poisons the queue, polls for admin's 302, uses the stolen cookie.

## Key Takeaways

- **HTTP/2 downgrade is where "immune to smuggling" becomes false.** End-to-end HTTP/2 is safe; downgrade re-introduces every HTTP/1 smuggling bug class.
- **Smuggling a complete request = response queue poisoning**, not just one-shot injection. Every subsequent client affected until the queue drains or the connection resets.
- **`/x` as the smuggled target** is a smart primitive — predictable attacker responses make non-attacker responses obvious to spot.
- **Session cookies travel in response headers** (Set-Cookie). Reading another user's response = session hijack.
- **The fix lives at the front-end's HTTP/2 → HTTP/1 translator.** It must strip TE and CL headers that HTTP/2 clients provided, since HTTP/2 doesn't use them for framing.
