# Lab 5: DOM-based cookie manipulation

**Category:** DOM-based Vulnerabilities
**Difficulty:** Practitioner
**Lab link:** [DOM-based cookie manipulation](https://portswigger.net/web-security/dom-based/cookie-manipulation/lab-dom-cookie-manipulation)

## Overview

Two pages, one trust corridor. The **product page** writes `window.location.href` into a `lastViewedProduct` cookie. The **home page** reads that cookie and reflects it into the DOM — inside an attribute like `<a href='COOKIE_VALUE'>` — with no encoding. Visiting a crafted product URL poisons the cookie; a subsequent home-page visit fires the payload.

## Key Concepts

- **Cookie manipulation bugs are two-step DOM XSS.** The "writer" page captures attacker input; the "reader" page reflects it. Neither looks exploitable in isolation.
- **Cookies are a persistent, same-origin trust corridor.** Data written there carries across page navigations and tabs.
- **Attribute-context reflection** needs a `'>` or `">` break-out depending on quoting. Here the sink is single-quoted, so `'>` closes it.
- **One-shot iframe latch** (`if(!window.x) ...; window.x=1`) lets a single iframe navigate twice in sequence without looping.

## Finding It With DOM Invader

1. DOM Invader on → enable **Cookies** sinks → visit any product page.
2. Logs show `document.cookie =` with `window.location.href` as the source → poisoning primitive confirmed.
3. Navigate to the home page. DOM Invader logs a sink hit: cookie value → DOM. Stack trace points at the "last viewed product" rendering.
4. From source + sink, the exploit is: craft a product URL that is simultaneously a valid-ish URL *and* a valid HTML payload when stored verbatim.

## Solution

Exploit server body:

```html
<iframe src="https://LAB-ID.web-security-academy.net/product?productId=1&'><script>print()</script>"
        onload="if(!window.x)this.src='https://LAB-ID.web-security-academy.net';window.x=1;">
```

**Store** → **Deliver exploit to victim**. Admin's browser:
1. Iframe loads the malicious product URL → product page writes the full URL (payload included) into `lastViewedProduct`.
2. `onload` fires, `window.x` undefined → iframe `src` set to home page; `window.x=1`.
3. Iframe navigates to home. Home reads poisoned cookie, drops it into the DOM, `<script>print()</script>` runs → lab solved.

## Payload Breakdown

Attacker URL:

```
https://LAB-ID.../product?productId=1&'><script>print()</script>
```

Reflected into home-page HTML (approx):

```html
<a href='https://LAB-ID.../product?productId=1&'><script>print()</script>'>Last viewed...</a>
```

| Fragment | Purpose |
|----------|---------|
| `productId=1` | Loads a real product so the writer runs. |
| `&` | Separator — ensures the next part is still inside the URL for the cookie writer. |
| `'>` | Closes the `href='...'` and the `<a>` tag on the home page. |
| `<script>print()</script>` | Payload that runs when the home page parses the poisoned cookie. |

**Iframe latch:**

| Fragment | Purpose |
|----------|---------|
| `src="malicious-product-url"` | First load → poisons the cookie. |
| `onload="if(!window.x)this.src='home-url'"` | On first load, redirect iframe to home. |
| `window.x=1` | Set latch — second `onload` won't redirect again. |

## Why It Worked

The product-page developer thought "it's just a URL being stored, who cares." The home-page developer thought "it's just a cookie we set ourselves, we trust it." Together they built a lossless path from URL query string → cookie → DOM, with no encoding at any step. The attacker only needs to visit the writer with a payload-shaped URL and force the victim to the reader.

## Remediation

- **Don't store raw user input in cookies.** Store an opaque key (`lastViewedId=42`) and look up the metadata server-side.
- **Encode at both ends.** Writer: encode the URL before putting it in the cookie. Reader: HTML-encode when inserting into the DOM. Either alone would have blocked this.
- **Prefer `textContent` over `innerHTML`** or attribute-context assignment when rendering untrusted strings.
- **`SameSite` and `HttpOnly` don't help here** — the cookie is set and read by same-origin JS. The fix is encoding/data-model, not cookie flags.

## Key Takeaways

- **Audit `document.cookie =` writes with attacker-reachable sources** — even if the write looks harmless, the reader elsewhere may be a sink.
- **Attribute-context reflections need a scheme-aware break-out.** `'>` for single quotes, `">` for double, `>` for unquoted.
- **The one-shot latch (`if(!window.x) ...; window.x=1`)** is a reusable gadget for sequencing two page loads in one iframe.
- **Pivot through same-origin state.** Cookies, `localStorage`, `IndexedDB`, service workers all let an attacker on the writer page influence the reader page later.
