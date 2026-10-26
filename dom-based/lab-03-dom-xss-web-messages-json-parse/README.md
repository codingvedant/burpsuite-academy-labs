# Lab 3: DOM XSS using web messages and JSON.parse

**Category:** DOM-based Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [DOM XSS using web messages and JSON.parse](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-json-parse)

## Overview

The home page's `message` handler parses `e.data` as JSON and dispatches on a `type` field. The `load-channel` branch assigns the message's `url` field to an iframe's `src` — no origin check, no URL validation. A `javascript:` URL on `iframe.src` executes same as `location.href`.

## Key Concepts

- **Structure ≠ validation.** `JSON.parse` + a `switch` gives you a schema shape, but every case is still a potential sink that needs its own validation.
- **`iframe.src =` executes `javascript:` URLs.** Same gadget as `location.href` or `a.href`.
- **No `e.origin` check** on the listener — any origin can craft a valid-shaped message.
- **Each `case` in the switch is a separate attack surface.** The dev essentially published the internal API; the attacker picks which branch to hit.

## Finding It With DOM Invader

1. DOM Invader → Postmessage interception → reload.
2. Messages tab → read the handler source. The `JSON.parse` + `switch(data.type)` structure is visible, as is `ACMEplayer.element.src = data.url` on the `load-channel` branch.
3. **Send message** with data `{"type":"load-channel","url":"javascript:document.title='DOMI'"}` and origin `*`. Title flips → sink confirmed.

## Solution

Exploit server body:

```html
<iframe src=https://LAB-ID.web-security-academy.net/ onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

The outer `onload` is single-quoted so the inner JSON string's `"` can be `\"`-escaped. **Store** → **Deliver exploit to victim**. Victim's iframe loads → `onload` fires → `postMessage` of the JSON string → listener parses, dispatches `load-channel`, assigns `ACMEplayer.element.src = 'javascript:print()'` → `print()` runs → lab solved.

## Payload Breakdown

Message `e.data` (after `JSON.parse`):

```json
{"type":"load-channel","url":"javascript:print()"}
```

| Field | Purpose |
|-------|---------|
| `type: "load-channel"` | Selects the switch case whose body is `ACMEplayer.element.src = data.url`. |
| `url: "javascript:print()"` | Attacker-controlled string assigned to `iframe.src`. `javascript:` scheme runs the following expression as JS. |

## Why It Worked

The developer took the right first step (schema-driven messaging) and stopped there. They validated the message's *shape* but not its *contents*. The `load-channel` branch assumes `data.url` is a legitimate URL because it's named `url` — but names are documentation, not validation. The `iframe.src =` sink then faithfully executes the attacker's `javascript:` URL.

## Remediation

- **Validate `e.origin` first.** Nothing else matters without a trust boundary.
- **Validate parsed data against a schema.** After `JSON.parse`, run the object through type guards (TypeScript, Zod, io-ts) or hand-written validators that reject unexpected fields and enforce field types/formats.
- **Validate URLs with the URL parser.** `new URL(data.url)`, check `.protocol` against `{'http:', 'https:'}`, reject anything else.
- **Treat each `case` as its own sink.** Audit every branch of the switch for the pattern `sink = userControlledValue`.

## Key Takeaways

- `JSON.parse(e.data)` + `switch(data.type)` is a common pattern — treat every case as a sink and audit each independently.
- `iframe.src` is a `javascript:` sink. Any attribute that navigates — `src`, `href`, `action`, `formaction`, `data` — is a candidate for a scheme-based XSS.
- A schema protects the parser, not the handlers. Fields still need per-field validation.
- The transferable fix is "parse, validate, then use" — never "parse, then use."
