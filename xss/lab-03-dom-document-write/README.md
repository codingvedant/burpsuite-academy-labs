# Lab 3: DOM XSS in document.write sink using source location.search

**Difficulty:** Apprentice
**Type:** DOM-based

## Goal

Trigger `alert` through a DOM-based XSS. The page's own JavaScript reads the search query from `location.search` and passes it to `document.write`, which writes it into the page inside an `<img>` tag.

## The key insight

This is purely client-side - the server never reflects or stores the payload. The browser's JavaScript reads a **source** (`location.search`) and writes it into a dangerous **sink** (`document.write`) with no sanitisation:

```javascript
document.write('<img src="/resources/images/tracker.gif?searchTerms=' + query + '">');
```

Your input lands **inside the double-quoted `src` attribute** of an img tag. A bare `<script>` won't run there - you break out of the attribute and tag first, then inject an element with an event handler.

- **Source:** `location.search`
- **Sink:** `document.write`
- **Context:** inside a double-quoted HTML attribute

(DOM Invader flags this source -> sink automatically: enable it, reload, search, and it reports the canary flowing into `document.write`.)

## Exploit

```html
"><svg onload=alert(1)>
```

Or straight from the URL:

```
https://LAB-ID.web-security-academy.net/?search="><svg onload=alert(1)>
```

- `">` closes the `src="` value and the `<img>` tag
- `<svg onload=alert(1)>` is a new element whose `onload` fires on parse -> `alert(1)`

## How I solved it

1. Identified the source (`location.search`) -> sink (`document.write`) flow, with input landing inside an img `src`
2. Broke out of the attribute/tag with `">` and injected `<svg onload=alert(1)>`
3. Submitted via the search box (equivalently the `search` URL param); the alert fired, solving the lab

## Why it's DOM-based

Everything happens in the browser: JS reads the URL (source) and writes it into the DOM (sink). The server never sees or processes the payload, which is the whole distinction from reflected/stored XSS.

## Takeaway

Avoid dangerous sinks like `document.write` with untrusted data. Prefer safe DOM APIs (`textContent`, `createElement` + `setAttribute`) and sanitise/encode for the specific context. Finding DOM XSS is a source->sink tracing problem - DOM Invader automates it.
