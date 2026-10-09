# Lab 4: Exploiting a clickjacking vulnerability to trigger DOM-based XSS

**Difficulty:** Practitioner

## Goal

Use clickjacking to deliver a DOM-based XSS. The target has a feedback form whose `name` field is written into the page through `element.innerHTML`. Clickjacking becomes the *delivery* mechanism: the victim's single click submits a form prefilled with an XSS payload, and the payload calls `print()`.

## Finding the sink (DOM Invader)

Loaded the page in Burp's embedded browser with DOM Invader on ("Inject canary into all sources"), submitted the feedback form, and the canary surfaced in:

- **Sink:** `element.innerHTML`
- **Landing spot:** `<span id="feedbackResult">Thank you for submitting feedback, CANARY!</span>`
- **Source:** the feedback form `name` field

So the `name` value flows into `innerHTML`. That is HTML injection, i.e. DOM XSS.

## The payload

`innerHTML` does **not** execute an injected `<script>` tag, so use an element that fires JavaScript on its own:

```html
<img src=1 onerror=print()>
```

`src=1` fails to load -> `onerror` fires -> `print()` runs. `print()` is the lab's success condition.

Confirm manually first: put `<img src=1 onerror=print()>` in the feedback form's name field and submit. The print dialog should appear.

## Exploit

The feedback form prefills from URL parameters, so the payload rides in the `name` param and the victim's click submits it:

```html
<style>
  iframe { position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }
  div    { position: absolute; top: 610px; left: 80px; z-index: 1; }
</style>
<div>Click me</div>
<iframe src="https://LAB-ID.web-security-academy.net/feedback?name=<img src=1 onerror=print()>&email=hacker@attacker-website.com&subject=test&message=test#feedbackResult"></iframe>
```

- All four fields (`name`, `email`, `subject`, `message`) are prefilled so the form validates; the payload is in `name`.
- `#feedbackResult` scrolls the page so the Submit button lands where the decoy can reach it.
- Tune `top` in the exploit-server preview until a decoy click triggers the print dialog yourself, then deliver.
- If the page ever busts out of the frame, add `sandbox="allow-forms allow-scripts"` - `allow-scripts` so the onerror JS runs, but never `allow-top-navigation`.

## Why it works

Two separate bugs chained: a DOM XSS (unsanitised `name` into `innerHTML`) and a clickjacking weakness (the page can be framed). Clickjacking supplies the victim interaction that fires the XSS, and URL-param prefilling supplies the payload. The request is genuine, so neither a CSRF token nor "the form needs input" would stop it.

## Takeaway

Clickjacking is not only for CSRF-style actions - it is a generic way to make a victim perform *any* single-click action, including one that triggers XSS. Fix both ends: sanitise/encode output into `innerHTML` (or use `textContent`), and send anti-framing headers (`X-Frame-Options` / CSP `frame-ancestors`).
