# Lab 13: Stored DOM XSS

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Practitioner  
**Lab link:** [Stored DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-stored)

## Overview

Blog comments are loaded via a JSON API and rendered client-side using `innerHTML`. The server encodes `<` and `>` in comment fields, but uses JavaScript's `.replace()` without the global flag — only the **first** occurrence of each is encoded.

## Key Concepts

- **Source:** Stored comment data fetched from `/post/comment?postId=X` (JSON)
- **Sink:** `innerHTML` in the comment-rendering script (e.g., `loadComments.js`)
- **Stored + DOM combo:** Data is stored server-side (like stored XSS), but the vulnerability is in client-side rendering (like DOM XSS)
- **Non-global replace bypass:** `.replace('<', '&lt;')` only encodes the first `<` — prepend a sacrificial `<>` so the real payload passes through

## Solution

1. Navigate to any blog post
2. Inspect the comment-loading JS (e.g., `loadComments.js`) — confirm it uses `innerHTML` and the server's replace is non-global
3. Post a comment with the following in the **comment body**:
   ```
   <><img src=1 onerror=alert(1)>
   ```
4. Reload the blog post — `alert(1)` fires

## Payload Breakdown

```
<><img src=1 onerror=alert(1)>
```

- `<>` — sacrificial pair; the server's `.replace('<','&lt;')` and `.replace('>','&gt;')` consume these (first occurrence only)
- `<img src=1 onerror=alert(1)>` — sails through untouched, rendered by `innerHTML`, fires `onerror`
