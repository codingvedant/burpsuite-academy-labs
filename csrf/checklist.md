# CSRF Testing Checklist

## Recon

1. **Find a state-changing action worth forging** - change email, change password, transfer funds, update settings
2. **Check how the request is authorized** - if it rides only on a session cookie the browser sends automatically, it is a CSRF candidate
3. **Identify the defense in place** - is there a CSRF token, a SameSite cookie attribute, a Referer check, or nothing at all?
4. **Generate a baseline PoC** - Burp: right-click the request > Engagement tools > Generate CSRF PoC

## Exploitation path - by defense

```
What protects the state-changing request?
|
+-- Nothing
|   +-- Auto-submitting form posts the action (Lab 1)
|
+-- A CSRF token
|   +-- Only checked on POST?        -> resend as GET, add _method if needed (Lab 2)
|   +-- Only checked if present?     -> delete the whole csrf parameter (Lab 3)
|   +-- Not tied to the session?     -> use a valid token from your own account (Lab 4)
|   +-- Tied to a non-session cookie?-> inject your csrfKey cookie, then send matching token (Lab 5)
|   +-- Duplicated in a cookie?      -> inject any csrf cookie, submit the same value in body (Lab 6)
|
+-- SameSite cookie
|   +-- Lax + method override        -> GET navigation with _method=POST (Lab 7)
|   +-- Strict + client-side redirect-> bounce through an on-site JS redirect (Lab 8)
|   +-- Strict + sibling subdomain   -> XSS on a same-site sibling launches the request (Lab 9)
|   +-- Lax via cookie refresh       -> silently refresh the cookie through OAuth (Lab 10)
|
+-- Referer validation
    +-- Only checked if present?     -> suppress it with <meta name=referrer content=no-referrer> (Lab 11)
    +-- Loose substring match?       -> put the target domain in your query string + unsafe-url (Lab 12)
```

## Cookie injection helper (Labs 5, 6)

When a token/key is tied to a cookie, look for an endpoint that reflects input into `Set-Cookie` (often the search feature) and inject via CRLF:

```
/?search=x%0d%0aSet-Cookie:%20csrfKey=VALUE%3b%20SameSite=None
```

Sequence the cookie set before the form post with `<img src="...cookie-inject..." onerror="submitForm()">`.

## SameSite quick reference

| Attribute | Cookie sent on... |
|-----------|-------------------|
| `Strict` | same-site requests only (no cross-site at all) |
| `Lax` (Chrome default) | same-site + top-level cross-site GET navigations |
| `None` | all requests (needs `Secure`) |

## Tools & automation

**Burp tools**
- Generate CSRF PoC (Engagement tools) - builds the base auto-submitting form
- Repeater - confirm the flaw first (tamper the token, change method, forge/strip the Referer) before building the PoC
- Exploit server - Store the HTML, "View exploit" to test on yourself, "Deliver to victim" to solve

**Scripts / exploits**
- Every lab has an `exploit.html` (the PoC hosted on the exploit server)
- lab-01 also has a `solve.py` that drives the exploit server's store + deliver API (what the "Deliver to victim" button does) - the reusable pattern for scripting any of these
- Python cannot BE the cross-site victim browser, so these are delivered from the exploit server, not fully automated

## Tips

- Validation must fail closed: a missing token, missing Referer, or wrong method should be rejected, not skipped
- A GET form rebuilds the query string from its inputs - put values in `<input>` fields, not the action URL
- `SameSite=Strict` isolates by site, not origin - a sibling subdomain (or an on-site redirect) is same-site
- Test on yourself with "View exploit" before delivering; check the exploit server access log for exfil-style attacks
- Labs 9 (WebSockets/CSWSH) and 10 (OAuth) depend on other topics
