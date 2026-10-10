# Lab 1: Reflected XSS into HTML context with nothing encoded

**Difficulty:** Apprentice

## Goal

Perform a reflected XSS attack that calls `alert`. The search function reflects whatever you submit straight back into the page's HTML with no encoding.

## The key insight

Your input lands **directly between HTML tags** (HTML context) and nothing is escaped - `<`, `>`, `"` all pass through raw. In that context an injected `<script>` tag is parsed as a real script element and just runs. No breaking out of quotes or tags is needed; that only comes up in later labs where the input lands inside an attribute or inside existing JavaScript.

## Exploit

Submit this in the search box:

```html
<script>alert(1)</script>
```

As a URL it's just:

```
https://LAB-ID.web-security-academy.net/?search=<script>alert(1)</script>
```

The response reflects the tag unescaped, the browser executes it, and the alert fires - solving the lab.

## Why it works

"Reflected" = the payload is echoed back in the immediate response (so a real attack needs the victim to open a crafted link). "Nothing encoded" = the app does no output encoding, so the tag is interpreted as markup rather than shown as text. Context + encoding are the two things that decide every XSS payload.

## Running the script

`solve.py` sends the payload in the `search` parameter and confirms it is reflected unescaped:

```bash
python solve.py https://0a...web-security-academy.net
```

Note: the alert actually executes in a browser. The script confirms the unescaped reflection (the condition that makes it fire) and reports the lab status, but load the URL in a browser to see the popup.

## Takeaway

The fix is output encoding: HTML-entity-encode user input on the way out (`<` -> `&lt;`, etc.) so it renders as text, never markup. A strong Content-Security-Policy is defence in depth on top.
