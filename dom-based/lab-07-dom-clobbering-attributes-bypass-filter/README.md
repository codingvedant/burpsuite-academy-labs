# Lab 7: Clobbering DOM attributes to bypass HTML filters

**Category:** DOM-based Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [Clobbering DOM attributes to bypass HTML filters](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-clobbering-attributes-to-bypass-html-filters)

> **Chrome only.** Firefox doesn't do the form-child shadowing we rely on.

## Overview

Comments are sanitized by HTMLJanitor, which iterates `node.attributes` to strip disallowed attributes. By injecting a `<form>` whose child `<input id=attributes>` shadows `form.attributes` with an element reference, the sanitizer's `.length` check reads `undefined` and the attribute-strip loop iterates zero times. The form's `onfocus=print()` survives sanitization. A URL fragment navigation (`#x`) focuses the form in the victim's browser, firing the payload.

## Key Concepts

- **Form named-child shadowing:** form elements expose their named children as own properties, overriding native props with the same name. `<form><input id=attributes>` makes `form.attributes` return the `<input>`, not the native `NamedNodeMap`.
- **`.length` on an element is `undefined`:** sanitizers that gate on `for (let i = 0; i < node.attributes.length; i++)` iterate zero times when `attributes` is clobbered.
- **URL fragment = free focus/scroll primitive.** Navigating to `#id` focuses (and scrolls to) the element with that id — fires `onfocus`, `onscroll`, `:target` CSS, lazy-loading, etc.
- **Element-property clobbering vs window clobbering:** Lab 6 clobbered `window.X`; this lab clobbers a property on a specific DOM element — a different, often-missed primitive.

## Finding It With DOM Invader

DOM Invader's DOM-clobbering scan focuses on `window.X || default` patterns, so it won't flag this one automatically. Workflow:

1. Observe comments feed into HTMLJanitor-sanitized HTML (visible in the loaded JS, or in DOM Invader's Sinks tab).
2. Read HTMLJanitor's source — the attribute-strip loop uses `node.attributes.length`.
3. Reason: can we make `node.attributes` not an attribute list? Form named-child shadowing provides exactly that.

## Solution

Post as a comment on a chosen `postId`:

```html
<form id=x tabindex=0 onfocus=print()><input id=attributes>
```

Then on the exploit server (matching `postId`):

```html
<iframe src=https://LAB-ID.web-security-academy.net/post?postId=3 onload="setTimeout(()=>this.src=this.src+'#x',500)">
```

**Store** → **Deliver exploit to victim**. Admin's browser loads the iframe → waits 500ms → iframe `src` gets `#x` appended → browser focuses `#x` (our form) → `onfocus=print()` → lab solved.

## Payload Breakdown

Comment:

| Fragment | Purpose |
|----------|---------|
| `<form id=x ...>` | Host element whose `onfocus` is the real payload. |
| `id=x` | Fragment-nav target — `#x` focuses this element. |
| `tabindex=0` | Makes the form focusable (forms don't take focus by default). |
| `onfocus=print()` | Dangerous attribute HTMLJanitor was supposed to strip; survives thanks to the clobber. |
| `<input id=attributes>` | The clobber — shadows `form.attributes` with an element → sanitizer's `.length` is `undefined` → loop iterates 0 times. |

Exploit iframe:

| Fragment | Purpose |
|----------|---------|
| `src=lab-url/post?postId=3` | Loads the post page containing our comment. |
| `onload="setTimeout(..., 500)"` | Waits for render. |
| `this.src = this.src + '#x'` | Appends the fragment to trigger focus navigation. |

The `setTimeout` is required because adding `#x` directly on the first load doesn't re-trigger fragment navigation reliably; we load without a fragment, then set it to force the focus event.

## Why It Worked

HTMLJanitor's filter design assumed `node.attributes` is the native `NamedNodeMap` with a numeric `.length`. The HTML spec says form elements expose named children as own properties; that spec feature wasn't on the sanitizer author's radar. Combining the two — a shadowing primitive on the host element and a sanitizer that trusts `.attributes` structurally — turns a "sanitized" comment into attribute-smuggling XSS.

## Remediation

- **Don't iterate `node.attributes` with `.length`.** Use `node.getAttributeNames()` (returns a real array) or iterate `node.attributes` with `for ... of` only after checking `node.attributes instanceof NamedNodeMap`.
- **Prefer a well-maintained sanitizer** (DOMPurify, sanitize-html) over abandoned ones. HTMLJanitor is unmaintained.
- **Trusted Types + CSP (`require-trusted-types-for 'script'`)** catches the final sink assignment.
- **Context-aware output encoding.** Sanitize *and* encode on insertion, especially for attribute contexts.

## Key Takeaways

- **Form named-child shadowing** is the most powerful DOM clobbering primitive you have on an existing element — `form.action`, `form.children`, `form.length`, `form.attributes` are all shadow-able.
- **Sanitizers that iterate `.attributes` with `.length`** are generically vulnerable. Audit any HTML filter for this exact pattern.
- **URL fragments are free focus triggers.** Any `onfocus`/`onscroll`/`:target` gadget on an element with a known `id` fires without user interaction when `#id` is appended to the URL.
- **Element-property clobbering** is a distinct bug class from window clobbering. DOM Invader won't find it for you — you need to know the shadowing primitive and look for sanitizers that read DOM properties structurally.
