# Lab 10: Exploiting HTTP request smuggling to deliver reflected XSS

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to deliver reflected XSS](https://portswigger.net/web-security/request-smuggling/exploiting/lab-deliver-reflected-xss)

## Overview

The blog post page reflects the `User-Agent` header into a hidden input in the comment form (reflected XSS). Normally the attacker can't modify a victim's User-Agent — but a smuggled request with a malicious User-Agent gets paired with the victim's socket on the back-end. The response (containing the attacker's reflected XSS) gets routed to the victim's browser, firing `alert(1)` in a user who never visited the attacker's URL.

## Key Concepts

- **Smuggling reroutes responses, not just requests.** The front-end pairs back-end responses with whichever client's request is next in the queue. A smuggled request's response can land on a different user's connection.
- **Reflected XSS in headers the client doesn't control** (`User-Agent`, `Referer`, `Accept-Language`) becomes a stored-XSS-grade primitive when smuggling is possible.
- **No "stored" anywhere.** The payload lives only in-flight on one back-end socket. No persistence, no database write.
- **CL.TE smuggle delivers one shot** per poisoned connection — the response goes to the first user whose request lands.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Body hex view → ends with `30 0D 0A 0D 0A` (`0 \r \n \r \n`) after the chunked `0`.

## Solution

Send once:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 150
Transfer-Encoding: chunked

0

GET /post?postId=5 HTTP/1.1
User-Agent: a"/><script>alert(1)</script>
Content-Type: application/x-www-form-urlencoded
Content-Length: 5

x=1
```

Wait 30-60s, reload the lab home page, check for the "Congratulations" banner. Resend once if nothing after 1-2 minutes. Don't spam.

## How the Attack Chains

**Front-end (CL: 150):** reads 150 bytes, forwards.

**Back-end (TE):** stops at `0\r\n\r\n` after 5 body bytes. The complete smuggled `GET /post?postId=5` with the malicious `User-Agent` parks in the socket buffer.

**Victim admin's request arrives** on the shared back-end connection. Back-end processes the parked smuggled request *first*:

1. Reads `GET /post?postId=5 HTTP/1.1` with attacker's `User-Agent: a"/><script>alert(1)</script>`.
2. Smuggled request needs 5 body bytes (`CL: 5`). Reads them from the start of the victim's request (eats `x=1` + 2 bytes of real request).
3. Processes the smuggled GET → returns the blog post HTML with the attacker's User-Agent reflected into the hidden input.

**Response relay:** the front-end has the back-end's response and the admin's request slot pending. It pairs them. Admin's browser receives the blog post HTML containing:

```html
<input ... value="a"/><script>alert(1)</script>">
```

Browser parses, breaks out of `value=""`, fires `<script>alert(1)</script>` → lab solved.

## Byte Count (150)

```
0\r\n                                               = 3
\r\n                                                = 2
GET /post?postId=5 HTTP/1.1\r\n                     = 29
User-Agent: a"/><script>alert(1)</script>\r\n       = 43
Content-Type: application/x-www-form-urlencoded\r\n = 49
Content-Length: 5\r\n                               = 19
\r\n                                                = 2
x=1                                                 = 3
----
                                                      150
```

## Debugging Encountered

- **Extra space on the chunked `0` line (`0 \r\n`)** → back-end rejected the body terminator → HTTP 400 "Invalid request." Deleted the trailing space.
- **Missing blank line between `0` and the smuggled GET** → the chunked body never terminated → back-end treated the smuggled HTTP as a malformed trailer header → HTTP 400. Added the blank line.
- **Content-Length drifted from 150** every time the body changed — always recount after any edit. Final body: exactly 150 bytes.

## Why the Response Goes to the Victim

HTTP is strict request-response pairing. The back-end doesn't know which client originated which request on a shared connection — it just serves responses in order. The front-end has a queue of client requests waiting for responses; when the back-end sends a response, the front-end hands it to the next waiting client.

The attacker's smuggled request has no attacker-side response slot (the attacker's own request got its response already). The next slot belongs to the admin. So the back-end's response to the smuggled request gets handed to the admin.

**This is the critical mechanism of request smuggling as an attack:** it doesn't just inject requests, it reroutes responses to unrelated users.

## Why It Worked

- The site has a legitimate reflected XSS in a client-set header, which the developer presumably considered low-impact ("the client controls their own browser, they'd only hurt themselves").
- CL.TE smuggling turns that self-only XSS into a cross-user XSS by letting the attacker set the User-Agent on behalf of someone else.
- Combined impact: self-XSS primitive + smuggling delivery → full session-cookie-stealing XSS against any user whose traffic shares the connection.

## Remediation

- Fix the reflected XSS: HTML-encode `User-Agent` (and any header) on output.
- Reject requests with both `Content-Length` and `Transfer-Encoding`.
- Use HTTP/2 end-to-end.
- Content-Security-Policy with no `unsafe-inline` would also stop the alert in this specific case.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-10-deliver-reflected-xss/solve.py)

Raw TLS sockets. Script sends the smuggle once; actual victim-browser response is delivered by PortSwigger's lab infrastructure asynchronously.

## Key Takeaways

- **Smuggling reroutes responses to unrelated users.** This is the mechanism that turns in-request-only XSS into cross-user attacks.
- **Any reflected XSS in a client-controlled header** becomes a cross-user primitive when smuggling exists. User-Agent is the common target; Referer, Accept-Language, custom tracking headers all qualify.
- **No persistence required for stored-XSS-grade impact.** The payload lives only in one in-flight back-end socket.
- **Patience over volume.** One well-formed smuggle + wait beats ten rapid sends — rapid sends fill the poisoned buffer with your own next request.
- **Byte-perfect still rules.** A single trailing space on the chunked `0` line produces HTTP 400 and no attack.
