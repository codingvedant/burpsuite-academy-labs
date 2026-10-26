# Lab 4: DOM-based open redirection

**Category:** DOM-based Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [DOM-based open redirection](https://portswigger.net/web-security/dom-based/open-redirection/lab-dom-open-redirection)

## Overview

Each blog post page has a "Back to Blog" link whose `onclick` handler regex-matches `url=https?://...` out of `location` and assigns the captured string to `location.href`. The regex restricts the scheme but doesn't check host or origin — any absolute URL is accepted. Visiting the lab with `?url=https://attacker/` and clicking the link navigates the victim to the attacker's domain.

## Key Concepts

- **Open redirect:** a page that redirects to a user-controlled URL with no host/origin validation.
- **DOM-based:** the redirect decision happens entirely in client-side JS. The server never sees the destination, so server-side filters are irrelevant.
- **Phishing primitive:** the attacker-shared link lives on the trusted origin — the redirect only fires after the browser has already navigated there. Also commonly chained into OAuth / SSO token theft.
- **Scheme check ≠ URL validation.** `https?://` matches *any* `http(s)` URL — including the attacker's.

## Finding It With DOM Invader

1. Burp embedded browser → DOM Invader on, **Redirection sinks** enabled.
2. Load any post page, click "Back to Blog" while watching the Sinks tab.
3. See `location.href =` fire with a stack trace pointing at the inline `onclick`. Trace the source back to `location` (via the regex) → confirmed open redirect.

## Solution

Just open this URL (no exploit server needed):

```
https://LAB-ID.web-security-academy.net/post?postId=4&url=https://EXPLOIT-ID.exploit-server.net/
```

Click **"Back to Blog"**. The onclick regex captures `https://EXPLOIT-ID.exploit-server.net/`, assigns it to `location.href`, browser navigates away, lab solved.

## Payload Breakdown

Vulnerable JS (roughly):

```javascript
const returnUrl = /url=(https?:\/\/.+)/.exec(location);
if (returnUrl) location.href = returnUrl[1];
else location.href = "/";
```

| Fragment | Role |
|----------|------|
| `location` | Source — the full current URL as a string. Attacker controls everything after the origin via the query string. |
| `/url=(https?:\/\/.+)/` | Regex that only restricts scheme; no host check. |
| `location.href = returnUrl[1]` | Sink — navigates to whatever matched. |

Attacker-controlled fragment of the URL: `&url=https://EXPLOIT-ID.exploit-server.net/` — the regex captures `https://EXPLOIT-ID.exploit-server.net/`.

## Why It Worked

The developer treated "URL has `https://` in it" as proof it's safe. In practice that lets through any attacker domain. The handler never asked the actual question — "is this URL on *our* origin?" — which is the only check that matters for a return-URL feature.

## Remediation

- **Parse before trusting:** `const parsed = new URL(candidate, location.origin); if (parsed.origin !== location.origin) reject();`
- **Allow-list, not deny-list:** prefer "same origin only" or an explicit set of allowed redirect destinations.
- **Use relative paths server-side.** If the feature is "return to a page on this site", send a path (`/post/42`) not a full URL — then there's nothing to validate.
- **Never allow `javascript:` or `data:` schemes** on any navigation sink. Even an open-redirect fix should hard-reject these.

## Key Takeaways

- Any client-side navigation driven by a URL parameter (`returnUrl`, `next`, `redirect`, `continue`, `url`) is an open-redirect candidate — audit first, exploit second.
- Scheme restrictions aren't host restrictions. `https?://` matches any attacker domain.
- Open redirects on their own are low severity (phishing); chained with OAuth or token flows they become critical.
- The correct check is "same origin as this page", using the URL parser — not regex, not substring matching.
