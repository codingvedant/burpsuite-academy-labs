# Lab 18: Reflected XSS into a JavaScript string with single quote and backslash escaped

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS into a JavaScript string with single quote and backslash escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-single-quote-backslash-escaped)

## Overview

The search term is reflected inside a single-quoted JavaScript string in a `<script>` block. Both `'` and `\` are escaped (`\'`, `\\`), so you can't break the string or use the backslash-eats-the-escape trick. However, angle brackets `<>` are not encoded — so you can break out of the `<script>` tag at the HTML level instead.

## Key Concepts

- **HTML parsing beats JS parsing:** The browser's HTML parser runs first and splits the document into tags — `</script>` inside a JS string still closes the script block before the JS engine sees it
- **Context shift:** When you can't break the JS string (quotes + backslash escaped), break the HTML tag instead (angle brackets not encoded)
- **Defense gap:** Escaping JS quotes alone is not enough — `<` must be encoded as `\x3c` or `\u003c` inside JS strings

## Solution

1. Search for:

```
</script><script>alert(1)</script>
```

2. `alert(1)` fires immediately

## Payload Breakdown

The page becomes:
```html
<script>
var searchTerms = '</script><script>alert(1)</script>';
</script>
```

- `</script>` — closes the existing script block at the HTML parser level (before JS ever runs)
- `<script>alert(1)</script>` — new script block that executes `alert(1)`
- The remaining `';` and `</script>` from the original code become harmless text/dead markup
