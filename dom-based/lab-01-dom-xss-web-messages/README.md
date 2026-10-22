# Lab 1: DOM XSS using web messages

**Category:** DOM-based Vulnerabilities
**Difficulty:** Apprentice
**Lab link:** [DOM XSS using web messages](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages)

## Overview

The lab's home page registers a `message` event listener that writes the received data straight into the DOM via `innerHTML`, with **no `e.origin` check** and no sanitization. Any cross-origin frame can `postMessage` a payload and get it executed. The exploit is a one-line iframe on the exploit server.

## Key Concepts

- **`window.postMessage(data, targetOrigin)`:** cross-origin messaging primitive. The sender can be any window; the receiver has to validate the sender.
- **`e.origin` is the only trust boundary.** Without checking it, every `message` handler is implicitly cross-origin reachable.
- **`innerHTML` is a DOM XSS sink.** The browser parses the assigned string as HTML and runs event handlers like `onerror`, `onload`, `onanimationend` immediately.
- **PortSwigger DOM-based labs want `print()`, not `alert()`.** The checker watches for the print dialog.

## Finding It With DOM Invader

1. Burp → **Proxy** → **Open browser**. In that embedded Chrome, click the DOM Invader extension icon → toggle on.
2. Enable **Postmessage interception** in DOM Invader settings and reload the lab.
3. DevTools → **DOM Invader** tab → **Messages** sub-tab. The lab's `message` listener is listed with its source code — the `innerHTML` assignment and the missing origin check are visible immediately.
4. Click **Send message**, set data to a canary like `<img src=x onerror=document.title='DOMI'>` and origin `*`. Tab title flips to `DOMI` → sink confirmed.

## Solution

Exploit server body:

```html
<iframe src="https://LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">
```

Replace `LAB-ID`. **Store** → **Deliver exploit to victim**. The admin's browser loads the iframe, the iframe's `onload` fires on the attacker's page, we `postMessage` the payload, the lab's listener drops it into `innerHTML`, `onerror` runs `print()`, lab solved.

## Payload Breakdown

| Fragment | Purpose |
|----------|---------|
| `<iframe src="lab-url">` | Embed the lab so we have a handle to its window via `contentWindow`. |
| `onload="..."` | Wait until the lab finishes loading and the `message` listener is registered. |
| `this.contentWindow.postMessage(data, '*')` | Send `data` to the iframe's window; `'*'` means any target origin — no restriction. |
| `<img src=1 onerror=print()>` | HTML parsed by `innerHTML`; broken `src` triggers `onerror`, which calls `print()`. |

## Why It Worked

The lab's developer treated `message` events as internal plumbing — forgetting that **any origin on the web can `postMessage` into any window that has it as an iframe or opener**. CSP wouldn't help here either: the inline handler runs in the lab origin's HTML parse, so `script-src 'self'` still permits it. The only fix is at the data boundary.

## Remediation

- Validate `e.origin` against an allow-list and reject anything else.
- Parse `e.data` strictly (e.g. `JSON.parse` + schema validation); never pass raw strings to `innerHTML`.
- Prefer `textContent` over `innerHTML` for display-only data.
- Trusted Types + a strict CSP (`require-trusted-types-for 'script'`) catches these sinks at the browser level.

## Key Takeaways

- No `e.origin` check = cross-origin trust boundary with no fence.
- `innerHTML` + attacker-controlled text = DOM XSS, every time.
- DOM Invader surfaces this in seconds — read the listener source, send a canary, done.
- Use `print()` for PortSwigger DOM-based labs.
