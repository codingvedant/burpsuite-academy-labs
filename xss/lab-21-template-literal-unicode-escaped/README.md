# Lab 21: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped)

## Overview

The search term is reflected inside a JavaScript template literal (backtick string). All breakout characters (`<>`, `'`, `"`, `` ` ``, `\`) are Unicode-escaped. But `$`, `{`, `}` are not — so you can inject `${...}` template expressions that get evaluated as JavaScript.

## Key Concepts

- **Template literal expressions:** `` `text ${expression} text` `` — anything inside `${...}` is evaluated as JS
- **No breakout needed:** You inject an expression, not escape the string
- **Wrong characters escaped:** The server escapes traditional breakout chars but misses `${}` which are the dangerous ones in template literals

## Solution

1. Search for:

```
${alert(1)}
```

2. `alert(1)` fires immediately

## Payload Breakdown

The template literal becomes:
```javascript
var message = `0 search results for '${alert(1)}'`;
```

- `${alert(1)}` — the JS engine evaluates this as a template expression
- No string breakout, no tag injection, no encoding tricks needed

## Detection Tip

Look for backtick strings in the source. If reflected input is inside a template literal, test with `${7*7}` — if it renders `49`, you have template literal injection.
