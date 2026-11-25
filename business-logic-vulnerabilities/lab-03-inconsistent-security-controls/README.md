# Lab: Inconsistent Security Controls

**Category:** Business Logic Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Inconsistent security controls](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-security-controls)

## Overview

The admin panel is restricted to users with a `@dontwannacry.com` email address. While registration requires email confirmation, the app allows users to **change their email after registration without re-verification**. By registering with any email, then changing it to an arbitrary `@dontwannacry.com` address, an attacker gains admin access.

## Key Concepts

- **Inconsistent enforcement:** The initial registration enforces email ownership (confirmation link), but the email change flow does not — creating an inconsistency that defeats the access control.
- **Post-registration privilege escalation:** Access controls based on email domain can be bypassed if the domain isn't re-verified on change.

## Exploit Flow

### Step 1 — Register with exploit server email

Register a new account using your exploit server address:
`attacker@YOUR-EXPLOIT-SERVER.exploit-server.net`

Confirm via the link sent to the exploit server email client.

### Step 2 — Log in

Log in with the new account.

### Step 3 — Change email to dontwannacry.com

In account settings, update email to:
`attacker@dontwannacry.com`

No verification is required — the app updates the email directly.

### Step 4 — Access admin panel and delete carlos

Navigate to `/admin`, delete carlos, and solve the lab.

## Remediation

- Re-verify email ownership whenever a user changes their email address.
- Never grant elevated privileges based solely on the email domain without ongoing verification.
- Treat email change as a sensitive operation: require current password confirmation and send confirmation links to both old and new addresses.

## Key Takeaways

- Security controls must be consistently applied across the full user lifecycle, not just at registration.
- Domain-based access controls are only as strong as the email verification enforcing them.
- Always test whether post-registration data changes (email, username) bypass the original access control checks.
