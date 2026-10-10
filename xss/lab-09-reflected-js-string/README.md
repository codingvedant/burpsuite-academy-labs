# Lab 9: Reflected XSS into a JavaScript string with angle brackets HTML-encoded

**Difficulty:** Apprentice
**Type:** Reflected

## Goal

Perform a reflected XSS that breaks out of a JavaScript string and calls `alert`. The search term is reflected inside a single-quoted JS string literal in a `<script>` block.

## The key insight

```html
<script>
    var searchTerms = 'YOUR_INPUT';
    ...
</script>
```

`<`/`>` are HTML-encoded, so tag injection is dead - but it doesn't matter, because you're **already inside a `<script>` block**. You don't need a tag; you need to escape the **string literal** and write raw JS. The **single quote is not encoded**, which is the way out.

- **Context:** inside a single-quoted JS string in a script block
- **Filter:** `<`/`>` encoded (tags useless); `'` not encoded

## Exploit

```
'-alert(1)-'
```

Reflected, the line becomes:

```javascript
var searchTerms = ''-alert(1)-'';
```

- `''` closes the original string
- `-alert(1)-` uses subtraction to force `alert(1)` to **execute** mid-expression
- trailing `''` keeps the expression syntactically valid (a parse error would stop execution)

Fires automatically on page load.

Alternative: `';alert(1)//` - `'` closes the string, `;` ends the statement, `alert(1)` runs, `//` comments out the leftover `';` so there's no syntax error.

## How I solved it

1. Searched a marker and found it reflected inside a single-quoted JS string in a script block
2. Confirmed `<`/`>` encoded but `'` raw -> break the string, not inject a tag
3. Submitted `'-alert(1)-'`; it broke out and alert executed on load, solving the lab

## Three contexts, three escapes

| Context | Escape |
| --- | --- |
| HTML (between tags) | inject a tag |
| HTML attribute | break the quote + event handler (or `javascript:` for URL attrs) |
| JS string | break the string quote, write JS, keep it valid |

The `-` operators matter: they execute a function mid-expression while keeping valid JavaScript, so no syntax error stops the payload.

## Takeaway

Reflecting user input into inline JavaScript is dangerous even with HTML encoding - HTML entities don't neutralise JS-string breakouts. Use JS-string escaping (or better, don't put untrusted data in inline scripts; pass it via data attributes / JSON with proper escaping).
