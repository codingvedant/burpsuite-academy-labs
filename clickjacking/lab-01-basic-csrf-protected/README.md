# Lab 1: Basic clickjacking with CSRF token protection

**Difficulty:** Apprentice

## Goal

Trick the victim into changing their account email through a clickjacking attack. The change-email form is protected by a CSRF token, so a plain auto-submitting CSRF PoC does not work here.

## The key insight

The change-email form carries a valid CSRF token. A normal CSRF attack fails because the attacker cannot guess that token. Clickjacking sidesteps the problem entirely: instead of forging the request, you frame the real page and let the victim's own browser submit it.

Because the iframe loads the genuine `/my-account` page inside the victim's authenticated session, the server hands that page a valid CSRF token. The victim then "clicks" the real Update email button themselves. The token is never something the attacker needs to see or forge, because the legitimate page supplies it.

The email value is prefilled through the `email` query parameter on `/my-account`, so the field is already populated before the victim ever clicks.

## Exploit

A transparent iframe of the target page, layered over a decoy element, hosted on the exploit server (`exploit.html`):

```html
<style>
  iframe { position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }
  div    { position: absolute; top: 495px; left: 60px; z-index: 1; }
</style>
<div>Click me</div>
<iframe src="https://LAB-ID.web-security-academy.net/my-account?email=attacker@evil.com"></iframe>
```

- `opacity: 0.0001` makes the iframe invisible but still clickable.
- `z-index: 2` keeps the invisible iframe on top, so the click lands on the real button rather than the decoy.
- Position the `div` ("Click me") so it sits directly over the Update email button. Use the exploit-server preview to nudge `top`/`left` until they line up.

Store it on the exploit server, click your own decoy in the preview to confirm the alignment, then Deliver to victim.

## Why the CSRF token does not save you

CSRF tokens stop an attacker from *forging* a request. They do nothing against an attack where the *victim* issues the genuine request. Clickjacking is a UI-redressing attack, not a request-forgery attack: the request is 100% legitimate, token and all. The only thing the attacker controls is *where the victim thinks they are clicking*.

## Running the script

`solve.py` drives the exploit server's store + deliver API (what the "Deliver to victim" button does):

```bash
python solve.py https://exploit-XXX.exploit-server.net https://0a...web-security-academy.net
```

Optional `--email` sets the address, and `--top`/`--left` tune the decoy alignment. As with the CSRF labs, Python can upload and deliver the PoC but cannot be the victim browser that performs the click.

## Takeaway

The defence against clickjacking is not a CSRF token, it is telling the browser not to frame your site in the first place: an `X-Frame-Options: DENY` header, or a `Content-Security-Policy: frame-ancestors 'none'` (or `'self'`) directive. If the page cannot be framed, there is nothing to overlay.
