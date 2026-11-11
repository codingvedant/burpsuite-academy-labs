# Lab 1: Unprotected Admin Functionality

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Unprotected admin functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality)

## Overview

The admin panel is accessible to anyone who knows the URL — no authentication or authorization check is applied. The path is leaked via `robots.txt`, which developers added to prevent search engine indexing but inadvertently published the location to anyone who looks.

## Key Concepts

- **Vertical access control failure:** a privileged function (admin panel) has no server-side access check — any user reaching the URL can use it.
- **Security through obscurity:** relying on a URL being unknown is not access control. `robots.txt` actively advertises "hidden" paths.
- **robots.txt as recon:** `Disallow:` entries name paths the site owner wants search engines to skip — attackers read these to find admin panels, staging URLs, and internal tools.

## Solution

### Step 1 — Read robots.txt

Navigate to:
```
https://LAB-ID.web-security-academy.net/robots.txt
```

You'll see something like:
```
User-agent: *
Disallow: /administrator-panel
```

### Step 2 — Browse to the admin panel

```
https://LAB-ID.web-security-academy.net/administrator-panel
```

No login prompt — you're in.

### Step 3 — Delete carlos

Click **Delete** next to the user `carlos`. Lab solved.

## How It Works

The server has no middleware or route guard checking whether the authenticated user has admin privileges before serving `/administrator-panel`. Any HTTP request to that path gets a 200 response with the full admin UI.

## Remediation

- Enforce access control server-side on every admin route — return 403 for non-admin sessions.
- Never rely on URL secrecy as a protection mechanism.
- Avoid listing sensitive paths in `robots.txt`; use a sitemap for indexable content instead.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-01-unprotected-admin/solve.py)

Fetches `robots.txt`, extracts the admin path, and deletes `carlos` automatically.

## Key Takeaways

- `robots.txt` is public — anything in `Disallow:` is a recon gift to attackers.
- Access control must be enforced server-side on every request; no URL is "secret" at scale.
- This is the most basic vertical privilege escalation: zero authorization check on an admin endpoint.
