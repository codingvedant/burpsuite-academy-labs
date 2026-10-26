# Lab 6: Exploiting DOM clobbering to enable XSS

**Category:** DOM-based Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Exploiting DOM clobbering to enable XSS](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-xss-exploiting-dom-clobbering)

> **Chrome only.** The intended solution relies on Chrome-specific HTML parsing + DOMPurify behaviour.

## Overview

The comments script uses `let defaultAvatar = window.defaultAvatar || {avatar: '/path'}`. An injected pair of same-id `<a>` elements creates a `window.defaultAvatar` HTMLCollection; the second anchor's `name=avatar` makes `defaultAvatar.avatar` resolve to its `href`. DOMPurify allows `cid:` URLs, which don't normalize quotes — so an `&quot;` smuggled inside the `href` survives sanitization and later breaks out of an attribute-context sink that renders the avatar URL.

## Key Concepts

- **DOM clobbering:** HTML elements with `id`/`name` attributes become `window.<name>` globals, overriding JS lookups like `window.foo || default`.
- **Same-id collection trick:** two elements with the same `id` become an `HTMLCollection`. An element inside it with `name="bar"` is addressable as `collection.bar`.
- **Anchor toString:** `<a>` elements stringify to their `href`, so `collection.bar + ''` produces an attacker-controlled URL string.
- **DOMPurify `cid:` bypass:** `cid:` is on DOMPurify's URL allow-list. Browsers don't URL-encode `"` inside `cid:` URLs, so `&quot;` entity-decodes to a literal `"` at runtime — attribute break-out survives.
- **Two-comment flow:** first comment plants the clobber payload; second comment triggers a re-render that executes the vulnerable code.

## Finding It With DOM Invader

1. DOM Invader → enable **DOM clobbering** mode → reload.
2. DevTools → DOM Invader → **DOM clobbering** sub-tab lists `window.X || fallback` candidates. `defaultAvatar` is flagged.
3. DOM Invader can auto-generate a candidate clobber payload. Add the DOMPurify `cid:` + `&quot;` trick manually to defeat the sanitizer.

## Solution

Post as the **first blog comment**:

```html
<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//">
```

Then post **any second comment** (e.g. "hi"). The second post re-renders comments, the vulnerable script resolves `defaultAvatar` from our clobbered collection, the avatar URL lands in an attribute with an injected `"` breaking out, `onerror=alert(1)` runs, lab solved.

## Payload Breakdown

| Fragment | Purpose |
|----------|---------|
| `<a id=defaultAvatar>` | Creates `window.defaultAvatar` (first anchor). |
| `<a id=defaultAvatar ...>` | Second same-id anchor → `window.defaultAvatar` becomes an HTMLCollection. |
| `name=avatar` | Makes the second anchor addressable as `defaultAvatar.avatar`. |
| `href="cid:&quot;onerror=alert(1)//"` | Anchor's href — what `defaultAvatar.avatar` stringifies to. `cid:` passes DOMPurify's URL filter; `&quot;` → `"` at runtime to break out of the later attribute context. |

Resulting `defaultAvatar.avatar` (as a string): `cid:"onerror=alert(1)//`
Rendered attribute: `src="cid:"onerror=alert(1)//"` → `"` closes the attribute, `onerror` fires.

## Why It Worked

Three independent weaknesses stacked:

1. **`window.X || default` is DOM-clobberable.** The developer assumed only trusted code can set globals; HTML content in the page can, too.
2. **DOMPurify is HTML-level, not context-aware.** It sanitizes HTML in isolation and has no idea the attribute value will be read back and used elsewhere.
3. **`cid:` + `&quot;` is a sanitizer blind spot** — a scheme on the allow-list that happens not to normalize quotes.

Each weakness is defensible on its own ("allowing `cid:` is fine", "DOM clobbering requires HTML injection"). Together they chain into script execution.

## Remediation

- **Never rely on `window.X || default`.** Use a module-scoped constant or an explicit configuration object: `const DEFAULTS = {...}; const defaultAvatar = userConfig.defaultAvatar ?? DEFAULTS.avatar;`
- **Tighten DOMPurify's URL allow-list.** `ALLOWED_URI_REGEXP` can exclude `cid:` if it isn't actually needed.
- **Encode on output as well as sanitize on input.** HTML-encode avatar URLs when inserting them into attribute contexts.
- **Trusted Types + CSP (`require-trusted-types-for 'script'`)** would catch the final attribute assignment.

## Key Takeaways

- `window.X || default` is a universal DOM clobbering sink — if `X` could ever match an injected element's `id`/`name`, assume it's attacker-controlled.
- Same-id anchor collections + the `name` trick give attackers *property-path control* over the clobbered object, not just single-value overrides.
- Sanitizers protect HTML, not downstream string use. Chain audits: input filter → data flow → output context.
- The `cid:` + `&quot;` trick is a reusable DOMPurify sanitizer bypass for attribute-smuggling.
- DOM clobbering parse behaviour varies between Chrome and Firefox — always test the payload in the target browser.
