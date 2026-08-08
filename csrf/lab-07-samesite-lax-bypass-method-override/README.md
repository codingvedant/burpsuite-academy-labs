# Lab 7: SameSite Lax bypass via method override

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The session cookie is `SameSite=Lax`, so a normal cross-site POST will not carry it.

## Background: SameSite Lax

- `SameSite=Lax` (Chrome's default) sends the cookie only on **top-level GET navigations** (clicking a link, `document.location`, a GET form submit) - not on cross-site POSTs or background requests (`img`, `fetch`).
- So a normal POST CSRF form fails: the session cookie is not attached.

## Exploit

Turn the attack into a GET navigation (Lax allows the cookie) and use the server's `_method` override to make it act as a POST.

```html
<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="GET">
  <input type="hidden" name="email" value="attacker@evil.com" />
  <input type="hidden" name="_method" value="POST" />
</form>
<script>document.forms[0].submit();</script>
```

`document.location = ".../change-email?email=...&_method=POST"` works equally well.

## Why it works

Two facts combine:

1. **A GET form submit is a top-level navigation**, which `SameSite=Lax` permits the session cookie on.
2. **The server honours `_method=POST`** in the query string, processing the GET as a POST and running the change-email action.

## Confirming the override

In Repeater, send `GET /my-account/change-email?email=test@example.com&_method=POST` and check the email changes. That proves the override before building the PoC.

## Takeaway

SameSite=Lax is not a complete CSRF defense. Any framework feature that lets a GET be treated as a POST (method override) reopens the exact hole Lax was meant to close, because Lax still sends cookies on top-level GET navigations.
