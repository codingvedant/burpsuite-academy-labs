# Lab 7: User ID Controlled by Request Parameter with Data Leakage in Redirect

**Category:** Access Control Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [User ID controlled by request parameter with data leakage in redirect](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect)

## Overview

The app attempts to block unauthorized account access by redirecting non-owners away. However, the server renders the full account page first and includes it in the 302 response body before issuing the redirect. The browser discards this body and follows the redirect, but Burp captures the full response — including the API key.

## Key Concepts

- **Redirect ≠ access control:** a 302 response with a `Location` header still sends a response body. Only the browser auto-follows the redirect; any HTTP client or proxy sees the full response.
- **Data in redirect body:** the server renders the page, calls `redirect()`, but doesn't stop the template from being included in the response body.
- **Burp as a tool to read redirect bodies:** browsers follow 302s automatically. Burp Repeater shows you the raw response before any redirection, exposing what the browser would skip.

## Solution

### Step 1 — Log in

Credentials: `wiener` / `peter`.

### Step 2 — Send the IDOR request in Burp Repeater

```
GET /my-account?id=carlos HTTP/1.1
Host: LAB-ID.web-security-academy.net
Cookie: session=YOUR-SESSION-COOKIE
```

### Step 3 — Read the 302 response body

The response is a redirect (`302 Found`, `Location: /login`) but the body contains the rendered account page:
```html
...Your API Key is: <span>XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX</span>...
```

### Step 4 — Submit the API key

Submit the key from the response body. Lab solved.

## How It Works

Server-side logic like this causes the leak:
```python
if account.owner != session.user:
    return redirect('/login')   # redirect is queued...
render_template('account.html', account=account)  # ...but body is sent anyway
```

Depending on the framework, the body of the render may be sent as part of the redirect response rather than being suppressed.

## Why Browsers Hide This

Browsers automatically follow 3xx redirects and discard the redirect response body entirely. This means the vulnerability is invisible in normal browser use — only visible via a tool that shows raw HTTP responses (Burp, curl, etc.).

## Remediation

- Use `return redirect(...)` as the last statement and ensure nothing else runs after it, or use `abort(403)` before any rendering.
- Frameworks that support it: use `before_request` guards or middleware that short-circuits before the view function runs.
- Never render sensitive data before performing the access check.

## Python Script

[solve.py on GitHub](https://github.com/codingvedant/burpsuite-academy-labs/blob/main/access-control/lab-07-userid-redirect-leak/solve.py)

Logs in, sends the IDOR request with `allow_redirects=False`, reads the API key from the 302 body, and submits it.

## Key Takeaways

- A redirect response body is still delivered to the client — only browsers discard it automatically.
- Access checks must happen **before** any data is rendered, not as an afterthought that issues a redirect after the fact.
- Burp Repeater / `allow_redirects=False` in `requests` are the tools to see redirect bodies.
