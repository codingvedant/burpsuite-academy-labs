# Lab 8: Stored XSS into anchor href attribute with double quotes HTML-encoded

**Difficulty:** Apprentice
**Type:** Stored

## Goal

Store a comment whose author link runs `alert`. The comment "Website" field is stored and rendered as the author's hyperlink, i.e. inside an anchor `href`.

## The key insight

The "Website" value lands inside a URL attribute:

```html
<a href="YOUR_WEBSITE_INPUT">commenter name</a>
```

This time the filter **HTML-encodes the double quote**, so the lab 7 breakout (`"onmouseover=...`) is dead - `"` becomes `&quot;` and you can't escape the attribute. But you don't need to: an `href` is a **URL context**, and URLs accept the `javascript:` scheme. So the payload is just a JS URL used *as* the href value.

- **Context:** anchor `href` (URL attribute)
- **Filter:** `"` encoded (no attribute breakout) - irrelevant, because we stay inside the href

## Exploit

In the **Website** field:

```
javascript:alert(1)
```

Rendered:

```html
<a href="javascript:alert(1)">commenter name</a>
```

Clicking the author link runs the JS.

## How I solved it

1. Found that the comment "Website" field becomes the author link's href
2. Confirmed `"` is encoded (so no breakout) - but it's a URL attribute
3. Put `javascript:alert(1)` in the Website field and posted the comment
4. Clicked my comment's author name - the javascript: href executed, alert fired, lab solved

## Attribute context splits two ways

- Quote **not** encoded (lab 7) -> **break out** of the attribute, add an event handler.
- Quote **encoded** but it's a **URL attribute** (`href`/`src`) -> **don't break out**, use a **`javascript:` scheme** value.

A "Website" field that becomes an href is a classic stored sink people forget to validate.

## Takeaway

Encoding the quote isn't enough for URL attributes - also **allowlist the scheme** (permit `http:`/`https:`/`mailto:`/relative, reject `javascript:` and `data:`). Same href/URL-sink lesson as the DOM jQuery-href lab, in a stored setting.
