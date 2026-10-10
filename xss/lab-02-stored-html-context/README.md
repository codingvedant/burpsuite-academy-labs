# Lab 2: Stored XSS into HTML context with nothing encoded

**Difficulty:** Apprentice

## Goal

Submit a blog comment that calls `alert`. The comment is stored server-side and rendered back into the post's HTML, raw, for everyone who views it.

## The key insight

Same HTML context + nothing encoded as the reflected lab, so a raw `<script>` tag just runs. The difference is **persistence**: the payload is saved and served to *every* visitor of the post. No crafted link, no victim interaction - the attacker comments once and every future viewer gets hit. That's why stored XSS is generally rated more severe than reflected.

## Exploit

In the comment field of a blog post:

```html
<script>alert(1)</script>
```

Fill the other required fields (name/email) with valid-looking values, post the comment, then reload the post. The stored comment renders unescaped, the browser executes it, and the alert fires.

## How I solved it

1. Opened a blog post and found the comment form
2. Put `<script>alert(1)</script>` in the comment body, filled name/email, posted
3. Reloaded the post - the stored comment rendered raw and the alert popped, solving the lab

## Why it works

"Stored" = the payload is persisted server-side and served on every view (vs reflected, which is echoed only in the immediate response to a crafted request). "Nothing encoded" = the comment is written into the page as markup, not text. Inject into the comment **body** - fields like email are often validated/encoded.

## Takeaway

Same fix as reflected: HTML-entity-encode user input on output so it renders as text. Stored XSS makes the case for encoding at the point of output (not just input validation), because the dangerous data may be written by one user and rendered to many others later.
