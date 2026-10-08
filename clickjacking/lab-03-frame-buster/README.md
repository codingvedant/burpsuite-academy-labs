# Lab 3: Clickjacking with a frame buster script

**Difficulty:** Practitioner

## Goal

Change the victim's email via clickjacking, but this time the target page ships a **frame buster** - JavaScript that detects when the page is loaded inside an iframe and tries to break out (typically by redirecting the top-level window to the real URL). A plain iframe gets kicked out before the victim can click.

## The key insight

A frame buster is just JavaScript, and its only escape move is **top-level navigation** - redirecting the whole browser out of the frame. The HTML5 `sandbox` attribute is a whitelist: switch it on and everything is blocked unless you explicitly allow it.

```html
<iframe sandbox="allow-forms" src="...">
```

- `allow-forms` - the change-email form can still be submitted (we need this)
- `allow-top-navigation` - **omitted**, so it stays blocked

The frame buster still runs and still decides "I'm framed, redirect!" - but when it tries to navigate the top window, the sandbox silently refuses. The escape hatch is nailed shut while the form still works.

## Exploit

```html
<style>
  iframe { position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }
  div    { position: absolute; top: 480px; left: 80px; z-index: 1; }
</style>
<div>Click me</div>
<iframe sandbox="allow-forms" src="https://LAB-ID.web-security-academy.net/my-account?email=attacker@evil.com"></iframe>
```

The only change from lab 2 is `sandbox="allow-forms"` on the iframe. Decoy alignment and prefill-via-`?email=` are identical.

## Why it works

`sandbox` was designed as a defensive feature, but here it is turned against the site: because it blocks everything not whitelisted, leaving out `allow-top-navigation` disables exactly the capability the frame buster depends on. The script runs harmlessly; the frame never busts.

Note: if a page needs its own scripts to render, use `allow-scripts` too. That lets the buster script execute, but it still cannot navigate the top window, so it is still defanged. Never add `allow-top-navigation`.

## Running the script

`solve.py` drives the exploit server's store + deliver API and includes the `sandbox="allow-forms"` attribute in the generated iframe:

```bash
python solve.py https://exploit-XXX.exploit-server.net https://0a...web-security-academy.net
```

`--email` sets the prefilled address, and `--top`/`--left` tune the decoy alignment. Align and test-click in the browser preview before delivering.

## Takeaway

Client-side frame busters are not a real defence - they are JavaScript an attacker can neutralise with a one-word iframe attribute. The only reliable control is server-sent anti-framing headers (`X-Frame-Options` / CSP `frame-ancestors`), which the browser enforces before any page script runs.
