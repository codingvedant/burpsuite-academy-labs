# Lab 2: DOM XSS using web messages and a JavaScript URL

**Category:** DOM-based Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [DOM XSS using web messages and a JavaScript URL](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-a-javascript-url)

## Overview

The home page's `message` listener does a filter before using `e.data` — it checks that the data contains `http:` or `https:` via `indexOf` — then assigns it to `location.href`. The filter is a substring check, not URL validation. A `javascript:` URL with `//http:` as a trailing JS line comment satisfies the filter and executes as JS when assigned to `location.href`.

## Key Concepts

- **`indexOf` is a substring check, not a URL validator.** Any string containing the literal letters `http:` passes.
- **`location.href =` accepts every URL scheme the browser knows,** including `javascript:` — which executes the following expression as JavaScript in the page's origin.
- **`//` is a single-line comment in JS.** Inside a `javascript:` URL, `//http:` is just dead code after the real payload.
- **Same source as Lab 1:** attacker-controlled `postMessage` with no `e.origin` check. The listener gatekeeper has filter logic but not origin logic.

## Finding It With DOM Invader

1. DOM Invader → **Postmessage interception** on → reload the lab.
2. DevTools → DOM Invader → **Messages** tab. The handler's source shows the `indexOf` filter and `location.href` sink.
3. **Send message** with data `javascript:document.title='DOMI'//http:` and origin `*`. Tab title flips → sink confirmed.

## Solution

Exploit server body:

```html
<iframe src="https://LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">
```

**Store** → **Deliver exploit to victim**. Admin's browser → iframe loads → `onload` on attacker page → `postMessage` fires → listener's `indexOf('http:')` matches → `location.href = 'javascript:print()//http:'` → `print()` runs → lab solved.

## Payload Breakdown

| Fragment | Purpose |
|----------|---------|
| `<iframe src="lab-url">` | Loads the lab in a frame so we can address its `window`. |
| `onload="..."` | Waits for the lab's scripts (and the `message` listener) to be registered. |
| `postMessage(data, '*')` | Sends `data` cross-origin to the iframe's window. |
| `javascript:print()` | The real payload — assigned to `location.href`, runs `print()` as JS. |
| `//http:` | A JS line comment that satisfies the listener's `indexOf('http:')` check. Ignored by the JS engine. |

## Why It Worked

The developer added a filter without understanding what they were filtering. They wanted "the message is a URL that starts with `http:`" but wrote "the message contains the substring `http:` anywhere". That turns a URL check into a trivially bypassable string match. Combine with a `javascript:` URL sink that treats `//` as a comment and the filter and the sink collaborate against the defender.

## Remediation

- **Parse before you validate.** `new URL(e.data)` throws on garbage and gives you a `.protocol` to check against an allow-list (`'http:' || 'https:'`).
- **Reject `javascript:` explicitly** anywhere a URL is assigned to a navigation sink (`location`, `location.href`, `window.open`, `<a href>`).
- **Validate `e.origin` first.** The filter is defence in depth; the origin check is the actual trust boundary.
- **Avoid `location.href = untrusted`** entirely — prefer parsing + rebuilding the URL from known-safe pieces.

## Key Takeaways

- **Substring check on a URL = not a URL check.** `indexOf`, `includes`, `startsWith` on raw strings always have a bypass.
- **`javascript:` scheme + `//` comment** is the universal "satisfy a stupid URL filter while still executing JS" trick.
- **Sinks matter.** Lab 1's sink was `innerHTML`; this one's is `location.href`. Different sinks, different payload shapes, same source class.
- **Validate URLs with the URL parser.** `URL`/`URLSearchParams` exist for exactly this reason.
