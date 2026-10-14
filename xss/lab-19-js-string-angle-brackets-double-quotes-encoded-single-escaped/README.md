# Lab 19: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped)

## Overview

The search term is reflected inside a single-quoted JavaScript string. Angle brackets are HTML-encoded (`<` → `&lt;`), double quotes are HTML-encoded (`"` → `&quot;`), and single quotes are escaped (`'` → `\'`). However, the backslash character `\` itself is **not** escaped — enabling the backslash-eats-the-escape attack.

## Key Concepts

- **Backslash eats the escape:** Your `\` escapes the server's `\`, freeing the quote — `\'` becomes `\\'` which JS reads as escaped-backslash + raw quote
- **Defense must cover all three:** `'` (string break), `<` (tag break), AND `\` (escape neutralization) — missing any one is exploitable
- **Same principle as Lab 12** (reflected DOM eval) but in a pure reflected JS-string context

## Solution

1. Search for:

```
\'-alert(1)//
```

2. `alert(1)` fires immediately

## Payload Breakdown

You send: `\'-alert(1)//`

Server escapes `'` → `\'`, producing: `\\'-alert(1)//`

```javascript
var searchTerms = '\\'-alert(1)//';
```

JS parses:
- `'\\'` — string containing a literal backslash (your `\` escaped their `\`)
- `'` — unescaped quote closes the string
- `-alert(1)` — subtraction operator invokes `alert(1)`
- `//` — comments out the trailing `';`

## The JS-String Escape Trilogy

| Lab | What's raw | Attack |
|-----|-----------|--------|
| Lab 9 | `'` not escaped | Break string directly: `'-alert(1)-'` |
| Lab 18 | `<>` not encoded | Break script tag: `</script><script>alert(1)</script>` |
| Lab 19 | `\` not escaped | Backslash eats escape: `\'-alert(1)//` |
