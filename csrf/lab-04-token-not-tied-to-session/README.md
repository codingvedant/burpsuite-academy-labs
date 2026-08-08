# Lab 4: CSRF where token is not tied to user session

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The server validates that the CSRF token is genuine, but never checks that it belongs to the requester's session.

## Exploit

Mint a valid token from your own session and hardcode it into the PoC. When the victim submits, their session cookie rides along but the token is yours - and the server accepts it.

```html
<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com" />
  <input type="hidden" name="csrf" value="ATTACKER_SESSION_TOKEN" />
</form>
<script>document.forms[0].submit();</script>
```

## How I solved it

1. Logged in as wiener and grabbed a valid `csrf` token from the change-email form (without submitting it)
2. Built the PoC with the email plus that token as a hidden field
3. Delivered to the victim - the token belonged to my session, not theirs, but the server accepted it
4. Email changed, lab solved

## Why it works

The token is validated for authenticity (it is a real, well-formed token the app issued) but not for ownership. The server never asks "was this token issued to the session making the request?" So a token from any session - including the attacker's - passes validation.

## Takeaway

A CSRF token must be bound to the session it was issued for. Validating only that a token is real, without checking whose session it belongs to, lets an attacker supply their own valid token in the victim's request.

## Note on automation

Browser/exploit-server driven, but the token must be freshly minted from a logged-in attacker session (tokens can expire), so this one is generated fresh rather than fully hardcoded.
