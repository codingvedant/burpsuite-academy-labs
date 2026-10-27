# Lab 3: HTTP request smuggling, obfuscating the TE header

**Category:** HTTP Request Smuggling
**Difficulty:** Practitioner
**Lab link:** [HTTP request smuggling, obfuscating the TE header](https://portswigger.net/web-security/request-smuggling/lab-obfuscating-te-header)

## Overview

Both servers **support** `Transfer-Encoding: chunked`. The attack sends two conflicting `Transfer-Encoding` headers — one with a valid value (`chunked`), one with a bogus value (`cow`). The front-end and back-end resolve the duplicate differently; one picks `chunked` and parses chunks, the other picks `cow`, doesn't recognize it, and silently falls back to `Content-Length`. Same TE.CL desync as Lab 2 — different root cause.

## Key Concepts

- **TE.TE variant:** both ends support TE, but one is tricked into ignoring it. The disagreement is *parser-level*, not *capability-level*.
- **Spec ambiguity around duplicate headers.** RFC 7230 is loose about which value wins when the same header appears multiple times — implementations vary.
- **Fallback-on-unknown-encoding.** When a server sees `Transfer-Encoding: cow`, strict spec compliance says return 400; most real servers silently fall back to CL.
- **Common TE obfuscations** (any one may trigger a desync against a given stack):
  - `Transfer-Encoding : chunked` (space before colon)
  - `Transfer-Encoding:\tchunked` (tab after colon)
  - `Transfer-Encoding: xchunked` (prefix on value)
  - `Transfer-Encoding: chunked ` (trailing space)
  - Duplicate headers with different values ← this lab

## Burp Setup

- Repeater → Inspector → Request attributes → HTTP/1.
- Repeater menu → uncheck **Update Content-Length**.
- Inspector hex view → confirm body ends with `30 0D 0A 0D 0A`.

## Solution

Send twice over the same connection:

```http
POST / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked
Transfer-encoding: cow

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

Second response: `Unrecognized method GPOST` → lab solved.

## How the Desync Works

- **Front-end:** picks the first `Transfer-Encoding: chunked`. Reads chunks, consumes 92 bytes of chunk data, sees the `0` terminator, forwards everything.
- **Back-end:** picks the second `Transfer-encoding: cow`. Doesn't recognize `cow` as a valid transfer encoding, falls back to `Content-Length: 4`. Reads 4 bytes = `5c\r\n`. Leaves the smuggled `GPOST ...` request in its socket buffer.
- **Second request:** back-end parses the leftover as a new request → `GPOST` method → error.

Direction here is TE (front) + CL-fallback (back), i.e. TE.CL — same primitive as Lab 2, reached via header-parsing confusion rather than native CL vs TE differences.

## Why Case Doesn't Matter

The case difference between `Transfer-Encoding` and `Transfer-encoding` is not what makes this work — HTTP header names are case-insensitive per spec. The real trick is the **duplicate header with an unknown value**. Any pair of same-named headers where the values differ, and one is unrecognizable, is a candidate.

## Why It Worked

- RFC 7230 §3.3.3 says if `Transfer-Encoding` is present, `Content-Length` must be ignored.
- The spec also says unrecognized transfer-encoding values must trigger `400 Bad Request`.
- Real implementations violate both rules routinely — they tolerate ambiguity to avoid breaking live traffic.
- That tolerance is the attack surface.

## Beyond This Lab

Every reverse proxy, CDN, and app server has its own set of header-parsing quirks. PortSwigger's **HTTP Request Smuggler** BApp automates probing ~10 TE obfuscations in parallel and reports which (if any) produce a desync. That's how real-world request smuggling bugs get discovered.

## Remediation

- Reject requests with any duplicate `Transfer-Encoding` or `Content-Length` header.
- Reject requests with unrecognized `Transfer-Encoding` values with 400 (don't fall back to CL).
- Normalize headers at the front-end before forwarding (one canonical pair of length headers per request).
- Use HTTP/2 end-to-end.
- Match front-end and back-end parser libraries.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-03-obfuscating-te-header/solve.py)

Raw TLS sockets. The script sends the exact byte sequence including the obfuscated duplicate header.

## Key Takeaways

- **TE.TE = TE on both ends + an obfuscation that breaks one of them.** Patches for native CL/TE differences don't prevent it.
- **Duplicate conflicting headers are a universal smuggling probe.** Any header spec-ambiguous enough to accept duplicates is a candidate.
- **Fallback-on-unknown is where the bug lives.** Strict rejection would stop every obfuscation attack.
- **HTTP Request Smuggler BApp** should be in your workflow for any new target — it tries the ~10 known obfuscations automatically.
