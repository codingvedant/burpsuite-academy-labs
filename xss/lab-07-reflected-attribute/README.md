# Lab 7: Reflected XSS into attribute with angle brackets HTML-encoded

**Difficulty:** Apprentice
**Type:** Reflected

## Goal

Perform a reflected XSS that injects an attribute and calls `alert`. The search term is reflected **inside an HTML attribute value**, and `<`/`>` are HTML-encoded - so you can't inject a new tag.

## The key insight

The filter encodes `<` and `>` (a `<script>` becomes `&lt;script&gt;`, inert text), so tag injection is dead. But it **does not encode the double quote (`"`)**. Since the input lands inside a double-quoted attribute, you break out of the quote and add a new attribute - an event handler.

- **Context:** inside a double-quoted HTML attribute (e.g. `value="..."`)
- **Filter:** `<` and `>` encoded; `"` not encoded

## Exploit

```
"onmouseover="alert(1)
```

Reflected, it turns the tag into:

```html
<input ... value="" onmouseover="alert(1)">
```

Hovering over the element fires `alert(1)`.

Auto-firing alternative (no hover needed, when the element is focusable):

```
" autofocus onfocus="alert(1)
```

`autofocus` focuses on load -> `onfocus` fires immediately.

## How I solved it

1. Searched a unique marker and found it reflected inside a double-quoted attribute
2. Confirmed `<`/`>` came back encoded but `"` came back raw - so tag injection is out, attribute breakout is in
3. Submitted `"onmouseover="alert(1)` to break out of the value and add an event handler
4. Triggered the handler (hover / autofocus variant) - alert fired, lab solved

## Context dictates the payload

- HTML context (labs 1-2) -> inject a tag
- **Attribute context (this lab)** -> break out of the quote, inject an attribute/event handler
- JS-string context (later) -> break out of the string

Same bug class, different payload each time. Partial encoding is still a vuln: blocking `<`/`>` but not `"` is enough to escape.

## Takeaway

Output encoding must be **context-complete**. For an attribute value, encode the quote characters (`"` -> `&quot;`) too, not just angle brackets. Best practice is a context-aware encoder plus quoting all attributes.
