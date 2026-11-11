# Lab 2: Unprotected Admin Functionality with Unpredictable URL

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [Unprotected admin functionality with unpredictable URL](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality-with-unpredictable-url)

## Overview

Same failure as Lab 1 — no server-side auth check on the admin panel — but the path is "unpredictable" (a random-looking string) rather than `/administrator-panel`. The path is hardcoded in the page's JavaScript, visible to anyone who reads the source.

## Key Concepts

- **Security through obscurity is not access control.** A "secret" URL embedded in client-side code is public — the browser downloads that JS and anyone can read it.
- **Client-side code is always attacker-visible:** HTML source, inline scripts, external JS files, and even minified/obfuscated bundles can all be read by an attacker with a browser.
- **Vertical privilege escalation:** admin path accessible with zero authorization check regardless of who's logged in.

## Solution

### Step 1 — View the page source

Open the lab homepage and press **Ctrl+U** (or right-click → View Page Source). Search for `admin`:

```js
var isAdmin = false;
if (isAdmin) {
   var adminPanelTag = document.createElement('a');
   adminPanelTag.setAttribute('href', '/admin-abc123');
   ...
}
```

The admin path (`/admin-abc123` or similar) is right there in the JS.

### Step 2 — Navigate directly to the admin path

```
https://LAB-ID.web-security-academy.net/admin-abc123
```

No login prompt — full admin UI loads.

### Step 3 — Delete carlos

Click **Delete** next to `carlos`. Lab solved.

## How It Works

The JS conditionally shows the admin link only if `isAdmin === true`, hiding it from normal users in the UI. But the URL is still in the source regardless of that condition, and the server has no access control on the route. The "unpredictable" string is theatre — the server never checks who's making the request.

## Why "Unpredictable" Isn't a Defense

- JS is downloaded by every browser — the string is in every visitor's cache.
- Automated scanners (Burp Spider, dirbusters) extract all URLs from JS.
- Minification and obfuscation slow a human down by minutes; they don't stop tooling.

## Remediation

- Server-side session check on every admin route — 403 for non-admin.
- Never treat client-side code as a secrets store.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-02-unpredictable-url/solve.py)

Fetches the homepage, extracts the admin path from JS with a regex, then deletes `carlos`.

## Key Takeaways

- Client-side code is always readable — hardcoded paths, tokens, and flags are all public.
- "Unpredictable" does not mean "secret" when the value is in the page source.
- Access control must live on the server, not in JS conditionals that hide UI elements.
