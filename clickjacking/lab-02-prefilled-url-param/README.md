# Lab 2: Clickjacking with form input data prefilled from a URL parameter

**Difficulty:** Apprentice

## Goal

Change the victim's email via clickjacking. Unlike lab 1, the change-email form needs a value entered, so an empty click would submit nothing useful. The form supports prefilling the email field from a URL parameter, so the attacker supplies the value through the iframe `src`.

## The key insight

A clickjack normally just borrows the victim's click. That is not enough when the target action needs *input data* the attacker has to provide. Here the `/my-account` page prefills the email field from an `email` query parameter, so the attacker bakes the value into the framed URL. The field is already populated before the victim clicks, and the single click submits it.

## Exploit

```html
<style>
  iframe { position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }
  div    { position: absolute; top: 500px; left: 80px; z-index: 1; }
</style>
<div>Click me</div>
<iframe src="https://LAB-ID.web-security-academy.net/my-account?email=attacker@evil.com"></iframe>
```

- The `?email=` parameter in the iframe `src` prefills the form field - this is the whole point of the lab.
- `opacity: 0.0001` + `z-index: 2` on the iframe: invisible but on top, so the click lands on the real Update email button.
- `top: 500px / left: 80px` positions the decoy over that button. Tune in the exploit-server preview until a decoy click changes your own email.

Store, test-click to confirm your own email changes, then Deliver to victim.

## Why it works

A clickjack only moves a mouse click. By prefilling the input through the URL, the attacker also controls the *data* the click submits, defeating the assumption that a form requiring user input is safe from framing. The request the victim sends is genuine and complete.

## Running the script

`solve.py` drives the exploit server's store + deliver API:

```bash
python solve.py https://exploit-XXX.exploit-server.net https://0a...web-security-academy.net
```

`--email` sets the prefilled address, and `--top`/`--left` tune the decoy alignment. Python hosts and delivers the PoC but cannot be the victim browser that clicks, so align and test in the browser preview first.

## Takeaway

Prefilling inputs via URL parameters turns "the form needs data" from a barrier into part of the attack. The fix is the same as every clickjacking lab: anti-framing headers (`X-Frame-Options` / CSP `frame-ancestors`), not anything about the form itself.
