# Lab 5: DOM XSS in jQuery anchor href attribute sink using location.search source

**Difficulty:** Apprentice
**Type:** DOM-based

## Goal

Trigger `alert` through DOM XSS. The feedback page uses jQuery to set a "Back" link's `href` from the `returnPath` URL parameter.

## The key insight

jQuery reads `returnPath` from `location.search` and writes it straight into an anchor's `href`:

```javascript
$(function() {
    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnPath'));
});
```

- **Source:** `location.search` (the `returnPath` param)
- **Sink:** jQuery `.attr("href", ...)` - an anchor href
- **Context:** a URL attribute

An `href` accepts `javascript:` pseudo-URLs, so no tags or event handlers are needed - the payload is just a JS-scheme URL, and it runs when the link is clicked.

## Exploit

```
https://LAB-ID.web-security-academy.net/feedback?returnPath=javascript:alert(1)
```

jQuery sets the Back link's `href` to `javascript:alert(1)`. **Click the Back link** and the JS executes.

## How I solved it

1. DOM Invader confirmed the flow: `location.search` -> `URLSearchParams` (`returnPath`) -> `jQuery.attr.href`, firing on DOMContentLoaded
2. Set `returnPath=javascript:alert(1)` in the feedback page URL
3. The Back link's href became the javascript: URL; clicking it fired the alert, solving the lab

## Why this one differs

Earlier DOM labs fired **automatically** on load (`document.write` / `innerHTML` parse immediately). An href sink is dormant until a **user interaction (the click)**. The payload shape also changes: no tag, no event handler - just a `javascript:` scheme URL, because that's what's valid in an href.

## Takeaway

Don't build URL/href attributes from untrusted input. Allowlist the scheme (permit only `http:`/`https:`/relative paths; reject `javascript:`) before assigning to an href. jQuery `.attr("href", ...)` is a URL sink, not just a text sink.
