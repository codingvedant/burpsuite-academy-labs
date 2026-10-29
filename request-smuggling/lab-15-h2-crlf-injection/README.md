# Lab 15: HTTP/2 request smuggling via CRLF injection

**Category:** HTTP Request Smuggling
**Difficulty:** Expert
**Lab link:** [HTTP/2 request smuggling via CRLF injection](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-smuggling-via-crlf-injection)

## Overview

HTTP/2 encodes headers as HPACK binary blobs where `\r\n` has no structural meaning. Injecting a real CRLF inside an HTTP/2 header value smuggles a second HTTP/1 header into the downgraded request. The front-end sees one HTTP/2 header `foo: bar<CRLF> Transfer-Encoding: chunked`; the back-end sees two HTTP/1 headers after downgrade and honors the smuggled TE. Combined with an oversized smuggled `Content-Length`, the victim's next request gets captured as "recent search" text under the attacker's account.

## Key Concepts

- **HTTP/2 CRLF injection** bypasses front-end TE/CL stripping by hiding the dangerous header inside another header's value — the front-end's inspection sees one benign header.
- **HPACK binary encoding** doesn't treat `\r\n` as structural, so no normalization happens unless implementations explicitly validate values (RFC 9113 says they SHOULD; many don't).
- **Smuggled Content-Length oversized** = capture-next-request primitive from Lab 9.
- **Victim capture via reflected "recent search"** = persistent, readable exfiltration channel tied to attacker's own account.

## Burp Setup

- Repeater → Inspector → HTTP/2.
- Repeater menu → uncheck **Update Content-Length**.
- Log in as `wiener:peter`; grab your session cookie from `/my-account`.

## Direct Steps

1. **Inspector → Request Attributes → Add header:**
   - Name: `foo`
   - Value: `bar` + **Shift+Enter** (real CRLF) + ` Transfer-Encoding: chunked`
   - The value field must visibly span two lines. Typing the literal characters `\r\n` does NOT work — only Shift+Enter inserts the real CRLF.

2. **Set the request body to:**
   ```
   0

   POST / HTTP/1.1
   Host: LAB-ID.web-security-academy.net
   Cookie: session=YOUR-SESSION
   Content-Length: 800

   search=x
   ```

3. **Send.** Wait ~15 seconds for the victim's request to land on the connection.

4. **Browser:** reload the lab home page. Scroll to "Recent searches." Look for a captured entry starting with `x` followed by raw HTTP (`POST / HTTP/1.1\nHost: ...\nCookie: session=VICTIM...`).

5. **Copy the victim's `session=` value** from the captured text.

6. **DevTools → Cookies →** replace your session with the victim's. Reload the page.

Lab solved when logged in as victim.

## How the Smuggling Works

**HTTP/2 on the wire:**
- One header `foo` with a value containing a literal CRLF byte sequence.
- HPACK encodes this as length-prefixed bytes; no structural interpretation of `\r\n`.
- Front-end inspects the header as a single opaque value — sees no TE/CL to strip.

**Front-end downgrades to HTTP/1:**
- Writes `foo: bar\r\n Transfer-Encoding: chunked\r\n` into the ASCII request.
- Back-end's HTTP/1 parser sees two headers:
  ```
  foo: bar
   Transfer-Encoding: chunked
  ```
- Leading space on line 2 either folds into the `foo` value OR is accepted as a legitimate header (parser-dependent). Vulnerable parsers accept it.

**Back-end (HTTP/1):**
- Honors `Transfer-Encoding: chunked`. Parses the body as chunks.
- Reads `0\r\n\r\n` → outer request body ends.
- Treats the smuggled `POST / HTTP/1.1 ... Content-Length: 800 ... search=x` as the next request.
- Smuggled POST has 8 bytes of body (`search=x`), waits for 792 more.

**Victim's request arrives** on the shared back-end connection:
- Back-end reads first 792 bytes of victim's request as the smuggled POST's body.
- Smuggled POST now has body: `search=x<+ 792 bytes of victim's HTTP request text>`.
- Back-end processes it with the attacker's cookie, stores the search as "recent search" under the attacker's account.

**Attacker reads their recent searches** → sees the victim's full request text, extracts the session cookie.

## Why the Literal `\r\n` Trick Doesn't Work in the Main Editor

Burp's main request editor shows what's actually in the request. Typing `\r\n` as four ASCII characters sends four ASCII characters — not a CRLF byte pair. The HPACK encoder just encodes those characters verbatim.

The Inspector's header editor is the only place that lets you insert a real `0x0D 0x0A` into a header value via Shift+Enter. The visual appearance (two lines of text, no visible backslashes) is the only confirmation that worked.

## Why This Matters Beyond H2.TE / H2.CL

Front-end defenses commonly strip or normalize top-level `Transfer-Encoding` and `Content-Length` headers on HTTP/2 requests before downgrade — defending against Labs 13-14. CRLF injection **tunnels the dangerous header inside another header's value**, invisible to that normalization. The attacker has effectively bypassed the top-level sanitizer by using HTTP/2's binary encoding as a smuggling layer.

Generalizes to:
- Injecting any HTTP/1 header the back-end honors (not just TE).
- Injecting into HTTP/2 pseudo-headers (`:method`, `:path`, `:authority`) if the front-end doesn't validate them.
- Request splitting (full new request smuggled via CRLF-injected request-line).

## Why It Worked

- Front-end accepts HTTP/2 header values containing CRLF without validation (RFC 9113 §8.1.1 says it SHOULD reject; this one doesn't).
- Front-end copies header value bytes verbatim into HTTP/1 ASCII during downgrade.
- Back-end's HTTP/1 parser treats the CRLF as a header separator.
- Back-end then processes an attacker-controlled `Transfer-Encoding` → H2.TE desync primitive.
- Oversized smuggled `Content-Length` captures the victim's request bytes as form data.

## Remediation

- **Validate HTTP/2 header values at the front-end.** Reject any header value containing CRLF, NUL, or control characters per RFC 9113 §8.1.1.
- **Normalize headers during downgrade.** Strip or reject `Transfer-Encoding`, `Content-Length`, and anything that didn't arrive as a legitimate HTTP/2 pseudo-header.
- **Use HTTP/2 end-to-end** to eliminate the downgrade step entirely.
- **Terminate the back-end connection on parser mismatches** (duplicate CL, unexpected TE, etc.).

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/request-smuggling/lab-15-h2-crlf-injection/solve.py)

Documentation-first — HTTP/2 CRLF injection requires low-level HPACK framing control. Manual Burp Inspector + Shift+Enter is the clean path.

## Key Takeaways

- **HTTP/2 CRLF injection is the generalization of HTTP/2 downgrade bugs.** Tunnels any HTTP/1 header the attacker wants, bypassing top-level front-end sanitizers.
- **`\r\n` as literal text is not the same as real CRLF bytes.** Only Burp Inspector + Shift+Enter inserts the real byte sequence.
- **The leading space on the smuggled header line** is a parser-folding gadget — vulnerable HTTP/1 parsers accept it as a separate header, strict ones fold it. Attackers get both behaviors depending on target.
- **"Recent searches" or any attacker-readable reflection** is a strong exfil channel for captured victim requests.
- **Fix is at the HTTP/2 → HTTP/1 translator.** Edge proxies must validate every byte of attacker-controlled header values before downgrading.
