# Lab 8: SameSite Strict bypass via client-side redirect

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The session cookie is `SameSite=Strict`, so it is never sent on any cross-site request.

## Background: SameSite Strict

`SameSite=Strict` sends the cookie on **no** cross-site request at all - GET or POST. The Lab 7 method-override trick does not help. The only way to attach the cookie is to make the final request originate from **within the site itself**.

## The gadget: client-side redirect

The comment confirmation page `/post/comment/confirmation?postId=X` runs JavaScript that builds a redirect path from the `postId` value and navigates there. Because that navigation is issued by the app's own page, it is same-site - so the Strict cookie is attached.

## Exploit

Send the victim to the confirmation page, but inject path traversal into `postId` so the JS redirect lands on the change-email endpoint.

```html
<script>
  document.location = "https://LAB-ID.web-security-academy.net/post/comment/confirmation?postId=1/../../my-account/change-email?email=attacker%40evil.com%26submit=1";
</script>
```

## URL breakdown

- `/post/comment/confirmation?postId=...` - hits the client-side redirect gadget
- `1/../../my-account/change-email` - the postId value; `../../` traverses out of `/post/comment/` so the redirect path resolves to `/my-account/change-email`
- `email=attacker%40evil.com` - `%40` is the encoded `@`
- `%26submit=1` - the `&` is encoded so `submit=1` stays inside the postId value rather than becoming a separate parameter of the confirmation URL

## Why it works

`document.location` sends the victim to the confirmation page. The app's own JavaScript then redirects to change-email. That second request is same-site, so the Strict session cookie is attached and the email changes.

## Takeaway

SameSite=Strict blocks cross-site requests, but a client-side redirect inside the app is a laundering gadget: the attacker triggers a same-site navigation that carries the Strict cookie. Redirect targets built from user input (path traversal here) turn that gadget into a CSRF primitive.
