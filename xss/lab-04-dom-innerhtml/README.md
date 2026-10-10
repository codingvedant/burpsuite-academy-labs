# Lab 4: DOM XSS in innerHTML sink using source location.search

**Difficulty:** Apprentice
**Type:** DOM-based

## Goal

Trigger `alert` through DOM XSS. The page's JavaScript reads the search query from `location.search` and assigns it to an element's `innerHTML`.

## The key insight

Same source as lab 3, different sink. The query is written as an element's inner HTML content directly:

```javascript
element.innerHTML = query;   // the "X search results for ..." display
```

- **Source:** `location.search`
- **Sink:** `innerHTML`
- **Context:** element content, not inside an attribute - so there is **no quote/tag to break out of**. You just inject your element.

The catch: `innerHTML` does **not** execute a `<script>` tag assigned to it. So you use an element that fires JS via an event handler instead.

## Exploit

```html
<img src=1 onerror=alert(1)>
```

Or via the URL:

```
https://LAB-ID.web-security-academy.net/?search=<img src=1 onerror=alert(1)>
```

`src=1` fails to load -> `onerror` fires -> `alert(1)`. (`<svg onload=alert(1)>` works too.)

## How I solved it

1. Identified source (`location.search`) -> sink (`innerHTML`), input written as element content
2. No breakout needed, but `<script>` is dead in innerHTML, so used `<img src=1 onerror=alert(1)>`
3. Submitted via the search box / `search` param - onerror fired the alert, lab solved

## Context vs sink (the pattern to keep)

- Lab 3 (`document.write`, inside an img `src` attribute) -> needed a **breakout** (`">`) then an element.
- Lab 4 (`innerHTML`, element content) -> **no breakout**, but `<script>` is blocked, so use an **event-handler element**.

Same source, different sink -> different payload. Context + sink/filter decide every XSS payload.

## Takeaway

Don't assign untrusted data to `innerHTML`. Use `textContent` for text, or sanitise with a vetted library (e.g. DOMPurify) when HTML is genuinely required. `<script>` being inert in innerHTML is not a defence - event handlers still fire.
